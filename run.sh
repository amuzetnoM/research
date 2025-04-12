#!/bin/bash

# Make scripts executable
chmod +x entrypoint.sh gpu_check.py

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
echo "Building and running container with Docker Compose..."
docker-compose up --build

# Execute this script to run the container
# Usage: ./run.sh
