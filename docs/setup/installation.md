# Installation Guide

This document details the installation process for the ML Docker Environment.

## Prerequisites

- Python 3.8+
- Docker
- NVIDIA drivers (optional, for GPU support)

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
- Make helper scripts executable
- Check for Docker installation
- Detect GPU availability
- Install Python dependencies

### 3. Package Installation (Optional)

To install as a Python package:

```bash
pip install -e .
```

## Verifying Installation

To verify that everything is installed correctly:

```bash
python -c "import torch; print(f'GPU Available: {torch.cuda.is_available()}')"
```

## Docker Setup Verification

To verify Docker setup:

```bash
docker --version
```

For GPU support verification:

```bash
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```
