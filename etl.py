import requests
import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# API Endpoints
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"
LASTFM_ARTIST_URL = "http://ws.audioscrobbler.com/2.0/"

def get_spotify_token():
    auth = (os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET"))
    response = requests.post(
        SPOTIFY_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=auth
    )

    print("Spotify Token Response:")
    print("Status code:", response.status_code)
    print("Response body:", response.text)

    return response.json()["access_token"]

def get_spotify_tracks(genre, limit=10):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": genre, "type": "track", "limit": limit}
    r = requests.get(SPOTIFY_SEARCH_URL, headers=headers, params=params)
    return r.json()["tracks"]["items"]

def get_lastfm_genre(artist_name):
    params = {
        "method": "artist.getinfo",
        "artist": artist_name,
        "api_key": os.getenv("LASTFM_API_KEY"),
        "format": "json"
    }
    r = requests.get(LASTFM_ARTIST_URL, params=params)
    tags = r.json().get("artist", {}).get("tags", {}).get("tag", [])
    return tags[0]["name"] if tags else None

def connect_db():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

def insert_data(tracks, current_genre):
    db = connect_db()
    cursor = db.cursor(buffered=True)

    for track in tracks:
        artist_name = track["artists"][0]["name"]
        song_title = track["name"]
        genre = get_lastfm_genre(artist_name)
        genre_from_lastfm = get_lastfm_genre(artist_name)
        if genre_from_lastfm in ["mierda", "mexico", "unknown", ""] or not genre_from_lastfm:
            genre = current_genre.lower()  # use the searched genre if Last.fm gives trash list
        else:
            genre = genre_from_lastfm
            image_url = track["album"]["images"][0]["url"] if track["album"]["images"] else None

        cursor.execute("INSERT IGNORE INTO artists (name, genre, image_url) VALUES (%s, %s, %s)", 
                       (artist_name, genre, image_url))
        db.commit()

        cursor.execute("SELECT id FROM artists WHERE name = %s", (artist_name,))
        artist_id = cursor.fetchone()[0]

        cursor.execute("INSERT INTO songs (title, artist_id, genre, bpm, duration, mood) VALUES (%s, %s, %s, %s, %s, %s)", 
                       (song_title, artist_id, genre, None, track["duration_ms"] // 1000, None))

    db.commit()
    cursor.close()
    db.close()

if __name__ == "__main__":
    genres = ["reggaeton", "house", "edm"]
    for genre in genres:
        print(f"Fetching tracks for genre: {genre}")
        tracks = get_spotify_tracks(genre, limit=10)
        insert_data(tracks, genre)

