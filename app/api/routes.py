from flask import Blueprint, jsonify
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

@api_bp.route("/igdb-covers", methods=['GET'])
@login_required
def igdb_proxy():
    conn = http.client.HTTPSConnection("api.igdb.com")
    payload = "fields name,cover.*,summary,first_release_date;\nwhere category = 0 & platforms = 48;\nsort rating desc;\nlimit 30;"
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
    
    return json.dumps(games)
