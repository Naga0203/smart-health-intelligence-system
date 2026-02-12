// ============================================================================
// Rate Limit Handler Utility
// ============================================================================
// Requirements: 9.1, 9.2, 9.3
// - Display specific messages for authenticated vs anonymous users
// - Show rate limit details (10/min, 100/hour, 200/day for auth; 5/hour for anon)
// - Suggest account creation for anonymous users

import { useNotificationStore } from '@/stores/notificationStore';
import { useAuthStore } from '@/stores/authStore';

/**
 * Rate limit information for different user types
 */
export const RATE_LIMITS = {
  authenticated: {
    perMinute: 10,
    perHour: 100,
    perDay: 200,
  },
  anonymous: {
    perHour: 5,
  },
} as const;

/**
 * Format rate limit message for authenticated users
 */
function getAuthenticatedRateLimitMessage(waitSeconds?: number): string {
  const limits = RATE_LIMITS.authenticated;
  
  let message = `Rate limit exceeded. You can make ${limits.perMinute} requests per minute, ${limits.perHour} per hour, and ${limits.perDay} per day.`;
  
  if (waitSeconds) {
    const minutes = Math.ceil(waitSeconds / 60);
    if (minutes > 1) {
      message += ` Please wait ${minutes} minutes before trying again.`;
    } else {
      message += ` Please wait ${waitSeconds} seconds before trying again.`;
    }
  } else {
    message += ' Please wait a moment before trying again.';
  }
  
  return message;
}

/**
 * Format rate limit message for anonymous users
 */
function getAnonymousRateLimitMessage(waitSeconds?: number): string {
  const limits = RATE_LIMITS.anonymous;
  
  let message = `Rate limit exceeded. Anonymous users can make ${limits.perHour} requests per hour.`;
  
  if (waitSeconds) {
    const minutes = Math.ceil(waitSeconds / 60);
    if (minutes > 1) {
      message += ` Please wait ${minutes} minutes before trying again.`;
    } else {
      message += ` Please wait ${waitSeconds} seconds before trying again.`;
    }
  } else {
    message += ' Please wait before trying again.';
  }
  
  message += '\n\nCreate a free account to get higher rate limits and access more features!';
  
  return message;
}

/**
 * Handle rate limit error and display appropriate message
 */
export function handleRateLimitError(
  waitSeconds?: number,
  errorDetails?: unknown
): void {
  const authState = useAuthStore.getState();
  const notificationStore = useNotificationStore.getState();
  
  const isAuthenticated = !!authState.user;
  
  const message = isAuthenticated
    ? getAuthenticatedRateLimitMessage(waitSeconds)
    : getAnonymousRateLimitMessage(waitSeconds);
  
  notificationStore.addNotification({
    type: 'warning',
    message,
    dismissible: true,
  });
  
  // Log for debugging
  if (import.meta.env.DEV) {
    console.warn('Rate limit exceeded:', {
      isAuthenticated,
      waitSeconds,
      errorDetails,
    });
  }
}

/**
 * Extract wait time from rate limit error response
 */
export function extractWaitTime(errorResponse: unknown): number | undefined {
  if (
    errorResponse &&
    typeof errorResponse === 'object' &&
    'wait_seconds' in errorResponse
  ) {
    const waitSeconds = (errorResponse as { wait_seconds?: number }).wait_seconds;
    return typeof waitSeconds === 'number' ? waitSeconds : undefined;
  }
  
  // Try to extract from Retry-After header (if available)
  if (
    errorResponse &&
    typeof errorResponse === 'object' &&
    'headers' in errorResponse
  ) {
    const headers = (errorResponse as { headers?: Record<string, string> }).headers;
    if (headers && 'retry-after' in headers) {
      const retryAfter = parseInt(headers['retry-after'], 10);
      if (!isNaN(retryAfter)) {
        return retryAfter;
      }
    }
  }
  
  return undefined;
}

/**
 * Check if user should be prompted to create account
 */
export function shouldPromptAccountCreation(): boolean {
  const authState = useAuthStore.getState();
  return !authState.user;
}

/**
 * Display account creation prompt
 */
export function displayAccountCreationPrompt(): void {
  const notificationStore = useNotificationStore.getState();
  
  notificationStore.addNotification({
    type: 'info',
    message: 'Create a free account to get higher rate limits and save your assessment history!',
    dismissible: true,
  });
}
