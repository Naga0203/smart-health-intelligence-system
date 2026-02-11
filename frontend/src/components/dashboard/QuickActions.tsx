import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Stack,
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

  const handleNewAssessment = () => {
    navigate('/app/assessment/new');
  };

  const handleUploadReport = () => {
    navigate('/app/upload');
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <Button
            variant="contained"
            color="primary"
            size="large"
            startIcon={<AssessmentIcon />}
            onClick={handleNewAssessment}
            fullWidth
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
          >
            Upload Medical Report
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}
