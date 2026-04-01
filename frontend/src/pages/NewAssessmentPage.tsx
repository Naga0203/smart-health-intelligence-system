// ============================================================================
// New Assessment Page - Single Page Design
// Clean, modern interface matching HealthIntel AI design
// ============================================================================

import React, { useState, useEffect } from 'react';
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
  CircularProgress,
  IconButton,
  InputAdornment,
  Alert,
  Fade,
  Divider,
  Card,
  CardActionArea,
} from '@mui/material';
import {
  AccessTime,
  Thermostat,
  Lock,
  Mic,
  AutoAwesome,
  Edit,
  Description,
  CheckCircle,
  ErrorOutline,
} from '@mui/icons-material';
import { useAuthStore } from '@/stores/authStore';
import { useUserStore } from '@/stores/userStore';
import { FileUploadComponent } from '@/components/FileUploadComponent';
import { ExtractedMedicalData, UploadError } from '@/types/medicalReport';
import { geminiAI } from '@/services/geminiService';
import { firebaseService } from '@/services/firebase';
import { apiService } from '@/services/api';

const COMMON_SYMPTOMS = ['Headache', 'Fever', 'Nausea', 'Fatigue'];

type AssessmentStage = 'IDLE' | 'PREDICTING' | 'ANALYZING' | 'SAVING' | 'COMPLETE' | 'ERROR';

