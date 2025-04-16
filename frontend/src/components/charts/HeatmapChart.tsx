import React, { useMemo } from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  ResponsiveContainer,
  Rectangle,
  TooltipProps,
} from 'recharts';
import Card from '@/components/common/Card';

interface HeatmapCell {
  x: number;
  y: number;
  value: number;
  xLabel?: string;
  yLabel?: string;
}

interface HeatmapProps {
  data: HeatmapCell[];
  title?: string;
  subtitle?: string;
  height?: number | string;
  loading?: boolean;
  error?: string | null;
  className?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  minColor?: string;
  maxColor?: string;
  midColor?: string;
  showScale?: boolean;
  xCategories?: string[];
  yCategories?: string[];
  cellSize?: number;
}

const HeatmapChart: React.FC<HeatmapProps> = ({
  data,
  title,
  subtitle,
  height = 400,
  loading = false,
  error = null,
  className = '',
  xAxisLabel = 'X-Axis',
  yAxisLabel = 'Y-Axis',
  minColor = '#3b82f6', // blue-500
  maxColor = '#ef4444', // red-500
  midColor = '#10b981', // green-500
  showScale = true,
  xCategories = [],
  yCategories = [],
  cellSize = 30,
}) => {
  // Calculate min, max values and prepare data
  const { min, max, enhancedData } = useMemo(() => {
    if (!data || data.length === 0) {
      return { min: 0, max: 0, enhancedData: [] };
    }
    
    const values = data.map(cell => cell.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    
    // Add display labels if categories are provided
    const enhancedData = data.map(cell => ({
      ...cell,
      xLabel: xCategories[cell.x] || `${cell.x}`,
      yLabel: yCategories[cell.y] || `${cell.y}`,
    }));
    
    return { min, max, enhancedData };
  }, [data, xCategories, yCategories]);

  // Generate color based on value
  const getColor = (value: number): string => {
    const normalizedValue = (value - min) / (max - min);
    
    if (min === max) return midColor; // Handle case when all values are the same
    
    if (normalizedValue < 0.5) {
      // Blend from minColor to midColor
      const ratio = normalizedValue * 2;
      return blendColors(minColor, midColor, ratio);
    } else {
      // Blend from midColor to maxColor
      const ratio = (normalizedValue - 0.5) * 2;
      return blendColors(midColor, maxColor, ratio);
    }
  };
  
  // Helper function to blend two colors
  const blendColors = (color1: string, color2: string, ratio: number): string => {
    // Parse hex colors
    const r1 = parseInt(color1.substring(1, 3), 16);
    const g1 = parseInt(color1.substring(3, 5), 16);
    const b1 = parseInt(color1.substring(5, 7), 16);
    
    const r2 = parseInt(color2.substring(1, 3), 16);
    const g2 = parseInt(color2.substring(3, 5), 16);
    const b2 = parseInt(color2.substring(5, 7), 16);
    
    // Blend colors
    const r = Math.round(r1 * (1 - ratio) + r2 * ratio);
    const g = Math.round(g1 * (1 - ratio) + g2 * ratio);
    const b = Math.round(b1 * (1 - ratio) + b2 * ratio);
    
    // Convert back to hex
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  };
  
  // Custom cell shape for heatmap
  const HeatmapCell = (props: any) => {
    const { x, y, width, height, value } = props;
    const color = getColor(value);
    
    return (
      <Rectangle
        x={x}
        y={y}
        width={width}
        height={height}
        fill={color}
        stroke="#fff"
        strokeWidth={1}
      />
    );
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: TooltipProps<number, string>) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-700 shadow-md rounded-md">
          <div className="space-y-1">
            <div className="flex items-center">
              <span className="text-xs font-medium">
                {xAxisLabel}: {data.xLabel}
              </span>
            </div>
            <div className="flex items-center">
              <span className="text-xs font-medium">
                {yAxisLabel}: {data.yLabel}
              </span>
            </div>
            <div className="flex items-center">
              <span className="text-xs font-medium">
                Value: {data.value}
              </span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  // Calculate dynamic chart margins based on axis labels
  const margins = {
    top: 20,
    right: 20,
    bottom: 50, // Space for x-axis label
    left: 60,   // Space for y-axis label
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
        {enhancedData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={margins}>
              <XAxis
                type="number"
                dataKey="x"
                name={xAxisLabel}
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => xCategories[value] || `${value}`}
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
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => yCategories[value] || `${value}`}
                label={{ 
                  value: yAxisLabel,
                  angle: -90,
                  position: 'insideLeft',
                  style: { fontSize: '12px', fill: '#9ca3af' }
                }}
              />
              <ZAxis
                type="number"
                dataKey="value"
                range={[cellSize, cellSize]}
                domain={[min, max]}
              />
              <Tooltip content={<CustomTooltip />} />
              <Scatter
                data={enhancedData}
                shape={<HeatmapCell />}
              />
            </ScatterChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
            No data available
          </div>
        )}
        
        {/* Color scale legend */}
        {showScale && enhancedData.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div className="text-xs text-gray-500 dark:text-gray-400">{min}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">{max}</div>
            </div>
            <div className="h-2 w-full bg-gradient-to-r from-blue-500 via-green-500 to-red-500 rounded-sm mt-1" />
          </div>
        )}
      </div>
    </Card>
  );
};

export default HeatmapChart;