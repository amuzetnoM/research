"""
Environment Manager

Handles the setup and configuration of the research environment,
including directory structure, Python environment, and system configuration.
"""

import logging
import os
import platform
import subprocess
import sys
import shutil
from pathlib import Path

from .utils import system_utils

# Get logger
logger = logging.getLogger('setup')

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

def setup_python_environment():
    """
    Ensure Python environment is properly set up.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Setting up Python environment...")
    
    # Check if Python is correctly installed
    python_version = platform.python_version_tuple()
    if int(python_version[0]) < 3 or (int(python_version[0]) == 3 and int(python_version[1]) < 8):
        logger.error(f"Python 3.8+ required, found {platform.python_version()}")
        logger.info("Running pre-installation script to install Python...")
        
        # Run the preinstall script
        preinstall_script = PROJECT_ROOT / "setup" / "_preinstall.py"
        if preinstall_script.exists():
            try:
                if platform.system() == "Windows":
                    result = subprocess.run([sys.executable, str(preinstall_script)], check=True)
                else:
                    result = subprocess.run(["python3", str(preinstall_script)], check=True)
                
                if result.returncode != 0:
                    logger.error("Python pre-installation failed")
                    return False
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to run Python pre-installation: {e}")
                return False
        else:
            logger.error("Python pre-installation script not found")
            return False
    
    # Check if pip is installed
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        logger.error("pip is not installed or not working properly")
        return False
    
    return True

def ensure_directory_structure():
    """
    Create the necessary directory structure for the project.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Creating directory structure...")
    
    directories = [
        "docker",
        "monitoring",
        "monitoring/prometheus",
        "monitoring/grafana",
        "monitoring/grafana/provisioning",
        "monitoring/grafana/provisioning/dashboards",
        "utils",
        "notebooks",
        "setup",
        "docs",
        "docs/examples",
        "docs/setup",
        "docs/troubleshooting",
    ]
    
    for directory in directories:
        dir_path = PROJECT_ROOT / directory
        os.makedirs(dir_path, exist_ok=True)
        logger.debug(f"Created directory: {dir_path}")
    
    return True

def detect_gpu():
    """
    Detect if a compatible GPU is available.
    
    Returns:
        bool: True if GPU is detected, False otherwise
    """
    logger.info("Detecting GPU...")
    
    # Check for NVIDIA GPU
    try:
        # Try using nvidia-smi command
        nvidia_smi = subprocess.run(
            ["nvidia-smi"], check=True, capture_output=True, text=True
        )
        logger.info("NVIDIA GPU detected")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Check for AMD GPU on Linux
    if platform.system() == "Linux":
        try:
            # Check for ROCm/AMD GPU
            result = subprocess.run(
                ["rocm-smi"], check=True, capture_output=True, text=True
            )
            logger.info("AMD GPU with ROCm detected")
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
    
    logger.info("No compatible GPU detected")
    return False

def make_executable(file_path):
    """
    Make a file executable.
    
    Args:
        file_path (str or Path): Path to the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    if platform.system() != "Windows":
        try:
            file_path = Path(file_path)
            mode = file_path.stat().st_mode
            file_path.chmod(mode | 0o111)  # Add executable bit
            logger.debug(f"Made file executable: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to make file executable: {e}")
            return False
    return True  # On Windows, executable bit is not relevant

def setup_environment(use_gpu=True, force_gpu=False, enable_monitoring=False):
    """
    Set up the research environment.
    
    Args:
        use_gpu (bool): Whether to configure for GPU support
        force_gpu (bool): Force GPU configuration even if no GPU is detected
        enable_monitoring (bool): Enable monitoring setup
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Create directory structure
    if not ensure_directory_structure():
        return False
    
    # Detect GPU
    has_gpu = force_gpu or (use_gpu and detect_gpu())
    
    # Make entrypoint executable
    entrypoint_path = PROJECT_ROOT / "entrypoint.sh"
    if not entrypoint_path.exists():
        # Create a default entrypoint.sh
        with open(entrypoint_path, 'w') as f:
            f.write("""#!/bin/bash

# Default entrypoint script for the research environment
echo "Starting research environment..."

# Start Jupyter Lab
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''
""")
    
    make_executable(entrypoint_path)
    
    # Create symlinks if needed
    docker_dir = PROJECT_ROOT / "docker"
    entrypoint_link = docker_dir / "entrypoint.sh"
    if not entrypoint_link.exists():
        try:
            os.symlink(
                os.path.relpath(entrypoint_path, docker_dir),
                entrypoint_link
            )
            logger.debug(f"Created symlink: {entrypoint_link}")
        except OSError as e:
            logger.warning(f"Failed to create symlink: {e}")
    
    # Set up GPU configuration if needed
    if has_gpu:
        logger.info("Setting up GPU configuration...")
        gpu_setup_script = PROJECT_ROOT / "setup" / "gpu_setup.sh"
        if gpu_setup_script.exists():
            try:
                if platform.system() == "Windows":
                    # On Windows, we just ensure the script exists, actual execution happens at Docker runtime
                    logger.info("GPU setup script exists but can't be executed on Windows directly")
                else:
                    make_executable(gpu_setup_script)
                    subprocess.run([str(gpu_setup_script)], check=True)
                logger.info("GPU setup completed")
            except subprocess.CalledProcessError as e:
                logger.error(f"GPU setup failed: {e}")
                return False
    
    # Set up monitoring if enabled
    if enable_monitoring:
        setup_monitoring()
    
    return True

def setup_monitoring():
    """
    Set up monitoring stack (Prometheus + Grafana).
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Setting up monitoring stack...")
    
    # Configure monitoring directories
    monitoring_dir = PROJECT_ROOT / "monitoring"
    prometheus_dir = monitoring_dir / "prometheus"
    grafana_dir = monitoring_dir / "grafana"
    
    # Create Prometheus configuration
    prometheus_config = prometheus_dir / "prometheus.yml"
    if not prometheus_config.exists():
        with open(prometheus_config, 'w') as f:
            f.write("""
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
""")
    
    # Create Grafana configuration
    grafana_datasource = grafana_dir / "provisioning" / "datasources" / "datasource.yml"
    os.makedirs(grafana_datasource.parent, exist_ok=True)
    
    if not grafana_datasource.exists():
        with open(grafana_datasource, 'w') as f:
            f.write("""
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
""")
    
    logger.info("Monitoring setup completed")
    return True
