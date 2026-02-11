// ============================================================================
// System Store - Zustand
// ============================================================================

import { create } from 'zustand';
import { apiService } from '@/services/api';
import type { SystemStatus, ModelInfo, DiseasesResponse } from '@/types';

interface SystemState {
  status: SystemStatus | null;
  modelInfo: ModelInfo | null;
  diseases: DiseasesResponse | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchSystemStatus: () => Promise<void>;
  fetchModelInfo: () => Promise<void>;
  fetchDiseases: () => Promise<void>;
  startStatusPolling: () => void;
  stopStatusPolling: () => void;
  clearError: () => void;
}

let pollingInterval: NodeJS.Timeout | null = null;

export const useSystemStore = create<SystemState>((set, get) => ({
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
    } catch (error: any) {
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
    } catch (error: any) {
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
    } catch (error: any) {
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
