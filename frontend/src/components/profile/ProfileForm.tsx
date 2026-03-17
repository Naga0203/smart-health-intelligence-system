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
  useTheme,
  alpha,
  Divider,
  Paper,
  InputAdornment,
  IconButton,
  Avatar
} from '@mui/material';
import { Save as SaveIcon, Cancel as CancelIcon, Add as AddIcon, Edit as EditIcon, Person as PersonIcon, MedicalInformation as MedicalIcon } from '@mui/icons-material';
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
  const theme = useTheme();
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
    setValue('medical_history', medicalHistory.filter((_, i) => i !== index));
  };

  const handleAddAllergy = () => {
    if (allergiesInput.trim()) {
      setValue('allergies', [...allergies, allergiesInput.trim()]);
      setAllergiesInput('');
    }
  };

  const handleRemoveAllergy = (index: number) => {
    setValue('allergies', allergies.filter((_, i) => i !== index));
  };

  const handleAddMedication = () => {
    if (medicationsInput.trim()) {
      setValue('current_medications', [...currentMedications, medicationsInput.trim()]);
      setMedicationsInput('');
    }
  };

  const handleRemoveMedication = (index: number) => {
    setValue('current_medications', currentMedications.filter((_, i) => i !== index));
  };

  const glassCardSx = {
    background: alpha(theme.palette.background.paper, 0.7),
    backdropFilter: 'blur(16px)',
    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    boxShadow: `0 8px 32px 0 ${alpha(theme.palette.common.black, 0.05)}`,
    borderRadius: 4,
    overflow: 'hidden',
  };

  const gradientHeaderSx = {
    background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.1)} 0%, ${alpha(theme.palette.secondary.main, 0.05)} 100%)`,
    p: { xs: 3, sm: 4 },
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`
  };

  return (
    <Card sx={glassCardSx} elevation={0}>
      <Box sx={gradientHeaderSx}>
        <Box display="flex" alignItems="center" gap={2}>
           <Avatar sx={{ bgcolor: theme.palette.primary.main, width: 48, height: 48, boxShadow: `0 4px 12px 0 ${alpha(theme.palette.primary.main, 0.3)}` }}>
              <EditIcon />
           </Avatar>
           <Typography variant="h5" component="h2" fontWeight="bold">
             Edit Profile
           </Typography>
        </Box>
        <Box display={{ xs: 'none', sm: 'flex' }} gap={2}>
           <Button variant="outlined" startIcon={<CancelIcon />} onClick={onCancel} disabled={loading} sx={{ borderRadius: 2 }}>
             Cancel
           </Button>
           <Button variant="contained" startIcon={<SaveIcon />} onClick={handleSubmit(onSubmit)} disabled={loading} sx={{ borderRadius: 2, boxShadow: 2 }}>
             {loading ? 'Saving...' : 'Save Changes'}
           </Button>
        </Box>
      </Box>

      <CardContent sx={{ p: { xs: 2, sm: 4 } }}>
        {error && <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>{error}</Alert>}

        <Box component="form" noValidate>
          {/* Section 1: Personal Info */}
          <Typography variant="h6" fontWeight="bold" color="primary" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
            <PersonIcon /> Personal Information
          </Typography>
          
          <Paper elevation={0} sx={{ p: 3, mb: 4, bgcolor: alpha(theme.palette.background.default, 0.4), borderRadius: 3, border: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
            <Grid container spacing={3}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <Controller
                  name="display_name"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Display Name" fullWidth required error={!!errors.display_name} helperText={errors.display_name?.message} variant="outlined" />
                  )}
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <Controller
                  name="date_of_birth"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Date of Birth" type="date" fullWidth InputLabelProps={{ shrink: true }} error={!!errors.date_of_birth} helperText={errors.date_of_birth?.message} variant="outlined" />
                  )}
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <Controller
                  name="gender"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.gender} variant="outlined">
                      <InputLabel>Gender</InputLabel>
                      <Select {...field} label="Gender">
                        <MenuItem value=""><em>Not specified</em></MenuItem>
                        <MenuItem value="male">Male</MenuItem>
                        <MenuItem value="female">Female</MenuItem>
                        <MenuItem value="other">Other</MenuItem>
                        <MenuItem value="prefer_not_to_say">Prefer not to say</MenuItem>
                      </Select>
                      {errors.gender && <FormHelperText>{errors.gender.message}</FormHelperText>}
                    </FormControl>
                  )}
                />
              </Grid>

              <Grid size={{ xs: 12, sm: 6 }}>
                <Controller
                  name="phone_number"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Phone Number" fullWidth error={!!errors.phone_number} helperText={errors.phone_number?.message} variant="outlined" />
                  )}
                />
              </Grid>
            </Grid>
          </Paper>

          {/* Section 2: Medical Info */}
          <Divider sx={{ my: 4, opacity: 0.6 }} />
          
          <Typography variant="h6" fontWeight="bold" color="primary" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
            <MedicalIcon /> Medical Dashboard
          </Typography>

          <Grid container spacing={3}>
            {/* Medical History */}
            <Grid size={{ xs: 12 }}>
              <Paper elevation={0} sx={{ p: 3, bgcolor: alpha(theme.palette.background.default, 0.4), borderRadius: 3, border: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Pre-existing Conditions
                </Typography>
                <Box display="flex" gap={1} mb={2} mt={1}>
                  <TextField
                    value={medicalHistoryInput}
                    onChange={(e) => setMedicalHistoryInput(e.target.value)}
                    placeholder="Add a condition (e.g. Asthma)"
                    size="small"
                    fullWidth
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') { e.preventDefault(); handleAddMedicalHistory(); }
                    }}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton onClick={handleAddMedicalHistory} edge="end" color="primary"><AddIcon /></IconButton>
                        </InputAdornment>
                      ),
                    }}
                  />
                </Box>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {medicalHistory.map((condition: string, index: number) => (
                    <Chip key={index} label={condition} onDelete={() => handleRemoveMedicalHistory(index)} size="medium" color="primary" variant="outlined" sx={{ borderRadius: 1.5 }} />
                  ))}
                  {medicalHistory.length === 0 && <Typography variant="body2" color="text.secondary" fontStyle="italic">No conditions added yet.</Typography>}
                </Box>
              </Paper>
            </Grid>

            {/* Allergies */}
            <Grid size={{ xs: 12, md: 6 }}>
              <Paper elevation={0} sx={{ p: 3, height: '100%', bgcolor: alpha(theme.palette.background.default, 0.4), borderRadius: 3, border: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom color="warning.main">
                  Allergies
                </Typography>
                <Box display="flex" gap={1} mb={2} mt={1}>
                  <TextField
                    value={allergiesInput}
                    onChange={(e) => setAllergiesInput(e.target.value)}
                    placeholder="Add an allergy (e.g. Peanuts)"
                    size="small"
                    fullWidth
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') { e.preventDefault(); handleAddAllergy(); }
                    }}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton onClick={handleAddAllergy} edge="end" color="warning"><AddIcon /></IconButton>
                        </InputAdornment>
                      ),
                    }}
                  />
                </Box>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {allergies.map((allergy: string, index: number) => (
                    <Chip key={index} label={allergy} onDelete={() => handleRemoveAllergy(index)} size="medium" color="warning" sx={{ borderRadius: 1.5 }} />
                  ))}
                  {allergies.length === 0 && <Typography variant="body2" color="text.secondary" fontStyle="italic">No allergies added yet.</Typography>}
                </Box>
              </Paper>
            </Grid>

            {/* Current Medications */}
            <Grid size={{ xs: 12, md: 6 }}>
              <Paper elevation={0} sx={{ p: 3, height: '100%', bgcolor: alpha(theme.palette.background.default, 0.4), borderRadius: 3, border: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom color="info.main">
                  Current Medications
                </Typography>
                <Box display="flex" gap={1} mb={2} mt={1}>
                  <TextField
                    value={medicationsInput}
                    onChange={(e) => setMedicationsInput(e.target.value)}
                    placeholder="Add a medication (e.g. Lisinopril 10mg)"
                    size="small"
                    fullWidth
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') { e.preventDefault(); handleAddMedication(); }
                    }}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton onClick={handleAddMedication} edge="end" color="info"><AddIcon /></IconButton>
                        </InputAdornment>
                      ),
                    }}
                  />
                </Box>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {currentMedications.map((medication: string, index: number) => (
                    <Chip key={index} label={medication} onDelete={() => handleRemoveMedication(index)} size="medium" color="info" sx={{ borderRadius: 1.5 }} />
                  ))}
                  {currentMedications.length === 0 && <Typography variant="body2" color="text.secondary" fontStyle="italic">No medications added yet.</Typography>}
                </Box>
              </Paper>
            </Grid>
          </Grid>

          {/* Action Buttons for Mobile */}
          <Box display={{ xs: 'flex', sm: 'none' }} gap={2} mt={4} justifyContent="stretch">
            <Button variant="outlined" fullWidth startIcon={<CancelIcon />} onClick={onCancel} disabled={loading} sx={{ borderRadius: 2 }}>
              Cancel
            </Button>
            <Button variant="contained" fullWidth startIcon={<SaveIcon />} onClick={handleSubmit(onSubmit)} disabled={loading} sx={{ borderRadius: 2, boxShadow: 2 }}>
              {loading ? 'Saving...' : 'Save Changes'}
            </Button>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
