CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    password TEXT,
    interests INT[],
    visible Boolean,
    role TEXT
);


CREATE TABLE topic (
    id SERIAL PRIMARY KEY,
    header TEXT,
    content TEXT,
    sender TEXT,
    tag TEXT,
    score INT,
    visible Boolean
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    content TEXT,
    sender TEXT,
    topic_id INT,
    visible Boolean
);

CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    subject TEXT,
    total TEXT  
);

CREATE TABLE block_list (
    id SERIAL PRIMARY KEY,
    name TEXT,
    category TEXT,
    blocked_at TIMESTAMPTZ,
    duration INTERVAL
);