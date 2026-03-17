import { useEffect, useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { LoginForm } from '@/components/auth/LoginForm';
import { Box, Typography, Button, useTheme, alpha } from '@mui/material';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const { user, login, loginWithGoogle, error, loading, clearError } = useAuthStore();
  const [socialLoading, setSocialLoading] = useState(false);

  useEffect(() => {
    if (user) navigate('/app/dashboard');
  }, [user, navigate]);

  useEffect(() => {
    return () => { clearError(); };
  }, [clearError]);

  const handleLogin = async (email: string, password: string) => {
    try {
      await login(email, password);
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      setSocialLoading(true);
      await loginWithGoogle();
      navigate('/app/dashboard');
    } catch (err) {
      console.error('Google login failed:', err);
    } finally {
      setSocialLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: `linear-gradient(135deg, ${theme.palette.background.default} 0%, ${theme.palette.background.paper} 100%)`,
        p: 2,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Background glow effects */}
      <Box 
        sx={{
          position: 'absolute',
          top: '-20%',
          right: '-10%',
          width: '60vw',
          height: '60vw',
          borderRadius: '50%',
          background: `radial-gradient(circle, ${alpha(theme.palette.primary.main, 0.15)} 0%, transparent 70%)`,
          zIndex: 0,
        }}
      />
      
      <Box
        sx={{
          maxWidth: 460,
          width: '100%',
          background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.4)} 0%, ${alpha(theme.palette.background.paper, 0.1)} 100%)`,
          backdropFilter: 'blur(24px)',
          borderRadius: 6,
          p: { xs: 4, md: 5 },
          border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
          boxShadow: `0 24px 48px -12px ${alpha(theme.palette.common.black, 0.3)}`,
          position: 'relative',
          zIndex: 1,
        }}
      >
        {/* Heading */}
        <Typography
          variant="h3"
          component="h1"
          align="center"
          gutterBottom
          sx={{
            fontWeight: 800,
            background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '-0.5px',
          }}
        >
          Welcome Back
        </Typography>

        <Typography variant="body2" align="center" color="text.secondary" sx={{ mb: 4 }}>
          Sign in to your health intelligence account
        </Typography>

        {/* Login Form */}
        <LoginForm onSubmit={handleLogin} error={error} loading={loading} />

        {/* Google Button */}
        <Box sx={{ mt: 3 }}>
          <Button
            fullWidth
            onClick={handleGoogleLogin}
            disabled={socialLoading || loading}
            sx={{
              py: 1.5,
              borderRadius: 3,
              borderColor: alpha(theme.palette.divider, 0.2),
              color: 'text.primary',
              background: alpha(theme.palette.background.paper, 0.4),
              backdropFilter: 'blur(10px)',
              fontSize: '1rem',
              fontWeight: 600,
              textTransform: 'none',
              border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
              '&:hover': {
                background: alpha(theme.palette.background.paper, 0.6),
                borderColor: theme.palette.primary.main,
              },
            }}
          >
            <svg width="24" height="24" viewBox="0 0 48 48" style={{ marginRight: 12 }}>
              <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
              <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
              <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
              <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
            </svg>
            {socialLoading ? 'Connecting...' : 'Continue with Google'}
          </Button>
        </Box>

        {/* Links */}
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="body2" color="text.secondary">
            Don't have an account?{' '}
            <RouterLink
              to="/register"
              style={{
                color: theme.palette.primary.main,
                textDecoration: 'none',
                fontWeight: 600,
              }}
            >
              Create one
            </RouterLink>
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};
