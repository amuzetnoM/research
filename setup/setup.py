#!/usr/bin/env python3
"""
Comprehensive setup script for AI Research Environment.
This script handles all aspects of environment setup, including:
- Docker configuration
- GPU detection
- System optimization
- Requirements installation
- Directory structure creation
"""

import argparse
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'setup.log'))
    ]
)
logger = logging.getLogger('setup')

# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='AI Research Environment Setup')
    
    # General options
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--force', '-f', action='store_true', help='Force setup even if already configured')
    
    # Component selection
    parser.add_argument('--all', action='store_true', help='Set up all components')
    parser.add_argument('--docker', action='store_true', help='Set up Docker environment')
    parser.add_argument('--python', action='store_true', help='Set up Python environment')
    parser.add_argument('--monitoring', action='store_true', help='Set up monitoring stack')
    
    # Docker options
    parser.add_argument('--gpu', action='store_true', help='Force GPU support')
    parser.add_argument('--no-gpu', action='store_true', help='Disable GPU support')
    
    # Path options
    parser.add_argument('--docker-dir', type=str, default='head_1', 
                        help='Directory for Docker files')
    
    return parser.parse_args()


def set_log_level(verbose: bool) -> None:
    """Set the log level based on verbosity."""
    if verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    else:
        logger.setLevel(logging.INFO)


