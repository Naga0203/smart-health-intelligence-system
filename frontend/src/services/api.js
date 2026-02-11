// ============================================================================
// API Service - Backend Integration
// ============================================================================

import axios from 'axios';

class APIService {
  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  setupInterceptors() {
    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('firebase_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired - handled by auth store
          localStorage.removeItem('firebase_token');
          window.location.href = '/login';
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
