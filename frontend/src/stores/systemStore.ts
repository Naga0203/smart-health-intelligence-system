// ============================================================================
// System Store - Zustand
// ============================================================================

import { create } from 'zustand';
import { apiService } from '@/services/api';
import { useNotificationStore } from './notificationStore';

let pollingInterval = null;

export const useSystemStore = create((set, get) => ({
  status: null,
  modelInfo: null,
  diseases: null,
  loading: false,
  error: null,

  // Fetch system status
  fetchSystemStatus: async () => {
    const previousStatus = get().status;
    set({ loading: true, error: null });
    try {
      const status = await apiService.getSystemStatus();

      // Check for status changes and notify
      if (previousStatus && previousStatus.status !== status.status) {
        const notificationStore = useNotificationStore.getState();

        if (status.status === 'degraded') {
          notificationStore.addNotification({
            type: 'warning',
            message: 'System status changed to degraded. Some services may be limited.',
            dismissible: true,
          });
        } else if (status.status === 'error') {
          notificationStore.addNotification({
            type: 'error',
            message: 'System is currently unavailable. Please try again later.',
            dismissible: true,
          });
        } else if (status.status === 'operational' && previousStatus.status !== 'operational') {
          notificationStore.addNotification({
            type: 'success',
            message: 'System is now operational.',
            dismissible: true,
          });
        }
      }

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
      const response = await apiService.getDiseases();
      // API returns { total: N, diseases: [...] }
      set({ diseases: response.diseases || [], loading: false, error: null });
    } catch (error) {
      set({
        loading: false,
        error: error.response?.data?.message || 'Failed to fetch diseases'
      });
    }
  },

  // Start polling system status every 60 seconds
  startStatusPolling: () => {
    const { fetchSystemStatus, fetchModelInfo } = get();

    // Initial fetch
    fetchSystemStatus();
    fetchModelInfo();

    // Poll every 60 seconds
    if (!pollingInterval) {
      pollingInterval = setInterval(() => {
        fetchSystemStatus();
        fetchModelInfo();
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
