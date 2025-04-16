import React, { ButtonHTMLAttributes, ReactNode } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
  loading?: boolean;
  fullWidth?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  iconPosition = 'left',
  loading = false,
  fullWidth = false,
  disabled,
  className = '',
  ...props
}) => {
  // Define style variants
  const variantStyles = {
    primary: 'glass neumorph gradient-bg accent shadow-glass border border-white/30 text-white hover:bg-primary-600/80 focus:ring-primary-400',
    secondary: 'glass neumorph border border-white/30 text-primary-600 bg-white/60 hover:bg-white/80 focus:ring-primary-200',
    success: 'glass neumorph border border-white/30 text-success-600 bg-success-100/60 hover:bg-success-200/80 focus:ring-success-200',
    danger: 'glass neumorph border border-white/30 text-danger-600 bg-danger-100/60 hover:bg-danger-200/80 focus:ring-danger-200',
    warning: 'glass neumorph border border-white/30 text-warning-600 bg-warning-100/60 hover:bg-warning-200/80 focus:ring-warning-200',
    info: 'glass neumorph border border-white/30 text-primary-500 bg-primary-100/60 hover:bg-primary-200/80 focus:ring-primary-200',
    ghost: 'bg-transparent text-primary-600 hover:bg-primary-50/40',
  };

  // Define size variants
  const sizeStyles = {
    sm: 'px-4 py-1.5 text-sm rounded-xl',
    md: 'px-6 py-2 text-base rounded-2xl',
    lg: 'px-8 py-3 text-lg rounded-3xl',
  };

  const baseStyles = `
    inline-flex items-center justify-center font-medium transition-colors duration-200
    focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-900
    disabled:opacity-50 disabled:pointer-events-none
    backdrop-blur-md
  `;

  return (
    <button
      className={`
        ${baseStyles}
        ${variantStyles[variant]}
        ${sizeStyles[size]}
        ${fullWidth ? 'w-full' : ''}
        ${className}
      `}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <>
          <span className="animate-spin -ml-1 mr-2 h-4 w-4 text-white">
            <svg className="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          </span>
          Loading...
        </>
      ) : (
        <>
          {icon && iconPosition === 'left' && <span className="mr-2">{icon}</span>}
          {children}
          {icon && iconPosition === 'right' && <span className="ml-2">{icon}</span>}
        </>
      )}
    </button>
  );
};

export default Button;