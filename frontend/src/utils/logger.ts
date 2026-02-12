// ============================================================================
// Secure Logger Utility
// ============================================================================
// Provides logging utilities that automatically redact sensitive information

/**
 * Sensitive field patterns to redact
 */
const SENSITIVE_PATTERNS = [
  /token/i,
  /authorization/i,
  /password/i,
  /secret/i,
  /api[_-]?key/i,
  /bearer/i,
  /credential/i,
  /auth/i,
];

/**
 * Check if a key contains sensitive information
 */
function isSensitiveKey(key: string): boolean {
  return SENSITIVE_PATTERNS.some(pattern => pattern.test(key));
}

/**
 * Redact sensitive values from an object
 */
function redactSensitiveData(data: any): any {
  if (data === null || data === undefined) {
    return data;
  }

  if (typeof data === 'string') {
    // Check if string looks like a token (long alphanumeric string)
    if (data.length > 20 && /^[A-Za-z0-9._-]+$/.test(data)) {
      return '[REDACTED]';
    }
    return data;
  }

  if (Array.isArray(data)) {
    return data.map(item => redactSensitiveData(item));
  }

  if (typeof data === 'object') {
    const redacted: any = {};
    for (const [key, value] of Object.entries(data)) {
      if (isSensitiveKey(key)) {
        redacted[key] = '[REDACTED]';
      } else {
        redacted[key] = redactSensitiveData(value);
      }
    }
    return redacted;
  }

  return data;
}

/**
 * Secure logger that redacts sensitive information
 */
export const logger = {
  /**
   * Log info message with redacted sensitive data
   */
  info(message: string, data?: any): void {
    if (data) {
      console.info(message, redactSensitiveData(data));
    } else {
      console.info(message);
    }
  },

  /**
   * Log warning message with redacted sensitive data
   */
  warn(message: string, data?: any): void {
    if (data) {
      console.warn(message, redactSensitiveData(data));
    } else {
      console.warn(message);
    }
  },

  /**
   * Log error message with redacted sensitive data
   */
  error(message: string, error?: any): void {
    if (error) {
      // Redact error object but preserve stack trace
      const redactedError = {
        message: error.message,
        name: error.name,
        stack: error.stack,
        ...redactSensitiveData(error),
      };
      console.error(message, redactedError);
    } else {
      console.error(message);
    }
  },

  /**
   * Log debug message with redacted sensitive data (only in development)
   */
  debug(message: string, data?: any): void {
    if (import.meta.env.DEV) {
      if (data) {
        console.debug(message, redactSensitiveData(data));
      } else {
        console.debug(message);
      }
    }
  },

  /**
   * Redact sensitive data from any value
   */
  redact(data: any): any {
    return redactSensitiveData(data);
  },
};

/**
 * Override console methods in production to prevent accidental logging
 */
export function setupSecureLogging(): void {
  if (import.meta.env.PROD) {
    const originalConsole = { ...console };
    
    console.log = (...args: any[]) => {
      originalConsole.log(...args.map(arg => redactSensitiveData(arg)));
    };
    
    console.info = (...args: any[]) => {
      originalConsole.info(...args.map(arg => redactSensitiveData(arg)));
    };
    
    console.warn = (...args: any[]) => {
      originalConsole.warn(...args.map(arg => redactSensitiveData(arg)));
    };
    
    console.error = (...args: any[]) => {
      originalConsole.error(...args.map(arg => redactSensitiveData(arg)));
    };
    
    console.debug = () => {
      // Disable debug logging in production
    };
  }
}