export const NewAssessmentPage: React.FC = () => {
  const navigate = useNavigate();

  // Entry mode: 'upload' or 'manual'
  const [entryMode, setEntryMode] = useState<'upload' | 'manual'>('upload');

  // Form state
  const [symptomDescription, setSymptomDescription] = useState('');
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [duration, setDuration] = useState('');
  const [temperature, setTemperature] = useState('');
  const [painSeverity, setPainSeverity] = useState(4);

  // Extracted data state
  const [extractedData, setExtractedData] = useState<ExtractedMedicalData | null>(null);
  const [reportMetadata, setReportMetadata] = useState<{
    reportId: string;
    fileName: string;
    fileSize: number;
    uploadTimestamp: string;
  } | null>(null);
  const [uploadError, setUploadError] = useState<UploadError | null>(null);

  // Track data sources for each field (manual vs extracted)
  const [dataSources, setDataSources] = useState<Map<string, 'manual' | 'extracted'>>(new Map());

  // Pipeline Stage
  const [stage, setStage] = useState<AssessmentStage>('IDLE');
  const [pipelineProgress, setPipelineProgress] = useState(0);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { user } = useAuthStore();
  const { profile, fetchProfile } = useUserStore();
  const userId = user?.uid || 'anonymous';

  // Load profile so age/gender are available for the predict call
  useEffect(() => {
    if (user && !profile) fetchProfile().catch(() => {});
  }, [user]);

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
    _jobId: string,
    metadata: {
      reportId: string;
      fileName: string;
      fileSize: number;
      uploadTimestamp: string;
    }
  ) => {
    setExtractedData(data);
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
    setReportMetadata(null);
    setDataSources(new Map());
    setStage('IDLE');
    setPipelineProgress(0);
  };

  // Submit form
  const handleSubmit = async () => {
    setStage('PREDICTING');
    setPipelineProgress(10);
    setSubmitError(null);

    try {
      // 1. Prepare symptoms
      const symptomsArray: string[] = [];
      if (symptomDescription.trim()) {
        symptomsArray.push(...symptomDescription.split(',').map(s => s.trim()).filter(Boolean));
      }
      symptomsArray.push(...selectedSymptoms);
      const uniqueSymptoms = Array.from(new Set(symptomsArray.map(s => s.toLowerCase())))
        .map(s => symptomsArray.find(orig => orig.toLowerCase() === s) || s);

      if (uniqueSymptoms.length === 0) {
        setSubmitError('Please describe your symptoms.');
        setStage('IDLE');
        return;
      }

      // 2. STEP 1: NN Prediction (Backend)
      setPipelineProgress(30);
      const predictionResponse = await apiService.predictSymptoms(
        uniqueSymptoms,
        profile?.age || undefined,
        profile?.gender || undefined,
        extractedData
      );

      // Save Prediction to Firestore
      const predictionId = `pred_${Date.now()}`;
      await firebaseService.saveToCollection('predictions', {
        userId,
        symptoms: uniqueSymptoms,
        results: predictionResponse.predictions || predictionResponse,
        timestamp: new Date().toISOString()
      }, predictionId);

      // 3. STEP 2: Agent Analysis (Gemini)
      setStage('ANALYZING');
      setPipelineProgress(60);
      
      // We need a mock or real ExtractionResult if manual
      const ocrDataToAnalyze = extractedData || {
        patientInfo: { age: profile?.age, gender: profile?.gender },
        symptoms: uniqueSymptoms,
        testResults: [],
        vitals: { temperature: temperature ? parseFloat(temperature) : null },
        confidence: 1.0
      };

      const agentAnalysis = await geminiAI.analyzeHealthCase(
        ocrDataToAnalyze as any, 
        predictionResponse.predictions || [predictionResponse]
      );

      // 4. STEP 3: Final Persistence (Firestore)
      setStage('SAVING');
      setPipelineProgress(90);

      const assessmentId = `assess_${Date.now()}`;
      
      // Save Assessment
      await firebaseService.saveToCollection('assessments', {
        ...agentAnalysis,
        userId,
        predictionId,
        reportId: reportMetadata?.reportId || null,
        status: 'completed'
      }, assessmentId);

      // Save Recommendations
      await firebaseService.saveToCollection('recommendations', {
        assessmentId,
        userId,
        ...agentAnalysis.recommendations
      });

      // Save Explanation
      await firebaseService.saveToCollection('explanations', {
        assessmentId,
        userId,
        ...agentAnalysis.explanation
      });

      // 5. COMPLETE
      setPipelineProgress(100);
      setStage('COMPLETE');

      // Navigate to results page
      setTimeout(() => {
        navigate(`/app/assessment/${assessmentId}`, { state: { result: agentAnalysis } });
      }, 1500);

    } catch (error: any) {
      console.error('Analysis Pipeline Failed:', error);
      const errorMessage = error.message || 'The AI analysis failed. Please try again.';
      setSubmitError(errorMessage);
      setStage('ERROR');
      
      // Log to Firestore
      firebaseService.logError(error, 'NewAssessmentPage.handleSubmit');
    }
  };

  const progress = calculateProgress();

  return (
    <Fade in={true} timeout={500}>
      <Box sx={{ minHeight: '100vh', pb: 8, pt: 4 }}>
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
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                '& .MuiLinearProgress-bar': {
                  background: 'linear-gradient(to right, #3b82f6, #7c3aed)',
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
                color: 'text.primary',
                mb: 1.5,
              }}
            >
              What brings you here today?
            </Typography>
            <Typography
              variant="body1"
              sx={{
                color: 'text.secondary',
                fontSize: { xs: '0.875rem', sm: '1rem' },
              }}
            >
              Our AI system will analyze your input to suggest next steps. Please be as descriptive as possible.
            </Typography>
          </Box>

          {/* Path Selection Cards */}
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
              gap: 2,
              mb: 4,
            }}
          >
            {/* Card 1: Medical Reports + Symptoms */}
            <Card
              data-testid="path-upload"
              elevation={0}
              sx={{
                border: '2px solid',
                borderColor: entryMode === 'upload' ? '#0ea5e9' : 'rgba(255, 255, 255, 0.1)',
                borderRadius: 3,
                transition: 'all 0.2s ease',
                background: entryMode === 'upload' ? 'rgba(14, 165, 233, 0.1)' : 'transparent',
                '&:hover': { borderColor: '#0ea5e9', boxShadow: '0 4px 20px rgba(14, 165, 233, 0.2)' },
              }}
            >
              <CardActionArea
                onClick={() => setEntryMode('upload')}
                aria-pressed={entryMode === 'upload'}
                aria-label="Medical Reports + Symptoms"
                sx={{ p: 3, height: '100%' }}
              >
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Box sx={{
                    display: 'flex', alignItems: 'center', gap: 1.5,
                    color: entryMode === 'upload' ? '#0ea5e9' : 'text.secondary',
                  }}>
                    <Description sx={{ fontSize: 28 }} />
                    <Typography sx={{ fontWeight: 700, fontSize: '1rem', color: 'text.primary' }}>
                      Medical Reports + Symptoms
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ color: 'text.secondary', fontSize: '0.8rem', lineHeight: 1.5 }}>
                    Upload a medical report (PDF/image) and our AI will extract your data, then you can review and add symptoms.
                  </Typography>
                  {entryMode === 'upload' && (
                    <Chip
                      label="Selected"
                      size="small"
                      sx={{ alignSelf: 'flex-start', background: 'linear-gradient(to right, #3b82f6, #7c3aed)', color: 'white', fontWeight: 600, fontSize: '0.7rem', mt: 0.5 }}
                    />
                  )}
                </Box>
              </CardActionArea>
            </Card>

            {/* Card 2: Symptoms Only */}
            <Card
              data-testid="path-manual"
              elevation={0}
              sx={{
                border: '2px solid',
                borderColor: entryMode === 'manual' ? '#0ea5e9' : 'rgba(255, 255, 255, 0.1)',
                borderRadius: 3,
                transition: 'all 0.2s ease',
                background: entryMode === 'manual' ? 'rgba(14, 165, 233, 0.1)' : 'transparent',
                '&:hover': { borderColor: '#0ea5e9', boxShadow: '0 4px 20px rgba(14, 165, 233, 0.2)' },
              }}
            >
              <CardActionArea
                onClick={() => { setEntryMode('manual'); setUploadError(null); }}
                aria-pressed={entryMode === 'manual'}
                aria-label="Symptoms Only"
                sx={{ p: 3, height: '100%' }}
              >
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Box sx={{
                    display: 'flex', alignItems: 'center', gap: 1.5,
                    color: entryMode === 'manual' ? '#0ea5e9' : 'text.secondary',
                  }}>
                    <Edit sx={{ fontSize: 28 }} />
                    <Typography sx={{ fontWeight: 700, fontSize: '1rem', color: 'text.primary' }}>
                      Symptoms Only
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ color: 'text.secondary', fontSize: '0.8rem', lineHeight: 1.5 }}>
                    Describe your symptoms manually. Quick and easy — no report required.
                  </Typography>
                  {entryMode === 'manual' && (
                    <Chip
                      label="Selected"
                      size="small"
                      sx={{ alignSelf: 'flex-start', background: 'linear-gradient(to right, #3b82f6, #7c3aed)', color: 'white', fontWeight: 600, fontSize: '0.7rem', mt: 0.5 }}
                    />
                  )}
                </Box>
              </CardActionArea>
            </Card>
          </Box>

          {/* File Upload Section - shown when Medical Reports + Symptoms path is selected */}
          {entryMode === 'upload' && (
            <Box sx={{ mb: 4 }}>
              <Typography
                variant="subtitle1"
                sx={{
                  fontWeight: 600,
                  color: 'text.primary',
                  mb: 1.5,
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                }}
              >
                Upload Medical Report
              </Typography>
              <Typography
                variant="body2"
                sx={{
                  color: 'text.secondary',
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
                  <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)' }}>
                    <Chip
                      label="Extracted Data - Review and Edit Below"
                      sx={{
                        background: 'rgba(14, 165, 233, 0.15)',
                        color: '#38bdf8',
                        border: '1px solid rgba(14, 165, 233, 0.3)',
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
                    background: 'rgba(52, 211, 153, 0.15)',
                    color: '#34d399',
                    fontSize: '0.7rem',
                    fontWeight: 600,
                    '& .MuiChip-icon': {
                      color: '#34d399',
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
                  background: extractedData && symptomDescription ? 'rgba(52, 211, 153, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                  borderRadius: 2,
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                  '& fieldset': {
                    borderColor: extractedData && symptomDescription ? '#34d399' : 'rgba(255, 255, 255, 0.1)',
                  },
                  '&:hover fieldset': {
                    borderColor: extractedData && symptomDescription ? '#10b981' : 'rgba(255, 255, 255, 0.2)',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#0ea5e9',
                  },
                },
                '& .MuiInputBase-input::placeholder': {
                  color: 'text.secondary',
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
                    background: selectedSymptoms.includes(symptom) ? 'rgba(14, 165, 233, 0.15)' : 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid',
                    borderColor: selectedSymptoms.includes(symptom) ? '#0ea5e9' : 'rgba(255, 255, 255, 0.1)',
                    color: selectedSymptoms.includes(symptom) ? '#38bdf8' : 'text.secondary',
                    fontWeight: 500,
                    fontSize: { xs: '0.75rem', sm: '0.875rem' },
                    px: 0.5,
                    transition: 'all 0.2s',
                    '&:hover': {
                      background: 'rgba(14, 165, 233, 0.2)',
                      borderColor: '#0ea5e9',
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
                      background: 'rgba(255, 255, 255, 0.05)',
                      borderRadius: 2,
                      fontSize: { xs: '0.875rem', sm: '0.875rem' },
                      '& fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                      },
                      '&:hover fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.2)',
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: '#0ea5e9',
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
                        background: 'rgba(52, 211, 153, 0.15)',
                        color: '#34d399',
                        fontSize: '0.65rem',
                        fontWeight: 600,
                        '& .MuiChip-icon': {
                          color: '#34d399',
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
                      background: extractedData && temperature ? 'rgba(52, 211, 153, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                      borderRadius: 2,
                      fontSize: { xs: '0.875rem', sm: '0.875rem' },
                      '& fieldset': {
                        borderColor: extractedData && temperature ? '#34d399' : 'rgba(255, 255, 255, 0.1)',
                      },
                      '&:hover fieldset': {
                        borderColor: extractedData && temperature ? '#10b981' : 'rgba(255, 255, 255, 0.2)',
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: '#0ea5e9',
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
                      color: 'text.secondary',
                      fontSize: '0.75rem',
                    }}
                  >
                    Pain Severity
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      fontWeight: 600,
                      color: '#38bdf8',
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
                    color: '#38bdf8',
                    '& .MuiSlider-thumb': {
                      width: 20,
                      height: 20,
                      bgcolor: '#38bdf8',
                      border: '3px solid #070612',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                    },
                    '& .MuiSlider-track': {
                      bgcolor: '#38bdf8',
                      border: 'none',
                    },
                    '& .MuiSlider-rail': {
                      bgcolor: 'rgba(255, 255, 255, 0.1)',
                    },
                  }}
                />
              </Box>
            </Box>
          </Box>



          {/* Pipeline Status */}
          {stage !== 'IDLE' && (
            <Box sx={{ mb: 4 }}>
              {/* Analysis in progress */}
              {(stage === 'PREDICTING' || stage === 'ANALYZING' || stage === 'SAVING') && (
                <Alert
                  icon={<CircularProgress size={20} sx={{ color: '#0ea5e9' }} />}
                  sx={{
                    background: 'rgba(14, 165, 233, 0.1)',
                    border: '1px solid rgba(14, 165, 233, 0.3)',
                    borderRadius: 2,
                    '& .MuiAlert-message': { color: '#38bdf8', width: '100%' },
                  }}
                >
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5, fontSize: '0.875rem' }}>
                    {stage === 'PREDICTING' ? 'Consulting Neural Network…' : stage === 'ANALYZING' ? 'AI Specialist Analyzing Findings…' : 'Finalizing Health Assessment…'}
                  </Typography>
                  <Typography variant="caption" sx={{ fontSize: '0.75rem', display: 'block', mb: 1 }}>
                    {pipelineProgress}% complete
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={pipelineProgress}
                    sx={{
                      height: 6,
                      borderRadius: 1,
                      bgcolor: 'rgba(14, 165, 233, 0.2)',
                      '& .MuiLinearProgress-bar': { background: 'linear-gradient(to right, #3b82f6, #7c3aed)', borderRadius: 1 },
                    }}
                  />
                </Alert>
              )}

              {/* Complete */}
              {stage === 'COMPLETE' && (
                <Alert
                  icon={<CheckCircle sx={{ color: '#10b981' }} />}
                  sx={{
                    background: 'rgba(52, 211, 153, 0.1)',
                    border: '1px solid rgba(52, 211, 153, 0.3)',
                    borderRadius: 2,
                    '& .MuiAlert-message': { color: '#34d399' },
                  }}
                >
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, fontSize: '0.875rem' }}>
                    Analysis complete — redirecting to results…
                  </Typography>
                </Alert>
              )}

              {/* Error */}
              {stage === 'ERROR' && (
                <Alert
                  severity="error"
                  icon={<ErrorOutline />}
                  sx={{ borderRadius: 2 }}
                  onClose={() => { setStage('IDLE'); setSubmitError(null); }}
                >
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, fontSize: '0.875rem' }}>
                    Analysis failed
                  </Typography>
                  {submitError && (
                    <Typography variant="caption" sx={{ fontSize: '0.75rem', display: 'block', mt: 0.5 }}>
                      {submitError}
                    </Typography>
                  )}
                </Alert>
              )}
            </Box>
          )}

          {/* AI Ready Alert */}
          <Alert
            icon={<AutoAwesome sx={{ color: '#38bdf8' }} />}
            sx={{
              mb: 4,
              background: 'rgba(14, 165, 233, 0.1)',
              border: '1px solid rgba(14, 165, 233, 0.3)',
              borderRadius: 2,
              '& .MuiAlert-message': {
                color: '#38bdf8',
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
                  color: 'text.secondary',
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
                disabled={stage !== 'IDLE'}
                sx={{
                  minHeight: { xs: 44, sm: 40 },
                  minWidth: { sm: 120 },
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 600,
                  fontSize: { xs: '0.875rem', sm: '0.875rem' },
                  borderColor: 'rgba(255, 255, 255, 0.1)',
                  color: 'text.secondary',
                  '&:hover': {
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    background: 'rgba(255, 255, 255, 0.05)',
                  },
                }}
              >
                Reset Form
              </Button>

              <Button
                variant="contained"
                onClick={handleSubmit}
                disabled={!symptomDescription || stage !== 'IDLE'}
                endIcon={stage === 'IDLE' && <Box component="span" sx={{ fontSize: '1.2rem' }}>→</Box>}
                sx={{
                  minHeight: { xs: 44, sm: 40 },
                  minWidth: { sm: 160 },
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 600,
                  fontSize: { xs: '0.875rem', sm: '0.875rem' },
                  background: 'linear-gradient(to right, #3b82f6, #7c3aed)',
                  boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
                  '&:hover': {
                    filter: 'brightness(1.1)',
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                  },
                  '&:disabled': {
                    background: 'rgba(255, 255, 255, 0.1)',
                    color: 'rgba(255, 255, 255, 0.3)',
                  },
                }}
              >
                {stage === 'IDLE' ? 'Submit Symptoms' : 'Analyzing…'}
              </Button>
            </Box>
          </Box>
        </Container>
      </Box>
    </Fade>
  );
};

export default NewAssessmentPage;
