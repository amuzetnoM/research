/**
 * API service for fetching visualization data
 */

// Base API URL
const API_BASE_URL = '/api';

// API endpoints
const ENDPOINTS = {
  timeSeriesData: `${API_BASE_URL}/time-series`,
  categoricalData: `${API_BASE_URL}/categorical`,
  multidimensionalData: `${API_BASE_URL}/multidimensional`,
  correlationData: `${API_BASE_URL}/correlation`,
  dimensionalityData: `${API_BASE_URL}/dimensionality`,
  selfAwarenessData: `${API_BASE_URL}/self-awareness`,
};

// Error handler for API requests
const handleApiError = (error: any) => {
  console.error('API Error:', error);
  
  if (error.response) {
    // Server responded with a status code outside of 2xx range
    return {
      error: `Server error: ${error.response.status}`,
      message: error.response.data?.message || 'Unknown server error',
    };
  } else if (error.request) {
    // Request was made but no response was received
    return {
      error: 'Network error',
      message: 'Unable to connect to the server. Please check your connection.',
    };
  } else {
    // Something else happened while setting up the request
    return {
      error: 'Request error',
      message: error.message || 'An unknown error occurred',
    };
  }
};

// Helper function to build query parameters
const buildQueryParams = (params: Record<string, any>): string => {
  const queryParams = new URLSearchParams();
  
  Object.entries(params)
    .filter(([_, value]) => value !== undefined && value !== null)
    .forEach(([key, value]) => {
      if (Array.isArray(value)) {
        value.forEach(val => queryParams.append(key, val.toString()));
      } else {
        queryParams.append(key, value.toString());
      }
    });
    
  const queryString = queryParams.toString();
  return queryString ? `?${queryString}` : '';
};

// Generic fetch function
const fetchApi = async <T>(url: string, options: RequestInit = {}): Promise<T> => {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    
    if (!response.ok) {
      throw {
        response: {
          status: response.status,
          data: await response.json().catch(() => ({})),
        },
      };
    }
    
    return await response.json();
  } catch (error) {
    throw handleApiError(error);
  }
};

// Time series data for LineChart
export const fetchTimeSeriesData = async (params: {
  metrics?: string[];
  startDate?: string;
  endDate?: string;
  resolution?: 'minute' | 'hour' | 'day' | 'week' | 'month';
  limit?: number;
}) => {
  const url = `${ENDPOINTS.timeSeriesData}${buildQueryParams(params)}`;
  return fetchApi(url);
};

// Categorical data for BarChart
export const fetchCategoricalData = async (params: {
  category?: string;
  metrics?: string[];
  limit?: number;
  sort?: 'asc' | 'desc';
}) => {
  const url = `${ENDPOINTS.categoricalData}${buildQueryParams(params)}`;
  return fetchApi(url);
};

// Multidimensional data for RadarChart
export const fetchMultidimensionalData = async (params: {
  dimensions?: string[];
  entities?: string[];
  limit?: number;
}) => {
  const url = `${ENDPOINTS.multidimensionalData}${buildQueryParams(params)}`;
  return fetchApi(url);
};

// Correlation data for ScatterPlot
export const fetchCorrelationData = async (params: {
  xMetric?: string;
  yMetric?: string;
  zMetric?: string;
  entities?: string[];
  limit?: number;
}) => {
  const url = `${ENDPOINTS.correlationData}${buildQueryParams(params)}`;
  return fetchApi(url);
};

// Correlation matrix for HeatmapChart
export const fetchCorrelationMatrix = async (params: {
  metrics?: string[];
  startDate?: string;
  endDate?: string;
}) => {
  const url = `${ENDPOINTS.correlationData}/matrix${buildQueryParams(params)}`;
  return fetchApi(url);
};

// Self awareness metrics for GaugeChart
export const fetchSelfAwarenessMetrics = async (params: {
  metric?: string;
  timestamp?: string;
}) => {
  const url = `${ENDPOINTS.selfAwarenessData}${buildQueryParams(params)}`;
  return fetchApi(url);
};

