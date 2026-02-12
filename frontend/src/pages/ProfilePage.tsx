// ============================================================================
// ProfilePage - User profile management with view and edit modes
// ============================================================================

import { useState, useEffect } from 'react';
import { Container, Box, Alert, CircularProgress } from '@mui/material';
import { ProfileView } from '@/components/profile/ProfileView';
import { ProfileForm } from '@/components/profile/ProfileForm';
import { useUserStore } from '@/stores/userStore';
import { useNotificationStore } from '@/stores/notificationStore';

export function ProfilePage() {
  const [isEditing, setIsEditing] = useState(false);
  const { profile, loading, error, fetchProfile } = useUserStore();
  const { addNotification } = useNotificationStore();

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
      <Container maxWidth="md">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Box py={4}>
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
      </Box>
    </Container>
  );
}

export default ProfilePage;
