// ============================================================================
// Notification Store - Zustand
// ============================================================================

import { create } from 'zustand';
import type { Notification } from '@/types';

interface NotificationState {
  notifications: Notification[];
  
  // Actions
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearAll: () => void;
}

export const useNotificationStore = create<NotificationState>((set) => ({
  notifications: [],

  // Add notification
  addNotification: (notification) => {
    const newNotification: Notification = {
      ...notification,
      id: `${Date.now()}-${Math.random()}`,
      timestamp: new Date().toISOString(),
    };

    set((state) => ({
      notifications: [...state.notifications, newNotification],
    }));

    // Auto-dismiss non-critical notifications after 5 seconds
    if (notification.dismissible && notification.type !== 'error') {
      setTimeout(() => {
        set((state) => ({
          notifications: state.notifications.filter(
            (n) => n.id !== newNotification.id
          ),
        }));
      }, 5000);
    }
  },

  // Remove notification
  removeNotification: (id) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    }));
  },

  // Clear all notifications
  clearAll: () => {
    set({ notifications: [] });
  },
}));
