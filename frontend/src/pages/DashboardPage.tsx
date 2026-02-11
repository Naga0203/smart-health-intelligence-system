// ============================================================================
// Dashboard Page
// ============================================================================

import { useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Button,
  CircularProgress,
} from '@mui/material';
import { Assessment, Upload } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useSystemStore } from '@/stores/systemStore';
import { useUserStore } from '@/stores/userStore';

export const DashboardPage = () => {
  const navigate = useNavigate();
  const { status, fetchSystemStatus, loading: systemLoading } = useSystemStore();
  const { statistics, fetchStatistics, loading: statsLoading } = useUserStore();

  useEffect(() => {
    fetchSystemStatus();
    fetchStatistics();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational':
        return 'success.main';
      case 'degraded':
        return 'warning.main';
      case 'error':
        return 'error.main';
      default:
        return 'grey.500';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* System Status */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              System Status
            </Typography>
            {systemLoading ? (
              <CircularProgress size={24} />
            ) : status ? (
              <Box>
                <Box
                  sx={{
                    display: 'inline-block',
                    px: 2,
                    py: 0.5,
                    borderRadius: 1,
                    bgcolor: getStatusColor(status.status),
                    color: 'white',
                    mb: 1,
                  }}
                >
                  {status.status.toUpperCase()}
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Version: {status.version}
                </Typography>
              </Box>
            ) : (
              <Typography color="text.secondary">Unable to fetch status</Typography>
            )}
          </Paper>
        </Grid>

        {/* User Statistics */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Your Statistics
            </Typography>
            {statsLoading ? (
              <CircularProgress size={24} />
            ) : statistics ? (
              <Box>
                <Typography variant="h3" fontWeight="bold">
                  {statistics.total_assessments}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Assessments
                </Typography>
              </Box>
            ) : (
              <Typography color="text.secondary">No statistics available</Typography>
            )}
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                size="large"
                startIcon={<Assessment />}
                onClick={() => navigate('/app/assessment/new')}
              >
                New Symptom Analysis
              </Button>
              
              <Button
                variant="outlined"
                size="large"
                startIcon={<Upload />}
                onClick={() => navigate('/app/upload')}
              >
                Upload Medical Report
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};
