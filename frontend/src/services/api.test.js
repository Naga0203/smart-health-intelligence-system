// ============================================================================
// API Service Tests - Property-Based and Unit Tests
// ============================================================================

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import * as fc from 'fast-check';
import axios from 'axios';

// Mock axios BEFORE importing apiService
vi.mock('axios');

// Mock stores
vi.mock('@/stores/authStore', () => ({
  useAuthStore: {
    getState: () => ({
      refreshToken: vi.fn(),
      logout: vi.fn(),
    }),
  },
}));

vi.mock('@/stores/notificationStore', () => ({
  useNotificationStore: {
    getState: () => ({
      addNotification: vi.fn(),
    }),
  },
}));

describe('API Service', () => {
  let mockAxiosInstance;
  let requestInterceptorSuccess;
  let requestInterceptorError;
  let responseInterceptorSuccess;
  let responseInterceptorError;

  beforeEach(() => {
    // Reset localStorage
    localStorage.clear();
    
    // Create mock axios instance
    mockAxiosInstance = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: {
          use: vi.fn((successHandler, errorHandler) => {
            requestInterceptorSuccess = successHandler;
            requestInterceptorError = errorHandler;
          }),
        },
        response: {
          use: vi.fn((successHandler, errorHandler) => {
            responseInterceptorSuccess = successHandler;
            responseInterceptorError = errorHandler;
          }),
        },
      },
    };

    axios.create.mockReturnValue(mockAxiosInstance);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  // ============================================================================
  // Property-Based Tests
  // ============================================================================

  describe('Property 1: Authenticated API requests include authorization', () => {
    /**
     * Feature: ai-health-frontend
     * Property 1: Authenticated API requests include authorization
     * 
     * For any API request made while authenticated, the request headers should 
     * include the Firebase authentication token in the Authorization header.
     * 
     * Validates: Requirements 1.8
     */
    it('should include Authorization header for any authenticated request', async () => {
      await fc.assert(
        fc.asyncProperty(
          // Generate arbitrary tokens (non-empty strings)
          fc.string({ minLength: 20, maxLength: 200 }),
          // Generate arbitrary API endpoints
          fc.constantFrom(
            '/api/health/analyze/',
            '/api/user/profile/',
            '/api/user/statistics/',
            '/api/user/assessments/',
            '/api/status/',
            '/api/diseases/'
          ),
          async (token, endpoint) => {
            // Setup: Store token in localStorage
            localStorage.setItem('firebase_token', token);

            // Import API service (will use mocked axios)
            const { apiService } = await import('./api.js');
            
            // Create a mock config
            const config = {
              url: endpoint,
              headers: {},
            };

            // Execute the request interceptor
            const modifiedConfig = await requestInterceptorSuccess(config);

            // Verify: Authorization header should be present with Bearer token
            expect(modifiedConfig.headers.Authorization).toBe(`Bearer ${token}`);
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should not include Authorization header when not authenticated', async () => {
      await fc.assert(
        fc.asyncProperty(
          // Generate arbitrary API endpoints
          fc.constantFrom(
            '/api/health/analyze/',
            '/api/user/profile/',
            '/api/assess/',
            '/api/status/'
          ),
          async (endpoint) => {
            // Setup: Ensure no token in localStorage
            localStorage.removeItem('firebase_token');

            // Import API service (will use mocked axios)
            const { apiService } = await import('./api.js');
            
            // Create a mock config
            const config = {
              url: endpoint,
              headers: {},
            };

            // Execute the request interceptor
            const modifiedConfig = await requestInterceptorSuccess(config);

            // Verify: Authorization header should not be present
            expect(modifiedConfig.headers.Authorization).toBeUndefined();
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  // ============================================================================
  // Unit Tests - Error Handling
  // ============================================================================

  describe('Error Handling', () => {
    beforeEach(async () => {
      // Import API service to trigger interceptor setup
      await import('./api.js');
    });

    it('should handle 401 error with token refresh', async () => {
      const { useAuthStore } = await import('@/stores/authStore');
      const mockRefreshToken = vi.fn().mockResolvedValue(undefined);
      useAuthStore.getState = vi.fn(() => ({
        refreshToken: mockRefreshToken,
        logout: vi.fn(),
      }));

      // Setup: Store initial token
      const oldToken = 'old-token-123';
      const newToken = 'new-token-456';
      localStorage.setItem('firebase_token', oldToken);

      // Create error with 401 status
      const error = {
        response: { status: 401 },
        config: { headers: {}, _retry: false },
      };

      // Mock the axios instance call method to return success after retry
      mockAxiosInstance.get.mockResolvedValue({ data: { success: true } });
      mockAxiosInstance.post.mockResolvedValue({ data: { success: true } });
      mockAxiosInstance.put.mockResolvedValue({ data: { success: true } });
      mockAxiosInstance.delete.mockResolvedValue({ data: { success: true } });

      // Simulate token refresh by updating localStorage
      mockRefreshToken.mockImplementation(() => {
        localStorage.setItem('firebase_token', newToken);
        return Promise.resolve();
      });

      // Execute response interceptor error handler
      try {
        await responseInterceptorError(error);
      } catch (e) {
        // Expected to potentially throw, but we're checking if refresh was called
      }

      // Verify: Token refresh was called
      expect(mockRefreshToken).toHaveBeenCalled();
    });

    it('should redirect to login when token refresh fails', async () => {
      const { useAuthStore } = await import('@/stores/authStore');
      const mockLogout = vi.fn();
      const mockRefreshToken = vi.fn().mockRejectedValue(new Error('Refresh failed'));
      
      useAuthStore.getState = vi.fn(() => ({
        refreshToken: mockRefreshToken,
        logout: mockLogout,
      }));

      // Setup: Store initial token
      localStorage.setItem('firebase_token', 'old-token');

      // Create error with 401 status
      const error = {
        response: { status: 401 },
        config: { headers: {}, _retry: false },
      };

      // Execute response interceptor error handler and expect rejection
      await expect(responseInterceptorError(error)).rejects.toThrow();

      // Verify: Logout was called
      expect(mockLogout).toHaveBeenCalled();
    });

    it('should display notification for 429 rate limit error', async () => {
      const { useNotificationStore } = await import('@/stores/notificationStore');
      const mockAddNotification = vi.fn();
      
      useNotificationStore.getState = vi.fn(() => ({
        addNotification: mockAddNotification,
      }));

      // Create error with 429 status
      const error = {
        response: {
          status: 429,
          data: { wait_seconds: 60 },
        },
        config: {},
      };

      // Execute response interceptor error handler
      await expect(responseInterceptorError(error)).rejects.toEqual(error);

      // Verify: Notification was added
      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'warning',
        message: expect.stringContaining('Rate limit exceeded'),
        dismissible: true,
      });
    });

    it('should display notification for 400 bad request error', async () => {
      const { useNotificationStore } = await import('@/stores/notificationStore');
      const mockAddNotification = vi.fn();
      
      useNotificationStore.getState = vi.fn(() => ({
        addNotification: mockAddNotification,
      }));

      // Create error with 400 status
      const error = {
        response: {
          status: 400,
          data: { message: 'Invalid input data' },
        },
        config: {},
      };

      // Execute response interceptor error handler
      await expect(responseInterceptorError(error)).rejects.toEqual(error);

      // Verify: Notification was added with specific message
      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'error',
        message: 'Invalid input data',
        dismissible: true,
      });
    });

    it('should display generic notification for 500 server error', async () => {
      const { useNotificationStore } = await import('@/stores/notificationStore');
      const mockAddNotification = vi.fn();
      
      useNotificationStore.getState = vi.fn(() => ({
        addNotification: mockAddNotification,
      }));

      // Create error with 500 status
      const error = {
        response: {
          status: 500,
          data: {},
        },
        config: {},
      };

      // Execute response interceptor error handler
      await expect(responseInterceptorError(error)).rejects.toEqual(error);

      // Verify: Notification was added
      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'error',
        message: 'Server error. Please try again later.',
        dismissible: true,
      });
    });

    it('should display notification for network error', async () => {
      const { useNotificationStore } = await import('@/stores/notificationStore');
      const mockAddNotification = vi.fn();
      
      useNotificationStore.getState = vi.fn(() => ({
        addNotification: mockAddNotification,
      }));

      // Create network error (no response)
      const error = {
        message: 'Network Error',
        config: {},
      };

      // Execute response interceptor error handler
      await expect(responseInterceptorError(error)).rejects.toEqual(error);

      // Verify: Notification was added
      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'error',
        message: 'Network error. Please check your connection.',
        dismissible: true,
      });
    });
  });
});
