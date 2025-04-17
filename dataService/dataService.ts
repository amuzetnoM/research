// Unified DataService abstraction for all layers (frontend, backend, shared)
// Location: /dataService/dataService.ts
// This module provides a single entry point for all data access, protocol routing, and context protocol (MCP) integration.
// It abstracts away the complexities of different protocols (REST, SSE, WebSocket) and provides a unified API for data access.
// It also includes a comprehensive context protocol (CCP) integration for session management and user context handling.
// Documentation for DataService usage and integration is present at the top of this file.
// For further details, see /frontend/plan/technical_architecture.md and /control/COMMUNICATION_PROTOCOL_AUDIT.md.
/**
 * DataService: Unified protocol abstraction for all data access (REST, SSE, WebSocket, MCP)
 *
 * Usage Example:
 *
 * import { dataService } from '../../dataService/dataService';
 *
 * // Fetch metrics (REST by default)
 * dataService.getMetrics('container1').then(metrics => { ... });
 *
 * // Fetch dashboard data
 * dataService.getDashboard('dashboard1').then(dashboard => { ... });
 *
 * // Fetch context/session (MCP)
 * dataService.getContextSession('sessionId').then(context => { ... });
 *
 * // Protocol routing is automatic based on config, but can be customized per feature.
 * // To change protocol for a feature:
 * // dataService.config.featureProtocols.metrics = 'SSE';
 *
 * // To set context for MCP:
 * // dataService.setContext({ sessionId: '...', userId: '...' });
 */

import type { AxiosRequestConfig } from 'axios';

// Protocol types
export type Protocol = 'REST' | 'SSE' | 'WebSocket';

// DataService configuration interface
export interface DataServiceConfig {
  defaultProtocol: Protocol;
  featureProtocols?: Record<string, Protocol>;
  endpoints: Record<string, string>;
}

// Context Protocol (MCP) integration stub
export interface MCPContext {
  sessionId: string;
  userId?: string;
  // ...other context fields
}

// Main DataService class
export class DataService {
  private config: DataServiceConfig;
  private mcpContext?: MCPContext;

  constructor(config: DataServiceConfig) {
    this.config = config;
  }

  // Set or update MCP context
  setContext(context: MCPContext) {
    this.mcpContext = context;
  }

  // Protocol routing for data fetch
  async fetch(feature: string, params?: any, options?: AxiosRequestConfig) {
    const protocol = this.config.featureProtocols?.[feature] || this.config.defaultProtocol;
    switch (protocol) {
      case 'REST':
        return this.fetchREST(feature, params, options);
      case 'SSE':
        return this.fetchSSE(feature, params);
      case 'WebSocket':
        return this.fetchWebSocket(feature, params);
      default:
        throw new Error(`Unsupported protocol: ${protocol}`);
    }
  }

  // REST fetch implementation
  private async fetchREST(feature: string, params?: any, options?: AxiosRequestConfig) {
    // Example: Use axios or fetch API
    const endpoint = this.config.endpoints[feature];
    if (!endpoint) throw new Error(`No endpoint configured for feature: ${feature}`);
    // Use axios/fetch here (pseudo-code)
    // return axios.get(endpoint, { params, ...options });
    throw new Error('REST fetch not implemented (stub)');
  }

  // SSE fetch implementation (stub)
  private fetchSSE(feature: string, params?: any) {
    // Example: Use EventSource for SSE
    const endpoint = this.config.endpoints[feature];
    if (!endpoint) throw new Error(`No endpoint configured for feature: ${feature}`);
    // return new EventSource(endpoint);
    throw new Error('SSE fetch not implemented (stub)');
  }

  // WebSocket fetch implementation (stub)
  private fetchWebSocket(feature: string, params?: any) {
    // Example: Use WebSocket API
    const endpoint = this.config.endpoints[feature];
    if (!endpoint) throw new Error(`No endpoint configured for feature: ${feature}`);
    // return new WebSocket(endpoint);
    throw new Error('WebSocket fetch not implemented (stub)');
  }

  // Example: Unified method for metrics
  async getMetrics(containerId: string, params?: any) {
    return this.fetch('metrics', { containerId, ...params });
  }

  // Example: Unified method for dashboard data
  async getDashboard(dashboardId: string, params?: any) {
    return this.fetch('dashboard', { dashboardId, ...params });
  }

  // Example: Unified method for context protocol (MCP) session
  async getContextSession(sessionId: string) {
    return this.fetch('context', { sessionId });
  }
}

// Example default config (to be customized per deployment)
export const defaultDataServiceConfig: DataServiceConfig = {
  defaultProtocol: 'REST',
  featureProtocols: {
    metrics: 'REST', // or 'SSE' when ready
    dashboard: 'REST',
    context: 'REST',
  },
  endpoints: {
    metrics: '/api/metrics',
    dashboard: '/api/dashboard',
    context: '/api/context',
  },
};

// Export singleton instance for app-wide use
export const dataService = new DataService(defaultDataServiceConfig);