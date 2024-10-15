from flask import Flask, request
from dotenv import load_dotenv
import http.client
import os 
from flask_cors import CORS
import random
import json

app = Flask(__name__)
CORS(app)  

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
    
@app.route("/games") 
def games():
    return random.randint(0,100) # :)

@app.route("/igdb-covers", methods=['GET'])
def igdb_proxy():
    conn = http.client.HTTPSConnection("api.igdb.com")
    payload = "fields name,cover.*,summary;\nwhere category = 0 & platforms = 48;\nsort rating desc;\nlimit 30;"
    headers = {
        'Client-ID': os.getenv('VITE_CLIENT_ID'),
        'Authorization': f"Bearer {os.getenv('VITE_ACCESS_TOKEN')}",
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

if __name__ == "__main__":
    load_dotenv()
    app.run(debug=True)