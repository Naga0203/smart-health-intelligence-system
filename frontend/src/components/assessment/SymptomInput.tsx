// ============================================================================
// Symptom Input Component
// Searchable autocomplete for symptom selection with chips
// ============================================================================

import React, { useState } from 'react';
import {
  Box,
  Autocomplete,
  TextField,
  Typography,
} from '@mui/material';
import { SymptomChip } from './SymptomChip';
import type { SymptomData } from './AssessmentStepper';

// Common symptoms list for autocomplete
const COMMON_SYMPTOMS = [
  'Fever',
  'Cough',
  'Headache',
  'Fatigue',
  'Nausea',
  'Vomiting',
  'Diarrhea',
  'Abdominal Pain',
  'Chest Pain',
  'Shortness of Breath',
  'Dizziness',
  'Sore Throat',
  'Runny Nose',
  'Muscle Pain',
  'Joint Pain',
  'Back Pain',
  'Rash',
  'Itching',
  'Swelling',
  'Weight Loss',
  'Weight Gain',
  'Loss of Appetite',
  'Difficulty Sleeping',
  'Anxiety',
  'Depression',
  'Confusion',
  'Memory Loss',
  'Blurred Vision',
  'Ear Pain',
  'Toothache',
  'Bleeding',
  'Bruising',
  'Numbness',
  'Tingling',
  'Weakness',
  'Tremor',
  'Seizures',
  'Palpitations',
  'High Blood Pressure',
  'Low Blood Pressure',
  'Constipation',
  'Frequent Urination',
  'Painful Urination',
  'Blood in Urine',
  'Night Sweats',
  'Chills',
  'Sneezing',
  'Wheezing',
  'Hoarseness',
  'Difficulty Swallowing',
];

interface SymptomInputProps {
  symptoms: SymptomData[];
  onChange: (symptoms: SymptomData[]) => void;
}

export const SymptomInput: React.FC<SymptomInputProps> = ({
  symptoms,
  onChange,
}) => {
  const [inputValue, setInputValue] = useState('');

  const handleAddSymptom = (symptomName: string | null) => {
    if (!symptomName) return;

    // Check if symptom already exists
    const exists = symptoms.some(
      (s) => s.name.toLowerCase() === symptomName.toLowerCase()
    );

    if (exists) {
      return;
    }

    // Add new symptom with default values
    const newSymptom: SymptomData = {
      name: symptomName,
      severity: 5,
      duration: {
        value: 1,
        unit: 'days',
      },
    };

    onChange([...symptoms, newSymptom]);
    setInputValue('');
  };

  const handleRemoveSymptom = (index: number) => {
    const updated = symptoms.filter((_, i) => i !== index);
    onChange(updated);
  };

  const handleSeverityChange = (index: number, severity: number) => {
    const updated = symptoms.map((symptom, i) =>
      i === index ? { ...symptom, severity } : symptom
    );
    onChange(updated);
  };

  const handleDurationChange = (
    index: number,
    duration: { value: number; unit: 'hours' | 'days' | 'weeks' | 'months' }
  ) => {
    const updated = symptoms.map((symptom, i) =>
      i === index ? { ...symptom, duration } : symptom
    );
    onChange(updated);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Select Your Symptoms
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Search and select symptoms you're experiencing. You can adjust the severity and duration for each symptom.
      </Typography>

      {/* Symptom Search/Autocomplete */}
      <Autocomplete
        freeSolo
        options={COMMON_SYMPTOMS}
        inputValue={inputValue}
        onInputChange={(_, value) => setInputValue(value)}
        onChange={(_, value) => handleAddSymptom(value)}
        renderInput={(params) => (
          <TextField
            {...params}
            label="Search symptoms"
            placeholder="Type to search or add custom symptom"
            fullWidth
          />
        )}
        sx={{ mb: 3 }}
      />

      {/* Selected Symptoms */}
      {symptoms.length === 0 ? (
        <Box
          sx={{
            p: 4,
            textAlign: 'center',
            border: '2px dashed',
            borderColor: 'divider',
            borderRadius: 2,
            bgcolor: 'background.default',
          }}
        >
          <Typography variant="body1" color="text.secondary">
            No symptoms selected yet. Start by searching above.
          </Typography>
        </Box>
      ) : (
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Selected Symptoms ({symptoms.length})
          </Typography>
          {symptoms.map((symptom, index) => (
            <SymptomChip
              key={index}
              symptom={symptom.name}
              severity={symptom.severity}
              duration={symptom.duration}
              onSeverityChange={(severity) => handleSeverityChange(index, severity)}
              onDurationChange={(duration) => handleDurationChange(index, duration)}
              onRemove={() => handleRemoveSymptom(index)}
            />
          ))}
        </Box>
      )}
    </Box>
  );
};
