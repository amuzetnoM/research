"""
Research Environment Setup Package

This package provides a comprehensive setup system for the research environment,
handling Python installation, dependency management, environment configuration,
and Docker preparation.
"""

__version__ = "1.0.0"

from .setup_manager import run_setup
from .dependency_manager import check_dependencies, install_dependencies
from .environment_manager import check_environment, setup_environment
from .docker_prep import check_docker_prerequisites, prepare_for_docker

__all__ = [
    'run_setup',
    'check_dependencies',
    'install_dependencies',
    'check_environment',
    'setup_environment',
    'check_docker_prerequisites',
    'prepare_for_docker',
    '__version__'
]
