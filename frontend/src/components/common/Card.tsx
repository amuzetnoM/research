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
    <div className={`glass neumorph gradient-bg shadow-glass p-0 rounded-3xl border border-white/30 backdrop-blur-md ${className}`}>
      {(title || subtitle || action) && (
        <div className="px-6 py-4 border-b border-white/20 flex justify-between items-center bg-white/10 backdrop-blur-sm rounded-t-3xl">
          <div>
            {title && <h3 className="text-xl font-semibold accent drop-shadow-sm">{title}</h3>}
            {subtitle && <p className="text-sm text-gray-500 dark:text-gray-300">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="p-6 relative">
        {loading && (
          <div className="absolute inset-0 bg-white/40 dark:bg-gray-900/40 flex items-center justify-center z-10 rounded-3xl">
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