"""
Authentication Middleware for Flask API
Provides JWT token validation using Supabase Auth
"""
from functools import wraps
from flask import request, jsonify, current_app
from supabase import create_client, Client
from typing import Optional


def get_supabase_client() -> Client:
    """
    Creates and returns a Supabase client instance.
    
    Returns:
        Supabase client configured with URL and key from Flask config
    
    Raises:
        ValueError: If Supabase configuration is missing
    """
    supabase_url = current_app.config.get('SUPABASE_URL')
    supabase_key = current_app.config.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError(
            "Supabase configuration missing. "
            "Set SUPABASE_URL and SUPABASE_KEY in environment variables."
        )
    
    return create_client(supabase_url, supabase_key)


def extract_token_from_header() -> Optional[str]:
    """
    Extracts JWT token from Authorization header.
    
    Expected header format: "Authorization: Bearer <token>"
    
    Returns:
        JWT token string if present and correctly formatted, None otherwise
    """
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return None
    
    # Check if header follows "Bearer <token>" format
    parts = auth_header.split()
    
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    
    return parts[1]


def require_auth(f):
    """
    Decorator for Flask routes requiring authentication.
    
    Validates JWT token from Authorization header using Supabase Auth.
    Returns 401 Unauthorized if token is missing, malformed, or invalid.
    Attaches authenticated user info to Flask request context.
    
    Usage:
        @app.route('/api/scores', methods=['POST'])
        @require_auth
        def compute_score():
            user = request.user  # Access authenticated user
            # ... implementation
    
    Args:
        f: Flask route function to protect
    
    Returns:
        Decorated function with authentication enforcement
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract token from Authorization header
        token = extract_token_from_header()
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Missing or invalid authorization header. Expected: Authorization: Bearer <token>'
            }), 401
        
        try:
            # Get Supabase client
            supabase = get_supabase_client()
            
            # Verify token with Supabase Auth
            response = supabase.auth.get_user(token)
            
            # Check if user was returned
            if not response or not response.user:
                return jsonify({
                    'success': False,
                    'error': 'Invalid or expired token'
                }), 401
            
            # Attach user to request context for route handler access
            request.user = response.user
            
            # Call the original route function
            return f(*args, **kwargs)
            
        except Exception as e:
            # Log error for debugging
            print(f"Authentication error: {str(e)}")
            
            return jsonify({
                'success': False,
                'error': 'Token verification failed'
            }), 401
    
    return decorated_function
