// ============================================================================
// Landing Page
// ============================================================================

import { Box, Container, Typography, Button, Stack } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { LocalHospital } from '@mui/icons-material';

export const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Container maxWidth="md">
        <Box textAlign="center" color="white">
          <LocalHospital sx={{ fontSize: 80, mb: 2 }} />
          
          <Typography variant="h2" component="h1" gutterBottom fontWeight="bold">
            AI Health Intelligence Platform
          </Typography>
          
          <Typography variant="h5" paragraph sx={{ mb: 4, opacity: 0.9 }}>
            Medical-grade AI-powered health risk assessment with multi-system treatment awareness
          </Typography>

          <Stack direction="row" spacing={2} justifyContent="center">
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/login')}
              sx={{
                bgcolor: 'white',
                color: '#667eea',
                '&:hover': { bgcolor: '#f0f0f0' },
                px: 4,
                py: 1.5,
              }}
            >
              Get Started
            </Button>
            
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate('/login')}
              sx={{
                borderColor: 'white',
                color: 'white',
                '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' },
                px: 4,
                py: 1.5,
              }}
            >
              Login
            </Button>
          </Stack>

          <Box mt={6}>
            <Typography variant="body2" sx={{ opacity: 0.8 }}>
              ⚠️ This is not a medical diagnosis tool. Always consult healthcare professionals.
            </Typography>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};
