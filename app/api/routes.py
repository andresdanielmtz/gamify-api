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

@api_bp.route("/igdb-proxy", methods=['GET'])
def igdb_proxy():
    category = request.args.get('category')
    sort_by = request.args.get('sort_by')
    limit = request.args.get('limit')
    offset = request.args.get('offset')
    platforms = request.args.get('platforms')

    # Construct the where_clause to include multiple platforms
    platform_list = platforms.split(',')
    platform_clause = ' | '.join([f'platforms = {platform}' for platform in platform_list])
    where_clause = f"category = {category} & ({platform_clause})"

    # Adjust the payload to include the offset and the reduced limit
    payload = (
        f"fields name,cover.*,summary,first_release_date;\n"
        f"where {where_clause};\n"
        f"sort {sort_by};\n"
        f"limit {limit};\n"
        f"offset {offset};"
    )
    
    headers = {
        'Client-ID': os.getenv('CLIENT_ID'),
        'Authorization': f"Bearer {os.getenv('ACCESS_TOKEN')}",
        'Content-Type': 'text/plain'
    }
    
    conn = http.client.HTTPSConnection("api.igdb.com")
    conn.request("POST", "/v4/games", payload, headers)
    res = conn.getresponse()
    data = res.read()
    games = json.loads(data.decode("utf-8"))

    # Adjust cover URLs if needed
    for game in games:
        if 'cover' in game and 'url' in game['cover']:
            game['cover']['url'] = game['cover']['url'].replace('t_thumb', 't_cover_big')

    return json.dumps(games)


@api_bp.route("/igdb-proxy/<string:name>", methods=['GET'])
def get_game_by_name():
    name = request.args.get('name')
    conn = http.client.HTTPSConnection("api.igdb.com")
    payload = f"fields name,cover.*,summary,first_release_date;\nsearch \"{name}\";"
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