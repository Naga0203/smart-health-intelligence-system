// ============================================================================
// User Store Tests
// ============================================================================

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useUserStore } from './userStore';
import { apiService } from '@/services/api';

// Mock API service
vi.mock('@/services/api', () => ({
  apiService: {
    getUserProfile: vi.fn(),
    updateUserProfile: vi.fn(),
    getUserStatistics: vi.fn(),
  },
}));

describe('UserStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useUserStore.setState({
      profile: null,
      statistics: null,
      loading: false,
      error: null,
    });
    
    // Clear all mocks
    vi.clearAllMocks();
  });

  describe('fetchProfile', () => {
    it('should successfully fetch user profile', async () => {
      const mockProfile = {
        email: 'test@example.com',
        name: 'Test User',
        age: 30,
        gender: 'male',
        medicalHistory: ['diabetes'],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      };

      apiService.getUserProfile.mockResolvedValue(mockProfile);

      const store = useUserStore.getState();
      await store.fetchProfile();

      const state = useUserStore.getState();
      expect(state.profile).toEqual(mockProfile);
      expect(state.loading).toBe(false);
      expect(state.error).toBe(null);
    });

    it('should handle fetch profile failure', async () => {
      const mockError = {
        response: {
          data: {
            message: 'Profile not found',
          },
        },
      };

      apiService.getUserProfile.mockRejectedValue(mockError);

      const store = useUserStore.getState();
      
      await expect(store.fetchProfile()).rejects.toThrow();

      const state = useUserStore.getState();
      expect(state.loading).toBe(false);
      expect(state.error).toBe('Profile not found');
      expect(state.profile).toBe(null);
    });

    it('should handle fetch profile failure with generic error', async () => {
      apiService.getUserProfile.mockRejectedValue(new Error('Network error'));

      const store = useUserStore.getState();
      
      await expect(store.fetchProfile()).rejects.toThrow();

      const state = useUserStore.getState();
      expect(state.loading).toBe(false);
      expect(state.error).toBe('Failed to fetch profile');
    });
  });

  describe('updateProfile', () => {
    it('should successfully update user profile', async () => {
      const updateData = {
        name: 'Updated Name',
        age: 31,
      };

      const mockUpdatedProfile = {
        email: 'test@example.com',
        name: 'Updated Name',
        age: 31,
        gender: 'male',
        medicalHistory: ['diabetes'],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-02T00:00:00Z',
      };

      apiService.updateUserProfile.mockResolvedValue(mockUpdatedProfile);

      const store = useUserStore.getState();
      await store.updateProfile(updateData);

      const state = useUserStore.getState();
      expect(state.profile).toEqual(mockUpdatedProfile);
      expect(state.loading).toBe(false);
      expect(state.error).toBe(null);
    });

    it('should handle update profile failure', async () => {
      const mockError = {
        response: {
          data: {
            message: 'Validation error',
          },
        },
      };

      apiService.updateUserProfile.mockRejectedValue(mockError);

      const store = useUserStore.getState();
      
      await expect(store.updateProfile({ name: '' })).rejects.toThrow();

      const state = useUserStore.getState();
      expect(state.loading).toBe(false);
      expect(state.error).toBe('Validation error');
    });
  });

  describe('fetchStatistics', () => {
    it('should successfully fetch user statistics', async () => {
      const mockStatistics = {
        totalAssessments: 10,
        lastAssessmentDate: '2024-01-15T00:00:00Z',
        averageRiskLevel: 'medium',
        mostCommonCondition: 'Flu',
      };

      apiService.getUserStatistics.mockResolvedValue(mockStatistics);

      const store = useUserStore.getState();
      await store.fetchStatistics();

      const state = useUserStore.getState();
      expect(state.statistics).toEqual(mockStatistics);
      expect(state.loading).toBe(false);
      expect(state.error).toBe(null);
    });

    it('should handle fetch statistics failure', async () => {
      const mockError = {
        response: {
          data: {
            message: 'Statistics unavailable',
          },
        },
      };

      apiService.getUserStatistics.mockRejectedValue(mockError);

      const store = useUserStore.getState();
      
      await expect(store.fetchStatistics()).rejects.toThrow();

      const state = useUserStore.getState();
      expect(state.loading).toBe(false);
      expect(state.error).toBe('Statistics unavailable');
    });
  });

  describe('clearError', () => {
    it('should clear error', () => {
      useUserStore.setState({ error: 'Some error' });

      const store = useUserStore.getState();
      store.clearError();

      const state = useUserStore.getState();
      expect(state.error).toBe(null);
    });
  });
});
