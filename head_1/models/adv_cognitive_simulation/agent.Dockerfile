FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for scientific packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy framework code
COPY ../../frameworks/self_awareness/self_awareness_client.py .

# Create simulation logs directory
RUN mkdir -p simulation_logs

# Copy cognitive simulation code
COPY cognitive_simulation.py .
COPY simulation_visualizer.py .
COPY cognitive_analysis.py .
COPY config.json .

# Run the cognitive simulation
CMD ["python", "cognitive_simulation.py"]
