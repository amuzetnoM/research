# Docker Configuration

This document explains the Docker configuration options available in the AI Research Environment.

## Docker Location

All Docker configuration files are now located in the `head_1` directory, providing a centralized location for container management:

```
head_1/
├── Dockerfile        # Main environment Dockerfile
└── docker-compose.yml # Container orchestration setup
```

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

The system automatically selects the appropriate base image depending on your hardware using the `environment_manager.py` script.

## Docker Compose

The docker-compose.yml file provides a streamlined way to start the container with all necessary configurations:

```yaml
version: '3.8'

services:
  ml-app:
    build:
      context: .
      dockerfile: head_1/Dockerfile
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
- 3000:3000 - Grafana (when monitoring is enabled)
- 9090:9090 - Prometheus (when monitoring is enabled)

## Volume Mappings

The default volume mapping mounts the current directory to /app in the container:
```
$(pwd):/app
```

Additional volumes can be mounted as needed for data directories, model storage, etc.

## Starting Docker Containers

### Using environment_manager.py

The recommended way to start containers is using the unified `environment_manager.py` script:

```bash
python environment_manager.py
```

This script:
1. Checks for Docker and Docker Compose installation
2. Detects GPU availability using the integrated `gpu_utils` module
3. Automatically determines optimal memory and CPU allocations with `system_utils`
4. Configures and launches the appropriate Docker Compose setup

### Customizing Docker Configuration

You can customize the Docker configuration with command-line arguments:

```bash
python environment_manager.py --port 8080:8888 --volume /data:/app/data
```

Available options:
- `--port HOST:CONTAINER`: Map additional ports
- `--mem-limit LIMIT`: Set memory limit (e.g., 16g)
- `--cpu-limit COUNT`: Set CPU core limit
- `--no-gpu`: Disable GPU support
- `--enable-monitoring`: Enable Prometheus and Grafana monitoring
- `--build`: Rebuild containers before starting
- `--no-cache`: Do not use cache when building images
- `--stop`: Stop the running environment

For a complete list of options:
```bash
python environment_manager.py --help
```

## Container Entry Point

The environment uses an enhanced `entrypoint.sh` script that:

1. Automatically detects and configures GPU support
2. Optimizes resource allocation based on container limits
3. Sets up monitoring if enabled
4. Applies system-level optimizations for improved performance
5. Provides comprehensive diagnostics on failure

## Monitoring Integration

The Docker configuration integrates with Prometheus and Grafana for monitoring:

```bash
python environment_manager.py --enable-monitoring
```

This will automatically:
1. Start Prometheus for metrics collection
2. Start Grafana for visualization dashboards
3. Configure appropriate network settings
4. Mount necessary volume mappings

See the [Monitoring Documentation](../monitoring/overview.md) for more details.
