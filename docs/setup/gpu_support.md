# GPU Support Configuration

This document explains how to configure and verify GPU support in the AI Research Environment.

## Prerequisites

To use GPU acceleration, you need:

1. NVIDIA GPU with CUDA support
2. NVIDIA drivers installed (version 450.80.02 or later recommended)
3. NVIDIA Container Toolkit (nvidia-docker2)

## Checking GPU Availability

### System Check

To check if your system recognizes the GPU:

```bash
nvidia-smi
```

Expected output:
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 515.65.01    Driver Version: 515.65.01    CUDA Version: 11.7     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  NVIDIA GeForce ...  Off  | 00000000:01:00.0  On |                  N/A |
| N/A   45C    P8    N/A /  N/A |    345MiB /  6144MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
```

### Using Built-in GPU Utilities

Our environment includes sophisticated GPU detection and optimization utilities:

```python
# Using the GPU manager to check availability
from utils.gpu_utils import gpu_manager

# Check if GPU is available
is_available = gpu_manager.check_gpu_availability()
print(f"GPU Available: {is_available}")

# Get detailed GPU information
if is_available:
    gpu_info = gpu_manager.get_gpu_info()
    for idx, gpu in enumerate(gpu_info):
        print(f"GPU {idx}: {gpu['name']} - {gpu['memory_total_mb']}MB total, "
              f"{gpu['memory_free_mb']}MB free, {gpu['utilization_pct']}% utilization")
              
    # Get optimal GPU settings
    settings = gpu_manager.get_optimal_gpu_settings()
    print("\nRecommended GPU settings:")
    for key, value in settings.items():
        print(f"  {key}={value}")
```

### Framework-Specific Checks

To check GPU availability for specific ML frameworks:

```python
# TensorFlow
import tensorflow as tf
print(f"TensorFlow GPU available: {len(tf.config.list_physical_devices('GPU')) > 0}")

# PyTorch
import torch
print(f"PyTorch GPU available: {torch.cuda.is_available()}")
print(f"PyTorch GPU count: {torch.cuda.device_count()}")
```

## Installing NVIDIA Container Toolkit

If not already installed:

### Ubuntu

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### CentOS/RHEL

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo | sudo tee /etc/yum.repos.d/nvidia-docker.repo
sudo yum install -y nvidia-container-toolkit
sudo systemctl restart docker
```

## Testing GPU in Docker

To test if Docker can access the GPU:

```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## GPU Configuration in This Project

The `environment_manager.py` script automatically:
1. Detects GPU availability using the `gpu_utils` module
2. Configures Docker with appropriate GPU flags
3. Sets optimal environment variables for GPU performance
4. Falls back to CPU if no GPU is detected or if explicitly disabled

You can manually control GPU usage:

```bash
# Force disable GPU even if available
python environment_manager.py --no-gpu

# Default (auto-detect)
python environment_manager.py
```

## Debugging GPU Issues

If you're experiencing GPU-related issues:

1. Run the built-in diagnostics:
   ```bash
   python -c "from utils.diagnostics import run_diagnostics; run_diagnostics()"
   ```

2. Check Docker's GPU access:
   ```bash
   python -c "from utils.gpu_utils import gpu_manager; print(gpu_manager.check_docker_gpu_support())"
   ```

3. Verify that appropriate Docker flags are being used:
   ```bash
   python -c "from utils.gpu_utils import gpu_manager; print(gpu_manager.get_docker_gpu_flags())"
   ```

## GPU Resource Optimization

The environment automatically optimizes GPU resource allocation:

- **Memory Allocation**: Sets appropriate memory limits for TensorFlow and PyTorch
- **Thread Configuration**: Configures optimal thread counts for parallel processing
- **Mixed Precision**: Enables automatic mixed precision where supported
- **Multi-GPU Support**: Automatically detects and configures multiple GPUs

To manually override GPU optimization settings, you can set environment variables before starting the environment:

```bash
export TF_MEMORY_ALLOCATION=0.5  # Use 50% of GPU memory for TensorFlow
export CUDA_VISIBLE_DEVICES=0     # Only use the first GPU
python environment_manager.py
```
