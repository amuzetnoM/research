#!/usr/bin/env python3
"""
Comprehensive System Setup for AI Research Environment

This script handles all aspects of system setup, including:
- Python environment configuration
- Dependency installation
- Docker environment configuration (if applicable)
- GPU detection and configuration
- Directory structure creation
- Framework deployment

It consolidates functionality from various setup scripts.
"""

import argparse
import contextlib
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Set, Any

# Try to import optional modules, but don't fail if they're not available
HAS_NUMPY = False
HAS_MATPLOTLIB = False
HAS_PSUTIL = False
HAS_PYTORCH = False
HAS_TENSORFLOW = False

with contextlib.suppress(ImportError):
    import numpy as np
    HAS_NUMPY = True
with contextlib.suppress(ImportError):
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
with contextlib.suppress(ImportError):
    import psutil
    HAS_PSUTIL = True
with contextlib.suppress(ImportError):
    import torch
    HAS_PYTORCH = True
with contextlib.suppress(ImportError):
    import tensorflow as tf
    HAS_TENSORFLOW = True

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('system_setup.log')
    ]
)
logger = logging.getLogger("system-setup")

# Set default paths
PROJECT_ROOT = Path(__file__).parent.absolute()
DOCKER_DIR = PROJECT_ROOT / "docker"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
CONFIGS_DIR = PROJECT_ROOT / "configs"


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging with appropriate verbosity.
    
    Args:
        verbose: Enable verbose logging
        
    Returns:
        Configured logger instance
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(log_level)
    return logger


def check_python_version() -> bool:
    """Check if Python version is compatible.
    
    Returns:
        True if compatible, False otherwise
    """
    python_version = platform.python_version_tuple()
    if int(python_version[0]) < 3 or (int(python_version[0]) == 3 and int(python_version[1]) < 8):
        logger.error(f"Python 3.8+ required, found {platform.python_version()}")
        return False
    
    logger.info(f"Python version: {platform.python_version()} (compatible)")
    return True


def is_admin() -> bool:
    """Check if the script is running with administrative privileges.
    
    Returns:
        True if running as admin/root, False otherwise
    """
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception as e:
        logger.warning(f"Failed to check admin status: {e}")
        return False


def request_admin(no_admin: bool = False) -> bool:
    """Request administrative privileges if needed.
    
    Args:
        no_admin: Skip admin check if True
        
    Returns:
        True to continue, False to abort
    """
    if no_admin:
        logger.info("Skipping admin check as requested")
        return True
    
    if platform.system() == "Windows":
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                logger.warning("Running without administrative privileges")
                print("="*80)
                print("Some operations may require administrative privileges.")
                print("Problems may occur with system-level operations like Docker setup.")
                print("="*80)

                # Prompt before attempting elevation
                choice = input("\nProceed with admin elevation? (y/n): ").lower()
                if choice in ('y', 'yes'):
                    logger.info("Attempting to restart with admin privileges...")
                    try:
                        # Re-run the program with admin rights
                        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                        logger.info("Elevation process initiated. Exiting current instance.")
                        # Exit the current instance directly
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
                        logger.info("Continuing with limited functionality")
                        print("Continuing with limited functionality (some features may not work properly).")
                        return True
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

    # For non-Windows platforms
    return True


