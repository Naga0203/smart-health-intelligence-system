// ============================================================================
// API Service - Backend Integration
// ============================================================================

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  AssessmentRequest,
  RiskAssessment,
  UserProfile,
  UserStatistics,
  AssessmentHistory,
  SystemStatus,
  ModelInfo,
  DiseasesResponse,
  Prediction,
  APIError,
} from '@/types';

class APIService {
  private client: AxiosInstance;

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

  private setupInterceptors() {
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
      async (error: AxiosError<APIError>) => {
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
  async analyzeHealth(data: AssessmentRequest): Promise<RiskAssessment> {
    const response = await this.client.post('/api/health/analyze/', data);
    return response.data;
  }

  /**
   * POST /api/assess/ - Anonymous health assessment
   */
  async assessAnonymous(data: AssessmentRequest): Promise<RiskAssessment> {
    const response = await this.client.post('/api/assess/', data);
    return response.data;
  }

  // ============================================================================
  // User Profile Endpoints
  // ============================================================================

  /**
   * GET /api/user/profile/ - Get user profile
   */
  async getUserProfile(): Promise<UserProfile> {
    const response = await this.client.get('/api/user/profile/');
    return response.data;
  }

  /**
   * PUT /api/user/profile/ - Update user profile
   */
  async updateUserProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    const response = await this.client.put('/api/user/profile/', data);
    return response.data;
  }

  /**
   * GET /api/user/statistics/ - Get user statistics
   */
  async getUserStatistics(): Promise<UserStatistics> {
    const response = await this.client.get('/api/user/statistics/');
    return response.data;
  }

  // ============================================================================
  // Assessment History Endpoints
  // ============================================================================

  /**
   * GET /api/user/assessments/ - Get assessment history
   */
  async getAssessmentHistory(
    page: number = 1,
    pageSize: number = 10
  ): Promise<AssessmentHistory> {
    const response = await this.client.get('/api/user/assessments/', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  }

  /**
   * GET /api/user/assessments/{id}/ - Get assessment detail
   */
  async getAssessmentDetail(id: string): Promise<RiskAssessment> {
    const response = await this.client.get(`/api/user/assessments/${id}/`);
    return response.data;
  }

  // ============================================================================
  // Prediction Endpoints
  // ============================================================================

  /**
   * POST /api/predict/top/ - Get top N predictions
   */
  async getTopPredictions(
    symptoms: string[],
    age: number,
    gender: string,
    n: number = 5
  ): Promise<Prediction[]> {
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
  async getSystemStatus(): Promise<SystemStatus> {
    const response = await this.client.get('/api/status/');
    return response.data;
  }

  /**
   * GET /api/health/ - Health check
   */
  async getHealthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await this.client.get('/api/health/');
    return response.data;
  }

  /**
   * GET /api/model/info/ - Get model information
   */
  async getModelInfo(): Promise<ModelInfo> {
    const response = await this.client.get('/api/model/info/');
    return response.data;
  }

  /**
   * GET /api/diseases/ - Get supported diseases
   */
  async getDiseases(): Promise<DiseasesResponse> {
    const response = await this.client.get('/api/diseases/');
    return response.data;
  }
}

export const apiService = new APIService();
