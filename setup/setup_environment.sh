#!/bin/bash

# Make script executable
chmod +x $(dirname $0)/setup.py

# Set up Python environment
echo "Setting up Python environment..."
python3 $(dirname $0)/setup.py

# Make Docker scripts executable
echo "Making Docker scripts executable..."
chmod +x $(dirname $(dirname $0))/entrypoint.sh
chmod +x $(dirname $(dirname $0))/gpu_check.py
chmod +x $(dirname $(dirname $0))/run.sh

# Check Docker installation
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Would you like to install Docker? (y/n)"
    read install_docker
    if [ "$install_docker" = "y" ]; then
        echo "Installing Docker..."
        if [ "$(uname)" == "Darwin" ]; then
            echo "Please download Docker Desktop for Mac from https://www.docker.com/products/docker-desktop"
        elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            echo "Please log out and log back in to use Docker without sudo."
        fi
    fi
fi

# Check NVIDIA Docker installation if GPU is available
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected."
    if ! command -v nvidia-docker &> /dev/null && ! grep -q "nvidia-container-toolkit" <<< "$(docker info 2>/dev/null)"; then
        echo "NVIDIA Docker support not found. Would you like to install NVIDIA Container Toolkit? (y/n)"
        read install_nvidia
        if [ "$install_nvidia" = "y" ]; then
            echo "Installing NVIDIA Container Toolkit..."
            if [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
                distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
                curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
                curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
                sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
                sudo systemctl restart docker
            else
                echo "Automatic installation not supported for this OS. Please install manually."
            fi
        fi
    else
        echo "NVIDIA Docker support already installed."
    fi
fi

echo "Environment setup complete."
echo "To build and run the Docker container, use: $(dirname $(dirname $0))/run.sh"
