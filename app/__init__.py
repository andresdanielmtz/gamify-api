from flask import Flask
from flask_cors import CORS
from .database import init_db
from dotenv import load_dotenv
import os
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    load_dotenv()
    app.secret_key = "EWBAITE"
    
    
    # CORS configuration
    CORS(app,
        supports_credentials=True,
        resources={
            r"/*": {
                "origins": ["http://127.0.0.1:5173", "http://localhost:5173"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type"],
                "expose_headers": ["Access-Control-Allow-Credentials"],  # Changed from Allow-Origin
                "supports_credentials": True
            }
        })
    
    # Session configuration
    app.config.update(
        SECRET_KEY=os.getenv('TEST', ':)'),
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        SESSION_COOKIE_NAME='gamify_session',
        SESSION_COOKIE_PATH='/',
    )
    

    # Register blueprints
    from .auth.routes import auth_bp
    from .api.routes import api_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Root route
    app.route('/')(lambda: 'Hello, World! \n This is the backend of the application. \n Please refer to the documentation for more information.')
    
    # Initialize database
    with app.app_context():
        init_db()
    
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    return app