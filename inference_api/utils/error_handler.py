"""
Enhanced error handling system for the backend
Provides a similar interface to the frontend error handler for consistency.
"""

import sys
import traceback
from enum import Enum
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from inference_api.utils.logger import logger

# Error categories
class ErrorCategory(str, Enum):
    NETWORK = "NETWORK"
    API = "API"
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    VALIDATION = "VALIDATION"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    RESOURCE = "RESOURCE"
    CONFIGURATION = "CONFIGURATION"
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"
    UNKNOWN = "UNKNOWN"

# Operational status
class OperationalStatus(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    NON_OPERATIONAL = "NON_OPERATIONAL"

# Severity levels
class ErrorSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class EnhancedError(Exception):
    """Enhanced Error class for the backend"""
    
    def __init__(self, 
                 message: str,
                 category: ErrorCategory = ErrorCategory.UNKNOWN,
                 operational: OperationalStatus = OperationalStatus.OPERATIONAL,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 code: Optional[str] = None,
                 source: str = "backend",
                 context: Optional[Dict[str, Any]] = None,
                 retryable: bool = True,
                 user_friendly_message: Optional[str] = None,
                 documentation_link: Optional[str] = None,
                 original_error: Optional[Exception] = None):
        """
        Initialize the enhanced error.
        
        Args:
            message: Error message
            category: Error category
            operational: Operational status
            severity: Error severity
            code: Error code
            source: Error source
            context: Error context
            retryable: Whether the operation is retryable
            user_friendly_message: User-friendly message
            documentation_link: Link to documentation
            original_error: Original exception
        """
        super().__init__(message)
        self.message = message
        self.category = category
        self.operational = operational
        self.severity = severity
        self.code = code
        self.source = source
        self.timestamp = datetime.now().isoformat()
        self.context = context or {}
        self.retryable = retryable
        self.user_friendly_message = user_friendly_message or "An unexpected error occurred. Please try again."
        self.documentation_link = documentation_link
        self.original_error = original_error
        self.traceback = traceback.format_exc() if original_error else None
        
        # Log the error
        self._log_error()
    
    def _log_error(self) -> None:
        """Log the error with the appropriate level."""
        error_info = self.to_dict()
        
        # Log with appropriate level based on severity
        if self.severity == ErrorSeverity.LOW:
            logger.info(f"Error: {self.message}", error_info)
        elif self.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"Error: {self.message}", error_info)
        elif self.severity in (ErrorSeverity.HIGH, ErrorSeverity.CRITICAL):
            logger.error(f"Error: {self.message}", error_info)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary."""
        return {
            "message": self.message,
            "category": self.category,
            "operational": self.operational,
            "severity": self.severity,
            "code": self.code,
            "source": self.source,
            "timestamp": self.timestamp,
            "context": self.context,
            "retryable": self.retryable,
            "user_friendly_message": self.user_friendly_message,
            "documentation_link": self.documentation_link,
            "traceback": self.traceback,
            "original_error": str(self.original_error) if self.original_error else None
        }
    
    def to_response(self) -> Dict[str, Any]:
        """Convert the error to an API response."""
        return {
            "status": "error",
            "error": {
                "message": self.message,
                "code": self.code,
                "category": self.category,
                "user_message": self.user_friendly_message,
                "retryable": self.retryable,
                "documentation": self.documentation_link
            }
        }

# Factory for creating common error types
def create_network_error(message: str, **kwargs) -> EnhancedError:
    """Create a network error."""
    return EnhancedError(
        message=message,
        category=ErrorCategory.NETWORK,
        severity=ErrorSeverity.MEDIUM,
        **kwargs
    )

def create_api_error(message: str, **kwargs) -> EnhancedError:
    """Create an API error."""
    return EnhancedError(
        message=message,
        category=ErrorCategory.API,
        severity=ErrorSeverity.MEDIUM,
        **kwargs
    )

def create_validation_error(message: str, **kwargs) -> EnhancedError:
    """Create a validation error."""
    return EnhancedError(
        message=message,
        category=ErrorCategory.VALIDATION,
        severity=ErrorSeverity.LOW,
        operational=OperationalStatus.OPERATIONAL,
        **kwargs
    )

def create_auth_error(message: str, **kwargs) -> EnhancedError:
    """Create an authentication error."""
    return EnhancedError(
        message=message,
        category=ErrorCategory.AUTHENTICATION,
        severity=ErrorSeverity.HIGH,
        **kwargs
    )

def create_internal_error(message: str, **kwargs) -> EnhancedError:
    """Create an internal error."""
    return EnhancedError(
        message=message,
        category=ErrorCategory.INTERNAL,
        severity=ErrorSeverity.HIGH,
        operational=OperationalStatus.NON_OPERATIONAL,
        **kwargs
    )

# Setup global exception handler
def setup_global_exception_handler() -> None:
    """Set up global exception handler."""
    def global_exception_handler(exctype, value, tb):
        """Global exception handler."""
        if issubclass(exctype, KeyboardInterrupt):
            # Call the default handler for KeyboardInterrupt
            sys.__excepthook__(exctype, value, tb)
            return
            
        error = EnhancedError(
            message=str(value),
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.HIGH,
            operational=OperationalStatus.NON_OPERATIONAL,
            context={
                "exception_type": exctype.__name__,
                "traceback": "".join(traceback.format_tb(tb))
            },
            original_error=value
        )
        
        logger.error("Unhandled exception", error.to_dict())
        
        # Call the default excepthook
        sys.__excepthook__(exctype, value, tb)
    
    # Set the exception hook
    sys.excepthook = global_exception_handler

# Create error factories object
error_factory = {
    "network": create_network_error,
    "api": create_api_error,
    "validation": create_validation_error,
    "auth": create_auth_error,
    "internal": create_internal_error
}

# Export constants and functions
__all__ = [
    'ErrorCategory',
    'OperationalStatus',
    'ErrorSeverity',
    'EnhancedError',
    'error_factory',
    'setup_global_exception_handler'
]
