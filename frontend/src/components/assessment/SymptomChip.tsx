// ============================================================================
// Symptom Chip Component
// Displays a symptom with severity slider, duration input, and remove button
// ============================================================================

import React from 'react';
import {
  Box,
  Chip,
  Slider,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Typography,
  Paper,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

interface SymptomChipProps {
  symptom: string;
  severity: number;
  duration: {
    value: number;
    unit: 'hours' | 'days' | 'weeks' | 'months';
  };
  onSeverityChange: (severity: number) => void;
  onDurationChange: (duration: { value: number; unit: 'hours' | 'days' | 'weeks' | 'months' }) => void;
  onRemove: () => void;
}

export const SymptomChip: React.FC<SymptomChipProps> = ({
  symptom,
  severity,
  duration,
  onSeverityChange,
  onDurationChange,
  onRemove,
}) => {
  const handleDurationValueChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value > 0) {
      onDurationChange({ ...duration, value });
    }
  };

  const handleDurationUnitChange = (e: any) => {
    onDurationChange({ ...duration, unit: e.target.value });
  };

  return (
    <Paper
      elevation={1}
      sx={{
        p: 2,
        mb: 2,
        position: 'relative',
        borderRadius: 2,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          {symptom}
        </Typography>
        <IconButton
          size="small"
          onClick={onRemove}
          aria-label={`Remove ${symptom}`}
        >
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Severity Slider */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Severity: {severity}/10
        </Typography>
        <Slider
          value={severity}
          onChange={(_, value) => onSeverityChange(value as number)}
          min={1}
          max={10}
          step={1}
          marks
          valueLabelDisplay="auto"
          aria-label="Symptom severity"
        />
      </Box>

      {/* Duration Input */}
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
        <TextField
          type="number"
          label="Duration"
          value={duration.value}
          onChange={handleDurationValueChange}
          inputProps={{ min: 1 }}
          sx={{ width: 120 }}
          size="small"
        />
        <FormControl sx={{ minWidth: 120 }} size="small">
          <InputLabel>Unit</InputLabel>
          <Select
            value={duration.unit}
            onChange={handleDurationUnitChange}
            label="Unit"
          >
            <MenuItem value="hours">Hours</MenuItem>
            <MenuItem value="days">Days</MenuItem>
            <MenuItem value="weeks">Weeks</MenuItem>
            <MenuItem value="months">Months</MenuItem>
          </Select>
        </FormControl>
      </Box>
    </Paper>
  );
};
