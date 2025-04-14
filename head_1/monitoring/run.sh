#!/bin/bash

# Set Node.js options to fix deprecated warning
export NODE_OPTIONS="--force-node-api-uncaught-exceptions-policy=true"

# Down any existing containers
docker compose down

# Start the monitoring stack
docker compose up -d

echo "Monitoring stack is running!"
echo "Access Grafana at: http://localhost:3000 (admin/admin)"
echo "Access Prometheus at: http://localhost:9090"
