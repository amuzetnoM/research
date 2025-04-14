#!/bin/bash

# Test the installation by running a base CUDA container
docker run --rm --gpus all nvidia/cuda:11.6.2-base-ubuntu20.04 nvidia-smi

# If you see GPU information displayed, the setup is working correctly
echo "If you see GPU information above, your NVIDIA Container Toolkit is working correctly."
