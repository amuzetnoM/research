# Monitoring Infrastructure

This document provides a comprehensive overview of the monitoring capabilities in the AI Research Environment.

## Overview

The monitoring stack consists of:
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Node Exporter**: Hardware and OS metrics
- **cAdvisor**: Container metrics
- **Python Metrics Integration**: Application-specific metrics

Our environment supports dual-container monitoring with separate instances for each research container.

## Accessing Monitoring

### Container 1
- **Grafana**: http://localhost:3000 (default credentials: admin/admin)
- **Prometheus**: http://localhost:9090

### Container 2
- **Grafana**: http://localhost:3001 (default credentials: admin/admin)
- **Prometheus**: http://localhost:9091

## Dashboards

### AI Research Environment Dashboard

This comprehensive dashboard provides real-time monitoring of both research containers:

- **System Metrics**: CPU, memory, disk, and network for both containers
- **Container Metrics**: Container resource usage comparison
- **GPU Metrics**: GPU utilization, memory, temperature, and power
- **ML Framework Metrics**: Training metrics and resource usage

### Performance Analysis Dashboard

Specialized dashboard for analyzing performance bottlenecks:
- CPU vs GPU utilization comparison
- Memory allocation breakdowns
- I/O wait analysis
- Network saturation monitoring
- Cross-container resource usage patterns

### ML/AI Workflow Dashboard

- Training metrics over time
- Model comparison views
- Hyperparameter tracking
- Resource efficiency metrics
- Experiment comparison across containers

## Prometheus Configuration

Prometheus collects metrics from multiple sources across both containers:
- The research applications (Container 1 and Container 2)
- Node exporters (for host system metrics)
- cAdvisor (for container metrics)
- Prometheus's own metrics

### Key Features

- **Data Retention**: 15 days
- **Scrape Interval**: 15 seconds
- **Persistent Storage**: Data persists across container restarts
- **Multi-container Support**: Centralized metrics collection from both research environments

### Common PromQL Queries

Useful PromQL queries for the research environment:

- CPU Usage (Container 1): `100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle",job="node_exporter"}[1m])) * 100)`
- CPU Usage (Container 2): `100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle",job="node_exporter_2"}[1m])) * 100)`
- Memory Usage (Container 1): `100 * (node_memory_MemTotal_bytes{job="node_exporter"} - node_memory_MemFree_bytes{job="node_exporter"} - node_memory_Buffers_bytes{job="node_exporter"} - node_memory_Cached_bytes{job="node_exporter"}) / node_memory_MemTotal_bytes{job="node_exporter"}`
- Memory Usage (Container 2): `100 * (node_memory_MemTotal_bytes{job="node_exporter_2"} - node_memory_MemFree_bytes{job="node_exporter_2"} - node_memory_Buffers_bytes{job="node_exporter_2"} - node_memory_Cached_bytes{job="node_exporter_2"}) / node_memory_MemTotal_bytes{job="node_exporter_2"}`
- Disk Usage: `100 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} * 100)`
- Network Traffic: `rate(node_network_receive_bytes_total[1m])`
- Container Comparison: `rate(container_cpu_usage_seconds_total{name=~"ai-research|ai-research-2"}[5m])`

## Diagnostics

For monitoring issues, use the diagnostics script:

```bash
python utils/monitoring_diagnostics.py --service grafana --container 1
python utils/monitoring_diagnostics.py --service grafana --container 2
```

This provides information about:
- Container status
- Port accessibility
- Data source connectivity
- Recent error logs

## Multi-Container Monitoring

Our dual-container setup allows for:

1. **Parallel Experiments**: Run different experiments in separate containers with isolated resources
2. **Comparative Analysis**: Compare performance across different configurations
3. **A/B Testing**: Test different models or algorithms against the same datasets
4. **Redundancy**: Maintain backup research environments for critical experiments
5. **Collaborative Work**: Support multiple researchers working on different aspects of a project

## Resource Allocation

Each container has dedicated resource allocations to ensure optimal performance:

| Resource | Container 1 | Container 2 |
|----------|-------------|-------------|
| Memory | 16GB | 16GB |
| CPU Cores | 4 | 4 |
| GPU | Shared | Shared |
| Ports | 8888, 6006, 9090, 3000 | 8889, 6007, 9091, 3001 |

## Alert Configuration

Both containers are configured with alerting capabilities:

- System resource thresholds
- Container health checks
- Experiment completion notifications
- Error rate monitoring
- Data pipeline alerts

Alerts can be configured through the Grafana interface or directly in Prometheus alert rules.
