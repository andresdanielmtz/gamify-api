from flask import Flask
from .database import init_db
from dotenv import load_dotenv
import os
from datetime import timedelta
from .auth.routes import auth_bp
from .api.routes import api_bp
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    load_dotenv()

    # Basic CORS configuration
    CORS(
        app,
        resources={
            r"/*": {
                "origins": ["http://localhost:5173"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True,
            }
        },
    )

    # Development session configuration
    app.config.update(
        SECRET_KEY="EWBAITE",
        SESSION_COOKIE_SECURE=False,  # Set to False for HTTP
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        SESSION_COOKIE_NAME="gamify_session",
        SESSION_COOKIE_PATH="/",
        SESSION_COOKIE_DOMAIN=None,  # Important for localhost
    )

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/")
    def home():
        return "Hello, World! \nThis is the backend of the application."


    # Simplified security headers for development
    @app.after_request
    def add_security_headers(response):
        # Set CORS headers
        response.headers.update(
            {
                "Access-Control-Allow-Origin": "http://localhost:5173",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            }
        )
        return response

    return app
