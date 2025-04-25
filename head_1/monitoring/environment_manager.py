#!/usr/bin/env python3
"""
Environment Manager for AI Research Environment

This is the unified entry point for managing the research environment.
It handles container creation, configuration, and orchestration,
along with monitoring setup and GPU configuration.

Usage:
    python environment_manager.py [options]

Options:
    --stop              Stop running containers
    --enable-monitoring Enable monitoring stack (Prometheus + Grafana)
    --no-monitoring     Disable monitoring stack
    --gpu               Force GPU support
    --no-gpu            Disable GPU support
    --port PORT         Set container port mapping (format: host:container)
    --jupyter-token TOKEN  Set Jupyter token
    --mem-limit LIMIT   Set memory limit (format: 16g, 1024m, etc.)
    --cpu-limit LIMIT   Set CPU limit
    --grafana-user USER Set Grafana admin username
    --grafana-password PASS Set Grafana admin password
    --reset-monitoring  Reset monitoring configuration
    --enable-temporal-locationing Enable temporal locationing framework
    --enable-social-dimensionality Enable social dimensionality framework
"""

import argparse
import json
import logging
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('environment.log')
    ]
)
logger = logging.getLogger('environment')

# Import utility modules with fallback to direct path import
try:
    from utils.gpu_utils import gpu_manager
    from utils.system_utils import system_manager
except ImportError:
    # Add parent directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from utils.gpu_utils import gpu_manager
        from utils.system_utils import system_manager
    except ImportError:
        logger.error("Could not import utility modules. Make sure the utils directory exists with required modules.")
        sys.exit(1)


