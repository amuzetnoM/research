# GPU Support Configuration

This document explains how to configure and verify GPU support in this environment.

## Prerequisites

To use GPU acceleration, you need:

1. NVIDIA GPU with CUDA support
2. NVIDIA drivers installed
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

### Python Check

To check GPU availability in Python:

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
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

## GPU Configuration in This Project

The `start_docker.py` script automatically:
1. Detects GPU availability
2. Configures Docker with GPU support if available
3. Falls back to CPU if no GPU is detected

You can manually specify GPU usage:

```bash
# Force disable GPU
python start_docker.py --no-gpu

# Default (auto-detect)
python start_docker.py
```
