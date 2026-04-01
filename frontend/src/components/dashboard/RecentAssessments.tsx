import { useNavigate } from 'react-router-dom';
import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Chip,
  Stack,
  useTheme,
  alpha,
  Box
} from '@mui/material';
import { format } from 'date-fns';
import { EmptyState } from '@/components/common/EmptyState';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';

/**
 * @typedef {import('@/types').AssessmentHistoryItem} AssessmentHistoryItem
 */

/**
 * Get color for confidence level
 * @param {'HIGH'|'MEDIUM'|'LOW'|string} confidence
 * @returns {'success'|'warning'|'error'|'default'}
 */
const getConfidenceColor = (confidence: string): 'success' | 'warning' | 'error' | 'default' => {
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
const getRiskLevelColor = (riskLevel: string): 'info' | 'warning' | 'error' | 'default' => {
  const level = riskLevel?.toLowerCase();
  switch (level) {
    case 'low':
      return 'info';
    case 'medium':
    case 'elevated':
      return 'warning';
    case 'high':
      return 'error';
    default:
      return 'default';
  }
};

interface RecentAssessmentsProps {
  assessments: any[];
  loading: boolean;
}

/**
 * Recent Assessments Component
 * Displays list of recent assessments with date, condition, risk level, confidence
 */
export default function RecentAssessments({ assessments, loading }: RecentAssessmentsProps) {
  const navigate = useNavigate();
  const theme = useTheme();

  const handleAssessmentClick = (assessmentId: string) => {
    navigate(`/app/assessment/${assessmentId}`);
  };

  const glassCardSx = {
    background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.4)} 0%, ${alpha(
      theme.palette.background.paper,
      0.1
    )} 100%)`,
    backdropFilter: 'blur(24px)',
    border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
    borderRadius: 4,
    boxShadow: `0 8px 32px 0 ${alpha(theme.palette.common.black, 0.05)}`,
    height: '100%'
  };

  if (loading) {
    return (
      <Card sx={glassCardSx}>
        <CardContent>
          <Typography variant="h6" gutterBottom fontWeight="600">
            Recent Assessments
          </Typography>
          <LoadingSkeleton />
        </CardContent>
      </Card>
    );
  }

  if (!assessments || assessments.length === 0) {
    return (
      <Card sx={glassCardSx}>
        <CardContent>
          <Typography variant="h6" gutterBottom fontWeight="600">
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
    <Card sx={glassCardSx}>
      <CardContent>
        <Typography variant="h6" gutterBottom fontWeight="600">
          Recent Assessments
        </Typography>
        <List>
          {assessments.map((assessment, index) => (
            <ListItem 
              key={assessment.id} 
              disablePadding
              sx={{
                mb: 1,
                borderRadius: 2,
                overflow: 'hidden',
                background: alpha(theme.palette.background.paper, 0.4),
                border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: `0 4px 12px ${alpha(theme.palette.common.black, 0.1)}`,
                  background: alpha(theme.palette.background.paper, 0.6),
                }
              }}
            >
              <ListItemButton onClick={() => handleAssessmentClick(assessment.id)} sx={{ p: 2 }}>
                <ListItemText
                  primary={
                    <Stack direction="row" spacing={1} alignItems="center" mb={0.5}>
                      <Typography variant="body1" component="span" fontWeight="500">
                        {assessment.disease}
                      </Typography>
                      <Chip
                        label={assessment.confidence}
                        size="small"
                        color={getConfidenceColor(assessment.confidence)}
                        sx={{ height: 20, fontSize: '0.7rem', fontWeight: 600 }}
                      />
                    </Stack>
                  }
                  secondary={
                    <Box sx={{ mt: 0.5, display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
                      <Typography variant="body2" color="text.secondary" component="span">
                        {format(new Date(assessment.created_at), 'MMM dd, yyyy • HH:mm')}
                      </Typography>
                      <Typography 
                        variant="body2" 
                        component="span"
                        color="primary.main"
                        fontWeight="500"
                      >
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
