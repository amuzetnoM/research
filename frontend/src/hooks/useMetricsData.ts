import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import visualizationService from '@/services/visualizationService';

export const useMetricsData = (containerId: string, metrics: string[], timeRange: string) => {
  const queryClient = useQueryClient();
  const [isRealtime, setIsRealtime] = useState(true);

  const { data, error, isLoading } = useQuery({
    queryKey: ['metrics', containerId, metrics, timeRange],
    queryFn: () => visualizationService.fetchContainerMetrics(containerId, metrics, timeRange),
    refetchInterval: isRealtime ? 5000 : false,
    retry: 3,
    staleTime: 4000,
  });

  // Set up WebSocket subscription
  useEffect(() => {
    if (!isRealtime) return;

    const unsubscribe = visualizationService.subscribeToMetrics(metrics, (newData) => {
      queryClient.setQueryData(['metrics', containerId, metrics, timeRange], (old: any) => ({
        ...old,
        ...newData,
      }));
    });

    return () => {
      unsubscribe();
    };
  }, [containerId, metrics, isRealtime, queryClient, timeRange]);

  return {
    data,
    error,
    isLoading,
    isRealtime,
    toggleRealtime: () => setIsRealtime(prev => !prev),
  };
};
