/**
 * Enhanced error handling system for the Research Dashboard
 * Integrates with the existing error handling infrastructure
 */

import { logger } from './logger';
import { toast } from 'react-toastify';

// Error categories for better classification
export enum ErrorCategory {
  NETWORK = 'NETWORK',
  API = 'API',
  AUTHENTICATION = 'AUTHENTICATION',
  AUTHORIZATION = 'AUTHORIZATION',
  VALIDATION = 'VALIDATION',
  BUSINESS_LOGIC = 'BUSINESS_LOGIC',
  RESOURCE = 'RESOURCE',
  CONFIGURATION = 'CONFIGURATION',
  INTERNAL = 'INTERNAL',
  EXTERNAL = 'EXTERNAL',
  UNKNOWN = 'UNKNOWN',
}

// Operational status (determines if error is expected/handled or unexpected)
export enum OperationalStatus {
  OPERATIONAL = 'OPERATIONAL',
  NON_OPERATIONAL = 'NON_OPERATIONAL',
}

// Severity levels
export enum ErrorSeverity {
  LOW = 'LOW',           // Minor issues, no user impact
  MEDIUM = 'MEDIUM',     // Issues with minimal user impact
  HIGH = 'HIGH',         // Significant issues with user impact
  CRITICAL = 'CRITICAL', // Major issues that prevent functionality
}

// Interface for extended error properties
export interface ErrorDetails {
  category: ErrorCategory;
  operational: OperationalStatus;
  severity: ErrorSeverity;
  code?: string;
  source?: string;
  timestamp?: string;
  context?: Record<string, any>;
  retryable?: boolean;
  userFriendlyMessage?: string;
  documentationLink?: string;
}

/**
 * Enhanced Error class for Research Dashboard
 * Provides extended error properties and integration with the logger
 */
export class EnhancedError extends Error {
  public readonly category: ErrorCategory;
  public readonly operational: OperationalStatus;
  public readonly severity: ErrorSeverity;
  public readonly code?: string;
  public readonly source?: string;
  public readonly timestamp: string;
  public readonly context?: Record<string, any>;
  public readonly retryable: boolean;
  public readonly userFriendlyMessage?: string;
  public readonly documentationLink?: string;
  public readonly originalError?: Error;

  constructor(
    message: string,
    details: Partial<ErrorDetails> = {},
    originalError?: Error
  ) {
    super(message);
    
    // Set default values for error details
    this.name = this.constructor.name;
    this.category = details.category || ErrorCategory.UNKNOWN;
    this.operational = details.operational || OperationalStatus.OPERATIONAL;
    this.severity = details.severity || ErrorSeverity.MEDIUM;
    this.code = details.code;
    this.source = details.source || 'frontend';
    this.timestamp = details.timestamp || new Date().toISOString();
    this.context = details.context;
    this.retryable = details.retryable !== undefined ? details.retryable : true;
    this.userFriendlyMessage = details.userFriendlyMessage || 'An unexpected error occurred. Please try again.';
    this.documentationLink = details.documentationLink;
    this.originalError = originalError;
    
    // Ensure prototype chain works correctly
    Object.setPrototypeOf(this, EnhancedError.prototype);
    
    // Capture stack trace
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
    
    // Log the error
    this.logError();
  }

  /**
   * Log the error with appropriate level based on severity
   */
  private logError(): void {
    const errorInfo = {
      name: this.name,
      message: this.message,
      category: this.category,
      operational: this.operational,
      severity: this.severity,
      code: this.code,
      source: this.source,
      timestamp: this.timestamp,
      context: this.context,
      retryable: this.retryable,
      stack: this.stack,
      originalError: this.originalError ? {
        name: this.originalError.name,
        message: this.originalError.message,
        stack: this.originalError.stack,
      } : undefined,
    };

    // Log with appropriate level based on severity
    switch (this.severity) {
      case ErrorSeverity.LOW:
        logger.info(`Error: ${this.message}`, errorInfo);
        break;
      case ErrorSeverity.MEDIUM:
        logger.warn(`Error: ${this.message}`, errorInfo);
        break;
      case ErrorSeverity.HIGH:
      case ErrorSeverity.CRITICAL:
        logger.error(`Error: ${this.message}`, errorInfo);
        break;
      default:
        logger.error(`Error: ${this.message}`, errorInfo);
    }
  }

  /**
   * Convert error to a plain object for serialization
   */
  public toJSON(): Record<string, any> {
    return {
      name: this.name,
      message: this.message,
      category: this.category,
      operational: this.operational,
      severity: this.severity,
      code: this.code,
      source: this.source,
      timestamp: this.timestamp,
      retryable: this.retryable,
      userFriendlyMessage: this.userFriendlyMessage,
      documentationLink: this.documentationLink,
      stack: this.stack,
      context: this.context,
      originalError: this.originalError ? {
        name: this.originalError.name,
        message: this.originalError.message,
        stack: this.originalError.stack,
      } : undefined,
    };
  }
}

