import React from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import { cn } from '@/lib/utils';

interface CardProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  className?: string;
  loading?: boolean;
  error?: string | null;
}

const Card: React.FC<CardProps> = ({ 
  children, 
  title, 
  subtitle, 
  className = '',
  loading = false,
  error = null
}) => {
  const { isDarkMode } = useTheme();

  return (
    <div
      className={cn(
        "p-6 rounded-2xl transition-all duration-300",
        isDarkMode
          ? "bg-gray-900 shadow-inner shadow-black/90"
          : "bg-white shadow-inner shadow-white/90",
        "border border-transparent",
        isDarkMode ? "border-gray-800" : "border-gray-200",
        "transition-shadow duration-300",
        "hover:scale-[1.01]",
        "overflow-hidden",
        className
      )}
    >
      {title && (
        <div className="mb-4">
          <h2
            className={cn(
              "text-xl font-semibold transition-colors duration-300",
              isDarkMode ? "text-gray-100" : "text-gray-900",
              "font-light"
            )}
          >
            {title}
          </h2>
          {subtitle && (
            <p
              className={cn(
                "text-sm transition-colors duration-300",
                isDarkMode ? "text-gray-400" : "text-gray-600",
              )}
            >
              {subtitle}
            </p>
          )}
        </div>
      )}

      <div className="w-full">
        {loading ? (
          <div className="flex justify-center items-center p-4">
            <svg className="animate-spin h-8 w-8" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          </div>
        ) : error ? (
          <div className={cn(
            "text-sm p-4 rounded-xl",
            isDarkMode ? "bg-red-900/20 text-red-300" : "bg-red-100 text-red-600",
          )}>
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
export { Card };