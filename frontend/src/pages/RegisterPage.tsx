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
import ButtonColorful from '@/components/ui/button-colorful';
import { ShinyButton } from '@/components/ui/shiny-button';

const GoogleIconSvg = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20">
    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
  </svg>
);
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
        <Paper className="card-gradient" elevation={0} sx={{ p: 4, width: '100%' }}>
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
          <ButtonColorful
            className="w-full text-base font-medium h-12 mb-6"
            onClick={handleGoogleLogin}
            disabled={loading}
          >
            <GoogleIconSvg />
            <span>Continue with Google</span>
          </ButtonColorful>

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

            <ShinyButton
              type="submit"
              className="w-full mt-8 mb-4 h-12"
              disabled={loading}
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </ShinyButton>
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
