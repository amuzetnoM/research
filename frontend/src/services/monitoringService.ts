import { AxiosRequestConfig } from 'axios';
import apiClient, { 
  getContainerClient,
  prometheusClient, 
  grafanaClient, 
  ENDPOINTS, 
  buildQueryParams,
  ApiError,
  ApiErrorType
} from './api';
import { logger } from '@utils/logger';

// Types for container metrics
export interface ContainerMetrics {
  cpu: {
    usage: number;
    cores: number;
    load: number;
  };
  memory: {
    used: number;
    total: number;
    percentage: number;
  };
  network: {
    rx: number;
    tx: number;
  };
  disk?: {
    used: number;
    total: number;
    percentage: number;
  };
  uptime: string;
  status: string;
  timestamp: string;
  version?: string;
  lastRestart?: string;
  errorRate?: number;
}

export interface TimeSeriesDataPoint {
  timestamp: number;
  value: number;
}

export interface TimeSeriesData {
  metric: string;
  values: TimeSeriesDataPoint[];
}

export interface PrometheusQueryResult {
  status: string;
  data: {
    resultType: string;
    result: Array<{
      metric: Record<string, string>;
      values?: [number, string][];
      value?: [number, string];
    }>;
  };
}

// Container-specific API functions
export const getContainerMetrics = async (containerId: 'container1' | 'container2'): Promise<ContainerMetrics> => {
  try {
    const client = getContainerClient(containerId);
    const response = await client.get(ENDPOINTS.metrics);
    return response.data;
  } catch (error) {
    logger.warn(`Failed to fetch metrics for ${containerId}, using mock data`, { error });
    return generateMockMetrics(containerId);
  }
};

export const getContainerHealth = async (containerId: 'container1' | 'container2'): Promise<{ status: string; details?: any }> => {
  try {
    const client = getContainerClient(containerId);
    const response = await client.get(ENDPOINTS.health);
    return response.data;
  } catch (error) {
    logger.error(`Failed to fetch health for ${containerId}`, { error });
    throw error instanceof ApiError 
      ? error 
      : new ApiError(`Failed to fetch health for ${containerId}`, ApiErrorType.UNKNOWN, undefined, error);
  }
};

export const analyzeContainerMetrics = async (
  containerId: 'container1' | 'container2',
  timeRange: string
): Promise<string> => {
  try {
    const response = await apiClient.post(`${ENDPOINTS.analyzeContainer}/${containerId}`, {
      timeRange
    });
    return response.data.analysis;
  } catch (error) {
    logger.error(`Failed to analyze metrics for ${containerId}`, { error });
    return generateMockAnalysis(containerId);
  }
};

// Prometheus query functions
export const queryPrometheus = async (query: string, time?: string): Promise<PrometheusQueryResult> => {
  const params = { query, time };
  const url = `${ENDPOINTS.prometheusQuery}${buildQueryParams(params)}`;
  
  try {
    const response = await prometheusClient.get(url);
    return response.data;
  } catch (error) {
    logger.error(`Prometheus query failed: ${query}`, { error });
    throw error instanceof ApiError 
      ? error 
      : new ApiError('Prometheus query failed', ApiErrorType.UNKNOWN, undefined, error);
  }
};

export const queryPrometheusRange = async (
  query: string, 
  start: string, 
  end: string, 
  step: string
): Promise<PrometheusQueryResult> => {
  const params = { query, start, end, step };
  const url = `${ENDPOINTS.prometheusQueryRange}${buildQueryParams(params)}`;
  
  try {
    const response = await prometheusClient.get(url);
    return response.data;
  } catch (error) {
    logger.error(`Prometheus range query failed: ${query}`, { error, params: { start, end, step } });
    throw error instanceof ApiError 
      ? error 
      : new ApiError('Prometheus range query failed', ApiErrorType.UNKNOWN, undefined, error);
  }
};

// Transform Prometheus results into time series data
export const transformPrometheusToTimeSeries = (
  result: PrometheusQueryResult,
  metricName: string
): TimeSeriesData => {
  if (result.status !== 'success' || !result.data.result || result.data.result.length === 0) {
    logger.warn('Empty or invalid Prometheus result', { result, metricName });
    return {
      metric: metricName,
      values: []
    };
  }

  const prometheusResult = result.data.result[0];
  
  if (prometheusResult.values) {
    // Range query result
    return {
      metric: metricName,
      values: prometheusResult.values.map(([timestamp, value]) => ({
        timestamp,
        value: parseFloat(value)
      }))
    };
  } else if (prometheusResult.value) {
    // Instant query result
    const [timestamp, value] = prometheusResult.value;
    return {
      metric: metricName,
      values: [{
        timestamp,
        value: parseFloat(value)
      }]
    };
  }
  
  return {
    metric: metricName,
    values: []
  };
};

