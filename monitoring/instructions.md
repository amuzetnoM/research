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

1. First, create a docker-compose.yml file in your monitoring directory:
   ```bash
   PS C:\_worxpace\research\monitoring> New-Item -Path . -Name "docker-compose.yml" -ItemType "file"
   ```

2. Copy the docker-compose configuration from the sample below into this file.
`
3. Start the monitoring stack:
   ```bash
   PS C:\_worxpace\research\monitoring> docker compose up -d
   ```

4. Access Grafana:
   - Open your browser and navigate to `http://localhost:3000`
   - Default login: admin/admin (you'll be prompted to change the password on first login)

5. The AI Research Environment Dashboard should be automatically provisioned and available
   - If not, go to Dashboards → Manage and look for "AI Research Environment Dashboard"

### Configuration

- Prometheus configuration is in `./prometheus/prometheus.yml`
- Grafana dashboards are provisioned from `./grafana/provisioning/dashboards/`
- Grafana data sources are provisioned from `./grafana/provisioning/datasources/`

### Troubleshooting

- If the dashboard doesn't show data, check that Prometheus is properly scraping your node exporters
- Verify that your node exporters are running at the expected targets in prometheus.yml
- Check Prometheus data source is properly configured in Grafana
- If you get "empty compose file" error, make sure docker-compose.yml exists in the current directory
