import React from 'react';
import {
  ScatterChart as RechartsScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  TooltipProps,
  ZAxis,
} from 'recharts';
import Card from '@/components/common/Card';

interface DataPoint {
  x: number;
  y: number;
  z?: number;
  name?: string;
  [key: string]: any;
}

interface ScatterPlotProps {
  data: {
    name: string;
    color?: string;
    data: DataPoint[];
  }[];
  title?: string;
  subtitle?: string;
  height?: number | string;
  loading?: boolean;
  error?: string | null;
  className?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  xAxisUnit?: string;
  yAxisUnit?: string;
  showGrid?: boolean;
  showBubbles?: boolean;
  bubbleSizeRange?: [number, number];
}

const DEFAULT_COLORS = [
  '#0ea5e9', // primary-500
  '#8b5cf6', // secondary-500
  '#10b981', // success-500
  '#f59e0b', // warning-500
  '#ef4444', // danger-500
  '#6366f1', // indigo-500
  '#ec4899', // pink-500
  '#14b8a6', // teal-500
];

const ScatterPlot: React.FC<ScatterPlotProps> = ({
  data,
  title,
  subtitle,
  height = 400,
  loading = false,
  error = null,
  className = '',
  xAxisLabel = 'X-Axis',
  yAxisLabel = 'Y-Axis',
  xAxisUnit = '',
  yAxisUnit = '',
  showGrid = true,
  showBubbles = false,
  bubbleSizeRange = [10, 60],
}) => {
  // Find min and max values for z-axis if showing bubbles
  let minZ = 0;
  let maxZ = 0;
  
  if (showBubbles) {
    const allZ = data.flatMap(series => series.data.map(point => point.z || 0));
    minZ = Math.min(...allZ);
    maxZ = Math.max(...allZ);
  }

  // Custom tooltip formatter
  const CustomTooltip = ({ active, payload }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      const point = payload[0];
      const seriesName = point.payload.seriesName;
      const pointName = point.payload.name || '';
      
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 shadow-md rounded-md">
          {seriesName && (
            <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
              {seriesName}
            </p>
          )}
          {pointName && (
            <p className="text-xs text-gray-700 dark:text-gray-300 mb-1">{pointName}</p>
          )}
          <div className="space-y-1">
            <div className="flex items-center">
              <span className="text-xs">
                {xAxisLabel}: {point.payload.x}
                {xAxisUnit}
              </span>
            </div>
            <div className="flex items-center">
              <span className="text-xs">
                {yAxisLabel}: {point.payload.y}
                {yAxisUnit}
              </span>
            </div>
            {showBubbles && point.payload.z !== undefined && (
              <div className="flex items-center">
                <span className="text-xs">
                  Size: {point.payload.z}
                </span>
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <Card
      title={title}
      subtitle={subtitle}
      className={className}
      loading={loading}
      error={error}
    >
      <div style={{ width: '100%', height }}>
        {data.some(series => series.data.length > 0) ? (
          <ResponsiveContainer width="100%" height="100%">
            <RechartsScatterChart
              margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
            >
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />}
              <XAxis 
                type="number" 
                dataKey="x" 
                name={xAxisLabel}
                unit={xAxisUnit}
                stroke="#9ca3af"
                tick={{ fontSize: 12 }}
                label={{ 
                  value: xAxisLabel,
                  position: 'insideBottom',
                  offset: -10,
                  style: { fontSize: '12px', fill: '#9ca3af' }
                }}
              />
              <YAxis 
                type="number" 
                dataKey="y" 
                name={yAxisLabel}
                unit={yAxisUnit}
                stroke="#9ca3af"
                tick={{ fontSize: 12 }}
                label={{ 
                  value: yAxisLabel,
                  angle: -90,
                  position: 'insideLeft',
                  style: { fontSize: '12px', fill: '#9ca3af' }
                }}
              />
              {showBubbles && (
                <ZAxis 
                  type="number" 
                  dataKey="z" 
                  range={bubbleSizeRange} 
                  domain={[minZ, maxZ]} 
                />
              )}
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              
              {data.map((series, index) => (
                <Scatter
                  key={`scatter-${index}`}
                  name={series.name}
                  data={series.data.map(point => ({ 
                    ...point, 
                    seriesName: series.name 
                  }))}
                  fill={series.color || DEFAULT_COLORS[index % DEFAULT_COLORS.length]}
                />
              ))}
            </RechartsScatterChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
            No data available
          </div>
        )}
      </div>
    </Card>
  );
};

export default ScatterPlot;