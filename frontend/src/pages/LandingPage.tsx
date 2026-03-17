import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  Stack,
  useTheme,
  alpha,
  Grid,
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  Security as SecurityIcon,
  TrendingUp as TrendingUpIcon,
  LocalHospital as LocalHospitalIcon,
  Psychology as PsychologyIcon,
  VerifiedUser as VerifiedUserIcon,
  HealthAndSafety as HealthAndSafetyIcon,
  SmartToy as SmartToyIcon,
  MonitorHeart as MonitorHeartIcon,
} from '@mui/icons-material';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();

  // Vibrant gradients based on Stitch MCP design
  const gradientPrimary = 'linear-gradient(135deg, #2b8cee 0%, #10b981 100%)';
  const isDark = theme.palette.mode === 'dark';

  const features = [
    {
      icon: <AssessmentIcon sx={{ fontSize: 32, color: '#2b8cee' }} />,
      title: 'Symptom Analysis',
      description: 'Deep dive into symptoms instantly with our AI model.',
      bgColor: alpha('#2b8cee', 0.1),
    },
    {
      icon: <MonitorHeartIcon sx={{ fontSize: 32, color: '#10b981' }} />,
      title: 'System Care',
      description: 'Holistic treatment paths across multiple medical disciplines.',
      bgColor: alpha('#10b981', 0.1),
    },
    {
      icon: <TrendingUpIcon sx={{ fontSize: 32, color: '#f59e0b' }} />,
      title: 'Health Tracking',
      description: 'Monitor your vital trends and health score over time.',
      bgColor: alpha('#f59e0b', 0.1),
    },
    {
      icon: <PsychologyIcon sx={{ fontSize: 32, color: '#8b5cf6' }} />,
      title: 'AI Insights',
      description: 'Receive clear, intelligent interpretation of health data.',
      bgColor: alpha('#8b5cf6', 0.1),
    },
    {
      icon: <SecurityIcon sx={{ fontSize: 32, color: '#3b82f6' }} />,
      title: 'Secure',
      description: 'Your health data is protected with enterprise-grade security.',
      bgColor: alpha('#3b82f6', 0.1),
    },
    {
      icon: <VerifiedUserIcon sx={{ fontSize: 32, color: '#14b8a6' }} />,
      title: 'Confidence',
      description: 'Every assessment includes reliable confidence metrics.',
      bgColor: alpha('#14b8a6', 0.1),
    },
  ];

  return (
    <Box 
      sx={{ 
        minHeight: '100vh', 
        display: 'flex', 
        flexDirection: 'column',
        bgcolor: isDark ? '#101922' : '#f6f7f8',
        fontFamily: "'Manrope', sans-serif",
        overflowX: 'hidden'
      }}
    >
      {/* Header */}
      <Box 
        component="header" 
        sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between', 
          px: 3, 
          py: 2, 
          position: 'sticky', 
          top: 0, 
          zIndex: 50,
          bgcolor: alpha(isDark ? '#101922' : '#f6f7f8', 0.8),
          backdropFilter: 'blur(12px)',
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`
        }}
      >
        <Stack direction="row" spacing={1.5} alignItems="center">
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              p: 1, 
              borderRadius: 3, 
              background: gradientPrimary, 
              color: 'white',
              boxShadow: '0 4px 12px rgba(43, 140, 238, 0.3)'
            }}
          >
            <HealthAndSafetyIcon />
          </Box>
          <Typography variant="h6" fontWeight="700" color="text.primary">
            AI Health
          </Typography>
        </Stack>
      </Box>

      <Box sx={{ flex: 1 }}>
        {/* Hero Section */}
        <Container maxWidth="lg" sx={{ px: { xs: 2, md: 3 }, py: { xs: 6, md: 10 } }}>
          <Box
            sx={{
              position: 'relative',
              overflow: 'hidden',
              borderRadius: { xs: 4, md: 6 },
              background: isDark 
                ? 'linear-gradient(135deg, rgba(43,140,238,0.1) 0%, rgba(16,185,129,0.05) 100%)'
                : 'linear-gradient(135deg, rgba(43,140,238,0.05) 0%, rgba(16,185,129,0.02) 100%)',
              p: { xs: 4, md: 8 },
              border: `1px solid ${isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'}`,
              boxShadow: isDark ? 'none' : '0 10px 40px rgba(0,0,0,0.02)'
            }}
          >
            {/* Glowing Orbs */}
            <Box 
              sx={{
                position: 'absolute',
                top: -80,
                right: -80,
                width: 200,
                height: 200,
                borderRadius: '50%',
                background: 'rgba(43, 140, 238, 0.2)',
                filter: 'blur(60px)',
                zIndex: 0
              }}
            />
            <Box 
              sx={{
                position: 'absolute',
                bottom: -80,
                left: -80,
                width: 200,
                height: 200,
                borderRadius: '50%',
                background: 'rgba(16, 185, 129, 0.2)',
                filter: 'blur(60px)',
                zIndex: 0
              }}
            />

            <Box sx={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 4 }}>
              <Box 
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  width: 80, 
                  height: 80, 
                  borderRadius: 6, 
                  bgcolor: isDark ? 'rgba(30,41,59,0.6)' : 'rgba(255,255,255,0.8)',
                  backdropFilter: 'blur(16px)',
                  boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
                  border: `1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(255,255,255,0.6)'}`,
                  mb: 1
                }}
              >
                <SmartToyIcon sx={{ fontSize: 44, color: '#2b8cee' }} />
              </Box>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxWidth: 700 }}>
                <Typography 
                  variant="h2" 
                  component="h1" 
                  fontWeight="800" 
                  lineHeight={1.2}
                  sx={{ 
                    color: 'text.primary',
                    fontSize: { xs: '2.5rem', md: '3.5rem' },
                    letterSpacing: '-1px'
                  }}
                >
                  Your Health, <Box component="span" sx={{ background: gradientPrimary, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Decoded</Box> by AI
                </Typography>
                <Typography 
                  variant="h6" 
                  fontWeight="500" 
                  color="text.secondary"
                  sx={{ mb: 2, maxWidth: 600, mx: 'auto', lineHeight: 1.6 }}
                >
                  Experience the future of personal wellness with our advanced health intelligence platform. Get accurate, multi-system insights instantly.
                </Typography>
              </Box>

              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ width: '100%', maxWidth: 400, justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={() => navigate('/register')}
                  sx={{
                    background: gradientPrimary,
                    color: 'white',
                    px: 4,
                    py: 1.8,
                    fontSize: '1.1rem',
                    fontWeight: 'bold',
                    borderRadius: 3,
                    boxShadow: '0 8px 24px rgba(43,140,238,0.3)',
                    textTransform: 'none',
                    flex: 1,
                    '&:hover': {
                      background: 'linear-gradient(135deg, #1e70c5 0%, #0d9468 100%)',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 12px 28px rgba(43,140,238,0.4)',
                    },
                    transition: 'all 0.2s ease-in-out',
                  }}
                >
                  Get Started
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => navigate('/login')}
                  sx={{
                    borderColor: alpha(theme.palette.text.primary, 0.2),
                    color: 'text.primary',
                    px: 4,
                    py: 1.8,
                    fontSize: '1.1rem',
                    fontWeight: 'bold',
                    borderRadius: 3,
                    textTransform: 'none',
                    bgcolor: 'transparent',
                    flex: 1,
                    '&:hover': {
                      borderColor: 'text.primary',
                      bgcolor: alpha(theme.palette.text.primary, 0.05),
                      transform: 'translateY(-2px)',
                    },
                    transition: 'all 0.2s ease-in-out',
                  }}
                >
                  Sign In
                </Button>
              </Stack>
            </Box>
          </Box>
        </Container>

        {/* Features Section */}
        <Container maxWidth="lg" sx={{ px: { xs: 2, md: 3 }, py: { xs: 4, md: 8 } }}>
          <Box sx={{ mb: 6, display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Typography variant="h3" fontWeight="800" color="text.primary">
              Intelligent Care
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Comprehensive insights powered by state-of-the-art AI models.
            </Typography>
          </Box>

          <Grid container spacing={3}>
            {features.map((feature, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    bgcolor: isDark ? alpha('#0f172a', 0.6) : '#ffffff',
                    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                    borderRadius: 4,
                    boxShadow: isDark ? 'none' : '0 4px 20px rgba(0,0,0,0.03)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-6px)',
                      boxShadow: isDark 
                        ? '0 12px 40px rgba(0,0,0,0.4)'
                        : '0 12px 40px rgba(0,0,0,0.08)',
                      borderColor: alpha('#2b8cee', 0.3),
                    },
                  }}
                >
                  <CardContent sx={{ p: 4, flexGrow: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Box 
                      sx={{ 
                        width: 56, 
                        height: 56, 
                        borderRadius: 3, 
                        bgcolor: feature.bgColor, 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center',
                        mb: 1
                      }}
                    >
                      {feature.icon}
                    </Box>
                    <Box>
                      <Typography variant="h6" fontWeight="700" color="text.primary" gutterBottom>
                        {feature.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" lineHeight={1.6}>
                        {feature.description}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>

        {/* Mini Dashboard Preview */}
        <Container maxWidth="lg" sx={{ px: { xs: 2, md: 3 }, py: { xs: 4, md: 8 }, mb: 4 }}>
          <Box
            sx={{
              position: 'relative',
              overflow: 'hidden',
              borderRadius: { xs: 4, md: 6 },
              bgcolor: '#0f172a',
              color: 'white',
              p: { xs: 4, md: 6 },
              boxShadow: '0 24px 48px rgba(0,0,0,0.2)',
            }}
          >
            <Box 
              sx={{
                position: 'absolute',
                right: -40,
                top: -40,
                opacity: 0.1,
                transform: 'scale(2)'
              }}
            >
              <TrendingUpIcon sx={{ fontSize: 200 }} />
            </Box>
            
            <Box sx={{ position: 'relative', zIndex: 1 }}>
              <Typography variant="h5" fontWeight="700" mb={4}>
                Daily Activity Preview
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 2, height: 160, mb: 4 }}>
                <Box sx={{ flex: 1, bgcolor: alpha('#2b8cee', 0.4), borderRadius: '8px 8px 0 0', height: '60%' }} />
                <Box sx={{ flex: 1, bgcolor: alpha('#2b8cee', 0.6), borderRadius: '8px 8px 0 0', height: '85%' }} />
                <Box sx={{ flex: 1, bgcolor: alpha('#2b8cee', 0.4), borderRadius: '8px 8px 0 0', height: '45%' }} />
                <Box sx={{ flex: 1, bgcolor: '#10b981', borderRadius: '8px 8px 0 0', height: '100%', boxShadow: '0 0 20px rgba(16,185,129,0.4)' }} />
                <Box sx={{ flex: 1, bgcolor: alpha('#2b8cee', 0.5), borderRadius: '8px 8px 0 0', height: '70%' }} />
              </Box>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid rgba(255,255,255,0.1)', pt: 3 }}>
                <Box>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)', textTransform: 'uppercase', letterSpacing: 1, fontWeight: 'bold' }}>
                    Overall Health Score
                  </Typography>
                  <Typography variant="h3" fontWeight="800" sx={{ color: '#10b981', mt: 0.5 }}>
                    92%
                  </Typography>
                </Box>
                <Box 
                  sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    width: 48, 
                    height: 48, 
                    borderRadius: '50%', 
                    bgcolor: alpha('#10b981', 0.2) 
                  }}
                >
                  <TrendingUpIcon sx={{ color: '#10b981' }} />
                </Box>
              </Box>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* Footer */}
      <Box 
        component="footer" 
        sx={{ 
          py: 4, 
          px: 3, 
          bgcolor: isDark ? 'rgba(15,23,42,0.8)' : '#ffffff',
          borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
          backdropFilter: 'blur(12px)'
        }}
      >
        <Container maxWidth="lg" sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, justifyContent: 'space-between', alignItems: 'center', gap: 2 }}>
          <Stack direction="row" spacing={1} alignItems="center">
            <HealthAndSafetyIcon sx={{ color: '#2b8cee' }} />
            <Typography variant="subtitle1" fontWeight="700">
              AI Health Intelligence
            </Typography>
          </Stack>
          <Typography variant="body2" color="text.secondary">
            © {new Date().getFullYear()} AI Health. All rights reserved. Not a substitute for professional medical advice.
          </Typography>
        </Container>
      </Box>
    </Box>
  );
};
