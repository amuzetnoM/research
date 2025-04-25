import React, { useMemo } from 'react';
import { useEnvironmentMonitoring } from '@/hooks/useEnvironmentMonitoring';
import { Card } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Alert } from '@/components/common/Alert';
import { formatBytes, formatNumber, formatPercentage } from '@/utils/formatters';

export const EnvironmentComparison: React.FC = () => {
  // Fetch data for both containers
  const container1 = useEnvironmentMonitoring({ containerId: 'container1' });
  const container2 = useEnvironmentMonitoring({ containerId: 'container2' });

  const isLoading = container1.isLoading || container2.isLoading;
  const isError = container1.isError || container2.isError;
  
  // Calculate performance differences
  const differences = useMemo(() => {
    if (!container1.metrics || !container2.metrics) return null;
    
    return {
      cpu: {
        usage: container2.metrics.cpu.usage - container1.metrics.cpu.usage,
        temperature: container2.metrics.cpu.temperature - container1.metrics.cpu.temperature,
      },
      memory: {
        usagePercentage: container2.metrics.memory.usagePercentage - container1.metrics.memory.usagePercentage,
        used: container2.metrics.memory.used - container1.metrics.memory.used,
      },
      network: {
        bytesIn: container2.metrics.network.bytesIn - container1.metrics.network.bytesIn,
        bytesOut: container2.metrics.network.bytesOut - container1.metrics.network.bytesOut,
      },
      storage: {
        usagePercentage: container2.metrics.storage.usagePercentage - container1.metrics.storage.usagePercentage,
        used: container2.metrics.storage.used - container1.metrics.storage.used,
      }
    };
  }, [container1.metrics, container2.metrics]);

  // Helper for highlighting differences
  const DifferenceIndicator = ({ value, unit = '', reverse = false }: { value: number, unit?: string, reverse?: boolean }) => {
    if (value === 0) return <span className="text-gray-500">0{unit}</span>;
    
    const isPositive = reverse ? value < 0 : value > 0;
    const absValue = Math.abs(value);
    const color = isPositive ? 'text-green-500' : 'text-red-500';
    const arrow = isPositive ? '↑' : '↓';
    
    return (
      <span className={color}>
        {arrow} {absValue.toFixed(2)}{unit}
      </span>
    );
  };

  const refresh = () => {
    container1.refresh();
    container2.refresh();
  };

  if (isLoading) {
    return (
      <Card title="Environment Comparison" className="p-4">
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse text-gray-500">Loading comparison data...</div>
        </div>
      </Card>
    );
  }

  if (isError) {
    return (
      <Card title="Environment Comparison" className="p-4">
        <Alert 
          type="error" 
          title="Failed to load comparison data" 
          message="There was an error retrieving the environment metrics. Please try again."
          action={<Button onClick={refresh}>Retry</Button>}
        />
      </Card>
    );
  }

  if (!container1.metrics || !container2.metrics) {
    return (
      <Card title="Environment Comparison" className="p-4">
        <Alert 
          type="warning" 
          title="Incomplete data" 
          message="Some environment metrics are missing. Data may be partial or unavailable."
          action={<Button onClick={refresh}>Refresh</Button>}
        />
      </Card>
    );
  }

  return (
    <Card 
      title="Environment Comparison" 
      className="p-4"
      actions={
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={refresh} 
          title="Refresh data"
          icon="refresh"
        />
      }
    >
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-100 dark:bg-gray-800">
              <th className="text-left p-2">Metric</th>
              <th className="text-center p-2">Container 1</th>
              <th className="text-center p-2">Container 2</th>
              <th className="text-center p-2">Difference</th>
            </tr>
          </thead>
          <tbody>
            {/* CPU Section */}
            <tr className="bg-gray-50 dark:bg-gray-900 font-medium">
              <td colSpan={4} className="p-2">CPU</td>
            </tr>
            <tr>
              <td className="border p-2">Usage</td>
              <td className="border p-2 text-center">{formatPercentage(container1.metrics.cpu.usage)}</td>
              <td className="border p-2 text-center">{formatPercentage(container2.metrics.cpu.usage)}</td>
              <td className="border p-2 text-center">
                <DifferenceIndicator value={differences.cpu.usage} unit="%" reverse={true} />
              </td>
            </tr>
            <tr>
              <td className="border p-2">Temperature</td>
              <td className="border p-2 text-center">{container1.metrics.cpu.temperature}°C</td>
              <td className="border p-2 text-center">{container2.metrics.cpu.temperature}°C</td>
              <td className="border p-2 text-center">
                <DifferenceIndicator value={differences.cpu.temperature} unit="°C" reverse={true} />
              </td>
            </tr>
            
            {/* Memory Section */}
            <tr className="bg-gray-50 dark:bg-gray-900 font-medium">
              <td colSpan={4} className="p-2">Memory</td>
            </tr>
            <tr>
              <td className="border p-2">Usage</td>
              <td className="border p-2 text-center">{formatPercentage(container1.metrics.memory.usagePercentage)}</td>
              <td className="border p-2 text-center">{formatPercentage(container2.metrics.memory.usagePercentage)}</td>
              <td className="border p-2 text-center">
                <DifferenceIndicator value={differences.memory.usagePercentage} unit="%" reverse={true} />
              </td>
            </tr>
            <tr>
              <td className="border p-2">Used Memory</td>
              <td className="border p-2 text-center">{formatBytes(container1.metrics.memory.used)}</td>
              <td className="border p-2 text-center">{formatBytes(container2.metrics.memory.used)}</td>
              <td className="border p-2 text-center">
                <DifferenceIndicator value={differences.memory.used} unit=" bytes" reverse={true} />
              </td>
            </tr>
            
            {/* Network Section */}
            <tr className="bg-gray-50 dark:bg-gray-900 font-medium">
              <td colSpan={4} className="p-2">Network</td>
            </tr>
            <tr>
              <td className="border p-2">Bytes In</td>
              <td className="border p-2 text-center">{formatBytes(container1.metrics.network.bytesIn)}/s</td>
              <td className="border p-2 text-center">{formatBytes(container2.metrics.network.bytesIn)}/s</td>
              <td className="border p-2 text-center">
                <DifferenceIndicator value={differences.network.bytesIn} unit=" bytes" />
              </td>
            </tr>
            <tr>
              <td className="border p-2">Bytes Out</td>
              <td className="border p-2 text-center">{formatBytes(container1.metrics.network.bytesOut)}/s</td>
              <td className="border p-2 text-center">{formatBytes(container2.metrics.network.bytesOut)}/s</td>
              <td className="border p-2 text-center">
                <DifferenceIndicator value={differences.network.bytesOut} unit=" bytes" />
              </td>
            </tr>
            
            {/* Storage Section */}
            <tr className="bg-gray-50 dark:bg-gray-900 font-medium">
              <td colSpan={4} className="p-2">Storage</td>
            </tr>
            <tr>
              <td className="border p-2">Usage</td>
              <td className="border p-2 text-center">{formatPercentage(container1.metrics.storage.usagePercentage)}</td>
              <td className="border p-2 text-center">{formatPercentage(container2.metrics.storage.usagePercentage)}</td>
              <td className="border p-2 text-center">
                <DifferenceIndicator value={differences.storage.usagePercentage} unit="%" reverse={true} />
              </td>
            </tr>
            <tr>
              <td className="border p-2">Used Storage</td>
              <td className="border p-2 text-center">{formatBytes(container1.metrics.storage.used)}</td>
              <td className="border p-2 text-center">{formatBytes(container2.metrics.storage.used)}</td>
              <td className="border p-2 text-center">
                <DifferenceIndicator value={differences.storage.used} unit=" bytes" reverse={true} />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>
  );
};
