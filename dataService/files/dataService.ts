// Unified DataService abstraction for all layers (frontend, backend, shared)
// Location: /dataService/dataService.ts
// This module provides a single entry point for all data access, protocol routing, and context protocol (MCP) integration.

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { logger } from '../../frontend/src/utils/logger';

// Protocol types
export type Protocol = 'REST' | 'SSE' | 'WebSocket';

// Cache configuration
interface CacheConfig {
  ttl: number; // Time-to-live in milliseconds
  staleWhileRevalidate: boolean;
}

// Cache entry structure
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
}

// DataService configuration interface
export interface DataServiceConfig {
  defaultProtocol: Protocol;
  featureProtocols?: Record<string, Protocol>;
  endpoints: Record<string, string>;
  baseUrl?: string;
  cache?: {
    enabled: boolean;
    defaultTTL: number;
    endpoints?: Record<string, CacheConfig>;
  };
  debounce?: {
    enabled: boolean;
    defaultDelay: number;
    endpoints?: Record<string, number>;
  };
  performance?: {
    trackRequestSize: boolean;
    trackResponseSize: boolean;
    trackTiming: boolean;
  };
  retry?: {
    enabled: boolean;
    maxRetries: number;
    baseDelay: number;
    exponentialBackoff: boolean;
  };
}

// Context Protocol (MCP) integration
export interface MCPContext {
  sessionId: string;
  userId?: string;
  // ...other context fields
}

// Main DataService class
export class DataService {
  private config: DataServiceConfig;
  private mcpContext?: MCPContext;
  private cache: Map<string, CacheEntry<any>> = new Map();
  private httpClient: AxiosInstance;
  private pendingRequests: Map<string, Promise<any>> = new Map();
  private debounceTimers: Map<string, NodeJS.Timeout> = new Map();

  constructor(config: DataServiceConfig) {
    this.config = {
      ...config,
      cache: {
        enabled: true,
        defaultTTL: 60000, // 1 minute default
        ...config.cache
      },
      debounce: {
        enabled: true,
        defaultDelay: 300, // 300ms default
        ...config.debounce
      },
      performance: {
        trackRequestSize: true,
        trackResponseSize: true,
        trackTiming: true,
        ...config.performance
      },
      retry: {
        enabled: true,
        maxRetries: 3,
        baseDelay: 300,
        exponentialBackoff: true,
        ...config.retry
      }
    };
    
    // Initialize HTTP client with interceptors
    this.httpClient = axios.create({
      baseURL: config.baseUrl || ''
    });
    
    // Add request interceptor for performance tracking
    this.httpClient.interceptors.request.use((request) => {
      if (this.config.performance?.trackTiming) {
        request.headers = request.headers || {};
        request.headers['X-Request-Start'] = Date.now().toString();
      }
      return request;
    });
    
    // Add response interceptor for performance tracking and error handling
    this.httpClient.interceptors.response.use(
      (response) => {
        this.trackPerformance(response);
        return response;
      },
      async (error) => {
        // Log error details
        this.logErrorDetails(error);
        
        // Handle retry logic
        if (this.config.retry?.enabled && this.shouldRetry(error)) {
          return this.retryRequest(error);
        }
        
        return Promise.reject(error);
      }
    );
  }

  // Set or update MCP context
  setContext(context: MCPContext): void {
    this.mcpContext = context;
  }

  // Protocol routing for data fetch
  async fetch<T>(feature: string, params?: any, options?: AxiosRequestConfig): Promise<T> {
    const protocol = this.config.featureProtocols?.[feature] || this.config.defaultProtocol;
    
    // Generate cache key if caching is enabled
    const cacheKey = this.config.cache?.enabled 
      ? this.generateCacheKey(feature, params)
      : null;
    
    // Check cache before making a request
    if (cacheKey) {
      const cachedData = this.getCachedData<T>(cacheKey);
      if (cachedData) {
        // If we have cached data, return it
        return cachedData;
      }
    }
    
    // If there's already a pending request for this cache key, return that promise
    if (cacheKey && this.pendingRequests.has(cacheKey)) {
      return this.pendingRequests.get(cacheKey);
    }
    
    // Implement protocol-specific fetch
    let request: Promise<T>;
    switch (protocol) {
      case 'REST':
        request = this.fetchREST<T>(feature, params, options);
        break;
      case 'SSE':
        request = this.fetchSSE<T>(feature, params);
        break;
      case 'WebSocket':
        request = this.fetchWebSocket<T>(feature, params);
        break;
      default:
        throw new Error(`Unsupported protocol: ${protocol}`);
    }
    
    // Store the pending request
    if (cacheKey) {
      this.pendingRequests.set(cacheKey, request);
      
      // Clean up the pending request when done
      request.finally(() => {
        this.pendingRequests.delete(cacheKey);
      });
    }
    
    return request;
  }

