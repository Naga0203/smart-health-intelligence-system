// ============================================================================
// Session Monitor Hook
// ============================================================================
// Requirements: 11.3
// - Monitor token expiration time
// - Display notification 5 minutes before expiration
// - Offer option to extend session

import { useEffect, useRef } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { useNotificationStore } from '@/stores/notificationStore';
import { auth } from '@/services/firebase';

const FIVE_MINUTES_MS = 5 * 60 * 1000; // 5 minutes in milliseconds
const CHECK_INTERVAL_MS = 60 * 1000; // Check every minute

export const useSessionMonitor = () => {
  const user = useAuthStore((state: any) => state.user);
  const refreshToken = useAuthStore((state: any) => state.refreshToken);
  const { addNotification } = useNotificationStore();
  const warningShownRef = useRef(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Only monitor if user is authenticated
    if (!user || !auth.currentUser) {
      return;
    }

    const checkTokenExpiration = async () => {
      try {
        const currentUser = auth.currentUser;
        if (!currentUser) return;

        // Get the ID token result which includes expiration time
        const tokenResult = await currentUser.getIdTokenResult();
        const expirationTime = new Date(tokenResult.expirationTime).getTime();
        const currentTime = Date.now();
        const timeUntilExpiration = expirationTime - currentTime;

        // If token expires in less than 5 minutes and warning hasn't been shown
        if (timeUntilExpiration <= FIVE_MINUTES_MS && timeUntilExpiration > 0 && !warningShownRef.current) {
          const minutesRemaining = Math.ceil(timeUntilExpiration / 60000);
          
          addNotification({
            type: 'warning',
            message: `Your session will expire in ${minutesRemaining} minute${minutesRemaining !== 1 ? 's' : ''}. Click to extend your session.`,
            dismissible: true,
          });

          warningShownRef.current = true;

          // Automatically refresh token to extend session
          setTimeout(async () => {
            try {
              await refreshToken();
              addNotification({
                type: 'success',
                message: 'Session extended successfully',
                dismissible: true,
              });
              warningShownRef.current = false;
            } catch (error) {
              console.error('Failed to refresh token:', error);
            }
          }, 1000);
        }

        // Reset warning flag if token has been refreshed
        if (timeUntilExpiration > FIVE_MINUTES_MS) {
          warningShownRef.current = false;
        }
      } catch (error) {
        console.error('Error checking token expiration:', error);
      }
    };

    // Initial check
    checkTokenExpiration();

    // Set up interval to check periodically
    intervalRef.current = setInterval(checkTokenExpiration, CHECK_INTERVAL_MS);

    // Cleanup
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [user, addNotification, refreshToken]);
};
