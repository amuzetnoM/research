#!/bin/bash
set -e

# Enhanced entrypoint script for Research Environment
# Integrates with consolidated Python utilities for optimal resource management

# Enable error handling
handle_error() {
  local exit_code=$?
  echo "Error occurred (exit code: $exit_code) at line $1"
  
  # Send error notification if configured
  if [[ -n "$NOTIFY_ON_ERROR" ]]; then
    curl -s -X POST "$NOTIFY_ON_ERROR" \
      -H "Content-Type: application/json" \
      -d "{\"error\": \"Container error\", \"exit_code\": $exit_code, \"container\": \"$HOSTNAME\"}" || true
  fi
  
  # Run Python diagnostics if available
  if command -v python3 &> /dev/null; then
    echo "Running diagnostics..."
    python3 -c "
try:
    from utils.diagnostics import run_diagnostics
    run_diagnostics()
except ImportError:
    import os, psutil, platform
    print(f'Platform: {platform.platform()}')
    print(f'Memory: {psutil.virtual_memory().percent}% used')
    print(f'Disk: {psutil.disk_usage(\"/\").percent}% used')
    print(f'CPU: {psutil.cpu_percent()}% used')
" || true
  fi
  
  # Log additional diagnostics
  echo "=== Error Diagnostics ==="
  echo "Memory Status:"
  free -h || true
  echo "Disk Status:"
  df -h || true
  echo "Process Status:"
  ps aux --sort=-%mem | head -10 || true
  echo "======================="
  
  # Exit with the original error code unless NOEXIT is set
  if [[ -z "$NOEXIT" ]]; then
    exit $exit_code
  fi
}

trap 'handle_error $LINENO' ERR

