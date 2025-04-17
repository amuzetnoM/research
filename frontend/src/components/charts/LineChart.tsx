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
import Card from '../common/Card';

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
    type?: 'monotone' | 'linear' | 'step' | 'stepBefore' | 'stepAfter' | 'basis' | 'basisOpen' | 'basisClosed' | 'natural';
    activeDotSize?: number;
    dotSize?: number;
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
  variant?: 'glass' | 'neumorph' | 'glass-gradient';
}

const DEFAULT_COLORS = [
  'hsl(var(--primary-500))', // primary
  'hsl(var(--secondary))',   // secondary
  '#10b981',                // success-500
  '#f59e0b',                // warning-500
  '#ef4444',                // danger-500
  '#6366f1',                // indigo-500
  '#ec4899',                // pink-500
  '#14b8a6',                // teal-500
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
  variant = 'glass',
}) => {
  // Custom tooltip formatter
  const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-sm border-thin border-white/20 p-2 backdrop-blur-md rounded-lg shadow-glass-sm">
          <p className="text-xs text-foreground/70 mb-1">
            {xAxisDataKey === 'timestamp'
              ? format(new Date(label), 'MMM dd, yyyy HH:mm:ss')
              : label}
          </p>
          <div className="space-y-1">
            {payload.map((entry, index) => (
              <div key={`tooltip-item-${index}`} className="flex items-center">
                <div
                  className="w-2 h-2 rounded-full mr-1.5"
                  style={{ backgroundColor: entry.color }}
                />
                <span className="text-xs font-medium text-foreground">
                  {entry.name}: <span className="font-semibold">{entry.value}</span>
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
      variant={variant}
    >
      <div style={{ width: '100%', height }} className="pt-2">
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <RechartsLineChart
              data={data}
              margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
            >
              {showGrid && (
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  stroke="rgba(148, 163, 184, 0.15)"
                  vertical={false} 
                />
              )}
              <XAxis
                dataKey={xAxisDataKey}
                tickFormatter={formatXAxis}
                stroke="rgba(148, 163, 184, 0.6)"
                tick={{ fontSize: 10 }}
                axisLine={{ stroke: 'rgba(148, 163, 184, 0.2)' }}
                tickLine={{ stroke: 'rgba(148, 163, 184, 0.2)' }}
              />
              <YAxis
                unit={yAxisUnit}
                stroke="rgba(148, 163, 184, 0.6)"
                tick={{ fontSize: 10 }}
                axisLine={{ stroke: 'rgba(148, 163, 184, 0.2)' }}
                tickLine={{ stroke: 'rgba(148, 163, 184, 0.2)' }}
              />
              <Tooltip 
                content={<CustomTooltip />} 
                cursor={{ stroke: 'rgba(148, 163, 184, 0.2)', strokeWidth: 1, strokeDasharray: '3 3' }}
              />
              <Legend 
                wrapperStyle={{ 
                  paddingTop: 10,
                  fontSize: 12, 
                  opacity: 0.8
                }}
              />
              {lines.map((line, index) => (
                <Line
                  key={line.dataKey}
                  type={line.type || 'monotone'}
                  dataKey={line.dataKey}
                  name={line.name}
                  stroke={line.color || DEFAULT_COLORS[index % DEFAULT_COLORS.length]}
                  strokeWidth={line.strokeWidth || 2}
                  dot={{ r: line.dotSize || 2, strokeWidth: 1, fill: '#fff' }}
                  activeDot={{ 
                    r: line.activeDotSize || 5, 
                    strokeWidth: 1, 
                    boxShadow: '0 0 6px rgba(0,0,0,0.2)' 
                  }}
                />
              ))}
            </RechartsLineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-full text-foreground/60">
            <span className="material-icons-outlined mr-2 text-sm">show_chart</span>
            No data available
          </div>
        )}
      </div>
    </Card>
  );
};

export default LineChart;