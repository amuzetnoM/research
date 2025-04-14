"""
Dependency Manager

Handles checking and installing Python dependencies for the research environment.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path
import importlib.util
import pkg_resources

# Get logger
logger = logging.getLogger('setup')

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Essential research packages
ESSENTIAL_PACKAGES = [
    'numpy',
    'pandas',
    'matplotlib',
    'scipy',
    'sklearn',
    'torch',
    'tensorflow',
    'jupyter',
    'jupyterlab',
    'plotly',
    'psutil',
    'pytest',
    'docker',
    'requests'
]

# Additional packages for GPU support
GPU_PACKAGES = [
    'torch==2.0.0+cu118',  # Example with CUDA 11.8 support
    'tensorflow-gpu',
    'cupy-cuda11x'  # For CUDA 11.x
]

def is_package_installed(package_name):
    """
    Check if a package is installed.
    
    Args:
        package_name (str): Name of the package to check
        
    Returns:
        bool: True if installed, False otherwise
    """
    try:
        pkg_resources.get_distribution(package_name)
        return True
    except pkg_resources.DistributionNotFound:
        return False

def check_dependencies():
    """
    Check if all required dependencies are installed.
    
    Returns:
        tuple: (bool, list) - Success flag and list of missing packages
    """
    logger.info("Checking dependencies...")
    
    missing_packages = []
    for package in ESSENTIAL_PACKAGES:
        # Strip version specifiers if any
        package_name = package.split('==')[0].split('>')[0].split('<')[0]
        if not is_package_installed(package_name):
            missing_packages.append(package)
            logger.debug(f"Missing package: {package}")
    
    return len(missing_packages) == 0, missing_packages

def install_dependencies(dependencies=None, upgrade=False):
    """
    Install Python dependencies.
    
    Args:
        dependencies (list): List of dependencies to install. If None, install missing ones.
        upgrade (bool): Whether to upgrade existing packages
        
    Returns:
        bool: True if successful, False otherwise
    """
    if dependencies is None:
        _, missing_packages = check_dependencies()
        if not missing_packages:
            logger.info("All dependencies are already installed.")
            return True
        dependencies = missing_packages
    
    if not dependencies:
        return True
    
    logger.info(f"Installing dependencies: {', '.join(dependencies)}")
    
    pip_args = [sys.executable, "-m", "pip", "install"]
    if upgrade:
        pip_args.append("--upgrade")
    
    pip_args.extend(dependencies)
    
    try:
        process = subprocess.run(
            pip_args,
            check=True,
            capture_output=True,
            text=True
        )
        logger.debug(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        logger.error(e.stderr)
        return False

def install_gpu_dependencies():
    """
    Install GPU-specific dependencies.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Installing GPU-specific dependencies...")
    return install_dependencies(GPU_PACKAGES)

def install_requirements_file():
    """
    Install dependencies from requirements.txt if it exists.
    
    Returns:
        bool: True if successful, False otherwise
    """
    req_file = PROJECT_ROOT / "setup" / "requirements.txt"
    if not req_file.exists():
        logger.warning(f"Requirements file not found: {req_file}")
        return True
    
    logger.info(f"Installing dependencies from {req_file}")
    
    try:
        process = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
            check=True,
            capture_output=True,
            text=True
        )
        logger.debug(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies from requirements.txt: {e}")
        logger.error(e.stderr)
        return False

def check_and_install_dependencies():
    """
    Check and install all dependencies.
    
    Returns:
        bool: True if successful, False otherwise
    """
    # First install from requirements.txt if it exists
    if not install_requirements_file():
        return False
    
    # Then check for any missing essential packages
    deps_ok, missing_deps = check_dependencies()
    if not deps_ok:
        if not install_dependencies(missing_deps):
            return False
    
    return True
