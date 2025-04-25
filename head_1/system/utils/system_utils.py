#!/usr/bin/env python3
"""
System Utilities for AI Research Environment

This module provides system resource management, optimization, 
diagnostics, temporal awareness, and social awareness for 
machine learning research environments.
"""

import logging
import os
import platform
import time
from datetime import datetime, timedelta
import psutil
import subprocess
from collections import deque
import json
from typing import Dict, List, Optional, Tuple, Union

# Configure logging
logger = logging.getLogger('environment.system')

class SystemManager:
    """Comprehensive system resource management for ML research environments."""

    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the system manager with optional configuration."""
        self.config = config or {}
        self.memory_fraction = self.config.get('memory_fraction', 0.8)  # Default to 80% of available memory
        
    def get_system_memory(self) -> int:
        """Get total system memory in MiB."""
        return psutil.virtual_memory().total // (1024 * 1024)
    
    def get_available_memory(self) -> int:
        """Get available system memory in MiB."""
        return psutil.virtual_memory().available // (1024 * 1024)
    
    def get_container_memory_limit(self) -> Optional[int]:
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
    
    def get_cpu_info(self) -> Dict:
        """Get detailed CPU information."""
        info = {
            'count_logical': psutil.cpu_count(logical=True),
            'count_physical': psutil.cpu_count(logical=False),
            'current_freq': None,
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'utilization': psutil.cpu_percent(interval=0.1)
        }
        
        # Try to get CPU frequency (not available on all platforms)
        try:
            freq = psutil.cpu_freq()
            if freq:
                info['current_freq'] = freq.current
                info['min_freq'] = freq.min
                info['max_freq'] = freq.max
        except (AttributeError, NotImplementedError):
            pass
            
        return info
    
    def check_container_environment(self) -> Dict:
        """Check if we're running in a container and get details."""
        container_info = {
            'is_container': False,
            'type': None,
            'runtime': None
        }
        
        # Check common container indicators
        if os.path.exists('/.dockerenv'):
            container_info['is_container'] = True
            container_info['type'] = 'docker'
        elif os.path.exists('/run/.containerenv'):
            container_info['is_container'] = True
            container_info['type'] = 'podman'
        
        # Check cgroup for container information
        try:
            with open('/proc/self/cgroup', 'r') as f:
                content = f.read()
                if 'docker' in content:
                    container_info['is_container'] = True
                    container_info['type'] = 'docker'
                elif 'kubepods' in content:
                    container_info['is_container'] = True
                    container_info['type'] = 'kubernetes'
        except (IOError, ValueError):
            pass
        
        return container_info
    
    def calculate_optimal_memory(self) -> str:
        """
        Calculate optimal memory setting based on system resources.
        Returns a string like '16g' or '8g' suitable for Docker limits.
        """
        # First check if we're in a container with limits
        container_limit = self.get_container_memory_limit()
        if container_limit:
            memory_mib = container_limit
            logger.debug(f"Running in container with {memory_mib}MiB limit")
        else:
            # Use system memory with a safety margin
            system_memory = self.get_system_memory()
            memory_mib = int(system_memory * self.memory_fraction)
            logger.debug(f"System memory: {system_memory}MiB, allocating {memory_mib}MiB")
        
        # Convert to a human-readable format for Docker
        if memory_mib >= 1024:
            return f"{memory_mib // 1024}g"
        else:
            return f"{memory_mib}m"
    
    def calculate_optimal_cpu(self) -> int:
        """
        Calculate optimal CPU count based on system resources.
        Returns number of CPU cores to use.
        """
        cpu_count = psutil.cpu_count(logical=True)
        
        # Leave at least one core for system operations
        optimal_cpus = max(1, cpu_count - 1)
        
        # If we have many cores, use a percentage instead
        if cpu_count > 8:
            optimal_cpus = max(4, int(cpu_count * 0.75))
            
        return optimal_cpus
    
    def get_memory_optimization_settings(self) -> Dict[str, str]:
        """
        Get recommended memory optimization settings based on system capability.
        Returns a dictionary of environment variables and their values.
        """
        settings = {}
        
        # Get available memory
        memory_mib = self.get_container_memory_limit() or (self.get_system_memory() * self.memory_fraction)
        
        # TensorFlow memory settings
        settings['TF_MEMORY_ALLOCATION_FRACTION'] = '0.8'  # Use 80% of GPU memory
        settings['TF_GPU_MEMORY_ALLOCATION'] = 'growth'    # Grow memory as needed
        
        # PyTorch memory settings
        settings['PYTORCH_CUDA_ALLOC_CONF'] = f'max_split_size_mb:{min(512, int(memory_mib * 0.1))}'
        
        # Numpy settings
        settings['NPY_MMAP_MAX_LEN'] = str(memory_mib * 1024 * 1024)  # Maximum memory mapping size
        
        # JVM settings (for libraries like PySpark)
        jvm_heap = min(int(memory_mib * 0.6), 31 * 1024)  # 60% of memory or max 31GB
        settings['JAVA_OPTS'] = f"-Xms1g -Xmx{jvm_heap}m"
        
        # Thread settings
        cpu_count = self.calculate_optimal_cpu()
        settings['OMP_NUM_THREADS'] = str(cpu_count)
        settings['NUMEXPR_NUM_THREADS'] = str(cpu_count)
        settings['MKL_NUM_THREADS'] = str(cpu_count)
        
        return settings
    
    def apply_system_optimizations(self):
        """Apply system-level optimizations if possible."""
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
    
    def get_disk_info(self) -> Dict:
        """Get information about disk usage."""
        disk_info = {}
        
        try:
            # Get mount points
            partitions = psutil.disk_partitions(all=False)
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.mountpoint] = {
                        'total_gb': usage.total / (1024**3),
                        'used_gb': usage.used / (1024**3),
                        'free_gb': usage.free / (1024**3),
                        'percent_used': usage.percent,
                        'filesystem': partition.fstype
                    }
                except (PermissionError, OSError):
                    # Skip partitions we can't access
                    continue
                    
        except Exception as e:
            logger.warning(f"Error getting disk info: {e}")
        
        return disk_info
    
    def get_system_summary(self) -> Dict:
        """Get comprehensive system information summary."""
        summary = {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'hostname': platform.node(),
            'cpu': self.get_cpu_info(),
            'memory': {
                'total_mib': self.get_system_memory(),
                'available_mib': self.get_available_memory(),
                'percent_used': psutil.virtual_memory().percent,
            },
            'disk': self.get_disk_info(),
            'container': self.check_container_environment(),
        }
        
        # Add container memory limit if applicable
        container_memory = self.get_container_memory_limit()
        if container_memory:
            summary['memory']['container_limit_mib'] = container_memory
        
        # Add load averages on Unix systems
        if hasattr(os, 'getloadavg'):
            try:
                summary['load_avg'] = os.getloadavg()
            except (AttributeError, OSError):
                pass
        
        return summary
    
    def get_docker_resource_flags(self) -> List[str]:
        """Generate appropriate Docker resource limit flags."""
        flags = []
        
        # Memory limits
        memory = self.calculate_optimal_memory()
        flags.extend(["--memory", memory])
        
        # CPU limits
        cpus = self.calculate_optimal_cpu()
        flags.extend(["--cpus", str(cpus)])
        
        return flags
    
    def get_environment_variables(self) -> Dict[str, str]:
        """Get optimal environment variables for the research environment."""
        env_vars = {}
        
        # Add memory optimization settings
        env_vars.update(self.get_memory_optimization_settings())
        
        # Add container-specific settings
        if self.check_container_environment()['is_container']:
            # These are only relevant inside a container
            env_vars['PYTHONUNBUFFERED'] = '1'
            env_vars['DEBIAN_FRONTEND'] = 'noninteractive'
        
        return env_vars


    def get_current_time(self) -> datetime:
        """
        Get the current time with microsecond precision.
        
        Returns:
            datetime: The current time.
        """
        return datetime.now()

    def calculate_time_difference(self, start_time: datetime, end_time: datetime) -> timedelta:
        """
        Calculate the time difference between two datetime objects.

        Args:
            start_time (datetime): The start time.
            end_time (datetime): The end time.

        Returns:
            timedelta: The difference between the two times.
        """
        return end_time - start_time

    def predict_future_time(self, current_time: datetime, duration: timedelta) -> datetime:
        """
        Predict the time that will occur after a specified duration from the current time.

        Args:
            current_time (datetime): The current time.
            duration (timedelta): The duration to add to the current time.

        Returns:
            datetime: The predicted future time.
        """
        return current_time + duration

    def is_past_event(self, event_time: datetime) -> bool:
        """
        Determine if an event has occurred in the past.

        Args:
            event_time (datetime): The time of the event.

        Returns:
            bool: True if the event is in the past, False otherwise.
        """
        return event_time < self.get_current_time()

