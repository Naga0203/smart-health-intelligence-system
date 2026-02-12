// ============================================================================
// Demographic Form Component
// Collects age, gender, and medical history
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
      <Typography variant="h6" gutterBottom>
        Demographic Information
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        This information helps provide more accurate risk assessments.
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* Age */}
        <TextField
          label="Age"
          type="number"
          value={data.age || ''}
          onChange={handleAgeChange}
          required
          inputProps={{ min: 1, max: 150 }}
          helperText="Enter your age in years"
          fullWidth
        />

        {/* Gender */}
        <FormControl fullWidth required>
          <InputLabel>Gender</InputLabel>
          <Select
            value={data.gender}
            onChange={handleGenderChange}
            label="Gender"
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
              />
            ))
          }
          renderInput={(params) => (
            <TextField
              {...params}
              label="Medical History"
              placeholder="Add conditions"
              helperText="Select or type existing medical conditions (optional)"
            />
          )}
        />
      </Box>
    </Box>
  );
};
