# Error Handling Guide

This document provides comprehensive guidance on error handling in the AI Research Environment, including how to use the built-in error handling utilities, how to implement proper error handling in your own code, and how to troubleshoot common errors.

## Error Handling Framework

The AI Research Environment includes a robust error handling framework in the `utils.diagnostics` module. This framework provides:

- Exception classes specific to the research environment
- Comprehensive error logging and reporting
- Automatic diagnostic information collection
- Retry mechanism for transient errors
- Signal handling for graceful shutdowns

## Using the Error Handling Framework

### Basic Error Handling

For basic error handling in your scripts:

```python
from utils.diagnostics import handle_exception

try:
    # Your code that might raise an exception
    result = perform_complex_operation()
except Exception as e:
    # Handle the exception with proper logging and diagnostics
    handle_exception("Failed to perform complex operation", e)
    # Optionally exit with a non-zero code
    # handle_exception("Failed to perform complex operation", e, exit_code=1)
```

### Environment-Specific Exceptions

Use the environment-specific exception classes for better error categorization:

```python
from utils.diagnostics import ResourceError, ConfigurationError, DockerError, NetworkError

# Example: Check for sufficient memory
def check_memory_requirements(required_mb):
    from utils.system_utils import system_manager
    available_mb = system_manager.get_available_memory()
    
    if available_mb < required_mb:
        raise ResourceError(
            f"Insufficient memory: required {required_mb}MB, only {available_mb}MB available"
        )
```

### Retry Mechanism for Transient Errors

Use the retry decorator for operations that might fail temporarily (e.g., network operations):

```python
from utils.diagnostics import retry

# Retry up to 3 times with exponential backoff
@retry(max_attempts=3, delay=1.0, backoff=2.0, exceptions=(ConnectionError, TimeoutError))
def download_dataset(url):
    # This function will be retried up to 3 times if it raises ConnectionError or TimeoutError
    import requests
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.content
```

### Collecting Diagnostic Information

To collect diagnostic information about the current environment:

```python
from utils.diagnostics import diagnostic_collector

# Collect diagnostic information
diagnostic_data = diagnostic_collector.collect_all()

# Print a summary
diagnostic_collector.print_summary()

# Save the diagnostic information to a file
file_path = diagnostic_collector.save_diagnostics("my_diagnostics.json")
print(f"Diagnostics saved to {file_path}")
```

### Setting Up Global Error Handlers

To set up global error handlers for uncaught exceptions and signals:

```python
from utils.diagnostics import setup_error_handlers

# Call this at the beginning of your main script
setup_error_handlers()
```

## Error Handling Best Practices

### 1. Be Specific with Exception Types

Instead of catching generic exceptions:

```python
try:
    # Code
except Exception as e:
    # Handle all exceptions the same way
```

Be more specific when possible:

```python
try:
    # Code
except FileNotFoundError as e:
    # Handle missing file
except PermissionError as e:
    # Handle permission issues
except Exception as e:
    # Fallback for other exceptions
```

### 2. Provide Contextual Information

Always include contextual information when handling errors:

```python
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
except json.JSONDecodeError as e:
    handle_exception(f"Invalid JSON in file {file_path} at line {e.lineno}, column {e.colno}", e)
```

### 3. Clean Up Resources

Use `finally` blocks or context managers to ensure resources are properly cleaned up:

```python
file_handle = None
try:
    file_handle = open('output.txt', 'w')
    file_handle.write('Data')
except IOError as e:
    handle_exception("Failed to write to output file", e)
finally:
    # This will run even if an exception occurs
    if file_handle:
        file_handle.close()
```

Better yet, use context managers:

```python
try:
    with open('output.txt', 'w') as file_handle:
        file_handle.write('Data')
except IOError as e:
    handle_exception("Failed to write to output file", e)
```

### 4. Log Before Raising

If you need to re-raise an exception, log it first:

