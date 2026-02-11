import {
  Box,
  Card,
  CardContent,
  Typography,
  Stack,
  Chip,
  Alert,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';

/**
 * @typedef {import('@/types').SystemStatus} SystemStatus
 */

/**
 * Get status icon and color based on system status
 * @param {'operational'|'degraded'|'error'} status
 * @returns {{icon: JSX.Element, color: string, label: string}}
 */
const getStatusDisplay = (status) => {
  switch (status) {
    case 'operational':
      return {
        icon: <CheckCircleIcon sx={{ color: 'success.main' }} />,
        color: 'success',
        label: 'System Operational',
      };
    case 'degraded':
      return {
        icon: <WarningIcon sx={{ color: 'warning.main' }} />,
        color: 'warning',
        label: 'Service Degraded',
      };
    case 'error':
      return {
        icon: <ErrorIcon sx={{ color: 'error.main' }} />,
        color: 'error',
        label: 'Service Unavailable',
      };
    default:
      return {
        icon: <WarningIcon sx={{ color: 'grey.500' }} />,
        color: 'default',
        label: 'Status Unknown',
      };
  }
};

/**
 * System Status Component
 * Displays system health status with color-coded indicators
 * @param {Object} props
 * @param {SystemStatus|null} props.status - System status object
 * @param {boolean} props.loading - Loading state
 */
export default function SystemStatus({ status, loading }) {
  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            System Status
          </Typography>
          <LoadingSkeleton />
        </CardContent>
      </Card>
    );
  }

  if (!status) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            System Status
          </Typography>
          <Alert severity="warning">Unable to fetch system status</Alert>
        </CardContent>
      </Card>
    );
  }

  const statusDisplay = getStatusDisplay(status.status);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          System Status
        </Typography>

        <Stack spacing={2}>
          {/* Status Indicator */}
          <Stack direction="row" spacing={2} alignItems="center">
            {statusDisplay.icon}
            <Box>
              <Typography variant="body1" fontWeight="medium">
                {statusDisplay.label}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Version: {status.version}
              </Typography>
            </Box>
          </Stack>

          {/* Component Status */}
          {status.components && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Components
              </Typography>
              <Stack spacing={1}>
                {status.components.orchestrator && (
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2">Orchestrator</Typography>
                    <Chip
                      label={status.components.orchestrator.status}
                      size="small"
                      color={status.components.orchestrator.status === 'operational' ? 'success' : 'error'}
                    />
                  </Stack>
                )}
                {status.components.predictor && (
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2">
                      Predictor ({status.components.predictor.models_loaded || 0} models)
                    </Typography>
                    <Chip
                      label={status.components.predictor.status}
                      size="small"
                      color={status.components.predictor.status === 'operational' ? 'success' : 'error'}
                    />
                  </Stack>
                )}
                {status.components.database && (
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2">Database</Typography>
                    <Chip
                      label={status.components.database.status}
                      size="small"
                      color={status.components.database.status === 'operational' ? 'success' : 'error'}
                    />
                  </Stack>
                )}
                {status.components.gemini_ai && (
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2">Gemini AI</Typography>
                    <Chip
                      label={status.components.gemini_ai.status}
                      size="small"
                      color={status.components.gemini_ai.status === 'operational' ? 'success' : 'error'}
                    />
                  </Stack>
                )}
              </Stack>
            </Box>
          )}

          {/* Degraded Service Warning */}
          {status.status === 'degraded' && (
            <Alert severity="warning">
              Some services are experiencing issues. Functionality may be limited.
            </Alert>
          )}

          {/* Service Unavailable Error */}
          {status.status === 'error' && (
            <Alert severity="error">
              System is currently unavailable. Please try again later.
            </Alert>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
