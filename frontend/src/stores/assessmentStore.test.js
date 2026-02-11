// ============================================================================
// Assessment Store Tests
// ============================================================================

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useAssessmentStore } from './assessmentStore';
import { apiService } from '@/services/api';

// Mock API service
vi.mock('@/services/api', () => ({
  apiService: {
    analyzeHealth: vi.fn(),
    assessAnonymous: vi.fn(),
    getAssessmentHistory: vi.fn(),
    getAssessmentDetail: vi.fn(),
  },
}));

describe('AssessmentStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useAssessmentStore.setState({
      currentAssessment: null,
      assessmentHistory: null,
      loading: false,
      error: null,
    });
    
    // Clear all mocks
    vi.clearAllMocks();
  });

  describe('submitAssessment', () => {
    const mockAssessmentData = {
      symptoms: [
        {
          name: 'fever',
          severity: 7,
          duration: { value: 3, unit: 'days' },
        },
      ],
      demographics: {
        age: 30,
        gender: 'male',
        medicalHistory: [],
      },
    };

    const mockAssessmentResult = {
      id: 'assessment-123',
      condition: 'Flu',
      riskLevel: 'medium',
      probability: 75,
      confidence: 'HIGH',
      confidenceScore: 85,
      interpretation: 'Based on your symptoms...',
      riskDrivers: [
        {
          factor: 'fever',
          contribution: 60,
          description: 'High fever is a key indicator',
        },
      ],
      dataQualityScore: 80,
      timestamp: '2024-01-15T00:00:00Z',
    };

    it('should successfully submit assessment for authenticated user', async () => {
      apiService.analyzeHealth.mockResolvedValue(mockAssessmentResult);

      const store = useAssessmentStore.getState();
      const result = await store.submitAssessment(mockAssessmentData, true);

      expect(result).toEqual(mockAssessmentResult);
      
      const state = useAssessmentStore.getState();
      expect(state.currentAssessment).toEqual(mockAssessmentResult);
      expect(state.loading).toBe(false);
      expect(state.error).toBe(null);
      expect(apiService.analyzeHealth).toHaveBeenCalledWith(mockAssessmentData);
    });

    it('should successfully submit assessment for anonymous user', async () => {
      apiService.assessAnonymous.mockResolvedValue(mockAssessmentResult);

      const store = useAssessmentStore.getState();
      const result = await store.submitAssessment(mockAssessmentData, false);

      expect(result).toEqual(mockAssessmentResult);
      
      const state = useAssessmentStore.getState();
      expect(state.currentAssessment).toEqual(mockAssessmentResult);
      expect(state.loading).toBe(false);
      expect(state.error).toBe(null);
      expect(apiService.assessAnonymous).toHaveBeenCalledWith(mockAssessmentData);
    });

    it('should handle assessment submission failure', async () => {
      const mockError = {
        response: {
          data: {
            message: 'Invalid symptoms',
          },
        },
      };

      apiService.analyzeHealth.mockRejectedValue(mockError);

      const store = useAssessmentStore.getState();
      
      await expect(store.submitAssessment(mockAssessmentData, true)).rejects.toThrow();

      const state = useAssessmentStore.getState();
      expect(state.loading).toBe(false);
      expect(state.error).toBe('Invalid symptoms');
      expect(state.currentAssessment).toBe(null);
    });

    it('should handle assessment submission failure with generic error', async () => {
      apiService.analyzeHealth.mockRejectedValue(new Error('Network error'));

      const store = useAssessmentStore.getState();
      
      await expect(store.submitAssessment(mockAssessmentData, true)).rejects.toThrow();

      const state = useAssessmentStore.getState();
      expect(state.error).toBe('Assessment failed');
    });
  });

  describe('fetchAssessmentHistory', () => {
    it('should successfully fetch assessment history', async () => {
      const mockHistory = {
        count: 2,
        next: null,
        previous: null,
        results: [
          {
            id: 'assessment-1',
            date: '2024-01-15T00:00:00Z',
            condition: 'Flu',
            riskLevel: 'medium',
            confidence: 'HIGH',
            probability: 75,
          },
          {
            id: 'assessment-2',
            date: '2024-01-10T00:00:00Z',
            condition: 'Cold',
            riskLevel: 'low',
            confidence: 'MEDIUM',
            probability: 45,
          },
        ],
      };

      apiService.getAssessmentHistory.mockResolvedValue(mockHistory);

      const store = useAssessmentStore.getState();
      await store.fetchAssessmentHistory(1, 10);

      const state = useAssessmentStore.getState();
      expect(state.assessmentHistory).toEqual(mockHistory);
      expect(state.loading).toBe(false);
      expect(state.error).toBe(null);
      expect(apiService.getAssessmentHistory).toHaveBeenCalledWith(1, 10);
    });

    it('should handle fetch history failure', async () => {
      const mockError = {
        response: {
          data: {
            message: 'History unavailable',
          },
        },
      };

      apiService.getAssessmentHistory.mockRejectedValue(mockError);

      const store = useAssessmentStore.getState();
      
      await expect(store.fetchAssessmentHistory()).rejects.toThrow();

      const state = useAssessmentStore.getState();
      expect(state.loading).toBe(false);
      expect(state.error).toBe('History unavailable');
    });
  });

  describe('fetchAssessmentDetail', () => {
    it('should successfully fetch assessment detail', async () => {
      const mockDetail = {
        id: 'assessment-123',
        condition: 'Flu',
        riskLevel: 'medium',
        probability: 75,
        confidence: 'HIGH',
        confidenceScore: 85,
        interpretation: 'Based on your symptoms...',
        riskDrivers: [],
        dataQualityScore: 80,
        timestamp: '2024-01-15T00:00:00Z',
      };

      apiService.getAssessmentDetail.mockResolvedValue(mockDetail);

      const store = useAssessmentStore.getState();
      await store.fetchAssessmentDetail('assessment-123');

      const state = useAssessmentStore.getState();
      expect(state.currentAssessment).toEqual(mockDetail);
      expect(state.loading).toBe(false);
      expect(state.error).toBe(null);
    });

    it('should handle fetch detail failure', async () => {
      const mockError = {
        response: {
          data: {
            message: 'Assessment not found',
          },
        },
      };

      apiService.getAssessmentDetail.mockRejectedValue(mockError);

      const store = useAssessmentStore.getState();
      
      await expect(store.fetchAssessmentDetail('invalid-id')).rejects.toThrow();

      const state = useAssessmentStore.getState();
      expect(state.loading).toBe(false);
      expect(state.error).toBe('Assessment not found');
    });
  });

  describe('clearCurrentAssessment', () => {
    it('should clear current assessment', () => {
      useAssessmentStore.setState({
        currentAssessment: {
          id: 'assessment-123',
          condition: 'Flu',
        },
      });

      const store = useAssessmentStore.getState();
      store.clearCurrentAssessment();

      const state = useAssessmentStore.getState();
      expect(state.currentAssessment).toBe(null);
    });
  });

  describe('clearError', () => {
    it('should clear error', () => {
      useAssessmentStore.setState({ error: 'Some error' });

      const store = useAssessmentStore.getState();
      store.clearError();

      const state = useAssessmentStore.getState();
      expect(state.error).toBe(null);
    });
  });
});
