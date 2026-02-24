// ============================================================================
// New Assessment Page - Single Page Design
// Clean, modern interface matching HealthIntel AI design
// ============================================================================

import React, { useState } from 'react';
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
  IconButton,
  InputAdornment,
  Alert,
  Fade,
  ToggleButton,
  ToggleButtonGroup,
  Divider,
} from '@mui/material';
import {
  AccessTime,
  Thermostat,
  Lock,
  Mic,
  AutoAwesome,
  Edit,
  Description,
} from '@mui/icons-material';
import { FileUploadComponent } from '@/components/FileUploadComponent';
import { ExtractedMedicalData, UploadError } from '@/types/medicalReport';

const COMMON_SYMPTOMS = ['Headache', 'Fever', 'Nausea', 'Fatigue'];

export const NewAssessmentPage: React.FC = () => {
  const navigate = useNavigate();

  // Check if report upload feature is enabled
  const isReportUploadEnabled = import.meta.env.VITE_ENABLE_REPORT_UPLOAD === 'true';

  // Entry mode: 'upload' or 'manual'
  const [entryMode, setEntryMode] = useState<'upload' | 'manual'>(
    isReportUploadEnabled ? 'upload' : 'manual'
  );

  // Form state
  const [symptomDescription, setSymptomDescription] = useState('');
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [duration, setDuration] = useState('');
  const [temperature, setTemperature] = useState('');
  const [painSeverity, setPainSeverity] = useState(4);

  // Extracted data state
  const [extractedData, setExtractedData] = useState<ExtractedMedicalData | null>(null);
  const [extractionJobId, setExtractionJobId] = useState<string | null>(null);
  const [reportMetadata, setReportMetadata] = useState<{
    reportId: string;
    fileName: string;
    fileSize: number;
    uploadTimestamp: string;
  } | null>(null);
  const [uploadError, setUploadError] = useState<UploadError | null>(null);

  // Track data sources for each field (manual vs extracted)
  const [dataSources, setDataSources] = useState<Map<string, 'manual' | 'extracted'>>(new Map());

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Get user ID from auth context or localStorage
  // For now, using a placeholder - should be replaced with actual auth
  const userId = 'user-123'; // TODO: Get from auth context

  // Calculate progress (for demo, based on filled fields)
  const calculateProgress = () => {
    let filled = 0;
    if (symptomDescription) filled += 1;
    if (selectedSymptoms.length > 0) filled += 1;
    if (duration || temperature || painSeverity !== 4) filled += 1;
    return Math.round((filled / 3) * 100);
  };

  /**
   * Handle successful upload and extraction
   */
  const handleUploadComplete = (
    data: ExtractedMedicalData,
    jobId: string,
    metadata: {
      reportId: string;
      fileName: string;
      fileSize: number;
      uploadTimestamp: string;
    }
  ) => {
    setExtractedData(data);
    setExtractionJobId(jobId);
    setReportMetadata(metadata);
    setUploadError(null);

    // Populate form with extracted data and track sources
    populateFormFromExtractedData(data);
  };

  /**
   * Handle upload error
   */
  const handleUploadError = (error: UploadError) => {
    setUploadError(error);
    setExtractedData(null);
    setExtractionJobId(null);
  };

  /**
   * Populate form fields from extracted data
   */
  const populateFormFromExtractedData = (data: ExtractedMedicalData) => {
    const newDataSources = new Map<string, 'manual' | 'extracted'>();

    // Populate symptoms
    if (data.symptoms && data.symptoms.length > 0) {
      const symptomsText = data.symptoms.join(', ');
      setSymptomDescription(symptomsText);
      newDataSources.set('symptomDescription', 'extracted');

      // Select matching common symptoms
      const matchingSymptoms = COMMON_SYMPTOMS.filter(symptom =>
        symptomsText.toLowerCase().includes(symptom.toLowerCase())
      );
      setSelectedSymptoms(matchingSymptoms);
      if (matchingSymptoms.length > 0) {
        newDataSources.set('selectedSymptoms', 'extracted');
      }
    }

    // Populate vitals
    if (data.vitals) {
      if (data.vitals.temperature) {
        setTemperature(`${data.vitals.temperature} °C`);
        newDataSources.set('temperature', 'extracted');
      }
      // Note: Duration is not in vitals, would need to be extracted from report context
    }

    // Update data sources
    setDataSources(newDataSources);

    // Note: Pain severity is subjective and typically not in reports
    // Lab results, medications, and diagnoses would be displayed separately
    // in a more comprehensive form (future enhancement)
  };

  /**
   * Handle entry mode change
   */
  const handleEntryModeChange = (
    _event: React.MouseEvent<HTMLElement>,
    newMode: 'upload' | 'manual' | null,
  ) => {
    if (newMode !== null) {
      setEntryMode(newMode);
      // Clear upload-related state when switching to manual
      if (newMode === 'manual') {
        setUploadError(null);
      }
    }
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



  // Reset form
  const handleReset = () => {
    setDuration('');
    setTemperature('');
    setPainSeverity(4);
    setSubmitError(null);
    setExtractedData(null);
    setExtractionJobId(null);
    setReportMetadata(null);
    setDataSources(new Map());
  };

  // Submit form
  const handleSubmit = async () => {
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      // Combine description and selected symptoms
      const symptomsInput = [
        symptomDescription,
        ...selectedSymptoms
      ].filter(Boolean).join(', ');

      if (!symptomsInput) {
        setSubmitError('Please describe your symptoms or select from the list.');
        setIsSubmitting(false);
        return;
      }

      console.log('Submitting symptoms:', symptomsInput);

      // Prepare report metadata if available
      const reportMetadataPayload = reportMetadata && extractionJobId ? {
        reportId: reportMetadata.reportId,
        extractionJobId: extractionJobId,
        hasExtractedData: extractedData !== null,
      } : undefined;

      // Convert data sources Map to plain object
      const dataSourcesObject: Record<string, 'manual' | 'extracted'> = {};
      dataSources.forEach((value, key) => {
        dataSourcesObject[key] = value;
      });

      // Call API with report data
      const response = await import('@/services/api').then(m =>
        m.apiService.predict(
          symptomsInput,
          reportMetadataPayload,
          extractedData,
          Object.keys(dataSourcesObject).length > 0 ? dataSourcesObject : undefined,
          30, // Default age (should come from form/profile)
          'male', // Default gender (should come from form/profile)
          {
            duration,
            temperature: temperature ? parseFloat(temperature.replace(/[^\d.]/g, '')) : undefined,
            pain_severity: painSeverity
          }
        )
      );

      console.log('Prediction Response:', response);

      // Navigate to results
      // Assuming response contains assessment_id or we use a temporary ID for now
      // For now, we'll use a placeholder or response ID if available
      const assessmentId = response.assessment_id || 'new';

      // Store result in state/store if needed, or pass via state
      navigate(`/app/assessment/${assessmentId}`, { state: { result: response } });

    } catch (error: any) {
      console.error('Prediction failed:', error);
      const errorMessage = error.response?.data?.message || error.message || 'Failed to submit symptoms. Please try again.';
      setSubmitError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
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

          {/* Entry Mode Toggle - Only show if report upload is enabled */}
          {isReportUploadEnabled && (
            <Box sx={{ mb: 4 }}>
              <ToggleButtonGroup
                value={entryMode}
                exclusive
                onChange={handleEntryModeChange}
                aria-label="entry mode"
                fullWidth
                sx={{
                  bgcolor: 'white',
                  borderRadius: 2,
                  '& .MuiToggleButton-root': {
                    py: 1.5,
                    textTransform: 'none',
                    fontWeight: 600,
                    fontSize: { xs: '0.875rem', sm: '1rem' },
                    border: '1px solid #E5E7EB',
                    color: '#6B7280',
                    '&.Mui-selected': {
                      bgcolor: '#EEF2FF',
                      color: '#2563EB',
                      borderColor: '#2563EB',
                      '&:hover': {
                        bgcolor: '#DBEAFE',
                      },
                    },
                    '&:hover': {
                      bgcolor: '#F9FAFB',
                    },
                  },
                }}
              >
                <ToggleButton value="upload" aria-label="upload report">
                  <Description sx={{ mr: 1, fontSize: 20 }} />
                  Upload Medical Report
                </ToggleButton>
                <ToggleButton value="manual" aria-label="manual entry">
                  <Edit sx={{ mr: 1, fontSize: 20 }} />
                  Manual Entry
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>
          )}

          {/* File Upload Section - Only show if feature is enabled and mode is upload */}
          {isReportUploadEnabled && entryMode === 'upload' && (
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
                Upload Medical Report
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  color: '#6B7280',
                  mb: 2,
                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                }}
              >
                Upload a PDF, JPG, or PNG file (max 10MB). Our AI will extract medical information and pre-fill the form below.
              </Typography>

              <FileUploadComponent
                onUploadComplete={handleUploadComplete}
                onUploadError={handleUploadError}
                userId={userId}
                maxFileSizeMB={10}
                acceptedFormats={['.pdf', '.jpg', '.jpeg', '.png']}
              />

              {/* Show divider after successful upload */}
              {extractedData && (
                <Box sx={{ mt: 4, mb: 4 }}>
                  <Divider>
                    <Chip
                      label="Extracted Data - Review and Edit Below"
                      sx={{
                        bgcolor: '#EEF2FF',
                        color: '#2563EB',
                        fontWeight: 600,
                        fontSize: '0.75rem',
                      }}
                    />
                  </Divider>
                </Box>
              )}
            </Box>
          )}

          {submitError && (
            <Alert severity="error" sx={{ mb: 4 }} onClose={() => setSubmitError(null)}>
              {submitError}
            </Alert>
          )}

          {/* Upload Error with Manual Entry Fallback */}
          {uploadError && entryMode === 'upload' && (
            <Alert
              severity="warning"
              sx={{ mb: 4 }}
              action={
                <Button
                  color="inherit"
                  size="small"
                  onClick={() => setEntryMode('manual')}
                >
                  Switch to Manual Entry
                </Button>
              }
            >
              <Typography variant="body2" fontWeight="medium">
                Report extraction failed: {uploadError.message}
              </Typography>
              <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                You can switch to manual entry to continue with your assessment.
              </Typography>
            </Alert>
          )}

          {/* Symptom Description */}
          <Box sx={{ mb: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
              <Typography
                variant="subtitle1"
                sx={{
                  fontWeight: 600,
                  color: '#111827',
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                }}
              >
                Symptom Description
              </Typography>
              {extractedData && symptomDescription && (
                <Chip
                  label="Auto-filled from report"
                  size="small"
                  icon={<AutoAwesome sx={{ fontSize: 14 }} />}
                  sx={{
                    ml: 1.5,
                    height: 24,
                    bgcolor: '#ECFDF5',
                    color: '#059669',
                    fontSize: '0.7rem',
                    fontWeight: 600,
                    '& .MuiChip-icon': {
                      color: '#059669',
                    },
                  }}
                />
              )}
            </Box>
            <TextField
              fullWidth
              multiline
              rows={4}
              value={symptomDescription}
              onChange={(e) => {
                setSymptomDescription(e.target.value);
                // Mark as manual if user edits after extraction
                if (dataSources.get('symptomDescription') === 'extracted') {
                  setDataSources(prev => new Map(prev).set('symptomDescription', 'manual'));
                }
              }}
              placeholder="Describe your symptoms here (e.g., I've had a throbbing headache and fever for 2 days...). Our AI will assist you."
              sx={{
                '& .MuiOutlinedInput-root': {
                  bgcolor: extractedData && symptomDescription ? '#F0FDF4' : 'white',
                  borderRadius: 2,
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                  '& fieldset': {
                    borderColor: extractedData && symptomDescription ? '#86EFAC' : '#E5E7EB',
                  },
                  '&:hover fieldset': {
                    borderColor: extractedData && symptomDescription ? '#4ADE80' : '#D1D5DB',
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
                  onChange={(e) => {
                    setDuration(e.target.value);
                    // Mark as manual when user enters data
                    if (e.target.value) {
                      setDataSources(prev => new Map(prev).set('duration', 'manual'));
                    }
                  }}
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
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Typography
                    variant="caption"
                    sx={{
                      fontWeight: 600,
                      color: '#6B7280',
                      fontSize: '0.75rem',
                    }}
                  >
                    Temperature
                  </Typography>
                  {extractedData && temperature && (
                    <Chip
                      label="Auto-filled"
                      size="small"
                      icon={<AutoAwesome sx={{ fontSize: 10 }} />}
                      sx={{
                        ml: 1,
                        height: 18,
                        bgcolor: '#ECFDF5',
                        color: '#059669',
                        fontSize: '0.65rem',
                        fontWeight: 600,
                        '& .MuiChip-icon': {
                          color: '#059669',
                          marginLeft: '4px',
                        },
                        '& .MuiChip-label': {
                          px: 0.5,
                        },
                      }}
                    />
                  )}
                </Box>
                <TextField
                  fullWidth
                  value={temperature}
                  onChange={(e) => {
                    setTemperature(e.target.value);
                    // Mark as manual if user edits after extraction
                    if (dataSources.get('temperature') === 'extracted') {
                      setDataSources(prev => new Map(prev).set('temperature', 'manual'));
                    } else if (e.target.value) {
                      setDataSources(prev => new Map(prev).set('temperature', 'manual'));
                    }
                  }}
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
                      bgcolor: extractedData && temperature ? '#F0FDF4' : 'white',
                      borderRadius: 2,
                      fontSize: { xs: '0.875rem', sm: '0.875rem' },
                      '& fieldset': {
                        borderColor: extractedData && temperature ? '#86EFAC' : '#E5E7EB',
                      },
                      '&:hover fieldset': {
                        borderColor: extractedData && temperature ? '#4ADE80' : '#D1D5DB',
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
                  onChange={(_, value) => {
                    setPainSeverity(value as number);
                    // Mark as manual when user changes from default
                    if (value !== 4) {
                      setDataSources(prev => new Map(prev).set('painSeverity', 'manual'));
                    }
                  }}
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
                disabled={isSubmitting}
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
                disabled={!symptomDescription || isSubmitting}
                endIcon={!isSubmitting && <Box component="span" sx={{ fontSize: '1.2rem' }}>→</Box>}
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
                {isSubmitting ? 'Analyzing...' : 'Submit Symptoms'}
              </Button>
            </Box>
          </Box>
        </Container>
      </Box>
    </Fade>
  );
};

export default NewAssessmentPage;
