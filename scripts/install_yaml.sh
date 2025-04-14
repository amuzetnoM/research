#!/bin/bash

echo "Installing dependencies..."
# Install shellcheck if not already installed
if ! command -v shellcheck &> /dev/null; then
    echo "Installing shellcheck..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y shellcheck
    elif command -v brew &> /dev/null; then
        brew install shellcheck
    else
        echo "Could not install shellcheck automatically. Please install it manually."
        exit 1
    fi
fi

echo "Installing YAML tools..."
# Install PyYAML (Python YAML library)
pip install pyyaml

# Install yamllint for YAML validation
pip install yamllint

echo "YAML installation completed successfully!"
echo "You can now use YAML tools in your environment."
