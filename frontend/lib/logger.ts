/**
 * Frontend logging utility with different log levels
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
}

class Logger {
  private level: LogLevel;
  private isDevelopment: boolean;

  constructor() {
    this.isDevelopment = process.env.NODE_ENV === 'development';
    this.level = this.isDevelopment ? LogLevel.DEBUG : LogLevel.INFO;
  }

  private shouldLog(level: LogLevel): boolean {
    return level >= this.level;
  }

  private formatMessage(level: string, message: string, data?: any): string {
    const timestamp = new Date().toISOString();
    const dataStr = data ? `\n${JSON.stringify(data, null, 2)}` : '';
    return `[${timestamp}] [${level}] ${message}${dataStr}`;
  }

  debug(message: string, data?: any) {
    if (this.shouldLog(LogLevel.DEBUG)) {
      console.log(this.formatMessage('DEBUG', message, data));
    }
  }

  info(message: string, data?: any) {
    if (this.shouldLog(LogLevel.INFO)) {
      console.info(this.formatMessage('INFO', message, data));
    }
  }

  warn(message: string, data?: any) {
    if (this.shouldLog(LogLevel.WARN)) {
      console.warn(this.formatMessage('WARN', message, data));
    }
  }

  error(message: string, error?: any) {
    if (this.shouldLog(LogLevel.ERROR)) {
      const errorData = error instanceof Error 
        ? { message: error.message, stack: error.stack }
        : error;
      console.error(this.formatMessage('ERROR', message, errorData));
    }
  }

  // API specific loggers
  apiRequest(endpoint: string, method: string, params?: any) {
    this.debug(`API Request: ${method} ${endpoint}`, params);
  }

  apiResponse(endpoint: string, status: number, data?: any) {
    this.debug(`API Response: ${endpoint} [${status}]`, data);
  }

  apiError(endpoint: string, error: any) {
    this.error(`API Error: ${endpoint}`, error);
  }

  // User interaction loggers
  userAction(action: string, details?: any) {
    this.info(`User Action: ${action}`, details);
  }

  // Performance loggers
  performance(label: string, duration: number) {
    this.debug(`Performance: ${label} took ${duration.toFixed(2)}ms`);
  }
}

export const logger = new Logger();

