import React from 'react';
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  TooltipProps,
} from 'recharts';
import { format } from 'date-fns';
import Card from '@/components/common/Card';

interface DataPoint {
  timestamp: number;
  [key: string]: any;
}

interface LineChartProps {
  data: DataPoint[];
  lines: {
    dataKey: string;
    name: string;
    color?: string;
    strokeWidth?: number;
  }[];
  title?: string;
  subtitle?: string;
  height?: number | string;
  loading?: boolean;
  error?: string | null;
  className?: string;
  xAxisDataKey?: string;
  yAxisUnit?: string;
  showGrid?: boolean;
  timeFormat?: string;
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

const LineChart: React.FC<LineChartProps> = ({
  data,
  lines,
  title,
  subtitle,
  height = 300,
  loading = false,
  error = null,
  className = '',
  xAxisDataKey = 'timestamp',
  yAxisUnit = '',
  showGrid = true,
  timeFormat = 'HH:mm',
}) => {
  // Custom tooltip formatter
  const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 shadow-md rounded-md">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
            {xAxisDataKey === 'timestamp'
              ? format(new Date(label), 'MMM dd, yyyy HH:mm:ss')
              : label}
          </p>
          <div className="space-y-1">
            {payload.map((entry, index) => (
              <div key={`tooltip-item-${index}`} className="flex items-center">
                <div
                  className="w-3 h-3 rounded-full mr-2"
                  style={{ backgroundColor: entry.color }}
                />
                <span className="text-xs font-medium">
                  {entry.name}: {entry.value}
                  {yAxisUnit}
                </span>
              </div>
            ))}
          </div>
        </div>
      );
    }
    return null;
  };

  // Format timestamp for X-axis
  const formatXAxis = (timestamp: number) => {
    if (xAxisDataKey === 'timestamp') {
      return format(new Date(timestamp), timeFormat);
    }
    return timestamp;
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
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <RechartsLineChart
              data={data}
              margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
            >
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />}
              <XAxis
                dataKey={xAxisDataKey}
                tickFormatter={formatXAxis}
                stroke="#9ca3af"
                tick={{ fontSize: 12 }}
              />
              <YAxis
                unit={yAxisUnit}
                stroke="#9ca3af"
                tick={{ fontSize: 12 }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              {lines.map((line, index) => (
                <Line
                  key={line.dataKey}
                  type="monotone"
                  dataKey={line.dataKey}
                  name={line.name}
                  stroke={line.color || DEFAULT_COLORS[index % DEFAULT_COLORS.length]}
                  strokeWidth={line.strokeWidth || 2}
                  activeDot={{ r: 6 }}
                  dot={{ r: 3 }}
                />
              ))}
            </RechartsLineChart>
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

export default LineChart;