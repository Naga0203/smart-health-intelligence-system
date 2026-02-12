// ============================================================================
// Error Handler Utility
// ============================================================================
// Requirements: 9.1, 9.2, 9.3, 9.4, 9.6, 9.7
// - Custom AppError class for structured error handling
// - handleAPIError function to process different error types
// - displayError function to show user-friendly notifications

import { AxiosError } from 'axios';
import { useNotificationStore } from '@/stores/notificationStore';

/**
 * Custom application error class
 */
export class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode?: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'AppError';
    Object.setPrototypeOf(this, AppError.prototype);
  }
}

/**
 * Handle API errors and convert to AppError
 */
export function handleAPIError(error: unknown): AppError {
  // Handle Axios errors
  if (error && typeof error === 'object' && 'isAxiosError' in error) {
    const axiosError = error as AxiosError;
    const statusCode = axiosError.response?.status;
    const message = axiosError.response?.data?.message || axiosError.message;
    const details = axiosError.response?.data;

    switch (statusCode) {
      case 400:
        return new AppError(
          message || 'Invalid request. Please check your input.',
          'BAD_REQUEST',
          400,
          details
        );

      case 401:
        return new AppError(
          'Authentication required. Please log in.',
          'UNAUTHORIZED',
          401,
          details
        );

      case 403:
        return new AppError(
          'You do not have permission to perform this action.',
          'FORBIDDEN',
          403,
          details
        );

      case 404:
        return new AppError(
          'The requested resource was not found.',
          'NOT_FOUND',
          404,
          details
        );

      case 429:
        return new AppError(
          'Rate limit exceeded. Please try again later.',
          'RATE_LIMIT',
          429,
          details
        );

      case 500:
        return new AppError(
          'Server error. Please try again later.',
          'SERVER_ERROR',
          500,
          details
        );

      case 502:
        return new AppError(
          'Bad gateway. The server is temporarily unavailable.',
          'BAD_GATEWAY',
          502,
          details
        );

      case 503:
        return new AppError(
          'Service unavailable. Please try again later.',
          'SERVICE_UNAVAILABLE',
          503,
          details
        );

      default:
        // Network error (no response)
        if (!error.response) {
          return new AppError(
            'Network error. Please check your connection.',
            'NETWORK_ERROR',
            undefined,
            details
          );
        }

        return new AppError(
          message || 'An unexpected error occurred.',
          'UNKNOWN_ERROR',
          statusCode,
          details
        );
    }
  }

  // Handle AppError instances
  if (error instanceof AppError) {
    return error;
  }

  // Handle generic Error instances
  if (error instanceof Error) {
    return new AppError(error.message, 'UNKNOWN_ERROR');
  }

  // Handle unknown error types
  return new AppError(
    'An unexpected error occurred.',
    'UNKNOWN_ERROR',
    undefined,
    error
  );
}

/**
 * Display error notification to user
 */
export function displayError(error: unknown): void {
  const appError = handleAPIError(error);
  const notificationStore = useNotificationStore.getState();

  // Determine notification type based on error code
  let notificationType: 'error' | 'warning' = 'error';
  
  if (appError.code === 'RATE_LIMIT' || appError.code === 'BAD_GATEWAY' || appError.code === 'SERVICE_UNAVAILABLE') {
    notificationType = 'warning';
  }

  // Add notification
  notificationStore.addNotification({
    type: notificationType,
    message: appError.message,
    dismissible: true,
  });

  // Log error details for debugging (without sensitive data)
  if (import.meta.env.DEV) {
    console.error('Error details:', {
      code: appError.code,
      statusCode: appError.statusCode,
      message: appError.message,
      // Don't log full details as they might contain sensitive data
    });
  }
}

/**
 * Display critical error modal
 */
export function displayCriticalError(
  title: string,
  message: string,
  details?: string
): void {
  const notificationStore = useNotificationStore.getState();
  
  notificationStore.setCriticalError({
    title,
    message,
    details,
  });
}

/**
 * Check if error is retryable
 */
export function isRetryableError(error: unknown): boolean {
  const appError = handleAPIError(error);
  
  // Retry on network errors, server errors, and rate limits
  const retryableCodes = [
    'NETWORK_ERROR',
    'SERVER_ERROR',
    'BAD_GATEWAY',
    'SERVICE_UNAVAILABLE',
    'RATE_LIMIT',
  ];
  
  return retryableCodes.includes(appError.code);
}

/**
 * Get user-friendly error message
 */
export function getErrorMessage(error: unknown): string {
  const appError = handleAPIError(error);
  return appError.message;
}
