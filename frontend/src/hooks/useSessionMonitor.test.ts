// ============================================================================
// Session Monitor Hook Unit Tests
// Tests for session expiration monitoring and warnings
// ============================================================================
// Requirements: 11.3

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useSessionMonitor } from './useSessionMonitor';
import { useAuthStore } from '@/stores/authStore';
import { useNotificationStore } from '@/stores/notificationStore';
import { auth } from '@/services/firebase';

// Mock stores
vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn(),
}));

vi.mock('@/stores/notificationStore', () => ({
  useNotificationStore: vi.fn(() => ({
    addNotification: vi.fn(),
  })),
}));

// Mock Firebase auth
vi.mock('@/services/firebase', () => ({
  auth: {
    currentUser: null,
  },
}));

describe('useSessionMonitor Hook', () => {
  const mockAddNotification = vi.fn();
  const mockRefreshToken = vi.fn();
  const mockGetIdTokenResult = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();

    // Setup default mocks
    vi.mocked(useNotificationStore).mockReturnValue({
      addNotification: mockAddNotification,
    } as any);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  /**
   * Test: Session expiration warning
   * Requirements: 11.3
   */
  describe('Session Expiration Warning', () => {
    it('should display notification 5 minutes before token expiration', async () => {
      const currentTime = Date.now();
      const expirationTime = currentTime + 4 * 60 * 1000; // 4 minutes from now

      // Mock authenticated user
      const mockUser = { uid: 'test-user', email: 'test@example.com' };
      vi.mocked(useAuthStore).mockReturnValue({
        user: mockUser,
        refreshToken: mockRefreshToken,
      } as any);

      // Mock Firebase current user
      (auth as any).currentUser = {
        getIdTokenResult: mockGetIdTokenResult,
      };

      mockGetIdTokenResult.mockResolvedValue({
        expirationTime: new Date(expirationTime).toISOString(),
      });

      renderHook(() => useSessionMonitor());

      // Wait for initial check
      await waitFor(() => {
        expect(mockGetIdTokenResult).toHaveBeenCalled();
      });

      // Should display warning notification
      await waitFor(() => {
        expect(mockAddNotification).toHaveBeenCalledWith({
          type: 'warning',
          message: expect.stringContaining('session will expire'),
          dismissible: true,
        });
      });
    });

    it('should display correct minutes remaining in notification', async () => {
      const currentTime = Date.now();
      const expirationTime = currentTime + 3 * 60 * 1000; // 3 minutes from now

      const mockUser = { uid: 'test-user', email: 'test@example.com' };
      vi.mocked(useAuthStore).mockReturnValue({
        user: mockUser,
        refreshToken: mockRefreshToken,
      } as any);

      (auth as any).currentUser = {
        getIdTokenResult: mockGetIdTokenResult,
      };

      mockGetIdTokenResult.mockResolvedValue({
        expirationTime: new Date(expirationTime).toISOString(),
      });

      renderHook(() => useSessionMonitor());

      await waitFor(() => {
        expect(mockAddNotification).toHaveBeenCalledWith({
          type: 'warning',
          message: expect.stringContaining('3 minute'),
          dismissible: true,
        });
      });
    });

    it('should not display warning when token expires in more than 5 minutes', async () => {
      const currentTime = Date.now();
      const expirationTime = currentTime + 10 * 60 * 1000; // 10 minutes from now

      const mockUser = { uid: 'test-user', email: 'test@example.com' };
      vi.mocked(useAuthStore).mockReturnValue({
        user: mockUser,
        refreshToken: mockRefreshToken,
      } as any);

      (auth as any).currentUser = {
        getIdTokenResult: mockGetIdTokenResult,
      };

      mockGetIdTokenResult.mockResolvedValue({
        expirationTime: new Date(expirationTime).toISOString(),
      });

      renderHook(() => useSessionMonitor());

      await waitFor(() => {
        expect(mockGetIdTokenResult).toHaveBeenCalled();
      });

      // Should not display warning
      expect(mockAddNotification).not.toHaveBeenCalled();
    });

    it('should not display warning when user is not authenticated', () => {
      vi.mocked(useAuthStore).mockReturnValue({
        user: null,
        refreshToken: mockRefreshToken,
      } as any);

      (auth as any).currentUser = null;

      renderHook(() => useSessionMonitor());

      // Should not check token or display warning
      expect(mockGetIdTokenResult).not.toHaveBeenCalled();
      expect(mockAddNotification).not.toHaveBeenCalled();
    });
  });

  /**
   * Test: Automatic session extension
   * Requirements: 11.3
   */
  describe('Session Extension', () => {
    it('should automatically refresh token after displaying warning', async () => {
      const currentTime = Date.now();
      const expirationTime = currentTime + 4 * 60 * 1000; // 4 minutes from now

      const mockUser = { uid: 'test-user', email: 'test@example.com' };
      mockRefreshToken.mockResolvedValue(undefined);

      vi.mocked(useAuthStore).mockReturnValue({
        user: mockUser,
        refreshToken: mockRefreshToken,
      } as any);

      (auth as any).currentUser = {
        getIdTokenResult: mockGetIdTokenResult,
      };

      mockGetIdTokenResult.mockResolvedValue({
        expirationTime: new Date(expirationTime).toISOString(),
      });

      renderHook(() => useSessionMonitor());

      // Wait for warning
      await waitFor(() => {
        expect(mockAddNotification).toHaveBeenCalledWith({
          type: 'warning',
          message: expect.stringContaining('session will expire'),
          dismissible: true,
        });
      });

      // Advance time for automatic refresh
      vi.advanceTimersByTime(1000);

      // Should refresh token
      await waitFor(() => {
        expect(mockRefreshToken).toHaveBeenCalled();
      });
    });

    it('should display success notification after successful token refresh', async () => {
      const currentTime = Date.now();
      const expirationTime = currentTime + 4 * 60 * 1000;

      const mockUser = { uid: 'test-user', email: 'test@example.com' };
      mockRefreshToken.mockResolvedValue(undefined);

      vi.mocked(useAuthStore).mockReturnValue({
        user: mockUser,
        refreshToken: mockRefreshToken,
      } as any);

      (auth as any).currentUser = {
        getIdTokenResult: mockGetIdTokenResult,
      };

      mockGetIdTokenResult.mockResolvedValue({
        expirationTime: new Date(expirationTime).toISOString(),
      });

      renderHook(() => useSessionMonitor());

      // Wait for warning
      await waitFor(() => {
        expect(mockAddNotification).toHaveBeenCalledWith({
          type: 'warning',
          message: expect.stringContaining('session will expire'),
          dismissible: true,
        });
      });

      // Advance time for automatic refresh
      vi.advanceTimersByTime(1000);

      // Should display success notification
      await waitFor(() => {
        expect(mockAddNotification).toHaveBeenCalledWith({
          type: 'success',
          message: 'Session extended successfully',
          dismissible: true,
        });
      });
    });

    it('should handle token refresh failure gracefully', async () => {
      const currentTime = Date.now();
      const expirationTime = currentTime + 4 * 60 * 1000;

      const mockUser = { uid: 'test-user', email: 'test@example.com' };
      const refreshError = new Error('Refresh failed');
      mockRefreshToken.mockRejectedValue(refreshError);

      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      vi.mocked(useAuthStore).mockReturnValue({
        user: mockUser,
        refreshToken: mockRefreshToken,
      } as any);

      (auth as any).currentUser = {
        getIdTokenResult: mockGetIdTokenResult,
      };

      mockGetIdTokenResult.mockResolvedValue({
        expirationTime: new Date(expirationTime).toISOString(),
      });

      renderHook(() => useSessionMonitor());

      // Wait for warning
      await waitFor(() => {
        expect(mockAddNotification).toHaveBeenCalledWith({
          type: 'warning',
          message: expect.stringContaining('session will expire'),
          dismissible: true,
        });
      });

      // Advance time for automatic refresh
      vi.advanceTimersByTime(1000);

      // Should log error
      await waitFor(() => {
        expect(consoleErrorSpy).toHaveBeenCalledWith('Failed to refresh token:', refreshError);
      });

      consoleErrorSpy.mockRestore();
    });
  });

  /**
   * Test: Periodic checking
   * Requirements: 11.3
   */
  describe('Periodic Token Checking', () => {
    it('should check token expiration every minute', async () => {
      const currentTime = Date.now();
      const expirationTime = currentTime + 10 * 60 * 1000; // 10 minutes from now

      const mockUser = { uid: 'test-user', email: 'test@example.com' };
      vi.mocked(useAuthStore).mockReturnValue({
        user: mockUser,
        refreshToken: mockRefreshToken,
      } as any);

      (auth as any).currentUser = {
        getIdTokenResult: mockGetIdTokenResult,
      };

      mockGetIdTokenResult.mockResolvedValue({
        expirationTime: new Date(expirationTime).toISOString(),
      });

      renderHook(() => useSessionMonitor());

      // Initial check
      await waitFor(() => {
        expect(mockGetIdTokenResult).toHaveBeenCalledTimes(1);
      });

      // Advance time by 1 minute
      vi.advanceTimersByTime(60 * 1000);

      await waitFor(() => {
        expect(mockGetIdTokenResult).toHaveBeenCalledTimes(2);
      });

      // Advance time by another minute
      vi.advanceTimersByTime(60 * 1000);

      await waitFor(() => {
        expect(mockGetIdTokenResult).toHaveBeenCalledTimes(3);
      });
    });

    it('should stop checking when component unmounts', async () => {
      const currentTime = Date.now();
      const expirationTime = currentTime + 10 * 60 * 1000;

      const mockUser = { uid: 'test-user', email: 'test@example.com' };
      vi.mocked(useAuthStore).mockReturnValue({
        user: mockUser,
        refreshToken: mockRefreshToken,
      } as any);

      (auth as any).currentUser = {
        getIdTokenResult: mockGetIdTokenResult,
      };

      mockGetIdTokenResult.mockResolvedValue({
        expirationTime: new Date(expirationTime).toISOString(),
      });

      const { unmount } = renderHook(() => useSessionMonitor());

      // Initial check
      await waitFor(() => {
        expect(mockGetIdTokenResult).toHaveBeenCalledTimes(1);
      });

      // Unmount
      unmount();

      // Advance time
      vi.advanceTimersByTime(60 * 1000);

      // Should not check again
      expect(mockGetIdTokenResult).toHaveBeenCalledTimes(1);
    });
  });

  /**
   * Test: Warning flag management
   * Requirements: 11.3
   */
  describe('Warning Flag Management', () => {
    it('should only show warning once until token is refreshed', async () => {
      const currentTime = Date.now();
      let expirationTime = currentTime + 4 * 60 * 1000; // 4 minutes from now

      const mockUser = { uid: 'test-user', email: 'test@example.com' };
      vi.mocked(useAuthStore).mockReturnValue({
        user: mockUser,
        refreshToken: mockRefreshToken,
      } as any);

      (auth as any).currentUser = {
        getIdTokenResult: mockGetIdTokenResult,
      };

      mockGetIdTokenResult.mockResolvedValue({
        expirationTime: new Date(expirationTime).toISOString(),
      });

      renderHook(() => useSessionMonitor());

      // Wait for first warning
      await waitFor(() => {
        expect(mockAddNotification).toHaveBeenCalledTimes(1);
      });

      // Advance time by 1 minute (still within 5 minute window)
      vi.advanceTimersByTime(60 * 1000);

      // Should not show warning again
      await waitFor(() => {
        expect(mockGetIdTokenResult).toHaveBeenCalledTimes(2);
      });

      expect(mockAddNotification).toHaveBeenCalledTimes(1);
    });

    it('should reset warning flag after token is refreshed', async () => {
      const currentTime = Date.now();
      const expirationTime = currentTime + 4 * 60 * 1000;

      const mockUser = { uid: 'test-user', email: 'test@example.com' };
      mockRefreshToken.mockResolvedValue(undefined);

      vi.mocked(useAuthStore).mockReturnValue({
        user: mockUser,
        refreshToken: mockRefreshToken,
      } as any);

      (auth as any).currentUser = {
        getIdTokenResult: mockGetIdTokenResult,
      };

      // First call: token expiring soon
      mockGetIdTokenResult.mockResolvedValueOnce({
        expirationTime: new Date(expirationTime).toISOString(),
      });

      // After refresh: token has more time
      mockGetIdTokenResult.mockResolvedValue({
        expirationTime: new Date(currentTime + 30 * 60 * 1000).toISOString(),
      });

      renderHook(() => useSessionMonitor());

      // Wait for warning and refresh
      await waitFor(() => {
        expect(mockRefreshToken).toHaveBeenCalled();
      });

      // Advance time for next check
      vi.advanceTimersByTime(60 * 1000);

      // Token should be checked again
      await waitFor(() => {
        expect(mockGetIdTokenResult).toHaveBeenCalledTimes(2);
      });
    });
  });

  /**
   * Test: Error handling
   * Requirements: 11.3
   */
  describe('Error Handling', () => {
    it('should handle errors when checking token expiration', async () => {
      const mockUser = { uid: 'test-user', email: 'test@example.com' };
      vi.mocked(useAuthStore).mockReturnValue({
        user: mockUser,
        refreshToken: mockRefreshToken,
      } as any);

      (auth as any).currentUser = {
        getIdTokenResult: mockGetIdTokenResult,
      };

      const tokenError = new Error('Token check failed');
      mockGetIdTokenResult.mockRejectedValue(tokenError);

      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      renderHook(() => useSessionMonitor());

      // Should log error
      await waitFor(() => {
        expect(consoleErrorSpy).toHaveBeenCalledWith('Error checking token expiration:', tokenError);
      });

      consoleErrorSpy.mockRestore();
    });

    it('should not crash when currentUser is null during check', async () => {
      const mockUser = { uid: 'test-user', email: 'test@example.com' };
      vi.mocked(useAuthStore).mockReturnValue({
        user: mockUser,
        refreshToken: mockRefreshToken,
      } as any);

      (auth as any).currentUser = null;

      // Should not throw error
      expect(() => {
        renderHook(() => useSessionMonitor());
      }).not.toThrow();
    });
  });
});
