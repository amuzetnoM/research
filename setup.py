#!/usr/bin/env python3
"""
Automated Setup Script for Research Environment

This script handles Python installation, dependency setup, Docker configuration,
and GPU detection for the research environment.

Usage:
    python setup.py [options]

Options:
    --verbose             Enable verbose output
    --skip-python         Skip Python environment setup
    --skip-deps           Skip dependency installation
    --skip-env-setup      Skip environment setup
    --skip-docker         Skip Docker setup and checks
    --gpu                 Force GPU configuration
    --no-gpu              Disable GPU configuration
    --force               Force reinstallation of dependencies
    --no-admin            Run without admin privileges (prevents automatic elevation)
"""


import argparse
import contextlib
import hashlib
import json
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
import tarfile
import ctypes
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Set

# Initialize these before they're used
HAS_NUMPY = False
HAS_MATPLOTLIB = False

with contextlib.suppress(ImportError):
    import numpy as np
    HAS_NUMPY = True
with contextlib.suppress(ImportError):
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True

# Initialize logging early so it can be accessed globally
logger = None

# Configure logging
def setup_logging(verbose=False):
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('automated_setup.log')
        ]
    )
    return logging.getLogger('automated_setup')

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Automated setup for research environment")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--skip-python", action="store_true", help="Skip Python environment setup")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--skip-env-setup", action="store_true", help="Skip environment setup")
    parser.add_argument("--skip-docker", action="store_true", help="Skip Docker setup and checks")
    parser.add_argument("--gpu", action="store_true", help="Force GPU configuration")
    parser.add_argument("--no-gpu", action="store_true", help="Disable GPU configuration")
    parser.add_argument("--force", action="store_true", help="Force reinstallation of dependencies")
    parser.add_argument("--no-admin", action="store_true", help="Run without admin privileges (prevents automatic elevation)")
    return parser.parse_args()

def request_admin(no_admin=False):
    """
    Check for administrative privileges and automatically escalate if needed.
    If --no-admin flag is provided, will not attempt to elevate privileges.
    
    Returns:
        bool: True if admin check should be bypassed or admin privileges obtained, False otherwise
    """
    if no_admin:
        return log_and_notify(
            "Admin check bypassed due to --no-admin flag",
            "Running without administrative privileges (limited functionality)."
        )
    
    if platform.system() == "Windows":
        try:
            # Check if we're running with admin privileges
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("\n" + "="*80)
                print("ADMINISTRATIVE PRIVILEGES REQUIRED")
                print("="*80)
                print("This script requires administrative privileges for:")
                print("- Installing system-wide Python packages")
                print("- Configuring Docker properly")
                print("- Setting up GPU drivers and configurations")
                print()
                print("The script will now attempt to elevate permissions.")
                print("If you don't want this, restart with the --no-admin flag.")
                print("="*80)

                # Prompt before attempting elevation
                choice = input("\nProceed with admin elevation? (y/n): ").lower()
                if choice in ('y', 'yes'):
                    logger.info("Attempting to restart with admin privileges...")
                    try:
                        # Re-run the program with admin rights
                        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                        logger.info("Elevation process initiated. Exiting current instance.")
                        # Exit the current instance directly instead of returning
                        sys.exit(0)
                    except Exception as e:
                        logger.error(f"Failed to elevate privileges: {e}")
                        print(f"Error elevating privileges: {e}")
                        choice = input("Continue without admin privileges? (y/n): ").lower()
                        if choice not in ('y', 'yes'):
                            return False
                else:
                    logger.info("User declined admin elevation")
                    choice = input("Continue with limited functionality? (y/n): ").lower()
                    if choice in ('y', 'yes'):
                        return log_and_notify(
                            "Continuing with limited functionality",
                            "Continuing with limited functionality (some features may not work properly)."
                        )
                    print("Setup aborted by user.")
                    print("Restart with --no-admin flag to bypass this check if needed.")
                    return False
            else:
                logger.info("Already running with admin privileges")
                return True
        except Exception as e:
            logger.warning(f"Error checking/requesting admin privileges: {e}")
            print(f"Could not verify admin privileges: {e}")
            # Ask user if they want to continue anyway
            choice = input("\nContinue without verifying admin privileges? (y/n): ").lower()
            return choice in ('y', 'yes')

    # For non-Windows platforms or if admin check passes
    return True

def log_and_notify(log_message, user_message):
    """
    Helper function to log a message and print a notification to the user.
    
    Args:
        log_message: Message to write to the log
        user_message: Message to display to the user
        
    Returns:
        bool: Always returns True to indicate process should continue
    """
    logger.info(log_message)
    print(user_message)
    return True

def setup_python(force=False):
    """Set up Python environment."""
    logger.info("Setting up Python environment")
    try:
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            logger.error("Python 3.8+ is required")
            return False
        logger.info(f"Python version: {python_version.major}.{python_version.minor}")
        return True
    except Exception as e:
        logger.error(f"Error setting up Python: {e}")
        return False

def setup_dependencies(force=False):
    """Install dependencies."""
    logger.info("Installing dependencies")
    global HAS_NUMPY, HAS_MATPLOTLIB

    try:
        return _extracted_from_setup_dependencies_8(force)
    except Exception as e:
        logger.error(f"Error installing dependencies: {e}")
        return False


