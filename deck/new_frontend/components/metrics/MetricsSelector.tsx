import React, { useState, useEffect } from 'react';
import Card from '@/components/common/Card';
import Input from '@/components/common/Input';
import Button from '@/components/common/Button';

interface MetricGroup {
  name: string;
  metrics: string[];
}

interface MetricsSelectorProps {
  selectedMetrics: string[];
  onMetricsChange: (metrics: string[]) => void;
  loading?: boolean;
  error?: string | null;
}

const METRIC_GROUPS: MetricGroup[] = [
  {
    name: 'System',
    metrics: ['cpu_usage', 'memory_usage', 'disk_usage', 'network_io'],
  },
  {
    name: 'Application',
    metrics: ['request_count', 'response_time', 'error_rate', 'success_rate'],
  },
  {
    name: 'Research',
    metrics: ['training_progress', 'validation_accuracy', 'loss_value', 'convergence_rate'],
  },
];

const MetricsSelector: React.FC<MetricsSelectorProps> = ({
  selectedMetrics,
  onMetricsChange,
  loading = false,
  error = null,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [availableMetrics, setAvailableMetrics] = useState<MetricGroup[]>(METRIC_GROUPS);

  const handleMetricToggle = (metric: string) => {
    const newSelection = selectedMetrics.includes(metric)
      ? selectedMetrics.filter(m => m !== metric)
      : [...selectedMetrics, metric];
    onMetricsChange(newSelection);
  };

  const handleSearch = (term: string) => {
    setSearchTerm(term);
    if (!term) {
      setAvailableMetrics(METRIC_GROUPS);
      return;
    }

    const filtered = METRIC_GROUPS.map(group => ({
      ...group,
      metrics: group.metrics.filter(metric => 
        metric.toLowerCase().includes(term.toLowerCase())
      ),
    })).filter(group => group.metrics.length > 0);

    setAvailableMetrics(filtered);
  };

  return (
    <Card
      title="Metrics Selection"
      subtitle="Select metrics to display"
      loading={loading}
      error={error}
    >
      <div className="space-y-4">
        <Input
          placeholder="Search metrics..."
          value={searchTerm}
          onChange={(e) => handleSearch(e.target.value)}
          leftIcon={<span className="material-icons-outlined text-gray-400">search</span>}
          fullWidth
        />
        
        <div className="space-y-6">
          {availableMetrics.map((group) => (
            <div key={group.name} className="space-y-2">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {group.name}
              </h3>
              <div className="grid grid-cols-2 gap-2">
                {group.metrics.map((metric) => (
                  <Button
                    key={metric}
                    variant={selectedMetrics.includes(metric) ? 'primary' : 'ghost'}
                    size="sm"
                    onClick={() => handleMetricToggle(metric)}
                    className="justify-start"
                  >
                    <span className="material-icons-outlined text-sm mr-2">
                      {selectedMetrics.includes(metric) ? 'check_box' : 'check_box_outline_blank'}
                    </span>
                    {metric.replace(/_/g, ' ')}
                  </Button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
};

export default MetricsSelector;
