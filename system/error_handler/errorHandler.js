const fs = require('fs');
const path = require('path');
const winston = require('winston');
const os = require('os');
const { v4: uuidv4 } = require('uuid');

// Define absolute path for logs to ensure consistency throughout the system
const SYSTEM_ROOT = path.resolve(path.join(__dirname, '..', '..'));
const LOGS_DIR = path.join(SYSTEM_ROOT, 'system', 'logs');

// Create logs directory if it doesn't exist
if (!fs.existsSync(LOGS_DIR)) {
  fs.mkdirSync(LOGS_DIR, { recursive: true });
}

// Create different log folders for different types of logs
const ERROR_LOGS = path.join(LOGS_DIR, 'errors');
const PERFORMANCE_LOGS = path.join(LOGS_DIR, 'performance');
const SECURITY_LOGS = path.join(LOGS_DIR, 'security');
const APPLICATION_LOGS = path.join(LOGS_DIR, 'application');

// Ensure all log directories exist
[ERROR_LOGS, PERFORMANCE_LOGS, SECURITY_LOGS, APPLICATION_LOGS].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// Custom log formatting
const customFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
  winston.format.errors({ stack: true }),
  winston.format.metadata(),
  winston.format.json()
);

// System information for enriching log entries
const systemInfo = {
  hostname: os.hostname(),
  platform: os.platform(),
  arch: os.arch(),
  cpus: os.cpus().length,
  memory: Math.round(os.totalmem() / (1024 * 1024 * 1024)) + 'GB',
  nodeVersion: process.version
};

// Create loggers for different purposes
const errorLogger = winston.createLogger({
  level: 'error',
  format: customFormat,
  defaultMeta: { 
    service: 'error-service', 
    system: systemInfo 
  },
  transports: [
    new winston.transports.File({ 
      filename: path.join(ERROR_LOGS, 'error.log')
    })
  ],
});

const performanceLogger = winston.createLogger({
  level: 'info',
  format: customFormat,
  defaultMeta: { 
    service: 'performance-service', 
    system: systemInfo 
  },
  transports: [
    new winston.transports.File({ 
      filename: path.join(PERFORMANCE_LOGS, 'performance.log')
    })
  ],
});

const securityLogger = winston.createLogger({
  level: 'info',
  format: customFormat,
  defaultMeta: { 
    service: 'security-service', 
    system: systemInfo 
  },
  transports: [
    new winston.transports.File({ 
      filename: path.join(SECURITY_LOGS, 'security.log')
    })
  ],
});

const applicationLogger = winston.createLogger({
  level: 'info',
  format: customFormat,
  defaultMeta: { 
    service: 'application-service', 
    system: systemInfo 
  },
  transports: [
    new winston.transports.File({ 
      filename: path.join(APPLICATION_LOGS, 'application.log')
    })
  ],
});

// Add console transport in development environment
if (process.env.NODE_ENV !== 'production') {
  const consoleFormat = winston.format.combine(
    winston.format.colorize(),
    winston.format.timestamp({ format: 'HH:mm:ss' }),
    winston.format.printf(info => {
      const { timestamp, level, message, service, ...meta } = info;
      return `[${timestamp}] [${service}] ${level}: ${message} ${
        Object.keys(meta).length ? JSON.stringify(meta, null, 2) : ''
      }`;
    })
  );

  const consoleTransport = new winston.transports.Console({ format: consoleFormat });
  
  errorLogger.add(consoleTransport);
  performanceLogger.add(consoleTransport);
  securityLogger.add(consoleTransport);
  applicationLogger.add(consoleTransport);
}

// Unified logger interface
const logger = {
  error: (message, meta = {}) => errorLogger.error(message, meta),
  warn: (message, meta = {}) => applicationLogger.warn(message, meta),
  info: (message, meta = {}) => applicationLogger.info(message, meta),
  http: (message, meta = {}) => applicationLogger.http(message, meta),
  verbose: (message, meta = {}) => applicationLogger.verbose(message, meta),
  debug: (message, meta = {}) => applicationLogger.debug(message, meta),
  silly: (message, meta = {}) => applicationLogger.silly(message, meta),
  performance: (message, meta = {}) => performanceLogger.info(message, meta),
  security: (message, meta = {}) => securityLogger.info(message, meta)
};

// Enhanced error classes with more context and functionality
class SystemError extends Error {
  constructor(message, options = {}) {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = options.statusCode || 500;
    this.errorCode = options.errorCode || 'SYSTEM_ERROR';
    this.severity = options.severity || 'error';
    this.details = options.details || {};
    this.timestamp = new Date().toISOString();
    this.id = uuidv4();
    this.isOperational = options.isOperational || true;  // Helps distinguish operational vs programmer errors
    this.source = options.source || 'system';
    
    // Capture stack trace excluding the constructor call
    Error.captureStackTrace(this, this.constructor);
    
    // Log error automatically when created
    this.log();
  }
  
