# Docker Configuration

This document explains the Docker configuration options available in this project.

## Dockerfile

The Dockerfile is configured to provide two paths:
1. GPU support via NVIDIA CUDA
2. CPU-only fallback

### Base Image

For GPU support:
```dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
```

For CPU-only:
```dockerfile
FROM ubuntu:22.04
```

The system automatically selects the appropriate base image depending on your hardware.

## Docker Compose

The docker-compose.yml file provides a streamlined way to start the container with all necessary configurations:

```yaml
version: '3.8'

services:
  ml-app:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - .:/app
    ports:
      - "8888:8888"
      - "6006:6006"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

## Port Mappings

Default port mappings:
- 8888:8888 - JupyterLab
- 6006:6006 - TensorBoard

## Volume Mappings

The default volume mapping mounts the current directory to /app in the container:
```
$(pwd):/app
```

## Starting Docker Containers

### Using start_docker.py

The recommended way to start containers is using the `start_docker.py` script:

```bash
python start_docker.py
```

This script:
1. Checks for Docker installation
2. Detects GPU availability
3. Creates necessary configuration files if they don't exist
4. Builds and runs the Docker container

### Customizing Docker Configuration

You can customize the Docker configuration with command-line arguments:

```bash
python start_docker.py --port 8080:8888 --volume /data:/app/data
```

Available options:
- `--image NAME`: Custom Docker image name
- `--container NAME`: Custom container name
- `--no-gpu`: Disable GPU support
- `--port HOST:CONTAINER`: Map additional ports
- `--volume HOST:CONTAINER`: Mount additional volumes
- `--command CMD`: Specify a custom command to run
