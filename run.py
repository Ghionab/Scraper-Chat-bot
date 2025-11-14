"""
Flask Application Entry Point

This script starts the Flask development server.

Usage:
    python run.py

Environment Variables:
    - SECRET_KEY: Secret key for Flask sessions and JWT tokens
    - OPENAI_API_KEY: OpenAI API key for AI processing
    - DATABASE_PATH: Path to SQLite database file (default: database.db)
    - FLASK_ENV: Flask environment (development/production)
"""

from backend.app import create_app

if __name__ == '__main__':
    app = create_app()
    
    # Run the Flask development server
    # Note: For production, use a WSGI server like Gunicorn
    app.run(debug=True, host='0.0.0.0', port=5000)
