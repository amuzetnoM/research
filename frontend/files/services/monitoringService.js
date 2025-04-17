import { dataService } from './dataService';

export const monitoringService = {
  // Replace direct API calls with dataService methods
  getSystemHealth: async () => {
    return await dataService.fetchData('monitoring/health');
  },
  
  getMetrics: async (timeRange) => {
    return await dataService.fetchData('monitoring/metrics', { timeRange });
  },
  
  getAlerts: async (status = 'all') => {
    return await dataService.fetchData('monitoring/alerts', { status });
  },
  
  acknowledgeAlert: async (alertId) => {
    return await dataService.updateData(`monitoring/alerts/${alertId}`, { acknowledged: true });
  },
  
  getPerformanceData: async (component, timeFrame) => {
    return await dataService.fetchData('monitoring/performance', { component, timeFrame });
  },
};