// ============================================================================
// Assessment Stepper Component - Responsive Design
// Multi-step form: Symptoms → Demographics → Vitals → Review
// Mobile-friendly with vertical stepper and proper touch targets
// ============================================================================

import React, { useState } from 'react';
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

const steps = ['Symptoms', 'Demographics', 'Vitals', 'Review'];

interface AssessmentStepperProps {
  onSubmit: (data: AssessmentFormData) => void;
  loading?: boolean;
  disabled?: boolean;
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
}

export const AssessmentStepper: React.FC<AssessmentStepperProps> = ({
  onSubmit,
  loading = false,
  disabled = false,
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
  });

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSymptomsChange = (symptoms: SymptomData[]) => {
    setFormData((prev) => ({ ...prev, symptoms }));
  };

  const handleDemographicsChange = (demographics: DemographicFormData) => {
    setFormData((prev) => ({ ...prev, demographics }));
  };

  const handleVitalsChange = (vitals: VitalsFormData) => {
    setFormData((prev) => ({ ...prev, vitals }));
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
          formData.demographics.gender !== ''
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
