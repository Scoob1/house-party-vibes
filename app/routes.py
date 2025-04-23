from flask import Blueprint, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

api_routes = Blueprint("api_routes", __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

@api_routes.route("/songs", methods=["GET"])
def get_songs():
    genre = request.args.get("genre")
    query = """
        SELECT songs.id, songs.title, songs.genre, songs.duration,
               artists.name AS artist_name
        FROM songs
        JOIN artists ON songs.artist_id = artists.id
    """
    params = []

    if genre:
        query += " WHERE songs.genre = %s"
        params.append(genre)

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, params)
    songs = cursor.fetchall()
    cursor.close()
    db.close()

    return jsonify(songs)

