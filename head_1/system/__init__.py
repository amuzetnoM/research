"""
AI Research Environment Setup Package

This package provides utilities for setting up and configuring
the AI research environment, including Docker configuration,
GPU detection, monitoring, and diagnostics.
"""

import logging
from pathlib import Path

# Package version
__version__ = "0.1.0"

# Configure package-level logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('setup')

# Package root directory
PACKAGE_DIR = Path(__file__).parent
PROJECT_ROOT = PACKAGE_DIR.parent

# Import key functions from setup module
from .setup import (
    parse_arguments,
    check_prerequisites,
    detect_gpu,
    ensure_directory_structure,
    install_python_dependencies,
    setup_docker_environment,
    setup_monitoring_stack,
    create_utils_diagnostic_tool,
    main,
    make_executable,  # Added missing function that's used elsewhere
    cleanup_unnecessary_files  # Added missing function that's used elsewhere
)

__all__ = [
    'parse_arguments',
    'check_prerequisites',
    'detect_gpu',
    'ensure_directory_structure',
    'install_python_dependencies',
    'setup_docker_environment',
    'setup_monitoring_stack',
    'create_utils_diagnostic_tool',
    'main',
    'make_executable',  # Added to __all__ list
    'cleanup_unnecessary_files',  # Added to __all__ list
    'PACKAGE_DIR',
    'PROJECT_ROOT',
    '__version__'
]
