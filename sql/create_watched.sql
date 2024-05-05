CREATE TABLE watched (
    username VARCHAR(255),
    movie_id INTEGER,
    review TEXT,
    rating INTEGER CHECK (
        rating >= 0
        AND rating <= 10
    ),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (username, movie_id),
    FOREIGN KEY (username) REFERENCES users(username),
    FOREIGN KEY (movie_id) REFERENCES movies(id)
);