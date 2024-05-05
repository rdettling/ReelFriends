CREATE TABLE friends (
    user_a VARCHAR(255),
    user_b VARCHAR(255),
    PRIMARY KEY (user_a, user_b),
    FOREIGN KEY (user_a) REFERENCES users(username),
    FOREIGN KEY (user_b) REFERENCES users(username)
);