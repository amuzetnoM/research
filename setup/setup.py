#!/usr/bin/env python3

# This script handles environment setup before any imports
import os
import sys
import subprocess
import platform

# Environment setup section (runs before imports)
def setup_environment():
    print("Setting up environment...")
    
    # Make Docker scripts executable
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scripts = ["entrypoint.sh", "gpu_check.py", "run.sh"]
    for script in scripts:
        script_path = os.path.join(parent_dir, script)
        if os.path.exists(script_path):
            print(f"Making {script} executable...")
            try:
                # Make executable for owner
                os.chmod(script_path, os.stat(script_path).st_mode | 0o755)
            except Exception as e:
                print(f"Warning: Failed to make {script} executable: {e}")
    
    # Check Docker installation
    try:
        subprocess.run(["docker", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("Docker is installed.")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Docker not found. Please install Docker to use container features.")
        print("Visit https://www.docker.com/products/docker-desktop for installation instructions.")
    
    # Check NVIDIA Docker installation if GPU is available
    if is_nvidia_gpu_available():
        print("NVIDIA GPU detected.")
        try:
            # Check if nvidia-docker or nvidia-container-toolkit is available
            docker_info = subprocess.run(["docker", "info"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if "nvidia" not in docker_info.stdout.lower():
                print("NVIDIA Docker support not found. Please install NVIDIA Container Toolkit.")
                print("Visit https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html")
        except subprocess.SubprocessError:
            print("Could not check Docker for NVIDIA support.")

def is_nvidia_gpu_available():
    """Check if NVIDIA GPU is available on the system."""
    if platform.system() == "Linux" or platform.system() == "Windows":
        try:
            nvidia_check = subprocess.run(["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return nvidia_check.returncode == 0
        except FileNotFoundError:
            pass
    return False

def install_dependencies():
    """Install dependencies from requirements.txt."""
    requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    if os.path.exists(requirements_path):
        print(f"Installing dependencies from {requirements_path}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
            print("Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            return False
    else:
        print(f"Requirements file not found: {requirements_path}")
        return False
    return True

# Run setup if executed directly (not during import)
if __name__ == "__main__" and not "install" in sys.argv:
    setup_environment()
    install_dependencies()
    print("Environment setup complete.")
    if len(sys.argv) == 1:  # No arguments provided
        sys.exit(0)

# Now proceed with normal imports for the setup package
from setuptools import setup, find_packages

# Package metadata for installation
setup(
    name="ml-docker-environment",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        line.strip() for line in open(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
        )
    ],
    author="ML Engineer",
    author_email="engineer@example.com",
    description="ML environment with GPU/CPU support in Docker",
    keywords="machine learning, deep learning, docker, gpu",
    python_requires=">=3.8",
    scripts=[
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "entrypoint.sh"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gpu_check.py"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "run.sh"),
    ],
    include_package_data=True,
)

# Post-install message
if __name__ == "__main__" and "install" in sys.argv:
    print("Package installed successfully.")
    print("To build and run the Docker container, use: ./run.sh")
