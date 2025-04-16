import React, { useState, useEffect } from 'react';
import Card from '@/components/common/Card';
import Button from '@/components/common/Button';
import MetricCard from '@/components/dashboard/MetricCard';
import TimeRangeSelector from '@/components/dashboard/TimeRangeSelector';
import LineChart from '@/components/charts/LineChart';
import BarChart from '@/components/charts/BarChart';
import useAppStore from '@/store/appStore';
import visualizationService from '@/services/visualizationService';

// Remove mock data generation functions
// const generateTimeSeriesData = ...
// const generateComparisonData = ...

// Remove Placeholder data for demo metrics
// const MOCK_METRICS = ...

const Dashboard: React.FC = () => {
  const { selectedTimeRange } = useAppStore();
  const [loading, setLoading] = useState(false);
  const [timeSeriesData, setTimeSeriesData] = useState<any[]>([]);
  const [comparisonData, setComparisonData] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch time series data from the API
        const timeSeriesParams = {
          metrics: ['cpu', 'memory', 'network', 'requests'],
          startDate: 'now-' + selectedTimeRange,
          endDate: 'now',
        };
        const timeSeriesResponse = await visualizationService.fetchTimeSeriesData(timeSeriesParams);
        setTimeSeriesData(timeSeriesResponse);

        // Fetch comparison data (replace with actual API call when available)
        // const comparisonParams = { ... };
        // const comparisonDataResponse = await visualizationService.fetchComparisonData(comparisonParams);
        // setComparisonData(comparisonDataResponse);
        setComparisonData([]); // Set to empty array for now

      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedTimeRange]);

  const handleRefresh = () => {
    // ...existing code...
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
        {/* Remove MetricCard components using MOCK_METRICS */}
        {/* Example: */}
        {/* <MetricCard ... /> */}
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