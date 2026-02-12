// ============================================================================
// ProfileForm Component - Edit user profile with validation
// ============================================================================

import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Chip,
  FormHelperText,
  Alert,
} from '@mui/material';
import { Save as SaveIcon, Cancel as CancelIcon } from '@mui/icons-material';
import { useState } from 'react';
import { useUserStore } from '@/stores/userStore';

// Validation schema
const profileSchema = z.object({
  display_name: z.string().min(1, 'Name is required').max(100, 'Name must be less than 100 characters'),
  date_of_birth: z.string().optional().refine(
    (val) => {
      if (!val) return true;
      const date = new Date(val);
      const now = new Date();
      const age = now.getFullYear() - date.getFullYear();
      return age >= 0 && age <= 150;
    },
    { message: 'Please enter a valid date of birth' }
  ),
  gender: z.enum(['male', 'female', 'other', 'prefer_not_to_say']).optional(),
  phone_number: z.string().optional().refine(
    (val) => {
      if (!val) return true;
      return /^[\d\s\-\+\(\)]+$/.test(val);
    },
    { message: 'Please enter a valid phone number' }
  ),
  medical_history: z.array(z.string()).optional(),
  allergies: z.array(z.string()).optional(),
  current_medications: z.array(z.string()).optional(),
});

type ProfileFormData = z.infer<typeof profileSchema>;

interface ProfileFormProps {
  profile: any;
  onCancel: () => void;
  onSave: () => void;
}

