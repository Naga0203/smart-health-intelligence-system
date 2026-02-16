// ============================================================================
// API Service - Backend Integration
// ============================================================================

import axios, { AxiosInstance } from 'axios';
import { getCsrfToken, requiresCsrfProtection } from '@/utils/csrf';
import { tokenStorage } from '@/utils/secureStorage';

class APIService {
  private client: AxiosInstance;
  private isRefreshing: boolean;
  private failedQueue: any[];

  constructor() {
    const baseURL = import.meta.env.VITE_API_BASE_URL || '';

    // Validate HTTPS in production
    if (import.meta.env.PROD && !baseURL.startsWith('https://')) {
      console.error('SECURITY WARNING: API base URL must use HTTPS in production');
      throw new Error('API base URL must use HTTPS in production');
    }

    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // Enable cookies for CSRF
    });

    this.isRefreshing = false;
    this.failedQueue = [];
    this.setupInterceptors();
  }

  /**
   * Process queued requests after token refresh
   */
  processQueue(error: any, token: string | null = null) {
    this.failedQueue.forEach((prom) => {
      if (error) {
        prom.reject(error);
      } else {
        prom.resolve(token);
      }
    });

    this.failedQueue = [];
  }

  setupInterceptors() {
    // Request interceptor - add auth token and CSRF token
    this.client.interceptors.request.use(
      (config) => {
        const token = tokenStorage.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Add CSRF token for state-changing requests
        if (requiresCsrfProtection(config.method || 'GET')) {
          const csrfToken = getCsrfToken();
          if (csrfToken) {
            config.headers['X-CSRFToken'] = csrfToken;
          }
        }

        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // Handle 401 Unauthorized - Token expired
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // Queue the request while token is being refreshed
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject });
            })
              .then((token) => {
                originalRequest.headers.Authorization = `Bearer ${token}`;
                return this.client(originalRequest);
              })
              .catch((err) => {
                return Promise.reject(err);
              });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            // Attempt to refresh token using auth store
            const { useAuthStore } = await import('@/stores/authStore');
            await useAuthStore.getState().refreshToken();

            const newToken = tokenStorage.getToken();

            if (newToken) {
              this.processQueue(null, newToken);
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              this.isRefreshing = false;
              return this.client(originalRequest);
            } else {
              throw new Error('Token refresh failed - no token returned');
            }
          } catch (refreshError) {
            this.processQueue(refreshError, null);
            this.isRefreshing = false;

            // Clear auth and redirect to login
            const { useAuthStore } = await import('@/stores/authStore');
            const { useNotificationStore } = await import('@/stores/notificationStore');

            useAuthStore.getState().logout();

            // Notify user
            useNotificationStore.getState().addNotification({
              type: 'warning',
              message: 'Your session has expired. Please log in again.',
              dismissible: true,
            });

            if (typeof window !== 'undefined') {
              window.location.href = '/login';
            }

            return Promise.reject(refreshError);
          }
        }

        // Handle 429 Rate Limit
        if (error.response?.status === 429) {
          const { handleRateLimitError, extractWaitTime } = await import('@/utils/rateLimitHandler');
          const waitSeconds = extractWaitTime(error.response.data);
          handleRateLimitError(waitSeconds, error.response.data);
        }

        // Handle 400 Bad Request
        if (error.response?.status === 400) {
          const { useNotificationStore } = await import('@/stores/notificationStore');
          const message = error.response.data?.message || 'Invalid request. Please check your input.';

          useNotificationStore.getState().addNotification({
            type: 'error',
            message,
            dismissible: true,
          });
        }

        // Handle 500 Server Error
        if (error.response?.status === 500) {
          const { useNotificationStore } = await import('@/stores/notificationStore');

          useNotificationStore.getState().addNotification({
            type: 'error',
            message: 'Server error. Please try again later.',
            dismissible: true,
          });
        }

        // Handle Network Errors
        if (!error.response) {
          const { useNotificationStore } = await import('@/stores/notificationStore');

          useNotificationStore.getState().addNotification({
            type: 'error',
            message: 'Network error. Please check your connection.',
            dismissible: true,
          });
        }

        return Promise.reject(error);
      }
    );
  }

  // ============================================================================
  // Health Analysis Endpoints
  // ============================================================================

  /**
   * POST /api/health/analyze/ - Authenticated health analysis
   */
  async analyzeHealth(data) {
    const response = await this.client.post('/api/health/analyze/', data);
    return response.data;
  }

  /**
   * POST /api/assess/ - Anonymous health assessment
   */
  async assessAnonymous(data) {
    const response = await this.client.post('/api/assess/', data);
    return response.data;
  }

  // ============================================================================
  // User Profile Endpoints
  // ============================================================================

  /**
   * GET /api/user/profile/ - Get user profile
   */
  async getUserProfile() {
    const response = await this.client.get('/api/user/profile/');
    return response.data;
  }

  /**
   * PUT /api/user/profile/ - Update user profile
   */
  async updateUserProfile(data) {
    const response = await this.client.put('/api/user/profile/', data);
    return response.data;
  }

  /**
   * GET /api/user/statistics/ - Get user statistics
   */
  async getUserStatistics() {
    const response = await this.client.get('/api/user/statistics/');
    return response.data;
  }

  // ============================================================================
  // Assessment History Endpoints
  // ============================================================================

  /**
   * GET /api/user/assessments/ - Get assessment history
   */
  async getAssessmentHistory(page = 1, pageSize = 10) {
    const response = await this.client.get('/api/user/assessments/', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  }

  /**
   * GET /api/user/assessments/{id}/ - Get assessment detail
   */
  async getAssessmentDetail(id) {
    const response = await this.client.get(`/api/user/assessments/${id}/`);
    return response.data;
  }

  // ============================================================================
  // Prediction Endpoints
  // ============================================================================

  /**
   * POST /api/predict/top/ - Get top N predictions
   */
  async getTopPredictions(symptoms, age, gender, n = 5) {
    const response = await this.client.post('/api/predict/top/', {
      symptoms,
      age,
      gender,
      n,
    });
    return response.data;
  }

  // ============================================================================
  // System Status Endpoints
  // ============================================================================

  /**
   * GET /api/status/ - Get system status
   */
  async getSystemStatus() {
    const response = await this.client.get('/api/status/');
    return response.data;
  }

  /**
   * GET /api/health/ - Health check
   */
  async getHealthCheck() {
    const response = await this.client.get('/api/health/');
    return response.data;
  }

  /**
   * GET /api/model/info/ - Get model information
   */
  async getModelInfo() {
    const response = await this.client.get('/api/model/info/');
    return response.data;
  }

  /**
   * GET /api/diseases/ - Get supported diseases
   */
  async getDiseases() {
    const response = await this.client.get('/api/diseases/');
    return response.data;
  }
}

export const apiService = new APIService();
