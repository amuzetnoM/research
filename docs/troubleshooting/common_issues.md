# Troubleshooting Common Issues

This document provides solutions for common issues you might encounter.

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
   docker port ml-container
   ```
3. Try accessing with the token:
   ```bash
   docker logs ml-container
   ```
   Look for a URL with token in the output.

## Scripts Not Executable

**Symptoms:**
```
bash: ./entrypoint.sh: Permission denied
```

**Solution:**
```bash
chmod +x entrypoint.sh gpu_check.py run.sh
```

## Additional Help

If you're still experiencing issues:
1. Check the logs: `docker logs ml-container`
2. Run setup in verbose mode: `python setup/setup.py --verbose`
3. Open an issue on GitHub with detailed information about your problem
