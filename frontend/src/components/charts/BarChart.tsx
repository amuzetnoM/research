import React from 'react';
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  TooltipProps,
  Cell,
} from 'recharts';
import Card from '@/components/common/Card';

interface DataPoint {
  name: string;
  [key: string]: any;
}

interface BarChartProps {
  data: DataPoint[];
  bars: {
    dataKey: string;
    name: string;
    color?: string;
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
  layout?: 'vertical' | 'horizontal';
  colorByValue?: boolean;
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

// Generate color based on value (for heatmap-like visualization)
const generateColorByValue = (value: number, min: number, max: number): string => {
  // Calculate a value between 0 and 1
  const normalizedValue = (value - min) / (max - min);
  
  // Use a gradient from blue to red
  if (normalizedValue < 0.25) {
    return '#3b82f6'; // blue-500
  } else if (normalizedValue < 0.5) {
    return '#10b981'; // green-500
  } else if (normalizedValue < 0.75) {
    return '#f59e0b'; // amber-500
  } else {
    return '#ef4444'; // red-500
  }
};

const BarChart: React.FC<BarChartProps> = ({
  data,
  bars,
  title,
  subtitle,
  height = 300,
  loading = false,
  error = null,
  className = '',
  xAxisDataKey = 'name',
  yAxisUnit = '',
  showGrid = true,
  layout = 'horizontal',
  colorByValue = false,
}) => {
  // Find min and max values if we're coloring by value
  let minValue = 0;
  let maxValue = 0;
  
  if (colorByValue && bars.length === 1) {
    const dataKey = bars[0].dataKey;
    const values = data.map(item => item[dataKey]);
    minValue = Math.min(...values);
    maxValue = Math.max(...values);
  }

  // Custom tooltip formatter
  const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 shadow-md rounded-md">
          <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">{label}</p>
          <div className="space-y-1">
            {payload.map((entry, index) => (
              <div key={`tooltip-item-${index}`} className="flex items-center">
                <div
                  className="w-3 h-3 rounded-full mr-2"
                  style={{ backgroundColor: entry.color }}
                />
                <span className="text-xs">
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
            <RechartsBarChart
              data={data}
              layout={layout}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />}
              <XAxis 
                dataKey={xAxisDataKey}
                type={layout === 'horizontal' ? 'category' : 'number'}
                stroke="#9ca3af"
                tick={{ fontSize: 12 }}
              />
              <YAxis
                unit={yAxisUnit}
                type={layout === 'horizontal' ? 'number' : 'category'}
                stroke="#9ca3af"
                tick={{ fontSize: 12 }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              {bars.map((bar, index) => (
                <Bar
                  key={bar.dataKey}
                  dataKey={bar.dataKey}
                  name={bar.name}
                  fill={bar.color || DEFAULT_COLORS[index % DEFAULT_COLORS.length]}
                >
                  {colorByValue && bars.length === 1 && 
                    data.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={generateColorByValue(entry[bar.dataKey], minValue, maxValue)} 
                      />
                    ))
                  }
                </Bar>
              ))}
            </RechartsBarChart>
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

export default BarChart;