// Mock data functions for development when API is not available
export const mockTimeSeriesData = (days = 30, metrics = ['cpu', 'memory', 'network']) => {
  const data = [];
  const now = new Date();
  
  for (let i = 0; i < days; i++) {
    const date = new Date(now);
    date.setDate(now.getDate() - (days - i));
    
    const entry: any = {
      timestamp: date.toISOString(),
      date: date.toISOString().split('T')[0],
    };
    
    metrics.forEach(metric => {
      // Generate somewhat realistic looking values with some randomness
      // but also with trends over time
      const baseValue = {
        cpu: 40,
        memory: 60,
        network: 25,
        latency: 150,
        throughput: 800,
        errors: 5,
      }[metric] || 50;
      
      // Add some randomness and a gentle trend
      const trend = Math.sin((i / days) * Math.PI) * 20;
      const randomness = Math.random() * 20 - 10;
      
      entry[metric] = Math.max(0, Math.round(baseValue + trend + randomness));
    });
    
    data.push(entry);
  }
  
  return data;
};

export const mockCategoricalData = (
  categories = ['Category A', 'Category B', 'Category C', 'Category D', 'Category E'],
  metrics = ['value', 'count']
) => {
  return categories.map(category => {
    const result: any = { name: category };
    
    metrics.forEach(metric => {
      result[metric] = Math.floor(Math.random() * 100);
    });
    
    return result;
  });
};

export const mockRadarData = (
  entities = ['Entity A', 'Entity B', 'Entity C'],
  dimensions = ['Speed', 'Reliability', 'Efficiency', 'Accuracy', 'Adaptability']
) => {
  const result = [];
  
  // Create a data point for each entity with random values for each dimension
  entities.forEach(entity => {
    const dataPoint: any = { name: entity };
    
    dimensions.forEach(dimension => {
      dataPoint[dimension] = Math.floor(Math.random() * 100);
    });
    
    result.push(dataPoint);
  });
  
  return result;
};

export const mockCorrelationData = (
  count = 50,
  xRange = [0, 100],
  yRange = [0, 100],
  zRange = [1, 30]
) => {
  return Array.from({ length: count }, (_, i) => {
    const x = Math.random() * (xRange[1] - xRange[0]) + xRange[0];
    const y = Math.random() * (yRange[1] - yRange[0]) + yRange[0];
    // Optional z value for bubble size
    const z = Math.random() * (zRange[1] - zRange[0]) + zRange[0];
    
    return {
      x: Math.round(x),
      y: Math.round(y),
      z: Math.round(z),
      name: `Point ${i + 1}`,
    };
  });
};

export const mockHeatmapData = (
  xCategories = ['A', 'B', 'C', 'D', 'E'],
  yCategories = ['1', '2', '3', '4', '5']
) => {
  const data = [];
  
  // Generate a cell for each x,y coordinate
  for (let x = 0; x < xCategories.length; x++) {
    for (let y = 0; y < yCategories.length; y++) {
      // Generate a random value, with some correlation to position
      // to make the heatmap look more realistic
      const baseValue = (x + y) / (xCategories.length + yCategories.length) * 100;
      const randomness = Math.random() * 30 - 15;
      
      data.push({
        x,
        y,
        xLabel: xCategories[x],
        yLabel: yCategories[y],
        value: Math.round(Math.max(0, Math.min(100, baseValue + randomness))),
      });
    }
  }
  
  return data;
};

export const mockGaugeData = (
  value = Math.random() * 100,
  thresholds = [30, 70]
) => {
  return {
    value: Math.round(value),
    min: 0,
    max: 100,
    thresholds,
  };
};

// Export default for convenient imports
const visualizationService = {
  fetchTimeSeriesData,
  fetchCategoricalData,
  fetchMultidimensionalData,
  fetchCorrelationData,
  fetchCorrelationMatrix,
  fetchSelfAwarenessMetrics,
  mockTimeSeriesData,
  mockCategoricalData,
  mockRadarData,
  mockCorrelationData,
  mockHeatmapData,
  mockGaugeData,
};

export default visualizationService;