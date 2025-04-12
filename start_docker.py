#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import time
import argparse
from typing import Optional, List, Dict, Any

class DockerRunner:
    """A class to manage Docker container initialization and execution."""
    
    def __init__(self, image_name: str = "ml-environment", 
                 container_name: str = "ml-container",
                 dockerfile_path: str = "./Dockerfile",
                 requirements_path: str = "./setup/requirements.txt",
                 docker_compose_path: str = "./docker-compose.yml",
                 use_gpu: Optional[bool] = None,
                 ports: Dict[str, str] = None,
                 volumes: Dict[str, str] = None,
                 command: str = None):
        """Initialize Docker runner with configuration settings."""
        self.image_name = image_name
        self.container_name = container_name
        self.dockerfile_path = dockerfile_path
        self.requirements_path = requirements_path
        self.docker_compose_path = docker_compose_path
        self.use_gpu = use_gpu if use_gpu is not None else self._check_gpu_availability()
        self.ports = ports or {"8888": "8888", "6006": "6006"}
        self.volumes = volumes or {os.getcwd(): "/app"}
        self.command = command
        
        # Ensure all helper scripts are executable
        self._ensure_scripts_executable()
    
    def _ensure_scripts_executable(self):
        """Make sure all necessary scripts are executable."""
        # Only maintain essential scripts, remove run.sh from the list
        scripts = ["entrypoint.sh", "gpu_check.py"]
        for script in scripts:
            script_path = os.path.join(os.getcwd(), script)
            if os.path.exists(script_path):
                try:
                    current_mode = os.stat(script_path).st_mode
                    os.chmod(script_path, current_mode | 0o755)
                    print(f"Made {script} executable")
                except Exception as e:
                    print(f"Warning: Could not make {script} executable: {e}")
            else:
                print(f"Creating script: {script}")
                self._create_script(script)
        
        # Remove run.sh if it exists (cleanup)
        run_sh_path = os.path.join(os.getcwd(), "run.sh")
        if os.path.exists(run_sh_path):
            try:
                os.remove(run_sh_path)
                print("Removed redundant run.sh script")
            except Exception as e:
                print(f"Warning: Could not remove run.sh: {e}")
    
    def _create_script(self, script_name: str):
        """Create a script file if it doesn't exist."""
        if script_name == "entrypoint.sh":
            content = """#!/bin/bash

# Check for GPU availability
python3 /app/gpu_check.py
HAS_GPU=$?

if [ $HAS_GPU -eq 0 ]; then
    echo "GPU is available. Running with GPU acceleration."
    export USE_GPU=1
else
    echo "No GPU detected. Falling back to CPU."
    export USE_GPU=0
fi

# Execute the command passed to the entrypoint
exec "$@"
"""
        elif script_name == "gpu_check.py":
            content = """#!/usr/bin/env python3

def check_tensorflow_gpu():
    try:
        import tensorflow as tf
        gpus = tf.config.list_physical_devices('GPU')
        return len(gpus) > 0
    except:
        return False

def check_pytorch_gpu():
    try:
        import torch
        return torch.cuda.is_available()
    except:
        return False

if __name__ == "__main__":
    # Check if either framework detects a GPU
    has_gpu = check_tensorflow_gpu() or check_pytorch_gpu()
    # Return 0 for success (GPU available), 1 for failure (no GPU)
    exit(0 if has_gpu else 1)
"""
        
        # Write the content to the file
        script_path = os.path.join(os.getcwd(), script_name)
        with open(script_path, "w") as f:
            f.write(content)
        
        # Make the file executable
        os.chmod(script_path, 0o755)
        print(f"Created and made executable: {script_name}")
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU is available on the system."""
        # Check using NVIDIA SMI
        if platform.system() in ["Linux", "Windows"]:
            try:
                result = subprocess.run(["nvidia-smi"], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE)
                return result.returncode == 0
            except FileNotFoundError:
                pass
        
        # Try using python libraries if installed
        try:
            import torch
            if torch.cuda.is_available():
                return True
        except (ImportError, ModuleNotFoundError):
            pass
        
        try:
            import tensorflow as tf
            gpus = tf.config.list_physical_devices('GPU')
            return len(gpus) > 0
        except (ImportError, ModuleNotFoundError):
            pass
        
        return False
    
    def check_docker_installation(self) -> bool:
        """Check if Docker is installed."""
        try:
            subprocess.run(["docker", "--version"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          check=True)
            print("Docker is installed.")
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Docker not found. Please install Docker to use container features.")
            print("Visit https://www.docker.com/products/docker-desktop for installation instructions.")
            return False
    
    def check_nvidia_docker(self) -> bool:
        """Check if NVIDIA Docker support is available."""
        if not self.use_gpu:
            return True  # No need for NVIDIA Docker if not using GPU
        
        try:
            docker_info = subprocess.run(["docker", "info"], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE, 
                                       text=True)
            if "nvidia" in docker_info.stdout.lower():
                print("NVIDIA Docker support is available.")
                return True
            else:
                print("Warning: NVIDIA Docker support not detected. GPU features may not work.")
                print("Visit https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html")
                return False
        except subprocess.SubprocessError:
            print("Could not check Docker for NVIDIA support.")
            return False
    
    def create_dockerfile_if_missing(self):
        """Create a Dockerfile if it doesn't exist."""
        if not os.path.exists(self.dockerfile_path):
            print(f"Creating Dockerfile at {self.dockerfile_path}")
            
            # Determine the base image based on GPU availability
            base_image = "nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04" if self.use_gpu else "ubuntu:22.04"
            
            dockerfile_content = f"""FROM {base_image}

# Set environment variables
ENV PYTHONUNBUFFERED=1 \\
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    python3.10 \\
    python3-pip \\
    python3-dev \\
    build-essential \\
    git \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
RUN ln -sf /usr/bin/python3.10 /usr/bin/python && \\
    ln -sf /usr/bin/python3.10 /usr/bin/python3

# Set up working directory
WORKDIR /app

# Copy requirements file
COPY {os.path.relpath(self.requirements_path, os.path.dirname(self.dockerfile_path))} .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r {os.path.basename(self.requirements_path)}

# Copy the rest of the application
COPY . .

# Set the entry point
ENTRYPOINT ["/app/entrypoint.sh"]
"""
            
            with open(self.dockerfile_path, "w") as f:
                f.write(dockerfile_content)
    
    def create_docker_compose_if_missing(self):
        """Create a docker-compose.yml file if it doesn't exist."""
        if not os.path.exists(self.docker_compose_path):
            print(f"Creating docker-compose.yml at {self.docker_compose_path}")
            
            # Prepare ports and volumes for docker-compose format
            ports_str = "\n      - ".join([f'"{host}:{container}"' for host, container in self.ports.items()])
            volumes_str = "\n      - ".join([f'"{host}:{container}"' for host, container in self.volumes.items()])
            
            # Determine if GPU configuration should be included
            gpu_config = """
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    environment:
      - NVIDIA_VISIBLE_DEVICES=all""" if self.use_gpu else ""
            
            compose_content = f"""version: '3.8'

services:
  ml-app:
    build:
      context: .
      dockerfile: {os.path.basename(self.dockerfile_path)}
    container_name: {self.container_name}
    volumes:
      - {volumes_str}
    ports:
      - {ports_str}{gpu_config}
    command: {self.command or 'jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token="" --NotebookApp.password=""'}
"""
            
            with open(self.docker_compose_path, "w") as f:
                f.write(compose_content)
    
    def build_image(self) -> bool:
        """Build the Docker image."""
        print(f"Building Docker image: {self.image_name}")
        try:
            subprocess.run(["docker", "build", "-t", self.image_name, "-f", self.dockerfile_path, "."], 
                          check=True)
            print(f"Successfully built image: {self.image_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error building Docker image: {e}")
            return False
    
    def run_container(self) -> bool:
        """Run the Docker container."""
        # Check if docker-compose exists and docker-compose.yml is available
        has_docker_compose = os.path.exists(self.docker_compose_path)
        try:
            subprocess.run(["docker-compose", "--version"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          check=True)
            
            if has_docker_compose:
                print("Starting container with docker-compose...")
                subprocess.run(["docker-compose", "-f", self.docker_compose_path, "up", "--build"], 
                              check=True)
                return True
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Docker Compose not available, falling back to docker command...")
        
        # Fall back to docker run command if docker-compose is not available
        print(f"Starting container: {self.container_name}")
        
        # Prepare docker run command arguments
        run_args = [
            "docker", "run", "-it", "--rm",
            "--name", self.container_name
        ]
        
        # Add port mappings
        for host_port, container_port in self.ports.items():
            run_args.extend(["-p", f"{host_port}:{container_port}"])
        
        # Add volume mappings
        for host_path, container_path in self.volumes.items():
            run_args.extend(["-v", f"{host_path}:{container_path}"])
        
        # Add GPU support if available
        if self.use_gpu:
            run_args.extend(["--gpus", "all"])
        
        # Add image name and command
        run_args.append(self.image_name)
        if self.command:
            run_args.extend(self.command.split())
        
        try:
            print(f"Running container with command: {' '.join(run_args)}")
            subprocess.run(run_args, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error running Docker container: {e}")
            return False
    
    def init_and_run(self) -> bool:
        """Initialize and run the Docker container."""
        # Check dependencies
        if not self.check_docker_installation():
            return False
        
        if self.use_gpu and not self.check_nvidia_docker():
            print("Warning: Continuing without GPU support.")
            self.use_gpu = False
        
        # Create necessary files
        self.create_dockerfile_if_missing()
        self.create_docker_compose_if_missing()
        
        # Build and run
        if self.build_image():
            return self.run_container()
        return False


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Start ML Docker environment")
    parser.add_argument("--image", type=str, default="ml-environment",
                        help="Docker image name")
    parser.add_argument("--container", type=str, default="ml-container",
                        help="Docker container name")
    parser.add_argument("--no-gpu", action="store_false", dest="use_gpu",
                        help="Disable GPU support")
    parser.add_argument("--port", action="append", default=[],
                        help="Port mapping in format HOST:CONTAINER (can be used multiple times)")
    parser.add_argument("--volume", action="append", default=[],
                        help="Volume mapping in format HOST:CONTAINER (can be used multiple times)")
    parser.add_argument("--command", type=str, 
                        default="jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''",
                        help="Command to run in the container")
    
    return parser.parse_args()


if __name__ == "__main__":
    print("ML Docker Environment Starter")
    print("=============================")
    
    args = parse_arguments()
    
    # Process port and volume mappings
    ports = {"8888": "8888", "6006": "6006"}  # Default ports
    for port_mapping in args.port:
        host, container = port_mapping.split(":")
        ports[host] = container
    
    volumes = {os.getcwd(): "/app"}  # Default volume
    for volume_mapping in args.volume:
        host, container = volume_mapping.split(":")
        volumes[host] = container
    
    # Initialize and run Docker
    runner = DockerRunner(
        image_name=args.image,
        container_name=args.container,
        use_gpu=args.use_gpu,
        ports=ports,
        volumes=volumes,
        command=args.command
    )
    
    success = runner.init_and_run()
    
    if success:
        print("Docker container started successfully!")
    else:
        print("Failed to start Docker container. Check the logs above for details.")
        sys.exit(1)
