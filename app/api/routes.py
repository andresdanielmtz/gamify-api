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
    # Lower the limit for each page to improve response time
    limit = int(request.args.get('limit', 20))  # Default to 20 for effective pagination
    offset = int(request.args.get('offset', 0))  # Offset for pagination

    # Other query parameters as before
    category = request.args.get('category', 1)
    platforms = request.args.get('platforms', 49)
    sort_by = request.args.get('sort_by', "rating desc")

    conn = http.client.HTTPSConnection("api.igdb.com")
    
    # Build the conditions for the where clause
    conditions = []
    if int(category) >= 0:
        conditions.append(f"category = {category}")
    if int(platforms) >= 0:
        conditions.append(f"platforms = {platforms}")
    
    where_clause = " & ".join(conditions) if conditions else "1=1"
    
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
    
    conn.request("POST", "/v4/games", payload, headers)
    res = conn.getresponse()
    data = res.read()
    games = json.loads(data.decode("utf-8"))

    # Adjust cover URLs if needed
    for game in games:
        if 'cover' in game and 'url' in game['cover']:
            game['cover']['url'] = game['cover']['url'].replace('t_thumb', 't_cover_big')

    return json.dumps(games)
