import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  Link,
  Divider,
} from '@mui/material';
import { Google as GoogleIcon } from '@mui/icons-material';
import { useAuthStore } from '@/stores/authStore';
import { apiService } from '@/services/api';

export function RegisterPage() {
  const navigate = useNavigate();
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

      // If we have profile data filled, try to update it (though usually Google login is instant)
      // For Google login, we might need a separate onboarding step if we want these fields mandatory
      // For now, we'll just navigate
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

    // Validate Profile Data
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
      // 1. Register with Firebase
      const { firebaseService } = await import('@/services/firebase');
      await firebaseService.registerWithEmail(email, password);

      // 2. Update Profile with Health Data
      // Note: We need to wait a bit for the token to be ready or just use the current session
      try {
        await apiService.updateUserProfile({
          age: parseInt(age),
          blood_pressure: bloodPressure,
          sugar_level: sugarLevel || null, // Optional
        });
      } catch (profileError) {
        console.error('Failed to update profile data:', profileError);
        // Continue anyway, as account is created
      }

      // 3. Navigate
      navigate('/app/dashboard');
    } catch (err: any) {
      setError(err.message || 'Registration failed');
      setLoading(false);
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
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ fontWeight: 'bold' }}>
            Create Account
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
            Register to access the AI Health Intelligence Platform
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {/* Google Login Button */}
          <Button
            fullWidth
            variant="outlined"
            startIcon={<GoogleIcon />}
            onClick={handleGoogleLogin}
            disabled={loading}
            sx={{
              mb: 3,
              height: 48,
              textTransform: 'none',
              fontSize: '1rem',
              borderColor: '#ddd',
              color: '#555',
              '&:hover': {
                borderColor: '#ccc',
                bgcolor: '#f5f5f5',
              }
            }}
          >
            Continue with Google
          </Button>

          <Divider sx={{ mb: 3 }}>
            <Typography variant="body2" color="text.secondary">
              OR REGISTER WITH EMAIL
            </Typography>
          </Divider>

          <form onSubmit={handleRegister}>
            {/* Account Info */}
            <TextField
              fullWidth
              label="Email Address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              margin="normal"
              required
              autoComplete="email"
            />

            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                margin="normal"
                required
                autoComplete="new-password"
                helperText="Min. 6 characters"
              />
              <TextField
                fullWidth
                label="Confirm Password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                margin="normal"
                required
                autoComplete="new-password"
              />
            </Box>

            <Typography variant="subtitle1" sx={{ mt: 3, mb: 1, fontWeight: 600 }}>
              Health Profile (Required)
            </Typography>

            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                fullWidth
                label="Age"
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                margin="normal"
                required
                InputProps={{ inputProps: { min: 0, max: 120 } }}
                placeholder="e.g. 30"
              />
              <TextField
                fullWidth
                label="Blood Pressure"
                value={bloodPressure}
                onChange={(e) => setBloodPressure(e.target.value)}
                margin="normal"
                required
                placeholder="e.g. 120/80"
                helperText="Systolic/Diastolic"
              />
            </Box>

            <TextField
              fullWidth
              label="Sugar Levels (Optional)"
              value={sugarLevel}
              onChange={(e) => setSugarLevel(e.target.value)}
              margin="normal"
              placeholder="e.g. 95 mg/dL"
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              sx={{
                mt: 4,
                mb: 2,
                height: 48,
                bgcolor: '#2563EB',
                fontSize: '1rem',
                fontWeight: 600,
                '&:hover': {
                  bgcolor: '#1D4ED8',
                }
              }}
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </Button>
          </form>

          <Box sx={{ textAlign: 'center', mt: 2 }}>
            <Typography variant="body2">
              Already have an account?{' '}
              <Link href="/login" underline="hover" sx={{ fontWeight: 600, color: '#2563EB' }}>
                Sign in
              </Link>
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}
