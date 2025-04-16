import React, { useState, useEffect } from 'react';
import Card from '@/components/common/Card';
import Button from '@/components/common/Button';
import MetricCard from '@/components/dashboard/MetricCard';
import TimeRangeSelector from '@/components/dashboard/TimeRangeSelector';
import LineChart from '@/components/charts/LineChart';
import BarChart from '@/components/charts/BarChart';
import useAppStore from '@/store/appStore';

// Generate sample time-series data
const generateTimeSeriesData = (points = 24, interval = 3600000) => {
  const now = Date.now();
  const result = [];
  
  for (let i = points - 1; i >= 0; i--) {
    const timestamp = now - i * interval;
    result.push({
      timestamp,
      cpu: Math.round(Math.random() * 30 + 20), // CPU: 20-50%
      memory: Math.round(Math.random() * 25 + 50), // Memory: 50-75%
      network: parseFloat((Math.random() * 1.5 + 0.5).toFixed(2)), // Network: 0.5-2.0 MB/s
      requests: Math.round(Math.random() * 150 + 150), // Requests: 150-300 req/min
    });
  }
  
  return result;
};

// Generate sample comparison data
const generateComparisonData = () => [
  {
    name: 'CPU Usage',
    container1: 42,
    container2: 35,
  },
  {
    name: 'Memory Usage',
    container1: 65,
    container2: 58,
  },
  {
    name: 'Network I/O',
    container1: 1.2,
    container2: 0.9,
  },
  {
    name: 'Disk I/O',
    container1: 5.8,
    container2: 4.3,
  },
  {
    name: 'Request Rate',
    container1: 256,
    container2: 187,
  },
  {
    name: 'Response Time',
    container1: 120,
    container2: 145,
  },
];

// Placeholder data for demo metrics
const MOCK_METRICS = {
  cpu: { current: 42, previous: 38, change: 10.5 },
  memory: { current: 65, previous: 72, change: -9.7 },
  network: { current: 1.2, previous: 0.8, change: 50.0 },
  requests: { current: 256, previous: 212, change: 20.8 },
};