def check_prerequisites() -> bool:
    """
    Check if all prerequisites are installed.
    Returns: True if all prerequisites are met, False otherwise
    """
    logger.info("Checking prerequisites...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        logger.error(f"Python 3.8+ is required, found {python_version.major}.{python_version.minor}")
        return False
    logger.debug(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check Docker
    try:
        docker_version = subprocess.run(
            ["docker", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        ).stdout.strip()
        logger.debug(f"Docker version: {docker_version}")
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.error("Docker not found. Please install Docker before continuing.")
        logger.info("Visit https://docs.docker.com/get-docker/ for installation instructions.")
        return False
    
    # Check Docker Compose
    try:
        compose_version = subprocess.run(
            ["docker-compose", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        ).stdout.strip()
        logger.debug(f"Docker Compose version: {compose_version}")
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.warning("Docker Compose not found. Some features may not work.")
        logger.info("Visit https://docs.docker.com/compose/install/ for installation instructions.")
    
    # Check git
    try:
        git_version = subprocess.run(
            ["git", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        ).stdout.strip()
        logger.debug(f"Git version: {git_version}")
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.warning("Git not found. Version control features may not work.")
    
    return True


def detect_gpu(force_gpu: bool = False, disable_gpu: bool = False) -> bool:
    """
    Detect if a GPU is available.
    
    Args:
        force_gpu: If True, assume GPU is available
        disable_gpu: If True, disable GPU detection
        
    Returns:
        bool: True if GPU is available, False otherwise
    """
    if disable_gpu:
        logger.info("GPU support disabled by user")
        return False
    
    if force_gpu:
        logger.info("GPU support forced by user")
        return True
    
    # Check using NVIDIA SMI
    try:
        nvidia_smi = subprocess.run(
            ["nvidia-smi"], 
            capture_output=True, 
            text=True
        )
        if nvidia_smi.returncode == 0:
            gpu_info = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()
            logger.info(f"GPU detected: {gpu_info}")
            
            # Check for NVIDIA Docker support
            docker_info = subprocess.run(
                ["docker", "info", "--format", "{{json .}}"],
                capture_output=True,
                text=True,
                check=True
            ).stdout
            
            try:
                docker_json = json.loads(docker_info)
                runtimes = docker_json.get("Runtimes", {})
                if "nvidia" not in runtimes:
                    logger.warning("NVIDIA Docker runtime not found. GPU support may not work correctly.")
                    logger.info("See https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html")
            except json.JSONDecodeError:
                logger.warning("Could not parse Docker info JSON. GPU support may not work correctly.")
            
            return True
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    logger.info("No GPU detected or NVIDIA drivers not installed")
    return False


def ensure_directory_structure(docker_dir: str) -> None:
    """
    Ensure all necessary directories exist.
    
    Args:
        docker_dir: Directory for Docker files
    """
    logger.info("Creating directory structure...")
    
    # Create directories
    directories = [
        docker_dir,
        "monitoring",
        "monitoring/prometheus",
        "monitoring/grafana",
        "monitoring/grafana/provisioning",
        "monitoring/grafana/provisioning/dashboards",
        "utils",
        "setup",
        "docs",
        "docs/examples",
        "docs/setup",
        "docs/troubleshooting",
    ]
    
    for directory in directories:
        dir_path = os.path.join(PROJECT_ROOT, directory)
        os.makedirs(dir_path, exist_ok=True)
        logger.debug(f"Created directory: {dir_path}")


def install_python_dependencies() -> None:
    """Install Python dependencies from requirements.txt."""
    logger.info("Installing Python dependencies...")
    requirements_path = os.path.join(PROJECT_ROOT, "setup/requirements.txt")
    
    if not os.path.exists(requirements_path):
        logger.error(f"Requirements file not found: {requirements_path}")
        return
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", requirements_path],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info("Successfully installed Python dependencies")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e.stderr}")
        logger.debug(f"Command output: {e.stdout}")


def make_executable(file_path: str) -> None:
    """
    Make a file executable.
    
    Args:
        file_path: Path to the file
    """
    if not os.path.exists(file_path):
        logger.warning(f"Cannot make non-existent file executable: {file_path}")
        return
    
    current_mode = os.stat(file_path).st_mode
    os.chmod(file_path, current_mode | 0o755)
    logger.debug(f"Made executable: {file_path}")


def setup_docker_environment(docker_dir: str, use_gpu: bool) -> None:
    """
    Set up Docker environment.
    
    Args:
        docker_dir: Directory for Docker files
        use_gpu: Whether to configure for GPU support
    """
    logger.info("Setting up Docker environment...")
    
    # Make entrypoint executable
    entrypoint_path = os.path.join(PROJECT_ROOT, "entrypoint.sh")
    make_executable(entrypoint_path)

    # Update symbolic links if needed
    docker_dir_path = os.path.join(PROJECT_ROOT, docker_dir)
    
    # Create symlink to entrypoint.sh in the docker directory for clarity
    entrypoint_link = os.path.join(docker_dir_path, "entrypoint.sh")
    if not os.path.exists(entrypoint_link):
        try:
            os.symlink(os.path.relpath(entrypoint_path, docker_dir_path), entrypoint_link)
            logger.debug(f"Created symlink: {entrypoint_link}")
        except OSError as e:
            logger.warning(f"Failed to create symlink: {e}")


def setup_monitoring_stack() -> None:
    """Set up the monitoring stack (Prometheus + Grafana)."""
    logger.info("Setting up monitoring stack...")
    
    # Create prometheus.yml if it doesn't exist
    prometheus_config = os.path.join(PROJECT_ROOT, "monitoring/prometheus/prometheus.yml")
    if not os.path.exists(prometheus_config):
        prometheus_config_dir = os.path.dirname(prometheus_config)
        os.makedirs(prometheus_config_dir, exist_ok=True)
        
        with open(prometheus_config, 'w') as f:
            f.write("""global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "node_exporter"
    static_configs:
      - targets: ["node-exporter:9100"]

  - job_name: "research_container"
    static_configs:
      - targets: ["research:8888"]
    metrics_path: /metrics

  - job_name: "cadvisor"
    static_configs:
      - targets: ["cadvisor:8080"]
""")
        logger.debug(f"Created Prometheus config: {prometheus_config}")


def cleanup_unnecessary_files(args: argparse.Namespace) -> None:
    """
    Clean up unnecessary files.
    
    Args:
        args: Command line arguments
    """
    logger.info("Cleaning up unnecessary files...")
    
    # Files to remove
    files_to_remove = [
        os.path.join(PROJECT_ROOT, "requirements.txt"),  # Root requirements file
        os.path.join(PROJECT_ROOT, "setup/requirements-core.txt"),
        os.path.join(PROJECT_ROOT, "Dockerfile"),
        os.path.join(PROJECT_ROOT, "docker-compose.yml"),
        os.path.join(PROJECT_ROOT, "run.sh"),
        os.path.join(PROJECT_ROOT, "start_docker.py"),
    ]
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.debug(f"Removed file: {file_path}")
            except OSError as e:
                logger.warning(f"Failed to remove file {file_path}: {e}")


def create_utils_diagnostic_tool() -> None:
    """Create the diagnostic tool in the utils directory."""
    logger.info("Creating diagnostic tool...")
    
    diagnostic_path = os.path.join(PROJECT_ROOT, "utils/diagnostic_tool.py")
    
    with open(diagnostic_path, 'w') as f:
        f.write("""#!/usr/bin/env python3
\"\"\"
Comprehensive Diagnostic Tool for AI Research Environment

This tool provides real-time diagnostics and monitoring for the research environment,
including system resources, GPU status, and container health.
\"\"\"

import argparse
import json
import logging
import os
import platform
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

import psutil

try:
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('diagnostic.log')
    ]
)
logger = logging.getLogger('diagnostic')

class SystemMonitor:
    \"\"\"Monitors system resource usage.\"\"\"
    
    def __init__(self):
        self.history_length = 60  # Keep 60 data points
        self.cpu_percent = [0] * self.history_length
        self.memory_percent = [0] * self.history_length
        self.disk_percent = [0] * self.history_length
        self.network_sent = [0] * self.history_length
        self.network_recv = [0] * self.history_length
        
        # Initial network counters
        net_io = psutil.net_io_counters()
        self.last_sent = net_io.bytes_sent
        self.last_recv = net_io.bytes_recv
    
    def update(self):
        \"\"\"Update system metrics.\"\"\"
        # CPU usage
        self.cpu_percent.pop(0)
        self.cpu_percent.append(psutil.cpu_percent())
        
        # Memory usage
        self.memory_percent.pop(0)
        self.memory_percent.append(psutil.virtual_memory().percent)
        
        # Disk usage
        self.disk_percent.pop(0)
        self.disk_percent.append(psutil.disk_usage('/').percent)
        
        # Network usage
        net_io = psutil.net_io_counters()
        sent_rate = net_io.bytes_sent - self.last_sent
        recv_rate = net_io.bytes_recv - self.last_recv
        self.last_sent = net_io.bytes_sent
        self.last_recv = net_io.bytes_recv
        
        self.network_sent.pop(0)
        self.network_sent.append(sent_rate)
        
        self.network_recv.pop(0)
        self.network_recv.append(recv_rate)
    
    def get_summary(self) -> Dict[str, float]:
        \"\"\"Get current system metrics summary.\"\"\"
        return {
            'cpu_percent': self.cpu_percent[-1],
            'memory_percent': self.memory_percent[-1],
            'disk_percent': self.disk_percent[-1],
            'network_sent_bytes': self.network_sent[-1],
            'network_recv_bytes': self.network_recv[-1],
        }

class GPUMonitor:
    \"\"\"Monitors GPU resource usage.\"\"\"
    
    def __init__(self):
        self.history_length = 60  # Keep 60 data points
        self.available = self._check_gpu_available()
        
        if self.available:
            self.gpu_count = self._get_gpu_count()
            self.memory_total = [0] * self.gpu_count
            self.memory_used = [[] for _ in range(self.gpu_count)]
            self.utilization = [[] for _ in range(self.gpu_count)]
            self.temperature = [[] for _ in range(self.gpu_count)]
            
            # Initialize history arrays
            for i in range(self.gpu_count):
                self.memory_used[i] = [0] * self.history_length
                self.utilization[i] = [0] * self.history_length
                self.temperature[i] = [0] * self.history_length
                
            # Get total memory for each GPU
            self._initialize_memory_total()
    
    def _check_gpu_available(self) -> bool:
        \"\"\"Check if NVIDIA GPU is available.\"\"\"
        try:
            subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _get_gpu_count(self) -> int:
        \"\"\"Get the number of GPUs.\"\"\"
        try:
            output = subprocess.run(
                ['nvidia-smi', '--list-gpus'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            ).stdout
            return len(output.strip().split('\\n'))
        except subprocess.SubprocessError:
            return 0
    
    def _initialize_memory_total(self):
        \"\"\"Initialize total memory for each GPU.\"\"\"
        try:
            output = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,memory.total', '--format=csv,noheader,nounits'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            ).stdout
            
            for line in output.strip().split('\\n'):
                parts = line.split(', ')
                if len(parts) == 2:
                    idx, total = int(parts[0]), float(parts[1])
                    if 0 <= idx < self.gpu_count:
                        self.memory_total[idx] = total
        except subprocess.SubprocessError:
            pass
    
    def update(self):
        \"\"\"Update GPU metrics.\"\"\"
        if not self.available:
            return
        
        try:
            output = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,memory.used,utilization.gpu,temperature.gpu', '--format=csv,noheader,nounits'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            ).stdout
            
            for line in output.strip().split('\\n'):
                parts = line.split(', ')
                if len(parts) == 4:
                    idx = int(parts[0])
                    if 0 <= idx < self.gpu_count:
                        memory_used = float(parts[1])
                        utilization = float(parts[2])
                        temperature = float(parts[3])
                        
                        self.memory_used[idx].pop(0)
                        self.memory_used[idx].append(memory_used)
                        
                        self.utilization[idx].pop(0)
                        self.utilization[idx].append(utilization)
                        
                        self.temperature[idx].pop(0)
                        self.temperature[idx].append(temperature)
        except subprocess.SubprocessError:
            pass
    
    def get_summary(self) -> List[Dict[str, float]]:
        \"\"\"Get current GPU metrics summary.\"\"\"
        if not self.available:
            return []
        
        result = []
        for i in range(self.gpu_count):
            result.append({
                'index': i,
                'memory_total_mb': self.memory_total[i],
                'memory_used_mb': self.memory_used[i][-1],
                'memory_percent': (self.memory_used[i][-1] / self.memory_total[i] * 100) if self.memory_total[i] > 0 else 0,
                'utilization_percent': self.utilization[i][-1],
                'temperature_c': self.temperature[i][-1]
            })
        return result

class DockerMonitor:
    \"\"\"Monitors Docker containers.\"\"\"
    
    def __init__(self):
        self.available = self._check_docker_available()
        self.containers = {}
    
    def _check_docker_available(self) -> bool:
        \"\"\"Check if Docker is available.\"\"\"
        try:
            subprocess.run(['docker', 'version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def update(self):
        \"\"\"Update Docker container metrics.\"\"\"
        if not self.available:
            return
        
        try:
            output = subprocess.run(
                ['docker', 'stats', '--no-stream', '--format', '{{.Name}}\\t{{.CPUPerc}}\\t{{.MemUsage}}\\t{{.NetIO}}\\t{{.BlockIO}}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            ).stdout
            
            new_containers = {}
            for line in output.strip().split('\\n'):
                if not line:
                    continue
                    
                parts = line.split('\\t')
                if len(parts) == 5:
                    name = parts[0]
                    
                    # Parse CPU percentage (e.g., "5.10%")
                    cpu_perc = float(parts[1].strip('%')) if parts[1] else 0
                    
                    # Parse memory usage (e.g., "1.2GiB / 15.5GiB")
                    mem_parts = parts[2].split(' / ')
                    mem_used = self._parse_size(mem_parts[0]) if len(mem_parts) > 0 else 0
                    mem_limit = self._parse_size(mem_parts[1]) if len(mem_parts) > 1 else 0
                    
                    # Parse network I/O (e.g., "648B / 648B")
                    net_parts = parts[3].split(' / ')
                    net_in = self._parse_size(net_parts[0]) if len(net_parts) > 0 else 0
                    net_out = self._parse_size(net_parts[1]) if len(net_parts) > 1 else 0
                    
                    # Parse block I/O (e.g., "0B / 0B")
                    io_parts = parts[4].split(' / ')
                    io_read = self._parse_size(io_parts[0]) if len(io_parts) > 0 else 0
                    io_write = self._parse_size(io_parts[1]) if len(io_parts) > 1 else 0
                    
                    new_containers[name] = {
                        'cpu_percent': cpu_perc,
                        'memory_used_bytes': mem_used,
                        'memory_limit_bytes': mem_limit,
                        'memory_percent': (mem_used / mem_limit * 100) if mem_limit > 0 else 0,
                        'network_in_bytes': net_in,
                        'network_out_bytes': net_out,
                        'io_read_bytes': io_read,
                        'io_write_bytes': io_write
                    }
            
            self.containers = new_containers
        except subprocess.SubprocessError:
            pass
    
    def _parse_size(self, size_str: str) -> float:
        \"\"\"Parse size string to bytes.\"\"\"
        if not size_str:
            return 0
            
        size_str = size_str.strip()
        
        # Handle empty input
        if not size_str or size_str == 'N/A':
            return 0
        
        # Extract value and unit
        units = {'B': 1, 'KiB': 1024, 'MiB': 1024**2, 'GiB': 1024**3, 'TiB': 1024**4,
                'KB': 1000, 'MB': 1000**2, 'GB': 1000**3, 'TB': 1000**4}
                
        # Extract number and unit
        for unit, multiplier in units.items():
            if size_str.endswith(unit):
                try:
                    value = float(size_str[:-len(unit)])
                    return value * multiplier
                except ValueError:
                    return 0
        
        # If no unit found, try parsing as a plain number
        try:
            return float(size_str)
        except ValueError:
            return 0
    
    def get_summary(self) -> Dict[str, Dict[str, float]]:
        \"\"\"Get current Docker container metrics summary.\"\"\"
        if not self.available:
            return {}
        
        return self.containers

class DiagnosticTool:
    \"\"\"Main diagnostic tool class.\"\"\"
    
    def __init__(self, interval: int = 5, graphical: bool = False):
        self.interval = interval
        self.graphical = graphical and HAS_MATPLOTLIB
        
        self.system_monitor = SystemMonitor()
        self.gpu_monitor = GPUMonitor()
        self.docker_monitor = DockerMonitor()
        
        self.start_time = datetime.now()
        self.update_count = 0
        
        if self.graphical:
            self._setup_gui()
    
    def _setup_gui(self):
        \"\"\"Set up graphical interface using matplotlib.\"\"\"
        if not HAS_MATPLOTLIB:
            logger.warning("Matplotlib not available, falling back to text mode")
            self.graphical = False
            return
        
        plt.ion()  # Enable interactive mode
        self.fig, self.axs = plt.subplots(3, 1, figsize=(10, 8))
        self.fig.suptitle('AI Research Environment Diagnostics')
        
        # CPU, Memory, Disk
        self.axs[0].set_title('System Resources')
        self.axs[0].set_ylim(0, 100)
        self.axs[0].set_ylabel('Percentage')
        self.cpu_line, = self.axs[0].plot([], [], label='CPU')
        self.mem_line, = self.axs[0].plot([], [], label='Memory')
        self.disk_line, = self.axs[0].plot([], [], label='Disk')
        self.axs[0].legend()
        
        # Network
        self.axs[1].set_title('Network I/O')
        self.axs[1].set_ylabel('Bytes/sec')
        self.net_in_line, = self.axs[1].plot([], [], label='In')
        self.net_out_line, = self.axs[1].plot([], [], label='Out')
        self.axs[1].legend()
        
        # GPU(s)
        if self.gpu_monitor.available:
            self.axs[2].set_title('GPU Utilization')
            self.axs[2].set_ylim(0, 100)
            self.axs[2].set_ylabel('Percentage')
            self.gpu_lines = []
            for i in range(self.gpu_monitor.gpu_count):
                line, = self.axs[2].plot([], [], label=f'GPU {i}')
                self.gpu_lines.append(line)
            self.axs[2].legend()
        else:
            self.axs[2].set_title('No GPU Detected')
            self.axs[2].set_visible(False)
        
        self.x_data = list(range(self.system_monitor.history_length))
        plt.tight_layout()
    
    def update_gui(self):
        \"\"\"Update the graphical interface.\"\"\"
        if not self.graphical:
            return
        
        # Update CPU, Memory, Disk lines
        self.cpu_line.set_data(self.x_data, self.system_monitor.cpu_percent)
        self.mem_line.set_data(self.x_data, self.system_monitor.memory_percent)
        self.disk_line.set_data(self.x_data, self.system_monitor.disk_percent)
        
        # Update Network lines
        self.net_in_line.set_data(self.x_data, self.system_monitor.network_recv)
        self.net_out_line.set_data(self.x_data, self.system_monitor.network_sent)
        
        # Adjust y-axis limits for network
        max_net = max(max(self.system_monitor.network_recv), max(self.system_monitor.network_sent))
        self.axs[1].set_ylim(0, max_net * 1.1 or 1000)
        
        # Update GPU lines
        if self.gpu_monitor.available:
            for i, line in enumerate(self.gpu_lines):
                line.set_data(self.x_data, self.gpu_monitor.utilization[i])
        
        # Redraw
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def update(self):
        \"\"\"Update all monitors.\"\"\"
        self.system_monitor.update()
        self.gpu_monitor.update()
        self.docker_monitor.update()
        self.update_count += 1
        
        if self.graphical:
            self.update_gui()
    
    def print_summary(self):
        \"\"\"Print a summary of current metrics.\"\"\"
        os.system('cls' if platform.system() == 'Windows' else 'clear')
        
        runtime = datetime.now() - self.start_time
        hours, remainder = divmod(runtime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        print(f"=== AI Research Environment Diagnostics ===")
        print(f"Runtime: {hours:02}:{minutes:02}:{seconds:02}, Updates: {self.update_count}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # System Resources
        system = self.system_monitor.get_summary()
        print(f"=== System Resources ===")
        print(f"CPU Usage: {system['cpu_percent']:.1f}%")
        print(f"Memory Usage: {system['memory_percent']:.1f}%")
        print(f"Disk Usage: {system['disk_percent']:.1f}%")
        print(f"Network: ↑ {self._format_bytes(system['network_sent_bytes'])}/s, ↓ {self._format_bytes(system['network_recv_bytes'])}/s")
        print()
        
        # GPU Resources
        if self.gpu_monitor.available:
            gpus = self.gpu_monitor.get_summary()
            print(f"=== GPU Resources ({len(gpus)} detected) ===")
            for gpu in gpus:
                print(f"GPU {gpu['index']}: {gpu['utilization_percent']:.1f}% util, {gpu['memory_percent']:.1f}% mem, {gpu['temperature_c']:.1f}°C")
            print()
        
        # Docker Containers
        containers = self.docker_monitor.get_summary()
        if containers:
            print(f"=== Docker Containers ({len(containers)} running) ===")
            for name, stats in containers.items():
                print(f"{name}: {stats['cpu_percent']:.1f}% CPU, {stats['memory_percent']:.1f}% MEM")
                print(f"  I/O: ↑ {self._format_bytes(stats['network_out_bytes'])}/s, ↓ {self._format_bytes(stats['network_in_bytes'])}/s")
            print()
        
        print("Press Ctrl+C to exit.")
    
    def _format_bytes(self, bytes_val: float) -> str:
        \"\"\"Format bytes to human-readable format.\"\"\"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f}{unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f}PB"
    
    def run(self):
        \"\"\"Run the diagnostic tool.\"\"\"
        try:
            while True:
                self.update()
                if not self.graphical:
                    self.print_summary()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\nDiagnostic tool stopped.")

def parse_args():
    \"\"\"Parse command line arguments.\"\"\"
    parser = argparse.ArgumentParser(description='AI Research Environment Diagnostic Tool')
    parser.add_argument('--interval', '-i', type=int, default=2, help='Update interval in seconds')
    parser.add_argument('--text', '-t', action='store_true', help='Force text mode (no graphics)')
    parser.add_argument('--log', '-l', action='store_true', help='Log output to file')
    return parser.parse_args()

def main():
    \"\"\"Main entry point.\"\"\"
    args = parse_args()
    
    if args.log:
        # Add file handler for logging
        log_file = f"diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        logger.info(f"Logging to {log_file}")
    
    graphical = not args.text and HAS_MATPLOTLIB
    
    logger.info(f"Starting diagnostic tool with {args.interval}s interval")
    if not graphical and not args.text and HAS_MATPLOTLIB:
        logger.info("Using graphical mode")
    elif args.text:
        logger.info("Using text mode (forced)")
    else:
        logger.info("Using text mode (matplotlib not available)")
    
    diagnostic = DiagnosticTool(interval=args.interval, graphical=graphical)
    diagnostic.run()

if __name__ == "__main__":
    main()
""")
    
    # Make the file executable
    make_executable(diagnostic_path)
    logger.info(f"Created diagnostic tool at {diagnostic_path}")


def main() -> None:
    """Main entry point for the setup script."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Configure logging
    set_log_level(args.verbose)
    
    logger.info("Starting AI Research Environment setup...")
    
    # Check prerequisites
    if not check_prerequisites():
        logger.error("Prerequisites check failed. Please address the issues above.")
        sys.exit(1)
    
    # Detect GPU
    use_gpu = detect_gpu(force_gpu=args.gpu, disable_gpu=args.no_gpu)
    
    # Create directory structure
    ensure_directory_structure(args.docker_dir)
    
    # Run requested components
    if args.all or args.python:
        install_python_dependencies()
    
    if args.all or args.docker:
        setup_docker_environment(args.docker_dir, use_gpu)
    
    if args.all or args.monitoring:
        setup_monitoring_stack()
    
    # Create diagnostic tool
    create_utils_diagnostic_tool()
    
    # Clean up unnecessary files
    cleanup_unnecessary_files(args)
    
    logger.info("Setup completed successfully!")
    
    # Print next steps
    print("\n=== Next Steps ===")
    print(f"1. Run the Docker environment: python start_environment.py")
    print(f"2. Access JupyterLab: http://localhost:8888")
    print(f"3. Run diagnostics: python utils/diagnostic_tool.py")
    print(f"4. For more information, see the documentation in the docs/ directory")


if __name__ == "__main__":
    main()
