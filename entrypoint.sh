#!/bin/bash

# Make script executable
chmod +x $(dirname $0)/gpu_check.py

# Check for GPU availability
HAS_GPU=$(python3 $(dirname $0)/gpu_check.py)

if [ "$HAS_GPU" = "True" ]; then
    echo "GPU is available. Running with GPU acceleration."
    export USE_GPU=1
else
    echo "No GPU detected. Falling back to CPU."
    export USE_GPU=0
fi

# Execute the command passed to the entrypoint
exec "$@"
