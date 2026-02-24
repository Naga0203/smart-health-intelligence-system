// ============================================================================
// Vitals Form Component - Responsive Design
// Collects optional vital signs measurements
// Mobile-friendly with adaptive grid layout
// Supports visual indicators for extracted data
// ============================================================================

import React from 'react';
import {
  Box,
  TextField,
  Typography,
  Grid,
  useTheme,
  useMediaQuery,
  Chip,
  InputAdornment,
} from '@mui/material';
import { Description as DocumentIcon } from '@mui/icons-material';
import type { VitalsFormData } from './AssessmentStepper';

interface VitalsFormProps {
  data: VitalsFormData;
  onChange: (data: VitalsFormData) => void;
  isFieldExtracted?: (fieldName: string) => boolean;
}

export const VitalsForm: React.FC<VitalsFormProps> = ({ data, onChange, isFieldExtracted }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm')); // < 600px

  const handleChange = (field: keyof VitalsFormData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = parseFloat(e.target.value);
    if (!isNaN(value) && value > 0) {
      onChange({ ...data, [field]: value });
    } else if (e.target.value === '') {
      const updated = { ...data };
      delete updated[field];
      onChange(updated);
    }
  };

  const getFieldIndicator = (fieldName: string, testId?: string) => {
    if (isFieldExtracted && isFieldExtracted(fieldName)) {
      return (
        <InputAdornment position="end">
          <Chip
            data-testid={testId}
            icon={<DocumentIcon sx={{ fontSize: '0.875rem' }} />}
            label="From Report"
            size="small"
            color="primary"
            variant="outlined"
            sx={{
              height: 24,
              fontSize: '0.75rem',
              '& .MuiChip-icon': {
                marginLeft: '4px',
              },
            }}
          />
        </InputAdornment>
      );
    }
    return null;
  };

  return (
    <Box>
      <Typography
        variant="h6"
        gutterBottom
        sx={{ fontSize: { xs: '1.125rem', sm: '1.25rem' } }}
      >
        Vital Signs (Optional)
      </Typography>
      <Typography
        variant="body2"
        color="text.secondary"
        sx={{ mb: { xs: 2, sm: 3 } }}
      >
        If available, adding vital signs can improve assessment accuracy. All
        fields are optional.
      </Typography>

      <Grid container spacing={{ xs: 2, sm: 2.5, md: 3 }}>
        {/* Temperature */}
        <Grid item xs={12} sm={6}>
          <TextField
            label="Temperature (°F)"
            type="number"
            value={data.temperature || ''}
            onChange={handleChange('temperature')}
            inputProps={{ 
              min: 90, 
              max: 110, 
              step: 0.1,
              'data-testid': 'temperature-input'
            }}
            helperText="Normal: 97.0-99.0°F"
            fullWidth
            sx={{
              '& .MuiInputBase-root': {
                minHeight: { xs: 44, sm: 40 },
              },
            }}
            size={isMobile ? 'medium' : 'medium'}
            InputProps={{
              endAdornment: getFieldIndicator('vitals_temperature', 'temp-extracted'),
            }}
          />
        </Grid>

        {/* Heart Rate */}
        <Grid item xs={12} sm={6}>
          <TextField
            label="Heart Rate (bpm)"
            type="number"
            value={data.heart_rate || ''}
            onChange={handleChange('heart_rate')}
            inputProps={{ 
              min: 30, 
              max: 200,
              'data-testid': 'heart-rate-input'
            }}
            helperText="Normal: 60-100 bpm"
            fullWidth
            sx={{
              '& .MuiInputBase-root': {
                minHeight: { xs: 44, sm: 40 },
              },
            }}
            size={isMobile ? 'medium' : 'medium'}
            InputProps={{
              endAdornment: getFieldIndicator('vitals_heart_rate', 'hr-extracted'),
            }}
          />
        </Grid>

        {/* Blood Pressure Systolic */}
        <Grid item xs={12} sm={6}>
          <TextField
            label="Blood Pressure (Systolic)"
            type="number"
            value={data.blood_pressure_systolic || ''}
            onChange={handleChange('blood_pressure_systolic')}
            inputProps={{ 
              min: 70, 
              max: 200,
              'data-testid': 'bp-systolic-input'
            }}
            helperText="Normal: 90-120 mmHg"
            fullWidth
            sx={{
              '& .MuiInputBase-root': {
                minHeight: { xs: 44, sm: 40 },
              },
            }}
            size={isMobile ? 'medium' : 'medium'}
            InputProps={{
              endAdornment: getFieldIndicator('vitals_blood_pressure_systolic', 'bp-sys-extracted'),
            }}
          />
        </Grid>

        {/* Blood Pressure Diastolic */}
        <Grid item xs={12} sm={6}>
          <TextField
            label="Blood Pressure (Diastolic)"
            type="number"
            value={data.blood_pressure_diastolic || ''}
            onChange={handleChange('blood_pressure_diastolic')}
            inputProps={{ 
              min: 40, 
              max: 130,
              'data-testid': 'bp-diastolic-input'
            }}
            helperText="Normal: 60-80 mmHg"
            fullWidth
            sx={{
              '& .MuiInputBase-root': {
                minHeight: { xs: 44, sm: 40 },
              },
            }}
            size={isMobile ? 'medium' : 'medium'}
            InputProps={{
              endAdornment: getFieldIndicator('vitals_blood_pressure_diastolic', 'bp-dia-extracted'),
            }}
          />
        </Grid>

        {/* Respiratory Rate */}
        <Grid item xs={12} sm={6}>
          <TextField
            label="Respiratory Rate (breaths/min)"
            type="number"
            value={data.respiratory_rate || ''}
            onChange={handleChange('respiratory_rate')}
            inputProps={{ min: 8, max: 40 }}
            helperText="Normal: 12-20 breaths/min"
            fullWidth
            sx={{
              '& .MuiInputBase-root': {
                minHeight: { xs: 44, sm: 40 },
              },
            }}
            size={isMobile ? 'medium' : 'medium'}
          />
        </Grid>
      </Grid>
    </Box>
  );
};
