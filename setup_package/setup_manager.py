"""
Setup Manager

Orchestrates the entire setup process, calling the appropriate modules
in the correct order to ensure a successful setup.
"""

import logging
import os
import platform
import sys
from pathlib import Path

from . import dependency_manager
from . import environment_manager
from . import docker_prep
from .utils import system_utils

# Get logger
logger = logging.getLogger('setup')

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

def run_setup(
    skip_python=False,
    skip_deps=False,
    skip_docker_prep=False,
    force_gpu=False,
    disable_gpu=False,
    enable_monitoring=False,
    verbose=False
):
    """
    Run the complete setup process.
    
    Args:
        skip_python (bool): Skip Python environment setup
        skip_deps (bool): Skip dependency installation
        skip_docker_prep (bool): Skip Docker preparation
        force_gpu (bool): Force GPU configuration
        disable_gpu (bool): Disable GPU configuration
        enable_monitoring (bool): Enable monitoring setup
        verbose (bool): Enable verbose output
        
    Returns:
        bool: True if setup was successful, False otherwise
    """
    logger.info(f"Starting setup with Python {platform.python_version()} on {platform.system()}")
    
    # Step 1: Check if we're running with admin/root privileges and warn if not
    if not system_utils.is_admin() and not system_utils.request_admin_permission():
        logger.warning("Running without admin/root privileges. Some operations may fail.")
    
    # Step 2: Setup Python environment if not skipped
    if not skip_python:
        logger.info("Setting up Python environment...")
        if not environment_manager.setup_python_environment():
            logger.error("Failed to setup Python environment.")
            return False
    
    # Step 3: Check and install dependencies if not skipped
    if not skip_deps:
        logger.info("Checking and installing dependencies...")
        if not dependency_manager.check_and_install_dependencies():
            logger.error("Failed to install required dependencies.")
            return False
    
    # Step 4: Setup environment (create directories, configuration files, etc.)
    logger.info("Setting up research environment...")
    if not environment_manager.setup_environment(
        use_gpu=not disable_gpu, 
        force_gpu=force_gpu,
        enable_monitoring=enable_monitoring
    ):
        logger.error("Failed to setup research environment.")
        return False
    
    # Step 5: Prepare for Docker if not skipped
    if not skip_docker_prep:
        logger.info("Preparing for Docker...")
        if not docker_prep.prepare_for_docker(use_gpu=not disable_gpu):
            logger.error("Failed to prepare for Docker deployment.")
            return False
    
    # Create run script for starting the environment
    if not docker_prep.create_run_script():
        logger.error("Failed to create run script.")
        return False
    
    logger.info("Setup completed successfully!")
    return True
