from flask import Blueprint, request, jsonify
from functools import wraps
import bcrypt
import jwt
import os
import re
from datetime import datetime, timedelta
from backend.utils.db import create_user, get_user_by_email, get_user_by_id

auth_bp = Blueprint('auth', __name__)

# Get secret key from environment
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')


# Password hashing functions

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password as string
    """
    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against a hash
    
    Args:
        password: Plain text password to verify
        hashed: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


# JWT token functions

def generate_token(user_id: int) -> str:
    """
    Generate a JWT token for a user
    
    Args:
        user_id: User's ID
        
    Returns:
        JWT token as string
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError('Token has expired')
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError('Invalid token')


# Authentication decorator

def require_auth(f):
    """
    Decorator to protect routes that require authentication
    
    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route():
            # Access current_user_id from request
            user_id = request.current_user_id
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'success': False, 'error': 'No authorization token provided'}), 401
        
        # Extract token from "Bearer <token>" format
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'success': False, 'error': 'Invalid authorization header format'}), 401
        
        # Verify token
        try:
            payload = verify_token(token)
            request.current_user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


# Validation functions

def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long'
    
    return True, ''


# Authentication endpoints

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request Body:
        {
            "email": "user@example.com",
            "username": "username",
            "password": "password123"
        }
    
    Response:
        {
            "success": true,
            "message": "User registered successfully"
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not email or not username or not password:
            return jsonify({'success': False, 'error': 'Email, username, and password are required'}), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        # Validate password strength
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Check if email already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return jsonify({'success': False, 'error': 'Email already registered'}), 400
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        user_id = create_user(email, username, password_hash)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully'
        }), 201
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login a user
    
    Request Body:
        {
            "email": "user@example.com",
            "password": "password123"
        }
    
    Response:
        {
            "success": true,
            "token": "jwt_token_here",
            "user": {
                "id": 1,
                "email": "user@example.com",
                "username": "username"
            }
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password are required'}), 400
        
        # Get user by email
        user = get_user_by_email(email)
        
        if not user:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = generate_token(user['id'])
        
        # Return success with token and user info (exclude password_hash)
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'username': user['username']
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """
    Logout a user
    
    Headers:
        Authorization: Bearer <token>
    
    Response:
        {
            "success": true,
            "message": "Logged out successfully"
        }
    
    Note: This is a simple logout that relies on client-side token removal.
    For enhanced security, implement a token blacklist.
    """
    try:
        # In a simple implementation, logout is handled client-side by removing the token
        # For enhanced security, you could implement a token blacklist here
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        print(f"Logout error: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
