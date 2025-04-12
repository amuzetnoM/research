# Troubleshooting Common Issues

This document provides solutions for common issues you might encounter with the AI Research Environment.

## Integrated Diagnostic Tool

The environment now includes a comprehensive diagnostic tool that can help identify and solve many common issues:

```bash
python -c "from utils.diagnostics import run_diagnostics; run_diagnostics()"
```

This will analyze your system, check for common issues, and provide specific recommendations.

## Docker Issues

### Error: Cannot connect to the Docker daemon

**Symptoms:**
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
```

**Solution:**
1. Ensure Docker is running:
   ```bash
   sudo systemctl start docker
   ```
2. Add your user to the docker group:
   ```bash
   sudo usermod -aG docker $USER
   ```
3. Log out and log back in, or restart the system.

### Permission Denied

**Symptoms:**
```
permission denied while trying to connect to the Docker daemon socket
```

**Solution:**
```bash
sudo chmod 666 /var/run/docker.sock
```

### Docker Compose Not Found

**Symptoms:**
```
docker-compose: command not found
```

**Solution:**
Install Docker Compose:
```bash
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

Or for the standalone version:
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## GPU Issues

### NVIDIA Container Toolkit Not Found

**Symptoms:**
```
could not select device driver "" with capabilities: [[gpu]]
```

**Solution:**
1. Install NVIDIA Container Toolkit:
   ```bash
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update
   sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```

2. Verify installation:
   ```bash
   # Test NVIDIA Docker
   docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
   
   # Check GPU detection with our utility
   python -c "from utils.gpu_utils import gpu_manager; print(f'GPU available: {gpu_manager.check_gpu_availability()}, Docker GPU support: {gpu_manager.check_docker_gpu_support()}')"
   ```

### CUDA Version Mismatch

**Symptoms:**
```
CUDA driver version is insufficient for CUDA runtime version
```

**Solution:**
1. Update your NVIDIA drivers
2. Or modify the Dockerfile to use an older CUDA version:
   ```dockerfile
   FROM nvidia/cuda:10.2-cudnn8-runtime-ubuntu20.04
   ```
3. Check compatibility with:
   ```bash
   python -c "from utils.gpu_utils import gpu_manager; info = gpu_manager.get_gpu_info()[0] if gpu_manager.get_gpu_info() else {}; print(f'CUDA version: {info.get(\"cuda_version\", \"N/A\")}, Driver version: {info.get(\"driver_version\", \"N/A\")}')"
   ```

### GPU Not Detected Inside Container

**Symptoms:**
- GPU is visible on the host but not in the container
- PyTorch/TensorFlow reports no GPU available

**Solution:**
1. Make sure you're using the latest environment manager:
   ```bash
   python environment_manager.py --debug
   ```
   The debug flag will show detailed information about GPU detection.

2. Verify Docker is configured to use NVIDIA runtime:
   ```bash
   # Check if nvidia-container-runtime is installed
   which nvidia-container-runtime
   ```

3. Check if environmental variables in entrypoint.sh are properly configured:
   ```bash
   grep -i "NVIDIA\|CUDA" entrypoint.sh
   ```

## Environment Manager Issues

### Environment Fails to Start

**Symptoms:**
```
Failed to start the environment: Command '[...]' returned non-zero exit status 1
```

**Solution:**
1. Run with debug mode for more information:
   ```bash
   python environment_manager.py --debug
   ```

2. Check if Docker Compose file exists and is valid:
   ```bash
   ls -la head_1/docker-compose.yml
   docker-compose -f head_1/docker-compose.yml config
   ```

### Memory or CPU Limits Issues

**Symptoms:**
- Container crashes with OOM (Out of Memory) errors
- System becomes unresponsive when running containers

**Solution:**
1. Manually specify lower memory limits:
   ```bash
   python environment_manager.py --mem-limit 4g --cpu-limit 2
   ```

2. Check system resources before starting:
   ```bash
   python -c "from utils.system_utils import system_manager; print(system_manager.get_system_summary())"
   ```

## Python Dependencies Issues

### Package Installation Fails

**Symptoms:**
```
ERROR: Could not build wheels for [package]
```

**Solution:**
1. Install build tools:
   ```bash
   sudo apt-get install build-essential python3-dev
   ```
2. Upgrade pip:
   ```bash
   pip install --upgrade pip
   ```
3. Try installing the specific package with verbose output:
   ```bash
   pip install -v [package]
   ```

## Container Access Issues

### Cannot Access JupyterLab

**Symptoms:**
- Browser cannot connect to http://localhost:8888

**Solution:**
1. Check if the container is running:
   ```bash
   docker ps
   ```
2. Check the port mapping:
   ```bash
   docker port $(docker ps -q --filter "name=jupyter")
   ```
3. Try accessing with the token (default: `researchenv`):
   ```bash
   docker logs $(docker ps -q --filter "name=jupyter")
   ```
   Look for a URL with token in the output.

4. Restart the environment with a specific port:
   ```bash
   python environment_manager.py --port 8080:8888
   ```
   Then try accessing at http://localhost:8080

### Cannot Access Monitoring Dashboard

**Symptoms:**
- Browser cannot connect to http://localhost:3000

**Solution:**
1. Ensure monitoring is enabled:
   ```bash
   python environment_manager.py --enable-monitoring
   ```
2. Check if the Grafana container is running:
   ```bash
   docker ps | grep grafana
   ```
3. Try a different port if 3000 is in use:
   ```bash
   python environment_manager.py --enable-monitoring --monitor-port 3030
   ```

## Scripts Not Executable

**Symptoms:**
```
bash: ./entrypoint.sh: Permission denied
```

**Solution:**
```bash
chmod +x entrypoint.sh run.sh
```

## Diagnostics and Utilities Issues

### Utility Import Errors

**Symptoms:**
```
ImportError: No module named 'utils.gpu_utils'
```

**Solution:**
1. Make sure your working directory is the root of the project:
   ```bash
   cd /path/to/research
   ```
2. Check if the utility files exist:
   ```bash
   ls -la utils/gpu_utils.py utils/system_utils.py utils/diagnostics.py
   ```
3. Try installing the package in development mode:
   ```bash
   pip install -e .
   ```

## Additional Help

If you're still experiencing issues:

1. Run the comprehensive diagnostics tool:
   ```bash
   python -c "from utils.diagnostics import run_diagnostics; run_diagnostics()"
   ```

2. Check container logs:
   ```bash
   # Get container logs
   docker logs $(docker ps -q --filter "name=research")
   
   # For monitoring containers
   docker logs $(docker ps -q --filter "name=grafana")
   docker logs $(docker ps -q --filter "name=prometheus")
   ```

3. Check the environment log:
   ```bash
   cat environment.log
   ```

4. Open an issue on GitHub with:
   - The diagnostic output
   - Error messages
   - Your system information
   - Steps to reproduce the issue
