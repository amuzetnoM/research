import { useState, useEffect } from 'react';
import { monitoringService } from '../services/monitoringService';

export const useMetricsData = (timeRange = '24h', refreshInterval = 60000) => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const data = await monitoringService.getMetrics(timeRange);
        setMetrics(data);
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to fetch metrics data');
        console.error('Error fetching metrics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    
    // Set up polling if refreshInterval is provided
    const intervalId = refreshInterval ? setInterval(fetchMetrics, refreshInterval) : null;
    
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [timeRange, refreshInterval]);

  return { metrics, loading, error, refresh: () => setLoading(true) };
};
