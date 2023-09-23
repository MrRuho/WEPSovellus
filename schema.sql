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
    tag TEXT,
    score INT
);

INSERT INTO topic (header, content, sender, tag, score) VALUES ('Slava ukraini! Foorumin eka!', 'slava ukraini!', 'Tero', 'Sota', 130);
INSERT INTO topic (header, content, sender, tag, score) VALUES ('Seppo takas!', 'Ei tuosta kepin heittelystä tule yhtään mitään.', 'Tuhnu66', 'Urheilu', 80);
INSERT INTO topic (header, content, sender, tag, score) VALUES ('Esittävää taidetta kiitos!', 'Ketä kiinnostaa jotkut epämääriset kakkakipot', 'Summy', 'Tiede', 88 );
INSERT INTO topic (header, content, sender, tag, score) VALUES ('Putinin tee resepti', 'Kiehauta vesi. Kun vesi on 110c niin lisää minttu ja polonium. Anna hautua', 'Tero', 'Sota', 104);
INSERT INTO topic (header, content, sender, tag, score) VALUES ('RTX2090!', 'Nyt muuten pyörii doom!!!', 'Joku_Vaa', 'Teknologia', 98);
INSERT INTO topic (header, content, sender, tag, score) VALUES ('Piirakka resepti?', 'Tietääkö joku hyvää piirakka reseptiä?', 'Saarx88', 'Ruoka', 100);


CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    content TEXT,
    sender TEXT,
    topic_id INT
);

INSERT INTO messages (content, sender, topic_id)
VALUES
  ('Slava Ukraini!', 'Tero', 0),
  ('Slava Ukraini!', 'Tuhnu66', 0),
  ('Slava Ukraini!', 'Summy', 0),
  ('Slava Ukraini!', 'Tero', 0),
  ('Slava Ukraini!', 'Joku_Vaa', 0),
  ('Slava Ukraini!', 'Saarx88', 0),
  ('Täytyypä testata =)', 'Saarx88',3);
