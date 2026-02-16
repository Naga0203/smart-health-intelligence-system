// ============================================================================
// New Assessment Page - Single Page Design
// Clean, modern interface matching HealthIntel AI design
// ============================================================================

import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Chip,
  Slider,
  LinearProgress,
  Paper,
  IconButton,
  InputAdornment,
  Alert,
  Fade,
} from '@mui/material';
import {
  AccessTime,
  Thermostat,
  CloudUpload,
  Lock,
  Mic,
  AutoAwesome,
} from '@mui/icons-material';

const COMMON_SYMPTOMS = ['Headache', 'Fever', 'Nausea', 'Fatigue'];

export const NewAssessmentPage: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Form state
  const [symptomDescription, setSymptomDescription] = useState('');
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [duration, setDuration] = useState('');
  const [temperature, setTemperature] = useState('');
  const [painSeverity, setPainSeverity] = useState(4);
  const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  // Calculate progress (for demo, based on filled fields)
  const calculateProgress = () => {
    let filled = 0;
    if (symptomDescription) filled += 1;
    if (selectedSymptoms.length > 0) filled += 1;
    if (duration || temperature || painSeverity !== 4) filled += 1;
    return Math.round((filled / 3) * 100);
  };

  // Toggle symptom chip
  // Toggle symptom chip and update description
  const toggleSymptom = (symptom: string) => {
    setSelectedSymptoms(prev => {
      const isSelected = prev.includes(symptom);

      // Update description text
      setSymptomDescription(current => {
        if (isSelected) {
          // Attempt to remove symptom text if present
          // This handles: ", symptom", "symptom, ", or just "symptom"
          let newDescription = current
            .replace(new RegExp(`(, )?${symptom}`, 'i'), '') // Try removing with leading comma
            .replace(new RegExp(`${symptom}(, )?`, 'i'), '') // Try removing with trailing comma
            .trim();

          // Clean up any double commas just in case
          newDescription = newDescription.replace(/, ,/g, ',');
          // Clean up leading/trailing commas
          return newDescription.replace(/^, /, '').replace(/, $/, '');
        } else {
          // Append to description
          const cleanCurrent = current.trim();
          // Avoid duplicates if user already typed it
          if (cleanCurrent.toLowerCase().includes(symptom.toLowerCase())) {
            return cleanCurrent;
          }
          return cleanCurrent ? `${cleanCurrent}, ${symptom}` : symptom;
        }
      });

      return isSelected
        ? prev.filter(s => s !== symptom)
        : [...prev, symptom];
    });
  };

  // Handle file upload
  const handleFiles = (files: FileList | null) => {
    if (!files) return;
    setAttachedFiles(prev => [...prev, ...Array.from(files)]);
  };

  // Drag handlers
  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  // Handle file browse
  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  // Reset form
  const handleReset = () => {
    setSymptomDescription('');
    setSelectedSymptoms([]);
    setDuration('');
    setTemperature('');
    setPainSeverity(4);
    setAttachedFiles([]);
  };

  // Submit form
  const handleSubmit = () => {
    // Here you would submit to backend
    console.log({
      symptomDescription,
      selectedSymptoms,
      duration,
      temperature,
      painSeverity,
      attachedFiles,
    });

    // Navigate to results
    // In a real app, this would be the ID returned from the backend
    // For demo purposes, we'll use a hardcoded ID or generate one
    const demoId = '12345';
    navigate(`/app/assessment/${demoId}`);
  };

  const progress = calculateProgress();

  return (
    <Fade in={true} timeout={500}>
      <Box sx={{ bgcolor: '#F9FAFB', minHeight: '100vh', pb: 8 }}>
        <Container
          maxWidth="md"
          sx={{
            py: { xs: 3, sm: 4, md: 5 },
            px: { xs: 2, sm: 3 },
          }}
        >
          {/* Progress Indicator */}
          <Box sx={{ mb: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography
                variant="caption"
                sx={{
                  fontWeight: 600,
                  color: 'text.secondary',
                  fontSize: '0.75rem',
                  letterSpacing: '0.05em',
                }}
              >
                STEP 1 OF 3: SYMPTOM REPORTING
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  fontWeight: 600,
                  color: 'text.secondary',
                  fontSize: '0.75rem',
                }}
              >
                {progress}% Completed
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 6,
                borderRadius: 1,
                bgcolor: '#E5E7EB',
                '& .MuiLinearProgress-bar': {
                  bgcolor: '#2563EB',
                  borderRadius: 1,
                }
              }}
            />
          </Box>

          {/* Main Title */}
          <Box sx={{ mb: 4 }}>
            <Typography
              variant="h3"
              sx={{
                fontSize: { xs: '2rem', sm: '2.5rem', md: '3rem' },
                fontWeight: 700,
                color: '#111827',
                mb: 1.5,
              }}
            >
              What brings you here today?
            </Typography>
            <Typography
              variant="body1"
              sx={{
                color: '#6B7280',
                fontSize: { xs: '0.875rem', sm: '1rem' },
              }}
            >
              Our AI system will analyze your input to suggest next steps. Please be as descriptive as possible.
            </Typography>
          </Box>

          {/* Symptom Description */}
          <Box sx={{ mb: 4 }}>
            <Typography
              variant="subtitle1"
              sx={{
                fontWeight: 600,
                color: '#111827',
                mb: 1.5,
                fontSize: { xs: '0.875rem', sm: '1rem' },
              }}
            >
              Symptom Description
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              value={symptomDescription}
              onChange={(e) => setSymptomDescription(e.target.value)}
              placeholder="Describe your symptoms here (e.g., I've had a throbbing headache and fever for 2 days...). Our AI will assist you."
              sx={{
                '& .MuiOutlinedInput-root': {
                  bgcolor: 'white',
                  borderRadius: 2,
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                  '& fieldset': {
                    borderColor: '#E5E7EB',
                  },
                  '&:hover fieldset': {
                    borderColor: '#D1D5DB',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#2563EB',
                  },
                },
                '& .MuiInputBase-input::placeholder': {
                  color: '#9CA3AF',
                  opacity: 1,
                },
              }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton size="small">
                      <Mic sx={{ color: '#9CA3AF' }} />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Box>

          {/* Common Suggestions */}
          <Box sx={{ mb: 4 }}>
            <Typography
              variant="caption"
              sx={{
                fontWeight: 600,
                color: '#6B7280',
                mb: 1.5,
                display: 'block',
                fontSize: '0.75rem',
              }}
            >
              Common Suggestions:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {COMMON_SYMPTOMS.map((symptom) => (
                <Chip
                  key={symptom}
                  label={symptom}
                  onClick={() => toggleSymptom(symptom)}
                  icon={<Box component="span" sx={{ fontSize: '1rem' }}>+</Box>}
                  sx={{
                    bgcolor: selectedSymptoms.includes(symptom) ? '#EEF2FF' : 'white',
                    border: '1px solid',
                    borderColor: selectedSymptoms.includes(symptom) ? '#2563EB' : '#E5E7EB',
                    color: selectedSymptoms.includes(symptom) ? '#2563EB' : '#6B7280',
                    fontWeight: 500,
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    px: 0.5,
                    transition: 'all 0.2s',
                    '&:hover': {
                      bgcolor: '#EEF2FF',
                      borderColor: '#2563EB',
                    },
                    '& .MuiChip-icon': {
                      color: 'inherit',
                      marginLeft: '8px',
                    },
                  }}
                />
              ))}
            </Box>
          </Box>

          {/* Additional Vitals */}
          <Box sx={{ mb: 4 }}>
            <Typography
              variant="subtitle1"
              sx={{
                fontWeight: 600,
                color: '#111827',
                mb: 2,
                fontSize: { xs: '0.875rem', sm: '1rem' },
              }}
            >
              Additional Vitals
            </Typography>

            <Box
              sx={{
                display: 'grid',
                gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' },
                gap: 2,
                mb: 3,
              }}
            >
              {/* Duration */}
              <Box>
                <Typography
                  variant="caption"
                  sx={{
                    fontWeight: 600,
                    color: '#6B7280',
                    mb: 1,
                    display: 'block',
                    fontSize: '0.75rem',
                  }}
                >
                  Duration
                </Typography>
                <TextField
                  fullWidth
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  placeholder="e.g. 2 days"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <AccessTime sx={{ color: '#9CA3AF', fontSize: 20 }} />
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      bgcolor: 'white',
                      borderRadius: 2,
                      fontSize: { xs: '0.875rem', sm: '0.875rem' },
                      '& fieldset': {
                        borderColor: '#E5E7EB',
                      },
                      '&:hover fieldset': {
                        borderColor: '#D1D5DB',
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: '#2563EB',
                      },
                    },
                  }}
                />
              </Box>

              {/* Temperature */}
              <Box>
                <Typography
                  variant="caption"
                  sx={{
                    fontWeight: 600,
                    color: '#6B7280',
                    mb: 1,
                    display: 'block',
                    fontSize: '0.75rem',
                  }}
                >
                  Temperature
                </Typography>
                <TextField
                  fullWidth
                  value={temperature}
                  onChange={(e) => setTemperature(e.target.value)}
                  placeholder="e.g. 38.5 C"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Thermostat sx={{ color: '#9CA3AF', fontSize: 20 }} />
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      bgcolor: 'white',
                      borderRadius: 2,
                      fontSize: { xs: '0.875rem', sm: '0.875rem' },
                      '& fieldset': {
                        borderColor: '#E5E7EB',
                      },
                      '&:hover fieldset': {
                        borderColor: '#D1D5DB',
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: '#2563EB',
                      },
                    },
                  }}
                />
              </Box>

              {/* Pain Severity */}
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography
                    variant="caption"
                    sx={{
                      fontWeight: 600,
                      color: '#6B7280',
                      fontSize: '0.75rem',
                    }}
                  >
                    Pain Severity
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      fontWeight: 600,
                      color: '#2563EB',
                      fontSize: '0.75rem',
                    }}
                  >
                    {painSeverity}/10
                  </Typography>
                </Box>
                <Slider
                  value={painSeverity}
                  onChange={(_, value) => setPainSeverity(value as number)}
                  min={0}
                  max={10}
                  step={1}
                  sx={{
                    color: '#2563EB',
                    '& .MuiSlider-thumb': {
                      width: 20,
                      height: 20,
                      bgcolor: '#2563EB',
                      border: '3px solid white',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                    },
                    '& .MuiSlider-track': {
                      bgcolor: '#2563EB',
                      border: 'none',
                    },
                    '& .MuiSlider-rail': {
                      bgcolor: '#E5E7EB',
                    },
                  }}
                />
              </Box>
            </Box>
          </Box>

          {/* Attachments */}
          <Box sx={{ mb: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
              <Typography
                variant="subtitle1"
                sx={{
                  fontWeight: 600,
                  color: '#111827',
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                }}
              >
                Attachments
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  color: '#9CA3AF',
                  fontSize: '0.75rem',
                }}
              >
                Optional: Images or PDF reports
              </Typography>
            </Box>

            <Paper
              onDragEnter={handleDragEnter}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={handleBrowseClick}
              sx={{
                border: '2px dashed',
                borderColor: isDragging ? '#2563EB' : '#E5E7EB',
                borderRadius: 2,
                bgcolor: isDragging ? '#EEF2FF' : 'white',
                p: { xs: 3, sm: 4 },
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': {
                  borderColor: '#2563EB',
                  bgcolor: '#F9FAFB',
                },
              }}
            >
              <Box
                sx={{
                  width: 48,
                  height: 48,
                  borderRadius: '50%',
                  bgcolor: '#EEF2FF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto',
                  mb: 1.5,
                }}
              >
                <CloudUpload sx={{ color: '#2563EB', fontSize: 24 }} />
              </Box>
              <Typography
                variant="body2"
                sx={{
                  fontWeight: 500,
                  color: '#111827',
                  mb: 0.5,
                  fontSize: { xs: '0.875rem', sm: '0.875rem' },
                }}
              >
                Click to upload or drag and drop
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  color: '#9CA3AF',
                  fontSize: '0.75rem',
                }}
              >
                SVG, PNG, JPG or GIF (max. 800x400px)
              </Typography>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*,.pdf"
                onChange={(e) => handleFiles(e.target.files)}
                style={{ display: 'none' }}
              />
            </Paper>

            {attachedFiles.length > 0 && (
              <Box sx={{ mt: 2 }}>
                {attachedFiles.map((file, index) => (
                  <Typography key={index} variant="caption" sx={{ display: 'block', color: '#6B7280' }}>
                    {file.name}
                  </Typography>
                ))}
              </Box>
            )}
          </Box>

          {/* AI Ready Alert */}
          <Alert
            icon={<AutoAwesome sx={{ color: '#2563EB' }} />}
            sx={{
              mb: 4,
              bgcolor: '#EEF2FF',
              border: '1px solid #DBEAFE',
              borderRadius: 2,
              '& .MuiAlert-message': {
                color: '#1E40AF',
              },
            }}
          >
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5, fontSize: '0.875rem' }}>
              AI Ready to Analyze
            </Typography>
            <Typography variant="caption" sx={{ fontSize: '0.75rem' }}>
              Once you submit, our health intelligence engine will cross-reference your symptoms with over 10,000 medical profiles to suggest the next steps.
            </Typography>
          </Alert>

          {/* Security Notice & Actions */}
          <Box
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', sm: 'row' },
              justifyContent: 'space-between',
              alignItems: { xs: 'stretch', sm: 'center' },
              gap: 2,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Lock sx={{ color: '#9CA3AF', fontSize: 16 }} />
              <Typography
                variant="caption"
                sx={{
                  color: '#6B7280',
                  fontSize: '0.75rem',
                }}
              >
                Your health data is end-to-end encrypted.
              </Typography>
            </Box>

            <Box
              sx={{
                display: 'flex',
                gap: 2,
                flexDirection: { xs: 'column', sm: 'row' },
              }}
            >
              <Button
                variant="outlined"
                onClick={handleReset}
                sx={{
                  minHeight: { xs: 44, sm: 40 },
                  minWidth: { sm: 120 },
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 600,
                  fontSize: { xs: '0.875rem', sm: '0.875rem' },
                  borderColor: '#E5E7EB',
                  color: '#6B7280',
                  '&:hover': {
                    borderColor: '#D1D5DB',
                    bgcolor: '#F9FAFB',
                  },
                }}
              >
                Reset Form
              </Button>

              <Button
                variant="contained"
                onClick={handleSubmit}
                disabled={!symptomDescription}
                endIcon={<Box component="span" sx={{ fontSize: '1.2rem' }}>→</Box>}
                sx={{
                  minHeight: { xs: 44, sm: 40 },
                  minWidth: { sm: 160 },
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 600,
                  fontSize: { xs: '0.875rem', sm: '0.875rem' },
                  bgcolor: '#2563EB',
                  boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
                  '&:hover': {
                    bgcolor: '#1D4ED8',
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                  },
                  '&:disabled': {
                    bgcolor: '#E5E7EB',
                    color: '#9CA3AF',
                  },
                }}
              >
                Submit Symptoms
              </Button>
            </Box>
          </Box>
        </Container>
      </Box>
    </Fade>
  );
};

export default NewAssessmentPage;
