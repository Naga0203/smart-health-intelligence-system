// ============================================================================
// ProfileView Component - Display user profile information
// ============================================================================

import { Box, Card, CardContent, Typography, Grid, Chip, Button } from '@mui/material';
import { Edit as EditIcon } from '@mui/icons-material';

interface ProfileViewProps {
  profile: any;
  onEdit: () => void;
}

export function ProfileView({ profile, onEdit }: ProfileViewProps) {
  if (!profile) {
    return null;
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5" component="h2">
            Profile Information
          </Typography>
          <Button
            variant="outlined"
            startIcon={<EditIcon />}
            onClick={onEdit}
          >
            Edit Profile
          </Button>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Email
            </Typography>
            <Typography variant="body1">{profile.email}</Typography>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Display Name
            </Typography>
            <Typography variant="body1">
              {profile.display_name || 'Not set'}
            </Typography>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Date of Birth
            </Typography>
            <Typography variant="body1">
              {profile.date_of_birth || 'Not set'}
            </Typography>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Gender
            </Typography>
            <Typography variant="body1">
              {profile.gender ? profile.gender.charAt(0).toUpperCase() + profile.gender.slice(1).replace('_', ' ') : 'Not set'}
            </Typography>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Phone Number
            </Typography>
            <Typography variant="body1">
              {profile.phone_number || 'Not set'}
            </Typography>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Email Verified
            </Typography>
            <Chip
              label={profile.email_verified ? 'Verified' : 'Not Verified'}
              color={profile.email_verified ? 'success' : 'default'}
              size="small"
            />
          </Grid>

          {profile.medical_history && profile.medical_history.length > 0 && (
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Medical History
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {profile.medical_history.map((condition: string, index: number) => (
                  <Chip key={index} label={condition} size="small" />
                ))}
              </Box>
            </Grid>
          )}

          {profile.allergies && profile.allergies.length > 0 && (
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Allergies
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {profile.allergies.map((allergy: string, index: number) => (
                  <Chip key={index} label={allergy} size="small" color="warning" />
                ))}
              </Box>
            </Grid>
          )}

          {profile.current_medications && profile.current_medications.length > 0 && (
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Current Medications
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {profile.current_medications.map((medication: string, index: number) => (
                  <Chip key={index} label={medication} size="small" color="info" />
                ))}
              </Box>
            </Grid>
          )}

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Account Created
            </Typography>
            <Typography variant="body2">
              {new Date(profile.created_at).toLocaleDateString()}
            </Typography>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Last Updated
            </Typography>
            <Typography variant="body2">
              {new Date(profile.updated_at).toLocaleDateString()}
            </Typography>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}
