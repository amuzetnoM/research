# Installation Guide

This document details the installation process for the AI Research Environment.

## Prerequisites

- Python 3.8+
- Docker
- Docker Compose
- NVIDIA drivers (optional, for GPU support)
- NVIDIA Container Toolkit (optional, for GPU support)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd research
```

### 2. Install Dependencies

Run the setup script to install all required dependencies:

```bash
python setup/setup.py
```

This script will:
- Make the entrypoint and helper scripts executable
- Check for Docker and Docker Compose installation
- Detect GPU availability and configure NVIDIA Docker support
- Install Python dependencies

### 3. Package Installation (Optional)

To install as a Python package:

```bash
pip install -e .
```

## Environment Configuration

The environment can be configured through the `environment_manager.py` script with various options:

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

## Verifying Installation

### Basic Verification

To verify that everything is installed correctly:

```bash
# Check Python and dependencies
python -c "import torch, tensorflow; print(f'PyTorch GPU: {torch.cuda.is_available()}, TensorFlow GPU: len(tensorflow.config.list_physical_devices(\"GPU\")) > 0')"

# Check utilities
python -c "from utils.gpu_utils import gpu_manager; print(f'GPU Available: {gpu_manager.check_gpu_availability()}')"
```

### Docker Setup Verification

To verify Docker setup:

```bash
docker --version
docker-compose --version
```

For GPU support verification:

```bash
# Check NVIDIA Docker configuration
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## Running Diagnostics

The environment includes a built-in diagnostics tool:

```bash
python -c "from utils.diagnostics import run_diagnostics; run_diagnostics()"
```

This will provide comprehensive information about your system and help identify any potential issues with the installation.

## Starting the Environment

After installation, start the research environment:

```bash
python environment_manager.py
```

Once running, you can access:
- JupyterLab at http://localhost:8888 (default token: `researchenv`)
- TensorBoard at http://localhost:6006 (if enabled)
- Monitoring Dashboard at http://localhost:3000 (if enabled, default credentials: `admin/admin`)

## Stopping the Environment

To stop the environment:

```bash
python environment_manager.py --stop
```

## Troubleshooting

If you encounter any issues during installation, please refer to the [Troubleshooting Guide](../troubleshooting/common_issues.md).
