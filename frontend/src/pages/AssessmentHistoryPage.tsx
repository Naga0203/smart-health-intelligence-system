// ============================================================================
// Assessment History Page
// ============================================================================

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Typography, Box, Alert, useTheme } from '@mui/material';
import { AssessmentTimeline } from '@/components/history/AssessmentTimeline';
import { HistoryFilters, FilterValues } from '@/components/history/HistoryFilters';
import { RiskTrendChart } from '@/components/history/RiskTrendChart';
import { useAssessmentStore } from '@/stores/assessmentStore';

export const AssessmentHistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const { assessmentHistory, loading, error, fetchAssessmentHistory } = useAssessmentStore();
  
  const [currentPage, setCurrentPage] = useState(1);
  const [filters, setFilters] = useState<FilterValues>({
    condition: '',
    startDate: '',
    endDate: '',
  });

  // Fetch assessment history on mount
  useEffect(() => {
    fetchAssessmentHistory(1, 10);
  }, [fetchAssessmentHistory]);

  // Handle assessment card click - navigate to detail view
  const handleAssessmentClick = (id: string) => {
    navigate(`/app/assessment/${id}`);
  };

  // Handle load more
  const handleLoadMore = () => {
    const nextPage = currentPage + 1;
    setCurrentPage(nextPage);
    fetchAssessmentHistory(nextPage, 10);
  };

  // Handle filter changes
  const handleFilterChange = (newFilters: FilterValues) => {
    setFilters(newFilters);
    setCurrentPage(1);
    // In a real implementation, you would pass filters to the API
    // For now, we'll just refetch with page 1
    fetchAssessmentHistory(1, 10);
  };

  // Get assessments from store
  const assessments: any[] = assessmentHistory?.assessments || [];
  const total = assessmentHistory?.total || 0;
  const hasMore = assessments.length < total;

  // Filter assessments client-side (in production, this should be done server-side)
  const filteredAssessments = assessments.filter((assessment: any) => {
    // Filter by condition
    if (filters.condition && assessment.disease !== filters.condition) {
      return false;
    }

    // Filter by date range
    const assessmentDate = new Date(assessment.created_at);
    if (filters.startDate) {
      const startDate = new Date(filters.startDate);
      if (assessmentDate < startDate) {
        return false;
      }
    }
    if (filters.endDate) {
      const endDate = new Date(filters.endDate);
      endDate.setHours(23, 59, 59, 999); // Include the entire end date
      if (assessmentDate > endDate) {
        return false;
      }
    }

    return true;
  });

  // Get unique conditions for filter dropdown
  const availableConditions = Array.from(
    new Set(assessments.map((a: any) => a.disease))
  ).sort() as string[];

  return (
    <Box 
      sx={{ 
        minHeight: '100vh', 
        pb: 8,
        background: `linear-gradient(135deg, ${theme.palette.background.default} 0%, ${theme.palette.background.paper} 100%)`, 
      }}
    >
      <Container maxWidth="lg" sx={{ py: 4, position: 'relative', zIndex: 1 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700, color: theme.palette.text.primary }}>
          Assessment History
        </Typography>

        <Typography variant="body1" sx={{ mb: 4, color: theme.palette.text.secondary }}>
          View and track your health assessments over time
        </Typography>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Risk Trend Chart */}
      {filteredAssessments.length > 0 && (
        <RiskTrendChart assessments={filteredAssessments} />
      )}

      {/* Filters */}
      <HistoryFilters
        onFilterChange={handleFilterChange}
        availableConditions={availableConditions}
      />

      {/* Assessment Timeline */}
      <AssessmentTimeline
        assessments={filteredAssessments}
        onAssessmentClick={handleAssessmentClick}
        onLoadMore={handleLoadMore}
        hasMore={hasMore && filters.condition === '' && filters.startDate === '' && filters.endDate === ''}
        loading={loading}
      />

      {/* Results Summary */}
      {filteredAssessments.length > 0 && (
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            Showing {filteredAssessments.length} of {total} assessments
          </Typography>
        </Box>
      )}
      </Container>
    </Box>
  );
};
