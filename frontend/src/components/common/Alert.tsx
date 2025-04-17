import React from 'react';

export type AlertType = 'info' | 'success' | 'warning' | 'error' | 'critical';

export interface AlertProps {
  type?: AlertType;
  title?: string;
  message: string;
  action?: React.ReactNode;
  dismissible?: boolean;
  timestamp?: Date;
  className?: string;
  onDismiss?: () => void;
}

export const Alert: React.FC<AlertProps> = ({
  type = 'info',
  title,
  message,
  action,
  dismissible = false,
  timestamp,
  className = '',
  onDismiss,
}) => {
  const typeClasses = {
    info: 'bg-blue-50 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 border-blue-200 dark:border-blue-800',
    success: 'bg-green-50 text-green-800 dark:bg-green-900/30 dark:text-green-300 border-green-200 dark:border-green-800',
    warning: 'bg-yellow-50 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800',
    error: 'bg-red-50 text-red-800 dark:bg-red-900/30 dark:text-red-300 border-red-200 dark:border-red-800',
    critical: 'bg-red-100 text-red-900 dark:bg-red-900/50 dark:text-red-200 border-red-300 dark:border-red-700',
  };

  const iconMap = {
    info: 'info',
    success: 'check_circle',
    warning: 'warning',
    error: 'error',
    critical: 'dangerous',
  };

  const handleDismiss = () => {
    if (onDismiss) {
      onDismiss();
    }
  };

  return (
    <div 
      className={`flex p-4 mb-4 border rounded-lg ${typeClasses[type]} ${className}`}
      role="alert"
    >
      <div className="flex-shrink-0 mr-3">
        <span className="material-icons-outlined">{iconMap[type]}</span>
      </div>
      <div className="flex-grow">
        {title && <h3 className="text-sm font-medium mb-1">{title}</h3>}
        <div className="text-sm">
          {message}
          {timestamp && (
            <div className="text-xs opacity-70 mt-1">
              {timestamp.toLocaleString()}
            </div>
          )}
        </div>
        {action && <div className="mt-2">{action}</div>}
      </div>
      {dismissible && (
        <button
          type="button"
          className="flex-shrink-0 ml-auto -mx-1.5 -my-1.5 p-1.5 rounded-lg focus:ring-2 focus:ring-primary-500 inline-flex items-center justify-center h-8 w-8 hover:bg-gray-200 dark:hover:bg-gray-700"
          onClick={handleDismiss}
          aria-label="Close"
        >
          <span className="material-icons-outlined text-sm">close</span>
        </button>
      )}
    </div>
  );
};

export default Alert;
