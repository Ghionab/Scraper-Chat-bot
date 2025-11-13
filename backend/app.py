from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os


def create_app():
    """
    Create and configure the Flask application
    
    Returns:
        Flask application instance
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DATABASE'] = os.getenv('DATABASE_PATH', 'database.db')
    
    # Enable CORS for all routes
    CORS(app)
    
    # Register blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.chat import chat_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    
    # Initialize database on app startup
    from backend.utils.db import init_db
    with app.app_context():
        init_db()
        print("Database initialized successfully")
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
