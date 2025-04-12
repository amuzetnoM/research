# Multi-stage build for AI Research Environment
# Stage 1: Base system dependencies
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04 as base

# Set environment variables to reduce size and improve caching
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    ca-certificates \
    python3.10 \
    python3.10-dev \
    python3-pip \
    python3-setuptools \
    libopenmpi-dev \
    bc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash researcher

# Stage 2: Python dependencies
FROM base as python-deps

# Install Python packages from consolidated requirements file
COPY setup/requirements.txt /tmp/
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r /tmp/requirements.txt

# Stage 3: Final image
FROM python-deps

# Set up working directory
WORKDIR /app
RUN chown researcher:researcher /app

# Copy application code
COPY --chown=researcher:researcher . /app/

# Setup Jupyter configuration
RUN mkdir -p /home/researcher/.jupyter && \
    echo "c.NotebookApp.ip = '0.0.0.0'" > /home/researcher/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.open_browser = False" >> /home/researcher/.jupyter/jupyter_notebook_config.py && \
    chown -R researcher:researcher /home/researcher/.jupyter

# Configure memory optimization
ENV MALLOC_TRIM_THRESHOLD_=65536
ENV TF_ENABLE_AUTO_MIXED_PRECISION=1
ENV TF_GPU_THREAD_MODE=gpu_private

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8888/api || exit 1

# Expose ports
EXPOSE 8888 6006

# Default command
ENTRYPOINT ["/app/entrypoint.sh"]
