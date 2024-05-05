import sqlite3
import requests
from dotenv import load_dotenv


DATABASE = "../sql/db.sqlite"
load_dotenv()


def get_db():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")


def get_user(username):
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()
            return dict(user) if user else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def get_friends(username):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT DISTINCT users.username, users.bio FROM users "
            "JOIN friends ON (users.username = friends.user_a OR users.username = friends.user_b) "
            "WHERE (friends.user_a = ? OR friends.user_b = ?) AND users.username != ?",
            (username, username, username),
        ).fetchall()
        return [dict(row) for row in rows]


def get_friend_activities(username):
    with get_db() as conn:
        activities = conn.execute(
            """
            SELECT w.username, m.imdb_id, w.review, w.rating, w.timestamp, m.title, m.genres
            FROM watched w
            JOIN (
                SELECT user_b as friend FROM friends WHERE user_a = ?
                UNION
                SELECT user_a as friend FROM friends WHERE user_b = ?
            ) friends ON w.username = friends.friend
            JOIN movies m ON m.id = w.movie_id
            WHERE w.username != ?
            ORDER BY w.timestamp DESC
            LIMIT 10
        """,
            (username, username, username),
        ).fetchall()
        return [dict(activity) for activity in activities]


def get_non_friends(username, friends):
    # Assuming we can now directly use usernames without converting them from a dict
    friends_usernames = [f["username"] for f in friends]
    # Include the username in the list to exclude from non-friends
    friends_usernames.append(username)
    query_placeholders = ", ".join("?" for _ in friends_usernames)
    with get_db() as conn:
        query = f"SELECT username, bio FROM users WHERE username NOT IN ({query_placeholders})"
        rows = conn.execute(query, friends_usernames).fetchall()
        return [dict(row) for row in rows]


def get_movie_reviews(movie_id):
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            reviews = conn.execute(
                """
                SELECT username, review, rating, timestamp
                FROM watched
                WHERE movie_id = ?
                ORDER BY timestamp DESC
                """,
                (movie_id,),
            ).fetchall()
            return [dict(row) for row in reviews]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def remove_movie_from_backlog(username, movie_id):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM backlog WHERE username = ? AND movie_id = ?",
                (username, movie_id),
            )
            conn.commit()
            return cursor.rowcount > 0  # Returns True if any row was affected
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def add_friend(user_a, user_b):
    # This function inserts a new friendship, ensuring not to duplicate existing ones
    with get_db() as conn:
        # Check if friendship already exists to avoid duplicates
        check = conn.execute(
            "SELECT 1 FROM friends WHERE (user_a = ? AND user_b = ?) OR (user_a = ? AND user_b = ?)",
            (user_a, user_b, user_b, user_a),
        ).fetchone()
        if not check:
            conn.execute(
                "INSERT INTO friends (user_a, user_b) VALUES (?, ?)", (user_a, user_b)
            )
            conn.commit()


def create_user(username, hashed_password):
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        print("Username already exists")
    except sqlite3.Error as e:
        print(f"Database error: {e}")


def fetch_movie_poster(imdb_id):
    url = f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={REELFRIENDS_API_KEY}&external_source=imdb_id"
    response = requests.get(url)
    data = response.json()
    # Assuming the movie is always found and has a poster, adjust as necessary
    poster_path = (
        data["movie_results"][0]["poster_path"] if data["movie_results"] else None
    )
    return f"http://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None


def get_movies_count():
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    conn.close()
    return count


def get_all_genres():
    conn = get_db()
    query = "SELECT DISTINCT genres FROM movies"
    all_genres = conn.execute(query).fetchall()
    unique_genres = set()
    for row in all_genres:
        if row["genres"]:
            unique_genres.update(map(str.strip, row["genres"].split(",")))
    conn.close()
    return sorted(list(unique_genres))


def get_collections():
    db = get_db()
    try:
        cursor = db.cursor()
        query = "SELECT DISTINCT collection FROM movies WHERE collection IS NOT NULL AND collection != '' ORDER BY collection;"
        cursor.execute(query)
        collections = cursor.fetchall()
        return [collection["collection"] for collection in collections]
    except sqlite3.Error as e:
        print(f"Error fetching collections: {e}")
        return []
    finally:
        db.close()


def get_movie_by_imdb_id(imdb_id):
    conn = get_db()
    if conn is None:
        return None

    try:
        # Assuming the movie details are stored in a table named 'movies'
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM movies WHERE imdb_id = ?", (imdb_id,))
        movie = cursor.fetchone()
        return dict(movie) if movie else None
    except Exception as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()