export function ProfileForm({ profile, onCancel, onSave }: ProfileFormProps) {
  const { updateProfile, loading, error } = useUserStore();
  const [medicalHistoryInput, setMedicalHistoryInput] = useState('');
  const [allergiesInput, setAllergiesInput] = useState('');
  const [medicationsInput, setMedicationsInput] = useState('');

  const {
    control,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      display_name: profile?.display_name || '',
      date_of_birth: profile?.date_of_birth || '',
      gender: profile?.gender || '',
      phone_number: profile?.phone_number || '',
      medical_history: profile?.medical_history || [],
      allergies: profile?.allergies || [],
      current_medications: profile?.current_medications || [],
    },
  });

  const medicalHistory = watch('medical_history') || [];
  const allergies = watch('allergies') || [];
  const currentMedications = watch('current_medications') || [];

  const onSubmit = async (data: ProfileFormData) => {
    try {
      await updateProfile(data);
      onSave();
    } catch (err) {
      // Error is handled by the store
      console.error('Failed to update profile:', err);
    }
  };

  const handleAddMedicalHistory = () => {
    if (medicalHistoryInput.trim()) {
      setValue('medical_history', [...medicalHistory, medicalHistoryInput.trim()]);
      setMedicalHistoryInput('');
    }
  };

  const handleRemoveMedicalHistory = (index: number) => {
    setValue(
      'medical_history',
      medicalHistory.filter((_, i) => i !== index)
    );
  };

  const handleAddAllergy = () => {
    if (allergiesInput.trim()) {
      setValue('allergies', [...allergies, allergiesInput.trim()]);
      setAllergiesInput('');
    }
  };

  const handleRemoveAllergy = (index: number) => {
    setValue(
      'allergies',
      allergies.filter((_, i) => i !== index)
    );
  };

  const handleAddMedication = () => {
    if (medicationsInput.trim()) {
      setValue('current_medications', [...currentMedications, medicationsInput.trim()]);
      setMedicationsInput('');
    }
  };

  const handleRemoveMedication = (index: number) => {
    setValue(
      'current_medications',
      currentMedications.filter((_, i) => i !== index)
    );
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" component="h2" gutterBottom>
          Edit Profile
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
          <Grid container spacing={3}>
            {/* Display Name */}
            <Grid item xs={12} sm={6}>
              <Controller
                name="display_name"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Display Name"
                    fullWidth
                    required
                    error={!!errors.display_name}
                    helperText={errors.display_name?.message}
                  />
                )}
              />
            </Grid>

            {/* Date of Birth */}
            <Grid item xs={12} sm={6}>
              <Controller
                name="date_of_birth"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Date of Birth"
                    type="date"
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                    error={!!errors.date_of_birth}
                    helperText={errors.date_of_birth?.message}
                  />
                )}
              />
            </Grid>

            {/* Gender */}
            <Grid item xs={12} sm={6}>
              <Controller
                name="gender"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.gender}>
                    <InputLabel>Gender</InputLabel>
                    <Select {...field} label="Gender">
                      <MenuItem value="">
                        <em>Not specified</em>
                      </MenuItem>
                      <MenuItem value="male">Male</MenuItem>
                      <MenuItem value="female">Female</MenuItem>
                      <MenuItem value="other">Other</MenuItem>
                      <MenuItem value="prefer_not_to_say">Prefer not to say</MenuItem>
                    </Select>
                    {errors.gender && (
                      <FormHelperText>{errors.gender.message}</FormHelperText>
                    )}
                  </FormControl>
                )}
              />
            </Grid>

            {/* Phone Number */}
            <Grid item xs={12} sm={6}>
              <Controller
                name="phone_number"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Phone Number"
                    fullWidth
                    error={!!errors.phone_number}
                    helperText={errors.phone_number?.message}
                  />
                )}
              />
            </Grid>

            {/* Medical History */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Medical History
              </Typography>
              <Box display="flex" gap={1} mb={1}>
                <TextField
                  value={medicalHistoryInput}
                  onChange={(e) => setMedicalHistoryInput(e.target.value)}
                  placeholder="Add condition"
                  size="small"
                  fullWidth
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddMedicalHistory();
                    }
                  }}
                />
                <Button variant="outlined" onClick={handleAddMedicalHistory}>
                  Add
                </Button>
              </Box>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {medicalHistory.map((condition: string, index: number) => (
                  <Chip
                    key={index}
                    label={condition}
                    onDelete={() => handleRemoveMedicalHistory(index)}
                    size="small"
                  />
                ))}
              </Box>
            </Grid>

            {/* Allergies */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Allergies
              </Typography>
              <Box display="flex" gap={1} mb={1}>
                <TextField
                  value={allergiesInput}
                  onChange={(e) => setAllergiesInput(e.target.value)}
                  placeholder="Add allergy"
                  size="small"
                  fullWidth
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddAllergy();
                    }
                  }}
                />
                <Button variant="outlined" onClick={handleAddAllergy}>
                  Add
                </Button>
              </Box>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {allergies.map((allergy: string, index: number) => (
                  <Chip
                    key={index}
                    label={allergy}
                    onDelete={() => handleRemoveAllergy(index)}
                    size="small"
                    color="warning"
                  />
                ))}
              </Box>
            </Grid>

            {/* Current Medications */}
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Current Medications
              </Typography>
              <Box display="flex" gap={1} mb={1}>
                <TextField
                  value={medicationsInput}
                  onChange={(e) => setMedicationsInput(e.target.value)}
                  placeholder="Add medication"
                  size="small"
                  fullWidth
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddMedication();
                    }
                  }}
                />
                <Button variant="outlined" onClick={handleAddMedication}>
                  Add
                </Button>
              </Box>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {currentMedications.map((medication: string, index: number) => (
                  <Chip
                    key={index}
                    label={medication}
                    onDelete={() => handleRemoveMedication(index)}
                    size="small"
                    color="info"
                  />
                ))}
              </Box>
            </Grid>

            {/* Action Buttons */}
            <Grid item xs={12}>
              <Box display="flex" gap={2} justifyContent="flex-end">
                <Button
                  variant="outlined"
                  startIcon={<CancelIcon />}
                  onClick={onCancel}
                  disabled={loading}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  startIcon={<SaveIcon />}
                  disabled={loading}
                >
                  {loading ? 'Saving...' : 'Save Changes'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>
      </CardContent>
    </Card>
  );
}
