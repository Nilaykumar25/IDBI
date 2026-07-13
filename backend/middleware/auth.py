"""
Authentication middleware for Flask API.
Validates JWT tokens from Supabase Auth on protected endpoints.
"""
from functools import wraps
from flask import request, jsonify
from supabase import create_client, Client
from config import Config

# Initialize Supabase client
supabase: Client = None

def init_supabase():
    """Initialize Supabase client with configuration."""
    global supabase
    if Config.SUPABASE_URL and Config.SUPABASE_KEY:
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    else:
        print("⚠ Supabase not configured - auth middleware will reject all requests")

def require_auth(f):
    """
    Decorator for Flask routes requiring authentication.
    Validates JWT token from Authorization header.
    Returns 401 if token is missing or invalid.
    
    Usage:
        @app.route('/api/scores', methods=['POST'])
        @require_auth
        def compute_score():
            user = request.user
            # ... implementation
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Missing or invalid authorization header'
            }), 401
        
        # Extract token
        token = auth_header.split(' ')[1]
        
        try:
            # Verify JWT token with Supabase
            if not supabase:
                init_supabase()
            
            if not supabase:
                return jsonify({
                    'success': False,
                    'error': 'Authentication service not configured'
                }), 500
            
            # Get user from token
            user_response = supabase.auth.get_user(token)
            
            if not user_response or not user_response.user:
                return jsonify({
                    'success': False,
                    'error': 'Invalid token'
                }), 401
            
            # Attach user to request context
            request.user = user_response.user
            
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Token verification failed'
            }), 401
    
    return decorated_function
