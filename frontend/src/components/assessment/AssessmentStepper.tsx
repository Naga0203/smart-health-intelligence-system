// ============================================================================
// Assessment Stepper Component - Responsive Design
// Multi-step form: Symptoms → Demographics → Vitals → Review
// Mobile-friendly with vertical stepper and proper touch targets
// ============================================================================

import React, { useState, useEffect } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  Paper,
  Typography,
  LinearProgress,
  useTheme,
  useMediaQuery,
  Fade,
} from '@mui/material';
import { SymptomInput } from './SymptomInput';
import { DemographicForm } from './DemographicForm';
import { VitalsForm } from './VitalsForm';
import { ReviewStep } from './ReviewStep';
import type { ExtractedMedicalData, ReportMetadata } from '../../types/medicalReport';

const steps = ['Symptoms', 'Demographics', 'Vitals', 'Review'];

interface AssessmentStepperProps {
  onSubmit: (data: AssessmentFormData) => void;
  loading?: boolean;
  disabled?: boolean;
  extractedData?: ExtractedMedicalData;
  reportMetadata?: ReportMetadata;
}

export interface SymptomData {
  name: string;
  severity: number;
  duration: {
    value: number;
    unit: 'hours' | 'days' | 'weeks' | 'months';
  };
}

export interface DemographicFormData {
  age: number;
  gender: 'male' | 'female' | 'other';
  medical_history: string[];
}

export interface VitalsFormData {
  temperature?: number;
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  heart_rate?: number;
  respiratory_rate?: number;
}

export interface AssessmentFormData {
  symptoms: SymptomData[];
  demographics: DemographicFormData;
  vitals: VitalsFormData;
  reportMetadata?: ReportMetadata;
  dataSources?: Map<string, 'manual' | 'extracted'>;
}

