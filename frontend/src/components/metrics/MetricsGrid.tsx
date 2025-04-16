import React, { memo } from 'react';
import { motion } from 'framer-motion';
import Card from '@/components/common/Card';

interface MetricsGridProps {
  metrics: Record<string, any>;
  loading?: boolean;
  error?: string | null;
  className?: string;
}

const MetricsGrid = memo(({ metrics, loading, error, className = '' }: MetricsGridProps) => {
  const gridVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 },
  };

  return (
    <Card
      title="Real-time Metrics"
      className={className}
      loading={loading}
      error={error}
    >
      <motion.div
        variants={gridVariants}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        {Object.entries(metrics).map(([key, value]) => (
          <motion.div
            key={key}
            variants={itemVariants}
            className="p-4 rounded-lg bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center space-x-2">
              <span className="material-icons-round text-primary-500">trending_up</span>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {key.replace(/_/g, ' ').toUpperCase()}
              </h3>
            </div>
            <div className="mt-2 flex items-baseline space-x-2">
              <span className="text-2xl font-semibold text-gray-900 dark:text-white">
                {typeof value === 'number' ? value.toFixed(2) : value}
              </span>
              <span className="text-sm text-gray-500">
                {typeof value === 'number' ? '%' : ''}
              </span>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </Card>
  );
});

MetricsGrid.displayName = 'MetricsGrid';

export default MetricsGrid;
