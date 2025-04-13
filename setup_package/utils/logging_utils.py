"""
Logging Utilities

Provides logging-related utility functions for the setup process.
"""

import logging
import os
import sys
from pathlib import Path

def setup_logging(log_file=None, verbose=False):
    """
    Set up logging with consistent formatting.
    
    Args:
        log_file (str): Path to log file
        verbose (bool): Enable verbose output
        
    Returns:
        logging.Logger: Configured logger
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create handlers list
    handlers = [logging.StreamHandler()]
    
    # Add file handler if log file is specified
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    # Return logger
    return logging.getLogger('setup')

def get_progress_logger():
    """
    Get a logger for progress reporting.
    
    Returns:
        logging.Logger: Logger for progress reporting
    """
    logger = logging.getLogger('progress')
    
    # Configure logger if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    
    return logger

def log_section(section_name):
    """
    Log a section header.
    
    Args:
        section_name (str): Name of the section
    """
    logger = logging.getLogger('setup')
    
    border = "=" * (len(section_name) + 4)
    logger.info(f"\n{border}")
    logger.info(f"| {section_name} |")
    logger.info(f"{border}\n")
