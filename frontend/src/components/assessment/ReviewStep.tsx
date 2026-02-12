// ============================================================================
// Review Step Component
// Displays all entered data for review before submission
// ============================================================================

import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Divider,
  Chip,
} from '@mui/material';
import type { AssessmentFormData } from './AssessmentStepper';

interface ReviewStepProps {
  data: AssessmentFormData;
}

export const ReviewStep: React.FC<ReviewStepProps> = ({ data }) => {
  const hasVitals = Object.keys(data.vitals).length > 0;

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Review Your Assessment
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Please review all information before submitting. You can go back to make changes.
      </Typography>

      {/* Symptoms Section */}
      <Paper elevation={0} sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}>
        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
          Symptoms ({data.symptoms.length})
        </Typography>
        <Divider sx={{ mb: 2 }} />
        {data.symptoms.map((symptom, index) => (
          <Box key={index} sx={{ mb: 2 }}>
            <Typography variant="body1" fontWeight="medium">
              {symptom.name}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
              <Chip
                label={`Severity: ${symptom.severity}/10`}
                size="small"
                color="primary"
                variant="outlined"
              />
              <Chip
                label={`Duration: ${symptom.duration.value} ${symptom.duration.unit}`}
                size="small"
                color="secondary"
                variant="outlined"
              />
            </Box>
          </Box>
        ))}
      </Paper>

      {/* Demographics Section */}
      <Paper elevation={0} sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}>
        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
          Demographics
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Age
            </Typography>
            <Typography variant="body1">{data.demographics.age} years</Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Gender
            </Typography>
            <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>
              {data.demographics.gender}
            </Typography>
          </Box>
        </Box>
        {data.demographics.medical_history.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Medical History
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {data.demographics.medical_history.map((condition, index) => (
                <Chip key={index} label={condition} size="small" />
              ))}
            </Box>
          </Box>
        )}
      </Paper>

      {/* Vitals Section */}
      {hasVitals && (
        <Paper elevation={0} sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            Vital Signs
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr 1fr', sm: '1fr 1fr 1fr' }, gap: 2 }}>
            {data.vitals.temperature && (
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Temperature
                </Typography>
                <Typography variant="body1">
                  {data.vitals.temperature}°F
                </Typography>
              </Box>
            )}
            {data.vitals.heart_rate && (
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Heart Rate
                </Typography>
                <Typography variant="body1">
                  {data.vitals.heart_rate} bpm
                </Typography>
              </Box>
            )}
            {data.vitals.blood_pressure_systolic && (
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Blood Pressure
                </Typography>
                <Typography variant="body1">
                  {data.vitals.blood_pressure_systolic}/
                  {data.vitals.blood_pressure_diastolic || '—'} mmHg
                </Typography>
              </Box>
            )}
            {data.vitals.respiratory_rate && (
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Respiratory Rate
                </Typography>
                <Typography variant="body1">
                  {data.vitals.respiratory_rate} breaths/min
                </Typography>
              </Box>
            )}
          </Box>
        </Paper>
      )}

      {/* Disclaimer */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
          bgcolor: 'warning.light',
          border: '1px solid',
          borderColor: 'warning.main',
        }}
      >
        <Typography variant="body2" fontWeight="medium">
          Important: This assessment is not a medical diagnosis. Always consult with a healthcare professional for medical advice.
        </Typography>
      </Paper>
    </Box>
  );
};
