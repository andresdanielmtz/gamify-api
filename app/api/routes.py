from flask import Blueprint, request
import http.client
import json
import random
import os
from ..auth.utils import login_required
from ..cache import cache
from ..login import login_manager

api_bp = Blueprint("api", __name__)


@api_bp.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@api_bp.route("/sample")
@login_required
def sample():
    return str(random.randint(0, 100))


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
@cache.cached(timeout=300, query_string=True)  # Cache for 5 minutes
def igdb_proxy():
    category = request.args.get("category")
    sort_by = request.args.get("sort_by")
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    platforms = request.args.get("platforms")
    
    print(f"Sort by: {sort_by}")

    if not limit:
        limit = 100


    platform_clause = f"platforms = {platforms}" 
    if category == "1":
        print("Category is -1")
        category_clause = ""
    elif category == "-1": 
        print("Category is -1")
        category_clause = "category = 1 &"
    else:
        category_clause = f"category = {category} &"

    where_clause = f"{category_clause} ({platform_clause})"

    payload = (
        f"fields name,cover.*,summary,first_release_date;\n"
        f"where {where_clause};\n"
        f"limit {limit};\n"
        f"sort {sort_by};\n"
        f"offset {offset};"
 
    )
    
    print(f"Payload: {payload}") # : ) 
    
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

    for game in games:
        if "cover" in game and "url" in game["cover"]:
            game["cover"]["url"] = game["cover"]["url"].replace(
                "t_thumb", "t_cover_big"
            )

    return json.dumps(games)
