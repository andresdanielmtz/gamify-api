from flask import Blueprint, request
import http.client
import json
import random
import os
from ..auth.utils import login_required

api_bp = Blueprint('api', __name__)

@api_bp.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@api_bp.route("/sample")
@login_required
def sample():
    return str(random.randint(0,100))

@api_bp.route("games/<int:id>", methods=['GET'])
def get_game(id):
    conn = http.client.HTTPSConnection("api.igdb.com")
    payload = f"fields name,cover.*,summary,first_release_date;\nwhere id = {id};"
    headers = {
        'Client-ID': os.getenv('CLIENT_ID'),
        'Authorization': f"Bearer {os.getenv('ACCESS_TOKEN')}",
        'Content-Type': 'text/plain'
    }
    conn.request("POST", "/v4/games", payload, headers)
    res = conn.getresponse()
    data = res.read()
    game = json.loads(data.decode("utf-8"))[0]
    
    if 'cover' in game and 'url' in game['cover']:
        game['cover']['url'] = game['cover']['url'].replace('t_thumb', 't_cover_big')
    
    return json.dumps(game)

@api_bp.route("/igdb-covers", methods=['GET'])
def igdb_proxy():
    # Default filters
    category = 1
    platforms = 49
    sort_by = "rating desc"
    limit = 50  # Increased limit

    # Optional filters from query parameters
    category = request.args.get('category', category)
    platforms = request.args.get('platforms', platforms)
    sort_by = request.args.get('sort_by', sort_by)
    limit = request.args.get('limit', limit)

    conn = http.client.HTTPSConnection("api.igdb.com")
    payload = f"fields name,cover.*,summary,first_release_date;\nwhere category = {category} & platforms = {platforms};\nsort {sort_by};\nlimit {limit};"
    headers = {
        'Client-ID': os.getenv('CLIENT_ID'),
        'Authorization': f"Bearer {os.getenv('ACCESS_TOKEN')}",
        'Content-Type': 'text/plain'
    }
    conn.request("POST", "/v4/games", payload, headers)
    res = conn.getresponse()
    data = res.read()
    games = json.loads(data.decode("utf-8"))

    
    for game in games:
        if 'cover' in game and 'url' in game['cover']:
            game['cover']['url'] = game['cover']['url'].replace('t_thumb', 't_cover_big')
    print(f"Games: {games}")
    return json.dumps(games)
