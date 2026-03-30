CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    ip_address VARCHAR(45)
);
