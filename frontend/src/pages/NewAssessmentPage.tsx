// ============================================================================
// New Assessment Page
// Integrates AssessmentStepper and handles submission
// ============================================================================

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Alert,
  CircularProgress,
} from '@mui/material';
import { AssessmentStepper, type AssessmentFormData } from '@/components/assessment/AssessmentStepper';
import { useAssessmentStore } from '@/stores/assessmentStore';
import { useAuthStore } from '@/stores/authStore';
import { useSystemStore } from '@/stores/systemStore';
import { useNotificationStore } from '@/stores/notificationStore';

export const NewAssessmentPage: React.FC = () => {
  const navigate = useNavigate();
  const [systemCheckLoading, setSystemCheckLoading] = useState(true);
  const [systemAvailable, setSystemAvailable] = useState(true);

  const { submitAssessment, loading: submitting } = useAssessmentStore();
  const { user } = useAuthStore();
  const { status, fetchSystemStatus } = useSystemStore();
  const { addNotification } = useNotificationStore();

  // Check system health on mount
  useEffect(() => {
    const checkSystemHealth = async () => {
      try {
        await fetchSystemStatus();
        setSystemCheckLoading(false);
      } catch (error) {
        console.error('Failed to check system status:', error);
        setSystemCheckLoading(false);
        setSystemAvailable(false);
      }
    };

    checkSystemHealth();
  }, [fetchSystemStatus]);

  // Check if system is available for assessment
  useEffect(() => {
    if (status) {
      const isAvailable = status.status === 'operational' || status.status === 'degraded';
      setSystemAvailable(isAvailable);
    }
  }, [status]);

  const handleSubmit = async (formData: AssessmentFormData) => {
    // Check system health before submission
    if (!systemAvailable) {
      addNotification({
        type: 'error',
        message: 'System is currently unavailable. Please try again later.',
        dismissible: true,
      });
      return;
    }

    try {
      // Transform form data to API format
      const assessmentData = {
        symptoms: formData.symptoms.map((s) => s.name),
        age: formData.demographics.age,
        gender: formData.demographics.gender,
        additional_info: {
          symptom_details: formData.symptoms.map((s) => ({
            name: s.name,
            severity: s.severity,
            duration: s.duration,
          })),
          medical_history: formData.demographics.medical_history,
          vitals: formData.vitals,
        },
      };

      // Submit assessment
      const result = await submitAssessment(assessmentData, !!user);

      // Show success notification
      addNotification({
        type: 'success',
        message: 'Assessment completed successfully',
        dismissible: true,
      });

      // Navigate to results page
      navigate(`/app/assessment/${result.assessment_id}`);
    } catch (error) {
      console.error('Assessment submission failed:', error);
      
      // Show error notification
      addNotification({
        type: 'error',
        message: error.response?.data?.message || 'Failed to submit assessment. Please try again.',
        dismissible: true,
      });
    }
  };

  if (systemCheckLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: 400,
          }}
        >
          <CircularProgress />
          <Typography variant="body1" sx={{ mt: 2 }}>
            Checking system status...
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          New Health Assessment
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Complete the following steps to receive a personalized health risk assessment.
        </Typography>
      </Box>

      {/* System Status Warning */}
      {!systemAvailable && (
        <Alert severity="error" sx={{ mb: 3 }}>
          The assessment system is currently unavailable. Please try again later or contact support if the issue persists.
        </Alert>
      )}

      {status?.status === 'degraded' && systemAvailable && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          The system is experiencing degraded performance. Assessments may take longer than usual.
        </Alert>
      )}

      {/* Assessment Stepper */}
      <AssessmentStepper onSubmit={handleSubmit} loading={submitting} />
    </Container>
  );
};

export default NewAssessmentPage;
