// ============================================================================
// Notification Store Unit Tests
// Tests for notification management and auto-dismiss functionality
// ============================================================================
// Requirements: 11.5, 11.6, 11.7

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useNotificationStore } from './notificationStore';

describe('Notification Store', () => {
  beforeEach(() => {
    // Reset store state before each test
    useNotificationStore.setState({
      notifications: [],
      criticalError: null,
    });

    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  /**
   * Test: Add notification
   * Requirements: 11.5, 11.6
   */
  describe('Add Notification', () => {
    it('should add notification to store', () => {
      const { addNotification } = useNotificationStore.getState();

      addNotification({
        type: 'info',
        message: 'Test notification',
        dismissible: true,
      });

      const state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);
      expect(state.notifications[0].message).toBe('Test notification');
      expect(state.notifications[0].type).toBe('info');
    });

    it('should generate unique ID for each notification', () => {
      const { addNotification } = useNotificationStore.getState();

      addNotification({
        type: 'info',
        message: 'First notification',
        dismissible: true,
      });

      addNotification({
        type: 'info',
        message: 'Second notification',
        dismissible: true,
      });

      const state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(2);
      expect(state.notifications[0].id).not.toBe(state.notifications[1].id);
    });

    it('should add timestamp to notification', () => {
      const { addNotification } = useNotificationStore.getState();

      addNotification({
        type: 'info',
        message: 'Test notification',
        dismissible: true,
      });

      const state = useNotificationStore.getState();
      expect(state.notifications[0].timestamp).toBeDefined();
      expect(new Date(state.notifications[0].timestamp).getTime()).not.toBeNaN();
    });

    it('should add multiple notifications', () => {
      const { addNotification } = useNotificationStore.getState();

      addNotification({
        type: 'info',
        message: 'First',
        dismissible: true,
      });

      addNotification({
        type: 'warning',
        message: 'Second',
        dismissible: true,
      });

      addNotification({
        type: 'error',
        message: 'Third',
        dismissible: true,
      });

      const state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(3);
    });
  });

  /**
   * Test: Auto-dismiss functionality
   * Requirements: 11.6
   */
  describe('Auto-Dismiss', () => {
    it('should auto-dismiss non-critical notifications after 5 seconds', () => {
      const { addNotification } = useNotificationStore.getState();

      addNotification({
        type: 'info',
        message: 'Auto-dismiss notification',
        dismissible: true,
      });

      // Notification should exist initially
      let state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);

      // Advance time by 5 seconds
      vi.advanceTimersByTime(5000);

      // Notification should be removed
      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(0);
    });

    it('should auto-dismiss success notifications', () => {
      const { addNotification } = useNotificationStore.getState();

      addNotification({
        type: 'success',
        message: 'Success notification',
        dismissible: true,
      });

      let state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);

      vi.advanceTimersByTime(5000);

      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(0);
    });

    it('should auto-dismiss warning notifications', () => {
      const { addNotification } = useNotificationStore.getState();

      addNotification({
        type: 'warning',
        message: 'Warning notification',
        dismissible: true,
      });

      let state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);

      vi.advanceTimersByTime(5000);

      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(0);
    });

    it('should NOT auto-dismiss error notifications', () => {
      const { addNotification } = useNotificationStore.getState();

      addNotification({
        type: 'error',
        message: 'Error notification',
        dismissible: true,
      });

      let state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);

      vi.advanceTimersByTime(5000);

      // Error notification should still be present
      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);
      expect(state.notifications[0].message).toBe('Error notification');
    });

    it('should NOT auto-dismiss non-dismissible notifications', () => {
      const { addNotification } = useNotificationStore.getState();

      addNotification({
        type: 'info',
        message: 'Non-dismissible notification',
        dismissible: false,
      });

      let state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);

      vi.advanceTimersByTime(5000);

      // Non-dismissible notification should still be present
      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);
    });

    it('should auto-dismiss multiple notifications independently', () => {
      const { addNotification } = useNotificationStore.getState();

      // Add first notification
      addNotification({
        type: 'info',
        message: 'First',
        dismissible: true,
      });

      // Advance time by 2 seconds
      vi.advanceTimersByTime(2000);

      // Add second notification
      addNotification({
        type: 'success',
        message: 'Second',
        dismissible: true,
      });

      let state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(2);

      // Advance time by 3 more seconds (5 seconds total for first notification)
      vi.advanceTimersByTime(3000);

      // First notification should be dismissed
      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);
      expect(state.notifications[0].message).toBe('Second');

      // Advance time by 2 more seconds (5 seconds total for second notification)
      vi.advanceTimersByTime(2000);

      // Second notification should be dismissed
      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(0);
    });
  });

  /**
   * Test: Remove notification
   * Requirements: 11.6
   */
  describe('Remove Notification', () => {
    it('should remove notification by ID', () => {
      const { addNotification, removeNotification } = useNotificationStore.getState();

      addNotification({
        type: 'info',
        message: 'Test notification',
        dismissible: true,
      });

      let state = useNotificationStore.getState();
      const notificationId = state.notifications[0].id;

      removeNotification(notificationId);

      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(0);
    });

    it('should remove specific notification from multiple notifications', () => {
      const { addNotification, removeNotification } = useNotificationStore.getState();

      addNotification({
        type: 'info',
        message: 'First',
        dismissible: true,
      });

      addNotification({
        type: 'info',
        message: 'Second',
        dismissible: true,
      });

      addNotification({
        type: 'info',
        message: 'Third',
        dismissible: true,
      });

      let state = useNotificationStore.getState();
      const secondNotificationId = state.notifications[1].id;

      removeNotification(secondNotificationId);

      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(2);
      expect(state.notifications[0].message).toBe('First');
      expect(state.notifications[1].message).toBe('Third');
    });

    it('should handle removing non-existent notification', () => {
      const { addNotification, removeNotification } = useNotificationStore.getState();

      addNotification({
        type: 'info',
        message: 'Test notification',
        dismissible: true,
      });

      let state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);

      // Try to remove non-existent notification
      removeNotification('non-existent-id');

      // Should not affect existing notifications
      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);
    });
  });

  /**
   * Test: Clear all notifications
   * Requirements: 11.6
   */
  describe('Clear All Notifications', () => {
    it('should clear all notifications', () => {
      const { addNotification, clearAll } = useNotificationStore.getState();

      addNotification({
        type: 'info',
        message: 'First',
        dismissible: true,
      });

      addNotification({
        type: 'warning',
        message: 'Second',
        dismissible: true,
      });

      addNotification({
        type: 'error',
        message: 'Third',
        dismissible: true,
      });

      let state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(3);

      clearAll();

      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(0);
    });

    it('should handle clearing when no notifications exist', () => {
      const { clearAll } = useNotificationStore.getState();

      clearAll();

      const state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(0);
    });
  });

  /**
   * Test: Critical error management
   * Requirements: 11.7
   */
  describe('Critical Error Management', () => {
    it('should set critical error', () => {
      const { setCriticalError } = useNotificationStore.getState();

      const criticalError = {
        title: 'Critical Error',
        message: 'A critical error occurred',
        details: 'Error details',
      };

      setCriticalError(criticalError);

      const state = useNotificationStore.getState();
      expect(state.criticalError).toEqual(criticalError);
    });

    it('should acknowledge and clear critical error', () => {
      const { setCriticalError, acknowledgeCriticalError } = useNotificationStore.getState();

      setCriticalError({
        title: 'Critical Error',
        message: 'Error message',
      });

      let state = useNotificationStore.getState();
      expect(state.criticalError).not.toBeNull();

      acknowledgeCriticalError();

      state = useNotificationStore.getState();
      expect(state.criticalError).toBeNull();
    });

    it('should replace existing critical error with new one', () => {
      const { setCriticalError } = useNotificationStore.getState();

      setCriticalError({
        title: 'First Error',
        message: 'First message',
      });

      let state = useNotificationStore.getState();
      expect(state.criticalError?.title).toBe('First Error');

      setCriticalError({
        title: 'Second Error',
        message: 'Second message',
      });

      state = useNotificationStore.getState();
      expect(state.criticalError?.title).toBe('Second Error');
    });

    it('should set critical error to null', () => {
      const { setCriticalError } = useNotificationStore.getState();

      setCriticalError({
        title: 'Error',
        message: 'Message',
      });

      let state = useNotificationStore.getState();
      expect(state.criticalError).not.toBeNull();

      setCriticalError(null);

      state = useNotificationStore.getState();
      expect(state.criticalError).toBeNull();
    });

    it('should handle critical error without details', () => {
      const { setCriticalError } = useNotificationStore.getState();

      setCriticalError({
        title: 'Error',
        message: 'Message',
      });

      const state = useNotificationStore.getState();
      expect(state.criticalError?.title).toBe('Error');
      expect(state.criticalError?.message).toBe('Message');
      expect(state.criticalError?.details).toBeUndefined();
    });
  });

  /**
   * Test: Notification types
   * Requirements: 11.5
   */
  describe('Notification Types', () => {
    it('should support info notifications', () => {
      const { addNotification } = useNotificationStore.getState();

      addNotification({
        type: 'info',
        message: 'Info message',
        dismissible: true,
      });

      const state = useNotificationStore.getState();
      expect(state.notifications[0].type).toBe('info');
    });

    it('should support warning notifications', () => {
      const { addNotification } = useNotificationStore.getState();

      addNotification({
        type: 'warning',
        message: 'Warning message',
        dismissible: true,
      });

      const state = useNotificationStore.getState();
      expect(state.notifications[0].type).toBe('warning');
    });

    it('should support error notifications', () => {
      const { addNotification } = useNotificationStore.getState();

      addNotification({
        type: 'error',
        message: 'Error message',
        dismissible: true,
      });

      const state = useNotificationStore.getState();
      expect(state.notifications[0].type).toBe('error');
    });

    it('should support success notifications', () => {
      const { addNotification } = useNotificationStore.getState();

      addNotification({
        type: 'success',
        message: 'Success message',
        dismissible: true,
      });

      const state = useNotificationStore.getState();
      expect(state.notifications[0].type).toBe('success');
    });
  });
});
