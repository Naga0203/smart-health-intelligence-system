// ============================================================================
// Assessment Timeline Component
// ============================================================================

import React from 'react';
import { Box, Button, Typography } from '@mui/material';
import { AssessmentCard } from './AssessmentCard';
import { EmptyState } from '@/components/common/EmptyState';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import AssignmentIcon from '@mui/icons-material/Assignment';

interface Assessment {
  id: string;
  created_at: string;
  disease: string;
  probability: number;
  confidence: 'LOW' | 'MEDIUM' | 'HIGH';
  riskLevel?: 'low' | 'medium' | 'elevated' | 'high';
}

interface AssessmentTimelineProps {
  assessments: Assessment[];
  onAssessmentClick: (id: string) => void;
  onLoadMore?: () => void;
  hasMore: boolean;
  loading: boolean;
}

// Helper function to determine risk level from probability
const getRiskLevel = (probability: number): 'low' | 'medium' | 'elevated' | 'high' => {
  if (probability < 25) return 'low';
  if (probability < 50) return 'medium';
  if (probability < 75) return 'elevated';
  return 'high';
};

export const AssessmentTimeline: React.FC<AssessmentTimelineProps> = ({
  assessments,
  onAssessmentClick,
  onLoadMore,
  hasMore,
  loading,
}) => {
  // Show loading skeleton on initial load
  if (loading && assessments.length === 0) {
    return <LoadingSkeleton variant="card" count={3} />;
  }

  // Show empty state when no assessments exist
  if (!loading && assessments.length === 0) {
    return (
      <EmptyState
        icon={AssignmentIcon}
        title="No Assessment History"
        description="You haven't completed any health assessments yet. Start your first assessment to track your health over time."
        actionLabel="New Assessment"
        onAction={() => {
          window.location.href = '/app/assessment/new';
        }}
      />
    );
  }

  // Sort assessments by date (most recent first)
  const sortedAssessments = [...assessments].sort((a, b) => {
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
        Assessment History
      </Typography>

      {sortedAssessments.map((assessment) => (
        <AssessmentCard
          key={assessment.id}
          id={assessment.id}
          date={assessment.created_at}
          condition={assessment.disease}
          riskLevel={assessment.riskLevel || getRiskLevel(assessment.probability)}
          confidence={assessment.confidence}
          probability={assessment.probability}
          onClick={onAssessmentClick}
        />
      ))}

      {/* Load More Button */}
      {hasMore && (
        <Box display="flex" justifyContent="center" mt={3}>
          <Button
            variant="outlined"
            onClick={onLoadMore}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Load More'}
          </Button>
        </Box>
      )}

      {/* Loading indicator for pagination */}
      {loading && assessments.length > 0 && (
        <Box mt={2}>
          <LoadingSkeleton variant="card" count={2} />
        </Box>
      )}
    </Box>
  );
};
