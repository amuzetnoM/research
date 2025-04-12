#!/usr/bin/env python3
"""
GPU Utility Module for AI Research Environment

This module provides comprehensive GPU detection, monitoring, and optimization
functions for machine learning research environments.
"""

import json
import logging
import os
import subprocess
import platform
from typing import Dict, List, Optional, Tuple, Union

# Configure logging
logger = logging.getLogger('environment.gpu')

class GPUManager:
    """A comprehensive GPU management class for ML research environments."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the GPU manager with optional configuration."""
        self.config = config or {}
        self.memory_headroom = self.config.get('memory_headroom', 0.2)  # 20% headroom by default
        
    def check_nvidia_smi(self) -> bool:
        """Check if nvidia-smi is available."""
        try:
            subprocess.run(
                ["nvidia-smi"], 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def check_tensorflow_gpu(self) -> bool:
        """Check if TensorFlow can access GPU."""
        try:
            import tensorflow as tf
            gpus = tf.config.list_physical_devices('GPU')
            return len(gpus) > 0
        except (ImportError, ModuleNotFoundError):
            logger.debug("TensorFlow not installed, skipping TensorFlow GPU check")
            return False
        except Exception as e:
            logger.debug(f"Error checking TensorFlow GPU: {e}")
            return False
    
    def check_pytorch_gpu(self) -> bool:
        """Check if PyTorch can access GPU."""
        try:
            import torch
            return torch.cuda.is_available()
        except (ImportError, ModuleNotFoundError):
            logger.debug("PyTorch not installed, skipping PyTorch GPU check")
            return False
        except Exception as e:
            logger.debug(f"Error checking PyTorch GPU: {e}")
            return False
    
    def get_gpu_info(self) -> List[Dict]:
        """Get detailed information about available GPUs using nvidia-smi."""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,memory.free,memory.used,temperature.gpu,utilization.gpu,compute_mode", 
                 "--format=csv,noheader,nounits"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            gpus = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(', ')
                    if len(parts) >= 6:
                        name, total, free, used, temp, util = parts[:6]
                        compute_mode = parts[6] if len(parts) > 6 else "Unknown"
                        
                        gpus.append({
                            'name': name,
                            'memory_total_mb': float(total),
                            'memory_free_mb': float(free),
                            'memory_used_mb': float(used),
                            'temperature_c': float(temp),
                            'utilization_pct': float(util),
                            'compute_mode': compute_mode
                        })
            return gpus
        except (subprocess.SubprocessError, FileNotFoundError):
            return []
    
    def check_docker_gpu_support(self) -> bool:
        """Check if Docker has GPU support configured."""
        try:
            docker_info = json.loads(subprocess.run(
                ["docker", "info", "--format", "{{json .}}"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            ).stdout)
            
            # Check for nvidia runtime in Docker
            runtimes = docker_info.get('Runtimes', {})
            if 'nvidia' in runtimes:
                return True
            
            # Check for GPU capabilities in newer Docker versions
            for plugin in docker_info.get('Plugins', {}).get('Runtime', []):
                if 'nvidia' in plugin.lower():
                    return True
                    
            logger.warning("NVIDIA Docker runtime not found. GPU support may not work correctly.")
            return False
            
        except (subprocess.SubprocessError, json.JSONDecodeError):
            logger.warning("Could not check Docker GPU support. Continuing anyway.")
            return False
    
    def check_gpu_availability(self) -> bool:
        """
        Check if GPUs are available and configured correctly for the research environment.
        Returns True if GPUs are available, False otherwise.
        """
        # Check if CUDA is disabled by environment
        if os.environ.get('DISABLE_CUDA', '').lower() in ('1', 'true', 'yes'):
            logger.info("CUDA disabled by environment variable")
            return False
        
        # Check for nvidia-smi
        if not self.check_nvidia_smi():
            logger.info("nvidia-smi not found, checking ML frameworks directly")
            # Try checking via ML frameworks
            ml_gpu = self.check_tensorflow_gpu() or self.check_pytorch_gpu()
            if ml_gpu:
                logger.info("GPU detected through ML framework")
                return True
            else:
                logger.info("No GPU available through any detection method")
                return False
        
        # Get GPU info
        gpus = self.get_gpu_info()
        if not gpus:
            logger.info("No GPUs detected")
            return False
        
        # Log available GPUs
        logger.info(f"Found {len(gpus)} GPU(s):")
        for idx, gpu in enumerate(gpus):
            logger.info(f"  GPU {idx}: {gpu['name']} - {gpu['memory_total_mb']}MB total, "
                       f"{gpu['memory_free_mb']}MB free, {gpu['utilization_pct']}% utilization")
        
        return True
    
    def get_optimal_gpu_settings(self) -> Dict[str, str]:
        """
        Determine optimal settings for GPU usage based on available hardware.
        Returns a dictionary of suggested environment variables and settings.
        """
        settings = {}
        
        if not self.check_gpu_availability():
            logger.info("No GPU available, skipping GPU optimization")
            return settings
        
        gpus = self.get_gpu_info()
        if not gpus:
            return settings
        
        # Calculate total GPU memory across all cards
        total_memory = sum(gpu['memory_total_mb'] for gpu in gpus)
        free_memory = sum(gpu['memory_free_mb'] for gpu in gpus)
        
        # Calculate memory fraction to use (leaving some headroom)
        memory_fraction = max(0.1, min(0.8, (free_memory / total_memory) * (1 - self.memory_headroom)))
        
        # TensorFlow settings
        settings['TF_MEMORY_ALLOCATION'] = str(memory_fraction)
        settings['TF_GPU_THREAD_COUNT'] = str(min(4, len(gpus) * 2))
        settings['TF_ENABLE_ONEDNN_OPTS'] = '1'
        
        # PyTorch settings
        settings['PYTORCH_CUDA_ALLOC_CONF'] = f"max_split_size_mb:{int(free_memory/len(gpus)*0.8)}"
        
        # General parallel processing settings
        settings['OMP_NUM_THREADS'] = str(min(8, len(gpus) * 4))
        
        return settings
    
    def get_docker_gpu_flags(self) -> List[str]:
        """Generate appropriate Docker flags for GPU support."""
        if not self.check_gpu_availability():
            return []
            
        # Check which GPU runtime syntax to use
        try:
            docker_version = subprocess.run(
                ["docker", "version", "--format", "{{.Server.Version}}"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            ).stdout.strip()
            
            # Parse version
            version_parts = [int(part) for part in docker_version.split('.')]
            major, minor = version_parts[0], version_parts[1]
            
            # Docker 19.03+ uses --gpus flag
            if major > 19 or (major == 19 and minor >= 3):
                return ["--gpus", "all"]
            # Older versions use --runtime=nvidia
            else:
                return ["--runtime=nvidia"]
                
        except (subprocess.SubprocessError, ValueError):
            # Fall back to newer syntax if version check fails
            return ["--gpus", "all"]


# Create a singleton instance for easy import
gpu_manager = GPUManager()


def is_gpu_available() -> bool:
    """Simple function to check if GPU is available (for backward compatibility)."""
    return gpu_manager.check_gpu_availability()


def get_gpu_settings() -> Dict[str, str]:
    """Get optimal GPU settings (for backward compatibility)."""
    return gpu_manager.get_optimal_gpu_settings()


if __name__ == "__main__":
    # Configure logging for CLI usage
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Check GPU availability
    manager = GPUManager()
    available = manager.check_gpu_availability()
    print(f"GPU Available: {available}")
    
    if available:
        # Get and display recommended settings
        settings = manager.get_optimal_gpu_settings()
        print("\nRecommended GPU settings:")
        for key, value in settings.items():
            print(f"  {key}={value}")
        
        # Check for Docker integration
        docker_support = manager.check_docker_gpu_support()
        print(f"\nDocker GPU support: {'Available' if docker_support else 'Not available'}")
        if docker_support:
            docker_flags = manager.get_docker_gpu_flags()
            if docker_flags:
                print(f"Recommended Docker GPU flags: {' '.join(docker_flags)}")
    
    # Return exit code for shell integration
    # (0 for GPU available, 1 for no GPU)
    exit(0 if available else 1)