def get_movies(limit, offset, sort_by, order, genre=None, search=None, collection=None):
    conn = get_db()
    where_clause = "WHERE vote_count >= 100"
    params = []

    if genre:
        where_clause += " AND genres LIKE ?"
        params.append(f"%{genre}%")

    if search:
        where_clause += " AND title LIKE ?"
        params.append(f"%{search}%")

    if collection:
        where_clause += " AND collection = ?"
        params.append(collection)

    count_query = f"SELECT COUNT(*) FROM movies {where_clause}"
    total = conn.execute(count_query, params).fetchone()[0]

    movies_query = f"""
        SELECT *
        FROM movies
        {where_clause}
        ORDER BY {sort_by} {order}
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])
    movies = conn.execute(movies_query, params).fetchall()
    conn.close()

    return total, [dict(row) for row in movies]


def add_to_backlog(username, movie_id):
    conn = get_db()
    if conn is None:
        return False, "Database connection error"

    try:
        with conn:
            # Check if the movie is already in the backlog
            cursor = conn.execute(
                "SELECT 1 FROM backlog WHERE username = ? AND movie_id = ?",
                (username, movie_id),
            )
            if cursor.fetchone():
                return True, "Movie already in backlog"

            # Insert the movie into the backlog
            conn.execute(
                "INSERT INTO backlog (username, movie_id) VALUES (?, ?)",
                (username, movie_id),
            )
            return True, "Movie added to backlog successfully"
    except sqlite3.Error as e:
        return False, str(e)
    finally:
        if conn:
            conn.close()


def get_backlog(username):
    conn = get_db()
    if conn is None:
        return None, "Database connection error"
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT m.*, b.timestamp AS added_on FROM movies m
            JOIN backlog b ON m.id = b.movie_id
            WHERE b.username = ?
        """,
            (username,),
        )
        movies = cursor.fetchall()
        return [dict(movie) for movie in movies], "Success"
    except sqlite3.Error as e:
        return None, str(e)
    finally:
        if conn:
            conn.close()


def remove_from_backlog(username, movie_id):
    conn = get_db()
    if conn is None:
        return False, "Database connection error"
    try:
        with conn:
            conn.execute(
                "DELETE FROM backlog WHERE username = ? AND movie_id = ?",
                (username, movie_id),
            )
        return True, "Removed from backlog"
    except sqlite3.Error as e:
        return False, str(e)


def mark_movie_as_watched(username, movie_id, review=None, rating=None):
    conn = get_db()
    if conn is None:
        return False, "Database connection error"
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO watched (username, movie_id, review, rating, timestamp)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(username, movie_id) 
                DO UPDATE SET review = excluded.review, rating = excluded.rating, timestamp = CURRENT_TIMESTAMP;
            """,
                (username, movie_id, review, rating),
            )
            conn.commit()
            return True, "Movie marked as watched and data updated"
    except sqlite3.Error as e:
        return False, str(e)
    finally:
        if conn:
            conn.close()


def get_user_profile(username):
    conn = get_db()

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, bio FROM users WHERE username = ?", (username,)
        )
        user = cursor.fetchone()
        if user:
            return dict(user)
        else:
            return None
    except sqlite3.Error as e:
        print(f"get_user_profile: SQL error - {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_watched_movies(username):
    conn = get_db()
    if conn is None:
        print("get_watched_movies: Failed to get DB connection.")
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT *
            FROM watched w
            JOIN movies m ON w.movie_id = m.id
            WHERE w.username = ?
            ORDER BY w.timestamp DESC
        """,
            (username,),
        )
        movies = cursor.fetchall()
        return [dict(movie) for movie in movies]
    except sqlite3.Error as e:
        print(f"get_watched_movies: SQL error - {e}")
        return None
    finally:
        if conn:
            conn.close()


def update_bio(username, bio):
    conn = get_db()
    if conn is None:
        return False, "Database connection error"
    try:
        with conn:
            conn.execute("UPDATE users SET bio = ? WHERE username = ?", (bio, username))
            return True, "Bio updated successfully"
    except sqlite3.Error as e:
        return False, str(e)
    finally:
        if conn:
            conn.close()


def update_movie_review(username, movie_id, review, rating):
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.execute(
                """
                INSERT INTO watched (username, movie_id, review, rating)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(username, movie_id)
                DO UPDATE SET review = ?, rating = ?
            """,
                (username, movie_id, review, rating, review, rating),
            )
            conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error during review update: {e}")
        return False
