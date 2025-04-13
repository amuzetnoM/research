# Setup and Installation

This comprehensive guide covers everything needed to set up the AI Research Environment.

## Prerequisites

- Python 3.8+
- Docker
- Docker Compose
- NVIDIA drivers (optional, for GPU support)

## Installation Steps

```bash
# Clone the repository
git clone <repository-url>
cd research

# Run setup script
python -m setup.setup

# Start the research environment with monitoring
python environment_manager.py --enable-monitoring
```

## Environment Configuration

The environment can be configured through the `environment_manager.py` script:

```bash
python environment_manager.py --help
```

Common configuration options:

```bash
# Basic configuration
python environment_manager.py --port 8888:8888 --jupyter-token mytoken

# Resource limits
python environment_manager.py --mem-limit 16g --cpu-limit 4

# GPU configuration
python environment_manager.py --no-gpu  # Disable GPU even if available

# Monitoring
python environment_manager.py --enable-monitoring --monitor-port 3000
```

## Starting and Stopping

Start the environment:
```bash
python environment_manager.py
```

Once running, you can access:
- JupyterLab at http://localhost:8888 (default token: `researchenv`)
- Monitoring Dashboard at http://localhost:3000 (if enabled)
- TensorBoard at http://localhost:6006 (if enabled)

Stop the environment:
```bash
python environment_manager.py --stop
```

## Docker Configuration

### Port Mappings

Default port mappings:
- 8888:8888 - JupyterLab
- 6006:6006 - TensorBoard
- 3000:3000 - Grafana (when monitoring is enabled)
- 9090:9090 - Prometheus (when monitoring is enabled)

### Volume Mappings

The default volume mapping mounts the current directory to /app in the container:
```
$(pwd):/app
```

Additional volumes can be mounted as needed for data directories, model storage, etc.
