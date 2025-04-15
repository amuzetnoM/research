"""
Authentication and authorization utilities for the API.
"""

import logging
from functools import wraps
from flask import request, abort, jsonify
import jwt
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def authenticate(func):
    """
    Authentication decorator that verifies the API key in request headers.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        from inference_api.config import Config
        config = Config()
        
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != config.API_KEY:
            logger.warning(f"Unauthorized access attempt from {request.remote_addr}")
            abort(401)  # Unauthorized
        return func(*args, **kwargs)
    return wrapper

def authorize(role):
    """
    Authorization decorator that verifies the user role in request headers.
    
    Args:
        role: Required role for the endpoint
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_role = request.headers.get('X-User-Role')
            if not user_role or user_role != role:
                logger.warning(f"Forbidden access attempt from {request.remote_addr} with role {user_role}")
                abort(403)  # Forbidden
            return func(*args, **kwargs)
        return wrapper
    return decorator

def generate_token(user_id, role, secret_key, expires_in=3600):
    """
    Generate a JWT token for authentication.
    
    Args:
        user_id: User identifier
        role: User role
        secret_key: Secret key for signing
        expires_in: Token expiration time in seconds (default: 1 hour)
        
    Returns:
        JWT token string
    """
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_token(token, secret_key):
    """
    Verify a JWT token.
    
    Args:
        token: JWT token string
        secret_key: Secret key for verification
        
    Returns:
        Decoded payload or None if invalid
    """
    try:
        return jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.PyJWTError as e:
        logger.warning(f"Token verification failed: {str(e)}")
        return None
