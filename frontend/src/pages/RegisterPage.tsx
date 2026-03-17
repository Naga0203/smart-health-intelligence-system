// ============================================================================
// Register Page — Redesigned UI
// ============================================================================

import { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { Alert, Box, Typography, Button, useTheme, alpha } from '@mui/material';
import { useAuthStore } from '@/stores/authStore';
import { apiService } from '@/services/api';



interface StyledInputProps {
  type?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder: string;
  required?: boolean;
  disabled?: boolean;
  autoComplete?: string;
  min?: number;
  max?: number;
}

const StyledInput: React.FC<StyledInputProps> = ({
  type = 'text',
  value,
  onChange,
  placeholder,
  required,
  disabled,
  autoComplete,
  min,
  max,
}) => {
  const [focused, setFocused] = useState(false);
  const theme = useTheme();

  return (
    <input
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      required={required}
      disabled={disabled}
      autoComplete={autoComplete}
      min={min}
      max={max}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      style={{
        width: '100%',
        background: alpha(theme.palette.background.paper, 0.4),
        border: `1px solid ${focused ? theme.palette.primary.main : alpha(theme.palette.divider, 0.2)}`,
        padding: '16px 22px',
        borderRadius: '16px',
        marginTop: '12px',
        boxShadow: focused ? `0 0 0 3px ${alpha(theme.palette.primary.main, 0.2)}` : 'none',
        outline: 'none',
        fontSize: '15px',
        color: theme.palette.text.primary,
        boxSizing: 'border-box',
        transition: 'all 0.2s',
        fontFamily: theme.typography.fontFamily,
      }}
    />
  );
};

export function RegisterPage() {
  const navigate = useNavigate();
  const theme = useTheme();
  const { loginWithGoogle } = useAuthStore();

  // Auth State
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Profile State
  const [age, setAge] = useState('');
  const [bloodPressure, setBloodPressure] = useState('');
  const [sugarLevel, setSugarLevel] = useState('');

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Handle Google Login
  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      setError('');
      await loginWithGoogle();
      navigate('/app/dashboard');
    } catch (err: any) {
      setError(err.message || 'Google sign-in failed');
      setLoading(false);
    }
  };

  // Handle Email Registration
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    if (!age || parseInt(age) < 0 || parseInt(age) > 120) {
      setError('Please enter a valid age');
      return;
    }

    if (!bloodPressure) {
      setError('Blood pressure is required');
      return;
    }

    setLoading(true);
    try {
      const { firebaseService } = await import('@/services/firebase');
      await firebaseService.registerWithEmail(email, password);

      try {
        await apiService.updateUserProfile({
          age: parseInt(age),
          blood_pressure: bloodPressure,
          sugar_level: sugarLevel || null,
        });
      } catch (profileError) {
        console.error('Failed to update profile data:', profileError);
      }

      navigate('/app/dashboard');
    } catch (err: any) {
      setError(err.message || 'Registration failed');
      setLoading(false);
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
          maxWidth: 520,
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
          Create Account
        </Typography>

        <Typography variant="body2" align="center" color="text.secondary" sx={{ mb: 4 }}>
          Register for AI Health Intelligence
        </Typography>

        {/* Error */}
        {error && (
          <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>
            {error}
          </Alert>
        )}

        {/* Google Button */}
        <Box sx={{ mb: 3 }}>
          <Button
            fullWidth
            onClick={handleGoogleLogin}
            disabled={loading}
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
            {loading ? 'Connecting...' : 'Continue with Google'}
          </Button>
        </Box>

        {/* Divider */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Box sx={{ flex: 1, height: '1px', background: alpha(theme.palette.divider, 0.2) }} />
          <Typography variant="caption" color="text.secondary" fontWeight="600" sx={{ letterSpacing: 1 }}>
            OR REGISTER WITH EMAIL
          </Typography>
          <Box sx={{ flex: 1, height: '1px', background: alpha(theme.palette.divider, 0.2) }} />
        </Box>

        {/* Registration Form */}
        <form onSubmit={handleRegister}>
          {/* Account Fields */}
          <StyledInput
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="E-mail"
            required
            disabled={loading}
            autoComplete="email"
          />

          <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
            <Box sx={{ flex: 1 }}>
              <StyledInput
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                required
                disabled={loading}
                autoComplete="new-password"
              />
            </Box>
            <Box sx={{ flex: 1 }}>
              <StyledInput
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm Password"
                required
                disabled={loading}
                autoComplete="new-password"
              />
            </Box>
          </Box>

          {/* Health Profile Section */}
          <Typography
            variant="subtitle2"
            sx={{
              fontWeight: 700,
              color: theme.palette.primary.main,
              mt: 3,
              ml: 1,
            }}
          >
            Health Profile
          </Typography>

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Box sx={{ flex: 1 }}>
              <StyledInput
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                placeholder="Age"
                required
                disabled={loading}
                min={0}
                max={120}
              />
            </Box>
            <Box sx={{ flex: 1 }}>
              <StyledInput
                type="text"
                value={bloodPressure}
                onChange={(e) => setBloodPressure(e.target.value)}
                placeholder="Blood Pressure (e.g. 120/80)"
                required
                disabled={loading}
              />
            </Box>
          </Box>

          <StyledInput
            type="text"
            value={sugarLevel}
            onChange={(e) => setSugarLevel(e.target.value)}
            placeholder="Sugar Level (optional, e.g. 95 mg/dL)"
            disabled={loading}
          />

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              display: 'block',
              width: '100%',
              fontWeight: 600,
              background: theme.palette.primary.main,
              color: 'white',
              padding: '16px 0',
              margin: '28px auto 0',
              borderRadius: '16px',
              boxShadow: `0 8px 24px ${alpha(theme.palette.primary.main, 0.4)}`,
              border: 'none',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '16px',
              letterSpacing: '0.3px',
              transition: 'all 0.2s ease-in-out',
              opacity: loading ? 0.8 : 1,
              fontFamily: theme.typography.fontFamily,
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(-2px)';
                (e.currentTarget as HTMLButtonElement).style.boxShadow = `0 12px 28px ${alpha(theme.palette.primary.main, 0.6)}`;
                (e.currentTarget as HTMLButtonElement).style.background = theme.palette.primary.dark;
              }
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(0)';
              (e.currentTarget as HTMLButtonElement).style.boxShadow = `0 8px 24px ${alpha(theme.palette.primary.main, 0.4)}`;
              (e.currentTarget as HTMLButtonElement).style.background = theme.palette.primary.main;
            }}
            onMouseDown={(e) => {
              if (!loading) {
                (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(1px)';
              }
            }}
            onMouseUp={(e) => {
              if (!loading) {
                (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(-2px)';
              }
            }}
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        {/* Sign in link */}
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="body2" color="text.secondary">
            Already have an account?{' '}
            <RouterLink
              to="/login"
              style={{
                color: theme.palette.primary.main,
                textDecoration: 'none',
                fontWeight: 600,
              }}
            >
              Sign in
            </RouterLink>
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