# Use Python utilities to configure resources if available
if python3 -c "import sys; sys.exit(0 if __import__('os').path.exists('/app/utils/system_utils.py') else 1)" 2>/dev/null; then
  echo "Using Python utilities for resource configuration"
  
  # Get optimal memory settings
  if [[ -z "$MEMORY_LIMIT" ]]; then
    export MEMORY_LIMIT=$(python3 -c "from utils.system_utils import system_manager; print(system_manager.calculate_optimal_memory())")
    echo "Auto-detected optimal memory limit: $MEMORY_LIMIT"
  fi
  
  # Get optimal thread settings
  if [[ -z "$NUM_THREADS" ]]; then
    export NUM_THREADS=$(python3 -c "from utils.system_utils import system_manager; print(system_manager.calculate_optimal_cpu())")
    echo "Auto-detected optimal thread count: $NUM_THREADS"
  fi
  
  # Apply environment variable optimizations
  eval $(python3 -c "
import json
from utils.system_utils import system_manager
env_vars = system_manager.get_environment_variables()
for key, value in env_vars.items():
    print(f'export {key}=\"{value}\"')
")
  
  # Check GPU and configure settings
  if python3 -c "from utils.gpu_utils import gpu_manager; import sys; sys.exit(0 if gpu_manager.check_gpu_availability() else 1)" 2>/dev/null; then
    echo "GPU detected, applying optimal GPU settings"
    eval $(python3 -c "
import json
from utils.gpu_utils import gpu_manager
env_vars = gpu_manager.get_optimal_gpu_settings()
for key, value in env_vars.items():
    print(f'export {key}=\"{value}\"')
")
    export ENABLE_GPU=true
  else
    echo "No GPU detected or GPU disabled, using CPU-only mode"
    export CUDA_VISIBLE_DEVICES=""
    export TF_DISABLE_GPU=1
    export ENABLE_GPU=false
  fi
  
else
  # Fall back to shell-based configuration if Python utilities aren't available
  echo "Python utilities not available, using shell-based configuration"
  
  # Configure resources based on environment variables
  configure_resources() {
    # Memory limits
    if [[ -n "$MEMORY_LIMIT" ]]; then
      MEMORY_MB=$(echo $MEMORY_LIMIT | sed -e 's/g/*1024/g' -e 's/m//g' | bc)
      echo "Setting memory limit to $MEMORY_LIMIT ($MEMORY_MB MB)"
      
      # Configure JVM memory (if applicable)
      export JAVA_OPTS="-Xms1g -Xmx${MEMORY_MB}m"
      
      # Configure Python memory settings
      export MALLOC_TRIM_THRESHOLD_=65536
      export NPY_MMAP_MAX_LEN=$((MEMORY_MB * 1024 * 1024))
      
      # Configure garbage collection for Python
      export PYTHONMALLOC=malloc
      export PYTHONMALLOCSTATS=${PYTHONMALLOCSTATS:-0}
      
      # Set memory growth for TensorFlow to avoid OOM
      export TF_FORCE_GPU_ALLOW_GROWTH=true
      
      # Configure memory for PyTorch
      PYTORCH_MEM=$((MEMORY_MB / 2))
      export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:${PYTORCH_MEM},garbage_collection_threshold:0.8"
    fi
    
    # CPU limits
    if [[ -n "$NUM_THREADS" ]]; then
      echo "Setting thread limits to $NUM_THREADS"
      export OMP_NUM_THREADS=$NUM_THREADS
      export NUMEXPR_NUM_THREADS=$NUM_THREADS
      export MKL_NUM_THREADS=$NUM_THREADS
      export OPENBLAS_NUM_THREADS=$NUM_THREADS
      export VECLIB_MAXIMUM_THREADS=$NUM_THREADS
      export JULIA_NUM_THREADS=$NUM_THREADS
      
      # Set TensorFlow intra/inter op parallelism
      export TF_INTRA_OP_PARALLELISM_THREADS=$NUM_THREADS
      export TF_INTER_OP_PARALLELISM_THREADS=$((NUM_THREADS / 2 > 0 ? NUM_THREADS / 2 : 1))
    else
      # Auto-detect optimal thread count
      AUTO_THREADS=$(nproc)
      export OMP_NUM_THREADS=$AUTO_THREADS
      export NUMEXPR_NUM_THREADS=$AUTO_THREADS
      export MKL_NUM_THREADS=$AUTO_THREADS
      export OPENBLAS_NUM_THREADS=$AUTO_THREADS
      export VECLIB_MAXIMUM_THREADS=$AUTO_THREADS
      export JULIA_NUM_THREADS=$AUTO_THREADS
      
      # Set TensorFlow intra/inter op parallelism
      export TF_INTRA_OP_PARALLELISM_THREADS=$AUTO_THREADS
      export TF_INTER_OP_PARALLELISM_THREADS=$((AUTO_THREADS / 2 > 0 ? AUTO_THREADS / 2 : 1))
      
      echo "Auto-configured thread settings to $AUTO_THREADS threads"
    fi
  }

  # Check GPU availability and configure settings
  configure_gpu() {
    if command -v nvidia-smi &> /dev/null; then
      echo "NVIDIA GPU detected, configuring for GPU acceleration"
      
      # Get GPU memory size and other details
      GPU_MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -n 1 | tr -d '[:space:]')
      GPU_COUNT=$(nvidia-smi --list-gpus | wc -l)
      
      if [[ -n "$GPU_MEM" ]]; then
        # Calculate memory fraction to avoid OOM
        MEM_FRACTION=$(echo "scale=2; 0.8 * $GPU_MEM / $GPU_MEM" | bc)
        export TF_MEMORY_ALLOCATION=$MEM_FRACTION
        export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:$((GPU_MEM / 2))"
        
        echo "GPU memory: ${GPU_MEM}MB, allocation fraction: $MEM_FRACTION"
        echo "Number of GPUs: $GPU_COUNT"
        
        # Configure cuDNN for better performance
        export CUDNN_LOGINFO_DBG=1
        export CUDNN_LOGDEST_DBG=stdout
        
        # Set PyTorch to use CUDA
        export CUDA_LAUNCH_BLOCKING=0
        export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:$((GPU_MEM / 2)),garbage_collection_threshold:0.8"
        
        # Set TensorFlow memory growth
        export TF_FORCE_GPU_ALLOW_GROWTH=true
        export TF_GPU_THREAD_MODE=gpu_private
        export TF_GPU_THREAD_COUNT=$((GPU_COUNT * 2))
        export TF_ENABLE_AUTO_MIXED_PRECISION=1
        
        # Set JAX GPU configuration if JAX is installed
        export XLA_PYTHON_CLIENT_ALLOCATOR=platform
        export XLA_PYTHON_CLIENT_PREALLOCATE=false
        export XLA_PYTHON_CLIENT_MEM_FRACTION=0.8
        
        export ENABLE_GPU=true
      fi
    else
      echo "No NVIDIA GPU detected, using CPU only"
      export CUDA_VISIBLE_DEVICES=""
      export TF_DISABLE_GPU=1
      export ENABLE_GPU=false
    fi
  }
  
  # Apply shell-based configurations
  configure_resources
  configure_gpu
fi

# Setup monitoring and metrics
setup_monitoring() {
  if [[ "$ENABLE_MONITORING" == "true" ]]; then
    echo "Setting up monitoring agent"
    
    # Start node exporter in background if available
    if command -v node_exporter &> /dev/null; then
      node_exporter --web.listen-address=:9100 &
      echo "Node exporter started on port 9100"
    fi
    
    # Enable PyTorch profiling
    export PYTORCH_PROFILER_ENABLE=1
    
    # Setup TensorFlow profiling
    export TF_PROFILER_ENABLED=1
    
    # Set up prometheus metrics for Python if module available
    if python3 -c "import importlib.util; print(importlib.util.find_spec('prometheus_client') is not None)" 2>/dev/null | grep -q "True"; then
      # Start the prometheus client exporter in background
      python3 -c "
from prometheus_client import start_http_server
import threading
def start_metrics():
    start_http_server(8888)
threading.Thread(target=start_metrics, daemon=True).start()
print('Started Prometheus metrics server on port 8888')
" &
    fi
    
    # Set up periodic memory stats logging
    if [[ "$LOG_MEMORY" == "true" ]]; then
      (while true; do
        echo "[$(date)] Memory usage:" >> /tmp/memory_log.txt
        free -h >> /tmp/memory_log.txt
        sleep 60
      done) &
      echo "Memory usage logging enabled"
    fi
  fi
}

# Optimize disk I/O
optimize_io() {
  # Setup tmpfs for temporary files if memory allows
  if [[ -n "$MEMORY_LIMIT" ]]; then
    MEMORY_MB=$(echo $MEMORY_LIMIT | sed -e 's/g/*1024/g' -e 's/m//g' | bc)
    TMPFS_SIZE=$((MEMORY_MB / 4))
    
    if [[ $TMPFS_SIZE -gt 1024 ]]; then
      echo "Setting up tmpfs with ${TMPFS_SIZE}MB for temporary files"
      mkdir -p /tmp/research
      mount -t tmpfs -o size=${TMPFS_SIZE}m tmpfs /tmp/research 2>/dev/null || true
      export TMPDIR=/tmp/research
      
      # Set up cache directories for commonly used libraries
      mkdir -p /tmp/research/torch_cache
      mkdir -p /tmp/research/huggingface
      mkdir -p /tmp/research/tensorflow
      export TORCH_HOME=/tmp/research/torch_cache
      export TRANSFORMERS_CACHE=/tmp/research/huggingface
      export HF_HOME=/tmp/research/huggingface
      export TENSORFLOW_CACHE=/tmp/research/tensorflow
    fi
  fi
  
  # Optimize I/O scheduling if running as root
  if [[ $EUID -eq 0 ]]; then
    # Try to set I/O scheduler to deadline for better throughput
    for DEVICE in /sys/block/sd*; do
      if [[ -e "$DEVICE/queue/scheduler" ]]; then
        echo "deadline" > "$DEVICE/queue/scheduler" 2>/dev/null || true
      fi
    done
    
    # Adjust readahead buffer
    for DEVICE in /sys/block/sd*; do
      if [[ -e "$DEVICE/queue/read_ahead_kb" ]]; then
        echo "4096" > "$DEVICE/queue/read_ahead_kb" 2>/dev/null || true
      fi
    done
    
    # Adjust swappiness for better performance
    echo 10 > /proc/sys/vm/swappiness 2>/dev/null || true
    
    # Clear caches for a fresh start
    echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true
  fi
}

# Apply remaining optimizations
setup_monitoring
optimize_io

# Print environment summary
echo "=============================================="
echo "AI Research Environment Configuration:"
echo "  - Hostname: $HOSTNAME"
echo "  - Python: $(python --version 2>&1)"
if command -v nvidia-smi &> /dev/null; then
  echo "  - GPU: $(nvidia-smi -L | head -n 1)"
  echo "  - GPU Enabled: ${ENABLE_GPU}"
else
  echo "  - GPU: Not available"
fi
echo "  - CPUs: $(nproc)"
echo "  - Memory Limit: ${MEMORY_LIMIT:-"Not set"}"
echo "  - Thread Limit: ${NUM_THREADS:-"Auto"}"
echo "  - Monitoring: ${ENABLE_MONITORING:-"Disabled"}"
echo "=============================================="

# Start Jupyter if no command provided
if [[ $# -eq 0 || "$1" == "jupyter" ]]; then
  echo "Starting Jupyter Lab..."
  exec jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root \
    --NotebookApp.token="${JUPYTER_TOKEN:-researchenv}" \
    --ServerApp.token="${JUPYTER_TOKEN:-researchenv}"
else
  # Execute provided command
  echo "Executing command: $@"
  exec "$@"
fi
