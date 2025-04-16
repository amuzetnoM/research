#!/usr/bin/env python3
"""
Unified Diagnostics and Error Handling Module

This module consolidates all diagnostic and error handling functionality:
- Error classes and exception handling
- System diagnostic utilities
- Error testing framework
- Monitoring utilities
- Recovery mechanisms
"""

import atexit
import json
import logging
import os
import platform
import signal
import sys
import traceback
import time
import random
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'diagnostics.log'), mode='a')
    ]
)
logger = logging.getLogger('diagnostics')

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
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    logger.warning("matplotlib not available, visualization will be disabled")

# ==========================================
# Exception Classes
# ==========================================

class EnvironmentError(Exception):
    """Base class for environment-related errors."""
    pass

class ResourceError(EnvironmentError):
    """Error related to resource limitations."""
    pass

class ConfigurationError(EnvironmentError):
    """Error related to system configuration."""
    pass

class NetworkError(EnvironmentError):
    """Error related to network operations."""
    pass

class DataError(EnvironmentError):
    """Error related to data operations."""
    pass

# ==========================================
# Error Handling Utilities
# ==========================================

def handle_exception(
    message: str, 
    exception: Optional[Exception] = None, 
    exit_code: Optional[int] = None,
    notify: bool = False
) -> None:
    """Handle an exception with detailed logging.
    
    Args:
        message: Error message
        exception: Exception object
        exit_code: Exit code to use if the program should exit
        notify: Whether to send a notification
    """
    # Prepare error details
    error_details = {
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'platform': platform.system(),
        'python_version': platform.python_version(),
    }
    
    if exception:
        error_details['exception'] = {
            'type': type(exception).__name__,
            'message': str(exception),
            'traceback': traceback.format_exc(),
        }
        logger.error(f"{message}: {exception}\n{traceback.format_exc()}")
        
        # Add system information if available
        if HAS_PSUTIL:
            try:
                mem = psutil.virtual_memory()
                error_details['system_state'] = {
                    'memory_percent': mem.percent,
                    'memory_available_mb': mem.available / (1024**2),
                    'cpu_percent': psutil.cpu_percent(interval=0.1),
                }
                logger.error(f"Memory: {mem.percent}% used, {mem.available/(1024**2):.1f}MB available")
                logger.error(f"CPU: {psutil.cpu_percent()}% used")
            except Exception as e:
                logger.error(f"Error collecting system information: {e}")
    else:
        logger.error(message)
    
    # Create error report file
    try:
        error_file = f"logs/error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(error_file, 'w') as f:
            json.dump(error_details, f, indent=2)
        logger.info(f"Error report saved to {error_file}")
    except Exception as e:
        logger.error(f"Failed to save error report: {e}")
    
    # Send notification if requested
    if notify:
        try:
            # Implement notification mechanism (email, Slack, etc.)
            logger.info("Notification would be sent here")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    # Exit if requested
    if exit_code is not None:
        logger.info(f"Exiting with code {exit_code}")
        sys.exit(exit_code)

# Register signal handlers for cleaner shutdown
def register_signal_handlers():
    """Register signal handlers for graceful shutdown."""
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}")
        handle_exception(f"Process interrupted by signal {sig}", exit_code=1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Register exit handler
    atexit.register(lambda: logger.info("Process exiting"))

# Decorator for function retry logic
def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Union[type, Tuple[type, ...]] = Exception
) -> Callable:
    """Retry decorator for functions that might fail temporarily.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for delay
        exceptions: Exception types to catch and retry
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts")
                        raise
                    
                    logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {current_delay:.1f}s...")
                    time.sleep(current_delay)
                    attempt += 1
                    current_delay *= backoff
                    
        return wrapper
    return decorator

# ==========================================
# System Diagnostics Utilities
# ==========================================

def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information.
    
    Returns:
        Dictionary with system information
    """
    info = {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'platform_release': platform.release(),
        'python_version': platform.python_version(),
        'hostname': platform.node(),
        'timestamp': datetime.now().isoformat(),
    }
    
    # Add CPU information
    if HAS_PSUTIL:
        info['cpu'] = {
            'count_physical': psutil.cpu_count(logical=False),
            'count_logical': psutil.cpu_count(logical=True),
            'utilization': psutil.cpu_percent(interval=0.5),
        }
        
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                info['cpu']['current_freq'] = cpu_freq.current
                info['cpu']['min_freq'] = cpu_freq.min
                info['cpu']['max_freq'] = cpu_freq.max
        except Exception:
            pass
        
        # Add memory information
        mem = psutil.virtual_memory()
        info['memory'] = {
            'total_mib': mem.total / (1024**2),
            'available_mib': mem.available / (1024**2),
            'percent_used': mem.percent,
        }
        
        # Add disk information
        disk = psutil.disk_usage('/')
        info['disk'] = {
            'total_gib': disk.total / (1024**3),
            'free_gib': disk.free / (1024**3),
            'percent_used': disk.percent,
        }
    
    # Check for GPU
    info['gpu'] = []
    try:
        # Use nvidia-smi to get GPU information
        import subprocess
        result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.used,memory.total,temperature.gpu', 
                                '--format=csv,noheader,nounits'], 
                               capture_output=True, text=True, check=True)
        
        for line in result.stdout.strip().split('\n'):
            parts = line.split(', ')
            if len(parts) >= 4:
                gpu_info = {
                    'name': parts[0],
                    'memory_used_mb': float(parts[1]),
                    'memory_total_mb': float(parts[2]),
                    'temperature_c': float(parts[3]),
                }
                info['gpu'].append(gpu_info)
    except Exception as e:
        logger.debug(f"Could not get GPU information: {e}")
    
    return info