```python
try:
    # Attempt some operation
except Exception as e:
    logging.error(f"Operation failed: {e}")
    # Add context and re-raise
    raise RuntimeError(f"Processing pipeline failed") from e
```

## Error Notifications

The error handling framework supports notifications for critical errors. To enable notifications:

1. Set the `NOTIFY_METHOD` environment variable to your preferred notification method:

```bash
# For console notifications
export NOTIFY_METHOD=console

# For file-based notifications
export NOTIFY_METHOD=file
```

2. Use the `notify` parameter when handling exceptions:

```python
try:
    # Critical operation
except Exception as e:
    handle_exception("Critical error in data processing", e, notify=True)
```

## Common Error Patterns and Solutions

### Out of Memory Errors

Memory errors often manifest as killed processes or `MemoryError` exceptions:

```python
try:
    large_array = numpy.zeros((1000000, 1000000))  # Attempt to allocate too much memory
except MemoryError as e:
    # The diagnostics module will automatically log memory stats
    handle_exception("Memory allocation failed", e)
    
    # Recommend solutions
    from utils.system_utils import system_manager
    print(f"Available memory: {system_manager.get_available_memory()} MB")
    print("Consider reducing batch size or using data generators")
```

### GPU-Related Errors

For GPU-related errors:

```python
try:
    # GPU operation
    import torch
    tensor = torch.ones(1000, 1000, device='cuda')
except RuntimeError as e:
    if "CUDA out of memory" in str(e):
        from utils.gpu_utils import gpu_manager
        info = gpu_manager.get_gpu_info()
        handle_exception("GPU memory allocation failed", e)
        print(f"GPU memory: {info[0]['memory_used_mb']}MB used out of {info[0]['memory_total_mb']}MB")
        print("Consider reducing batch size or model size")
    else:
        handle_exception("GPU operation failed", e)
```

### Docker and Container Errors

For Docker-related errors:

```python
try:
    # Docker operation
    import subprocess
    result = subprocess.run(["docker", "run", "image"], check=True)
except subprocess.SubprocessError as e:
    # Check if Docker is running
    import shutil
    if not shutil.which("docker"):
        handle_exception("Docker not found in PATH", e)
    else:
        handle_exception("Docker operation failed", e)
        print("Ensure Docker daemon is running with 'sudo systemctl start docker'")
```

## Debugging Errors

The research environment includes tools to help debug errors:

### Running Diagnostics

Run comprehensive diagnostics to understand the current state:

```bash
python -c "from utils.diagnostics import run_diagnostics; run_diagnostics()"
```

### Examining Error Reports

Error reports are saved in the `logs` directory with a timestamp, e.g., `logs/error_report_20250412_123045.json`. These contain valuable information for debugging.

## Implementing Error Handling in Jupyter Notebooks

For Jupyter notebooks, add the following to a cell at the beginning of your notebook:

```python
# Setup error handling in this notebook
import sys
from utils.diagnostics import handle_exception, diagnostic_collector

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
    filepath = diagnostic_collector.save_diagnostics()
    print(f"Diagnostics saved to {filepath}")
    
    # Display the traceback
    import traceback
    traceback.print_exception(exc_type, exc_value, exc_traceback)

# Set the custom exception handler
sys.excepthook = notebook_exception_handler

print("Error handling configured for this notebook")
```

## Extended Example: Robust Data Processing Pipeline

Here's a complete example of a robust data processing pipeline with proper error handling:

