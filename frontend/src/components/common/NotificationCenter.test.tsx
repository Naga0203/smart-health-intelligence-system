// ============================================================================
// Notification Center Unit Tests
// Tests for notification display, auto-dismiss, and critical error modal
// ============================================================================
// Requirements: 11.1, 11.2, 11.3, 11.6, 11.7

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NotificationCenter } from './NotificationCenter';
import { useNotificationStore } from '@/stores/notificationStore';

// Mock the notification store
vi.mock('@/stores/notificationStore', () => ({
  useNotificationStore: vi.fn(),
}));

describe('NotificationCenter Component', () => {
  const mockRemoveNotification = vi.fn();
  const mockAcknowledgeCriticalError = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  /**
   * Test: Notification display
   * Requirements: 11.5, 11.6
   */
  describe('Notification Display', () => {
    it('should display notifications in the notification area', () => {
      const mockNotifications = [
        {
          id: '1',
          type: 'info' as const,
          message: 'Information message',
          dismissible: true,
          timestamp: '2024-01-15T10:00:00Z',
        },
        {
          id: '2',
          type: 'success' as const,
          message: 'Success message',
          dismissible: true,
          timestamp: '2024-01-15T10:01:00Z',
        },
      ];

      vi.mocked(useNotificationStore).mockReturnValue({
        notifications: mockNotifications,
        removeNotification: mockRemoveNotification,
        criticalError: null,
        acknowledgeCriticalError: mockAcknowledgeCriticalError,
      } as any);

      render(<NotificationCenter />);

      // Should display both notifications
      expect(screen.getByText('Information message')).toBeInTheDocument();
      expect(screen.getByText('Success message')).toBeInTheDocument();
    });

    it('should display notifications with correct severity types', () => {
      const mockNotifications = [
        {
          id: '1',
          type: 'info' as const,
          message: 'Info notification',
          dismissible: true,
          timestamp: '2024-01-15T10:00:00Z',
        },
        {
          id: '2',
          type: 'warning' as const,
          message: 'Warning notification',
          dismissible: true,
          timestamp: '2024-01-15T10:01:00Z',
        },
        {
          id: '3',
          type: 'error' as const,
          message: 'Error notification',
          dismissible: true,
          timestamp: '2024-01-15T10:02:00Z',
        },
        {
          id: '4',
          type: 'success' as const,
          message: 'Success notification',
          dismissible: true,
          timestamp: '2024-01-15T10:03:00Z',
        },
      ];

      vi.mocked(useNotificationStore).mockReturnValue({
        notifications: mockNotifications,
        removeNotification: mockRemoveNotification,
        criticalError: null,
        acknowledgeCriticalError: mockAcknowledgeCriticalError,
      } as any);

      render(<NotificationCenter />);

      // All notifications should be displayed
      expect(screen.getByText('Info notification')).toBeInTheDocument();
      expect(screen.getByText('Warning notification')).toBeInTheDocument();
      expect(screen.getByText('Error notification')).toBeInTheDocument();
      expect(screen.getByText('Success notification')).toBeInTheDocument();
    });

    it('should display notifications in top-right corner', () => {
      const mockNotifications = [
        {
          id: '1',
          type: 'info' as const,
          message: 'Test notification',
          dismissible: true,
          timestamp: '2024-01-15T10:00:00Z',
        },
      ];

      vi.mocked(useNotificationStore).mockReturnValue({
        notifications: mockNotifications,
        removeNotification: mockRemoveNotification,
        criticalError: null,
        acknowledgeCriticalError: mockAcknowledgeCriticalError,
      } as any);

      const { container } = render(<NotificationCenter />);

      // Find the notification container
      const notificationRegion = screen.getByRole('region', { name: 'Notifications' });
      expect(notificationRegion).toBeInTheDocument();

      // Check positioning styles
      const styles = window.getComputedStyle(notificationRegion);
      expect(notificationRegion).toHaveStyle({ position: 'fixed' });
    });

    it('should display empty notification center when no notifications', () => {
      vi.mocked(useNotificationStore).mockReturnValue({
        notifications: [],
        removeNotification: mockRemoveNotification,
        criticalError: null,
        acknowledgeCriticalError: mockAcknowledgeCriticalError,
      } as any);

      const { container } = render(<NotificationCenter />);

      // Notification region should exist but be empty
      const notificationRegion = screen.getByRole('region', { name: 'Notifications' });
      expect(notificationRegion).toBeInTheDocument();
      expect(notificationRegion.children).toHaveLength(0);
    });
  });

  /**
   * Test: Notification dismissal
   * Requirements: 11.6
   */
  describe('Notification Dismissal', () => {
    it('should call removeNotification when dismiss button is clicked', async () => {
      // Don't use fake timers for this test
      vi.useRealTimers();
      
      const user = userEvent.setup();
      const mockNotifications = [
        {
          id: 'test-1',
          type: 'info' as const,
          message: 'Dismissible notification',
          dismissible: true,
          timestamp: '2024-01-15T10:00:00Z',
        },
      ];

      vi.mocked(useNotificationStore).mockReturnValue({
        notifications: mockNotifications,
        removeNotification: mockRemoveNotification,
        criticalError: null,
        acknowledgeCriticalError: mockAcknowledgeCriticalError,
      } as any);

      render(<NotificationCenter />);

      // Find and click the close button
      const closeButton = screen.getByRole('button', { name: /close notification/i });
      await user.click(closeButton);

      // Should call removeNotification with correct ID
      expect(mockRemoveNotification).toHaveBeenCalledWith('test-1');
      
      vi.useFakeTimers();
    });

    it('should display dismiss button for all notifications', () => {
      const mockNotifications = [
        {
          id: '1',
          type: 'info' as const,
          message: 'First notification',
          dismissible: true,
          timestamp: '2024-01-15T10:00:00Z',
        },
        {
          id: '2',
          type: 'warning' as const,
          message: 'Second notification',
          dismissible: true,
          timestamp: '2024-01-15T10:01:00Z',
        },
      ];

      vi.mocked(useNotificationStore).mockReturnValue({
        notifications: mockNotifications,
        removeNotification: mockRemoveNotification,
        criticalError: null,
        acknowledgeCriticalError: mockAcknowledgeCriticalError,
      } as any);

      render(<NotificationCenter />);

      // Should have two close buttons
      const closeButtons = screen.getAllByRole('button', { name: /close notification/i });
      expect(closeButtons).toHaveLength(2);
    });
  });

  /**
   * Test: Critical error modal
   * Requirements: 11.7
   */
  describe('Critical Error Modal', () => {
    it('should display critical error modal when criticalError is set', () => {
      const mockCriticalError = {
        title: 'Critical System Error',
        message: 'A critical error has occurred',
        details: 'Error details here',
      };

      vi.mocked(useNotificationStore).mockReturnValue({
        notifications: [],
        removeNotification: mockRemoveNotification,
        criticalError: mockCriticalError,
        acknowledgeCriticalError: mockAcknowledgeCriticalError,
      } as any);

      render(<NotificationCenter />);

      // Should display modal with title
      expect(screen.getByText('Critical System Error')).toBeInTheDocument();

      // Should display message
      expect(screen.getByText('A critical error has occurred')).toBeInTheDocument();

      // Should display details
      expect(screen.getByText('Error details here')).toBeInTheDocument();
    });

    it('should call acknowledgeCriticalError when acknowledge button is clicked', async () => {
      // Don't use fake timers for this test
      vi.useRealTimers();
      
      const user = userEvent.setup();
      const mockCriticalError = {
        title: 'Critical Error',
        message: 'Error message',
      };

      vi.mocked(useNotificationStore).mockReturnValue({
        notifications: [],
        removeNotification: mockRemoveNotification,
        criticalError: mockCriticalError,
        acknowledgeCriticalError: mockAcknowledgeCriticalError,
      } as any);

      render(<NotificationCenter />);

      // Find and click the acknowledge button
      const acknowledgeButton = screen.getByRole('button', { name: /I Understand/i });
      await user.click(acknowledgeButton);

      // Should call acknowledgeCriticalError
      expect(mockAcknowledgeCriticalError).toHaveBeenCalled();
      
      vi.useFakeTimers();
    });

    it('should not display critical error modal when criticalError is null', () => {
      vi.mocked(useNotificationStore).mockReturnValue({
        notifications: [],
        removeNotification: mockRemoveNotification,
        criticalError: null,
        acknowledgeCriticalError: mockAcknowledgeCriticalError,
      } as any);

      render(<NotificationCenter />);

      // Should not display modal
      expect(screen.queryByText(/Critical/i)).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /I Understand/i })).not.toBeInTheDocument();
    });

    it('should display critical error modal without details when details is undefined', () => {
      const mockCriticalError = {
        title: 'Critical Error',
        message: 'Error message',
      };

      vi.mocked(useNotificationStore).mockReturnValue({
        notifications: [],
        removeNotification: mockRemoveNotification,
        criticalError: mockCriticalError,
        acknowledgeCriticalError: mockAcknowledgeCriticalError,
      } as any);

      render(<NotificationCenter />);

      // Should display modal with title and message
      expect(screen.getByText('Critical Error')).toBeInTheDocument();
      expect(screen.getByText('Error message')).toBeInTheDocument();
    });
  });

  /**
   * Test: Multiple notifications display
   * Requirements: 11.5, 11.6
   */
  describe('Multiple Notifications', () => {
    it('should display multiple notifications simultaneously', () => {
      const mockNotifications = [
        {
          id: '1',
          type: 'info' as const,
          message: 'First notification',
          dismissible: true,
          timestamp: '2024-01-15T10:00:00Z',
        },
        {
          id: '2',
          type: 'warning' as const,
          message: 'Second notification',
          dismissible: true,
          timestamp: '2024-01-15T10:01:00Z',
        },
        {
          id: '3',
          type: 'success' as const,
          message: 'Third notification',
          dismissible: true,
          timestamp: '2024-01-15T10:02:00Z',
        },
      ];

      vi.mocked(useNotificationStore).mockReturnValue({
        notifications: mockNotifications,
        removeNotification: mockRemoveNotification,
        criticalError: null,
        acknowledgeCriticalError: mockAcknowledgeCriticalError,
      } as any);

      render(<NotificationCenter />);

      // All three notifications should be visible
      expect(screen.getByText('First notification')).toBeInTheDocument();
      expect(screen.getByText('Second notification')).toBeInTheDocument();
      expect(screen.getByText('Third notification')).toBeInTheDocument();
    });

    it('should display notifications and critical error modal simultaneously', () => {
      const mockNotifications = [
        {
          id: '1',
          type: 'info' as const,
          message: 'Regular notification',
          dismissible: true,
          timestamp: '2024-01-15T10:00:00Z',
        },
      ];

      const mockCriticalError = {
        title: 'Critical Error',
        message: 'Critical error message',
      };

      vi.mocked(useNotificationStore).mockReturnValue({
        notifications: mockNotifications,
        removeNotification: mockRemoveNotification,
        criticalError: mockCriticalError,
        acknowledgeCriticalError: mockAcknowledgeCriticalError,
      } as any);

      render(<NotificationCenter />);

      // Both notification and modal should be visible
      expect(screen.getByText('Regular notification')).toBeInTheDocument();
      expect(screen.getByText('Critical Error')).toBeInTheDocument();
      expect(screen.getByText('Critical error message')).toBeInTheDocument();
    });
  });
});
