"""
Logger utility for consistent logging across the backend application.
Provides a similar interface to the frontend logger for consistency.
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, Union, List

# Log levels mapping
LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

class Logger:
    """Backend logger with similar interface to the frontend logger."""
    
    def __init__(self, name: str = "backend", 
                 level: str = "info", 
                 log_to_file: bool = True,
                 log_dir: Optional[str] = None,
                 max_file_size: int = 10485760,  # 10 MB
                 backup_count: int = 5):
        """
        Initialize the logger.
        
        Args:
            name: Logger name
            level: Log level (debug, info, warning, error, critical)
            log_to_file: Whether to log to file
            log_dir: Directory for log files
            max_file_size: Maximum log file size in bytes
            backup_count: Number of backup files to keep
        """
        self.name = name
        self.level = LOG_LEVELS.get(level.lower(), logging.INFO)
        
        # Create the logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)
        
        # Remove existing handlers to avoid duplicate logs
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Add file handler if requested
        if log_to_file:
            if log_dir is None:
                log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
            
            # Create log directory if it doesn't exist
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            
            # Create rotating file handler
            from logging.handlers import RotatingFileHandler
            log_file = os.path.join(log_dir, f"{name}.log")
            file_handler = RotatingFileHandler(
                log_file, 
                maxBytes=max_file_size, 
                backupCount=backup_count
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def _format_context(self, context: Any) -> str:
        """Format context for logging."""
        if context is None:
            return ""
            
        try:
            if isinstance(context, dict):
                return json.dumps(context)
            elif isinstance(context, (list, tuple)):
                return json.dumps(list(context))
            elif isinstance(context, Exception):
                return f"{type(context).__name__}: {str(context)}"
            else:
                return str(context)
        except Exception as e:
            return f"[Error formatting context: {e}] {str(context)}"
    
    def debug(self, message: str, context: Any = None) -> None:
        """Log a debug message."""
        if context:
            self.logger.debug(f"{message} | Context: {self._format_context(context)}")
        else:
            self.logger.debug(message)
    
    def info(self, message: str, context: Any = None) -> None:
        """Log an info message."""
        if context:
            self.logger.info(f"{message} | Context: {self._format_context(context)}")
        else:
            self.logger.info(message)
    
    def warn(self, message: str, context: Any = None) -> None:
        """Log a warning message."""
        if context:
            self.logger.warning(f"{message} | Context: {self._format_context(context)}")
        else:
            self.logger.warning(message)
    
    def warning(self, message: str, context: Any = None) -> None:
        """Alias for warn."""
        self.warn(message, context)
    
    def error(self, message: str, context: Any = None) -> None:
        """Log an error message."""
        if context:
            self.logger.error(f"{message} | Context: {self._format_context(context)}")
        else:
            self.logger.error(message)
    
    def critical(self, message: str, context: Any = None) -> None:
        """Log a critical message."""
        if context:
            self.logger.critical(f"{message} | Context: {self._format_context(context)}")
        else:
            self.logger.critical(message)

# Create and export a default logger instance
logger = Logger()

# Export the Logger class for extending if needed
def create_logger(name: str, level: str = "info", **kwargs) -> Logger:
    """Create a new logger instance."""
    return Logger(name=name, level=level, **kwargs)
