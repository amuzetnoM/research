import React, { ReactNode } from 'react';

interface CardProps {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
  action?: ReactNode;
  loading?: boolean;
  error?: string | null;
}

const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  children,
  className = '',
  action,
  loading = false,
  error = null,
}) => {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden ${className}`}>
      {(title || subtitle || action) && (
        <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <div>
            {title && <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">{title}</h3>}
            {subtitle && <p className="text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="p-4 relative">
        {loading && (
          <div className="absolute inset-0 bg-white/50 dark:bg-gray-800/50 flex items-center justify-center z-10">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
          </div>
        )}
        {error ? (
          <div className="text-danger-600 dark:text-danger-400 text-sm p-4 bg-danger-50 dark:bg-danger-900/20 rounded">
            <span className="material-icons-outlined text-sm align-middle mr-1">error</span>
            {error}
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
};

export default Card;