const Dashboard: React.FC = () => {
  const { selectedTimeRange } = useAppStore();
  const [loading, setLoading] = useState(false);
  const [timeSeriesData, setTimeSeriesData] = useState<any[]>([]);
  const [comparisonData, setComparisonData] = useState<any[]>([]);

  // Generate initial data
  useEffect(() => {
    // Generate different amounts of data based on selected time range
    const getPointsForTimeRange = (range: string): number => {
      switch (range) {
        case '1h': return 60; // 1 point per minute
        case '6h': return 72; // 1 point per 5 minutes
        case '12h': return 72; // 1 point per 10 minutes
        case '24h': return 96; // 1 point per 15 minutes
        case '7d': return 84; // 1 point per 2 hours
        case '30d': return 90; // 1 point per 8 hours
        default: return 24;
      }
    };

    // Generate different intervals based on selected time range
    const getIntervalForTimeRange = (range: string): number => {
      switch (range) {
        case '1h': return 60 * 1000; // 1 minute
        case '6h': return 5 * 60 * 1000; // 5 minutes
        case '12h': return 10 * 60 * 1000; // 10 minutes
        case '24h': return 15 * 60 * 1000; // 15 minutes
        case '7d': return 2 * 60 * 60 * 1000; // 2 hours
        case '30d': return 8 * 60 * 60 * 1000; // 8 hours
        default: return 60 * 60 * 1000; // 1 hour
      }
    };

    const points = getPointsForTimeRange(selectedTimeRange);
    const interval = getIntervalForTimeRange(selectedTimeRange);
    
    setTimeSeriesData(generateTimeSeriesData(points, interval));
    setComparisonData(generateComparisonData());
  }, [selectedTimeRange]);

  const handleRefresh = () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      // Generate new data with the same parameters
      const getPointsForTimeRange = (range: string): number => {
        switch (range) {
          case '1h': return 60;
          case '6h': return 72;
          case '12h': return 72;
          case '24h': return 96;
          case '7d': return 84;
          case '30d': return 90;
          default: return 24;
        }
      };

      const getIntervalForTimeRange = (range: string): number => {
        switch (range) {
          case '1h': return 60 * 1000;
          case '6h': return 5 * 60 * 1000;
          case '12h': return 10 * 60 * 1000;
          case '24h': return 15 * 60 * 1000;
          case '7d': return 2 * 60 * 60 * 1000;
          case '30d': return 8 * 60 * 60 * 1000;
          default: return 60 * 60 * 1000;
        }
      };

      const points = getPointsForTimeRange(selectedTimeRange);
      const interval = getIntervalForTimeRange(selectedTimeRange);
      
      setTimeSeriesData(generateTimeSeriesData(points, interval));
      setComparisonData(generateComparisonData());
      setLoading(false);
    }, 1500);
  };

  return (
    <div>
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Research Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Monitor and analyze research container metrics
          </p>
        </div>
        <div className="mt-4 md:mt-0 flex flex-col sm:flex-row gap-3 items-center">
          <TimeRangeSelector />
          <Button 
            onClick={handleRefresh}
            icon={<span className="material-icons-outlined">refresh</span>}
            loading={loading}
            variant="primary"
            size="sm"
          >
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <MetricCard 
          title="CPU Usage"
          value={MOCK_METRICS.cpu.current}
          previousValue={MOCK_METRICS.cpu.previous}
          unit="%"
          icon="memory"
          change={MOCK_METRICS.cpu.change}
          changeTimeframe={`vs previous ${selectedTimeRange}`}
          loading={loading}
        />
        <MetricCard 
          title="Memory Usage"
          value={MOCK_METRICS.memory.current}
          previousValue={MOCK_METRICS.memory.previous}
          unit="%"
          icon="storage"
          change={MOCK_METRICS.memory.change}
          changeTimeframe={`vs previous ${selectedTimeRange}`}
          loading={loading}
        />
        <MetricCard 
          title="Network Traffic"
          value={MOCK_METRICS.network.current}
          previousValue={MOCK_METRICS.network.previous}
          unit="MB/s"
          icon="lan"
          change={MOCK_METRICS.network.change}
          changeTimeframe={`vs previous ${selectedTimeRange}`}
          loading={loading}
        />
        <MetricCard 
          title="Requests"
          value={MOCK_METRICS.requests.current}
          previousValue={MOCK_METRICS.requests.previous}
          unit="req/min"
          icon="swap_calls"
          change={MOCK_METRICS.requests.change}
          changeTimeframe={`vs previous ${selectedTimeRange}`}
          loading={loading}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <LineChart
          title="Performance Metrics"
          subtitle={`Last ${selectedTimeRange}`}
          data={timeSeriesData}
          lines={[
            { dataKey: 'cpu', name: 'CPU Usage', color: '#0ea5e9' },
            { dataKey: 'memory', name: 'Memory Usage', color: '#8b5cf6' },
          ]}
          yAxisUnit="%"
          loading={loading}
        />
        <LineChart
          title="Network & Request Activity"
          subtitle={`Last ${selectedTimeRange}`}
          data={timeSeriesData}
          lines={[
            { dataKey: 'network', name: 'Network Traffic (MB/s)', color: '#10b981' },
            { dataKey: 'requests', name: 'Requests per minute', color: '#f59e0b' },
          ]}
          loading={loading}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 mb-6">
        <BarChart
          title="Container Comparison"
          subtitle="Container 1 vs Container 2"
          data={comparisonData}
          bars={[
            { dataKey: 'container1', name: 'Container 1', color: '#0ea5e9' },
            { dataKey: 'container2', name: 'Container 2', color: '#8b5cf6' },
          ]}
          loading={loading}
        />
      </div>

      <div className="grid grid-cols-1 gap-6">
        <Card 
          title="DSPy Analysis Insights" 
          subtitle="AI-powered analysis of container metrics"
          loading={loading}
        >
          <div className="space-y-4">
            <div className="p-3 border border-gray-200 dark:border-gray-700 rounded-md bg-gray-50 dark:bg-gray-800/50">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                <span className="material-icons-outlined text-sm mr-1 align-middle text-primary-500">psychology</span>
                Container 1 shows a 10.5% increase in CPU usage over the last {selectedTimeRange}, which correlates with the increased request volume.
              </p>
            </div>
            <div className="p-3 border border-gray-200 dark:border-gray-700 rounded-md bg-gray-50 dark:bg-gray-800/50">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                <span className="material-icons-outlined text-sm mr-1 align-middle text-primary-500">psychology</span>
                Memory usage has decreased by 9.7%, suggesting recent optimization efforts have been effective.
              </p>
            </div>
            <div className="p-3 border border-gray-200 dark:border-gray-700 rounded-md bg-gray-50 dark:bg-gray-800/50">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                <span className="material-icons-outlined text-sm mr-1 align-middle text-primary-500">psychology</span>
                Network traffic has increased significantly (50%), which may indicate a need for bandwidth optimization.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;