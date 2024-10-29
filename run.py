from dotenv import load_dotenv
from app import create_app
from flask_cors import CORS

if __name__ == "__main__":
    load_dotenv()
    app = create_app()
    app.run(debug=True, threaded=True)
