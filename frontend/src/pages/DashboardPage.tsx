import { useEffect } from 'react';
import { Box, Container, Grid, Typography } from '@mui/material';
import { useAssessmentStore } from '@/stores/assessmentStore';
import { useSystemStore } from '@/stores/systemStore';
import { useUserStore } from '@/stores/userStore';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import RecentAssessments from '@/components/dashboard/RecentAssessments';
import SystemStatus from '@/components/dashboard/SystemStatus';
import QuickActions from '@/components/dashboard/QuickActions';
import UserStatistics from '@/components/dashboard/UserStatistics';

/**
 * Dashboard overview page
 * Displays recent assessments, system status, user statistics, and quick actions
 */
export default function DashboardPage() {
  const { fetchAssessmentHistory, assessmentHistory, loading: assessmentsLoading } = useAssessmentStore();
  const { fetchSystemStatus, fetchModelInfo, status, modelInfo, loading: systemLoading } = useSystemStore();
  const { fetchStatistics, statistics, loading: statsLoading } = useUserStore();

  useEffect(() => {
    // Fetch all dashboard data on mount
    const fetchData = async () => {
      try {
        await Promise.all([
          fetchAssessmentHistory(1, 5), // Fetch first 5 recent assessments
          fetchSystemStatus(),
          fetchModelInfo(),
          fetchStatistics(),
        ]);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };

    fetchData();
  }, [fetchAssessmentHistory, fetchSystemStatus, fetchModelInfo, fetchStatistics]);

  const isLoading = assessmentsLoading || systemLoading || statsLoading;

  if (isLoading && !assessmentHistory && !status && !statistics) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <LoadingSkeleton />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12}>
          <QuickActions />
        </Grid>

        {/* System Status */}
        <Grid item xs={12} md={6}>
          <SystemStatus status={status} modelInfo={modelInfo} loading={systemLoading} />
        </Grid>

        {/* User Statistics */}
        <Grid item xs={12} md={6}>
          <UserStatistics statistics={statistics} loading={statsLoading} />
        </Grid>

        {/* Recent Assessments */}
        <Grid item xs={12}>
          <RecentAssessments 
            assessments={assessmentHistory?.assessments || []} 
            loading={assessmentsLoading} 
          />
        </Grid>
      </Grid>
    </Container>
  );
}
