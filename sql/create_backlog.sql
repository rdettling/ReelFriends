CREATE TABLE backlog (
    username TEXT,
    movie_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (username, movie_id),
    FOREIGN KEY (username) REFERENCES users(username),
    FOREIGN KEY (movie_id) REFERENCES movies(id)
);