// ============================================================================
// System Store Unit Tests
// Tests for system monitoring functionality
// ============================================================================

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useSystemStore } from './systemStore';
import { useNotificationStore } from './notificationStore';
import { apiService } from '@/services/api';

// Mock API service
vi.mock('@/services/api', () => ({
  apiService: {
    getSystemStatus: vi.fn(),
    getModelInfo: vi.fn(),
    getDiseases: vi.fn(),
  },
}));

// Mock notification store
vi.mock('./notificationStore', () => ({
  useNotificationStore: {
    getState: vi.fn(() => ({
      addNotification: vi.fn(),
    })),
  },
}));

describe('System Store', () => {
  beforeEach(() => {
    // Reset store state before each test
    useSystemStore.setState({
      status: null,
      modelInfo: null,
      diseases: null,
      loading: false,
      error: null,
    });

    // Clear all mocks
    vi.clearAllMocks();
  });

  afterEach(() => {
    // Stop any polling intervals
    useSystemStore.getState().stopStatusPolling();
  });

  /**
   * Test: Status polling functionality
   * Requirements: 10.1
   */
  describe('Status Polling', () => {
    it('should fetch system status and model info on startStatusPolling', async () => {
      const mockStatus = {
        status: 'operational',
        version: '1.0.0',
        timestamp: '2024-01-15T10:00:00Z',
      };
      const mockModelInfo = {
        model_type: 'RandomForest',
        num_diseases: 42,
        model_loaded: true,
      };

      vi.mocked(apiService.getSystemStatus).mockResolvedValue(mockStatus);
      vi.mocked(apiService.getModelInfo).mockResolvedValue(mockModelInfo);

      const { startStatusPolling } = useSystemStore.getState();
      startStatusPolling();

      // Wait for async operations
      await vi.waitFor(() => {
        expect(apiService.getSystemStatus).toHaveBeenCalled();
        expect(apiService.getModelInfo).toHaveBeenCalled();
      });

      const state = useSystemStore.getState();
      expect(state.status).toEqual(mockStatus);
      expect(state.modelInfo).toEqual(mockModelInfo);
    });

    it('should poll system status every 60 seconds', async () => {
      vi.useFakeTimers();

      const mockStatus = {
        status: 'operational',
        version: '1.0.0',
        timestamp: '2024-01-15T10:00:00Z',
      };

      vi.mocked(apiService.getSystemStatus).mockResolvedValue(mockStatus);
      vi.mocked(apiService.getModelInfo).mockResolvedValue({});

      const { startStatusPolling } = useSystemStore.getState();
      startStatusPolling();

      // Initial fetch
      await vi.waitFor(() => {
        expect(apiService.getSystemStatus).toHaveBeenCalledTimes(1);
      });

      // Advance time by 60 seconds
      vi.advanceTimersByTime(60000);

      await vi.waitFor(() => {
        expect(apiService.getSystemStatus).toHaveBeenCalledTimes(2);
      });

      // Advance time by another 60 seconds
      vi.advanceTimersByTime(60000);

      await vi.waitFor(() => {
        expect(apiService.getSystemStatus).toHaveBeenCalledTimes(3);
      });

      vi.useRealTimers();
    });

    it('should stop polling when stopStatusPolling is called', async () => {
      vi.useFakeTimers();

      const mockStatus = {
        status: 'operational',
        version: '1.0.0',
        timestamp: '2024-01-15T10:00:00Z',
      };

      vi.mocked(apiService.getSystemStatus).mockResolvedValue(mockStatus);
      vi.mocked(apiService.getModelInfo).mockResolvedValue({});

      const { startStatusPolling, stopStatusPolling } = useSystemStore.getState();
      startStatusPolling();

      // Initial fetch
      await vi.waitFor(() => {
        expect(apiService.getSystemStatus).toHaveBeenCalledTimes(1);
      });

      // Stop polling
      stopStatusPolling();

      // Advance time by 60 seconds
      vi.advanceTimersByTime(60000);

      // Should not fetch again
      expect(apiService.getSystemStatus).toHaveBeenCalledTimes(1);

      vi.useRealTimers();
    });
  });

  /**
   * Test: Notification on status change
   * Requirements: 11.4
   */
  describe('Status Change Notifications', () => {
    it('should notify when status changes to degraded', async () => {
      const mockAddNotification = vi.fn();
      vi.mocked(useNotificationStore.getState).mockReturnValue({
        addNotification: mockAddNotification,
      } as any);

      // Set initial operational status
      useSystemStore.setState({
        status: {
          status: 'operational',
          version: '1.0.0',
          timestamp: '2024-01-15T10:00:00Z',
        },
      });

      // Fetch new degraded status
      const degradedStatus = {
        status: 'degraded',
        version: '1.0.0',
        timestamp: '2024-01-15T10:05:00Z',
      };

      vi.mocked(apiService.getSystemStatus).mockResolvedValue(degradedStatus);

      const { fetchSystemStatus } = useSystemStore.getState();
      await fetchSystemStatus();

      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'warning',
        message: 'System status changed to degraded. Some services may be limited.',
        dismissible: true,
      });
    });

    it('should notify when status changes to error', async () => {
      const mockAddNotification = vi.fn();
      vi.mocked(useNotificationStore.getState).mockReturnValue({
        addNotification: mockAddNotification,
      } as any);

      // Set initial operational status
      useSystemStore.setState({
        status: {
          status: 'operational',
          version: '1.0.0',
          timestamp: '2024-01-15T10:00:00Z',
        },
      });

      // Fetch new error status
      const errorStatus = {
        status: 'error',
        version: '1.0.0',
        timestamp: '2024-01-15T10:05:00Z',
      };

      vi.mocked(apiService.getSystemStatus).mockResolvedValue(errorStatus);

      const { fetchSystemStatus } = useSystemStore.getState();
      await fetchSystemStatus();

      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'error',
        message: 'System is currently unavailable. Please try again later.',
        dismissible: true,
      });
    });

    it('should notify when status changes from error to operational', async () => {
      const mockAddNotification = vi.fn();
      vi.mocked(useNotificationStore.getState).mockReturnValue({
        addNotification: mockAddNotification,
      } as any);

      // Set initial error status
      useSystemStore.setState({
        status: {
          status: 'error',
          version: '1.0.0',
          timestamp: '2024-01-15T10:00:00Z',
        },
      });

      // Fetch new operational status
      const operationalStatus = {
        status: 'operational',
        version: '1.0.0',
        timestamp: '2024-01-15T10:05:00Z',
      };

      vi.mocked(apiService.getSystemStatus).mockResolvedValue(operationalStatus);

      const { fetchSystemStatus } = useSystemStore.getState();
      await fetchSystemStatus();

      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'success',
        message: 'System is now operational.',
        dismissible: true,
      });
    });

    it('should not notify when status remains the same', async () => {
      const mockAddNotification = vi.fn();
      vi.mocked(useNotificationStore.getState).mockReturnValue({
        addNotification: mockAddNotification,
      } as any);

      // Set initial operational status
      useSystemStore.setState({
        status: {
          status: 'operational',
          version: '1.0.0',
          timestamp: '2024-01-15T10:00:00Z',
        },
      });

      // Fetch same operational status
      const sameStatus = {
        status: 'operational',
        version: '1.0.0',
        timestamp: '2024-01-15T10:05:00Z',
      };

      vi.mocked(apiService.getSystemStatus).mockResolvedValue(sameStatus);

      const { fetchSystemStatus } = useSystemStore.getState();
      await fetchSystemStatus();

      expect(mockAddNotification).not.toHaveBeenCalled();
    });
  });

  /**
   * Test: Error handling
   * Requirements: 10.1
   */
  describe('Error Handling', () => {
    it('should handle fetchSystemStatus errors', async () => {
      const errorMessage = 'Network error';
      vi.mocked(apiService.getSystemStatus).mockRejectedValue({
        response: { data: { message: errorMessage } },
      });

      const { fetchSystemStatus } = useSystemStore.getState();
      await fetchSystemStatus();

      const state = useSystemStore.getState();
      expect(state.error).toBe(errorMessage);
      expect(state.loading).toBe(false);
    });

    it('should handle fetchModelInfo errors', async () => {
      const errorMessage = 'Model info unavailable';
      vi.mocked(apiService.getModelInfo).mockRejectedValue({
        response: { data: { message: errorMessage } },
      });

      const { fetchModelInfo } = useSystemStore.getState();
      await fetchModelInfo();

      const state = useSystemStore.getState();
      expect(state.error).toBe(errorMessage);
      expect(state.loading).toBe(false);
    });

    it('should use default error message when response has no message', async () => {
      vi.mocked(apiService.getSystemStatus).mockRejectedValue({
        response: {},
      });

      const { fetchSystemStatus } = useSystemStore.getState();
      await fetchSystemStatus();

      const state = useSystemStore.getState();
      expect(state.error).toBe('Failed to fetch system status');
    });
  });

  /**
   * Test: Fetch diseases
   * Requirements: 15.3
   */
  describe('Fetch Diseases', () => {
    it('should fetch and store diseases list', async () => {
      const mockDiseases = [
        { id: 1, name: 'Diabetes', category: 'Metabolic' },
        { id: 2, name: 'Hypertension', category: 'Cardiovascular' },
      ];

      vi.mocked(apiService.getDiseases).mockResolvedValue(mockDiseases);

      const { fetchDiseases } = useSystemStore.getState();
      await fetchDiseases();

      const state = useSystemStore.getState();
      expect(state.diseases).toEqual(mockDiseases);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
    });

    it('should handle fetchDiseases errors', async () => {
      const errorMessage = 'Failed to load diseases';
      vi.mocked(apiService.getDiseases).mockRejectedValue({
        response: { data: { message: errorMessage } },
      });

      const { fetchDiseases } = useSystemStore.getState();
      await fetchDiseases();

      const state = useSystemStore.getState();
      expect(state.error).toBe(errorMessage);
      expect(state.loading).toBe(false);
    });
  });

  /**
   * Test: Clear error
   * Requirements: 10.1
   */
  describe('Clear Error', () => {
    it('should clear error state', () => {
      useSystemStore.setState({ error: 'Some error' });

      const { clearError } = useSystemStore.getState();
      clearError();

      const state = useSystemStore.getState();
      expect(state.error).toBeNull();
    });
  });
});
