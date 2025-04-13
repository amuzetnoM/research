"""
Docker Preparation

Handles preparation for Docker deployment, including checking
prerequisites and generating Docker configuration files.
"""

import logging
import os
import platform
import subprocess
import sys
from pathlib import Path

from .utils import system_utils

# Get logger
logger = logging.getLogger('setup')

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

def check_docker_prerequisites():
    """
    Check if Docker and Docker Compose are installed.
    
    Returns:
        bool: True if prerequisites are met, False otherwise
    """
    logger.info("Checking Docker prerequisites...")
    
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
        logger.info("Visit https://docs.docker.com/get-docker/ for installation instructions.")
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
    
    return True

def prepare_dockerfile(use_gpu=False):
    """
    Prepare Dockerfile based on environment configuration.
    
    Args:
        use_gpu (bool): Whether to include GPU support
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Preparing Dockerfile with GPU support: {use_gpu}")
    
    docker_dir = PROJECT_ROOT / "docker"
    dockerfile_path = docker_dir / "Dockerfile"
    
    # Create base Dockerfile
    with open(dockerfile_path, 'w') as f:
        if use_gpu:
            f.write("""FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    python3 python3-pip python3-dev \\
    git wget curl \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy requirements
COPY setup/requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy utilities
COPY utils /workspace/utils

# Expose ports
EXPOSE 8888 6006 3000 9090

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
WORKDIR /workspace

# Copy requirements
COPY setup/requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy utilities
COPY utils /workspace/utils

# Expose ports
EXPOSE 8888 6006 3000 9090

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
""")
    
    logger.info(f"Created Dockerfile at {dockerfile_path}")
    return True

def prepare_docker_compose(use_gpu=False):
    """
    Prepare docker-compose.yml based on environment configuration.
    
    Args:
        use_gpu (bool): Whether to include GPU support
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Preparing docker-compose.yml with GPU support: {use_gpu}")
    
    docker_dir = PROJECT_ROOT / "docker"
    compose_path = docker_dir / "docker-compose.yml"
    
    # Create base docker-compose.yml
    with open(compose_path, 'w') as f:
        if use_gpu:
            f.write("""version: '3'

services:
  research:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    image: research-env
    container_name: research-env
    volumes:
      - ../notebooks:/workspace/notebooks
      - ../data:/workspace/data
    ports:
      - "8888:8888"  # JupyterLab
      - "6006:6006"  # TensorBoard
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
""")
        else:
            f.write("""version: '3'

services:
  research:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    image: research-env
    container_name: research-env
    volumes:
      - ../notebooks:/workspace/notebooks
      - ../data:/workspace/data
    ports:
      - "8888:8888"  # JupyterLab
      - "6006:6006"  # TensorBoard
""")
    
    logger.info(f"Created docker-compose.yml at {compose_path}")
    return True

def create_run_script():
    """
    Create the run script for launching the Docker environment.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Creating run script...")
    
    run_script_path = PROJECT_ROOT / "run.sh"
    
    with open(run_script_path, 'w') as f:
        f.write("""#!/bin/bash

# Make scripts executable
chmod +x entrypoint.sh 2>/dev/null || true

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit https://docs.docker.com/compose/install/ for installation instructions."
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
    
    # Make the file executable
    if platform.system() != "Windows":
        os.chmod(run_script_path, 0o755)
    
    logger.info(f"Created run script at {run_script_path}")
    return True

def prepare_for_docker(use_gpu=False):
    """
    Prepare the environment for Docker deployment.
    
    Args:
        use_gpu (bool): Whether to include GPU support
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Check Docker prerequisites
    if not check_docker_prerequisites():
        return False
    
    # Prepare Dockerfile
    if not prepare_dockerfile(use_gpu):
        return False
    
    # Prepare docker-compose.yml
    if not prepare_docker_compose(use_gpu):
        return False
    
    return True