class EnvironmentManager:
    """
    Comprehensive manager for AI research environments.
    Handles setup, configuration, and startup with proper
    resource allocation and monitoring.
    """
    
    def __init__(self, args):
        """Initialize the environment manager with command line arguments."""
        self.args = args
        self.env_vars = os.environ.copy()
        self.project_root = Path(__file__).resolve().parent
        
        # Store discovered capabilities
        self.capabilities = {
            'gpu_available': False,
            'docker_available': False,
            'docker_compose_available': False,
            'nvidia_docker_available': False
        }
        
        # Check basic prerequisites
        self._check_prerequisites()
    
    def _check_prerequisites(self):
        """Check if all prerequisites are installed."""
        # Check Docker
        try:
            subprocess.run(["docker", "--version"], check=True, 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.capabilities['docker_available'] = True
            logger.info("Docker is available")
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.warning("Docker not found. Please install Docker before continuing.")
            self.capabilities['docker_available'] = False
        
        # Check Docker Compose
        try:
            subprocess.run(["docker-compose", "--version"], check=True, 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.capabilities['docker_compose_available'] = True
            logger.info("Docker Compose is available")
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.warning("Docker Compose not found. Some features may be limited.")
            self.capabilities['docker_compose_available'] = False
        
        # Check GPU capabilities
        self.capabilities['gpu_available'] = not self.args.no_gpu and gpu_manager.check_gpu_availability()
        
        if self.capabilities['gpu_available']:
            logger.info("GPU support is available")
            # Check NVIDIA Docker support
            self.capabilities['nvidia_docker_available'] = gpu_manager.check_docker_gpu_support()
            if not self.capabilities['nvidia_docker_available']:
                logger.warning("NVIDIA Docker support not detected. GPU acceleration may not work in containers.")
        else:
            logger.info("Running in CPU-only mode")
    
    def setup_environment_variables(self):
        """Set up environment variables for Docker containers."""
        # Set Jupyter token
        self.env_vars['JUPYTER_TOKEN'] = self.args.jupyter_token
        
        # Set resource limits
        if self.args.mem_limit:
            self.env_vars['MEMORY_LIMIT'] = self.args.mem_limit
        else:
            # Auto-detect optimal memory based on system
            optimal_memory = system_manager.calculate_optimal_memory()
            self.env_vars['MEMORY_LIMIT'] = optimal_memory
            logger.info(f"Automatically setting memory limit to {optimal_memory}")
        
        if self.args.cpu_limit:
            self.env_vars['CPU_LIMIT'] = self.args.cpu_limit
        else:
            # Auto-detect optimal CPU count
            optimal_cpus = system_manager.calculate_optimal_cpu()
            self.env_vars['CPU_LIMIT'] = str(optimal_cpus)
            logger.info(f"Automatically setting CPU limit to {optimal_cpus} cores")
        
        # GPU settings
        if self.capabilities['gpu_available'] and not self.args.no_gpu:
            self.env_vars['NVIDIA_VISIBLE_DEVICES'] = 'all'
            self.env_vars['ENABLE_GPU'] = 'true'
            
            # Add GPU optimization settings
            gpu_settings = gpu_manager.get_optimal_gpu_settings()
            for key, value in gpu_settings.items():
                self.env_vars[key] = value
            
            logger.info(f"Configured GPU settings with {len(gpu_settings)} optimizations")
        else:
            self.env_vars['NVIDIA_VISIBLE_DEVICES'] = ''
            self.env_vars['ENABLE_GPU'] = 'false'
        
        # Monitoring settings
        if self.args.enable_monitoring and not self.args.no_monitoring:
            self.env_vars['ENABLE_MONITORING'] = 'true'
            self.env_vars['GRAFANA_USER'] = self.args.grafana_user
            self.env_vars['GRAFANA_PASSWORD'] = self.args.grafana_password
        else:
            self.env_vars['ENABLE_MONITORING'] = 'false'
        
        # Temporal locationing settings
        if self.args.enable_temporal_locationing:
            self.env_vars['ENABLE_TEMPORAL_LOCATIONING'] = 'true'
        else:
            self.env_vars['ENABLE_TEMPORAL_LOCATIONING'] = 'false'
        # Social dimensionality settings
        if self.args.enable_social_dimensionality:
            self.env_vars['ENABLE_SOCIAL_DIMENSIONALITY'] = 'true'
        else:
            self.env_vars['ENABLE_SOCIAL_DIMENSIONALITY'] = 'false'
        return self.env_vars
    
    def determine_compose_files(self):
        """Determine which docker-compose files to use."""
        compose_files = []
        
        # Base docker-compose file in head_1 directory
        base_compose = self.project_root / 'head_1' / 'docker-compose.yml'
        if base_compose.exists():
            compose_files.append(str(base_compose))
        else:
            logger.error(f"Base docker-compose file not found at {base_compose}")
            sys.exit(1)
        
        # Add GPU override if available and enabled
        if self.capabilities['gpu_available'] and not self.args.no_gpu:
            gpu_compose = self.project_root / 'head_1' / 'docker-compose.gpu.yml'
            if gpu_compose.exists():
                compose_files.append(str(gpu_compose))
                logger.info("Added GPU configuration override")
            else:
                # If the GPU override doesn't exist, the base compose file should have GPU configuration
                logger.info("Using GPU configuration from base docker-compose file")
        
        # Add monitoring if enabled
        monitoring_enabled = self.args.enable_monitoring and not self.args.no_monitoring
        if monitoring_enabled:
            monitoring_compose = self.project_root / 'head_1' / 'docker-compose.monitoring.yml'
            if monitoring_compose.exists():
                compose_files.append(str(monitoring_compose))
                logger.info("Added monitoring configuration override")
            else:
                # If the monitoring compose doesn't exist, the base should have it
                logger.info("Using monitoring configuration from base docker-compose file")
        
        return compose_files
    
    def ensure_docker_files(self):
        """Ensure required Docker files exist and are properly configured."""
        # Check if Dockerfile exists
        dockerfile_path = self.project_root / 'head_1' / 'Dockerfile'
        if not dockerfile_path.exists():
            logger.error(f"Dockerfile not found at {dockerfile_path}")
            sys.exit(1)
        
        # Check if docker-compose.yml exists
        compose_path = self.project_root / 'head_1' / 'docker-compose.yml'
        if not compose_path.exists():
            logger.error(f"docker-compose.yml not found at {compose_path}")
            sys.exit(1)
        
        # Ensure entrypoint.sh is executable
        entrypoint_path = self.project_root / 'entrypoint.sh'
        if entrypoint_path.exists():
            try:
                current_mode = os.stat(entrypoint_path).st_mode
                os.chmod(entrypoint_path, current_mode | 0o755)
                logger.debug("Ensured entrypoint.sh is executable")
            except Exception as e:
                logger.warning(f"Could not make entrypoint.sh executable: {e}")
        else:
            logger.warning("entrypoint.sh not found, Docker containers may not start correctly")
    
    def start_environment(self, compose_files):
        """Start the Docker environment."""
        # Prepare docker-compose command
        docker_compose_cmd = ['docker-compose']
        for file in compose_files:
            docker_compose_cmd.extend(['-f', file])
        
        # Build containers if requested
        if self.args.build:
            logger.info("Building containers...")
            build_cmd = docker_compose_cmd + ['build', '--pull']
            if self.args.no_cache:
                build_cmd.append('--no-cache')
            
            try:
                subprocess.run(build_cmd, env=self.env_vars, check=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to build containers: {e}")
                sys.exit(1)
        
        # Start the environment
        try:
            logger.info("Starting the research environment...")
            up_cmd = docker_compose_cmd + ['up', '-d']
            subprocess.run(up_cmd, env=self.env_vars, check=True)
            
            # Wait for services to be ready
            logger.info("Waiting for services to be ready...")
            time.sleep(5)
            
            # Check if containers are running
            ps_cmd = docker_compose_cmd + ['ps']
            ps_result = subprocess.run(ps_cmd, env=self.env_vars, 
                                     check=True, stdout=subprocess.PIPE, text=True)
            
            if "Exit" in ps_result.stdout or "Exited" in ps_result.stdout:
                logger.warning("Some containers may have exited. Check logs for details.")
                
                # Show logs for troubleshooting
                logs_cmd = docker_compose_cmd + ['logs']
                subprocess.run(logs_cmd, env=self.env_vars, check=False)
            
            # Print access information
            port = self.args.port.split(':')[0] if self.args.port else '8888'
            monitor_port = self.args.monitor_port if self.args.monitor_port else '3000'
            
            logger.info("\n" + "="*50)
            logger.info("AI Research Environment is running!")
            logger.info(f"JupyterLab: http://localhost:{port}")
            logger.info("  Authentication token: " + self.args.jupyter_token)
            logger.info("TensorBoard: http://localhost:6006")
            
            if self.args.enable_monitoring and not self.args.no_monitoring:
                logger.info(f"Monitoring Dashboard: http://localhost:{monitor_port}")
                logger.info(f"  Username: {self.args.grafana_user}")
                logger.info(f"  Password: {self.args.grafana_password}")
            
            logger.info("="*50)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start the environment: {e}")
            logger.info("Cleaning up...")
            down_cmd = docker_compose_cmd + ['down']
            subprocess.run(down_cmd, env=self.env_vars)
            sys.exit(1)
    
    def stop_environment(self, compose_files):
        """Stop the Docker environment."""
        # Prepare docker-compose command
        docker_compose_cmd = ['docker-compose']
        for file in compose_files:
            docker_compose_cmd.extend(['-f', file])
        
        try:
            logger.info("Stopping the research environment...")
            down_cmd = docker_compose_cmd + ['down']
            if self.args.volumes:
                down_cmd.append('-v')
            
            subprocess.run(down_cmd, env=self.env_vars, check=True)
            logger.info("Research environment has been stopped.")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop the environment: {e}")
            sys.exit(1)
    
    def run(self):
        """Run the environment manager."""
        # Only proceed if Docker is available
        if not self.capabilities['docker_available']:
            logger.error("Docker is required but not available. Please install Docker and try again.")
            sys.exit(1)
        
        # Validate that Docker Compose is available for our use case
        if not self.capabilities['docker_compose_available']:
            logger.error("Docker Compose is required but not available. Please install Docker Compose and try again.")
            sys.exit(1)
        
        # Setup environment variables
        self.setup_environment_variables()
        
        # Determine compose files
        compose_files = self.determine_compose_files()
        logger.debug(f"Using compose files: {compose_files}")
        
        # Ensure Docker files exist and are configured
        self.ensure_docker_files()
        
        # Perform the requested action
        if self.args.stop:
            self.stop_environment(compose_files)
        else:
            # Start the environment
            self.start_environment(compose_files)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='AI Research Environment Manager',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Action group
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument('--start', action='store_true', default=True,
                            help='Start the research environment (default)')
    action_group.add_argument('--stop', action='store_true',
                            help='Stop the research environment')
    
    # Container configuration
    container_group = parser.add_argument_group('Container Configuration')
    container_group.add_argument('--port', default='8888:8888',
                                help='Port mapping for JupyterLab (host:container)')
    container_group.add_argument('--mem-limit', default=None,
                                help='Memory limit (e.g., 16g, auto-detected if not specified)')
    container_group.add_argument('--cpu-limit', default=None,
                                help='CPU limit (e.g., 4, auto-detected if not specified)')
    container_group.add_argument('--volume', action='append', default=[],
                                help='Additional volumes to mount (host:container)')
    container_group.add_argument('--jupyter-token', default='researchenv',
                                help='Jupyter token for authentication')
    
    # GPU settings
    gpu_group = parser.add_argument_group('GPU Configuration')
    gpu_group.add_argument('--no-gpu', action='store_true',
                          help='Disable GPU usage even if available')
    
    # Monitoring configuration
    monitoring_group = parser.add_argument_group('Monitoring Configuration')
    monitoring_group.add_argument('--enable-monitoring', action='store_true',
                                help='Enable monitoring services (Prometheus, Grafana)')
    monitoring_group.add_argument('--no-monitoring', action='store_true',
                                help='Disable monitoring services')
    monitoring_group.add_argument('--monitor-port', default='3000',
                                help='Port for Grafana monitoring dashboard')
    monitoring_group.add_argument('--grafana-user', default='admin',
                                help='Username for Grafana')
    monitoring_group.add_argument('--grafana-password', default='admin',
                                help='Password for Grafana')
    
    # Framework settings
    framework_group = parser.add_argument_group('Framework Configuration')
    framework_group.add_argument('--enable-temporal-locationing', action='store_true', help='Enable temporal locationing framework')
    framework_group.add_argument('--enable-social-dimensionality', action='store_true', help='Enable social dimensionality framework')

    # Development options
    dev_group = parser.add_argument_group('Development Options')
    dev_group.add_argument('--build', action='store_true',
                          help='Rebuild containers before starting')
    dev_group.add_argument('--no-cache', action='store_true',
                          help='Do not use cache when building images')
    dev_group.add_argument('--volumes', action='store_true',
                          help='Remove volumes when stopping')
    dev_group.add_argument('--debug', action='store_true',
                          help='Enable debug logging')
    
    return parser.parse_args()


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_arguments()
    
    # Set up logging level
    if args.debug:
        logger.setLevel(logging.DEBUG)
        # Also set debug for imported utilities
        logging.getLogger('environment.gpu').setLevel(logging.DEBUG)
        logging.getLogger('environment.system').setLevel(logging.DEBUG)
    
    try:
        # Create and run the environment manager
        manager = EnvironmentManager(args)
        manager.run()
        
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()