def check_dependencies() -> Tuple[List[str], List[str]]:
    """Check for installed and missing dependencies.
    
    Returns:
        Tuple of (installed_packages, missing_packages)
    """
    required_packages = [
        "numpy",
        "matplotlib",
        "psutil",
        "requests"
    ]
    
    installed = []
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            installed.append(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.warning(f"Missing required packages: {', '.join(missing)}")
    else:
        logger.info("All required packages are installed")
        
    return installed, missing


def install_dependencies(packages: List[str] = None, force: bool = False) -> bool:
    """Install Python dependencies.
    
    Args:
        packages: List of packages to install (if None, use defaults)
        force: Force reinstallation of packages
        
    Returns:
        True if successful, False otherwise
    """
    if packages is None:
        _, missing_packages = check_dependencies()
        if not missing_packages and not force:
            logger.info("All dependencies already installed")
            return True
        packages = missing_packages if not force else [
            "numpy",
            "matplotlib",
            "psutil",
            "requests",
            "flask",
            "prometheus-client",
            "docker"
        ]
    
    if not packages:
        return True
    
    logger.info(f"Installing dependencies: {', '.join(packages)}")
    
    # Upgrade pip first
    try:
        logger.info("Upgrading pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to upgrade pip: {e}")
        # Continue anyway
    
    # Install packages
    for package in packages:
        try:
            logger.info(f"Installing {package}...")
            cmd = [sys.executable, "-m", "pip", "install", package]
            if force:
                cmd.extend(["--upgrade", "--force-reinstall"])
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.debug(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {package}: {e}")
            logger.error(e.stderr)
            return False
    
    logger.info("All dependencies installed successfully")
    return True


def check_docker() -> bool:
    """Check if Docker is installed and running.
    
    Returns:
        True if Docker is available, False otherwise
    """
    try:
        # Check Docker
        result = subprocess.run(["docker", "--version"], 
                               check=True, capture_output=True, text=True)
        logger.info(f"Docker detected: {result.stdout.strip()}")
        
        # Check if Docker daemon is running
        result = subprocess.run(["docker", "info"], 
                               check=True, capture_output=True, text=True)
        logger.debug("Docker daemon is running")
        
        # Check Docker Compose if applicable
        try:
            result = subprocess.run(["docker-compose", "--version"], 
                                   check=True, capture_output=True, text=True)
            logger.info(f"Docker Compose detected: {result.stdout.strip()}")
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.warning("Docker Compose not found, but Docker is available")
            logger.info("Visit https://docs.docker.com/compose/install/ for installation")
        
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.warning("Docker not found or not running")
        logger.info("Visit https://docs.docker.com/get-docker/ for installation")
        return False


def detect_gpu(force_gpu: bool = False, disable_gpu: bool = False) -> bool:
    """Detect if GPU is available for acceleration.
    
    Args:
        force_gpu: Force GPU support even if not detected
        disable_gpu: Disable GPU support even if available
        
    Returns:
        True if GPU should be used, False otherwise
    """
    if disable_gpu:
        logger.info("GPU support disabled by user")
        return False
    
    # If user forces GPU, use it regardless of detection
    if force_gpu:
        logger.info("GPU support forced by user")
        return True
    
    has_gpu = False
    
    # Check for NVIDIA GPU (Linux/Windows)
    try:
        result = subprocess.run(["nvidia-smi"], 
                               check=True, capture_output=True, text=True)
        gpu_info = result.stdout
        logger.info("NVIDIA GPU detected")
        logger.debug(f"GPU info: {gpu_info}")
        has_gpu = True
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.debug("NVIDIA GPU not detected via nvidia-smi")
    
    # On Windows, also check via WMIC
    if platform.system() == "Windows" and not has_gpu:
        try:
            result = subprocess.run(["wmic", "path", "win32_VideoController", "get", "name"], 
                                   check=True, capture_output=True, text=True)
            if "NVIDIA" in result.stdout:
                logger.info("NVIDIA GPU detected via WMIC")
                has_gpu = True
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.debug("Could not check GPU via WMIC")
    
    # Check for Docker GPU support if Docker is available
    if has_gpu and check_docker():
        try:
            result = subprocess.run(["docker", "run", "--rm", "--gpus", "all", "nvidia/cuda:11.0-base", "nvidia-smi"],
                                   check=True, capture_output=True, text=True)
            logger.info("Docker GPU support confirmed")
        except subprocess.SubprocessError:
            logger.warning("GPU detected but Docker GPU support not available")
            logger.info("Please install NVIDIA Docker support for GPU acceleration in containers")
            logger.info("See: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html")
    
    if has_gpu:
        logger.info("GPU acceleration is available")
    else:
        logger.info("No GPU detected, using CPU only")
    
    return has_gpu


def create_directory_structure() -> bool:
    """Create the necessary directory structure.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("Creating directory structure")
    
    directories = [
        DOCKER_DIR,
        DATA_DIR,
        DATA_DIR / "models",
        DATA_DIR / "logs",
        DATA_DIR / "configs",
        LOGS_DIR,
        CONFIGS_DIR,
        PROJECT_ROOT / "utils",
        PROJECT_ROOT / "notebooks"
    ]
    
    try:
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {directory}")
        
        logger.info("Directory structure created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating directory structure: {e}")
        return False


def make_executable(file_path: Union[str, Path]) -> bool:
    """Make a file executable.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if successful, False otherwise
    """
    if platform.system() == "Windows":
        # Not applicable on Windows
        return True
    
    try:
        file_path = Path(file_path)
        mode = file_path.stat().st_mode
        file_path.chmod(mode | 0o111)  # Add executable bit
        logger.debug(f"Made file executable: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to make file executable: {e}")
        return False


def prepare_docker_environment(use_gpu: bool = False) -> bool:
    """Prepare Docker environment files.
    
    Args:
        use_gpu: Configure for GPU support
        
    Returns:
        True if successful, False otherwise
    """
    if not check_docker():
        logger.warning("Docker not available, skipping Docker environment setup")
        return False
    
    logger.info("Preparing Docker environment")
    
    try:
        # Create entrypoint script
        entrypoint_path = PROJECT_ROOT / "entrypoint.sh"
        with open(entrypoint_path, 'w') as f:
            f.write("""#!/bin/bash

# Default entrypoint script for the research environment
echo "Starting research environment..."

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:/app"

# Start Jupyter Lab
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''
""")
        
        make_executable(entrypoint_path)
        
        # Create Dockerfile
        dockerfile_path = DOCKER_DIR / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            if use_gpu:
                f.write("""FROM nvidia/cuda:11.6.2-cudnn8-runtime-ubuntu20.04

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    python3-pip python3-dev git wget curl \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create requirements file
RUN echo "numpy>=1.19.0" > /tmp/requirements.txt && \\
    echo "matplotlib>=3.3.0" >> /tmp/requirements.txt && \\
    echo "psutil>=5.8.0" >> /tmp/requirements.txt && \\
    echo "requests>=2.25.0" >> /tmp/requirements.txt && \\
    echo "flask>=2.0.0" >> /tmp/requirements.txt && \\
    echo "prometheus-client>=0.11.0" >> /tmp/requirements.txt && \\
    echo "jupyter>=1.0.0" >> /tmp/requirements.txt && \\
    echo "jupyterlab>=3.0.0" >> /tmp/requirements.txt && \\
    echo "torch>=1.9.0" >> /tmp/requirements.txt

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports
EXPOSE 8888 6006 8000 9090

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
""")
            else:
                f.write("""FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    git wget curl \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create requirements file
RUN echo "numpy>=1.19.0" > /tmp/requirements.txt && \\
    echo "matplotlib>=3.3.0" >> /tmp/requirements.txt && \\
    echo "psutil>=5.8.0" >> /tmp/requirements.txt && \\
    echo "requests>=2.25.0" >> /tmp/requirements.txt && \\
    echo "flask>=2.0.0" >> /tmp/requirements.txt && \\
    echo "prometheus-client>=0.11.0" >> /tmp/requirements.txt && \\
    echo "jupyter>=1.0.0" >> /tmp/requirements.txt && \\
    echo "jupyterlab>=3.0.0" >> /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports
EXPOSE 8888 6006 8000 9090

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
""")
        
        # Create docker-compose.yml
        compose_path = DOCKER_DIR / "docker-compose.yml"
        with open(compose_path, 'w') as f:
            f.write("""version: '3'

services:
  research:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    volumes:
      - ..:/app
    ports:
      - "8888:8888"  # JupyterLab
      - "6006:6006"  # TensorBoard
      - "8000:8000"  # Prometheus metrics
""")
            
            # Add GPU support if needed
            if use_gpu:
                f.write("""    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
""")
        
        # Create run script
        run_script_path = PROJECT_ROOT / "run.sh"
        with open(run_script_path, 'w') as f:
            f.write("""#!/bin/bash

# Make scripts executable
chmod +x entrypoint.sh 2>/dev/null || true

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if nvidia-docker is installed for GPU support
if ! command -v nvidia-smi &> /dev/null; then
    echo "Warning: NVIDIA drivers not detected. This might affect GPU support."
    echo "Consider installing NVIDIA Container Toolkit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
fi

# Build and run the container
echo "Starting research environment..."
cd docker && docker-compose up --build

# This script launches the Docker container
# Usage: ./run.sh
""")
        
        make_executable(run_script_path)
        
        # Create Windows batch file version
        run_cmd_path = PROJECT_ROOT / "run.cmd"
        with open(run_cmd_path, 'w') as f:
            f.write("""@echo off
REM Windows batch file for running the research environment

REM Check if Docker is installed
where docker >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if docker-compose is installed
where docker-compose >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Check for NVIDIA GPU
where nvidia-smi >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Warning: NVIDIA drivers not detected. This might affect GPU support.
    echo Consider installing NVIDIA Container Toolkit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
) else (
    echo NVIDIA GPU detected. Enabling GPU support.
)

REM Build and run the container
echo Starting research environment...
cd docker && docker-compose up --build

REM Usage: run.cmd
""")
        
        logger.info("Docker environment prepared successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error preparing Docker environment: {e}")
        return False


def setup_frameworks() -> bool:
    """Set up and install all research frameworks.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("Setting up research frameworks")
    
    frameworks = [
        # Path relative to PROJECT_ROOT
        "head_1/frameworks/emotional_dimensionality",
        "head_1/frameworks/self_awareness",
        "head_1/frameworks/probabalistic_uncertainty_principle",
        # Add other frameworks here
    ]
    
    successes = []
    
    for framework_path in frameworks:
        full_path = PROJECT_ROOT / framework_path
        if not full_path.exists():
            logger.warning(f"Framework path does not exist: {framework_path}")
            continue
            
        setup_path = full_path / "setup.py"
        if not setup_path.exists():
            logger.warning(f"No setup.py found for framework: {framework_path}")
            continue
            
        logger.info(f"Installing framework: {framework_path}")
        try:
            # Install in development mode
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", str(full_path)],
                check=True,
                capture_output=True,
                text=True
            )
            logger.debug(result.stdout)
            successes.append(framework_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install framework {framework_path}: {e}")
            logger.error(e.stderr)
    
    if not successes:
        logger.warning("No frameworks were successfully installed")
        return False
        
    logger.info(f"Successfully installed {len(successes)} frameworks")
    return True


def setup_environment(
        install_deps: bool = True,
        force_deps: bool = False,
        setup_docker: bool = True,
        force_gpu: bool = False,
        disable_gpu: bool = False,
        install_frameworks: bool = True
    ) -> bool:
    """Set up the complete research environment.
    
    Args:
        install_deps: Install Python dependencies
        force_deps: Force reinstallation of dependencies
        setup_docker: Set up Docker environment
        force_gpu: Force GPU configuration
        disable_gpu: Disable GPU configuration
        install_frameworks: Install research frameworks
        
    Returns:
        True if successful, False otherwise
    """
    # Check Python version
    if not check_python_version():
        logger.error("Incompatible Python version")
        return False
    
    # Create directory structure
    if not create_directory_structure():
        logger.error("Failed to create directory structure")
        return False
    
    # Install dependencies if requested
    if install_deps:
        if not install_dependencies(force=force_deps):
            logger.error("Failed to install dependencies")
            return False
    
    # Detect GPU
    use_gpu = detect_gpu(force_gpu=force_gpu, disable_gpu=disable_gpu)
    
    # Set up Docker environment if requested
    if setup_docker:
        if not prepare_docker_environment(use_gpu=use_gpu):
            logger.warning("Docker environment setup failed")
            # Continue anyway, as Docker is optional
    
    # Set up research frameworks if requested
    if install_frameworks:
        if not setup_frameworks():
            logger.warning("Framework setup failed")
            # Continue anyway, as frameworks are optional
    
    logger.info("Environment setup completed successfully")
    return True


def get_environment_summary() -> Dict[str, Any]:
    """Get a summary of the environment.
    
    Returns:
        Dictionary with environment information
    """
    summary = {
        'platform': platform.system(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
        'has_numpy': HAS_NUMPY,
        'has_matplotlib': HAS_MATPLOTLIB,
        'has_psutil': HAS_PSUTIL,
        'docker_available': check_docker(),
        'gpu_available': detect_gpu(),
        'time': datetime.now().isoformat()
    }
    
    if HAS_PSUTIL:
        try:
            memory = psutil.virtual_memory()
            summary['memory_total'] = memory.total
            summary['memory_available'] = memory.available
            summary['cpu_count'] = psutil.cpu_count()
        except Exception as e:
            logger.warning(f"Error getting system info: {e}")
    
    return summary


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="System Setup for AI Research Environment",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # General options
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose output")
    parser.add_argument("--no-admin", action="store_true",
                       help="Skip admin privilege check")
    
    # Setup options
    parser.add_argument("--skip-deps", action="store_true",
                       help="Skip dependency installation")
    parser.add_argument("--force-deps", action="store_true",
                       help="Force reinstallation of dependencies")
    parser.add_argument("--skip-docker", action="store_true",
                       help="Skip Docker environment setup")
    parser.add_argument("--skip-frameworks", action="store_true",
                       help="Skip research frameworks installation")
    
    # GPU options
    parser.add_argument("--gpu", action="store_true",
                       help="Force GPU support")
    parser.add_argument("--no-gpu", action="store_true",
                       help="Disable GPU support")
    
    # Special actions
    parser.add_argument("--summary", action="store_true",
                       help="Show environment summary and exit")
    
    return parser.parse_args()


def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_arguments()
    
    # Configure logging
    setup_logging(args.verbose)
    
    # Print environment summary if requested
    if args.summary:
        summary = get_environment_summary()
        print(json.dumps(summary, indent=2))
        return 0
    
    logger.info("Starting system setup")
    
    # Check for admin privileges if needed
    if not request_admin(args.no_admin):
        logger.error("Setup aborted: administrative privileges required but not obtained")
        return 1
    
    try:
        # Run environment setup
        success = setup_environment(
            install_deps=not args.skip_deps,
            force_deps=args.force_deps,
            setup_docker=not args.skip_docker,
            force_gpu=args.gpu,
            disable_gpu=args.no_gpu,
            install_frameworks=not args.skip_frameworks
        )
        
        if success:
            logger.info("System setup completed successfully")
            
            # Print next steps
            print("\n=== Next Steps ===")
            print("1. Start the environment using:")
            if platform.system() == "Windows":
                print("   > run.cmd")
            else:
                print("   $ ./run.sh")
            print("2. Open your browser to access JupyterLab: http://localhost:8888")
            print("3. Use deployment.py to manage Self-Awareness Framework instances")
            
            return 0
        else:
            logger.error("System setup failed")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unhandled error in setup: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
