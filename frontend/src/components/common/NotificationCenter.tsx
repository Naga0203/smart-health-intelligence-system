// ============================================================================
// Notification Center Component
// ============================================================================
// Requirements: 11.5, 11.6, 11.7
// - Display notifications in non-intrusive area (top-right corner)
// - Auto-dismiss for non-critical notifications (5 seconds)
// - Add dismiss button for all notifications
// - Display critical error modal requiring acknowledgment

import { Snackbar, Alert, IconButton, Box } from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { useNotificationStore } from '@/stores/notificationStore';
import { CriticalErrorModal } from './CriticalErrorModal';

export const NotificationCenter = () => {
  const { 
    notifications, 
    removeNotification, 
    criticalError, 
    acknowledgeCriticalError 
  } = useNotificationStore();

  return (
    <>
      <Box
        sx={{
          position: 'fixed',
          top: 80,
          right: 16,
          zIndex: (theme) => theme.zIndex.snackbar,
          display: 'flex',
          flexDirection: 'column',
          gap: 1,
          maxWidth: 400,
        }}
        role="region"
        aria-label="Notifications"
      >
        {notifications.map((notification) => (
          <Snackbar
            key={notification.id}
            open={true}
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
            sx={{ position: 'relative', top: 0, right: 0 }}
          >
            <Alert
              severity={notification.type}
              variant="filled"
              action={
                <IconButton
                  size="small"
                  aria-label="close notification"
                  color="inherit"
                  onClick={() => removeNotification(notification.id)}
                >
                  <CloseIcon fontSize="small" />
                </IconButton>
              }
              sx={{ width: '100%' }}
            >
              {notification.message}
            </Alert>
          </Snackbar>
        ))}
      </Box>

      {criticalError && (
        <CriticalErrorModal
          open={true}
          title={criticalError.title}
          message={criticalError.message}
          details={criticalError.details}
          onAcknowledge={acknowledgeCriticalError}
        />
      )}
    </>
  );
};
