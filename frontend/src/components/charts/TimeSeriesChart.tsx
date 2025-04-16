import React, { useMemo } from 'react';
import { Line, LineChart as RechartsLineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import Card from '@/components/common/Card';
import { format } from 'date-fns';

interface TimeSeriesData {
  timestamp: number;
  value: number;
}

interface TimeSeriesChartProps {
  data: TimeSeriesData[];
  name: string;
  color?: string;
  title?: string;
  subtitle?: string;
  height?: number;
  unit?: string;
  loading?: boolean;
  error?: string | null;
}

const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({
  data,
  name,
  color = '#0ea5e9',
  title,
  subtitle,
  height = 200,
  unit = '',
  loading = false,
  error = null,
}) => {
  // Downsample data for better performance
  const downsampledData = useMemo(() => {
    if (data.length <= 1000) return data;
    const factor = Math.ceil(data.length / 1000);
    return data.filter((_, i) => i % factor === 0);
  }, [data]);

  return (
    <Card title={title} subtitle={subtitle} loading={loading} error={error}>
      <div style={{ width: '100%', height }}>
        <ResponsiveContainer>
          <RechartsLineChart data={downsampledData} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
            <XAxis
              dataKey="timestamp"
              type="number"
              domain={['dataMin', 'dataMax']}
              tickFormatter={(ts) => format(ts, 'HH:mm:ss')}
              fontSize={12}
              stroke="#9ca3af"
            />
            <YAxis
              width={40}
              fontSize={12}
              stroke="#9ca3af"
              tickFormatter={(value) => `${value}${unit}`}
            />
            <Tooltip
              labelFormatter={(ts) => format(ts as number, 'HH:mm:ss')}
              formatter={(value: number) => [`${value}${unit}`, name]}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke={color}
              dot={false}
              strokeWidth={2}
              isAnimationActive={false}
            />
          </RechartsLineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};

export default TimeSeriesChart;
