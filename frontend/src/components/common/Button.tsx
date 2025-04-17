import React, { ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'ghost' | 'neumorph';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  loading?: boolean;
  fullWidth?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'neumorph',
  size = 'md',
  loading = false,
  fullWidth = false,
  disabled,
  className = '',
  ...props
}) => {
  // Define style variants with consistent neumorphic styling and no borders
  const variantStyles = {
    primary: 'glass neumorph shadow-neumorph-bulge bg-primary-500 text-white',
    secondary: 'glass neumorph shadow-neumorph-bulge text-primary-600 bg-white/60 hover:bg-white/80',
    success: 'glass neumorph shadow-neumorph-bulge text-success-600 bg-success-100/60 hover:bg-success-200/80',
    danger: 'glass neumorph shadow-neumorph-bulge text-danger-600 bg-danger-100/60 hover:bg-danger-200/80',
    warning: 'glass neumorph shadow-neumorph-bulge text-warning-600 bg-warning-100/60 hover:bg-warning-200/80',
    info: 'glass neumorph shadow-neumorph-bulge text-primary-500 bg-primary-100/60 hover:bg-primary-200/80',
    ghost: 'glass neumorph shadow-neumorph-bulge bg-transparent text-primary-600 hover:bg-primary-50/40',
    neumorph: 'glass neumorph shadow-neumorph-bulge text-foreground/90',
  };

  // Define size variants
  const sizeStyles = {
    xs: 'px-3 py-1.5 text-xs',
    sm: 'px-4 py-2 text-sm',
    md: 'px-5 py-2.5 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  const baseStyles = `
    btn inline-flex items-center justify-center font-medium tracking-tight
    focus:outline-none 
    disabled:opacity-50 disabled:pointer-events-none
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