```python
import os
import logging
from typing import List, Dict, Any, Optional
from utils.diagnostics import handle_exception, retry, ResourceError
from utils.system_utils import system_manager

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('data_pipeline')

class DataProcessor:
    def __init__(self, input_dir: str, output_dir: str):
        # Validate directories
        if not os.path.isdir(input_dir):
            raise ConfigurationError(f"Input directory does not exist: {input_dir}")
        
        if not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except OSError as e:
                raise ConfigurationError(f"Could not create output directory: {output_dir}") from e
        
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # Check system resources
        self._check_resources()
        
    def _check_resources(self):
        """Verify we have sufficient resources for processing."""
        # Check available memory
        available_mb = system_manager.get_available_memory()
        if available_mb < 1024:  # Need at least 1GB
            raise ResourceError(f"Insufficient memory: only {available_mb}MB available")
        
        # Check available disk space
        disk_info = system_manager.get_disk_info()
        output_mount = self._find_mount_point(self.output_dir)
        if output_mount in disk_info:
            if disk_info[output_mount]['free_gb'] < 1.0:  # Need at least 1GB
                raise ResourceError(f"Insufficient disk space: only {disk_info[output_mount]['free_gb']:.1f}GB available")
    
    def _find_mount_point(self, path: str) -> str:
        """Find the mount point for a given path."""
        path = os.path.abspath(path)
        while not os.path.ismount(path):
            path = os.path.dirname(path)
        return path
    
    @retry(max_attempts=3, exceptions=(IOError, OSError))
    def _load_file(self, file_path: str) -> Dict[str, Any]:
        """Load a data file with retry capability."""
        import json
        
        logger.debug(f"Loading file: {file_path}")
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            # Don't retry JSON parsing errors
            raise ValueError(f"Invalid JSON in {file_path}: {e}") from e
    
    @retry(max_attempts=3, exceptions=(IOError, OSError))
    def _save_file(self, data: Dict[str, Any], file_path: str) -> None:
        """Save processed data with retry capability."""
        import json
        
        logger.debug(f"Saving file: {file_path}")
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def process_data(self, transform_func) -> int:
        """
        Process all data files using the provided transform function.
        
        Args:
            transform_func: Function that takes a data dict and returns transformed data
            
        Returns:
            Number of files successfully processed
        """
        processed_count = 0
        error_count = 0
        
        # Get list of input files
        try:
            input_files = [f for f in os.listdir(self.input_dir) 
                          if f.endswith('.json') and os.path.isfile(os.path.join(self.input_dir, f))]
        except OSError as e:
            handle_exception(f"Failed to list files in {self.input_dir}", e)
            return 0
        
        if not input_files:
            logger.warning(f"No JSON files found in {self.input_dir}")
            return 0
        
        # Process each file
        for filename in input_files:
            input_path = os.path.join(self.input_dir, filename)
            output_path = os.path.join(self.output_dir, f"processed_{filename}")
            
            try:
                # Load data
                data = self._load_file(input_path)
                
                # Transform data
                processed_data = transform_func(data)
                
                # Save results
                self._save_file(processed_data, output_path)
                
                processed_count += 1
                logger.info(f"Successfully processed {filename}")
                
            except Exception as e:
                error_count += 1
                handle_exception(f"Error processing {filename}", e)
                # Continue with next file instead of stopping the whole process
                continue
        
        logger.info(f"Processing complete. {processed_count} files processed successfully, {error_count} errors.")
        return processed_count

# Example usage
if __name__ == "__main__":
    from utils.diagnostics import setup_error_handlers
    
    # Set up global error handlers
    setup_error_handlers()
    
    try:
        # Initialize processor
        processor = DataProcessor(
            input_dir="./data/raw",
            output_dir="./data/processed"
        )
        
        # Define transformation function
        def transform_data(data):
            # Example transformation
            result = {}
            result['processed'] = True
            result['timestamp'] = datetime.now().isoformat()
            result['items'] = [item.upper() for item in data.get('items', [])]
            result['count'] = len(result['items'])
            return result
        
        # Process the data
        num_processed = processor.process_data(transform_data)
        print(f"Processed {num_processed} files")
        
    except Exception as e:
        handle_exception("Data processing pipeline failed", e, exit_code=1)
```

## Additional Resources

- [Common Issues Troubleshooting Guide](../troubleshooting/common_issues.md)
- [System Utilities Documentation](system_utils.md)
- [GPU Utilities Documentation](../setup/gpu_support.md)
- [Python Official Error Handling Documentation](https://docs.python.org/3/tutorial/errors.html)