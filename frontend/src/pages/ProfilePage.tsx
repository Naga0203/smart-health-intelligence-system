// ============================================================================
// ProfilePage - User profile management with view and edit modes
// ============================================================================

import { useState, useEffect } from 'react';
import { Container, Box, Alert, CircularProgress, useTheme, alpha } from '@mui/material';
import { ProfileView } from '@/components/profile/ProfileView';
import { ProfileForm } from '@/components/profile/ProfileForm';
import { useUserStore } from '@/stores/userStore';
import { useNotificationStore } from '@/stores/notificationStore';

export function ProfilePage() {
  const [isEditing, setIsEditing] = useState(false);
  const { profile, loading, error, fetchProfile } = useUserStore();
  const { addNotification } = useNotificationStore();
  const theme = useTheme();

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  const handleSave = () => {
    setIsEditing(false);
    addNotification({
      type: 'success',
      message: 'Profile updated successfully',
      dismissible: true,
    });
  };

  if (loading && !profile) {
    return (
      <Box 
        sx={{
          minHeight: 'calc(100vh - 64px)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${alpha(theme.palette.background.default, 1)} 100%)`,
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box 
      sx={{
        minHeight: 'calc(100vh - 64px)',
        background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.03)} 0%, ${alpha(theme.palette.background.default, 1)} 100%)`,
        py: { xs: 4, md: 8 },
        transition: 'background 0.3s ease'
      }}
    >
      <Container maxWidth="md">
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {isEditing ? (
          <ProfileForm
            profile={profile}
            onCancel={handleCancel}
            onSave={handleSave}
          />
        ) : (
          <ProfileView profile={profile} onEdit={handleEdit} />
        )}
      </Container>
    </Box>
  );
}

export default ProfilePage;
