# Monitoring Infrastructure

This document provides a comprehensive overview of the monitoring capabilities in the AI Research Environment.

## Overview

The monitoring stack consists of:
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Node Exporter**: Hardware and OS metrics
- **cAdvisor**: Container metrics
- **Python Metrics Integration**: Application-specific metrics

## Accessing Monitoring

- **Grafana**: http://localhost:3000 (default credentials: admin/admin)
- **Prometheus**: http://localhost:9090

## Dashboards

### AI Research Environment Dashboard

This comprehensive dashboard provides real-time monitoring of:

- **System Metrics**: CPU, memory, disk, and network
- **Container Metrics**: Container resource usage
- **GPU Metrics**: GPU utilization, memory, temperature, and power
- **ML Framework Metrics**: Training metrics and resource usage

### Performance Analysis Dashboard

Specialized dashboard for analyzing performance bottlenecks:
- CPU vs GPU utilization comparison
- Memory allocation breakdowns
- I/O wait analysis
- Network saturation monitoring

### ML/AI Workflow Dashboard

- Training metrics over time
- Model comparison views
- Hyperparameter tracking
- Resource efficiency metrics

## Prometheus Configuration

Prometheus collects metrics from multiple sources:
- The research application
- Node exporter (for host system metrics)
- cAdvisor (for container metrics)
- Prometheus's own metrics

### Key Features

- **Data Retention**: 15 days
- **Scrape Interval**: 15 seconds
- **Persistent Storage**: Data persists across container restarts

### Common PromQL Queries

Useful PromQL queries for the research environment:

- CPU Usage: `100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)`
- Memory Usage: `100 * (node_memory_MemTotal_bytes - node_memory_MemFree_bytes - node_memory_Buffers_bytes - node_memory_Cached_bytes) / node_memory_MemTotal_bytes`
- Disk Usage: `100 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} * 100)`
- Network Traffic: `rate(node_network_receive_bytes_total[1m])`

## Diagnostics

For monitoring issues, use the diagnostics script:

```bash
python utils/monitoring_diagnostics.py --service grafana
```

This provides information about:
- Container status
- Port accessibility
- Data source connectivity
- Recent error logs
