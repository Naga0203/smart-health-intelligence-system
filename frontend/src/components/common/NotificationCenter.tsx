// ============================================================================
// Notification Center Component
// ============================================================================

import { Snackbar, Alert, IconButton, Box } from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { useNotificationStore } from '@/stores/notificationStore';

export const NotificationCenter = () => {
  const { notifications, removeNotification } = useNotificationStore();

  return (
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
              notification.dismissible && (
                <IconButton
                  size="small"
                  aria-label="close"
                  color="inherit"
                  onClick={() => removeNotification(notification.id)}
                >
                  <CloseIcon fontSize="small" />
                </IconButton>
              )
            }
            sx={{ width: '100%' }}
          >
            {notification.message}
          </Alert>
        </Snackbar>
      ))}
    </Box>
  );
};
