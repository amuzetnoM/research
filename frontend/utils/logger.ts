/**
 * Logger utility for consistent logging across the application
 * Supports different log levels and formats
 */

// Log levels enum
export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
}

// Interface for logger options
interface LoggerOptions {
  level: LogLevel;
  enableConsole: boolean;
  enableStorage: boolean;
  storageKey: string;
  maxLogEntries: number;
}

// Log entry structure
export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  context?: any;
}

// Default logger configuration
const DEFAULT_OPTIONS: LoggerOptions = {
  level: process.env.NODE_ENV === 'production' ? LogLevel.INFO : LogLevel.DEBUG,
  enableConsole: true,
  enableStorage: true,
  storageKey: 'research_dashboard_logs',
  maxLogEntries: 1000,
};

class Logger {
  private options: LoggerOptions;
  private logs: LogEntry[] = [];

  constructor(options: Partial<LoggerOptions> = {}) {
    this.options = { ...DEFAULT_OPTIONS, ...options };
    this.loadLogsFromStorage();
  }

  /**
   * Log a debug message
   */
  public debug(message: string, context?: any): void {
    this.log(LogLevel.DEBUG, message, context);
  }

  /**
   * Log an info message
   */
  public info(message: string, context?: any): void {
    this.log(LogLevel.INFO, message, context);
  }

  /**
   * Log a warning message
   */
  public warn(message: string, context?: any): void {
    this.log(LogLevel.WARN, message, context);
  }

  /**
   * Log an error message
   */
  public error(message: string, context?: any): void {
    this.log(LogLevel.ERROR, message, context);
  }

  /**
   * Get all logs
   */
  public getLogs(): LogEntry[] {
    return [...this.logs];
  }

  /**
   * Clear all logs
   */
  public clearLogs(): void {
    this.logs = [];
    if (this.options.enableStorage) {
      try {
        localStorage.removeItem(this.options.storageKey);
      } catch (error) {
        console.error('Failed to clear logs from storage', error);
      }
    }
  }

  /**
   * Set logger options
   */
  public setOptions(options: Partial<LoggerOptions>): void {
    this.options = { ...this.options, ...options };
  }

  /**
   * Internal logging implementation
   */
  private log(level: LogLevel, message: string, context?: any): void {
    // Check if this log level should be processed
    if (!this.shouldLog(level)) {
      return;
    }

    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context: context ? this.sanitizeContext(context) : undefined,
    };

    // Add to internal logs array
    this.logs.push(entry);
    
    // Trim logs if exceeding max entries
    if (this.logs.length > this.options.maxLogEntries) {
      this.logs = this.logs.slice(-this.options.maxLogEntries);
    }

    // Log to console if enabled
    if (this.options.enableConsole) {
      this.logToConsole(entry);
    }

    // Store in localStorage if enabled
    if (this.options.enableStorage) {
      this.saveLogsToStorage();
    }
  }

  /**
   * Determine if a log level should be processed
   */
  private shouldLog(level: LogLevel): boolean {
    const levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR];
    const configuredLevelIndex = levels.indexOf(this.options.level);
    const currentLevelIndex = levels.indexOf(level);
    
    return currentLevelIndex >= configuredLevelIndex;
  }

  /**
   * Output log to console with appropriate styling
   */
  private logToConsole(entry: LogEntry): void {
    const { timestamp, level, message, context } = entry;
    const timeString = timestamp.split('T')[1].split('.')[0];
    
    const styles = {
      [LogLevel.DEBUG]: 'color: #6c757d',
      [LogLevel.INFO]: 'color: #0ea5e9',
      [LogLevel.WARN]: 'color: #f59e0b',
      [LogLevel.ERROR]: 'color: #ef4444; font-weight: bold',
    };

    // Format with or without context
    if (context) {
      console[level === LogLevel.DEBUG ? 'log' : level](
        `%c[${timeString}] [${level.toUpperCase()}] ${message}`,
        styles[level],
        context
      );
    } else {
      console[level === LogLevel.DEBUG ? 'log' : level](
        `%c[${timeString}] [${level.toUpperCase()}] ${message}`,
        styles[level]
      );
    }
  }

  /**
   * Save logs to localStorage
   */
  private saveLogsToStorage(): void {
    try {
      localStorage.setItem(this.options.storageKey, JSON.stringify(this.logs));
    } catch (error) {
      console.error('Failed to save logs to storage', error);
    }
  }

  /**
   * Load logs from localStorage
   */
  private loadLogsFromStorage(): void {
    try {
      const storedLogs = localStorage.getItem(this.options.storageKey);
      if (storedLogs) {
        const parsedLogs = JSON.parse(storedLogs) as LogEntry[];
        this.logs = parsedLogs;
      }
    } catch (error) {
      console.error('Failed to load logs from storage', error);
    }
  }

  /**
   * Sanitize context to prevent circular references
   */
  private sanitizeContext(context: any): any {
    try {
      // Clone the context to avoid modifying the original
      const seen = new WeakSet();
      return JSON.parse(JSON.stringify(context, (key, value) => {
        // Handle circular references
        if (typeof value === 'object' && value !== null) {
          if (seen.has(value)) {
            return '[Circular Reference]';
          }
          seen.add(value);
        }
        // Handle Error objects
        if (value instanceof Error) {
          return {
            name: value.name,
            message: value.message,
            stack: value.stack,
          };
        }
        return value;
      }));
    } catch (error) {
      return { sanitized: `Failed to sanitize context: ${error instanceof Error ? error.message : String(error)}` };
    }
  }
}

// Create and export singleton instance
export const logger = new Logger();

// Export the Logger class for extending if needed
export default Logger;
