import { useEffect, useState } from 'react';
import { Container, Grid, Typography } from '@mui/material';
import { useAssessmentStore } from '@/stores/assessmentStore';

import { useUserStore } from '@/stores/userStore';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import RecentAssessments from '@/components/dashboard/RecentAssessments';

import QuickActions from '@/components/dashboard/QuickActions';
import UserStatistics from '@/components/dashboard/UserStatistics';
import TopPredictions from '@/components/dashboard/TopPredictions';
import { apiService } from '@/services/api';

/**
 * Dashboard overview page
 * Displays recent assessments, system status, user statistics, and quick actions
 */
export default function DashboardPage() {
  const { fetchAssessmentHistory, assessmentHistory, loading: assessmentsLoading } = useAssessmentStore();

  const { fetchStatistics, statistics, loading: statsLoading } = useUserStore();

  // Top predictions state
  const [predictions, setPredictions] = useState(null);
  const [predictionsLoading, setPredictionsLoading] = useState(false);
  const [predictionsError, setPredictionsError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch all dashboard data on mount
    const fetchData = async () => {
      try {
        await Promise.all([
          fetchAssessmentHistory(1, 5), // Fetch first 5 recent assessments

          fetchStatistics(),
        ]);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };

    fetchData();
  }, [fetchAssessmentHistory, fetchStatistics]);

  /**
   * Fetch top N predictions
   * Note: This requires symptoms, age, and gender. 
   * For demo purposes, we'll use sample data or fetch from last assessment
   */
  const handleFetchPredictions = async (n = 5) => {
    setPredictionsLoading(true);
    setPredictionsError(null);

    try {
      // Try to get data from the most recent assessment
      const recentAssessment = assessmentHistory?.assessments?.[0];

      if (!recentAssessment || !recentAssessment.symptoms || recentAssessment.symptoms.length === 0) {
        setPredictionsError('No recent assessment data available. Complete an assessment first.');
        setPredictions(null);
        return;
      }

      // Use data from recent assessment
      const result = await apiService.getTopPredictions(
        recentAssessment.symptoms,
        30, // Default age if not available
        'other', // Default gender if not available
        n
      );

      setPredictions(result.predictions || []);
    } catch (error) {
      console.error('Error fetching top predictions:', error);
      setPredictionsError(error.response?.data?.message || 'Failed to fetch predictions');
      setPredictions(null);
    } finally {
      setPredictionsLoading(false);
    }
  };

  const isLoading = assessmentsLoading || statsLoading;

  if (isLoading && !assessmentHistory && !statistics) {
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
        <Grid size={{ xs: 12 }}>
          <QuickActions />
        </Grid>



        {/* User Statistics */}
        <Grid size={{ xs: 12, md: 6 }}>
          <UserStatistics statistics={statistics} loading={statsLoading} />
        </Grid>

        {/* Top Predictions */}
        <Grid size={{ xs: 12, md: 6 }}>
          <TopPredictions
            predictions={predictions}
            loading={predictionsLoading}
            error={predictionsError}
            onFetchPredictions={handleFetchPredictions}
            defaultN={5}
          />
        </Grid>

        {/* Recent Assessments */}
        <Grid size={{ xs: 12, md: 6 }}>
          <RecentAssessments
            assessments={assessmentHistory?.assessments || []}
            loading={assessmentsLoading}
          />
        </Grid>
      </Grid>
    </Container>
  );
}
