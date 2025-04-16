import React, { useEffect, useState } from 'react';
import Card from '@/components/common/Card';
import { LineChart, GaugeChart } from '@/components/charts';
import visualizationService from '@/services/visualizationService';

interface MetricsDisplayProps {
  containerId: string;
  metrics: string[];
  refreshInterval?: number;
  className?: string;
}

const MetricsDisplay: React.FC<MetricsDisplayProps> = ({
  containerId,
  metrics,
  refreshInterval = 15000,
  className = '',
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metricsData, setMetricsData] = useState<Record<string, any>>({});

  const fetchMetrics = async () => {
    try {
      const data = await visualizationService.fetchContainerMetrics(containerId, metrics);
      setMetricsData(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch metrics');
      console.error('Error fetching metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, refreshInterval);
    return () => clearInterval(interval);
  }, [containerId, metrics.join(',')]);

  return (
    <Card
      title="Container Metrics"
      className={className}
      loading={loading}
      error={error}
    >
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {metrics.map(metric => (
          <div key={metric} className="p-4 border rounded-lg dark:border-gray-700">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {metric.replace(/_/g, ' ').toUpperCase()}
            </h3>
            {metricsData[metric] && (
              <div className="text-2xl font-semibold">
                {metricsData[metric].value.toFixed(2)}
                <span className="text-sm text-gray-500 ml-1">%</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
};

export default MetricsDisplay;
