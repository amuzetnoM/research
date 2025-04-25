import React, { Component, ReactNode, ErrorInfo } from 'react';
import { handleComponentError } from '@utils/errorHandler';
import { logger } from '@utils/logger';
import Card from './Card';
import Button from './Button';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onReset?: () => void;
  name?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Error Boundary component to catch and handle React errors gracefully
 */
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null 
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log the error to our error handling system
    const componentName = this.props.name || 'Unnamed Component';
    logger.error(`Error caught in ${componentName} boundary:`, { error, errorInfo });
    
    // Use the enhanced error handler
    handleComponentError(error, errorInfo);
    
    // Update state with error details
    this.setState({ errorInfo });
  }

  handleReset = (): void => {
    // Reset the error boundary state
    this.setState({ 
      hasError: false, 
      error: null, 
      errorInfo: null 
    });
    
    // Call the onReset prop if provided
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render(): ReactNode {
    const { children, fallback } = this.props;
    const { hasError, error, errorInfo } = this.state;

    if (hasError) {
      // If a custom fallback is provided, render it
      if (fallback) {
        return fallback;
      }

      // Default error UI
      return (
        <Card title="Something went wrong" className="bg-danger-50 dark:bg-danger-900/20 border-danger-200 dark:border-danger-800">
          <div className="p-4 text-center">
            <div className="text-danger-600 dark:text-danger-400 text-xl mb-4">
              <span className="material-icons-outlined text-4xl block mb-2">error_outline</span>
              Error in {this.props.name || 'Component'}
            </div>
            
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              {error?.message || 'An unexpected error occurred.'}
            </p>
            
            {process.env.NODE_ENV !== 'production' && error && (
              <details className="mb-4 text-left">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Error Details
                </summary>
                <pre className="bg-gray-100 dark:bg-gray-800 p-3 rounded text-xs overflow-auto max-h-48 text-left">
                  {error.stack}
                </pre>
                {errorInfo && (
                  <>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mt-2 mb-1">Component Stack:</p>
                    <pre className="bg-gray-100 dark:bg-gray-800 p-3 rounded text-xs overflow-auto max-h-48 text-left">
                      {errorInfo.componentStack}
                    </pre>
                  </>
                )}
              </details>
            )}
            
            <Button
              onClick={this.handleReset}
              variant="primary"
              icon={<span className="material-icons-outlined">refresh</span>}
            >
              Try Again
            </Button>
          </div>
        </Card>
      );
    }

    // If there's no error, render children normally
    return children;
  }
}

export default ErrorBoundary;
