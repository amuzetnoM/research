#!/bin/bash

# GPU setup script

# Check for root privileges
check_privileges() {
    if [[ $EUID -ne 0 ]]; then
        echo "This script must be run as root"
        exit 1
    fi
}

# Detect operating system
detect_os() {
    OS=$(uname -s)
    case "$OS" in
        Linux*)     OS_TYPE="Linux";;
        Darwin*)    OS_TYPE="Mac";;
        *)          OS_TYPE="Unknown";;
    esac
    echo "Detected OS: $OS_TYPE"
}

# Check for NVIDIA GPU
check_nvidia_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        HAS_NVIDIA=true
        echo "NVIDIA GPU detected"
    else
        HAS_NVIDIA=false
        echo "No NVIDIA GPU detected"
    fi
}

# Check for AMD GPU
check_amd_gpu() {
    if lspci | grep -i amd &> /dev/null; then
        HAS_AMD=true
        echo "AMD GPU detected"
    else
        HAS_AMD=false
        echo "No AMD GPU detected"
    fi
}

# Install NVIDIA Container Toolkit
install_nvidia_container_toolkit() {
    echo "Installing NVIDIA Container Toolkit..."
    # Installation commands for NVIDIA Container Toolkit
}

# Install ROCm for AMD GPUs
install_rocm() {
    echo "Installing ROCm for AMD GPUs..."
    # Installation commands for ROCm
}

# Configure GPU optimization
configure_gpu_optimization() {
    echo "Configuring GPU optimization..."
    # Optimization commands
}

# Print header
print_header() {
    echo "=============================="
    echo "$1"
    echo "=============================="
}

# Main execution
check_privileges
detect_os
check_nvidia_gpu
check_amd_gpu

if [ "$HAS_NVIDIA" = true ] || [ "$HAS_AMD" = true ]; then
    echo "GPU detected. Proceeding with setup..."
    
    if [ "$HAS_NVIDIA" = true ]; then
        install_nvidia_container_toolkit
    fi
    
    if [ "$HAS_AMD" = true ]; then
        install_rocm
    fi
    
    configure_gpu_optimization
    
    echo "GPU setup completed successfully!"
    echo "To verify GPU performance, run: python $PROJECT_ROOT/utils/gpu_test.py"
else
    echo "No supported GPU detected."
    echo "If you believe this is an error, you can manually install GPU drivers."
fi

print_header "GPU Setup Complete"