from flask import Flask
from flask_cors import CORS
from .database import init_db
from dotenv import load_dotenv
import os

def create_app():
    app = Flask(__name__)
    
    # Configure CORS properly
    CORS(app, 
         supports_credentials=True,
         resources={
             r"/*": {
                 "origins": ["http://127.0.0.1:5173", "http://localhost:5173"],  # Add your frontend URL
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type"],
                 "expose_headers": ["Access-Control-Allow-Origin"],
                 "supports_credentials": True
             }
         })
    
    # Session configuration
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'your-secret-key-here'),
        SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=1800  # 30 minutes
    )

    # Register blueprints
    from .auth.routes import auth_bp
    from .api.routes import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    app.route('/')(lambda: 'Hello, World! \n This is the backend of the application. \n Please refer to the documentation for more information.')

    # Initialize database
    with app.app_context():
        init_db()

    return app