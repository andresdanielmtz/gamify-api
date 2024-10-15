from flask import Flask
from dotenv import load_dotenv
import http.client
import os 
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
    
@app.route("/games") 
def games():
    return os.getenv("TEST")

@app.route("/igdb-proxy", methods=['GET'])
def igdb_proxy():
    conn = http.client.HTTPSConnection("api.igdb.com")
    payload = "fields name,category,platforms;\nwhere category = 0 & platforms = 48;\nsort rating desc;\nlimit 30;"
    headers = {
        'Client-ID': os.getenv('VITE_CLIENT_ID'),
        'Authorization': f"Bearer {os.getenv('VITE_ACCESS_TOKEN')}",
        'Content-Type': 'text/plain'
    }
    
    conn.request("POST", "/v4/games", payload, headers)
    res = conn.getresponse()
    data = res.read()
    
    return data.decode("utf-8")

#
if __name__ == "__main__":
    load_dotenv()
    app.run(debug=True)