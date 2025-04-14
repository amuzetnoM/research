#!/usr/bin/env python3
"""
Comprehensive setup script for AI Research Environment.
This script handles all aspects of environment setup, including:
- Docker configuration
- GPU detection
- System optimization
- Requirements installation
- Directory structure creation

This script can be called directly or through setup_all.py
"""

import argparse
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Make imports more resilient by handling missing packages
try:
    import psutil  # For system monitoring
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Warning: psutil module not found. Some features will be limited.")
    
try:
    import numpy as np  # For numerical operations
    import matplotlib.pyplot as plt  # For graphical diagnostics
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'setup.log'))
    ]
)
logger = logging.getLogger('setup')

# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='AI Research Environment Setup')
    
    # General options
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--force', '-f', action='store_true', help='Force setup even if already configured')
    
    # Component selection
    parser.add_argument('--all', action='store_true', help='Set up all components')
    parser.add_argument('--docker', action='store_true', help='Set up Docker environment')
    parser.add_argument('--python', action='store_true', help='Set up Python environment')
    parser.add_argument('--monitoring', action='store_true', help='Set up monitoring stack')
    
    # Docker options
    parser.add_argument('--gpu', action='store_true', help='Force GPU support')
    parser.add_argument('--no-gpu', action='store_true', help='Disable GPU support')
    parser.add_argument('--skip-docker-check', action='store_true', 
                        help='Skip Docker installation check (use for Python-only setup)')
    
    # Path options
    parser.add_argument('--docker-dir', type=str, default='docker', 
                        help='Directory for Docker files')
    
    # Allow for execution without any args
    args = parser.parse_args()
    
    # If no component is selected, default to --all
    if not (args.all or args.docker or args.python or args.monitoring):
        args.all = True
    
    return args


def set_log_level(verbose: bool) -> None:
    """Set the log level based on verbosity."""
    if verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    else:
        logger.setLevel(logging.INFO)