export const AssessmentStepper: React.FC<AssessmentStepperProps> = ({
  onSubmit,
  loading = false,
  disabled = false,
  extractedData,
  reportMetadata,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md')); // < 900px
  const isSmallMobile = useMediaQuery(theme.breakpoints.down('sm')); // < 600px

  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<AssessmentFormData>({
    symptoms: [],
    demographics: {
      age: 0,
      gender: 'male',
      medical_history: [],
    },
    vitals: {},
    reportMetadata,
    dataSources: new Map(),
  });
  const [modifiedFields, setModifiedFields] = useState<Set<string>>(new Set());

  // Populate form from extracted data when available
  useEffect(() => {
    if (extractedData) {
      populateFromExtractedData(extractedData);
    }
  }, [extractedData]);

  const populateFromExtractedData = (data: ExtractedMedicalData) => {
    const newDataSources = new Map<string, 'manual' | 'extracted'>();

    // Populate symptoms
    if (data.symptoms && data.symptoms.length > 0) {
      const symptomData: SymptomData[] = data.symptoms.map(symptom => ({
        name: symptom,
        severity: 5, // Default severity
        duration: { value: 1, unit: 'days' as const },
      }));

      setFormData(prev => ({ ...prev, symptoms: symptomData }));
      data.symptoms.forEach((_, index) => {
        newDataSources.set(`symptom_${index}`, 'extracted');
      });
    }

    // Populate vitals
    if (data.vitals) {
      const vitalsData: VitalsFormData = {};

      if (data.vitals.temperature) {
        vitalsData.temperature = data.vitals.temperature;
        newDataSources.set('vitals_temperature', 'extracted');
      }

      if (data.vitals.heartRate) {
        vitalsData.heart_rate = data.vitals.heartRate;
        newDataSources.set('vitals_heart_rate', 'extracted');
      }

      if (data.vitals.bloodPressure) {
        // Parse blood pressure string like "120/80"
        const bpParts = data.vitals.bloodPressure.split('/');
        if (bpParts.length === 2) {
          vitalsData.blood_pressure_systolic = parseInt(bpParts[0], 10);
          vitalsData.blood_pressure_diastolic = parseInt(bpParts[1], 10);
          newDataSources.set('vitals_blood_pressure_systolic', 'extracted');
          newDataSources.set('vitals_blood_pressure_diastolic', 'extracted');
        }
      }

      setFormData(prev => ({ ...prev, vitals: vitalsData }));
    }

    // Update data sources
    setFormData(prev => ({ ...prev, dataSources: newDataSources }));
  };

  const markFieldSource = (fieldName: string, source: 'manual' | 'extracted') => {
    setFormData(prev => {
      const newDataSources = new Map(prev.dataSources);
      newDataSources.set(fieldName, source);
      return { ...prev, dataSources: newDataSources };
    });
  };

  const markFieldAsModified = (fieldName: string) => {
    setModifiedFields(prev => new Set(prev).add(fieldName));
    markFieldSource(fieldName, 'manual');
  };

  const isFieldExtracted = (fieldName: string): boolean => {
    return formData.dataSources?.get(fieldName) === 'extracted' && !modifiedFields.has(fieldName);
  };

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSymptomsChange = (symptoms: SymptomData[]) => {
    setFormData((prev) => ({ ...prev, symptoms }));
    // Mark symptoms as manually modified
    symptoms.forEach((_, index) => {
      markFieldAsModified(`symptom_${index}`);
    });
  };

  const handleDemographicsChange = (demographics: DemographicFormData) => {
    setFormData((prev) => ({ ...prev, demographics }));
  };

  const handleVitalsChange = (vitals: VitalsFormData) => {
    setFormData((prev) => ({ ...prev, vitals }));
    // Mark vitals as manually modified
    Object.keys(vitals).forEach(key => {
      markFieldAsModified(`vitals_${key}`);
    });
  };

  const handleSubmit = () => {
    onSubmit(formData);
  };

  const canProceed = () => {
    switch (activeStep) {
      case 0: // Symptoms
        return formData.symptoms.length > 0;
      case 1: // Demographics
        return (
          formData.demographics.age > 0 &&
          (formData.demographics.gender as string) !== ''
        );
      case 2: // Vitals (optional)
        return true;
      case 3: // Review
        return true;
      default:
        return false;
    }
  };

  const progressPercentage = ((activeStep + 1) / steps.length) * 100;

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return (
          <SymptomInput
            symptoms={formData.symptoms}
            onChange={handleSymptomsChange}
            extractedSymptoms={extractedData?.symptoms}
          />
        );
      case 1:
        return (
          <DemographicForm
            data={formData.demographics}
            onChange={handleDemographicsChange}
          />
        );
      case 2:
        return (
          <VitalsForm
            data={formData.vitals}
            onChange={handleVitalsChange}
            isFieldExtracted={isFieldExtracted}
          />
        );
      case 3:
        return <ReviewStep data={formData} />;
      default:
        return null;
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Progress Bar - More visible on mobile */}
      <Box sx={{ mb: 2 }}>
        <LinearProgress
          variant="determinate"
          value={progressPercentage}
          sx={{
            height: { xs: 6, sm: 4 },
            borderRadius: 2,
            backgroundColor: 'grey.200',
            '& .MuiLinearProgress-bar': {
              borderRadius: 2,
              transition: 'transform 0.4s ease-in-out',
            },
          }}
        />
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{
            display: 'block',
            textAlign: 'right',
            mt: 0.5,
            fontSize: { xs: '0.75rem', sm: '0.75rem' },
          }}
        >
          Step {activeStep + 1} of {steps.length}
        </Typography>
      </Box>

      {/* Stepper - Responsive orientation */}
      <Stepper
        activeStep={activeStep}
        orientation={isMobile ? 'vertical' : 'horizontal'}
        sx={{
          mb: { xs: 3, sm: 4 },
          // Better spacing for mobile
          '& .MuiStepLabel-root': {
            px: { xs: 0, sm: 1 },
          },
        }}
      >
        {steps.map((label, index) => (
          <Step key={label}>
            <StepLabel
              sx={{
                '& .MuiStepLabel-label': {
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                  fontWeight: activeStep === index ? 600 : 400,
                },
              }}
            >
              {isSmallMobile ? label.substring(0, 10) : label}
            </StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* Content Area */}
      <Fade in={true} timeout={300} key={activeStep}>
        <Paper
          sx={{
            p: { xs: 2, sm: 3, md: 4 },
            minHeight: { xs: 350, sm: 400 },
            transition: 'all 0.3s ease-in-out',
          }}
        >
          {renderStepContent()}

          {/* Navigation Buttons */}
          <Box
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column-reverse', sm: 'row' },
              justifyContent: 'space-between',
              gap: { xs: 2, sm: 0 },
              mt: 4,
            }}
          >
            <Button
              disabled={activeStep === 0}
              onClick={handleBack}
              variant="outlined"
              sx={{
                minHeight: { xs: 44, sm: 40 },
                width: { xs: '100%', sm: 'auto' },
                minWidth: { sm: 100 },
              }}
            >
              Back
            </Button>

            <Box sx={{ display: 'flex', gap: 2 }}>
              {activeStep === steps.length - 1 ? (
                <Button
                  variant="contained"
                  onClick={handleSubmit}
                  disabled={loading || disabled || !canProceed()}
                  sx={{
                    minHeight: { xs: 44, sm: 40 },
                    width: { xs: '100%', sm: 'auto' },
                    minWidth: { sm: 160 },
                    position: 'relative',
                  }}
                >
                  {loading ? 'Submitting...' : 'Submit Assessment'}
                </Button>
              ) : (
                <Button
                  variant="contained"
                  onClick={handleNext}
                  disabled={disabled || !canProceed()}
                  sx={{
                    minHeight: { xs: 44, sm: 40 },
                    width: { xs: '100%', sm: 'auto' },
                    minWidth: { sm: 100 },
                  }}
                >
                  Next
                </Button>
              )}
            </Box>
          </Box>
        </Paper>
      </Fade>
    </Box>
  );
};