  log() {
    const logData = {
      errorId: this.id,
      name: this.name,
      message: this.message,
      code: this.errorCode,
      severity: this.severity,
      details: this.details,
      stack: this.stack,
      source: this.source
    };
    
    logger.error(`${this.name}: ${this.message}`, logData);
    return this;
  }
  
  toJSON() {
    return {
      id: this.id,
      name: this.name,
      message: this.message,
      code: this.errorCode,
      statusCode: this.statusCode,
      timestamp: this.timestamp,
      details: this.details
    };
  }
}

// Specialized error classes
class DocumentationError extends SystemError {
  constructor(message, options = {}) {
    super(message, { 
      ...options,
      source: 'documentation',
      errorCode: options.errorCode || 'DOC_ERROR'
    });
  }
}

class DataProcessingError extends SystemError {
  constructor(message, options = {}) {
    super(message, { 
      ...options,
      source: 'data-processing',
      errorCode: options.errorCode || 'DATA_PROC_ERROR'
    });
  }
}

class ModelError extends SystemError {
  constructor(message, options = {}) {
    super(message, { 
      ...options,
      source: 'model',
      errorCode: options.errorCode || 'MODEL_ERROR'
    });
  }
}

class NetworkError extends SystemError {
  constructor(message, options = {}) {
    super(message, { 
      ...options,
      source: 'network',
      errorCode: options.errorCode || 'NETWORK_ERROR'
    });
  }
}

class ValidationError extends SystemError {
  constructor(message, options = {}) {
    super(message, { 
      ...options,
      statusCode: options.statusCode || 400,
      source: 'validation',
      errorCode: options.errorCode || 'VALIDATION_ERROR'
    });
  }
}

class AuthenticationError extends SystemError {
  constructor(message, options = {}) {
    super(message, { 
      ...options,
      statusCode: options.statusCode || 401,
      source: 'authentication',
      errorCode: options.errorCode || 'AUTH_ERROR'
    });
  }
}

class AuthorizationError extends SystemError {
  constructor(message, options = {}) {
    super(message, { 
      ...options,
      statusCode: options.statusCode || 403,
      source: 'authorization',
      errorCode: options.errorCode || 'ACCESS_DENIED'
    });
  }
}

class ResourceNotFoundError extends SystemError {
  constructor(resource, id, options = {}) {
    super(`${resource} with ID ${id} not found`, { 
      ...options,
      statusCode: 404,
      source: resource.toLowerCase(),
      errorCode: options.errorCode || 'NOT_FOUND',
      details: { 
        ...options.details,
        resourceType: resource,
        resourceId: id
      }
    });
  }
}

// For backward compatibility
class DocumentNotFoundError extends ResourceNotFoundError {
  constructor(docId, options = {}) {
    super('Document', docId, options);
  }
}

class InvalidDocumentError extends ValidationError {
  constructor(message, options = {}) {
    super(message, {
      ...options,
      source: 'document-validation'
    });
  }
}

class AccessDeniedError extends AuthorizationError {
  constructor(message, options = {}) {
    super(message, options);
  }
}

// Performance monitoring
const startTimer = () => {
  const start = process.hrtime();
  return {
    end: (label) => {
      const diff = process.hrtime(start);
      const duration = (diff[0] * 1e9 + diff[1]) / 1e6; // Convert to milliseconds
      logger.performance(`Timer: ${label}`, { 
        label, 
        durationMs: duration.toFixed(3),
        timestamp: new Date().toISOString()
      });
      return duration;
    }
  };
};

// Express middleware
const errorMiddleware = (err, req, res, next) => {
  // Convert plain errors to SystemErrors
  let systemError = err;
  if (!(err instanceof SystemError)) {
    systemError = new SystemError(err.message, {
      statusCode: err.statusCode || 500,
      details: {
        originalError: {
          name: err.name,
          message: err.message,
          
        }
      }
    });
  }
  
  // Enrich with request information
  const requestInfo = {
    path: req.path,
    method: req.method,
    params: req.params,
    query: req.query,
    body: req.body,
    user: req.user ? req.user.id : 'anonymous',
    ip: req.ip,
    userAgent: req.get('User-Agent')
  };
  
  // Log the enriched error
  logger.error(`Request Error: ${err.message}`, {
    error: systemError.toJSON(),
    request: requestInfo
  });

  // Send appropriate response
  const statusCode = systemError.statusCode || 500;
  const errorResponse = {
    error: {
      id: systemError.id,
      code: systemError.errorCode,
      name: systemError.name,
      message: systemError.message,
      status: statusCode,
    },
  };
  
  // Include error details in development mode
  if (process.env.NODE_ENV !== 'production' && systemError.details) {
    errorResponse.error.details = systemError.details;
    errorResponse.error.stack = systemError.stack;
  }
  
  res.status(statusCode).json(errorResponse);
};

