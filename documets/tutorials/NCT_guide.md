# NVIDIA Container Toolkit Setup Guide

## Installation

1. Run the installation script:
   ```bash
   chmod +x install-nvidia-toolkit.sh
   ./install-nvidia-toolkit.sh
   ```

2. Test the installation:
   ```bash
   chmod +x test-nvidia-setup.sh
   ./test-nvidia-setup.sh
   ```

## Next Steps

After installation, you can:

1. **Run GPU-accelerated containers**: Use the `--gpus` flag to specify which GPUs to use:
   ```bash
   # Use all GPUs
   docker run --gpus all ...
   
   # Use specific GPUs (e.g., GPU 0 and 1)
   docker run --gpus '"device=0,1"' ...
   
   # Set GPU capabilities
   docker run --gpus '"capabilities=compute,utility"' ...
   ```

2. **Docker Compose Integration**: Add GPU access to your services:
   ```yaml
   services:
     my-gpu-service:
       image: nvidia/cuda:11.6.2-base-ubuntu20.04
       deploy:
         resources:
           reservations:
             devices:
               - driver: nvidia
                 count: 1
                 capabilities: [gpu]
   ```

3. **Kubernetes Integration**: If using Kubernetes, install the NVIDIA Device Plugin:
   ```bash
   kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.13.0/nvidia-device-plugin.yml
   ```

4. **Troubleshooting**:
   - Verify drivers: `nvidia-smi`
   - Check container toolkit: `nvidia-ctk --version`
   - View Docker runtimes: `docker info | grep Runtimes`

## Common Docker Errors

### PowerShell-specific Issues

When running Docker in PowerShell using scripts like `run.ps1`, you might encounter connection errors:

#### "Error during connect: GET and HEAD errors" 

This typically indicates that Docker daemon isn't running or is inaccessible. Try the following:

1. **Check if Docker Desktop is running**:
   - Look for the Docker icon in your system tray
   - Start Docker Desktop if it's not running

2. **Restart Docker service**:
   ```powershell
   Restart-Service docker
   ```

3. **Check Docker context**:
   ```powershell
   docker context ls
   docker context use default
   ```

4. **Verify Docker daemon settings**:
   - Open Docker Desktop → Settings → Resources
   - Check that the daemon is properly configured

5. **Run PowerShell as Administrator** when executing Docker commands

6. **Use proper PowerShell syntax for GPU flags**:
   ```powershell
   # PowerShell syntax for GPU flags (note the escaping differences)
   docker run --gpus all nvidia/cuda:11.6.2-base-ubuntu20.04 nvidia-smi
   docker run --gpus """device=0""" nvidia/cuda:11.6.2-base-ubuntu20.04 nvidia-smi
   ```

For more information, visit the [official documentation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/index.html).
