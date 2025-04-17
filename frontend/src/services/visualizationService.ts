/**
 * API service for fetching visualization data
 */
import apiClient from './apiClient';
import { dataService } from '../../../dataService/files/dataService';

// API endpoints
const ENDPOINTS = {
  prometheus: '/api/metrics',
  grafana1: '/api/grafana1',
  grafana2: '/api/grafana2',
  container1: '/api/container1',
  container2: '/api/container2',
};

// Helper to get correct Grafana endpoint based on container
const getGrafanaEndpoint = (containerId: string) => {
  return containerId === 'container2' ? ENDPOINTS.grafana2 : ENDPOINTS.grafana1;
};

// Prometheus specific queries for each container
const PROMETHEUS_QUERIES = {
  cpu: (containerId: string) => 
    `100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle",job="node_exporter${containerId === 'container2' ? '_2' : ''}"}[1m])) * 100)`,
  memory: (containerId: string) =>
    `100 * (node_memory_MemTotal_bytes{job="node_exporter${containerId === 'container2' ? '_2' : ''}"} - node_memory_MemFree_bytes - node_memory_Buffers_bytes - node_memory_Cached_bytes) / node_memory_MemTotal_bytes`,
  disk: (containerId: string) =>
    `100 - (node_filesystem_avail_bytes{mountpoint="/",job="node_exporter${containerId === 'container2' ? '_2' : ''}"} / node_filesystem_size_bytes{mountpoint="/"} * 100)`,
  network_receive: (containerId: string) =>
    `rate(node_network_receive_bytes_total{job="node_exporter${containerId === 'container2' ? '_2' : ''}"}[1m])`,
  network_transmit: (containerId: string) =>
    `rate(node_network_transmit_bytes_total{job="node_exporter${containerId === 'container2' ? '_2' : ''}"}[1m])`,
};

// Data transformation utilities
const transformTimeSeriesData = (prometheusData: any) => {
  if (!prometheusData?.data?.result) {
    return [];
  }

  return prometheusData.data.result.map((series: any) => ({
    metric: series.metric.__name__,
    values: series.values.map(([timestamp, value]: [number, string]) => ({
      timestamp: timestamp * 1000, // Convert to milliseconds
      value: parseFloat(value),
    })),
  }));
};

const transformGrafanaData = (grafanaData: any) => {
  if (!grafanaData?.data) {
    return [];
  }

  return grafanaData.data.map((series: any) => ({
    metric: series.target,
    values: series.datapoints.map(([value, timestamp]: [number, number]) => ({
      timestamp,
      value,
    })),
  }));
};

// Helper to transform Prometheus response into standardized format
const transformPrometheusResponse = (data: any, metricName: string) => {
  if (!data?.data?.result?.[0]?.values) {
    return [];
  }

  return data.data.result[0].values.map(([timestamp, value]: [number, string]) => ({
    timestamp: timestamp * 1000, // Convert to milliseconds
    [metricName]: parseFloat(value),
  }));
};

// Helper to parse time range strings into seconds
const parseTimeRange = (range: string): number => {
  const units = {
    'm': 60,
    'h': 3600,
    'd': 86400,
  };
  const match = range.match(/^(\d+)([mhd])$/);
  if (!match) return 3600; // Default to 1 hour
  const [, value, unit] = match;
  return parseInt(value) * units[unit];
};

// Error handler
const handleError = (error: any) => {
  console.error('Visualization Service Error:', error);
  throw {
    message: error.response?.data?.error || 'An error occurred while fetching data',
    status: error.response?.status || 500,
    details: error.response?.data || error,
  };
};

// API Functions
export const fetchMetrics = async (query: string, start?: number, end?: number) => {
  try {
    // Use dataService for REST/SSE
    return await dataService.fetch('metrics', { query, start, end });
  } catch (error) {
    handleError(error);
    throw error;
  }
};

export const fetchContainerMetrics = async (containerId: string, metrics: string[], timeRange?: string) => {
  try {
    const now = Math.floor(Date.now() / 1000);
    const start = timeRange ? now - parseTimeRange(timeRange) : now - 3600; // Default to 1 hour

    const queries = metrics.map(metric => ({
      metric,
      query: PROMETHEUS_QUERIES[metric]?.(containerId) || metric,
    }));

    const results = await Promise.all(
      queries.map(async ({ metric, query }) => {
        const response = await apiClient.get(`${ENDPOINTS.prometheus}/query_range`, {
          params: {
            query,
            start,
            end: now,
            step: '15s', // Match Prometheus scrape interval
          },
        });
        return {
          metric,
          data: transformPrometheusResponse(response.data, metric),
        };
      })
    );

    return results.reduce((acc, { metric, data }) => {
      acc[metric] = data;
      return acc;
    }, {});
  } catch (error) {
    console.error('Error fetching container metrics:', error);
    throw new Error(`Failed to fetch metrics: ${error.message}`);
  }
};

export const fetchGrafanaDashboard = async (dashboardId: string) => {
  try {
    const response = await apiClient.get(`${ENDPOINTS.grafana1}/dashboards/uid/${dashboardId}`);
    return response.data;
  } catch (error) {
    handleError(error);
  }
};

// Add support for Grafana panel embedding
export const getGrafanaEmbedUrl = (containerId: string, dashboardId: string, panelId?: string) => {
  const baseUrl = getGrafanaEndpoint(containerId);
  const params = new URLSearchParams({
    orgId: '1',
    theme: 'dark',
    ...(panelId && { panelId })
  });
  return `${baseUrl}/d/${dashboardId}?${params}`;
};

const visualizationService = {
  fetchMetrics,
  fetchContainerMetrics,
  fetchGrafanaDashboard,
  getGrafanaEmbedUrl,
};

export default visualizationService;