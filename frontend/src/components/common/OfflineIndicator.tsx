// ============================================================================
// Offline Indicator Component
// ============================================================================
// Displays a banner when the user is offline or has a slow connection

import { Alert, Snackbar, Box } from '@mui/material';
import { WifiOff, SignalCellularConnectedNoInternet0Bar } from '@mui/icons-material';
import { useNetworkStatus } from '@/hooks/useNetworkStatus';

export function OfflineIndicator() {
  const { isOnline, isSlow } = useNetworkStatus();

  // Show offline banner
  if (!isOnline) {
    return (
      <Snackbar
        open={true}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        sx={{ top: { xs: 8, sm: 24 } }}
      >
        <Alert
          severity="error"
          icon={<WifiOff />}
          sx={{
            width: '100%',
            boxShadow: 3,
          }}
        >
          You are currently offline. Some features may not be available.
        </Alert>
      </Snackbar>
    );
  }

  // Show slow connection warning
  if (isSlow) {
    return (
      <Snackbar
        open={true}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        sx={{ top: { xs: 8, sm: 24 } }}
      >
        <Alert
          severity="warning"
          icon={<SignalCellularConnectedNoInternet0Bar />}
          sx={{
            width: '100%',
            boxShadow: 3,
          }}
        >
          Your connection is slow. Loading may take longer than usual.
        </Alert>
      </Snackbar>
    );
  }

  return null;
}

/**
 * Inline offline indicator for specific components
 */
export function InlineOfflineIndicator() {
  const { isOnline, isSlow } = useNetworkStatus();

  if (!isOnline) {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          p: 2,
          bgcolor: 'error.light',
          color: 'error.contrastText',
          borderRadius: 1,
          mb: 2,
        }}
      >
        <WifiOff />
        <span>You are offline. Please check your internet connection.</span>
      </Box>
    );
  }

  if (isSlow) {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          p: 2,
          bgcolor: 'warning.light',
          color: 'warning.contrastText',
          borderRadius: 1,
          mb: 2,
        }}
      >
        <SignalCellularConnectedNoInternet0Bar />
        <span>Slow connection detected. Some features may be slower.</span>
      </Box>
    );
  }

  return null;
}
