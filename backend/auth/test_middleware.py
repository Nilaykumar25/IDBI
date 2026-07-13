"""
Test Authentication Middleware - Bypasses Supabase Auth for Local Testing
USE ONLY FOR DEVELOPMENT/TESTING - NOT FOR PRODUCTION
"""
from functools import wraps
from flask import request, jsonify, current_app


class MockUser:
    """Mock user object for testing"""
    def __init__(self):
        self.id = "test-user-id-12345"
        self.email = "testuser@example.com"
        self.created_at = "2026-01-01T00:00:00Z"


def require_auth_test(f):
    """
    Test version of authentication decorator that bypasses Supabase validation.
    
    Accepts any Bearer token and attaches a mock user to the request.
    
    SECURITY WARNING: This should ONLY be used in development/testing mode.
    Never deploy this to production!
    
    Usage:
        from auth.test_middleware import require_auth_test as require_auth
        
        @app.route('/api/scores', methods=['POST'])
        @require_auth
        def compute_score():
            user = request.user  # Access mock user
            # ... implementation
    
    Args:
        f: Flask route function to protect
    
    Returns:
        Decorated function with mock authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        # Still require Authorization header to be present
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Missing or invalid authorization header. Expected: Authorization: Bearer <token>'
            }), 401
        
        # Extract token (but don't validate it)
        token = auth_header.split(' ')[1]
        
        # Check if token is present
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token is required'
            }), 401
        
        # Attach mock user to request
        request.user = MockUser()
        
        # Call the original route function
        return f(*args, **kwargs)
    
    return decorated_function
