// ============================================================================
// Demographic Form Component - Responsive Design
// Collects age, gender, and medical history
// Mobile-friendly with proper touch targets
// ============================================================================

import React from 'react';
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Chip,
  Autocomplete,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import type { DemographicFormData } from './AssessmentStepper';

// Common medical conditions for autocomplete
const COMMON_CONDITIONS = [
  'Diabetes',
  'Hypertension',
  'Asthma',
  'Heart Disease',
  'Kidney Disease',
  'Liver Disease',
  'Cancer',
  'Arthritis',
  'Thyroid Disorder',
  'High Cholesterol',
  'Obesity',
  'Depression',
  'Anxiety',
  'COPD',
  'Stroke',
  'Epilepsy',
  'Migraine',
  'Allergies',
  'Anemia',
  'Osteoporosis',
];

interface DemographicFormProps {
  data: DemographicFormData;
  onChange: (data: DemographicFormData) => void;
}

export const DemographicForm: React.FC<DemographicFormProps> = ({
  data,
  onChange,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm')); // < 600px

  const handleAgeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const age = parseInt(e.target.value, 10);
    if (!isNaN(age) && age > 0 && age <= 150) {
      onChange({ ...data, age });
    } else if (e.target.value === '') {
      onChange({ ...data, age: 0 });
    }
  };

  const handleGenderChange = (e: any) => {
    onChange({ ...data, gender: e.target.value });
  };

  const handleMedicalHistoryChange = (
    _: any,
    value: string[]
  ) => {
    onChange({ ...data, medical_history: value });
  };

  return (
    <Box>
      <Typography
        variant="h6"
        gutterBottom
        sx={{ fontSize: { xs: '1.125rem', sm: '1.25rem' } }}
      >
        Demographic Information
      </Typography>
      <Typography
        variant="body2"
        color="text.secondary"
        sx={{ mb: { xs: 2, sm: 3 } }}
      >
        This information helps provide more accurate risk assessments.
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: { xs: 2.5, sm: 3 } }} data-testid="demographic-form">
        {/* Age */}
        <TextField
          label="Age"
          type="number"
          value={data.age || ''}
          onChange={handleAgeChange}
          required
          inputProps={{ 
            min: 1, 
            max: 150,
            'data-testid': 'age-input'
          }}
          helperText="Enter your age in years"
          fullWidth
          sx={{
            '& .MuiInputBase-root': {
              minHeight: { xs: 44, sm: 40 },
            },
          }}
          size={isMobile ? 'medium' : 'medium'}
        />

        {/* Gender */}
        <FormControl
          fullWidth
          required
          sx={{
            '& .MuiInputBase-root': {
              minHeight: { xs: 44, sm: 40 },
            },
          }}
          size={isMobile ? 'medium' : 'medium'}
        >
          <InputLabel>Gender</InputLabel>
          <Select
            value={data.gender}
            onChange={handleGenderChange}
            label="Gender"
            inputProps={{
              'data-testid': 'gender-select'
            }}
          >
            <MenuItem value="male">Male</MenuItem>
            <MenuItem value="female">Female</MenuItem>
            <MenuItem value="other">Other</MenuItem>
          </Select>
        </FormControl>

        {/* Medical History */}
        <Autocomplete
          multiple
          freeSolo
          options={COMMON_CONDITIONS}
          value={data.medical_history}
          onChange={handleMedicalHistoryChange}
          renderTags={(value, getTagProps) =>
            value.map((option, index) => (
              <Chip
                label={option}
                {...getTagProps({ index })}
                key={index}
                sx={{
                  // Ensure chips are touch-friendly
                  minHeight: { xs: 32, sm: 28 },
                }}
              />
            ))
          }
          renderInput={(params) => (
            <TextField
              {...params}
              label="Medical History"
              placeholder="Add conditions"
              helperText="Select or type existing medical conditions (optional)"
              sx={{
                '& .MuiInputBase-root': {
                  minHeight: { xs: 44, sm: 40 },
                },
              }}
            />
          )}
        />
      </Box>
    </Box>
  );
};
