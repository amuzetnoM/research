# JupyterLab Usage Example

This guide demonstrates how to use JupyterLab within the Docker environment.

## Starting JupyterLab

JupyterLab is the default application started in the container:

```bash
python start_docker.py
```

This will start JupyterLab on port 8888.

## Accessing JupyterLab

1. Open your browser and navigate to: http://localhost:8888
2. No password or token is required by default

## Creating a New Notebook

1. Click the "Python 3" icon under "Notebook" in the launcher
2. A new notebook will open

## GPU Test in JupyterLab

Create a new notebook and run the following code to test GPU access:

```python
# Check if GPU is available (PyTorch)
import torch
print(f"PyTorch GPU available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")

# Check if GPU is available (TensorFlow)
import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
print(f"TensorFlow GPUs: {gpus}")

# Run a simple GPU task
if torch.cuda.is_available():
    # Create random tensors
    x = torch.randn(1000, 1000).cuda()
    y = torch.randn(1000, 1000).cuda()
    
    # Measure time for matrix multiplication
    import time
    start = time.time()
    z = torch.matmul(x, y)
    torch.cuda.synchronize()
    end = time.time()
    
    print(f"GPU time: {end - start:.4f} seconds")
    
    # CPU comparison
    x_cpu = x.cpu()
    y_cpu = y.cpu()
    
    start = time.time()
    z_cpu = torch.matmul(x_cpu, y_cpu)
    end = time.time()
    
    print(f"CPU time: {end - start:.4f} seconds")
```

## Additional Features

### Running TensorBoard

```python
# In your notebook
%load_ext tensorboard
%tensorboard --logdir ./logs
```

TensorBoard will be available at http://localhost:6006

### Installing Additional Packages

```python
!pip install pandas-profiling xgboost lightgbm
```

### Saving Your Work

Files created in JupyterLab are automatically saved to your host machine through the volume mapping.

## Stopping JupyterLab

To stop the container and JupyterLab:

1. Press Ctrl+C in the terminal where you started the container
2. Or run: `docker stop ml-container`
