import apiClient from './api';

/**
 * Types for DSPy API requests and responses
 */
export interface DspyStatusResponse {
  status: 'active' | 'inactive';
  message: string;
}

export interface MetricsAnalysisRequest {
  metrics: Record<string, number>;
  context: string;
}

export interface MetricsAnalysisResponse {
  analysis: string;
  metrics: Record<string, number>;
  success: boolean;
}

export interface ContainerComparisonRequest {
  container1_metrics: Record<string, number>;
  container2_metrics: Record<string, number>;
  metric_name: string;
}

export interface ContainerComparisonResponse {
  comparison: string;
  recommendation: string;
  success: boolean;
}

export interface InsightGenerationRequest {
  data: Record<string, any>;
  context: string;
}

export interface InsightGenerationResponse {
  insights: string[];
  summary: string;
  success: boolean;
}

/**
 * Service for interacting with the DSPy API
 */
const dspyService = {
  /**
   * Get DSPy status
   */
  getStatus: async (): Promise<DspyStatusResponse> => {
    const response = await apiClient.get<DspyStatusResponse>('/dspy/status');
    return response.data;
  },

  /**
   * Analyze metrics using DSPy
   */
  analyzeMetrics: async (request: MetricsAnalysisRequest): Promise<MetricsAnalysisResponse> => {
    const response = await apiClient.post<MetricsAnalysisResponse>('/dspy/analyze-metrics', request);
    return response.data;
  },

  /**
   * Compare containers using DSPy
   */
  compareContainers: async (request: ContainerComparisonRequest): Promise<ContainerComparisonResponse> => {
    const response = await apiClient.post<ContainerComparisonResponse>('/dspy/compare-containers', request);
    return response.data;
  },

  /**
   * Generate insights using DSPy
   */
  generateInsights: async (request: InsightGenerationRequest): Promise<InsightGenerationResponse> => {
    const response = await apiClient.post<InsightGenerationResponse>('/dspy/generate-insights', request);
    return response.data;
  },
};

export default dspyService;