// Grafana dashboard functions
export const getGrafanaDashboards = async (): Promise<any[]> => {
  try {
    const response = await grafanaClient.get(ENDPOINTS.grafanaDashboards);
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch Grafana dashboards', { error });
    return [];
  }
};

// Self-awareness metrics
export const fetchSelfAwarenessMetrics = async (params: {
  metric?: string;
  timestamp?: string;
}): Promise<any> => {
  try {
    const url = `${ENDPOINTS.selfAwarenessData}${buildQueryParams(params)}`;
    const response = await apiClient.get(url);
    return response.data;
  } catch (error) {
    logger.error('Failed to fetch self-awareness metrics', { error, params });
    return {};
  }
};

// Mock data generators for development
const generateMockMetrics = (containerId: string): ContainerMetrics => {
  const baseValue = containerId === 'container1' ? 0.8 : 1.2;
  const timestamp = new Date().toISOString();
  
  return {
    cpu: {
      usage: Math.round((35 + Math.random() * 20 * baseValue) * 10) / 10,
      cores: 4,
      load: Math.round((1.2 + Math.random() * 1.5 * baseValue) * 100) / 100,
    },
    memory: {
      used: Math.round((8 + Math.random() * 4 * baseValue) * 10) / 10,
      total: 16,
      percentage: Math.round((50 + Math.random() * 25 * baseValue) * 10) / 10,
    },
    network: {
      rx: Math.round((2.5 + Math.random() * 1.5 * baseValue) * 100) / 100,
      tx: Math.round((1.8 + Math.random() * 1.2 * baseValue) * 100) / 100,
    },
    disk: {
      used: Math.round((120 + Math.random() * 30) * 10) / 10,
      total: 500,
      percentage: Math.round((24 + Math.random() * 6) * 10) / 10,
    },
    uptime: containerId === 'container1' ? '7d 5h 32m' : '3d 14h 08m',
    status: Math.random() > 0.95 ? 'warning' : 'running',
    timestamp,
    version: containerId === 'container1' ? '1.5.2' : '1.5.1',
    lastRestart: containerId === 'container1' 
      ? new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString() 
      : new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    errorRate: Math.round(Math.random() * 2 * 10) / 10,
  };
};

const generateMockAnalysis = (containerId: string): string => {
  const analyses = [
    `Based on the metrics for ${containerId}, there appears to be a correlation between CPU usage spikes and increased request volume. The container is handling the load efficiently, but you might want to consider optimizing the request handling logic to reduce CPU consumption.`,
    `${containerId} shows a gradual increase in memory usage over time, which could indicate a memory leak. Consider investigating this issue to prevent potential performance degradation or container restarts in the future.`,
    `The metrics indicate that ${containerId} is experiencing occasional network spikes that correlate with increased response times. Consider implementing rate limiting or optimizing network-intensive operations to improve overall stability.`,
    `Analysis of ${containerId} metrics reveals that CPU and memory usage patterns are within normal operational parameters. However, the error rate has increased slightly over the past period, which may require attention.`,
    `${containerId} is showing stable performance metrics over the monitored period. Resource utilization is consistent and within expected ranges, suggesting that the current configuration is adequate for the workload.`
  ];
  
  return analyses[Math.floor(Math.random() * analyses.length)];
};

// Generate sample time-series data for development
export const generateTimeSeriesData = (points = 24, interval = 3600000) => {
  const now = Date.now();
  const result = [];
  
  for (let i = points - 1; i >= 0; i--) {
    const timestamp = now - i * interval;
    result.push({
      timestamp,
      cpu: Math.round(Math.random() * 30 + 20), // CPU: 20-50%
      memory: Math.round(Math.random() * 25 + 50), // Memory: 50-75%
      network: parseFloat((Math.random() * 1.5 + 0.5).toFixed(2)), // Network: 0.5-2.0 MB/s
      requests: Math.round(Math.random() * 150 + 150), // Requests: 150-300 req/min
      responseTime: Math.round(Math.random() * 100 + 100), // Response time: 100-200ms
      errorRate: parseFloat((Math.random() * 2).toFixed(2)), // Error rate: 0-2%
    });
  }
  
  return result;
};

// Generate sample comparison data
export const generateComparisonData = () => [
  {
    name: 'CPU Usage',
    container1: 42,
    container2: 35,
  },
  {
    name: 'Memory Usage',
    container1: 65,
    container2: 58,
  },
  {
    name: 'Network I/O',
    container1: 1.2,
    container2: 0.9,
  },
  {
    name: 'Disk I/O',
    container1: 5.8,
    container2: 4.3,
  },
  {
    name: 'Request Rate',
    container1: 256,
    container2: 187,
  },
  {
    name: 'Response Time',
    container1: 120,
    container2: 145,
  },
];
