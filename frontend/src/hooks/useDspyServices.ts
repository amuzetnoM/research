import { useQuery, useMutation } from '@tanstack/react-query';
import dspyService, {
  MetricsAnalysisRequest,
  ContainerComparisonRequest,
  InsightGenerationRequest,
} from '@/services/dspyService';

/**
 * Custom hook for interacting with DSPy services
 */
export const useDspyServices = () => {
  /**
   * Query hook for getting DSPy status
   */
  const useDspyStatus = () => {
    return useQuery({
      queryKey: ['dspyStatus'],
      queryFn: dspyService.getStatus,
      refetchInterval: 60000, // Refetch every minute
    });
  };

  /**
   * Mutation hook for analyzing metrics
   */
  const useAnalyzeMetrics = () => {
    return useMutation({
      mutationFn: (request: MetricsAnalysisRequest) => dspyService.analyzeMetrics(request),
    });
  };

  /**
   * Mutation hook for comparing containers
   */
  const useCompareContainers = () => {
    return useMutation({
      mutationFn: (request: ContainerComparisonRequest) => dspyService.compareContainers(request),
    });
  };

  /**
   * Mutation hook for generating insights
   */
  const useGenerateInsights = () => {
    return useMutation({
      mutationFn: (request: InsightGenerationRequest) => dspyService.generateInsights(request),
    });
  };

  return {
    useDspyStatus,
    useAnalyzeMetrics,
    useCompareContainers,
    useGenerateInsights,
  };
};

export default useDspyServices;