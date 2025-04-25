import React from 'react';
import {
  RadarChart as RechartsRadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ResponsiveContainer,
  Tooltip,
  TooltipProps,
} from 'recharts';
import Card from '@/components/common/Card';

interface DataPoint {
  name: string;
  [key: string]: any;
}

interface RadarChartProps {
  data: DataPoint[];
  dataKeys: {
    key: string;
    name: string;
    color?: string;
  }[];
  title?: string;
  subtitle?: string;
  height?: number | string;
  loading?: boolean;
  error?: string | null;
  className?: string;
  showGrid?: boolean;
  fillOpacity?: number;
  maxValue?: number;
  angleAxisProps?: any;
  radiusAxisProps?: any;
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

const RadarChart: React.FC<RadarChartProps> = ({
  data,
  dataKeys,
  title,
  subtitle,
  height = 400,
  loading = false,
  error = null,
  className = '',
  showGrid = true,
  fillOpacity = 0.5,
  maxValue,
  angleAxisProps = {},
  radiusAxisProps = {},
}) => {
  // Custom tooltip
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
            <RechartsRadarChart
              data={data}
              margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
            >
              {showGrid && <PolarGrid stroke="#e5e7eb" />}
              <PolarAngleAxis
                dataKey="name"
                tick={{ fontSize: 12, fill: '#6b7280' }}
                {...angleAxisProps}
              />
              <PolarRadiusAxis
                tickCount={5}
                tick={{ fontSize: 12, fill: '#6b7280' }}
                domain={maxValue ? [0, maxValue] : undefined}
                {...radiusAxisProps}
              />
              
              {dataKeys.map((item, index) => (
                <Radar
                  key={`radar-${index}`}
                  name={item.name}
                  dataKey={item.key}
                  stroke={item.color || DEFAULT_COLORS[index % DEFAULT_COLORS.length]}
                  fill={item.color || DEFAULT_COLORS[index % DEFAULT_COLORS.length]}
                  fillOpacity={fillOpacity}
                />
              ))}
              
              <Tooltip content={<CustomTooltip />} />
              <Legend />
            </RechartsRadarChart>
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

export default RadarChart;