  // REST fetch implementation
  private async fetchREST<T>(feature: string, params?: any, options?: AxiosRequestConfig): Promise<T> {
    const endpoint = this.config.endpoints[feature];
    if (!endpoint) throw new Error(`No endpoint configured for feature: ${feature}`);
    
    // Replace any path parameters in the endpoint
    let url = endpoint;
    if (params && typeof params === 'object') {
      // Handle path parameters like ':id'
      Object.entries(params).forEach(([key, value]) => {
        if (url.includes(`:${key}`)) {
          url = url.replace(`:${key}`, encodeURIComponent(String(value)));
          delete params[key]; // Remove used path parameters
        }
      });
    }
    
    const startTime = Date.now();
    try {
      const response = await this.httpClient.get(url, {
        params,
        ...options
      });
      
      // Cache the response if caching is enabled
      this.cacheResponse(feature, params, response.data);
      
      return response.data;
    } catch (error) {
      throw error;
    } finally {
      const duration = Date.now() - startTime;
      logger.debug(`REST request to ${url} completed in ${duration}ms`, {
        feature,
        duration,
        params
      });
    }
  }

  // SSE fetch implementation
  private fetchSSE<T>(feature: string, params?: any): Promise<T> {
    return new Promise<T>((resolve, reject) => {
      const endpoint = this.config.endpoints[feature];
      if (!endpoint) {
        reject(new Error(`No endpoint configured for feature: ${feature}`));
        return;
      }
      
      let url = endpoint;
      // Add query parameters to URL
      if (params) {
        const queryParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
          queryParams.append(key, String(value));
        });
        url = `${url}?${queryParams.toString()}`;
      }
      
      try {
        const eventSource = new EventSource(url);
        const data: any[] = [];
        
        eventSource.onmessage = (event) => {
          try {
            const parsedData = JSON.parse(event.data);
            data.push(parsedData);
          } catch (error) {
            logger.error('Error parsing SSE data', { error, data: event.data });
          }
        };
        
        eventSource.onerror = (error) => {
          eventSource.close();
          reject(error);
        };
        
        // Configure a timeout for SSE response
        const timeout = setTimeout(() => {
          eventSource.close();
          resolve(data as unknown as T);
        }, 5000); // 5 second timeout for initial data
        
        // Clean up on completion
        eventSource.addEventListener('complete', () => {
          clearTimeout(timeout);
          eventSource.close();
          resolve(data as unknown as T);
        });
      } catch (error) {
        reject(error);
      }
    });
  }

  // WebSocket fetch implementation (stub)
  private async fetchWebSocket<T>(feature: string, params?: any): Promise<T> {
    // Legacy WebSocket implementation - maintained only for backward compatibility
    // New features should use REST or SSE
    logger.warn('WebSocket protocol is deprecated. Use REST or SSE instead.');
    
    const endpoint = this.config.endpoints[feature];
    if (!endpoint) throw new Error(`No endpoint configured for feature: ${feature}`);
    
    throw new Error('WebSocket fetch is deprecated. Use REST or SSE instead.');
  }

  // Debounced API call
  async debounced<T>(feature: string, params?: any, options?: AxiosRequestConfig, delay?: number): Promise<T> {
    if (!this.config.debounce?.enabled) {
      return this.fetch<T>(feature, params, options);
    }
    
    const cacheKey = this.generateCacheKey(feature, params);
    
    // Clear any existing timer for this cache key
    if (this.debounceTimers.has(cacheKey)) {
      clearTimeout(this.debounceTimers.get(cacheKey));
    }
    
    // Set up a new debounced call
    return new Promise<T>((resolve, reject) => {
      const timer = setTimeout(async () => {
        try {
          const result = await this.fetch<T>(feature, params, options);
          resolve(result);
        } catch (error) {
          reject(error);
        } finally {
          this.debounceTimers.delete(cacheKey);
        }
      }, delay || this.getDebounceDelay(feature));
      
      this.debounceTimers.set(cacheKey, timer);
    });
  }

  // Get metrics data with caching
  async getMetrics(containerId: string, params?: any): Promise<any> {
    return this.fetch('metrics', { containerId, ...params });
  }

  // Get dashboard data with prefetching for widgets
  async getDashboard(dashboardId: string, params?: any): Promise<any> {
    const dashboard = await this.fetch('dashboard', { dashboardId, ...params });
    
    // Prefetch widget data if available
    if (dashboard && dashboard.widgets) {
      this.prefetchWidgets(dashboard.widgets);
    }
    
    return dashboard;
  }

  // Prefetch widget data for a dashboard
  private prefetchWidgets(widgetIds: string[]): void {
    widgetIds.forEach(widgetId => {
      // Low priority fetch that doesn't block the main dashboard rendering
      setTimeout(() => {
        this.fetch('widget', { widgetId })
          .catch(error => {
            logger.debug('Widget prefetch failed', { widgetId, error: error.message });
          });
      }, 100);
    });
  }

  // Get MCP session data
  async getContextSession(sessionId: string): Promise<any> {
    return this.fetch('context', { sessionId });
  }

  // Create data using POST
  async createData<T>(feature: string, data: any, options?: AxiosRequestConfig): Promise<T> {
    const endpoint = this.config.endpoints[feature];
    if (!endpoint) throw new Error(`No endpoint configured for feature: ${feature}`);
    
    const startTime = Date.now();
    try {
      const response = await this.httpClient.post(endpoint, data, options);
      this.invalidateRelatedCache(feature);
      return response.data;
    } catch (error) {
      throw error;
    } finally {
      const duration = Date.now() - startTime;
      logger.debug(`POST request to ${endpoint} completed in ${duration}ms`, {
        feature,
        duration
      });
    }
  }

  // Update data using PUT or PATCH
  async updateData<T>(feature: string, data: any, method: 'PUT' | 'PATCH' = 'PUT', options?: AxiosRequestConfig): Promise<T> {
    const endpoint = this.config.endpoints[feature];
    if (!endpoint) throw new Error(`No endpoint configured for feature: ${feature}`);
    
    const startTime = Date.now();
    try {
      const response = method === 'PUT'
        ? await this.httpClient.put(endpoint, data, options)
        : await this.httpClient.patch(endpoint, data, options);
      
      this.invalidateRelatedCache(feature);
      return response.data;
    } catch (error) {
      throw error;
    } finally {
      const duration = Date.now() - startTime;
      logger.debug(`${method} request to ${endpoint} completed in ${duration}ms`, {
        feature,
        duration
      });
    }
  }

  // Delete data
  async deleteData<T>(feature: string, options?: AxiosRequestConfig): Promise<T> {
    const endpoint = this.config.endpoints[feature];
    if (!endpoint) throw new Error(`No endpoint configured for feature: ${feature}`);
    
    const startTime = Date.now();
    try {
      const response = await this.httpClient.delete(endpoint, options);
      this.invalidateRelatedCache(feature);
      return response.data;
    } catch (error) {
      throw error;
    } finally {
      const duration = Date.now() - startTime;
      logger.debug(`DELETE request to ${endpoint} completed in ${duration}ms`, {
        feature,
        duration
      });
    }
  }

  // Upload file with multipart/form-data
  async uploadFile<T>(feature: string, fileData: FormData, options?: AxiosRequestConfig): Promise<T> {
    const endpoint = this.config.endpoints[feature];
    if (!endpoint) throw new Error(`No endpoint configured for feature: ${feature}`);
    
    const config: AxiosRequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      ...options
    };
    
    const startTime = Date.now();
    try {
      const response = await this.httpClient.post(endpoint, fileData, config);
      return response.data;
    } catch (error) {
      throw error;
    } finally {
      const duration = Date.now() - startTime;
      logger.debug(`File upload to ${endpoint} completed in ${duration}ms`, {
        feature,
        duration
      });
    }
  }

  // Batch update multiple items
  async batchUpdate<T>(feature: string, items: any[], options?: AxiosRequestConfig): Promise<T> {
    const endpoint = this.config.endpoints[feature];
    if (!endpoint) throw new Error(`No endpoint configured for feature: ${feature}`);
    
    const startTime = Date.now();
    try {
      const response = await this.httpClient.post(`${endpoint}/batch`, { items }, options);
      this.invalidateRelatedCache(feature);
      return response.data;
    } catch (error) {
      throw error;
    } finally {
      const duration = Date.now() - startTime;
      logger.debug(`Batch update to ${endpoint} completed in ${duration}ms`, {
        feature,
        itemCount: items.length,
        duration
      });
    }
  }

  // Generate a cache key for a request
  private generateCacheKey(feature: string, params?: any): string {
    const endpoint = this.config.endpoints[feature];
    if (!endpoint) return '';
    
    let cacheKey = endpoint;
    if (params) {
      cacheKey += JSON.stringify(params);
    }
    return cacheKey;
  }

  // Get cached data if valid
  private getCachedData<T>(cacheKey: string): T | null {
    if (!this.cache.has(cacheKey)) return null;
    
    const cached = this.cache.get(cacheKey)!;
    const now = Date.now();
    
    // If cache is still valid, return it
    if (now < cached.expiresAt) {
      return cached.data;
    }
    
    // If staleWhileRevalidate is enabled, return stale data
    const endpointConfig = this.getEndpointCacheConfig(cacheKey);
    if (endpointConfig.staleWhileRevalidate) {
      // Asynchronously refresh the cache
      setTimeout(() => {
        const parts = cacheKey.split('?');
        const feature = Object.keys(this.config.endpoints)
          .find(key => this.config.endpoints[key] === parts[0]);
        
        if (feature) {
          const paramsString = parts[1] || '{}';
          try {
            const params = JSON.parse(paramsString);
            this.fetch(feature, params).catch(err => {
              logger.debug('Background cache refresh failed', { feature, error: err.message });
            });
          } catch (e) {
            // Invalid params string, can't refresh
          }
        }
      }, 0);
      
      return cached.data;
    }
    
    // Cache is expired and staleWhileRevalidate is disabled
    this.cache.delete(cacheKey);
    return null;
  }

  // Cache a response
  private cacheResponse(feature: string, params: any, data: any): void {
    if (!this.config.cache?.enabled) return;
    
    const cacheKey = this.generateCacheKey(feature, params);
    const endpointConfig = this.getEndpointCacheConfig(cacheKey);
    
    const now = Date.now();
    this.cache.set(cacheKey, {
      data,
      timestamp: now,
      expiresAt: now + endpointConfig.ttl
    });
  }

  // Invalidate related cache entries when data changes
  private invalidateRelatedCache(feature: string): void {
    if (!this.config.cache?.enabled) return;
    
    const endpoint = this.config.endpoints[feature];
    
    // Delete all cache entries that start with this endpoint
    for (const [key] of this.cache) {
      if (key.startsWith(endpoint)) {
        this.cache.delete(key);
      }
    }
  }

  // Get cache configuration for an endpoint
  private getEndpointCacheConfig(cacheKey: string): CacheConfig {
    if (!this.config.cache?.endpoints) {
      return {
        ttl: this.config.cache?.defaultTTL || 60000,
        staleWhileRevalidate: true
      };
    }
    
    // Find the matching endpoint in the configuration
    const endpoint = Object.keys(this.config.endpoints)
      .find(key => cacheKey.startsWith(this.config.endpoints[key]));
    
    if (!endpoint || !this.config.cache.endpoints[endpoint]) {
      return {
        ttl: this.config.cache.defaultTTL || 60000,
        staleWhileRevalidate: true
      };
    }
    
    return this.config.cache.endpoints[endpoint];
  }

  // Get debounce delay for a feature
  private getDebounceDelay(feature: string): number {
    return this.config.debounce?.endpoints?.[feature] || 
           this.config.debounce?.defaultDelay || 
           300;
  }

  // Track API performance metrics
  private trackPerformance(response: AxiosResponse): void {
    if (!this.config.performance?.trackTiming) return;
    
    const requestStart = response.config.headers?.['X-Request-Start'];
    if (!requestStart) return;
    
    const duration = Date.now() - parseInt(requestStart as string, 10);
    
    const metrics: Record<string, any> = { 
      url: response.config.url,
      method: response.config.method?.toUpperCase(),
      status: response.status,
      duration
    };
    
    // Track request size
    if (this.config.performance.trackRequestSize && response.config.data) {
      const requestSize = this.calculateSize(response.config.data);
      metrics.requestSize = requestSize;
    }
    
    // Track response size
    if (this.config.performance.trackResponseSize && response.data) {
      const responseSize = this.calculateSize(response.data);
      metrics.responseSize = responseSize;
    }
    
    logger.debug('API Request Performance', metrics);
  }

  // Calculate size of data in bytes
  private calculateSize(data: any): number {
    if (typeof data === 'string') {
      return new Blob([data]).size;
    }
    return new Blob([JSON.stringify(data)]).size;
  }

  // Log detailed error information
  private logErrorDetails(error: any): void {
    if (!error.config) {
      logger.error('API Error (non-request)', { error });
      return;
    }
    
    const errorDetails: Record<string, any> = {
      url: error.config.url,
      method: error.config.method?.toUpperCase(),
      status: error.response?.status,
      statusText: error.response?.statusText,
      message: error.message
    };
    
    // Add request data if available
    if (error.config.data) {
      errorDetails.requestData = typeof error.config.data === 'string' 
        ? JSON.parse(error.config.data) 
        : error.config.data;
    }
    
    // Add response data if available
    if (error.response?.data) {
      errorDetails.responseData = error.response.data;
    }
    
    // Add context data
    if (this.mcpContext) {
      errorDetails.context = {
        sessionId: this.mcpContext.sessionId,
        userId: this.mcpContext.userId
      };
    }
    
    logger.error('API Request Failed', errorDetails);
  }

  // Determine if a request should be retried
  private shouldRetry(error: any): boolean {
    // Don't retry if maximum retries exceeded
    if (error.config?.__retryCount >= this.config.retry?.maxRetries) {
      return false;
    }
    
    // Only retry network errors or specific HTTP status codes
    return !error.response || // Network error
           error.response.status >= 500 || // Server error
           error.response.status === 429; // Rate limited
  }

  // Retry a failed request with exponential backoff
  private async retryRequest(error: any): Promise<any> {
    const config = error.config;
    
    // Initialize retry count
    config.__retryCount = config.__retryCount || 0;
    config.__retryCount++;
    
    // Calculate delay with exponential backoff
    const delay = this.config.retry?.exponentialBackoff
      ? this.config.retry.baseDelay * Math.pow(2, config.__retryCount - 1)
      : this.config.retry?.baseDelay;
    
    // Log retry attempt
    logger.debug('Retrying API request', {
      url: config.url,
      attempt: config.__retryCount,
      maxRetries: this.config.retry?.maxRetries,
      delay
    });
    
    // Wait before retrying
    await new Promise(resolve => setTimeout(resolve, delay));
    
    // Make a new request
    return this.httpClient(config);
  }
}

// Example default config
export const defaultDataServiceConfig: DataServiceConfig = {
  defaultProtocol: 'REST',
  featureProtocols: {
    metrics: 'REST',
    dashboard: 'REST', 
    realTimeMetrics: 'SSE',
    context: 'REST',
  },
  endpoints: {
    metrics: '/api/metrics',
    dashboard: '/api/dashboards',
    widget: '/api/widgets',
    realTimeMetrics: '/api/metrics/stream',
    context: '/api/v1/session',
  },
  cache: {
    enabled: true,
    defaultTTL: 60000, // 1 minute
    endpoints: {
      metrics: { ttl: 30000, staleWhileRevalidate: true }, // 30 seconds for metrics
      dashboard: { ttl: 300000, staleWhileRevalidate: true }, // 5 minutes for dashboards
    }
  },
  debounce: {
    enabled: true,
    defaultDelay: 300, // 300ms
    endpoints: {
      search: 500, // 500ms for search
      filter: 300, // 300ms for filters
    }
  },
  retry: {
    enabled: true,
    maxRetries: 3,
    baseDelay: 300,
    exponentialBackoff: true,
  }
};

// Create and export a singleton instance
export const dataService = new DataService(defaultDataServiceConfig);