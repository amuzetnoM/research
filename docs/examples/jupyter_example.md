# JupyterLab Usage Example

This guide demonstrates how to use JupyterLab within the Docker environment with robust error handling.

## Starting JupyterLab

JupyterLab is the default application started in the container:

```bash
python environment_manager.py
```

This will start JupyterLab on port 8888.

## Accessing JupyterLab

1. Open your browser and navigate to: http://localhost:8888
2. Default token is `researchenv`

## Setting Up Error Handling in Notebooks

For robust error handling in your notebooks, add the following code to a cell at the beginning of each notebook:

```python
# Setup error handling in this notebook
import sys
import logging
from datetime import datetime
from utils.diagnostics import diagnostic_collector, handle_exception, setup_error_handlers

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('notebook')

# Custom exception handler for notebook
def notebook_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Handle KeyboardInterrupt specially
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Display the error and save diagnostics
    print(f"Error: {exc_type.__name__}: {exc_value}")
    print("\nCollecting diagnostics...")
    diagnostic_collector.collect_all()
    filepath = diagnostic_collector.save_diagnostics(f"notebook_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    print(f"Diagnostics saved to {filepath}")
    
    # Display the traceback
    import traceback
    traceback.print_exception(exc_type, exc_value, exc_traceback)

# Set the custom exception handler
sys.excepthook = notebook_exception_handler

print("Error handling configured for this notebook")
```

## Creating a New Notebook

1. Click the "Python 3" icon under "Notebook" in the launcher
2. A new notebook will open
3. Add the error handling code from above to the first cell

## Robust GPU Test Example

Create a new notebook and run the following code to test GPU access with proper error handling:

```python
# First, set up error handling as shown above

# Try GPU operations with proper error handling
try:
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
    else:
        print("No GPU available, skipping GPU tests")
except ImportError as e:
    # Handle missing libraries
    handle_exception("Could not import required libraries", e)
    print("Please ensure PyTorch and TensorFlow are properly installed")
except RuntimeError as e:
    # Handle CUDA errors
    if "CUDA" in str(e):
        # Import GPU utilities for diagnostics
        from utils.gpu_utils import gpu_manager
        
        # Log error with GPU information
        gpu_info = gpu_manager.get_gpu_info()
        handle_exception("GPU operation failed", e)
        
        # Print helpful information
        if gpu_info:
            print(f"GPU detected but operation failed. Current GPU Memory usage:")
            for idx, info in enumerate(gpu_info):
                print(f"GPU {idx}: {info.get('memory_used_mb', 'N/A')}MB / {info.get('memory_total_mb', 'N/A')}MB")
            print("\nTry reducing batch size or model complexity")
        else:
            print("No GPU information available. Ensure NVIDIA drivers are properly installed.")
    else:
        # Handle other runtime errors
        handle_exception("Unexpected runtime error", e)
except Exception as e:
    # Catch any other exceptions
    handle_exception("Unexpected error during GPU test", e)
```

## Using the Retry Decorator for Network Operations

For operations that might fail temporarily (like downloading data), use the retry decorator:

```python
from utils.diagnostics import retry

# Define a function with retry capability
@retry(max_attempts=3, delay=1.0, backoff=2.0, exceptions=(ConnectionError, TimeoutError))
def download_dataset(url):
    """Download a dataset with automatic retry on failure."""
    import requests
    print(f"Attempting to download from {url}...")
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.content

# Use it in a try-except block
try:
    # Replace with your actual dataset URL
    data = download_dataset("https://example.com/dataset.csv")
    print(f"Successfully downloaded {len(data)} bytes")
    
    # Save the data
    with open("dataset.csv", "wb") as f:
        f.write(data)
except Exception as e:
    handle_exception("Failed to download dataset", e)
```

## Resource Monitoring in Notebooks

Add resource monitoring to your notebook:

```python
from utils.system_utils import system_manager
from utils.gpu_utils import gpu_manager

def print_resource_usage():
    """Print current system and GPU resource usage."""
    # Get system information
    mem_info = system_manager.get_system_memory(), system_manager.get_available_memory()
    print(f"System Memory: {mem_info[1]} MB available out of {mem_info[0]} MB total")
    
    # Get GPU information if available
    if gpu_manager.check_gpu_availability():
        gpu_info = gpu_manager.get_gpu_info()
        for idx, info in enumerate(gpu_info):
            print(f"GPU {idx}: {info.get('name')}")
            print(f"  Memory: {info.get('memory_used_mb')}MB / {info.get('memory_total_mb')}MB")
            print(f"  Utilization: {info.get('utilization')}%")
    else:
        print("No GPU available")

# Call this function whenever you want to monitor resource usage
print_resource_usage()
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
try:
    # Install packages with pip
    !pip install pandas-profiling xgboost lightgbm
    
    # Verify installation
    import pandas_profiling
    import xgboost
    import lightgbm
    print("Packages successfully installed and imported")
except Exception as e:
    handle_exception("Failed to install or import packages", e)
    print("Try manually installing one package at a time to identify the problematic package")
```

### Saving Your Work

Files created in JupyterLab are automatically saved to your host machine through the volume mapping. For robust file saving:

```python
def safe_save(data, filename):
    """Safely save data to a file with error handling."""
    try:
        # Create a backup of existing file
        import os
        if os.path.exists(filename):
            backup_name = f"{filename}.bak"
            import shutil
            shutil.copy2(filename, backup_name)
            print(f"Created backup at {backup_name}")
        
        # Save the file
        with open(filename, 'w') as f:
            f.write(data)
        print(f"Successfully saved to {filename}")
        return True
    except Exception as e:
        handle_exception(f"Failed to save to {filename}", e)
        return False

# Example usage
model_summary = "This is a test model summary"
safe_save(model_summary, "model_summary.txt")
```

## Exporting Notebooks with Results

To export a notebook with all cell outputs:

```python
try:
    from nbconvert import HTMLExporter
    import nbformat
    import os
    
    # Define notebook name
    notebook_name = os.path.basename(os.environ.get('JUPYTER_SERVER_ROOT', '.')) + '.ipynb'
    
    # Export to HTML
    html_exporter = HTMLExporter()
    html_exporter.template_name = 'classic'
    
    # Load the notebook
    with open(notebook_name, 'r') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Export to HTML
    (body, resources) = html_exporter.from_notebook_node(nb)
    
    # Write to file
    html_file = notebook_name.replace('.ipynb', '.html')
    with open(html_file, 'w') as f:
        f.write(body)
    
    print(f"Notebook exported to {html_file}")
except Exception as e:
    handle_exception("Failed to export notebook", e)
```

## Stopping JupyterLab

To stop the container and JupyterLab:

1. Press Ctrl+C in the terminal where you started the container
2. Or run: `python environment_manager.py --stop`

## Advanced Error Handling

For more detailed information about error handling capabilities, refer to the [Error Handling Guide](../advanced/error_handling.md).
