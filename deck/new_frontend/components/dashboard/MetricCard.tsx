import React from 'react';
import Card from '@/components/common/Card';

interface MetricCardProps {
  title: string;
  value: number | string;
  previousValue?: number | string;
  unit?: string;
  icon?: string;
  change?: number;
  changeTimeframe?: string;
  loading?: boolean;
  error?: string | null;
  className?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  previousValue,
  unit = '',
  icon = 'trending_up',
  change,
  changeTimeframe = 'from previous period',
  loading = false,
  error = null,
  className = '',
}) => {
  const isPositiveChange = typeof change === 'number' ? change > 0 : false;
  const isNegativeChange = typeof change === 'number' ? change < 0 : false;
  
  const formatChange = (change: number): string => {
    const absChange = Math.abs(change);
    return `${change > 0 ? '+' : ''}${absChange.toFixed(1)}%`;
  };

  return (
    <Card 
      className={className}
      loading={loading}
      error={error}
    >
      <div className="flex items-start justify-between">
        <div>
          <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">{title}</h4>
          <div className="flex items-baseline">
            <span className="text-2xl font-semibold text-gray-900 dark:text-white">{value}</span>
            {unit && <span className="ml-1 text-sm text-gray-500 dark:text-gray-400">{unit}</span>}
          </div>
        </div>
        <div className="h-10 w-10 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
          <span className="material-icons-outlined text-primary-600 dark:text-primary-400">{icon}</span>
        </div>
      </div>
      
      {typeof change === 'number' && (
        <div className="mt-3">
          <div className={`flex items-center text-sm ${
            isPositiveChange ? 'text-success-600 dark:text-success-400' : 
            isNegativeChange ? 'text-danger-600 dark:text-danger-400' : 
            'text-gray-500 dark:text-gray-400'
          }`}>
            <span className="material-icons-outlined text-sm mr-1">
              {isPositiveChange ? 'arrow_upward' : isNegativeChange ? 'arrow_downward' : 'remove'}
            </span>
            <span>{formatChange(change)}</span>
            <span className="ml-1 text-gray-500 dark:text-gray-400">{changeTimeframe}</span>
          </div>
          {previousValue !== undefined && (
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
              Previous: {previousValue}{unit}
            </div>
          )}
        </div>
      )}
    </Card>
  );
};

export default MetricCard;