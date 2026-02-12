// ============================================================================
// Assessment Store - Zustand
// ============================================================================

import { create } from 'zustand';
import { apiService } from '@/services/api';

export const useAssessmentStore = create((set) => ({
  currentAssessment: null,
  assessmentHistory: null,
  loading: false,
  error: null,

  // Submit assessment
  submitAssessment: async (data, isAuthenticated) => {
    set({ loading: true, error: null });
    try {
      const assessment = isAuthenticated 
        ? await apiService.analyzeHealth(data)
        : await apiService.assessAnonymous(data);
      
      set({ currentAssessment: assessment, loading: false, error: null });
      return assessment;
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Assessment failed';
      set({ loading: false, error: errorMessage });
      throw error;
    }
  },

  // Fetch assessment history
  fetchAssessmentHistory: async (page = 1, pageSize = 10) => {
    set({ loading: true, error: null });
    try {
      const history = await apiService.getAssessmentHistory(page, pageSize);
      set({ assessmentHistory: history, loading: false, error: null });
    } catch (error) {
      set({ 
        loading: false, 
        error: error.response?.data?.message || 'Failed to fetch history' 
      });
      throw error;
    }
  },

  // Fetch assessment detail
  fetchAssessmentDetail: async (id) => {
    set({ loading: true, error: null });
    try {
      const assessment = await apiService.getAssessmentDetail(id);
      set({ currentAssessment: assessment, loading: false, error: null });
    } catch (error) {
      set({ 
        loading: false, 
        error: error.response?.data?.message || 'Failed to fetch assessment' 
      });
      throw error;
    }
  },

  // Clear current assessment
  clearCurrentAssessment: () => {
    set({ currentAssessment: null });
  },

  // Clear error
  clearError: () => {
    set({ error: null });
  },
}));
