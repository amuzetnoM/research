import React, { useState } from 'react';
import { useEnvironmentMonitoring } from '@/hooks/useEnvironmentMonitoring';
import { Card } from '@/components/common/Card';
import { LineChart } from '@/components/visualizations/LineChart';
import { GaugeChart } from '@/components/charts';
import { Alert } from '@/components/common/Alert';
import { Button } from '@/components/common/Button';
import { Tabs, TabPanel } from '@/components/common/Tabs';
import { formatBytes, formatNumber, formatTimeAgo } from '@/utils/formatters';

interface EnvironmentMonitorProps {
  containerId?: 'container1' | 'container2';
  title?: string;
  className?: string;
}

export const EnvironmentMonitor: React.FC<EnvironmentMonitorProps> = ({
  containerId,
  title = containerId ? `Environment: ${containerId}` : 'Environment Monitor',
  className = '',
}) => {
  const [activeTab, setActiveTab] = useState('overview');
  const { 
    metrics, 
    status, 
    isLoading, 
    isError, 
    lastUpdated, 
    refresh 
  } = useEnvironmentMonitoring({ containerId, useWebSockets: true });

  if (isLoading) {
    return (
      <Card title={title} className={`p-4 ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse text-gray-500">Loading environment data...</div>
        </div>
      </Card>
    );
  }

  if (isError) {
    return (
      <Card title={title} className={`p-4 ${className}`}>
        <Alert 
          type="error" 
          title="Failed to load environment data" 
          message="There was an error retrieving the environment metrics. Please try again."
          action={<Button onClick={refresh}>Retry</Button>}
        />
      </Card>
    );
  }

  // Get status color based on environment health
  const getStatusColor = () => {
    if (!status) return 'gray';
    
    switch (status.status) {
      case 'healthy': return 'green';
      case 'warning': return 'yellow';
      case 'critical': return 'red';
      default: return 'gray';
    }
  };

  return (
    <Card 
      title={title} 
      className={`p-4 ${className}`}
      actions={
        <div className="flex items-center space-x-2">
          <div 
            className={`w-3 h-3 rounded-full bg-${getStatusColor()}-500`} 
            title={status?.status || 'Unknown status'}
          />
          <span className="text-xs text-gray-500">
            {lastUpdated ? `Updated ${formatTimeAgo(lastUpdated)}` : 'Not updated yet'}
          </span>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={refresh} 
            title="Refresh data"
            icon="refresh"
          />
        </div>
      }
    >
      {/* Alerts Section */}
      {status?.alerts && status.alerts.length > 0 && (
        <div className="mb-4">
          {status.alerts.map(alert => (
            <Alert
              key={alert.id}
              type={alert.severity}
              title={alert.type}
              message={alert.message}
              timestamp={new Date(alert.timestamp)}
              dismissible
            />
          ))}
        </div>
      )}

      {/* Tabs Navigation */}
      <Tabs 
        activeTab={activeTab} 
        onChange={setActiveTab}
        tabs={[
          { id: 'overview', label: 'Overview' },
          { id: 'cpu', label: 'CPU' },
          { id: 'memory', label: 'Memory' },
          { id: 'network', label: 'Network' },
          { id: 'storage', label: 'Storage' },
        ]}
      />

      {/* Tab Content */}
      <div className="p-4">
        <TabPanel id="overview" activeTab={activeTab}>
          {metrics && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <h3 className="text-lg font-medium mb-2">CPU Usage</h3>
                <GaugeChart 
                  value={metrics.cpu.usage} 
                  min={0} 
                  max={100}
                  units="%"
                  thresholds={[
                    { value: 60, color: 'green' },
                    { value: 80, color: 'yellow' },
                    { value: 100, color: 'red' },
                  ]}
                />
                <div className="mt-2 text-sm">
                  <div>Temperature: {metrics.cpu.temperature}°C</div>
                  <div>Cores: {metrics.cpu.cores}</div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-medium mb-2">Memory Usage</h3>
                <GaugeChart 
                  value={metrics.memory.usagePercentage} 
                  min={0} 
                  max={100}
                  units="%"
                  thresholds={[
                    { value: 60, color: 'green' },
                    { value: 80, color: 'yellow' },
                    { value: 100, color: 'red' },
                  ]}
                />
                <div className="mt-2 text-sm">
                  <div>Used: {formatBytes(metrics.memory.used)}</div>
                  <div>Free: {formatBytes(metrics.memory.free)}</div>
                  <div>Total: {formatBytes(metrics.memory.total)}</div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-medium mb-2">Disk Usage</h3>
                <GaugeChart 
                  value={metrics.storage.usagePercentage} 
                  min={0} 
                  max={100}
                  units="%"
                  thresholds={[
                    { value: 70, color: 'green' },
                    { value: 85, color: 'yellow' },
                    { value: 100, color: 'red' },
                  ]}
                />
                <div className="mt-2 text-sm">
                  <div>Used: {formatBytes(metrics.storage.used)}</div>
                  <div>Free: {formatBytes(metrics.storage.free)}</div>
                  <div>Total: {formatBytes(metrics.storage.total)}</div>
                </div>
              </div>
              
              <div className="col-span-1 md:col-span-2 lg:col-span-3">
                <h3 className="text-lg font-medium mb-2">System Status</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg">
                    <div className="text-sm text-gray-500">Uptime</div>
                    <div className="text-xl font-semibold">
                      {formatNumber(status?.uptime || 0, { style: 'unit', unit: 'hour' })}
                    </div>
                  </div>
                  
                  <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg">
                    <div className="text-sm text-gray-500">Processes</div>
                    <div className="text-xl font-semibold">
                      {metrics?.processes.running || 0} / {metrics?.processes.total || 0}
                    </div>
                  </div>
                  
                  <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg">
                    <div className="text-sm text-gray-500">Network In</div>
                    <div className="text-xl font-semibold">
                      {formatBytes(metrics?.network.bytesIn || 0)}/s
                    </div>
                  </div>
                  
                  <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg">
                    <div className="text-sm text-gray-500">Network Out</div>
                    <div className="text-xl font-semibold">
                      {formatBytes(metrics?.network.bytesOut || 0)}/s
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </TabPanel>

        {/* More tab panels for CPU, Memory, Network, Storage with detailed metrics */}
        <TabPanel id="cpu" activeTab={activeTab}>
          {/* CPU-specific detailed metrics and charts would go here */}
          <div className="text-center py-12 text-gray-500">
            Detailed CPU metrics visualizations coming soon
          </div>
        </TabPanel>
        
        {/* Similar panels for other tabs */}
      </div>
    </Card>
  );
};
