// ============================================================================
// Notification Store Tests
// ============================================================================

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { useNotificationStore } from './notificationStore';

describe('NotificationStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useNotificationStore.setState({
      notifications: [],
    });
    
    // Use fake timers
    vi.useFakeTimers();
  });

  afterEach(() => {
    // Restore real timers
    vi.restoreAllMocks();
  });

  describe('addNotification', () => {
    it('should add notification with id and timestamp', () => {
      const notification = {
        type: 'info',
        message: 'Test notification',
        dismissible: true,
      };

      const store = useNotificationStore.getState();
      store.addNotification(notification);

      const state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);
      expect(state.notifications[0]).toMatchObject({
        type: 'info',
        message: 'Test notification',
        dismissible: true,
      });
      expect(state.notifications[0].id).toBeDefined();
      expect(state.notifications[0].timestamp).toBeDefined();
    });

    it('should add multiple notifications', () => {
      const store = useNotificationStore.getState();
      
      store.addNotification({
        type: 'info',
        message: 'First notification',
        dismissible: true,
      });

      store.addNotification({
        type: 'warning',
        message: 'Second notification',
        dismissible: true,
      });

      const state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(2);
      expect(state.notifications[0].message).toBe('First notification');
      expect(state.notifications[1].message).toBe('Second notification');
    });

    it('should auto-dismiss non-critical dismissible notifications after 5 seconds', () => {
      const store = useNotificationStore.getState();
      
      store.addNotification({
        type: 'info',
        message: 'Auto-dismiss notification',
        dismissible: true,
      });

      let state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);

      // Fast-forward time by 5 seconds
      vi.advanceTimersByTime(5000);

      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(0);
    });

    it('should not auto-dismiss error notifications', () => {
      const store = useNotificationStore.getState();
      
      store.addNotification({
        type: 'error',
        message: 'Error notification',
        dismissible: true,
      });

      let state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);

      // Fast-forward time by 5 seconds
      vi.advanceTimersByTime(5000);

      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);
    });

    it('should not auto-dismiss non-dismissible notifications', () => {
      const store = useNotificationStore.getState();
      
      store.addNotification({
        type: 'info',
        message: 'Non-dismissible notification',
        dismissible: false,
      });

      let state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);

      // Fast-forward time by 5 seconds
      vi.advanceTimersByTime(5000);

      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);
    });
  });

  describe('removeNotification', () => {
    it('should remove notification by id', () => {
      const store = useNotificationStore.getState();
      
      store.addNotification({
        type: 'info',
        message: 'First notification',
        dismissible: true,
      });

      store.addNotification({
        type: 'warning',
        message: 'Second notification',
        dismissible: true,
      });

      let state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(2);

      const firstNotificationId = state.notifications[0].id;
      store.removeNotification(firstNotificationId);

      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);
      expect(state.notifications[0].message).toBe('Second notification');
    });

    it('should handle removing non-existent notification', () => {
      const store = useNotificationStore.getState();
      
      store.addNotification({
        type: 'info',
        message: 'Test notification',
        dismissible: true,
      });

      let state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);

      store.removeNotification('non-existent-id');

      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(1);
    });
  });

  describe('clearAll', () => {
    it('should clear all notifications', () => {
      const store = useNotificationStore.getState();
      
      store.addNotification({
        type: 'info',
        message: 'First notification',
        dismissible: true,
      });

      store.addNotification({
        type: 'warning',
        message: 'Second notification',
        dismissible: true,
      });

      store.addNotification({
        type: 'error',
        message: 'Third notification',
        dismissible: true,
      });

      let state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(3);

      store.clearAll();

      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(0);
    });

    it('should handle clearing when no notifications exist', () => {
      const store = useNotificationStore.getState();
      
      let state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(0);

      store.clearAll();

      state = useNotificationStore.getState();
      expect(state.notifications).toHaveLength(0);
    });
  });
});
