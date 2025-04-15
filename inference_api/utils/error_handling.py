"""
Error handling utilities for the API.
"""

import logging
import traceback
from typing import Dict, Any, Callable
from functools import wraps
from flask import jsonify, request

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base exception for API errors."""
    
    def __init__(self, message: str, status_code: int = 500, details: Any = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary for JSON response."""
        error_dict = {
            "error": self.message,
            "status_code": self.status_code
        }
        if self.details:
            error_dict["details"] = self.details
        return error_dict

def handle_api_errors(app):
    """
    Register error handlers for the Flask app.
    
    Args:
        app: Flask application instance
    """
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Resource not found", "status_code": 404}), 404
    
    @app.errorhandler(500)
    def handle_server_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({"error": "Internal server error", "status_code": 500}), 500

def api_error_handler(func: Callable) -> Callable:
    """
    Decorator to handle exceptions in API routes.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            logger.warning(f"API error: {e.message} (Status: {e.status_code})")
            response = jsonify(e.to_dict())
            response.status_code = e.status_code
            return response
        except Exception as e:
            logger.error(f"Unhandled exception in {func.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            response = jsonify({
                "error": "Internal server error",
                "status_code": 500,
                "path": request.path
            })
            response.status_code = 500
            return response
    
    return wrapper
