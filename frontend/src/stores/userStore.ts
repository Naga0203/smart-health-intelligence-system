// ============================================================================
// User Store - Zustand
// ============================================================================

import { create } from 'zustand';
import { apiService } from '@/services/api';
import type { UserProfile, UserStatistics } from '@/types';

interface UserState {
  profile: UserProfile | null;
  statistics: UserStatistics | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchProfile: () => Promise<void>;
  updateProfile: (data: Partial<UserProfile>) => Promise<void>;
  fetchStatistics: () => Promise<void>;
  clearError: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  profile: null,
  statistics: null,
  loading: false,
  error: null,

  // Fetch user profile
  fetchProfile: async () => {
    set({ loading: true, error: null });
    try {
      const profile = await apiService.getUserProfile();
      set({ profile, loading: false, error: null });
    } catch (error: any) {
      set({ 
        loading: false, 
        error: error.response?.data?.message || 'Failed to fetch profile' 
      });
      throw error;
    }
  },

  // Update user profile
  updateProfile: async (data: Partial<UserProfile>) => {
    set({ loading: true, error: null });
    try {
      const profile = await apiService.updateUserProfile(data);
      set({ profile, loading: false, error: null });
    } catch (error: any) {
      set({ 
        loading: false, 
        error: error.response?.data?.message || 'Failed to update profile' 
      });
      throw error;
    }
  },

  // Fetch user statistics
  fetchStatistics: async () => {
    set({ loading: true, error: null });
    try {
      const statistics = await apiService.getUserStatistics();
      set({ statistics, loading: false, error: null });
    } catch (error: any) {
      set({ 
        loading: false, 
        error: error.response?.data?.message || 'Failed to fetch statistics' 
      });
      throw error;
    }
  },

  // Clear error
  clearError: () => {
    set({ error: null });
  },
}));
