CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    password TEXT
);


CREATE TABLE topic (
    id SERIAL PRIMARY KEY,
    header TEXT,
    content TEXT,
    sender TEXT,
    tag TEXT
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    content TEXT,
    sender TEXT,
    topic_id INT
);

