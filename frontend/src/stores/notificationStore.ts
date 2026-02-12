// ============================================================================
// Notification Store - Zustand
// ============================================================================
// Requirements: 11.5, 11.6, 11.7
// - Store notifications with type, message, dismissible flag
// - Auto-dismiss non-critical notifications after 5 seconds
// - Handle critical errors that require user acknowledgment

import { create } from 'zustand';

interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  dismissible: boolean;
  timestamp: string;
}

interface CriticalError {
  title: string;
  message: string;
  details?: string;
}

interface NotificationStore {
  notifications: Notification[];
  criticalError: CriticalError | null;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearAll: () => void;
  setCriticalError: (error: CriticalError | null) => void;
  acknowledgeCriticalError: () => void;
}

export const useNotificationStore = create<NotificationStore>((set) => ({
  notifications: [],
  criticalError: null,

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

  // Set critical error
  setCriticalError: (error) => {
    set({ criticalError: error });
  },

  // Acknowledge critical error
  acknowledgeCriticalError: () => {
    set({ criticalError: null });
  },
}));
