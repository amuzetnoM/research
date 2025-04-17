import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import Card from '@/components/common/Card';

interface GaugeChartProps {
  value: number;
  title?: string;
  subtitle?: string;
  min?: number;
  max?: number;
  unit?: string;
  threshold?: {
    warning?: number;
    critical?: number;
  };
  height?: number | string;
  showValue?: boolean;
  loading?: boolean;
  error?: string | null;
  className?: string;
}

const GaugeChart: React.FC<GaugeChartProps> = ({
  value,
  title,
  subtitle,
  min = 0,
  max = 100,
  unit = '%',
  threshold = { warning: 70, critical: 90 },
  height = 200,
  showValue = true,
  loading = false,
  error = null,
  className = '',
}) => {
  // Normalize value to be within min and max
  const normalizedValue = Math.max(min, Math.min(max, value));
  const percentage = ((normalizedValue - min) / (max - min)) * 100;
  
  // Determine color based on thresholds
  const getColor = (): string => {
    if (threshold.critical && percentage >= threshold.critical) {
      return '#ef4444'; // danger-500
    }
    if (threshold.warning && percentage >= threshold.warning) {
      return '#f59e0b'; // warning-500
    }
    return '#10b981'; // success-500
  };

  // Data for the gauge chart
  const data = [
    { name: 'value', value: percentage },
    { name: 'empty', value: 100 - percentage },
  ];

  return (
    <Card
      title={title}
      subtitle={subtitle}
      className={`glass neumorph-inset ${className}`}
      loading={loading}
      error={error}
    >
      <div style={{ width: '100%', height }} className="glass neumorph-inset relative">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              startAngle={180}
              endAngle={0}
              innerRadius="60%"
              outerRadius="80%"
              paddingAngle={0}
              dataKey="value"
              stroke="none"
            >
              <Cell fill={getColor()} />
              <Cell fill="#e5e7eb" /> {/* gray-200 */}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        {showValue && (
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-bold">
              {normalizedValue}
              <span className="text-sm font-normal">{unit}</span>
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {percentage.toFixed(1)}% of {max}
            </span>
          </div>
        )}
      </div>
    </Card>
  );
};

export default GaugeChart;