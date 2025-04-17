import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import visualizationService from '@/services/visualizationService';

export const useMetricsData = (containerId: string, metrics: string[], timeRange: string) => {
  const queryClient = useQueryClient();
  // Only REST polling is used for real-time updates
  const [isRealtime, setIsRealtime] = useState(true);

  const { data, error, isLoading } = useQuery({
    queryKey: ['metrics', containerId, metrics, timeRange],
    queryFn: () => visualizationService.fetchContainerMetrics(containerId, metrics, timeRange),
    refetchInterval: isRealtime ? 5000 : false,
    retry: 3,
    staleTime: 4000,
  });

  return {
    data,
    error,
    isLoading,
    isRealtime,
    toggleRealtime: () => setIsRealtime(prev => !prev),
  };
};
