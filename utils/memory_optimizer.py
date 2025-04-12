"""
Memory optimization utilities for the AI Research Environment.
"""

import os
import platform
import logging
import subprocess
import psutil
from typing import Dict, Optional

logger = logging.getLogger('environment.memory')

def get_system_memory() -> int:
    """Get total system memory in MiB."""
    return psutil.virtual_memory().total // (1024 * 1024)

def get_container_memory_limit() -> Optional[int]:
    """
    Get container memory limit in MiB if running in a container.
    Returns None if not in a container or unable to determine.
    """
    # Check cgroup v2
    cgroup_file = '/sys/fs/cgroup/memory.max'
    if os.path.exists(cgroup_file):
        try:
            with open(cgroup_file, 'r') as f:
                content = f.read().strip()
                if content != 'max':
                    return int(content) // (1024 * 1024)
        except (IOError, ValueError):
            pass
    
    # Check cgroup v1
    cgroup_file = '/sys/fs/cgroup/memory/memory.limit_in_bytes'
    if os.path.exists(cgroup_file):
        try:
            with open(cgroup_file, 'r') as f:
                content = f.read().strip()
                mem_limit = int(content)
                # Check if it's set to maximum (usually a very large value)
                if mem_limit < 2**63 - 1:
                    return mem_limit // (1024 * 1024)
        except (IOError, ValueError):
            pass
    
    return None

def calculate_optimal_memory() -> str:
    """
    Calculate optimal memory setting based on system resources.
    Returns a string like '16g' or '8g' suitable for Docker limits.
    """
    # First check if we're in a container with limits
    container_limit = get_container_memory_limit()
    if container_limit:
        memory_mib = container_limit
        logger.debug(f"Running in container with {memory_mib}MiB limit")
    else:
        # Use system memory with a safety margin
        system_memory = get_system_memory()
        memory_mib = int(system_memory * 0.8)  # Use 80% of available memory
        logger.debug(f"System memory: {system_memory}MiB, using {memory_mib}MiB")
    
    # Convert to a human-readable format for Docker
    if memory_mib >= 1024:
        return f"{memory_mib // 1024}g"
    else:
        return f"{memory_mib}m"

def get_memory_optimization_settings() -> Dict[str, str]:
    """
    Get recommended memory optimization settings based on system capability.
    Returns a dictionary of environment variables and their values.
    """
    settings = {}
    
    # Get available memory
    memory_mib = get_container_memory_limit() or (get_system_memory() * 0.8)
    
    # TensorFlow memory settings
    settings['TF_MEMORY_ALLOCATION_FRACTION'] = '0.8'  # Use 80% of GPU memory
    settings['TF_GPU_MEMORY_ALLOCATION'] = 'growth'    # Grow memory as needed
    
    # PyTorch memory settings
    settings['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
    
    # Numpy settings
    settings['NPY_MMAP_MAX_LEN'] = str(memory_mib * 1024 * 1024)  # Maximum memory mapping size
    
    # JVM settings (for libraries like PySpark)
    jvm_heap = min(int(memory_mib * 0.6), 31 * 1024)  # 60% of memory or max 31GB
    settings['JAVA_OPTS'] = f"-Xms1g -Xmx{jvm_heap}m"
    
    # Thread settings
    cpu_count = os.cpu_count() or 4
    settings['OMP_NUM_THREADS'] = str(max(1, cpu_count - 1))
    settings['NUMEXPR_NUM_THREADS'] = str(max(1, cpu_count - 1))
    settings['MKL_NUM_THREADS'] = str(max(1, cpu_count - 1))
    
    return settings

def apply_system_optimizations():
    """Apply system-level memory optimizations."""
    # Only run on Linux
    if platform.system() != 'Linux':
        return
    
    try:
        # Check if we have permission to modify system settings
        if os.geteuid() == 0:  # Root user
            # Set swappiness to reduce swap usage
            subprocess.run(["sysctl", "-w", "vm.swappiness=10"], check=False)
            
            # Disable transparent hugepages for better memory management
            with open('/sys/kernel/mm/transparent_hugepage/enabled', 'w') as f:
                f.write('never')
    except (AttributeError, subprocess.SubprocessError, IOError):
        # Not on Linux or don't have permission
        pass

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Print memory information
    system_memory = get_system_memory()
    container_limit = get_container_memory_limit()
    optimal_setting = calculate_optimal_memory()
    
    print(f"System memory: {system_memory}MiB")
    print(f"Container limit: {container_limit}MiB" if container_limit else "Not running in a container")
    print(f"Recommended memory setting: {optimal_setting}")
    
    # Print optimization settings
    settings = get_memory_optimization_settings()
    print("\nRecommended memory optimization settings:")
    for key, value in settings.items():
        print(f"  {key}={value}")
