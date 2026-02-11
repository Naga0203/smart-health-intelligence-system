import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Chip,
  Stack,
} from '@mui/material';
import { format } from 'date-fns';
import { EmptyState } from '@/components/common/EmptyState';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';

/**
 * @typedef {import('@/types').AssessmentHistoryItem} AssessmentHistoryItem
 */

/**
 * Get color for confidence level
 * @param {'LOW'|'MEDIUM'|'HIGH'} confidence
 * @returns {string}
 */
const getConfidenceColor = (confidence) => {
  switch (confidence) {
    case 'HIGH':
      return 'success';
    case 'MEDIUM':
      return 'warning';
    case 'LOW':
      return 'error';
    default:
      return 'default';
  }
};

/**
 * Get color for risk level
 * @param {string} riskLevel
 * @returns {string}
 */
const getRiskLevelColor = (riskLevel) => {
  const level = riskLevel?.toLowerCase();
  switch (level) {
    case 'low':
      return 'info';
    case 'medium':
      return 'warning';
    case 'elevated':
      return 'warning';
    case 'high':
      return 'error';
    default:
      return 'default';
  }
};

/**
 * Recent Assessments Component
 * Displays list of recent assessments with date, condition, risk level, confidence
 * @param {Object} props
 * @param {AssessmentHistoryItem[]} props.assessments - Array of assessment history items
 * @param {boolean} props.loading - Loading state
 */
export default function RecentAssessments({ assessments, loading }) {
  const navigate = useNavigate();

  const handleAssessmentClick = (assessmentId) => {
    navigate(`/app/assessment/${assessmentId}`);
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Assessments
          </Typography>
          <LoadingSkeleton />
        </CardContent>
      </Card>
    );
  }

  if (!assessments || assessments.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Assessments
          </Typography>
          <EmptyState
            title="No assessments yet"
            description="Start your first health assessment to see results here"
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recent Assessments
        </Typography>
        <List>
          {assessments.map((assessment) => (
            <ListItem key={assessment.id} disablePadding>
              <ListItemButton onClick={() => handleAssessmentClick(assessment.id)}>
                <ListItemText
                  primary={
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Typography variant="body1" component="span">
                        {assessment.disease}
                      </Typography>
                      <Chip
                        label={assessment.confidence}
                        size="small"
                        color={getConfidenceColor(assessment.confidence)}
                      />
                    </Stack>
                  }
                  secondary={
                    <Box sx={{ mt: 0.5 }}>
                      <Typography variant="body2" color="text.secondary" component="span">
                        {format(new Date(assessment.created_at), 'MMM dd, yyyy HH:mm')}
                      </Typography>
                      <Typography variant="body2" component="span" sx={{ ml: 2 }}>
                        Probability: {Math.round(assessment.probability * 100)}%
                      </Typography>
                    </Box>
                  }
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
}
