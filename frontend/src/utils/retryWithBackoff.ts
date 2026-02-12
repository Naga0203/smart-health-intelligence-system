// ============================================================================
// Retry with Exponential Backoff Utility
// ============================================================================
// Requirements: 9.8
// - Implement exponential backoff for failed API requests
// - Configure max retry attempts
// - Increase delay exponentially between retries

import { isRetryableError } from './errorHandler';

export interface RetryOptions {
  maxRetries?: number;
  initialDelay?: number;
  maxDelay?: number;
  backoffMultiplier?: number;
  onRetry?: (attempt: number, delay: number, error: unknown) => void;
}

const DEFAULT_OPTIONS: Required<RetryOptions> = {
  maxRetries: 3,
  initialDelay: 1000, // 1 second
  maxDelay: 30000, // 30 seconds
  backoffMultiplier: 2,
  onRetry: () => {},
};

/**
 * Calculate exponential backoff delay
 */
export function calculateBackoffDelay(
  attempt: number,
  initialDelay: number,
  backoffMultiplier: number,
  maxDelay: number
): number {
  // Exponential backoff: initialDelay * (backoffMultiplier ^ attempt)
  const delay = initialDelay * Math.pow(backoffMultiplier, attempt);
  
  // Add jitter (random variation) to prevent thundering herd
  const jitter = Math.random() * 0.3 * delay; // ±30% jitter
  
  // Cap at maxDelay
  return Math.min(delay + jitter, maxDelay);
}

/**
 * Sleep for specified milliseconds
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Retry a function with exponential backoff
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  let lastError: unknown;

  for (let attempt = 0; attempt <= opts.maxRetries; attempt++) {
    try {
      // Attempt the function
      return await fn();
    } catch (error) {
      lastError = error;

      // Check if error is retryable
      if (!isRetryableError(error)) {
        throw error;
      }

      // If this was the last attempt, throw the error
      if (attempt === opts.maxRetries) {
        throw error;
      }

      // Calculate delay for next retry
      const delay = calculateBackoffDelay(
        attempt,
        opts.initialDelay,
        opts.backoffMultiplier,
        opts.maxDelay
      );

      // Call onRetry callback
      opts.onRetry(attempt + 1, delay, error);

      // Wait before retrying
      await sleep(delay);
    }
  }

  // This should never be reached, but TypeScript needs it
  throw lastError;
}

/**
 * Create a retry wrapper for an async function
 */
export function withRetry<TArgs extends unknown[], TReturn>(
  fn: (...args: TArgs) => Promise<TReturn>,
  options: RetryOptions = {}
): (...args: TArgs) => Promise<TReturn> {
  return async (...args: TArgs): Promise<TReturn> => {
    return retryWithBackoff(() => fn(...args), options);
  };
}

/**
 * Retry configuration presets
 */
export const RetryPresets = {
  // Quick retry for fast operations
  quick: {
    maxRetries: 2,
    initialDelay: 500,
    maxDelay: 5000,
    backoffMultiplier: 2,
  } as RetryOptions,

  // Standard retry for most operations
  standard: {
    maxRetries: 3,
    initialDelay: 1000,
    maxDelay: 30000,
    backoffMultiplier: 2,
  } as RetryOptions,

  // Aggressive retry for critical operations
  aggressive: {
    maxRetries: 5,
    initialDelay: 1000,
    maxDelay: 60000,
    backoffMultiplier: 2,
  } as RetryOptions,

  // Conservative retry for rate-limited operations
  conservative: {
    maxRetries: 2,
    initialDelay: 2000,
    maxDelay: 10000,
    backoffMultiplier: 3,
  } as RetryOptions,
} as const;
