# Setup and Installation

This comprehensive guide covers everything needed to set up the AI Research Environment.

## Prerequisites

- Python 3.8+
- Docker
- Docker Compose
- NVIDIA drivers (optional, for GPU support)

## Installation Steps

```bash
# Clone the repository
git clone <repository-url>
cd research

# Run setup script
python -m setup.setup

# Start the research environment with monitoring
python environment_manager.py --enable-monitoring
```

## Environment Configuration

The environment manager supports both single and dual-container configurations:

```bash
python environment_manager.py --help
```

## Dual Container Setup

Our research environment now supports dual container operation for parallel experiments and improved workflow:

### Starting Container 1 (Primary)

```bash
cd terminal_1
# On Windows
.\run.ps1
# On Linux/macOS
bash run.sh
```

### Starting Container 2 (Secondary)

```bash
cd terminal_2
# On Windows
.\run.ps1
# On Linux/macOS
bash run.sh
```

## Configuration Options

Common configuration options for both containers:

```bash
# Basic configuration
python environment_manager.py --container 1 --port 8888:8888 --jupyter-token mytoken
python environment_manager.py --container 2 --port 8889:8888 --jupyter-token mytoken2

# Resource limits
python environment_manager.py --container 1 --mem-limit 16g --cpu-limit 4
python environment_manager.py --container 2 --mem-limit 16g --cpu-limit 4

# GPU configuration
python environment_manager.py --container 1 --gpu-ids 0  # Use GPU 0
python environment_manager.py --container 2 --gpu-ids 0,1  # Use multiple GPUs

# Monitoring
python environment_manager.py --container 1 --enable-monitoring --monitor-port 3000
python environment_manager.py --container 2 --enable-monitoring --monitor-port 3001
```

## Starting and Stopping

Start the environments:
```bash
# Start both containers
python environment_manager.py --start-all

# Start specific container
python environment_manager.py --container 1 --start
python environment_manager.py --container 2 --start
```

Once running, you can access:

### Container 1
- JupyterLab at http://localhost:8888 (default token: `researchenv`)
- Monitoring Dashboard at http://localhost:3000 (if enabled)
- TensorBoard at http://localhost:6006 (if enabled)

### Container 2
- JupyterLab at http://localhost:8889 (default token: `researchenv2`)
- Monitoring Dashboard at http://localhost:3001 (if enabled)
- TensorBoard at http://localhost:6007 (if enabled)

Stop the environments:
```bash
# Stop both containers
python environment_manager.py --stop-all

# Stop specific container
python environment_manager.py --container 1 --stop
python environment_manager.py --container 2 --stop
```

## Docker Configuration

### Port Mappings

#### Container 1
- 8888:8888 - JupyterLab
- 6006:6006 - TensorBoard
- 3000:3000 - Grafana (when monitoring is enabled)
- 9090:9090 - Prometheus (when monitoring is enabled)

#### Container 2
- 8889:8888 - JupyterLab
- 6007:6006 - TensorBoard
- 3001:3000 - Grafana (when monitoring is enabled)
- 9091:9090 - Prometheus (when monitoring is enabled)

### Volume Mappings

Each container mounts the current directory to /app in the container:
```
$(pwd):/app
```

Additional volumes can be mounted as needed for data directories, model storage, etc.

## Using Both Containers Together

The dual-container setup enables several advanced workflows:

1. **Parallel Experimentation**: Run different model architectures simultaneously
2. **A/B Testing**: Test different hyperparameters with identical base conditions
3. **Distributed Training**: Split workloads across containers
4. **Pipeline Development**: Use one container for data preparation and another for model training
5. **Research Collaboration**: Allow multiple researchers to work in isolated environments with shared data

## Resource Management

Both containers can be configured to share resources intelligently:

- GPU memory splitting via CUDA_VISIBLE_DEVICES
- CPU core allocation via Docker resource limits
- Memory allocation controls via Docker memory limits
- Storage sharing via mounted volumes

## Troubleshooting

For container-specific issues, use the diagnostics tools:

```bash
# Container 1 diagnostics
python utils/diagnostics.py --container 1

# Container 2 diagnostics
python utils/diagnostics.py --container 2
```
