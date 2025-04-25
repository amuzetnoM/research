import React, { ButtonHTMLAttributes } from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import { cn } from '@/lib/utils';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'ghost' | 'neumorph';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  loading?: boolean;
  children: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  children,
  className = '',
  ...props
}) => {
  const { isDarkMode } = useTheme();

  // Define variant styles based on theme
  const getVariantStyle = (variant: string) => {
    if (isDarkMode) {
      // Dark mode variants
      switch(variant) {
        case 'primary':
          return 'bg-blue-600 hover:bg-blue-700 text-white';
        case 'secondary':
          return 'bg-gray-700 hover:bg-gray-800 text-gray-200';
        case 'success':
          return 'bg-green-600 hover:bg-green-700 text-white';
        case 'danger':
          return 'bg-red-600 hover:bg-red-700 text-white';
        case 'warning':
          return 'bg-yellow-500 hover:bg-yellow-600 text-white';
        case 'info':
          return 'bg-cyan-600 hover:bg-cyan-700 text-white';
        case 'ghost':
          return 'bg-transparent hover:bg-gray-800 text-gray-300';
        case 'neumorph':
          return 'bg-gray-900 text-gray-300 shadow-inner shadow-black/90 hover:bg-gray-800/80';
        default:
          return 'bg-blue-600 hover:bg-blue-700 text-white';
      }
    } else {
      // Light mode variants
      switch(variant) {
        case 'primary':
          return 'bg-blue-600 hover:bg-blue-700 text-white';
        case 'secondary':
          return 'bg-gray-200 hover:bg-gray-300 text-gray-800';
        case 'success':
          return 'bg-green-600 hover:bg-green-700 text-white';
        case 'danger':
          return 'bg-red-600 hover:bg-red-700 text-white';
        case 'warning':
          return 'bg-yellow-500 hover:bg-yellow-600 text-white';
        case 'info':
          return 'bg-cyan-600 hover:bg-cyan-700 text-white';
        case 'ghost':
          return 'bg-transparent hover:bg-gray-100 text-gray-700';
        case 'neumorph':
          return 'bg-white text-gray-700 shadow-inner shadow-white/90 hover:bg-gray-100/80';
        default:
          return 'bg-blue-600 hover:bg-blue-700 text-white';
      }
    }
  };

  // Define size variants
  const sizeStyles = {
    xs: 'px-2 py-1 text-xs rounded-lg',
    sm: 'px-3 py-1.5 text-sm rounded-lg',
    md: 'px-4 py-2 text-base rounded-xl',
    lg: 'px-6 py-3 text-lg rounded-xl',
  };

  return (
    <button
      className={cn(
        "inline-flex items-center justify-center font-medium transition-all duration-300",
        "focus:outline-none disabled:opacity-50 disabled:pointer-events-none",
        "border border-transparent",
        isDarkMode ? "border-gray-800" : "border-gray-200",
        getVariantStyle(variant),
        sizeStyles[size],
        fullWidth ? 'w-full' : '',
        variant === 'neumorph' || variant === 'ghost' ? 'hover:scale-[1.02]' : '',
        className
      )}
      disabled={props.disabled || loading}
      {...props}
    >
      {loading ? (
        <>
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <span>Processing</span>
        </>
      ) : (
        <span>{children}</span>
      )}
    </button>
  );
};

export default Button;
export { Button };