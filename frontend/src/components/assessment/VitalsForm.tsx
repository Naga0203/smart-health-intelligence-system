// ============================================================================
// Vitals Form Component
// Optional fields for vital signs
// ============================================================================

import React from 'react';
import {
  Box,
  TextField,
  Typography,
  InputAdornment,
} from '@mui/material';
import type { VitalsFormData } from './AssessmentStepper';

interface VitalsFormProps {
  data: VitalsFormData;
  onChange: (data: VitalsFormData) => void;
}

export const VitalsForm: React.FC<VitalsFormProps> = ({ data, onChange }) => {
  const handleChange = (field: keyof VitalsFormData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = e.target.value === '' ? undefined : parseFloat(e.target.value);
    onChange({ ...data, [field]: value });
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Vital Signs (Optional)
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Adding vital signs can improve assessment accuracy. All fields are optional.
      </Typography>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 3 }}>
        {/* Temperature */}
        <TextField
          label="Temperature"
          type="number"
          value={data.temperature || ''}
          onChange={handleChange('temperature')}
          InputProps={{
            endAdornment: <InputAdornment position="end">°F</InputAdornment>,
          }}
          inputProps={{
            min: 90,
            max: 110,
            step: 0.1,
          }}
          helperText="Normal: 97-99°F"
          fullWidth
        />

        {/* Heart Rate */}
        <TextField
          label="Heart Rate"
          type="number"
          value={data.heart_rate || ''}
          onChange={handleChange('heart_rate')}
          InputProps={{
            endAdornment: <InputAdornment position="end">bpm</InputAdornment>,
          }}
          inputProps={{
            min: 30,
            max: 250,
          }}
          helperText="Normal: 60-100 bpm"
          fullWidth
        />

        {/* Blood Pressure Systolic */}
        <TextField
          label="Blood Pressure (Systolic)"
          type="number"
          value={data.blood_pressure_systolic || ''}
          onChange={handleChange('blood_pressure_systolic')}
          InputProps={{
            endAdornment: <InputAdornment position="end">mmHg</InputAdornment>,
          }}
          inputProps={{
            min: 70,
            max: 250,
          }}
          helperText="Normal: 90-120 mmHg"
          fullWidth
        />

        {/* Blood Pressure Diastolic */}
        <TextField
          label="Blood Pressure (Diastolic)"
          type="number"
          value={data.blood_pressure_diastolic || ''}
          onChange={handleChange('blood_pressure_diastolic')}
          InputProps={{
            endAdornment: <InputAdornment position="end">mmHg</InputAdornment>,
          }}
          inputProps={{
            min: 40,
            max: 150,
          }}
          helperText="Normal: 60-80 mmHg"
          fullWidth
        />

        {/* Respiratory Rate */}
        <TextField
          label="Respiratory Rate"
          type="number"
          value={data.respiratory_rate || ''}
          onChange={handleChange('respiratory_rate')}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">breaths/min</InputAdornment>
            ),
          }}
          inputProps={{
            min: 8,
            max: 60,
          }}
          helperText="Normal: 12-20 breaths/min"
          fullWidth
        />
      </Box>
    </Box>
  );
};