def run_diagnostics():
    """Run system diagnostics and print a report."""
    logger.info("Running system diagnostics...")
    
    try:
        info = get_system_info()
        
        print("\n========== System Diagnostics Report ==========")
        print(f"Platform: {info['platform']} {info['platform_version']}")
        print(f"Python: {info['python_version']}")
        print(f"Hostname: {info['hostname']}")
        
        if 'cpu' in info:
            print(f"\nCPU: {info['cpu']['count_physical']} physical cores, {info['cpu']['count_logical']} logical cores")
            print(f"CPU Utilization: {info['cpu']['utilization']}%")
            if 'current_freq' in info['cpu']:
                print(f"CPU Frequency: {info['cpu']['current_freq']} MHz")
        
        if 'memory' in info:
            print(f"\nMemory: {info['memory']['total_mib']:.1f} MiB total")
            print(f"Memory Available: {info['memory']['available_mib']:.1f} MiB ({100-info['memory']['percent_used']:.1f}% free)")
        
        if 'disk' in info:
            print(f"\nDisk: {info['disk']['total_gib']:.1f} GiB total")
            print(f"Disk Free: {info['disk']['free_gib']:.1f} GiB ({100-info['disk']['percent_used']:.1f}% free)")
        
        if info['gpu']:
            print("\nGPU Information:")
            for i, gpu in enumerate(info['gpu']):
                print(f"  GPU {i}: {gpu['name']}")
                print(f"    Memory: {gpu['memory_used_mb']:.1f} MB / {gpu['memory_total_mb']:.1f} MB")
                print(f"    Temperature: {gpu['temperature_c']}°C")
        else:
            print("\nNo GPU detected")
        
        print("================================================\n")
        
        # Save diagnostics to file
        diagnostics_file = f"logs/diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(diagnostics_file, 'w') as f:
            json.dump(info, f, indent=2)
        logger.info(f"Diagnostics saved to {diagnostics_file}")
        
    except Exception as e:
        handle_exception("Error running diagnostics", e)

# ==========================================
# Memory Profiling
# ==========================================

