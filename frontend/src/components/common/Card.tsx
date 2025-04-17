import React, { ReactNode } from 'react';

interface CardProps {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
  action?: ReactNode;
  loading?: boolean;
  error?: string | null;
  variant?: 'neumorph' | 'inset' | 'flat';
  noPadding?: boolean;
  elevation?: 'low' | 'medium' | 'high';
}

const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  children,
  className = '',
  action,
  loading = false,
  error = null,
  variant = 'neumorph',
  noPadding = false,
  elevation = 'medium',
}) => {
  // Create consistent neumorphic variants with no borders
  const variantClasses = {
    neumorph: 'neumorph bg-background',
    inset: 'neumorph-inset bg-background',
    flat: 'bg-background rounded-2xl',
  };

  // Elevation only affects neumorph variant
  const elevationClasses = {
    low: variant === 'neumorph' ? 'neumorph-sm' : '',
    medium: variant === 'neumorph' ? 'neumorph' : '',
    high: variant === 'neumorph' ? 'neumorph-lg' : '',
  };

  return (
    <div 
      className={`
        ${variantClasses[variant]} 
        ${elevation && variant === 'neumorph' ? elevationClasses[elevation] : ''} 
        overflow-hidden
        ${className}
      `}
    >
      {(title || subtitle || action) && (
        <div className="px-5 py-4 flex justify-between items-center">
          <div>
            {title && (
              <h3 className="text-base font-medium text-foreground tracking-tight">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="text-sm text-foreground/60 mt-0.5">
                {subtitle}
              </p>
            )}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className={`relative ${noPadding ? '' : 'p-5'}`}>
        {loading && (
          <div className="absolute inset-0 bg-background/80 flex items-center justify-center z-10 backdrop-blur-sm">
            <svg className="animate-spin h-8 w-8" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          </div>
        )}
        {error ? (
          <div className="text-danger-500 text-sm p-4 bg-danger-500/5 neumorph-inset">
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
// Add named export to support both import styles
export { Card };