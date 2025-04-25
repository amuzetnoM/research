import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { logger } from '@/utils/logger';

// API endpoints configuration
export const ENDPOINTS = {
  // Common API endpoints
  metrics: '/metrics',
  status: '/status',
  health: '/health',
  
  // Container specific endpoints
  container1: '/api/container1',
  container2: '/api/container2',
  
  // Prometheus endpoints
  prometheusQuery: '/prometheus/api/v1/query',
  prometheusQueryRange: '/prometheus/api/v1/query_range',
  
  // Grafana endpoints
  grafanaDashboards: '/grafana/api/dashboards',
  
  // Analysis endpoints
  analyzeMetrics: '/api/analyze',
  analyzeContainer: '/api/analyze/container',
  selfAwarenessData: '/api/self-awareness',
};

// Error types for better error handling
export enum ApiErrorType {
  NETWORK = 'NETWORK',
  TIMEOUT = 'TIMEOUT',
  SERVER = 'SERVER',
  AUTH = 'AUTH',
  CLIENT = 'CLIENT',
  UNKNOWN = 'UNKNOWN',
}

// Custom API error class
export class ApiError extends Error {
  public type: ApiErrorType;
  public status?: number;
  public response?: any;

  constructor(message: string, type: ApiErrorType, status?: number, response?: any) {
    super(message);
    this.name = 'ApiError';
    this.type = type;
    this.status = status;
    this.response = response;
    
    // Ensure instanceof works correctly
    Object.setPrototypeOf(this, ApiError.prototype);
  }
}

// Base API client factory
const createApiClient = (baseURL: string, config: AxiosRequestConfig = {}): AxiosInstance => {
  const client = axios.create({
    baseURL,
    timeout: 30000, // 30 seconds
    headers: {
      'Content-Type': 'application/json',
    },
    ...config,
  });

  // Request interceptor
  client.interceptors.request.use(
    (config) => {
      // Add any auth headers or other request modifications here
      logger.debug(`API Request: ${config.method?.toUpperCase()} ${config.url}`, { config });
      return config;
    },
    (error) => {
      logger.error('API Request Error', { error });
      return Promise.reject(
        new ApiError(
          'Request configuration error',
          ApiErrorType.CLIENT,
          undefined,
          error
        )
      );
    }
  );

  // Response interceptor
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      logger.debug('API Response', { 
        status: response.status,
        url: response.config.url,
      });
      return response;
    },
    (error) => {
      if (error.response) {
        // Server responded with error status
        const status = error.response.status;
        let type = ApiErrorType.SERVER;
        
        if (status >= 400 && status < 500) {
          type = status === 401 || status === 403 ? ApiErrorType.AUTH : ApiErrorType.CLIENT;
        }
        
        logger.error(`API Error (${status})`, { 
          url: error.config?.url,
          status,
          data: error.response.data
        });
        
        return Promise.reject(
          new ApiError(
            error.response.data?.message || `Server error (${status})`,
            type,
            status,
            error.response.data
          )
        );
      } else if (error.request) {
        // Request made but no response received
        logger.error('API No Response Error', { 
          url: error.config?.url,
          request: error.request 
        });
        
        const errorType = error.code === 'ECONNABORTED' 
          ? ApiErrorType.TIMEOUT 
          : ApiErrorType.NETWORK;
          
        return Promise.reject(
          new ApiError(
            error.code === 'ECONNABORTED' 
              ? 'Request timeout' 
              : 'Network error, no response received',
            errorType,
            undefined,
            error
          )
        );
      }
      
      // Something else happened in setting up the request
      logger.error('Unexpected API Error', { error });
      return Promise.reject(
        new ApiError(
          error.message || 'Unknown API error',
          ApiErrorType.UNKNOWN,
          undefined,
          error
        )
      );
    }
  );

  return client;
};

// Create the base API client
export const apiClient = createApiClient('/api');

// Factory function to create container-specific clients
export const getContainerClient = (containerId: string): AxiosInstance => {
  return createApiClient(`/api/${containerId}`);
};

// Create service-specific clients
export const prometheusClient = createApiClient('/prometheus');
export const grafanaClient = createApiClient('/grafana');

// Helper to build query parameters
export const buildQueryParams = (params: Record<string, any>): string => {
  const queryParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      queryParams.append(key, String(value));
    }
  });
  
  return queryParams.toString() ? `?${queryParams.toString()}` : '';
};

export default apiClient;