/**
 * Factory for creating common error types
 */
export const createError = {
  network: (message: string, details?: Partial<ErrorDetails>, originalError?: Error) => 
    new EnhancedError(message, {
      category: ErrorCategory.NETWORK,
      severity: ErrorSeverity.MEDIUM,
      ...details
    }, originalError),
    
  api: (message: string, details?: Partial<ErrorDetails>, originalError?: Error) => 
    new EnhancedError(message, {
      category: ErrorCategory.API,
      severity: ErrorSeverity.MEDIUM,
      ...details
    }, originalError),
    
  validation: (message: string, details?: Partial<ErrorDetails>, originalError?: Error) => 
    new EnhancedError(message, {
      category: ErrorCategory.VALIDATION,
      severity: ErrorSeverity.LOW,
      operational: OperationalStatus.OPERATIONAL,
      ...details
    }, originalError),
    
  auth: (message: string, details?: Partial<ErrorDetails>, originalError?: Error) => 
    new EnhancedError(message, {
      category: ErrorCategory.AUTHENTICATION,
      severity: ErrorSeverity.HIGH,
      ...details
    }, originalError),
    
  internal: (message: string, details?: Partial<ErrorDetails>, originalError?: Error) => 
    new EnhancedError(message, {
      category: ErrorCategory.INTERNAL,
      severity: ErrorSeverity.HIGH,
      operational: OperationalStatus.NON_OPERATIONAL,
      ...details
    }, originalError),
};

/**
 * Global error handler for unhandled errors/rejections
 */
export const setupGlobalErrorHandlers = (): void => {
  // Handle uncaught exceptions
  window.addEventListener('error', (event: ErrorEvent) => {
    const error = new EnhancedError(
      event.message || 'Uncaught error',
      {
        category: ErrorCategory.UNKNOWN,
        severity: ErrorSeverity.HIGH,
        operational: OperationalStatus.NON_OPERATIONAL,
        context: {
          fileName: event.filename,
          lineNumber: event.lineno,
          columnNumber: event.colno,
        },
      },
      event.error
    );
    
    logger.error('Global error caught', error.toJSON());
    
    // Don't prevent default to allow browser to handle the error as well
  });

  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event: PromiseRejectionEvent) => {
    const reason = event.reason;
    const errorMessage = reason instanceof Error 
      ? reason.message 
      : (typeof reason === 'string' ? reason : 'Unhandled promise rejection');
    
    const error = new EnhancedError(
      errorMessage,
      {
        category: ErrorCategory.UNKNOWN,
        severity: ErrorSeverity.HIGH,
        operational: OperationalStatus.NON_OPERATIONAL,
        context: {
          reason: reason instanceof Error 
            ? { name: reason.name, message: reason.message, stack: reason.stack }
            : reason,
        },
      },
      reason instanceof Error ? reason : undefined
    );
    
    logger.error('Unhandled promise rejection', error.toJSON());
    
    // Don't prevent default to allow browser to handle the rejection as well
  });
};

/**
 * Error boundary component function
 * Can be used with React's error boundary pattern
 */
export const handleComponentError = (error: Error, componentInfo: { componentStack: string }): void => {
  const enhancedError = new EnhancedError(
    error.message,
    {
      category: ErrorCategory.INTERNAL,
      severity: ErrorSeverity.HIGH,
      operational: OperationalStatus.NON_OPERATIONAL,
      context: {
        componentStack: componentInfo.componentStack,
      },
    },
    error
  );
  
  logger.error('React component error', enhancedError.toJSON());
};

/**
 * AppError class for simplified error handling
 */
export class AppError extends Error {
  constructor(
    message: string,
    public code?: string,
    public statusCode?: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'AppError';
  }
}

/**
 * Handle errors and display notifications
 */
export const handleError = (error: unknown, fallbackMessage = 'An error occurred'): AppError => {
  console.error('Error caught:', error);

  const appError = error instanceof AppError ? error : new AppError(
    error instanceof Error ? error.message : fallbackMessage
  );

  toast.error(appError.message, {
    position: 'top-right',
    autoClose: 5000
  });

  return appError;
};

/**
 * Create error message from unknown error
 */
export const createErrorMessage = (error: unknown): string => {
  if (error instanceof Error) return error.message;
  if (typeof error === 'string') return error;
  return 'An unexpected error occurred';
};

// Export default functions for error handling
export default {
  createError,
  setupGlobalErrorHandlers,
  handleComponentError,
  handleError,
  createErrorMessage,
};
