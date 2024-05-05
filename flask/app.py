from flask import Flask, jsonify, request
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_cors import CORS
import database
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
MOVIE_LIMIT = 25
app.config["SECRET_KEY"] = "nXcjUL2vkn"
CORS(app, supports_credentials=True, origins=["http://localhost:8011"])

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@app.route("/")
def home():
    return "Hello from Flask!"


class User(UserMixin):
    def __init__(self, username):
        self.id = username

    @property
    def is_active(self):
        return True


@login_manager.user_loader
def load_user(user_id):
    user = database.get_user(user_id)
    if user:
        return User(user["username"])
    return None


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user_dict = database.get_user(username)
    if user_dict:
        if check_password_hash(user_dict["password"], password):
            user = User(username)
            login_user(user)
            return (
                jsonify(
                    {
                        "login": True,
                        "message": "Logged in successfully",
                        "username": username,
                    }
                ),
                200,
            )
        else:
            return jsonify({"login": False, "message": "Invalid password"}), 401
    else:
        return jsonify({"login": False, "message": "Invalid username"}), 404


@app.route("/friend_activities/<username>", methods=["GET"])
@login_required
def fetch_friend_activities(username):
    if (
        current_user.id == username
    ):  # Ensuring the logged-in user is requesting their own data
        activities = database.get_friend_activities(username)
        return jsonify({"activities": activities}), 200
    else:
        return jsonify({"message": "Unauthorized"}), 403


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if database.get_user(username) is not None:
        return jsonify({"message": "Username already taken"}), 409

    hashed_password = generate_password_hash(password)

    try:
        database.create_user(username, hashed_password)
        user = User(username)
        login_user(user)
        return (
            jsonify({"message": "User created successfully", "username": username}),
            201,
        )
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        return jsonify({"logout": True, "message": "Logged out successfully"}), 200
    else:
        return jsonify({"logout": False, "message": "Not logged in"}), 401


@app.route("/get_genres", methods=["GET"])
@login_required
def get_genres():
    genres = database.get_all_genres()
    return jsonify(genres)


@app.route("/friends/<username>", methods=["GET"])
def get_friends(username):
    friends = database.get_friends(username)
    non_friends = database.get_non_friends(username, friends)
    return jsonify({"friends": friends, "nonFriends": non_friends})


@app.route("/add_friend", methods=["POST"])
def add_friend():
    data = request.json
    database.add_friend(data["user_a"], data["user_b"])
    return jsonify({"status": "success"})


@app.route("/movies/<imdb_id>", methods=["GET"])
def get_movie(imdb_id):
    movie_details = database.get_movie_by_imdb_id(imdb_id)
    if movie_details:
        return jsonify(movie_details), 200
    else:
        return jsonify({"error": "Movie not found"}), 404


@app.route("/reviews/<movie_id>", methods=["GET"])
def get_reviews(movie_id):
    reviews = database.get_movie_reviews(movie_id)
    return jsonify(reviews)


@app.route("/remove_from_backlog/<int:movie_id>", methods=["DELETE"])
@login_required
def remove_from_backlog(movie_id):
    if database.remove_movie_from_backlog(current_user.id, movie_id):
        return jsonify({"success": True, "message": "Movie removed from backlog"}), 200
    else:
        return (
            jsonify(
                {"success": False, "message": "Failed to remove movie from backlog"}
            ),
            500,
        )


@app.route("/get_movies", methods=["GET"])
@login_required
def get_movies():
    page = request.args.get("page", 1, type=int)
    sort_by = request.args.get("sort_by", "vote_average", type=str)
    order = request.args.get("order", "desc", type=str)
    genre = request.args.get("genre", type=str)
    search = request.args.get("search", type=str)
    collection = request.args.get("collection", type=str)

    offset = (page - 1) * MOVIE_LIMIT

    total, movies = database.get_movies(
        MOVIE_LIMIT, offset, sort_by, order, genre, search, collection
    )
    return jsonify({"movies": movies, "total": total})


@app.route("/get_poster/<imdb_id>", methods=["GET"])
@login_required
def get_movie_poster(imdb_id):
    poster_url = database.fetch_movie_poster(imdb_id)
    return jsonify({"poster_url": poster_url})


@app.route("/add_to_backlog", methods=["POST"])
@login_required  # Assuming you want this route protected as well
def add_to_backlog():
    data = request.json
    username = current_user.id  # Using current_user from Flask-Login
    movie_id = data["movie_id"]

    success, message = database.add_to_backlog(username, movie_id)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400  # Use 400 for client-side errors


@app.route("/get_backlog", methods=["GET"])
def get_backlog():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Username is required"}), 400

    backlog_movies, message = database.get_backlog(username)
    if backlog_movies is not None:
        return jsonify({"movies": backlog_movies}), 200
    else:
        return jsonify({"error": message}), 500


@app.route("/mark_watched", methods=["POST"])
def mark_watched():
    data = request.get_json()
    username = data["username"]
    movie_id = data["movie_id"]
    review = data.get("review")
    rating = data.get("rating")

    database.remove_from_backlog(username, movie_id)
    success, message = database.mark_movie_as_watched(
        username, movie_id, review, rating
    )
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 500


@app.route("/get_user_profile", methods=["GET"])
def get_user_profile():
    username = request.args.get("username")
    user = database.get_user_profile(username)
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"message": "User not found"}), 404


@app.route("/get_watched_movies", methods=["GET"])
def get_watched_movies():
    username = request.args.get("username")
    movies = database.get_watched_movies(username)
    return jsonify({"movies": movies}), 200


@app.route("/update_bio", methods=["POST"])
def update_bio():
    data = request.get_json()
    username = data["username"]
    bio = data["bio"]
    success, message = database.update_bio(username, bio)
    if success:
        return jsonify({"message": "Bio updated successfully"}), 200
    else:
        return jsonify({"error": message}), 500


@app.route("/update_movie_review", methods=["POST"])
def handle_update_movie_review():
    data = request.get_json()
    username = data["username"]
    movie_id = data["movie_id"]
    review = data["review"]
    rating = data["rating"]
    result = database.update_movie_review(username, movie_id, review, rating)
    if result:
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "error"}), 500


@app.route("/get_collections")
def get_collections():
    collections = database.get_collections()
    if collections:
        return jsonify(collections=collections), 200
    else:
        return jsonify(message="No collections found"), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