class MemoryProfiler:
    """Profiles and analyzes memory usage in the application."""
    
    def __init__(self, output_dir: str = "logs"):
        """Initialize the memory profiler.
        
        Args:
            output_dir: Directory to save results
        """
        if not HAS_PSUTIL:
            raise ImportError("Memory profiling requires the psutil module")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.records = []
        self.start_time = time.time()
        self.process = psutil.Process()
    
    def snapshot(self) -> Dict[str, Any]:
        """Take a snapshot of current memory usage.
        
        Returns:
            Dictionary with memory usage information
        """
        try:
            with self.process.oneshot():
                mem_info = self.process.memory_info()
                system_mem = psutil.virtual_memory()
                
                record = {
                    'timestamp': time.time(),
                    'elapsed_time': time.time() - self.start_time,
                    'process': {
                        'pid': self.process.pid,
                        'rss_mb': mem_info.rss / (1024 * 1024),
                        'vms_mb': mem_info.vms / (1024 * 1024),
                        'percent': self.process.memory_percent(),
                    },
                    'system': {
                        'total_mb': system_mem.total / (1024 * 1024),
                        'available_mb': system_mem.available / (1024 * 1024),
                        'used_percent': system_mem.percent,
                    }
                }
                
                self.records.append(record)
                return record
        except Exception as e:
            logger.error(f"Error taking memory snapshot: {e}")
            return {'error': str(e)}
    
    def start_monitoring(self, interval: float = 1.0, callback: Optional[Callable] = None):
        """Start continuous memory monitoring in a background thread.
        
        Args:
            interval: Time between snapshots in seconds
            callback: Optional callback function to call with each snapshot
        
        Returns:
            Background thread
        """
        import threading
        
        def monitor():
            while self._monitoring:
                snapshot = self.snapshot()
                if callback:
                    try:
                        callback(snapshot)
                    except Exception as e:
                        logger.error(f"Error in memory monitoring callback: {e}")
                time.sleep(interval)
        
        self._monitoring = True
        self.monitoring_thread = threading.Thread(target=monitor, daemon=True)
        self.monitoring_thread.start()
        return self.monitoring_thread
    
    def stop_monitoring(self):
        """Stop continuous memory monitoring."""
        self._monitoring = False
        if hasattr(self, 'monitoring_thread') and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of memory usage over time.
        
        Returns:
            Dictionary with memory usage summary
        """
        if not self.records:
            return {'error': 'No memory snapshots recorded'}
        
        # Calculate statistics
        process_rss = [r['process']['rss_mb'] for r in self.records]
        system_used = [r['system']['used_percent'] for r in self.records]
        
        summary = {
            'samples': len(self.records),
            'duration': self.records[-1]['elapsed_time'],
            'process': {
                'min_rss_mb': min(process_rss),
                'max_rss_mb': max(process_rss),
                'avg_rss_mb': sum(process_rss) / len(process_rss),
                'growth_mb': process_rss[-1] - process_rss[0],
            },
            'system': {
                'min_used_percent': min(system_used),
                'max_used_percent': max(system_used),
                'avg_used_percent': sum(system_used) / len(system_used),
            }
        }
        
        return summary
    
    def save_report(self) -> str:
        """Save a memory profiling report to file.
        
        Returns:
            Path to the saved report
        """
        summary = self.get_summary()
        
        # Combine summary and records
        report = {
            'summary': summary,
            'detailed_records': self.records
        }
        
        # Save to file
        filename = f"memory_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Memory profiling report saved to {filepath}")
        return str(filepath)
    
    def visualize(self, output_file: Optional[str] = None) -> Optional[str]:
        """Visualize memory usage over time.
        
        Args:
            output_file: Optional file path to save the visualization
            
        Returns:
            Path to the saved visualization if output_file provided
        """
        if not HAS_MATPLOTLIB:
            logger.error("Visualization requires matplotlib")
            return None
        
        if not self.records:
            logger.error("No memory data to visualize")
            return None
        
        try:
            # Extract data
            timestamps = [r['elapsed_time'] for r in self.records]
            process_rss = [r['process']['rss_mb'] for r in self.records]
            process_percent = [r['process']['percent'] for r in self.records]
            system_percent = [r['system']['used_percent'] for r in self.records]
            
            # Create the figure
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
            
            # Process memory
            ax1.plot(timestamps, process_rss, 'b-', label='Process RSS')
            ax1.set_ylabel('Memory (MB)')
            ax1.set_title('Memory Usage Over Time')
            ax1.legend(loc='upper left')
            ax1.grid(True)
            
            # Usage percentages
            ax2.plot(timestamps, process_percent, 'g-', label='Process %')
            ax2.plot(timestamps, system_percent, 'r-', label='System %')
            ax2.set_xlabel('Time (seconds)')
            ax2.set_ylabel('Usage %')
            ax2.set_ylim(0, 100)
            ax2.legend(loc='upper left')
            ax2.grid(True)
            
            plt.tight_layout()
            
            # Save if requested
            if output_file:
                plt.savefig(output_file)
                logger.info(f"Memory visualization saved to {output_file}")
                return output_file
            else:
                plt.show()
                return None
                
        except Exception as e:
            logger.error(f"Error visualizing memory data: {e}")
            return None

# ==========================================
# Performance Optimization
# ==========================================

def suggest_optimizations() -> List[Dict[str, Any]]:
    """Analyze the system and suggest performance optimizations.
    
    Returns:
        List of optimization suggestions
    """
    if not HAS_PSUTIL:
        return [{'error': 'psutil module required for optimization suggestions'}]
    
    suggestions = []
    
    # Check memory usage
    try:
        mem = psutil.virtual_memory()
        if mem.percent > 85:
            suggestions.append({
                'category': 'memory',
                'severity': 'high',
                'title': 'High memory usage detected',
                'description': f'Memory usage is at {mem.percent}%. Consider closing unused applications or increasing swap space.',
                'metrics': {'memory_percent': mem.percent}
            })
        elif mem.percent > 70:
            suggestions.append({
                'category': 'memory',
                'severity': 'medium',
                'title': 'Moderate memory usage detected',
                'description': f'Memory usage is at {mem.percent}%. Monitor for potential issues if running memory-intensive tasks.',
                'metrics': {'memory_percent': mem.percent}
            })
    except Exception as e:
        logger.error(f"Error checking memory: {e}")
    
    # Check CPU usage
    try:
        cpu_percent = psutil.cpu_percent(interval=0.5)
        if cpu_percent > 90:
            suggestions.append({
                'category': 'cpu',
                'severity': 'high',
                'title': 'High CPU usage detected',
                'description': f'CPU usage is at {cpu_percent}%. This may slow down overall system performance.',
                'metrics': {'cpu_percent': cpu_percent}
            })
        elif cpu_percent > 75:
            suggestions.append({
                'category': 'cpu',
                'severity': 'medium',
                'title': 'Moderate CPU usage detected',
                'description': f'CPU usage is at {cpu_percent}%. Consider optimizing CPU-intensive tasks.',
                'metrics': {'cpu_percent': cpu_percent}
            })
    except Exception as e:
        logger.error(f"Error checking CPU: {e}")
    
    # Check disk space
    try:
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            suggestions.append({
                'category': 'disk',
                'severity': 'high',
                'title': 'Low disk space detected',
                'description': f'Disk usage is at {disk.percent}%. Free up disk space to prevent system issues.',
                'metrics': {'disk_percent': disk.percent}
            })
        elif disk.percent > 80:
            suggestions.append({
                'category': 'disk',
                'severity': 'medium',
                'title': 'Moderate disk usage detected',
                'description': f'Disk usage is at {disk.percent}%. Consider cleaning up unnecessary files.',
                'metrics': {'disk_percent': disk.percent}
            })
    except Exception as e:
        logger.error(f"Error checking disk: {e}")
    
    # Check for running Python processes
    try:
        python_processes = [p for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])
                          if 'python' in p.info['name'].lower()]
        
        if len(python_processes) > 5:
            high_resource_procs = [p for p in python_processes 
                                  if p.info['cpu_percent'] > 10 or p.info['memory_percent'] > 5]
            
            if high_resource_procs:
                proc_list = ', '.join([f"{p.info['name']}({p.info['pid']})" for p in high_resource_procs[:3]])
                suggestions.append({
                    'category': 'processes',
                    'severity': 'medium',
                    'title': 'Multiple resource-intensive Python processes',
                    'description': f'Found {len(high_resource_procs)} Python processes using significant resources. '
                                  f'Examples: {proc_list}. Consider consolidating or optimizing.',
                    'metrics': {'process_count': len(python_processes)}
                })
    except Exception as e:
        logger.error(f"Error checking processes: {e}")
    
    # Python-specific suggestions
    if sys.version_info < (3, 9):
        suggestions.append({
            'category': 'python',
            'severity': 'low',
            'title': 'Python version upgrade recommended',
            'description': f'Current Python version is {platform.python_version()}. '
                          f'Upgrading to Python 3.9+ can provide performance improvements.',
            'metrics': {'python_version': platform.python_version()}
        })
    
    return suggestions

# ==========================================
# Error Testing Framework
# ==========================================

class ErrorTestingFramework:
    """Framework for testing error handling mechanisms and measuring their effectiveness."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize the error testing framework.
        
        Args:
            config_file: Path to configuration file
        """
        self.config = self._load_config(config_file)
        self.results = {}
        self.success_count = 0
        self.test_count = 0
    
    def _load_config(self, config_file: Optional[str]) -> Dict:
        """Load configuration from file or use defaults.
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            Config dictionary
        """
        default_config = {
            "scenarios": [
                {
                    "name": "resource_limits",
                    "description": "Test handling of resource limitation errors",
                    "tests": [
                        {"function": "test_memory_allocation", "iterations": 5},
                        {"function": "test_cpu_intensive", "iterations": 3}
                    ]
                },
                {
                    "name": "configuration_errors",
                    "description": "Test handling of configuration errors",
                    "tests": [
                        {"function": "test_missing_config", "iterations": 2},
                        {"function": "test_invalid_config", "iterations": 2}
                    ]
                },
                {
                    "name": "network_errors",
                    "description": "Test handling of network errors",
                    "tests": [
                        {"function": "test_connection_timeout", "iterations": 3},
                        {"function": "test_invalid_endpoint", "iterations": 2}
                    ]
                }
            ],
            "output_path": "logs/error_test_results.json",
            "concurrent_tests": 2
        }
        
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with default config
                    for key, value in loaded_config.items():
                        default_config[key] = value
                logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.error(f"Error loading configuration: {e}")
        
        return default_config
    
    def run_tests(self) -> Dict:
        """Run all test scenarios and collect results.
        
        Returns:
            Test results dictionary
        """
        start_time = time.time()
        logger.info("Starting error testing...")
        
        for scenario in self.config["scenarios"]:
            self._run_scenario(scenario)
        
        # Calculate overall statistics
        total_time = time.time() - start_time
        success_rate = (self.success_count / self.test_count) * 100 if self.test_count else 0
        
        # Save results
        self.results["summary"] = {
            "total_scenarios": len(self.config["scenarios"]),
            "total_tests": self.test_count,
            "success_count": self.success_count,
            "success_rate": f"{success_rate:.2f}%",
            "execution_time": f"{total_time:.2f}s"
        }
        
        # Save to file
        with open(self.config["output_path"], 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Testing complete: {self.success_count}/{self.test_count} tests passed ({success_rate:.2f}%)")
        return self.results
    
    def _run_scenario(self, scenario: Dict) -> None:
        """Run a specific test scenario.
        
        Args:
            scenario: Scenario configuration dictionary
        """
        name = scenario["name"]
        logger.info(f"Running scenario: {name}")
        scenario_start = time.time()
        
        results = []
        
        # Get the maximum number of concurrent tests
        max_workers = min(self.config.get("concurrent_tests", 2), len(scenario["tests"]))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for test in scenario["tests"]:
                test_func = getattr(self, test["function"], None)
                
                if test_func:
                    for i in range(test.get("iterations", 1)):
                        futures.append(executor.submit(test_func))
                else:
                    logger.warning(f"Test function {test['function']} not found")
            
            # Collect results
            for future in futures:
                try:
                    result = future.result()
                    results.append(result)
                    self.test_count += 1
                    if result["success"]:
                        self.success_count += 1
                except Exception as e:
                    logger.error(f"Error running test: {e}")
        
        # Calculate statistics
        scenario_time = time.time() - scenario_start
        success_count = sum(1 for r in results if r["success"])
        success_rate = (success_count / len(results)) * 100 if results else 0
        
        self.results[name] = {
            "description": scenario.get("description", ""),
            "results": results,
            "success_rate": f"{success_rate:.2f}%",
            "execution_time": f"{scenario_time:.2f}s",
            "success_count": success_count,
            "total_tests": len(results)
        }
        
        logger.info(f"Scenario '{name}' completed: {success_count}/{len(results)} tests passed ({success_rate:.2f}%)")
    
    # ==========================================
    # Test Functions
    # ==========================================
    
    def test_memory_allocation(self) -> Dict:
        """Test error handling for large memory allocations.
        
        Returns:
            Test result dictionary
        """
        result = {
            "name": "memory_allocation",
            "success": False,
            "time": time.time()
        }
        
        try:
            # Create a log entry
            logger.info("Testing memory allocation error handling")
            
            # Attempt to allocate a large amount of memory
            try:
                # This should be caught by the error handler
                large_list = [0] * (1024 * 1024 * 1024)  # Try to allocate 1GB
                result["message"] = "Memory allocation succeeded unexpectedly"
            except MemoryError as e:
                # This is expected
                handle_exception("Memory allocation error (expected)", e)
                result["success"] = True
                result["message"] = "Memory allocation error handled correctly"
        except Exception as e:
            result["message"] = f"Unexpected error: {str(e)}"
        
        return result
    
    def test_cpu_intensive(self) -> Dict:
        """Test error handling for CPU-intensive operations.
        
        Returns:
            Test result dictionary
        """
        result = {
            "name": "cpu_intensive",
            "success": False,
            "time": time.time()
        }
        
        try:
            logger.info("Testing CPU-intensive operation error handling")
            
            # Simulate a CPU-intensive operation
            start_time = time.time()
            try:
                # Calculate prime numbers inefficiently
                timeout = 2  # seconds
                primes = []
                num = 2
                
                while time.time() - start_time < timeout:
                    is_prime = True
                    for i in range(2, int(num ** 0.5) + 1):
                        if num % i == 0:
                            is_prime = False
                            break
                    if is_prime:
                        primes.append(num)
                    num += 1
                
                result["success"] = True
                result["message"] = f"CPU-intensive operation completed with {len(primes)} primes found"
            except Exception as e:
                handle_exception("CPU intensive operation error", e)
                result["message"] = f"Error during CPU-intensive operation: {str(e)}"
        except Exception as e:
            result["message"] = f"Unexpected error: {str(e)}"
        
        return result
    
    def test_missing_config(self) -> Dict:
        """Test error handling for missing configuration.
        
        Returns:
            Test result dictionary
        """
        result = {
            "name": "missing_config",
            "success": False,
            "time": time.time()
        }
        
        try:
            logger.info("Testing missing configuration error handling")
            
            # Try to load a non-existent configuration file
            try:
                with open('non_existent_config.json', 'r') as f:
                    config = json.load(f)
                result["message"] = "Loading non-existent file succeeded unexpectedly"
            except FileNotFoundError as e:
                # This is expected
                handle_exception("Configuration file not found (expected)", e)
                result["success"] = True
                result["message"] = "Missing configuration error handled correctly"
        except Exception as e:
            result["message"] = f"Unexpected error: {str(e)}"
        
        return result
    
    def test_invalid_config(self) -> Dict:
        """Test error handling for invalid configuration.
        
        Returns:
            Test result dictionary
        """
        result = {
            "name": "invalid_config",
            "success": False,
            "time": time.time()
        }
        
        try:
            logger.info("Testing invalid configuration error handling")
            
            # Create a temporary file with invalid JSON
            temp_file = "temp_invalid_config.json"
            try:
                with open(temp_file, 'w') as f:
                    f.write("{ 'invalid': 'json' ")  # Missing closing brace
                
                # Try to load the invalid JSON
                try:
                    with open(temp_file, 'r') as f:
                        config = json.load(f)
                    result["message"] = "Loading invalid JSON succeeded unexpectedly"
                except json.JSONDecodeError as e:
                    # This is expected
                    handle_exception("Invalid JSON configuration (expected)", e)
                    result["success"] = True
                    result["message"] = "Invalid configuration error handled correctly"
            finally:
                # Clean up
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        except Exception as e:
            result["message"] = f"Unexpected error: {str(e)}"
        
        return result
    
    def test_connection_timeout(self) -> Dict:
        """Test error handling for network connection timeouts.
        
        Returns:
            Test result dictionary
        """
        result = {
            "name": "connection_timeout",
            "success": False,
            "time": time.time()
        }
        
        try:
            logger.info("Testing connection timeout error handling")
            
            # Try to connect to a non-responsive endpoint
            try:
                import socket
                import urllib.request
                
                # Set a very short timeout
                socket.setdefaulttimeout(0.01)
                
                # Use a non-routable IP address
                urllib.request.urlopen("http://192.0.2.1/")
                
                result["message"] = "Connection succeeded unexpectedly"
            except (socket.timeout, urllib.error.URLError) as e:
                # This is expected
                handle_exception("Connection timeout (expected)", e)
                result["success"] = True
                result["message"] = "Connection timeout error handled correctly"
            finally:
                # Reset timeout
                socket.setdefaulttimeout(None)
        except Exception as e:
            result["message"] = f"Unexpected error: {str(e)}"
        
        return result
    
    def test_invalid_endpoint(self) -> Dict:
        """Test error handling for invalid network endpoints.
        
        Returns:
            Test result dictionary
        """
        result = {
            "name": "invalid_endpoint",
            "success": False,
            "time": time.time()
        }
        
        try:
            logger.info("Testing invalid endpoint error handling")
            
            # Try to connect to an invalid URL
            try:
                import urllib.request
                urllib.request.urlopen("http://invalid.domain.that.doesnt.exist/")
                result["message"] = "Invalid endpoint connection succeeded unexpectedly"
            except urllib.error.URLError as e:
                # This is expected
                handle_exception("Invalid endpoint (expected)", e)
                result["success"] = True
                result["message"] = "Invalid endpoint error handled correctly"
        except Exception as e:
            result["message"] = f"Unexpected error: {str(e)}"
        
        return result

# ==========================================
# Main Function
# ==========================================

def main():
    """Main entry point for the diagnostics module."""
    parser = argparse.ArgumentParser(description='Diagnostics and Error Testing Tool')
    parser.add_argument('--run-diagnostics', '-d', action='store_true', help='Run system diagnostics')
    parser.add_argument('--test-errors', '-t', action='store_true', help='Run error handling tests')
    parser.add_argument('--profile-memory', '-m', action='store_true', help='Run memory profiling')
    parser.add_argument('--suggest-optimizations', '-o', action='store_true', help='Suggest performance optimizations')
    parser.add_argument('--config', '-c', help='Path to test configuration file')
    parser.add_argument('--output', '-o', help='Path to save test results')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--duration', type=float, default=10.0, help='Duration for monitoring in seconds')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Register signal handlers
    register_signal_handlers()
    
    # Run diagnostics if requested
    if args.run_diagnostics:
        run_diagnostics()
    
    # Run error tests if requested
    if args.test_errors:
        framework = ErrorTestingFramework(args.config)
        
        if args.output:
            framework.config["output_path"] = args.output
        
        results = framework.run_tests()
        
        # Print summary
        summary = results["summary"]
        print("\n========== Error Testing Summary ==========")
        print(f"Total Scenarios: {summary['total_scenarios']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"Execution Time: {summary['execution_time']}")
        print("===========================================\n")
    
    # Run memory profiling if requested
    if args.profile_memory:
        if not HAS_PSUTIL:
            print("Memory profiling requires psutil module")
            return
        
        print("\nStarting memory profiling...")
        profiler = MemoryProfiler()
        
        # Take initial snapshot
        print("Taking initial memory snapshot...")
        initial = profiler.snapshot()
        print(f"Initial process memory: {initial['process']['rss_mb']:.2f} MB")
        
        # Monitor for the specified duration
        print(f"Monitoring memory for {args.duration} seconds...")
        profiler.start_monitoring(interval=0.5)
        time.sleep(args.duration)
        profiler.stop_monitoring()
        
        # Get and display results
        summary = profiler.get_summary()
        print("\n========== Memory Profile Summary ==========")
        print(f"Duration: {summary['duration']:.2f} seconds")
        print(f"Process RSS: min={summary['process']['min_rss_mb']:.2f} MB, "
              f"max={summary['process']['max_rss_mb']:.2f} MB, "
              f"avg={summary['process']['avg_rss_mb']:.2f} MB")
        print(f"Memory growth: {summary['process']['growth_mb']:.2f} MB")
        print(f"System memory usage: min={summary['system']['min_used_percent']:.2f}%, "
              f"max={summary['system']['max_used_percent']:.2f}%, "
              f"avg={summary['system']['avg_used_percent']:.2f}%")
        print("============================================\n")
        
        # Save report
        report_path = profiler.save_report()
        print(f"Memory profile saved to: {report_path}")
        
        # Visualize if matplotlib is available
        if HAS_MATPLOTLIB:
            vis_path = os.path.join("logs", f"memory_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            profiler.visualize(vis_path)
            print(f"Memory visualization saved to: {vis_path}")
    
    # Suggest optimizations if requested
    if args.suggest_optimizations:
        print("\nAnalyzing system for optimization opportunities...")
        suggestions = suggest_optimizations()
        
        if suggestions:
            print("\n========== Optimization Suggestions ==========")
            for i, suggestion in enumerate(suggestions, 1):
                severity = suggestion.get('severity', 'info').upper()
                print(f"{i}. [{severity}] {suggestion.get('title', 'Unnamed suggestion')}")
                print(f"   {suggestion.get('description', 'No description')}")
                print()
            print("=============================================\n")
        else:
            print("\nNo optimization suggestions found. Your system appears to be running optimally.\n")
    
    # If no action specified, run diagnostics by default
    if not (args.run_diagnostics or args.test_errors or args.profile_memory or args.suggest_optimizations):
        run_diagnostics()

if __name__ == "__main__":
    main()
