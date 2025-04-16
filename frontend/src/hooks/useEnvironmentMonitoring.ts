import { useState, useEffect, useCallback, useRef } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/services/api';
import { createEnvironmentMonitoringSocket } from '@/services/websocketService';
import { logger } from '@/utils/logger';

export interface EnvironmentMetrics {
  cpu: {
    usage: number;
    temperature: number;
    cores: number;
  };
  memory: {
    total: number;
    used: number;
    free: number;
    usagePercentage: number;
  };
  network: {
    bytesIn: number;
    bytesOut: number;
    packetsIn: number;
    packetsOut: number;
  };
  storage: {
    total: number;
    used: number;
    free: number;
    usagePercentage: number;
  };
  processes: {
    total: number;
    running: number;
  };
  timestamp: string;
}

export interface SystemStatus {
  status: 'healthy' | 'warning' | 'critical' | 'unknown';
  uptime: number;
  alerts: {
    id: string;
    type: string;
    message: string;
    severity: 'info' | 'warning' | 'error' | 'critical';
    timestamp: string;
  }[];
}

export interface UseEnvironmentMonitoringOptions {
  containerId?: 'container1' | 'container2';
  pollingInterval?: number;
  useWebSockets?: boolean;
}

export interface EnvironmentMonitoringResult {
  metrics: EnvironmentMetrics | null;
  status: SystemStatus | null;
  isLoading: boolean;
  isError: boolean;
  error: unknown;
  lastUpdated: Date | null;
  refresh: () => void;
}

export function useEnvironmentMonitoring({
  containerId,
  pollingInterval = 5000,
  useWebSockets = true
}: UseEnvironmentMonitoringOptions = {}): EnvironmentMonitoringResult {
  const queryClient = useQueryClient();
  const webSocketRef = useRef<ReturnType<typeof createEnvironmentMonitoringSocket> | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // API endpoint based on container ID
  const metricsEndpoint = containerId 
    ? `/monitoring/${containerId}/metrics` 
    : '/monitoring/metrics';
    
  const statusEndpoint = containerId 
    ? `/monitoring/${containerId}/status` 
    : '/monitoring/status';

  // Fetch metrics data
  const { 
    data: metrics,
    isLoading: isMetricsLoading,
    isError: isMetricsError,
    error: metricsError,
    refetch: refetchMetrics
  } = useQuery({
    queryKey: ['environment', 'metrics', containerId],
    queryFn: async () => {
      const response = await apiClient.get<EnvironmentMetrics>(metricsEndpoint);
      return response.data;
    },
    enabled: true,
    refetchInterval: useWebSockets ? false : pollingInterval,
    staleTime: 1000, // Consider data stale after 1 second
  });

  // Fetch system status
  const { 
    data: status,
    isLoading: isStatusLoading,
    isError: isStatusError,
    error: statusError,
    refetch: refetchStatus
  } = useQuery({
    queryKey: ['environment', 'status', containerId],
    queryFn: async () => {
      const response = await apiClient.get<SystemStatus>(statusEndpoint);
      return response.data;
    },
    enabled: true,
    refetchInterval: useWebSockets ? false : pollingInterval,
    staleTime: 1000, // Consider data stale after 1 second
  });

  // Set up WebSocket connection if enabled
  useEffect(() => {
    if (!useWebSockets) return;

    // Create WebSocket connection
    const socket = createEnvironmentMonitoringSocket(containerId);
    webSocketRef.current = socket;
    
    // Connect to WebSocket
    socket.connect();
    
    // Set up event handlers
    const unsubscribeMetrics = socket.onMessage('metrics', (data: EnvironmentMetrics) => {
      // Update the cache with fresh data from WebSocket
      queryClient.setQueryData(['environment', 'metrics', containerId], data);
      setLastUpdated(new Date());
    });
    
    const unsubscribeStatus = socket.onMessage('status', (data: SystemStatus) => {
      // Update the cache with fresh data from WebSocket
      queryClient.setQueryData(['environment', 'status', containerId], data);
      setLastUpdated(new Date());
    });
    
    // Cleanup
    return () => {
      unsubscribeMetrics();
      unsubscribeStatus();
      socket.disconnect();
    };
  }, [containerId, queryClient, useWebSockets]);

  // Combined refresh function
  const refresh = useCallback(() => {
    refetchMetrics();
    refetchStatus();
    setLastUpdated(new Date());
  }, [refetchMetrics, refetchStatus]);

  // Update lastUpdated when data changes
  useEffect(() => {
    if (metrics || status) {
      setLastUpdated(new Date());
    }
  }, [metrics, status]);

  return {
    metrics: metrics || null,
    status: status || null,
    isLoading: isMetricsLoading || isStatusLoading,
    isError: isMetricsError || isStatusError,
    error: metricsError || statusError,
    lastUpdated,
    refresh
  };
}