# TODO Rename this here and in `setup_dependencies`
def _extracted_from_setup_dependencies_8(force):
    # Upgrade pip first
    logger.info("Upgrading pip...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)

    # Install dependencies from requirements.txt if it exists
    system_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system")
    req_file = os.path.join(system_folder, "requirements.txt")

    # Create system folder if it doesn't exist
    if not os.path.exists(system_folder):
        os.makedirs(system_folder, exist_ok=True)
        logger.info(f"Created system folder at {system_folder}")

    if os.path.exists(req_file):
        logger.info("Installing dependencies from requirements.txt...")
        cmd = [sys.executable, "-m", "pip", "install", "-r", req_file]
        if force:
            cmd.append("--force-reinstall")
        subprocess.run(cmd, check=True)
    else:
        # Install individual packages if no requirements file
        logger.info("No requirements.txt found. Installing packages individually.")
        logger.info("Installing NumPy...")
        subprocess.run([sys.executable, "-m", "pip", "install", "numpy"], check=True)

        logger.info("Installing Matplotlib...")
        subprocess.run([sys.executable, "-m", "pip", "install", "matplotlib"], check=True)

    # Verify installations
    try:
        import numpy as np
        HAS_NUMPY = True
        logger.info(f"NumPy {np.__version__} installed successfully")
    except ImportError:
        logger.warning("NumPy installation failed or is not available.")

    try:
        import matplotlib
        import matplotlib.pyplot as plt
        HAS_MATPLOTLIB = True
        logger.info(f"Matplotlib {matplotlib.__version__} installed successfully")
    except ImportError:
        logger.warning("Matplotlib installation failed or is not available.")

    logger.info("Dependencies installed successfully")
    return True

def check_docker():
    """Check if Docker is installed and working."""
    logger.info("Checking Docker installation")
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        logger.info("Docker is installed")
        return True
    except Exception as e:
        logger.error(f"Docker check failed: {e}")
        return False

def detect_gpu(force_gpu=False, disable_gpu=False):
    """Detect GPU availability."""
    logger.info("Detecting GPU")
    if disable_gpu:
        logger.info("GPU support disabled")
        return False
    if force_gpu:
        logger.info("GPU support forced")
        return True
    try:
        subprocess.run(["nvidia-smi"], capture_output=True, check=True)
        logger.info("GPU detected")
        return True
    except Exception as e:
        logger.warning(f"GPU detection failed: {e}")
        return False

def setup_environment(skip_docker=False, gpu=False, no_gpu=False):
    """Set up the research environment."""
    logger.info("Setting up research environment")
    try:
        if not skip_docker and not check_docker():
            logger.warning("Docker is not available")
        if detect_gpu(force_gpu=gpu, disable_gpu=no_gpu):
            logger.info("GPU will be used")
        logger.info("Environment setup completed")
        return True
    except Exception as e:
        logger.error(f"Error setting up environment: {e}")
        return False

def install_jupyter_notebook():
    """Install Jupyter Notebook."""
    logger.info("Installing Jupyter Notebook")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "notebook"])
        logger.info("Jupyter Notebook installed successfully")
    except Exception as e:
        logger.error(f"Error installing Jupyter Notebook: {e}")
        return False
    return True

def main():
    """Main entry point for the automated setup."""
    args = parse_arguments()
    global logger
    logger = setup_logging(args.verbose)
    logger.info("Starting automated setup")

    # Request admin privileges if needed
    if not request_admin(args.no_admin):
        logger.error("Setup aborted: administrative privileges required but not obtained")
        return 1

    # If we get here, we either have admin rights or the user accepted to proceed without them
    if platform.system() == "Windows" and ctypes.windll.shell32.IsUserAnAdmin():
        logger.info("Running with administrative privileges")
        print("Running with administrative privileges")

    try:
        return _extracted_from_main_19(args, logger)
    except Exception as e:
        logger.error(f"Unhandled error in setup: {e}")
        print(f"Setup failed with error: {e}")
        return 1


# TODO Rename this here and in `main`
def _extracted_from_main_19(args, logger):
    if not args.skip_python and not setup_python(force=args.force):
        logger.error("Python setup failed")
        return 1
    if not args.skip_deps and not setup_dependencies(force=args.force):
        logger.error("Dependency installation failed")
        return 1
    if not args.skip_env_setup and not setup_environment(
        skip_docker=args.skip_docker, gpu=args.gpu, no_gpu=args.no_gpu
    ):
        logger.error("Environment setup failed")
        return 1
    if not install_jupyter_notebook():
        logger.error("Jupyter Notebook installation failed")
        return 1
    logger.info("Automated setup completed successfully")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

from setuptools import setup, find_packages

setup(
    name="research-frameworks",
    version="0.1.0",
    description="Advanced AI Research Frameworks",
    author="Research Team",
    packages=find_packages(),
    install_requires=[
        # Core dependencies
        "numpy>=1.19.0",
        "pandas>=1.1.0",
        "matplotlib>=3.3.0",
        "seaborn>=0.11.0",
        
        # For self-awareness framework
        "psutil>=5.8.0",      # For system monitoring
        "networkx>=2.5",      # For knowledge graph creation
        
        # For emotional dimensionality framework
        "scikit-learn>=0.24.0",  # For ML components
        
        # For visualization
        "plotly>=4.14.0",
        "ipywidgets>=7.6.0",
        
        # For metrics collection
        "prometheus-client>=0.11.0",
        
        # For distributed operations
        "docker>=5.0.0",      # For container management
        
        # Jupyter notebook support
        "jupyterlab>=3.0.0",
        "ipython>=7.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.5b2",
            "flake8>=3.9.0",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
        "gpu": [
            "torch>=1.9.0",
            "tensorflow>=2.5.0",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)