class SocialAwarenessManager:
    """
    Manages interactions with other agents and maintains a history of those interactions.
    """
    def __init__(self, max_history_length: int = 100):
        """
        Initializes the SocialAwarenessManager with an empty interaction history.

        Args:
            max_history_length (int): The maximum number of interactions to keep in the history.
        """
        self.interaction_history = deque(maxlen=max_history_length)

    def log_interaction(self, agent_id: str, interaction_type: str, details: Dict = None):
        """
        Logs an interaction with another agent.

        Args:
            agent_id (str): The ID of the agent interacted with.
            interaction_type (str): The type of interaction (e.g., "request", "response", "communication").
            details (Dict): Optional additional details about the interaction.
        """
        timestamp = datetime.now().isoformat()
        interaction = {"timestamp": timestamp, "agent_id": agent_id, "type": interaction_type, "details": details}
        self.interaction_history.append(interaction)
        logger.info(f"Logged interaction: {interaction}")

    def get_interaction_history(self) -> List[Dict]:
        return list(self.interaction_history)


# Create a singleton instance for easy import
system_manager = SystemManager()


def calculate_optimal_memory() -> str:
    """Get optimal memory setting (for backward compatibility)."""
    return system_manager.calculate_optimal_memory()


def get_system_summary() -> Dict:
    """Get system information summary (for backward compatibility)."""
    return system_manager.get_system_summary()


