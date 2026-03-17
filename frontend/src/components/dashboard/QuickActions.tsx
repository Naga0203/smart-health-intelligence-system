import { useNavigate } from 'react-router-dom';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Stack,
  useTheme,
  alpha
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  Upload as UploadIcon,
} from '@mui/icons-material';

/**
 * Quick Actions Component
 * Provides quick access buttons for common actions
 */
export default function QuickActions() {
  const navigate = useNavigate();
  const theme = useTheme();

  const handleNewAssessment = () => {
    navigate('/app/assessment/new');
  };

  const handleUploadReport = () => {
    navigate('/app/upload');
  };

  return (
    <Card
      sx={{
        background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.4)} 0%, ${alpha(
          theme.palette.background.paper,
          0.1
        )} 100%)`,
        backdropFilter: 'blur(24px)',
        border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
        borderRadius: 4,
        boxShadow: `0 8px 32px 0 ${alpha(theme.palette.common.black, 0.05)}`,
      }}
    >
      <CardContent>
        <Typography variant="h6" gutterBottom fontWeight="600">
          Quick Actions
        </Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} mt={2}>
          <Button
            variant="contained"
            color="primary"
            size="large"
            startIcon={<AssessmentIcon />}
            onClick={handleNewAssessment}
            fullWidth
            sx={{
              borderRadius: 3,
              py: 1.5,
              fontWeight: 600,
              textTransform: 'none',
              background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
              boxShadow: `0 4px 12px ${alpha(theme.palette.primary.main, 0.3)}`,
            }}
          >
            New Symptom Analysis
          </Button>
          <Button
            variant="outlined"
            color="primary"
            size="large"
            startIcon={<UploadIcon />}
            onClick={handleUploadReport}
            fullWidth
            sx={{
              borderRadius: 3,
              py: 1.5,
              fontWeight: 600,
              textTransform: 'none',
              borderWidth: 2,
              '&:hover': {
                borderWidth: 2,
                backgroundColor: alpha(theme.palette.primary.main, 0.04),
              }
            }}
          >
            Upload Medical Report
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}
