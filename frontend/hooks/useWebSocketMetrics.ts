import { useState, useEffect, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';

// LEGACY: This hook uses WebSocket for real-time metrics. Deprecated in favor of REST polling/SSE.
// TODO: Remove or refactor to use SSE after backend integration.

interface WebSocketMetricsOptions {
  url: string;
  topics?: string[];
  onMessage?: (data: any) => void;
  onError?: (error: any) => void;
  reconnectInterval?: number;
  maxRetries?: number;
}

export const useWebSocketMetrics = ({
  url,
  topics = [],
  onMessage,
  onError,
  reconnectInterval = 3000,
  maxRetries = 5
}: WebSocketMetricsOptions) => {
  const [connected, setConnected] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const queryClient = useQueryClient();

  const connect = useCallback(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setConnected(true);
      setRetryCount(0);
      if (topics.length) {
        ws.send(JSON.stringify({ type: 'subscribe', topics }));
      }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        queryClient.setQueryData(['metrics'], (old: any) => ({
          ...old,
          ...data
        }));
        onMessage?.(data);
      } catch (error) {
        console.error('WebSocket message error:', error);
        onError?.(error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      onError?.(error);
    };

    ws.onclose = () => {
      setConnected(false);
      if (retryCount < maxRetries) {
        setTimeout(() => {
          setRetryCount(prev => prev + 1);
          connect();
        }, reconnectInterval);
      }
    };

    return ws;
  }, [url, topics, onMessage, onError, retryCount, maxRetries, reconnectInterval, queryClient]);

  useEffect(() => {
    const ws = connect();
    return () => {
      ws.close();
    };
  }, [connect]);

  return { connected, retryCount };
};
