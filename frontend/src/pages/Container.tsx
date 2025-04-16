import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Card from '@/components/common/Card';
import Button from '@/components/common/Button';
import Input from '@/components/common/Input';
import TimeRangeSelector from '@/components/dashboard/TimeRangeSelector';
import LineChart from '@/components/charts/LineChart';
import BarChart from '@/components/charts/BarChart';
import GaugeChart from '@/components/charts/GaugeChart';
import useAppStore from '@/store/appStore';
import visualizationService from '@/services/visualizationService';

// Remove mock data generation function
// const generateTimeSeriesData = ...

// Remove Metrics for current container
// const getCurrentMetrics = ...

const Container: React.FC = () => {
  const { containerId } = useParams<{ containerId: string }>();
  const { selectedTimeRange } = useAppStore();
  const [loading, setLoading] = useState(false);
  const [timeSeriesData, setTimeSeriesData] = useState<any[]>([]);
  const [containerMetrics, setContainerMetrics] = useState<any>(null);
  const [dspyAnalysis, setDspyAnalysis] = useState<string>('');
  const [analysisLoading, setAnalysisLoading] = useState(false);

  const containerName = containerId === 'container1' ? 'Container 1' : 'Container 2';

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch container metrics from the API
        // Replace with actual API endpoint
        // const containerMetricsResponse = await apiClient.get(`/api/containers/${containerId}`);
        // setContainerMetrics(containerMetricsResponse.data);
        setContainerMetrics({
          cpu: 42,
          memory: 65,
          network: 1.2,
          disk: 58,
          requests: 256,
          responseTime: 120,
          errorRate: 0.8,
          uptime: '7d 5h 32m',
          status: 'running',
          version: '1.5.2',
          lastRestart: '2025-04-10T08:12:45Z',
        });

        // Fetch time series data from the API
        const timeSeriesParams = {
          metrics: ['cpu', 'memory', 'network', 'requests'],
          startDate: 'now-' + selectedTimeRange,
          endDate: 'now',
        };
        const timeSeriesResponse = await visualizationService.fetchTimeSeriesData(timeSeriesParams);
        setTimeSeriesData(timeSeriesResponse);

      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedTimeRange, containerId]);

  const handleRefresh = () => {
    // ...existing code...
  };

  const handleGenerateAnalysis = () => {
    // ...existing code...
  };

  if (!containerMetrics) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">{containerName}</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Detailed metrics and analysis
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

      {/* Container Info Card */}
      <div className="grid grid-cols-1 gap-6 mb-6">
        <Card title="Container Information">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-4">
              <div>
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400 block mb-1">Status</span>
                <div className="flex items-center">
                  <span className="inline-block w-2 h-2 rounded-full bg-success-500 mr-2"></span>
                  <span className="capitalize">{containerMetrics.status}</span>
                </div>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400 block mb-1">Version</span>
                <span>{containerMetrics.version}</span>
              </div>
            </div>
            <div className="space-y-4">
              <div>
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400 block mb-1">Uptime</span>
                <span>{containerMetrics.uptime}</span>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400 block mb-1">Last Restart</span>
                <span>{new Date(containerMetrics.lastRestart).toLocaleString()}</span>
              </div>
            </div>
            <div className="md:text-right md:flex md:justify-end md:items-center">
              <Button
                variant="ghost"
                size="sm"
                icon={<span className="material-icons-outlined">open_in_new</span>}
              >
                View Logs
              </Button>
            </div>
          </div>
        </Card>
      </div>

      {/* Gauge Charts */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <GaugeChart
          title="CPU Usage"
          value={containerMetrics.cpu}
          unit="%"
          threshold={{ warning: 60, critical: 80 }}
          loading={loading}
        />
        <GaugeChart
          title="Memory Usage"
          value={containerMetrics.memory}
          unit="%"
          threshold={{ warning: 70, critical: 85 }}
          loading={loading}
        />
        <GaugeChart
          title="Disk Usage"
          value={containerMetrics.disk}
          unit="%"
          threshold={{ warning: 75, critical: 90 }}
          loading={loading}
        />
      </div>

      {/* Line Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <LineChart
          title="Resource Usage"
          subtitle={`Last ${selectedTimeRange}`}
          data={timeSeriesData}
          lines={[
            { dataKey: 'cpu', name: 'CPU Usage (%)', color: '#0ea5e9' },
            { dataKey: 'memory', name: 'Memory Usage (%)', color: '#8b5cf6' },
          ]}
          loading={loading}
        />
        <LineChart
          title="Network & Requests"
          subtitle={`Last ${selectedTimeRange}`}
          data={timeSeriesData}
          lines={[
            { dataKey: 'network', name: 'Network Traffic (MB/s)', color: '#10b981' },
            { dataKey: 'requests', name: 'Requests per minute', color: '#f59e0b' },
          ]}
          loading={loading}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <LineChart
          title="Response Time & Error Rate"
          subtitle={`Last ${selectedTimeRange}`}
          data={timeSeriesData}
          lines={[
            { dataKey: 'responseTime', name: 'Response Time (ms)', color: '#6366f1' },
            { dataKey: 'errorRate', name: 'Error Rate (%)', color: '#ef4444' },
          ]}
          loading={loading}
        />
        <Card
          title="DSPy Analysis"
          subtitle="AI-powered insights"
          loading={analysisLoading}
          action={
            <Button
              onClick={handleGenerateAnalysis}
              size="sm"
              variant="primary"
              loading={analysisLoading}
              icon={<span className="material-icons-outlined">psychology</span>}
            >
              Generate
            </Button>
          }
        >
          {dspyAnalysis ? (
            <div className="p-3 border border-gray-200 dark:border-gray-700 rounded-md bg-gray-50 dark:bg-gray-800/50">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                <span className="material-icons-outlined text-sm mr-1 align-middle text-primary-500">psychology</span>
                {dspyAnalysis}
              </p>
            </div>
          ) : (
            <div className="flex items-center justify-center h-32 text-gray-500 dark:text-gray-400">
              Click Generate to analyze container metrics
            </div>
          )}
        </Card>
      </div>

      {/* Event Log */}
      <div className="grid grid-cols-1 gap-6">
        <Card title="Container Events" subtitle="Recent events and alerts">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Time</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Type</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Message</th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">2025-04-16 09:45:12</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-success-100 text-success-800 dark:bg-success-900/20 dark:text-success-400">
                      Info
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">Container health check passed</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">2025-04-16 08:32:05</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-warning-100 text-warning-800 dark:bg-warning-900/20 dark:text-warning-400">
                      Warning
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">High memory usage detected (78%)</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">2025-04-16 07:15:41</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-danger-100 text-danger-800 dark:bg-danger-900/20 dark:text-danger-400">
                      Error
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">Connection timeout to external service</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">2025-04-16 06:02:18</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-success-100 text-success-800 dark:bg-success-900/20 dark:text-success-400">
                      Info
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">Background task completed successfully</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Container;