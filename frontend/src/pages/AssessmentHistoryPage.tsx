// ============================================================================
// Assessment History Page
// ============================================================================

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Typography, Box, Alert } from '@mui/material';
import { AssessmentTimeline } from '@/components/history/AssessmentTimeline';
import { HistoryFilters, FilterValues } from '@/components/history/HistoryFilters';
import { RiskTrendChart } from '@/components/history/RiskTrendChart';
import { useAssessmentStore } from '@/stores/assessmentStore';

export const AssessmentHistoryPage: React.FC = () => {
  const navigate = useNavigate();
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
  const assessments = assessmentHistory?.assessments || [];
  const total = assessmentHistory?.total || 0;
  const pageSize = assessmentHistory?.page_size || 10;
  const hasMore = assessments.length < total;

  // Filter assessments client-side (in production, this should be done server-side)
  const filteredAssessments = assessments.filter((assessment) => {
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
    new Set(assessments.map((a) => a.disease))
  ).sort();

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Assessment History
      </Typography>

      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
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
          <Typography variant="body2" color="text.secondary">
            Showing {filteredAssessments.length} of {total} assessments
          </Typography>
        </Box>
      )}
    </Container>
  );
};
