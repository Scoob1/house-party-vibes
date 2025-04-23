CREATE DATABASE IF NOT EXISTS house_party_vibes;
USE house_party_vibes;

CREATE TABLE IF NOT EXISTS artists (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  genre VARCHAR(100),
  image_url TEXT
);

CREATE TABLE IF NOT EXISTS songs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(100) NOT NULL,
  artist_id INT,
  genre VARCHAR(100),
  bpm INT,
  duration INT,
  mood VARCHAR(50),
  FOREIGN KEY (artist_id) REFERENCES artists(id)
);
