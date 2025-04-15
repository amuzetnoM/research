#!/usr/bin/env python3
"""
Unified Runtime Optimization Module

This module provides comprehensive runtime optimization:
- Memory usage optimization
- CPU configuration and threading
- GPU memory management
- I/O performance tuning
- Framework initialization
- Container configuration
"""

import argparse
import json
import logging
import os
import platform
import subprocess
import sys
import time
import gc
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'runtime_optimizer.log'), mode='a')
    ]
)
logger = logging.getLogger('runtime_optimizer')

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Try to import optional dependencies
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    logger.warning("psutil not available, system monitoring will be limited")

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logger.warning("numpy not available, some optimizations will be disabled")

# Define colors for terminal output
COLORS = {
    "RED": "\033[0;31m",
    "GREEN": "\033[0;32m",
    "YELLOW": "\033[1;33m",
    "BLUE": "\033[0;34m",
    "RESET": "\033[0m"
}

# ==========================================
# Memory Optimization Functions
# ==========================================

def get_system_memory() -> int:
    """Get total system memory in MiB."""
    if HAS_PSUTIL:
        return psutil.virtual_memory().total // (1024 * 1024)
    else:
        logger.warning("psutil not available, using default memory value")
        return 8192  # Default to 8GB if psutil is not available

def get_container_memory_limit() -> Optional[int]:
    """Get container memory limit in MiB (if running in a container)."""
    # Check for cgroup v1 memory limit
    if os.path.exists('/sys/fs/cgroup/memory/memory.limit_in_bytes'):
        try:
            with open('/sys/fs/cgroup/memory/memory.limit_in_bytes', 'r') as f:
                mem_limit = int(f.read().strip())
                if mem_limit < 9223372036854771712:  # Not set to max value
                    return mem_limit // (1024 * 1024)
        except (IOError, ValueError):
            pass
            
    # Check for cgroup v2 memory limit
    if os.path.exists('/sys/fs/cgroup/memory.max'):
        try:
            with open('/sys/fs/cgroup/memory.max', 'r') as f:
                content = f.read().strip()
                if content != 'max':
                    mem_limit = int(content)
                    return mem_limit // (1024 * 1024)
        except (IOError, ValueError):
            pass
    
    return None

