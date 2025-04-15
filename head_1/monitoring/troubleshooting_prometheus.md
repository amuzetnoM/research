# Prometheus Troubleshooting Guide

If Prometheus isn't collecting metrics, follow these troubleshooting steps:

## 1. Check Prometheus Status

1.  Open Prometheus UI at http://localhost:9090/
2.  Go to Status > Targets to see if targets are up or down
3.  Check Status > Configuration to verify your configuration was loaded properly

## 2. Verify Node Exporters are Running

```bash
# Check container status
docker ps | grep node-exporter

# Check logs for node exporters
docker logs node-exporter
docker logs node-exporter-2
```

## 3. Test Node Exporter Endpoints Directly

```bash
# Test from host machine
curl http://localhost:9100/metrics
curl http://localhost:9101/metrics

# Test from within Prometheus container
docker exec -it prometheus wget -qO- node-exporter:9100/metrics | head
```

## 4. Check Prometheus Logs

```bash
docker logs prometheus
```

## 5. Network Issues

If running on Windows, ensure 'host.docker.internal' resolves correctly within Docker.
If not, use container names instead (as updated in the prometheus.yml file).

## 6. DNS Resolution Issues

If container names are not resolving, check your Docker network configuration. Ensure that containers are on the same network.

## 7. Firewall Issues

Ensure that no firewalls are blocking communication between Prometheus and the exporters.

## 8. Target Discovery

Double-check that the targets defined in `prometheus.yml` are correct and reachable.

## 9. Restart Services

```bash
docker compose down
docker compose up -d
```

## 10. Check Volumes

Ensure Prometheus has proper permissions to write to its data volume:

```bash
docker exec -it prometheus ls -la /prometheus
```
