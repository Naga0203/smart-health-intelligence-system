// ============================================================================
// Login Page
// ============================================================================

import { useEffect } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Box,
  Paper,
  Typography,
  Divider,
  Link,
} from '@mui/material';
import { useAuthStore } from '@/stores/authStore';
import { LoginForm } from '@/components/auth/LoginForm';
import { GoogleAuthButton } from '@/components/auth/GoogleAuthButton';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, login, error, loading, clearError } = useAuthStore();

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (user) {
      navigate('/app/dashboard');
    }
  }, [user, navigate]);

  // Clear error on unmount
  useEffect(() => {
    return () => {
      clearError();
    };
  }, [clearError]);

  const handleLogin = async (email: string, password: string) => {
    try {
      await login(email, password);
      // Navigation will happen via the useEffect above
    } catch (error) {
      // Error is already set in the store
      console.error('Login failed:', error);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          py: 4,
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            width: '100%',
            borderRadius: 2,
          }}
        >
          <Typography
            variant="h4"
            component="h1"
            align="center"
            gutterBottom
            sx={{ mb: 3 }}
          >
            AI Health Intelligence
          </Typography>

          <Typography
            variant="body1"
            align="center"
            color="text.secondary"
            sx={{ mb: 4 }}
          >
            Sign in to access your health assessments
          </Typography>

          <LoginForm
            onSubmit={handleLogin}
            error={error}
            loading={loading}
          />

          <Divider sx={{ my: 3 }}>
            <Typography variant="body2" color="text.secondary">
              OR
            </Typography>
          </Divider>

          <GoogleAuthButton />

          <Box sx={{ textAlign: 'center', mt: 3 }}>
            <Typography variant="body2">
              Don't have an account?{' '}
              <Link component={RouterLink} to="/register" underline="hover">
                Create one
              </Link>
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};
