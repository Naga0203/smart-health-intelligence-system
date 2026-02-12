// ============================================================================
// Assessment Stepper Component
// Multi-step form: Symptoms → Demographics → Vitals → Review
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
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Paper sx={{ p: 3, minHeight: 400 }}>
        {renderStepContent()}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
            variant="outlined"
          >
            Back
          </Button>

          <Box sx={{ display: 'flex', gap: 2 }}>
            {activeStep === steps.length - 1 ? (
              <Button
                variant="contained"
                onClick={handleSubmit}
                disabled={loading || disabled || !canProceed()}
              >
                {loading ? 'Submitting...' : 'Submit Assessment'}
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={disabled || !canProceed()}
              >
                Next
              </Button>
            )}
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};