# Create a singleton instance for easy import of Social Awareness.
social_awareness_manager = SocialAwarenessManager()


if __name__ == "__main__":
    # Configure logging for CLI usage
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create manager and print system information
    manager = SystemManager()
    summary = manager.get_system_summary()
    
    print("AI Research Environment - System Information")
    print("============================================")
    
    print(f"\nPlatform: {summary['platform']}")
    print(f"Python: {summary['python_version']}")
    print(f"Hostname: {summary['hostname']}")
    
    print("\nCPU Information:")
    print(f"  {summary['cpu']['count_physical']} physical cores, {summary['cpu']['count_logical']} logical cores")
    if summary['cpu'].get('current_freq'):
        print(f"  Current frequency: {summary['cpu']['current_freq']} MHz")
    print(f"  Current utilization: {summary['cpu']['utilization']}%")
    
    print("\nMemory Information:")
    print(f"  Total: {summary['memory']['total_mib']} MiB")
    print(f"  Available: {summary['memory']['available_mib']} MiB")
    print(f"  Used: {summary['memory']['percent_used']}%")
    if summary['memory'].get('container_limit_mib'):
        print(f"  Container limit: {summary['memory']['container_limit_mib']} MiB")
    
    print("\nDisk Information:")
    for mount, disk in summary['disk'].items():
        print(f"  {mount}:")
        print(f"    {disk['total_gb']:.1f} GB total, {disk['free_gb']:.1f} GB free ({disk['percent_used']}% used)")
    
    print("\nContainer Environment:")
    if summary['container']['is_container']:
        print(f"  Running in a {summary['container']['type']} container")
    else:
        print("  Not running in a container")
    
    print("\nRecommended Settings:")
    print(f"  Memory: {manager.calculate_optimal_memory()}")
    print(f"  CPUs: {manager.calculate_optimal_cpu()}")
    
    print("\nRecommended Docker Resource Flags:")
    print("  " + " ".join(manager.get_docker_resource_flags()))
    
    print("\nRecommended Environment Variables:")
    env_vars = manager.get_environment_variables()
    for key, value in env_vars.items():
        print(f"  {key}={value}")

    # Temporal Awareness example
    print("\nTemporal Awareness Example:")
    current_time = manager.get_current_time()
    print(f"  Current time: {current_time}")

    future_time = manager.predict_future_time(current_time, timedelta(days=7))
    print(f"  Predicted time 7 days from now: {future_time}")

    past_event = manager.is_past_event(current_time - timedelta(days=3))
    print(f"  Was an event 3 days ago in the past? {past_event}")

    future_event = manager.is_past_event(future_time)
    print(f"  Will an event 7 days from now be in the past? {future_event}")

    # Social Awareness example
    print("\nSocial Awareness Example:")

    social_awareness_manager.log_interaction(agent_id="AgentA", interaction_type="request", details={"action": "process data"})
    social_awareness_manager.log_interaction(agent_id="AgentB", interaction_type="response", details={"status": "completed", "duration": "5 seconds"})
    social_awareness_manager.log_interaction(agent_id="AgentA", interaction_type="communication", details={"message": "Thank you!"})
    social_awareness_manager.log_interaction(agent_id="AgentC", interaction_type="request", details={"action": "process data"})
    social_awareness_manager.log_interaction(agent_id="AgentC", interaction_type="response", details={"status": "completed", "duration": "3 seconds"})

    print("\nInteraction History:")
    for interaction in social_awareness_manager.get_interaction_history():
        print(f"  {interaction}")

    