def calculate_optimal_memory() -> str:
    """Calculate optimal memory limit based on system memory.
    
    Returns:
        Memory limit string (e.g., "16g")
    """
    # Try to get container memory limit first
    container_memory = get_container_memory_limit()
    if container_memory:
        # Use 80% of container memory
        memory_limit = max(2048, int(container_memory * 0.8))
        return f"{memory_limit // 1024}g" if memory_limit >= 1024 else f"{memory_limit}m"
    
    # If not in container or can't detect limit, use system memory
    system_memory = get_system_memory()
    
    # Reserve some memory for the OS and other applications
    # Use 70% of total memory, but ensure at least 2GB
    memory_gb = max(2, int(system_memory * 0.7) // 1024)
    
    logger.info(f"Calculated optimal memory limit: {memory_gb}g")
    return f"{memory_gb}g"

def optimize_memory_usage(memory_limit: Optional[str] = None) -> Dict[str, str]:
    """Configure memory optimization settings.
    
    Args:
        memory_limit: Memory limit string (e.g., "16g")
        
    Returns:
        Dictionary of environment variables
    """
    logger.info("Optimizing memory usage...")
    
    if memory_limit is None:
        memory_limit = calculate_optimal_memory()
    
    # Convert memory limit to MB
    if memory_limit.endswith('g'):
        memory_mb = int(float(memory_limit[:-1]) * 1024)
    elif memory_limit.endswith('m'):
        memory_mb = int(float(memory_limit[:-1]))
    else:
        memory_mb = int(float(memory_limit) * 1024)
    
    logger.info(f"Setting memory limit to {memory_limit} ({memory_mb} MB)")
    
    # Configure memory optimization environment variables
    env_vars = {
        # Configure JVM memory (if applicable)
        "JAVA_OPTS": f"-Xms1g -Xmx{memory_mb}m",
        
        # Configure Python memory settings
        "MALLOC_TRIM_THRESHOLD_": "65536",
        "NPY_MMAP_MAX_LEN": str(memory_mb * 1024 * 1024),
        
        # Configure garbage collection for Python
        "PYTHONMALLOC": "malloc",
        "PYTHONMALLOCSTATS": "0",
        
        # Set memory growth for TensorFlow to avoid OOM
        "TF_FORCE_GPU_ALLOW_GROWTH": "true",
    }
    
    # Configure memory for PyTorch
    pytorch_mem = memory_mb // 2
    env_vars["PYTORCH_CUDA_ALLOC_CONF"] = f"max_split_size_mb:{pytorch_mem},garbage_collection_threshold:0.8"
    
    return env_vars

# ==========================================
# CPU Optimization Functions
# ==========================================

def calculate_optimal_cpu() -> int:
    """Calculate optimal number of CPU threads.
    
    Returns:
        Number of threads to use
    """
    if not HAS_PSUTIL:
        return 4  # Default if psutil not available
    
    try:
        # Get number of CPU cores
        cpu_count = psutil.cpu_count(logical=True)
        
        # Use all available cores, but keep at least 1 free for the OS
        # and never use more than 16 cores (diminishing returns)
        thread_count = min(max(1, cpu_count - 1), 16)
        
        logger.info(f"Calculated optimal CPU thread count: {thread_count}")
        return thread_count
    except Exception as e:
        logger.error(f"Error calculating optimal CPU threads: {e}")
        return 4  # Default fallback

def optimize_cpu_usage(num_threads: Optional[int] = None) -> Dict[str, str]:
    """Configure CPU optimization settings.
    
    Args:
        num_threads: Number of threads to use
        
    Returns:
        Dictionary of environment variables
    """
    logger.info("Optimizing CPU usage...")
    
    if num_threads is None:
        num_threads = calculate_optimal_cpu()
    
    logger.info(f"Setting thread count to {num_threads}")
    
    # Configure CPU optimization environment variables
    env_vars = {
        # Configure OpenMP threads
        "OMP_NUM_THREADS": str(num_threads),
        
        # Configure MKL threads (Intel Math Kernel Library)
        "MKL_NUM_THREADS": str(num_threads),
        
        # Configure OpenBLAS threads
        "OPENBLAS_NUM_THREADS": str(num_threads),
        "VECLIB_MAXIMUM_THREADS": str(num_threads),
        
        # Configure NumPy to use OpenBLAS
        "NUMEXPR_NUM_THREADS": str(num_threads),
        
        # Configure TensorFlow inter and intra op parallelism
        "TF_INTER_OP_PARALLELISM_THREADS": str(max(1, num_threads // 2)),
        "TF_INTRA_OP_PARALLELISM_THREADS": str(num_threads),
        
        # Configure Julia threads
        "JULIA_NUM_THREADS": str(num_threads),
    }
    
    return env_vars

# ==========================================
# GPU Optimization Functions
# ==========================================

def check_gpu_availability() -> bool:
    """Check if GPU is available.
    
    Returns:
        True if GPU is available, False otherwise
    """
    logger.info("Checking GPU availability...")
    
    try:
        # Try to use nvidia-smi to check for NVIDIA GPUs
        result = subprocess.run(
            ["nvidia-smi"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True
        )
        logger.info("NVIDIA GPU detected")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info("No NVIDIA GPU detected")
        
        # Check for ROCm GPU (AMD) as a fallback
        try:
            result = subprocess.run(
                ["rocminfo"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                check=True
            )
            logger.info("AMD GPU with ROCm detected")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info("No AMD GPU with ROCm detected")
        
        # Check for PyTorch CUDA availability as a fallback
        try:
            import torch
            if torch.cuda.is_available():
                logger.info("CUDA available through PyTorch")
                return True
            else:
                logger.info("CUDA not available through PyTorch")
        except ImportError:
            logger.info("PyTorch not available")
        
        # Check for TensorFlow GPU as a fallback
        try:
            import tensorflow as tf
            physical_devices = tf.config.list_physical_devices('GPU')
            if physical_devices:
                logger.info("GPU available through TensorFlow")
                return True
            else:
                logger.info("GPU not available through TensorFlow")
        except ImportError:
            logger.info("TensorFlow not available")
        
        return False

def get_gpu_info() -> List[Dict[str, Any]]:
    """Get GPU information.
    
    Returns:
        List of dictionaries with GPU information
    """
    gpus = []
    
    try:
        # Try to use nvidia-smi to get GPU information
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.used,memory.total,temperature.gpu,utilization.gpu", 
             "--format=csv,noheader,nounits"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        
        for line in result.stdout.strip().split('\n'):
            parts = line.split(', ')
            if len(parts) >= 5:
                gpu_info = {
                    "name": parts[0].strip(),
                    "memory_used_mb": float(parts[1].strip()),
                    "memory_total_mb": float(parts[2].strip()),
                    "temperature_c": float(parts[3].strip()),
                    "utilization_percent": float(parts[4].strip())
                }
                gpus.append(gpu_info)
        
        logger.info(f"Found {len(gpus)} GPUs")
    except Exception as e:
        logger.error(f"Error getting GPU information: {e}")
    
    return gpus

def optimize_gpu_usage() -> Dict[str, str]:
    """Configure GPU optimization settings.
    
    Returns:
        Dictionary of environment variables
    """
    logger.info("Optimizing GPU usage...")
    
    # Check GPU availability
    if not check_gpu_availability():
        logger.info("No GPU detected, disabling GPU support")
        return {
            "CUDA_VISIBLE_DEVICES": "",
            "TF_DISABLE_GPU": "1",
            "ENABLE_GPU": "false"
        }
    
    # Get GPU information
    gpus = get_gpu_info()
    
    # Configure GPU optimization environment variables
    env_vars = {
        "ENABLE_GPU": "true",
        
        # TensorFlow memory growth to avoid allocating all GPU memory
        "TF_FORCE_GPU_ALLOW_GROWTH": "true",
        "TF_GPU_THREAD_MODE": "gpu_private",
        
        # PyTorch memory settings
        "PYTORCH_NO_CACHE_ALLOCATOR": "0",
        "CUDA_LAUNCH_BLOCKING": "0",
        
        # Allow PyTorch to release memory
        "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:128,garbage_collection_threshold:0.8",
        
        # CUDA settings
        "CUDA_DEVICE_ORDER": "PCI_BUS_ID",
        
        # TensorFlow logging level
        "TF_CPP_MIN_LOG_LEVEL": "2",  # 0=DEBUG, 1=INFO, 2=WARNING, 3=ERROR
        
        # NVIDIA settings
        "NVIDIA_VISIBLE_DEVICES": "all",
        "NVIDIA_DRIVER_CAPABILITIES": "compute,utility",
        
        # cuDNN optimizations
        "CUDNN_LOGINFO_DBG": "1",
        "CUDNN_LOGDEST_DBG": "stdout",
    }
    
    # Optimize settings based on GPU information
    if gpus:
        # Get first GPU memory and adjust settings
        gpu_memory = gpus[0]["memory_total_mb"]
        
        # Configure TensorFlow thread count
        env_vars["TF_GPU_THREAD_COUNT"] = str(min(4, len(gpus) * 2))
        
        # Configure memory fractions and limits
        memory_fraction = 0.8  # Use 80% of GPU memory
        env_vars["TF_MEMORY_ALLOCATION"] = str(memory_fraction)
        
        # Configure PyTorch memory settings
        pytorch_mem = int(gpu_memory / 2)
        env_vars["PYTORCH_CUDA_ALLOC_CONF"] = f"max_split_size_mb:{pytorch_mem},garbage_collection_threshold:0.8"
        
        # Enable automatic mixed precision for faster inference/training
        env_vars["TF_ENABLE_AUTO_MIXED_PRECISION"] = "1"
        
        # Configure JAX memory settings
        env_vars["XLA_PYTHON_CLIENT_ALLOCATOR"] = "platform"
        env_vars["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"
        env_vars["XLA_PYTHON_CLIENT_MEM_FRACTION"] = "0.8"
        
        logger.info(f"GPU optimization configured for {gpu_memory} MB of GPU memory")
    
    return env_vars

# ==========================================
# I/O Optimization Functions
# ==========================================

def optimize_io_performance() -> Dict[str, str]:
    """Optimize I/O performance.
    
    Returns:
        Dictionary of environment variables
    """
    logger.info("Optimizing I/O performance...")
    
    # Configure I/O optimization environment variables
    env_vars = {
        # Python buffer size for stdout/stderr
        "PYTHONUNBUFFERED": "1",
        
        # File I/O buffer size
        "ARROW_BUFFER_SIZE": "65536",  # 64KB
        
        # HDF5 buffer size (if used)
        "HDF5_CACHE_SIZE": str(256 * 1024 * 1024),  # 256MB
        
        # Compression level for data processing libraries
        "COMPRESSION_LEVEL": "1",  # Faster compression but less effective
    }
    
    return env_vars

def setup_tmpfs(memory_limit: Optional[str] = None) -> Dict[str, str]:
    """Set up tmpfs for temporary files.
    
    Args:
        memory_limit: Memory limit string (e.g., "16g")
        
    Returns:
        Dictionary of environment variables
    """
    logger.info("Setting up tmpfs for temporary files...")
    
    env_vars = {}
    
    if memory_limit is None:
        memory_limit = calculate_optimal_memory()
    
    # Convert memory limit to MB
    if memory_limit.endswith('g'):
        memory_mb = int(float(memory_limit[:-1]) * 1024)
    elif memory_limit.endswith('m'):
        memory_mb = int(float(memory_limit[:-1]))
    else:
        memory_mb = int(float(memory_limit) * 1024)
    
    # Use 1/4 of available memory for tmpfs, but ensure it's at least 1GB
    tmpfs_size = max(1024, memory_mb // 4)
    
    if platform.system() == "Linux" and tmpfs_size > 1024:
        # Create research tmp directory
        tmp_dir = "/tmp/research"
        
        try:
            os.makedirs(tmp_dir, exist_ok=True)
            
            # Try to mount tmpfs
            try:
                subprocess.run(
                    ["mount", "-t", "tmpfs", "-o", f"size={tmpfs_size}m", "tmpfs", tmp_dir],
                    check=True
                )
                logger.info(f"Mounted tmpfs at {tmp_dir} with size {tmpfs_size}MB")
                
                # Set up cache directories
                os.makedirs(f"{tmp_dir}/torch_cache", exist_ok=True)
                os.makedirs(f"{tmp_dir}/huggingface", exist_ok=True)
                os.makedirs(f"{tmp_dir}/tensorflow", exist_ok=True)
                
                # Set environment variables for cache locations
                env_vars["TMPDIR"] = tmp_dir
                env_vars["TORCH_HOME"] = f"{tmp_dir}/torch_cache"
                env_vars["TRANSFORMERS_CACHE"] = f"{tmp_dir}/huggingface"
                env_vars["HF_HOME"] = f"{tmp_dir}/huggingface"
                env_vars["TENSORFLOW_CACHE"] = f"{tmp_dir}/tensorflow"
            except subprocess.CalledProcessError:
                logger.warning(f"Failed to mount tmpfs at {tmp_dir}. Using default tmp directory.")
        except Exception as e:
            logger.warning(f"Failed to set up tmpfs: {e}")
    
    return env_vars

def setup_monitoring(enable_monitoring: bool = False) -> Dict[str, str]:
    """Configure monitoring settings.
    
    Args:
        enable_monitoring: Whether to enable monitoring
        
    Returns:
        Dictionary of environment variables
    """
    logger.info(f"Setting up monitoring (enabled: {enable_monitoring})...")
    
    if not enable_monitoring:
        return {
            "ENABLE_MONITORING": "false",
            "LOG_MEMORY": "false"
        }
    
    env_vars = {
        "ENABLE_MONITORING": "true",
        "LOG_MEMORY": "true",
        
        # Enable PyTorch profiling
        "PYTORCH_PROFILER_ENABLE": "1",
        
        # Setup TensorFlow profiling
        "TF_PROFILER_ENABLED": "1",
    }
    
    return env_vars

def apply_system_optimizations() -> None:
    """Apply system-level optimizations if possible."""
    logger.info("Applying system-level optimizations...")
    
    # Only run on Linux
    if platform.system() != 'Linux':
        logger.info("System optimizations only available on Linux")
        return
    
    # Check if running as root
    try:
        is_root = os.geteuid() == 0
    except AttributeError:
        is_root = False
    
    if not is_root:
        logger.info("System optimizations require root privileges")
        return
    
    try:
        # Set swappiness to reduce swap usage
        subprocess.run(["sysctl", "-w", "vm.swappiness=10"], check=False)
        logger.info("Set vm.swappiness=10")
        
        # Drop caches
        subprocess.run(["sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"], check=False)
        logger.info("Dropped filesystem caches")
        
        # Set I/O scheduler to deadline for better throughput
        for device_path in Path("/sys/block").glob("sd*"):
            scheduler_path = device_path / "queue" / "scheduler"
            
            if scheduler_path.exists():
                try:
                    with open(scheduler_path, 'w') as f:
                        f.write("deadline")
                    logger.info(f"Set I/O scheduler to deadline for {device_path.name}")
                except Exception as e:
                    logger.warning(f"Failed to set I/O scheduler for {device_path.name}: {e}")
            
            # Set readahead buffer
            readahead_path = device_path / "queue" / "read_ahead_kb"
            if readahead_path.exists():
                try:
                    with open(readahead_path, 'w') as f:
                        f.write("4096")
                    logger.info(f"Set read_ahead_kb=4096 for {device_path.name}")
                except Exception as e:
                    logger.warning(f"Failed to set read_ahead_kb for {device_path.name}: {e}")
        
        # Disable transparent hugepages for better memory management
        if os.path.exists('/sys/kernel/mm/transparent_hugepage/enabled'):
            try:
                with open('/sys/kernel/mm/transparent_hugepage/enabled', 'w') as f:
                    f.write('never')
                logger.info("Disabled transparent hugepages")
            except Exception as e:
                logger.warning(f"Failed to disable transparent hugepages: {e}")
    
    except Exception as e:
        logger.warning(f"Error applying system optimizations: {e}")

# ==========================================
# Framework Initialization
# ==========================================

def initialize_frameworks(container_id: str = 'unknown') -> bool:
    """Initialize AI frameworks.
    
    Args:
        container_id: Container identifier
        
    Returns:
        True if successful, False otherwise
    """
    logger.info("Initializing AI frameworks...")
    
    # Get environment variables
    enable_self_awareness = os.environ.get('ENABLE_SELF_AWARENESS', 'true').lower() == 'true'
    enable_emotional_framework = os.environ.get('ENABLE_EMOTIONAL_FRAMEWORK', 'true').lower() == 'true'
    
    success = True
    
    # Initialize Self-Awareness Framework
    if enable_self_awareness:
        success = success and initialize_self_awareness_framework(container_id)
    
    # Initialize Emotional Dimensionality Framework
    if enable_emotional_framework:
        success = success and initialize_emotional_framework(container_id)
    
    return success

def initialize_self_awareness_framework(container_id: str = 'unknown') -> bool:
    """Initialize the Self-Awareness Framework.
    
    Args:
        container_id: Container identifier
        
    Returns:
        True if successful, False otherwise
    """
    logger.info("Initializing Self-Awareness Framework...")
    
    try:
        # Import the framework
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from frameworks.self_awareness.self_awareness import SelfAwarenessFramework
        
        # Get configuration
        config = {
            'id': f'self-aware-{container_id}',
            'monitoring_rate': 1.0,
            'safety_bounds': {
                'max_memory_percent': 90,
                'max_cpu_percent': 95
            }
        }
        
        # Initialize the framework
        framework = SelfAwarenessFramework(config)
        
        # Start the framework
        framework.start()
        
        logger.info('Self-Awareness Framework initialized and running')
        return True
    except Exception as e:
        logger.error(f'Error initializing Self-Awareness Framework: {e}')
        return False

def initialize_emotional_framework(container_id: str = 'unknown') -> bool:
    """Initialize the Emotional Dimensionality Framework.
    
    Args:
        container_id: Container identifier
        
    Returns:
        True if successful, False otherwise
    """
    logger.info("Initializing Emotional Dimensionality Framework...")
    
    try:
        # Import the framework
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from frameworks.emotional_dimensionality.emotional_dimensionality import EmotionalDimensionalityFramework, RuleBasedEDFModel
        
        # Get configuration
        config = {
            'id': f'edf-{container_id}'
        }
        
        # Initialize the framework
        framework = EmotionalDimensionalityFramework(config)
        
        # Add rule-based model
        framework.add_model('rule_based', RuleBasedEDFModel())
        
        logger.info('Emotional Dimensionality Framework initialized')
        return True
    except Exception as e:
        logger.error(f'Error initializing Emotional Dimensionality Framework: {e}')
        return False

# ==========================================
# Main Functions
# ==========================================

def get_environment_variables(args: Optional[Dict] = None) -> Dict[str, str]:
    """Get all environment variables based on configuration.
    
    Args:
        args: Dictionary of configuration arguments
        
    Returns:
        Dictionary of environment variables
    """
    if args is None:
        args = {}
    
    all_vars = {}
    
    # Add memory optimization variables
    all_vars.update(optimize_memory_usage(args.get('memory_limit')))
    
    # Add CPU optimization variables
    all_vars.update(optimize_cpu_usage(args.get('num_threads')))
    
    # Add GPU optimization variables if not disabled
    if not args.get('disable_gpu'):
        all_vars.update(optimize_gpu_usage())
    
    # Add I/O optimization variables
    all_vars.update(optimize_io_performance())
    
    # Add monitoring variables
    all_vars.update(setup_monitoring(args.get('enable_monitoring', False)))
    
    # Add tmpfs configuration if available
    all_vars.update(setup_tmpfs(args.get('memory_limit')))
    
    # Add framework initialization variables
    all_vars.update({
        "ENABLE_SELF_AWARENESS": str(args.get('enable_self_awareness', True)).lower(),
        "ENABLE_EMOTIONAL_FRAMEWORK": str(args.get('enable_emotional_framework', True)).lower(),
        "CONTAINER_ID": args.get('container_id', 'unknown')
    })
    
    return all_vars

def print_environment_summary(env_vars: Dict[str, str]) -> None:
    """Print a summary of the environment configuration.
    
    Args:
        env_vars: Dictionary of environment variables
    """
    print("============================================")
    print("AI Research Environment Configuration:")
    print(f"  - Hostname: {platform.node()}")
    print(f"  - Python: {platform.python_version()}")
    
    # GPU information
    gpu_enabled = env_vars.get("ENABLE_GPU", "false").lower() == "true"
    if gpu_enabled:
        gpus = get_gpu_info()
        if gpus:
            print(f"  - GPU: {gpus[0]['name']}")
            print(f"  - GPU Memory: {gpus[0]['memory_total_mb']}MB")
        else:
            print("  - GPU: Enabled but no details available")
    else:
        print("  - GPU: Not available or disabled")
    
    # CPU and memory information
    cpu_threads = env_vars.get("OMP_NUM_THREADS", "Unknown")
    memory_limit = env_vars.get("MEMORY_LIMIT", "Unknown")
    print(f"  - CPUs: {cpu_threads}")
    print(f"  - Memory Limit: {memory_limit}")
    
    # Framework information
    enable_self_awareness = env_vars.get("ENABLE_SELF_AWARENESS", "false").lower() == "true"
    enable_emotional = env_vars.get("ENABLE_EMOTIONAL_FRAMEWORK", "false").lower() == "true"
    print(f"  - Self-Awareness Framework: {'Enabled' if enable_self_awareness else 'Disabled'}")
    print(f"  - Emotional Dimensionality Framework: {'Enabled' if enable_emotional else 'Disabled'}")
    
    # Monitoring
    enable_monitoring = env_vars.get("ENABLE_MONITORING", "false").lower() == "true"
    print(f"  - Monitoring: {'Enabled' if enable_monitoring else 'Disabled'}")
    print("============================================")

def optimize_runtime(memory_limit: Optional[str] = None, 
                    num_threads: Optional[int] = None,
                    container_id: str = 'unknown',
                    enable_monitoring: bool = False,
                    disable_gpu: bool = False,
                    enable_self_awareness: bool = True,
                    enable_emotional_framework: bool = True) -> Dict[str, str]:
    """Main function to optimize the runtime environment.
    
    Args:
        memory_limit: Memory limit string (e.g., "16g")
        num_threads: Number of threads to use
        container_id: Container identifier
        enable_monitoring: Whether to enable monitoring
        disable_gpu: Whether to disable GPU support
        enable_self_awareness: Whether to enable Self-Awareness Framework
        enable_emotional_framework: Whether to enable Emotional Dimensionality Framework
        
    Returns:
        Dictionary of environment variables
    """
    # Create configuration dictionary
    config = {
        'memory_limit': memory_limit,
        'num_threads': num_threads,
        'container_id': container_id,
        'enable_monitoring': enable_monitoring,
        'disable_gpu': disable_gpu,
        'enable_self_awareness': enable_self_awareness,
        'enable_emotional_framework': enable_emotional_framework
    }
    
    # Get all environment variables
    env_vars = get_environment_variables(config)
    
    # Apply system optimizations (if possible)
    apply_system_optimizations()
    
    # Initialize frameworks
    initialize_frameworks(container_id)
    
    # Print environment summary
    print_environment_summary(env_vars)
    
    return env_vars

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Optimize runtime environment')
    parser.add_argument('--memory', '-m', help='Memory limit (e.g., "16g")')
    parser.add_argument('--threads', '-t', type=int, help='Number of threads to use')
    parser.add_argument('--container-id', '-i', default='unknown', help='Container identifier')
    parser.add_argument('--monitoring', action='store_true', help='Enable monitoring')
    parser.add_argument('--no-gpu', action='store_true', help='Disable GPU support')
    parser.add_argument('--no-self-awareness', action='store_true', help='Disable Self-Awareness Framework')
    parser.add_argument('--no-emotional-framework', action='store_true', help='Disable Emotional Dimensionality Framework')
    
    return parser.parse_args()

def main():
    """Main entry point for the runtime optimizer."""
    args = parse_arguments()
    
    # Run the optimizer
    env_vars = optimize_runtime(
        memory_limit=args.memory,
        num_threads=args.threads,
        container_id=args.container_id,
        enable_monitoring=args.monitoring,
        disable_gpu=args.no_gpu,
        enable_self_awareness=not args.no_self_awareness,
        enable_emotional_framework=not args.no_emotional_framework
    )
    
    # Print environment variables for shell integration
    if platform.system() != 'Windows':
        print("\n# Add these to your shell environment:")
        for key, value in env_vars.items():
            print(f"export {key}=\"{value}\"")
    else:
        print("\n# Add these to your Windows environment:")
        for key, value in env_vars.items():
            print(f"SET {key}={value}")

if __name__ == "__main__":
    main()
