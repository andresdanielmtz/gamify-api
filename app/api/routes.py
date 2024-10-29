from flask import Blueprint, request, jsonify
import http.client
import json
import os
import sqlite3
import time
import random


api_bp = Blueprint("api", __name__)


@api_bp.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@api_bp.route("/sample")
def sample():
    return str(random.randint(0, 100))


# Connect to SQLite database (or create it if it doesn't exist)
def get_db_connection():
    conn = sqlite3.connect("game_cache.db")
    conn.row_factory = sqlite3.Row
    return conn


# Initialize the database
def initialize_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS games_cache (
            id INTEGER PRIMARY KEY,
            name TEXT,
            summary TEXT,
            release_date TEXT,
            cover_url TEXT,
            last_updated TIMESTAMP
        )
        """
    )
    conn.commit()
    print("games_cache table initialized")  # Debugging statement
    conn.close()

# Call this once at startup

CACHE_EXPIRY = 86400  # Cache expiry time in seconds (e.g., 1 day)


def fetch_game_from_cache(game_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM games_cache WHERE id = ? AND last_updated > ?",
        (game_id, time.time() - CACHE_EXPIRY),
    )
    game = cur.fetchone()
    conn.close()
    return game


def update_cache(game_data):
    conn = get_db_connection()
    conn.execute(
        """INSERT OR REPLACE INTO games_cache (id, name, summary, release_date, cover_url, last_updated)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            game_data.get("id"),
            game_data.get("name"),
            game_data.get("summary", None),  # Use None if summary is missing
            game_data.get("first_release_date", None),
            (
                game_data["cover"]["url"]
                if "cover" in game_data and "url" in game_data["cover"]
                else None
            ),
            time.time(),
        ),
    )
    conn.commit()
    print("Cache updated")
    conn.close()


@api_bp.route("games/<int:id>", methods=["GET"])
def get_game(id):
    conn = http.client.HTTPSConnection("api.igdb.com")
    payload = f"fields name,cover.*,summary,first_release_date;\nwhere id = {id};"
    headers = {
        "Client-ID": os.getenv("CLIENT_ID"),
        "Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}",
        "Content-Type": "text/plain",
    }
    conn.request("POST", "/v4/games", payload, headers)
    res = conn.getresponse()
    data = res.read()
    game = json.loads(data.decode("utf-8"))[0]

    if "cover" in game and "url" in game["cover"]:
        game["cover"]["url"] = game["cover"]["url"].replace("t_thumb", "t_cover_big")

    return json.dumps(game)


@api_bp.route("/igdb-proxy", methods=["GET"])
def igdb_proxy():
    category = request.args.get("category")
    sort_by = request.args.get("sort_by")
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    platforms = request.args.get("platforms")

    # Check if the data is cached (simplified example: only checks if first game is cached)
    conn = get_db_connection()
    game_in_cache = fetch_game_from_cache(
        category
    )  # Assuming category ID for example, use unique identifier logic as needed

    if game_in_cache:
        return jsonify(dict(game_in_cache))

    # Construct API payload if cache miss
    platform_clause = f"platforms = {platforms}"
    where_clause = f"category = {category} & ({platform_clause})"
    payload = (
        f"fields name,cover.*,summary,first_release_date;\n"
        f"where {where_clause};\n"
        f"sort {sort_by};\n"
        f"limit {limit};\n"
        f"offset {offset};"
    )

    headers = {
        "Client-ID": os.getenv("CLIENT_ID"),
        "Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}",
        "Content-Type": "text/plain",
    }

    conn = http.client.HTTPSConnection("api.igdb.com")
    conn.request("POST", "/v4/games", payload, headers)
    res = conn.getresponse()
    data = res.read()
    games = json.loads(data.decode("utf-8"))

    # Process cover URLs if needed and update cache
    for game in games:
        if "cover" in game and "url" in game["cover"]:
            game["cover"]["url"] = game["cover"]["url"].replace(
                "t_thumb", "t_cover_big"
            )
        update_cache(game)  # Update cache for each game

    return json.dumps(games)


@api_bp.route("/igdb-proxy/<string:name>", methods=["GET"])
def get_game_by_name():
    name = request.args.get("name")
    conn = http.client.HTTPSConnection("api.igdb.com")
    payload = f'fields name,cover.*,summary,first_release_date;\nsearch "{name}";'
    headers = {
        "Client-ID": os.getenv("CLIENT_ID"),
        "Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}",
        "Content-Type": "text/plain",
    }
    conn.request("POST", "/v4/games", payload, headers)
    res = conn.getresponse()
    data = res.read()
    game = json.loads(data.decode("utf-8"))[0]

    if "cover" in game and "url" in game["cover"]:
        game["cover"]["url"] = game["cover"]["url"].replace("t_thumb", "t_cover_big")

    return json.dumps(game)
