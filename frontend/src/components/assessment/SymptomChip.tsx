// ============================================================================
// Symptom Chip Component - Responsive Design
// Displays a symptom with severity slider, duration input, and remove button
// Mobile-friendly with stacked layout and smooth animations
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
  Fade,
  useTheme,
  useMediaQuery,
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
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm')); // < 600px

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
    <Fade in={true} timeout={300}>
      <Paper
        elevation={1}
        sx={{
          p: { xs: 2, sm: 2.5 },
          mb: 2,
          position: 'relative',
          borderRadius: 2,
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            elevation: 3,
            boxShadow: theme.shadows[4],
            transform: 'translateY(-2px)',
          },
        }}
      >
        {/* Header with symptom name and remove button */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography
            variant="h6"
            sx={{
              flexGrow: 1,
              fontSize: { xs: '1rem', sm: '1.25rem' },
            }}
          >
            {symptom}
          </Typography>
          <IconButton
            size="small"
            onClick={onRemove}
            aria-label={`Remove ${symptom}`}
            sx={{
              // Ensure minimum touch target size on mobile
              minWidth: { xs: 44, sm: 40 },
              minHeight: { xs: 44, sm: 40 },
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: 'error.light',
                color: 'error.contrastText',
              },
            }}
          >
            <CloseIcon />
          </IconButton>
        </Box>

        {/* Severity Slider */}
        <Box sx={{ mb: 3 }}>
          <Typography
            variant="body2"
            color="text.secondary"
            gutterBottom
            sx={{ fontSize: { xs: '0.875rem', sm: '0.875rem' } }}
          >
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
            sx={{
              // Better touch target on mobile
              '& .MuiSlider-thumb': {
                width: { xs: 20, sm: 16 },
                height: { xs: 20, sm: 16 },
              },
              '& .MuiSlider-mark': {
                height: { xs: 8, sm: 6 },
              },
            }}
          />
        </Box>

        {/* Duration Input - Responsive Layout */}
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            gap: 2,
            alignItems: { xs: 'stretch', sm: 'center' },
          }}
        >
          <TextField
            type="number"
            label="Duration"
            value={duration.value}
            onChange={handleDurationValueChange}
            inputProps={{ min: 1 }}
            sx={{
              width: { xs: '100%', sm: 120 },
              // Ensure proper touch target height on mobile
              '& .MuiInputBase-root': {
                minHeight: { xs: 44, sm: 40 },
              },
            }}
            size={isMobile ? 'medium' : 'small'}
          />
          <FormControl
            sx={{
              minWidth: { xs: '100%', sm: 120 },
              // Ensure proper touch target height on mobile
              '& .MuiInputBase-root': {
                minHeight: { xs: 44, sm: 40 },
              },
            }}
            size={isMobile ? 'medium' : 'small'}
          >
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
    </Fade>
  );
};
