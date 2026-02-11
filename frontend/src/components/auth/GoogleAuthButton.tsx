// ============================================================================
// Google OAuth Button Component
// ============================================================================

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Box } from '@mui/material';
import { Google as GoogleIcon } from '@mui/icons-material';
import { useAuthStore } from '@/stores/authStore';

export const GoogleAuthButton: React.FC = () => {
  const navigate = useNavigate();
  const { loginWithGoogle } = useAuthStore();
  const [loading, setLoading] = useState(false);

  const handleGoogleLogin = async () => {
    setLoading(true);
    try {
      await loginWithGoogle();
      navigate('/app/dashboard');
    } catch (error) {
      console.error('Google login failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button
      variant="outlined"
      fullWidth
      size="large"
      onClick={handleGoogleLogin}
      disabled={loading}
      startIcon={<GoogleIcon />}
      sx={{
        borderColor: '#4285f4',
        color: '#4285f4',
        '&:hover': {
          borderColor: '#357ae8',
          backgroundColor: 'rgba(66, 133, 244, 0.04)',
        },
      }}
    >
      {loading ? 'Signing in...' : 'Continue with Google'}
    </Button>
  );
};