def check_prerequisites(skip_docker_check=False) -> bool:
    """
    Check if all prerequisites are installed.
    
    Args:
        skip_docker_check: If True, skip Docker installation check
        
    Returns: 
        True if all prerequisites are met, False otherwise
    """
    logger.info("Checking prerequisites...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        logger.error(f"Python 3.8+ is required, found {python_version.major}.{python_version.minor}")
        return False
    logger.debug(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check for missing required packages
    missing_packages = []
    for package in ["psutil"]:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning(f"Missing required packages: {', '.join(missing_packages)}")
        logger.info("Installing missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    check=True,
                    capture_output=True
                )
                logger.info(f"Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {package}: {e}")
                logger.info(f"Please install it manually with: pip install {package}")
                return False
    
    if skip_docker_check:
        logger.info("Skipping Docker check as requested")
        return True
    
    # Check Docker
    try:
        docker_version = subprocess.run(
            ["docker", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        ).stdout.strip()
        logger.debug(f"Docker version: {docker_version}")
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.error("Docker not found. Please install Docker before continuing.")
        
        # Provide platform-specific installation instructions
        if platform.system() == "Windows":
            logger.info("For Windows: Download and install Docker Desktop from https://www.docker.com/products/docker-desktop")
            logger.info("Make sure to enable WSL 2 integration during installation")
        elif platform.system() == "Darwin":  # macOS
            logger.info("For macOS: Download and install Docker Desktop from https://www.docker.com/products/docker-desktop")
        elif platform.system() == "Linux":
            dist_info = ""
            try:
                with open("/etc/os-release", "r") as f:
                    dist_info = f.read()
            except:
                pass
            
            if "ubuntu" in dist_info.lower() or "debian" in dist_info.lower():
                logger.info("For Ubuntu/Debian: sudo apt-get update && sudo apt-get install docker.io docker-compose")
            elif "fedora" in dist_info.lower() or "centos" in dist_info.lower() or "rhel" in dist_info.lower():
                logger.info("For Fedora/CentOS/RHEL: sudo dnf install docker docker-compose")
            else:
                logger.info("Visit https://docs.docker.com/get-docker/ for platform-specific installation instructions")
        else:
            logger.info("Visit https://docs.docker.com/get-docker/ for installation instructions")
        
        return False
    
    # Check Docker Compose
    try:
        compose_version = subprocess.run(
            ["docker-compose", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        ).stdout.strip()
        logger.debug(f"Docker Compose version: {compose_version}")
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.warning("Docker Compose not found. Some features may not work.")
        logger.info("Visit https://docs.docker.com/compose/install/ for installation instructions.")
    
    # Check git
    try:
        git_version = subprocess.run(
            ["git", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        ).stdout.strip()
        logger.debug(f"Git version: {git_version}")
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.warning("Git not found. Version control features may not work.")
    
    return True


def detect_gpu(force_gpu: bool = False, disable_gpu: bool = False) -> bool:
    """
    Detect if a GPU is available.
    
    Args:
        force_gpu: If True, assume GPU is available
        disable_gpu: If True, disable GPU detection
        
    Returns:
        bool: True if GPU is available, False otherwise
    """
    if disable_gpu:
        logger.info("GPU support disabled by user")
        return False
    
    if force_gpu:
        logger.info("GPU support forced by user")
        return True
    
    # Check using NVIDIA SMI
    try:
        nvidia_smi = subprocess.run(
            ["nvidia-smi"], 
            capture_output=True, 
            text=True
        )
        if nvidia_smi.returncode == 0:
            gpu_info = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()
            logger.info(f"GPU detected: {gpu_info}")
            
            # Check for NVIDIA Docker support
            docker_info = subprocess.run(
                ["docker", "info", "--format", "{{json .}}"],
                capture_output=True,
                text=True,
                check=True
            ).stdout
            
            docker_json = json.loads(docker_info)
            runtimes = docker_json.get("Runtimes", {})
            
            # Check if "nvidia" is in runtimes
            if "nvidia" not in runtimes:
                logger.warning("NVIDIA Docker runtime not found. GPU support may not work correctly.")
                logger.info("See https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html")
            
            return True
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    logger.info("No GPU detected or NVIDIA drivers not installed")
    return False


def ensure_directory_structure(docker_dir: str) -> None:
    """
    Ensure all necessary directories exist.
    
    Args:
        docker_dir: Directory for Docker files
    """
    logger.info("Creating directory structure...")
    
    # Create directories
    directories = [
        docker_dir,
        "monitoring",
        "monitoring/prometheus",
        "monitoring/grafana",
        "monitoring/grafana/provisioning",
        "monitoring/grafana/provisioning/dashboards",
        "utils",
        "setup",
        "docs",
        "docs/examples",
        "docs/setup",
        "docs/troubleshooting",
    ]
    
    for directory in directories:
        dir_path = os.path.join(PROJECT_ROOT, directory)
        os.makedirs(dir_path, exist_ok=True)
        logger.debug(f"Created directory: {dir_path}")


def install_python_dependencies() -> None:
    """Install Python dependencies from requirements.txt."""
    logger.info("Installing Python dependencies...")
    requirements_path = os.path.join(PROJECT_ROOT, "setup/requirements.txt")
    
    if not os.path.exists(requirements_path):
        logger.error(f"Requirements file not found: {requirements_path}")
        return
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", requirements_path],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info("Successfully installed Python dependencies")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e.stderr}")
        logger.debug(f"Command output: {e.stdout}")


def make_executable(file_path: str) -> None:
    """
    Make a file executable.
    
    Args:
        file_path: Path to the file
    """
    if not os.path.exists(file_path):
        logger.warning(f"Cannot make non-existent file executable: {file_path}")
        return
    
    # Only change permissions on non-Windows systems
    if platform.system() != "Windows":
        current_mode = os.stat(file_path).st_mode
        os.chmod(file_path, current_mode | 0o755)
        logger.debug(f"Made executable: {file_path}")
    else:
        logger.debug(f"Skipping chmod on Windows for: {file_path}")


def setup_docker_environment(docker_dir: str, use_gpu: bool) -> None:
    """
    Set up Docker environment.
    
    Args:
        docker_dir: Directory for Docker files
        use_gpu: Whether to configure for GPU support
    """
    logger.info("Setting up Docker environment...")
    
    # Make entrypoint executable
    entrypoint_path = os.path.join(PROJECT_ROOT, "entrypoint.sh")
    make_executable(entrypoint_path)

    # Update symbolic links if needed
    docker_dir_path = os.path.join(PROJECT_ROOT, docker_dir)
    
    # Create symlink to entrypoint.sh in the docker directory for clarity
    entrypoint_link = os.path.join(docker_dir_path, "entrypoint.sh")
    if not os.path.exists(entrypoint_link):
        try:
            os.symlink(os.path.relpath(entrypoint_path, docker_dir_path), entrypoint_link)
            logger.debug(f"Created symlink: {entrypoint_link}")
        except OSError as e:
            logger.warning(f"Failed to create symlink: {e}")


def setup_monitoring_stack() -> None:
    """Set up the monitoring stack (Prometheus + Grafana)."""
    logger.info("Setting up monitoring stack...")
    
    # Create prometheus.yml if it doesn't exist
    prometheus_config = os.path.join(PROJECT_ROOT, "monitoring/prometheus/prometheus.yml")
    if not os.path.exists(prometheus_config):
        prometheus_config_dir = os.path.dirname(prometheus_config)
        os.makedirs(prometheus_config_dir, exist_ok=True)
        
        with open(prometheus_config, 'w') as f:
            f.write("""global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "node_exporter"
    static_configs:
      - targets: ["node-exporter:9100"]

  - job_name: "research_container"
    static_configs:
      - targets: ["research:8888"]
    metrics_path: /metrics

  - job_name: "cadvisor"
    static_configs:
      - targets: ["cadvisor:8080"]
""")
        logger.debug(f"Created Prometheus config: {prometheus_config}")


def cleanup_unnecessary_files(args: argparse.Namespace) -> None:
    """
    Clean up unnecessary files.
    
    Args:
        args: Command line arguments
    """
    logger.info("Cleaning up unnecessary files...")
    
    # Files to remove
    files_to_remove = [
        os.path.join(PROJECT_ROOT, "requirements.txt"),  # Root requirements file
        os.path.join(PROJECT_ROOT, "setup/requirements-core.txt"),
        os.path.join(PROJECT_ROOT, "Dockerfile"),
        os.path.join(PROJECT_ROOT, "docker-compose.yml"),
        os.path.join(PROJECT_ROOT, "run.sh"),
        os.path.join(PROJECT_ROOT, "start_docker.py"),
    ]
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.debug(f"Removed file: {file_path}")
            except OSError as e:
                logger.warning(f"Failed to remove file {file_path}: {e}")


def create_utils_diagnostic_tool() -> None:
    """Create the diagnostic tool in the utils directory."""
    logger.info("Creating diagnostic tool...")
    
    diagnostic_path = os.path.join(PROJECT_ROOT, "utils/diagnostic_tool.py")
    
    with open(diagnostic_path, 'w') as f:
        f.write("""#!/usr/bin/env python3
\"\"\"Diagnostic Tool for AI Research Environment\"\"\"

# Tool implementation goes here...
""")
    
    # Make the file executable
    make_executable(diagnostic_path)
    logger.info(f"Created diagnostic tool at {diagnostic_path}")


def create_environment_manager():
    """Create the environment_manager.py script for managing the research environment."""
    logger.info("Creating environment manager...")
    
    env_manager_path = os.path.join(PROJECT_ROOT, "environment_manager.py")
    
    with open(env_manager_path, 'w') as f:
        f.write("""#!/usr/bin/env python3
\"\"\"Environment Manager for AI Research Environment

This script manages the Docker environment for the research workspace.
\"\"\"

import argparse
import logging
import os
import platform
import subprocess
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('environment_manager')

def parse_arguments():
    \"\"\"Parse command line arguments.\"\"\"
    parser = argparse.ArgumentParser(description='AI Research Environment Manager')
    
    # General options
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    # Container options
    parser.add_argument('--gpu', action='store_true', help='Enable GPU support')
    parser.add_argument('--detach', '-d', action='store_true', help='Run in detached mode')
    parser.add_argument('--port', type=int, default=8888, help='JupyterLab port (default: 8888)')
    
    # Monitoring options
    parser.add_argument('--enable-monitoring', action='store_true', help='Enable monitoring stack')
    parser.add_argument('--monitor-port', type=int, default=3000, help='Monitoring dashboard port (default: 3000)')
    
    return parser.parse_args()

def check_docker():
    \"\"\"Check if Docker is installed and running.\"\"\"
    try:
        subprocess.run(['docker', 'info'], check=True, capture_output=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.error("Docker is not installed or not running")
        logger.info("Please install Docker and start the Docker service")
        return False

def check_environment():
    \"\"\"Check if the environment is correctly set up.\"\"\"
    # Check if docker directory exists
    docker_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docker")
    if not os.path.exists(docker_dir):
        logger.error(f"Docker directory not found: {docker_dir}")
        logger.info("Please run the setup script first: python setup/setup.py")
        return False
    
    # Check if entrypoint.sh exists
    entrypoint = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entrypoint.sh")
    if not os.path.exists(entrypoint):
        logger.error(f"Entrypoint script not found: {entrypoint}")
        logger.info("Please run the setup script first: python setup/setup.py")
        return False
    
    return True

def main():
    \"\"\"Main entry point.\"\"\"
    args = parse_arguments()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Check if Docker is installed and running
    if not check_docker():
        return 1
    
    # Check if environment is set up
    if not check_environment():
        return 1
    
    # Determine Docker command
    if platform.system() == "Windows":
        cmd = ["docker-compose", "-f", "docker/docker-compose.yml", "up"]
    else:
        cmd = ["docker-compose", "-f", "docker/docker-compose.yml", "up"]
    
    if args.detach:
        cmd.append("-d")
    
    # Run Docker Compose
    try:
        subprocess.run(cmd, check=True)
        return 0
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run Docker Compose: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
""")
    
    make_executable(env_manager_path)
    logger.info(f"Created environment manager at {env_manager_path}")


def create_run_script() -> None:
    """Create the run.sh script for launching the environment."""
    logger.info("Creating run script...")
    
    run_script_path = os.path.join(PROJECT_ROOT, "run.sh")
    run_cmd_path = os.path.join(PROJECT_ROOT, "run.cmd")  # Windows batch file
    
    # Create bash script for Unix/Git Bash
    with open(run_script_path, 'w') as f:
        f.write("""#!/bin/bash

# Make scripts executable
chmod +x entrypoint.sh 2>/dev/null || true
chmod +x utils/gpu_check.py 2>/dev/null || true

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
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected. Enabling GPU support."
else
    echo "Warning: NVIDIA drivers not detected. This might affect GPU support."
    echo "Consider installing NVIDIA Container Toolkit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
fi

# Build and run the container using environment_manager.py
echo "Starting research environment..."
python environment_manager.py "$@"

# Execute this script to run the container
# Usage: ./run.sh
""")
    
    # Create Windows CMD script
    with open(run_cmd_path, 'w') as f:
        f.write("""@echo off
REM Windows batch file for running the research environment

REM Check if docker is installed
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
python environment_manager.py %*

REM Usage: run.cmd
""")
    
    # Make the files executable
    make_executable(run_script_path)
    logger.info(f"Created run scripts at {run_script_path} and {run_cmd_path}")


def execute_script_with_platform_awareness(script_path):
    """
    Execute a script with platform-specific awareness.
    
    Args:
        script_path: Path to the script to execute
        
    Returns:
        bool: True if successful, False otherwise
    """
    script_name = os.path.basename(script_path)
    script_ext = os.path.splitext(script_path)[1]
    logger.debug(f"Executing script: {script_path}")
    
    try:
        if platform.system() == "Windows":
            # Check if bash is available (Git Bash, WSL, etc.)
            try:
                subprocess.run(["bash", "--version"], check=True, capture_output=True)
                has_bash = True
            except (subprocess.SubprocessError, FileNotFoundError):
                has_bash = False
            
            # For .sh scripts on Windows
            if script_ext == ".sh" and has_bash:
                logger.debug("Using bash to execute .sh script on Windows")
                return subprocess.run(["bash", script_path], check=True)
            elif script_ext == ".sh" and not has_bash:
                logger.warning("Bash not available on Windows for .sh script")
                alt_script = os.path.splitext(script_path)[0] + ".cmd"
                if os.path.exists(alt_script):
                    logger.debug(f"Using alternative Windows script: {alt_script}")
                    return subprocess.run([alt_script], shell=True, check=True)
                else:
                    logger.error(f"Cannot execute .sh script without bash, and no .cmd alternative found")
                    return False
            # For .cmd scripts or other Windows executables
            else:
                logger.debug("Using Windows shell to execute script")
                return subprocess.run([script_path], shell=True, check=True)
        else:
            # On Unix-like systems
            logger.debug("Executing script on Unix-like system")
            return subprocess.run([script_path], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to execute script {script_path}: {e}")
        return False


def main() -> None:
    """Main entry point for the setup script."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Configure logging
    set_log_level(args.verbose)
    
    logger.info("Starting AI Research Environment setup...")
    
    # Check prerequisites - allow skipping Docker check for Python-only setup
    skip_docker = args.skip_docker_check or (args.python and not args.docker and not args.all and not args.monitoring)
    if not check_prerequisites(skip_docker_check=skip_docker):
        logger.error("Prerequisites check failed. Please address the issues above.")
        sys.exit(1)
    
    # Detect GPU
    use_gpu = detect_gpu(force_gpu=args.gpu, disable_gpu=args.no_gpu)
    
    # Create directory structure
    ensure_directory_structure(args.docker_dir)
    
    # Run requested components
    if args.all or args.python:
        install_python_dependencies()
    
    if (args.all or args.docker) and not skip_docker:
        setup_docker_environment(args.docker_dir, use_gpu)
    
    if (args.all or args.monitoring) and not skip_docker:
        setup_monitoring_stack()
    
    # Create diagnostic tool
    create_utils_diagnostic_tool()
    
    # Create environment manager
    create_environment_manager()
    
    # Clean up unnecessary files
    cleanup_unnecessary_files(args)
    
    # Create run script
    create_run_script()
    
    logger.info("Setup completed successfully!")
    
    # Print next steps with platform-specific instructions
    print("\n=== Next Steps ===")
    if skip_docker:
        print("You've set up the Python environment without Docker.")
        print("To complete the setup with Docker later:")
        print("1. Install Docker: https://docs.docker.com/get-docker/")
        print("2. Run the setup script again with: python setup_all.py")
    else:
        if platform.system() == "Windows":
            print(f"1. Run the Docker environment: run.cmd")
        else:
            print(f"1. Run the Docker environment: ./run.sh")
        print(f"2. Access JupyterLab: http://localhost:8888")
    print(f"3. Run diagnostics: python utils/diagnostic_tool.py")
    print(f"4. For more information, see the documentation in the docs/ directory")
    
    # Only try to execute the run script if Docker is installed and not being called from setup_all.py
    parent_process = ""
    if HAS_PSUTIL:
        try:
            current_process = psutil.Process()
            parent = current_process.parent()
            parent_process = parent.name() if parent else ""
        except:
            pass
    
    # Don't auto-execute if parent process is python (likely setup_all.py)
    if not skip_docker and not parent_process.lower().startswith("python"):
        # Execute the run script with platform awareness
        print("\nExecuting run script to start the environment...")
        
        if platform.system() == "Windows":
            run_script_path = os.path.join(PROJECT_ROOT, "run.cmd")
        else:
            run_script_path = os.path.join(PROJECT_ROOT, "run.sh")
        
        if not execute_script_with_platform_awareness(run_script_path):
            logger.error("Failed to execute run script")
            print("\nPlease run the script manually:")
            if platform.system() == "Windows":
                print(f"   > run.cmd")
            else:
                print(f"   $ ./run.sh")


if __name__ == "__main__":
    if __name__ == "__main__":
        main()
