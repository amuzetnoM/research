# Prometheus Configuration

This document describes the Prometheus setup in the research environment, including configuration options and monitoring targets.

## Overview

Prometheus is configured in the research environment to collect metrics from multiple sources:
- The research application itself
- Node exporter (for host system metrics)
- cAdvisor (for container metrics)
- Prometheus's own metrics

## Configuration File

The main configuration file is located at `monitoring/prometheus/prometheus.yml`. This file defines:
- Global settings (scrape intervals, evaluation intervals)
- Alerting configuration
- Rule files
- Scrape configurations (what endpoints to collect metrics from)

### Current Configuration

```yaml
global:
  scrape_interval: 15s     # How frequently to scrape targets
  evaluation_interval: 15s # How frequently to evaluate rules

# Scrape configurations define monitoring targets
scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "node_exporter"
    static_configs:
      - targets: ["node-exporter:9100"]

  - job_name: "research_container"
    static_configs:
      - targets: ["research:8888"]
    metrics_path: /metrics

  - job_name: "cadvisor"
    static_configs:
      - targets: ["cadvisor:8080"]
```

## Docker Configuration

Prometheus runs as a Docker container with the following configuration (from `head_1/docker-compose.yml`):

```yaml
prometheus:
  image: prom/prometheus:latest
  container_name: prometheus
  restart: unless-stopped
  ports:
    - "9090:9090"
  volumes:
    - ../monitoring/prometheus:/etc/prometheus
    - prometheus_data:/prometheus
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--web.console.libraries=/etc/prometheus/console_libraries'
    - '--web.console.templates=/etc/prometheus/consoles'
    - '--storage.tsdb.retention.time=15d'
```

## Key Features

### Data Retention

Prometheus is configured to retain metrics for 15 days (`--storage.tsdb.retention.time=15d`). 

### Persistent Storage

Metrics data is stored in a Docker volume (`prometheus_data`) to ensure data persistence across container restarts.

### Scrape Interval

The default scrape interval is set to 15 seconds, meaning Prometheus collects new data points from all targets every 15 seconds.

## Using Prometheus

### Web Interface

The Prometheus web interface is accessible at http://localhost:9090. From here, you can:

1. **Execute Queries**: Use PromQL (Prometheus Query Language) to query and analyze collected metrics
2. **View Targets**: See the status of all monitoring targets
3. **View Configuration**: Review the active configuration
4. **Access Graph**: Visualize metrics using the built-in graphing tool

### Common PromQL Queries

Here are some useful PromQL queries for the research environment:

- CPU Usage: `100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)`
- Memory Usage: `100 * (node_memory_MemTotal_bytes - node_memory_MemFree_bytes - node_memory_Buffers_bytes - node_memory_Cached_bytes) / node_memory_MemTotal_bytes`
- Disk Usage: `100 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} * 100)`
- Network Traffic Received: `rate(node_network_receive_bytes_total[1m])`
- Network Traffic Transmitted: `rate(node_network_transmit_bytes_total[1m])`

## Adding New Targets

To monitor additional services or applications:

1. Edit the `monitoring/prometheus/prometheus.yml` file
2. Add a new job under `scrape_configs`
3. Restart the Prometheus container: `docker-compose -f head_1/docker-compose.yml restart prometheus`

Example for adding a new target:

```yaml
- job_name: "new_service"
  static_configs:
    - targets: ["new-service:9100"]
  metrics_path: /metrics
```