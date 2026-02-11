// ============================================================================
// System Store - Zustand
// ============================================================================

import { create } from 'zustand';
import { apiService } from '@/services/api';

let pollingInterval = null;

export const useSystemStore = create((set, get) => ({
  status: null,
  modelInfo: null,
  diseases: null,
  loading: false,
  error: null,

  // Fetch system status
  fetchSystemStatus: async () => {
    set({ loading: true, error: null });
    try {
      const status = await apiService.getSystemStatus();
      set({ status, loading: false, error: null });
    } catch (error) {
      set({ 
        loading: false, 
        error: error.response?.data?.message || 'Failed to fetch system status' 
      });
    }
  },

  // Fetch model info
  fetchModelInfo: async () => {
    set({ loading: true, error: null });
    try {
      const modelInfo = await apiService.getModelInfo();
      set({ modelInfo, loading: false, error: null });
    } catch (error) {
      set({ 
        loading: false, 
        error: error.response?.data?.message || 'Failed to fetch model info' 
      });
    }
  },

  // Fetch diseases
  fetchDiseases: async () => {
    set({ loading: true, error: null });
    try {
      const diseases = await apiService.getDiseases();
      set({ diseases, loading: false, error: null });
    } catch (error) {
      set({ 
        loading: false, 
        error: error.response?.data?.message || 'Failed to fetch diseases' 
      });
    }
  },

  // Start polling system status every 60 seconds
  startStatusPolling: () => {
    const { fetchSystemStatus } = get();
    
    // Initial fetch
    fetchSystemStatus();
    
    // Poll every 60 seconds
    if (!pollingInterval) {
      pollingInterval = setInterval(() => {
        fetchSystemStatus();
      }, 60000);
    }
  },

  // Stop polling
  stopStatusPolling: () => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      pollingInterval = null;
    }
  },

  // Clear error
  clearError: () => {
    set({ error: null });
  },
}));
