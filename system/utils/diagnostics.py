#!/usr/bin/env python3
"""
Diagnostic and Error Handling Utilities for AI Research Environment

This module provides comprehensive error handling, diagnostics, and monitoring
capabilities for the research environment, including performance tracking,
error logging, and recovery mechanisms.
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
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union, Tuple

# Configure logging
logger = logging.getLogger('environment.diagnostics')

# Import system utilities with fallback mechanism
try:
    from utils.system_utils import system_manager
except ImportError:
    # Add parent directory to path for imports if needed
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from utils.system_utils import system_manager
    except ImportError:
        logger.warning("Could not import system_utils. Some diagnostic features will be limited.")
        system_manager = None


# Define exception classes for the research environment
class EnvironmentError(Exception):
    """Base class for environment-specific exceptions."""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)
        
    def __str__(self) -> str:
        """String representation including original error if available."""
        if self.original_error:
            return f"{self.message} (Original error: {self.original_error})"
        return self.message


class ResourceError(EnvironmentError):
    """Error related to system resources (memory, disk, etc.)."""
    pass


class ConfigurationError(EnvironmentError):
    """Error related to environment configuration."""
    pass


class DockerError(EnvironmentError):
    """Error related to Docker operations."""
    pass


class NetworkError(EnvironmentError):
    """Error related to network operations."""
    pass


# Diagnostic data collection class
class DiagnosticCollector:
    """Collects diagnostic information about the system and environment."""
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize the diagnostic collector."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.data = {}
        self.start_time = datetime.now()
        
        # Register shutdown handler
        atexit.register(self.save_diagnostics)
    
    def collect_system_info(self) -> Dict:
        """Collect system information."""
        if system_manager:
            return system_manager.get_system_summary()
        
        # Fallback implementation if system_manager not available
        import psutil
        
        system_info = {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'hostname': platform.node(),
            'cpu': {
                'count_logical': psutil.cpu_count(logical=True),
                'count_physical': psutil.cpu_count(logical=False),
                'utilization': psutil.cpu_percent(interval=0.1)
            },
            'memory': {
                'total_mib': psutil.virtual_memory().total // (1024 * 1024),
                'available_mib': psutil.virtual_memory().available // (1024 * 1024),
                'percent_used': psutil.virtual_memory().percent,
            },
        }
        
        return system_info
    
    def collect_environment_variables(self) -> Dict:
        """Collect relevant environment variables."""
        # Only collect non-sensitive environment variables
        safe_vars = [
            'PATH', 'PYTHONPATH', 'LANG', 'LC_ALL', 'SHELL', 'TERM',
            'CUDA_VISIBLE_DEVICES', 'NVIDIA_VISIBLE_DEVICES',
            'TF_MEMORY_ALLOCATION', 'PYTHONUNBUFFERED',
            'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
            'JUPYTER_TOKEN',  # Usually safe to log this
            'ENABLE_MONITORING', 'ENABLE_GPU'
        ]
        
        env_vars = {}
        for var in safe_vars:
            if var in os.environ:
                env_vars[var] = os.environ[var]
        
        return env_vars
    
    def collect_docker_info(self) -> Dict:
        """Collect Docker-related information."""
        docker_info = {'available': False}
        
        try:
            import subprocess
            result = subprocess.run(
                ["docker", "info", "--format", "{{json .}}"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            docker_info = {'available': True, 'docker_info': json.loads(result.stdout)}
            
            # Get container status
            result = subprocess.run(
                ["docker", "ps", "--format", "{{json .}}"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    containers.append(json.loads(line))
            docker_info['containers'] = containers
            
        except (subprocess.SubprocessError, json.JSONDecodeError, ImportError, FileNotFoundError):
            pass
        
        return docker_info
    
    def check_common_issues(self) -> List[Dict]:
        """Check for common issues in the environment."""
        issues = []
        
        # Check disk space
        if system_manager:
            disk_info = system_manager.get_disk_info()
            for mount, info in disk_info.items():
                if info['percent_used'] > 90:
                    issues.append({
                        'severity': 'warning',
                        'category': 'disk_space',
                        'message': f"Low disk space on {mount}: {info['percent_used']}% used",
                        'details': {
                            'mount_point': mount,
                            'free_gb': info['free_gb'],
                            'percent_used': info['percent_used']
                        }
                    })
        
        # Check memory usage
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                issues.append({
                    'severity': 'warning',
                    'category': 'memory',
                    'message': f"High memory usage: {memory.percent}% used",
                    'details': {
                        'available_mb': memory.available // (1024 * 1024),
                        'percent_used': memory.percent
                    }
                })
        except ImportError:
            pass
        
        # Check if Docker is running
        try:
            import subprocess
            subprocess.run(["docker", "info"], check=True, 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (subprocess.SubprocessError, FileNotFoundError):
            issues.append({
                'severity': 'error',
                'category': 'docker',
                'message': "Docker is not running or not installed"
            })
        
        return issues
    
    def collect_all(self) -> Dict:
        """Collect all diagnostic information."""
        self.data = {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            'system': self.collect_system_info(),
            'environment': self.collect_environment_variables(),
            'docker': self.collect_docker_info(),
            'issues': self.check_common_issues()
        }
        return self.data
    
    def save_diagnostics(self, filename: Optional[str] = None) -> str:
        """Save the diagnostic information to a file."""
        if not self.data:
            self.collect_all()
        
        if filename is None:
            filename = f"diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.log_dir / filename
        with open(filepath, 'w') as f:
            json.dump(self.data, f, indent=2)
        
        logger.info(f"Saved diagnostic information to {filepath}")
        return str(filepath)
    
    def print_summary(self) -> None:
        """Print a summary of the diagnostic information."""
        if not self.data:
            self.collect_all()
        
        print("AI Research Environment - Diagnostic Summary")
        print("============================================")
        
        # System information
        system = self.data['system']
        print(f"\nSystem: {system['platform']} - Python {system['python_version']}")
        print(f"CPU: {system['cpu']['count_physical']} physical cores, "
              f"{system['cpu']['count_logical']} logical cores, "
              f"{system['cpu']['utilization']}% utilization")
        print(f"Memory: {system['memory']['total_mib']} MiB total, "
              f"{system['memory']['available_mib']} MiB available, "
              f"{system['memory']['percent_used']}% used")
        
        # Docker information
        docker = self.data['docker']
        if docker['available']:
            print(f"\nDocker: Available")
            if 'containers' in docker:
                print(f"Running containers: {len(docker['containers'])}")
        else:
            print("\nDocker: Not available")
        
        # Issues
        issues = self.data['issues']
        if issues:
            print("\nDetected Issues:")
            for issue in issues:
                print(f"  [{issue['severity'].upper()}] {issue['message']}")
        else:
            print("\nNo issues detected")


# Error handling functions
def handle_exception(
    message: str, 
    exception: Optional[Exception] = None, 
    exit_code: Optional[int] = None,
    notify: bool = False
) -> None:
    """
    Handle an exception with proper logging and optional termination.
    
    Args:
        message: Human-readable error message
        exception: The original exception that was caught
        exit_code: If not None, exit the program with this code
        notify: Whether to attempt to send a notification
    """
    error_details = {
        'timestamp': datetime.now().isoformat(),
        'message': message,
    }
    
    if exception:
        error_details['exception_type'] = type(exception).__name__
        error_details['exception_msg'] = str(exception)
        
        # Log the full traceback
        logger.error(f"{message}: {type(exception).__name__}: {exception}")
        logger.debug(traceback.format_exc())
        
        # Additional details for specific error types
        if isinstance(exception, MemoryError):
            logger.error("Memory error detected. Check available system memory.")
            try:
                import psutil
                mem = psutil.virtual_memory()
                logger.error(f"Memory stats: {mem.percent}% used, {mem.available/(1024**2):.1f}MB available")
                error_details['memory_stats'] = {
                    'percent_used': mem.percent,
                    'available_mb': mem.available/(1024**2)
                }
            except ImportError:
                pass
    else:
        logger.error(message)
    
    # Create error report file
    try:
        os.makedirs('logs', exist_ok=True)
        error_file = f"logs/error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(error_file, 'w') as f:
            json.dump(error_details, f, indent=2)
        logger.info(f"Error report saved to {error_file}")
    except Exception as e:
        logger.warning(f"Could not write error report: {e}")
    
    # Try to send notification if requested
    if notify:
        try:
            _send_notification(message, error_details)
        except Exception as e:
            logger.warning(f"Failed to send notification: {e}")
    
    # Exit if requested
    if exit_code is not None:
        sys.exit(exit_code)


def _send_notification(message: str, details: Dict) -> None:
    """
    Send a notification about an error.
    
    This is a stub implementation that can be expanded with your preferred
    notification method (e.g., email, Slack, etc.).
    """
    # Check if notification settings are configured
    notify_method = os.environ.get('NOTIFY_METHOD', '').lower()
    
    if not notify_method:
        logger.debug("No notification method configured")
        return
    
    # Simplified example for demonstration - expand with your preferred method
    if notify_method == 'console':
        print("\n" + "!"*50)
        print(f"NOTIFICATION: {message}")
        print("!"*50 + "\n")
    elif notify_method == 'file':
        with open('notifications.txt', 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")


def setup_error_handlers() -> None:
    """Set up global error handlers for signals and uncaught exceptions."""
    # Handle keyboard interrupt (SIGINT)
    def sigint_handler(sig, frame):
        logger.info("\nInterrupted by user. Shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, sigint_handler)
    
    # Handle termination (SIGTERM)
    def sigterm_handler(sig, frame):
        logger.info("Received termination signal. Shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, sigterm_handler)
    
    # Handle uncaught exceptions
    def exception_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Handle KeyboardInterrupt specially for clean user interruption
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.critical("Uncaught exception", 
                       exc_info=(exc_type, exc_value, exc_traceback))
        
        # Save diagnostic information
        try:
            collector = DiagnosticCollector()
            collector.collect_all()
            collector.save_diagnostics(f"crash_diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        except Exception:
            pass
    
    sys.excepthook = exception_handler


def retry(
    max_attempts: int = 3, 
    delay: float = 1.0, 
    backoff: float = 2.0, 
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    logger_instance: Optional[logging.Logger] = None
) -> Callable:
    """
    Retry decorator for functions that might fail temporarily.
    
    Args:
        max_attempts: Maximum number of attempts to make
        delay: Initial delay between retries in seconds
        backoff: Multiplier applied to delay between retries
        exceptions: Exceptions to catch and retry on
        logger_instance: Logger to use for logging retries
    
    Returns:
        Decorator function
    """
    log = logger_instance or logging.getLogger('environment.retry')
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        log.warning(f"Final attempt failed after {max_attempts} tries")
                        raise
                    
                    log.warning(f"Attempt {attempt} failed: {e}. Retrying in {current_delay:.1f}s...")
                    time.sleep(current_delay)
                    attempt += 1
                    current_delay *= backoff
        
        return wrapper
    return decorator


def run_diagnostics() -> Dict:
    """
    Run comprehensive diagnostics and return results.
    This function is the main entry point for diagnostic tools.
    """
    collector = DiagnosticCollector()
    data = collector.collect_all()
    collector.print_summary()
    filepath = collector.save_diagnostics()
    
    print(f"\nDetailed diagnostic information saved to {filepath}")
    return data


# Create singleton instance for easy access
diagnostic_collector = DiagnosticCollector()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up error handlers
    setup_error_handlers()
    
    # Run diagnostics
    run_diagnostics()
    
    # Example of retry decorator usage
    @retry(max_attempts=3)
    def unstable_function():
        import random
        if random.random() < 0.7:
            raise ConnectionError("Simulated error")
        return "Success!"
    
    try:
        print("\nTesting retry functionality...")
        result = unstable_function()
        print(f"Function result: {result}")
    except Exception as e:
        handle_exception("Error in demonstration", e)