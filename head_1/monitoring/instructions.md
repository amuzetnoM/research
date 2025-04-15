# AI Research Environment Monitoring

This folder contains configurations for monitoring your AI research environment using Grafana and Prometheus.

## Running the Dashboard

### Prerequisites

1. Docker and Docker Compose installed
2. Node exporters running on your target containers

### Directory Setup
Before running, ensure you have the correct directory structure:
```bash
mkdir -p prometheus
mkdir -p grafana/provisioning/dashboards
mkdir -p grafana/provisioning/datasources
```

### Setup Instructions

1.  Copy the docker-compose configuration into a `docker-compose.yml` file in your monitoring directory.
2.  Start the monitoring stack:

    ```bash
    docker compose up -d
    ```
3.  Access Grafana:

    *   Open your browser and navigate to `http://localhost:3000`
    *   Default login: admin/admin (you'll be prompted to change the password on first login)
4.  The AI Research Environment Dashboard should be automatically provisioned and available

    *   If not, go to Dashboards → Manage and look for "AI Research Environment Dashboard"

### Configuration

*   Prometheus configuration is in `./prometheus/prometheus.yml`
*   Grafana dashboards are provisioned from `./grafana/provisioning/dashboards/`
*   Grafana data sources are provisioned from `./grafana/provisioning/datasources/`

### Troubleshooting

*   If the dashboard doesn't show data, check that Prometheus is properly scraping your node exporters
*   Verify that your node exporters are running at the expected targets in `prometheus/prometheus.yml`
*   Check Prometheus data source is properly configured in Grafana
*   If you encounter issues, refer to `troubleshooting_prometheus.md` for detailed steps.