// Smarter async handler with timeout and better error capturing
const asyncHandler = (fn, options = {}) => {
  const timeout = options.timeout || 30000; // Default 30s timeout

  return (req, res, next) => {
    const timer = startTimer();
    let timeoutId;
    
    // Create promise that rejects on timeout
    const timeoutPromise = new Promise((_, reject) => {
      timeoutId = setTimeout(() => {
        reject(new SystemError(`Request timeout after ${timeout}ms`, {
          statusCode: 408,
          errorCode: 'REQUEST_TIMEOUT'
        }));
      }, timeout);
    });
    
    // Race the handler against the timeout
    Promise.race([
      Promise.resolve(fn(req, res, next)),
      timeoutPromise
    ])
      .then(result => {
        clearTimeout(timeoutId);
        const duration = timer.end(`${req.method} ${req.path}`);
        
        // Log slow requests
        if (duration > 1000) { // Over 1 second
          logger.performance('Slow Request', {
            path: req.path,
            method: req.method,
            durationMs: duration.toFixed(2),
            threshold: 1000
          });
        }
        
        return result;
      })
      .catch(error => {
        clearTimeout(timeoutId);
        next(error);
      });
  };
};

// Global error handler for uncaught exceptions and unhandled rejections
const setupGlobalErrorHandlers = () => {
  process.on('uncaughtException', (error) => {
    const systemError = new SystemError(`Uncaught Exception: ${error.message}`, {
      isOperational: false,
      details: { 
        originalError: {
          name: error.name,
          message: error.message,
          stack: error.stack
        }
      }
    });
    
    logger.error('UNCAUGHT EXCEPTION - Application will exit', {
      error: systemError.toJSON()
    });
    
    // Allow logs to be written before exiting
    setTimeout(() => {
      process.exit(1);
    }, 1000);
  });

  process.on('unhandledRejection', (reason, promise) => {
    const systemError = new SystemError('Unhandled Promise Rejection', {
      isOperational: false,
      details: {
        reason: reason instanceof Error ? {
          name: reason.name,
          message: reason.message,
          stack: reason.stack
        } : reason
      }
    });
    
    logger.error('UNHANDLED REJECTION', {
      error: systemError.toJSON()
    });
  });
  
  // Monitor memory usage
  const memoryMonitorInterval = setInterval(() => {
    const memoryUsage = process.memoryUsage();
    const formattedMemory = {
      rss: `${Math.round(memoryUsage.rss / 1024 / 1024)}MB`,
      heapTotal: `${Math.round(memoryUsage.heapTotal / 1024 / 1024)}MB`,
      heapUsed: `${Math.round(memoryUsage.heapUsed / 1024 / 1024)}MB`,
      external: `${Math.round(memoryUsage.external / 1024 / 1024)}MB`
    };
    
    logger.performance('Memory Usage', {
      ...formattedMemory,
      rawBytes: memoryUsage
    });
    
    // Alert on high memory usage
    const heapUsedPercentage = (memoryUsage.heapUsed / memoryUsage.heapTotal) * 100;
    if (heapUsedPercentage > 85) {
      logger.error('HIGH MEMORY USAGE', {
        usage: formattedMemory,
        percentage: `${heapUsedPercentage.toFixed(2)}%`
      });
    }
  }, 5 * 60 * 1000); // Every 5 minutes
  
  // Ensure we clean up the interval on process exit
  process.on('exit', () => {
    clearInterval(memoryMonitorInterval);
    logger.info('Process exiting', { timestamp: new Date().toISOString() });
  });
};

// Path constants exported to ensure consistent log path usage across the application
const LOG_PATHS = {
  SYSTEM_ROOT,
  LOGS_DIR,
  ERROR_LOGS,
  PERFORMANCE_LOGS,
  SECURITY_LOGS,
  APPLICATION_LOGS,
};

module.exports = {
  logger,
  LOG_PATHS,
  SystemError,
  DocumentationError,
  DataProcessingError,
  ModelError,
  NetworkError,
  ValidationError,
  AuthenticationError,
  AuthorizationError,
  ResourceNotFoundError,
  DocumentNotFoundError,
  InvalidDocumentError,
  AccessDeniedError,
  errorMiddleware,
  asyncHandler,
  startTimer,
  setupGlobalErrorHandlers,
};
