// ============================================================================
// Landing Page - Entry Point for AI Health Intelligence Platform
// ============================================================================

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
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  Security as SecurityIcon,
  TrendingUp as TrendingUpIcon,
  LocalHospital as LocalHospitalIcon,
  Psychology as PsychologyIcon,
  VerifiedUser as VerifiedUserIcon,
} from '@mui/icons-material';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();

  const features = [
    {
      icon: <AssessmentIcon sx={{ fontSize: 48, color: 'primary.main' }} />,
      title: 'Symptom Analysis',
      description: 'Enter your symptoms and receive AI-powered health risk assessments with clear confidence indicators.',
    },
    {
      icon: <LocalHospitalIcon sx={{ fontSize: 48, color: 'primary.main' }} />,
      title: 'Multi-System Treatment',
      description: 'Explore treatment options from Modern Medicine, Ayurveda, Homeopathy, and Lifestyle approaches.',
    },
    {
      icon: <TrendingUpIcon sx={{ fontSize: 48, color: 'primary.main' }} />,
      title: 'Health Tracking',
      description: 'Track your health assessments over time with visual trend analysis and historical data.',
    },
    {
      icon: <PsychologyIcon sx={{ fontSize: 48, color: 'primary.main' }} />,
      title: 'AI Interpretation',
      description: 'Receive clear, transparent AI explanations that emphasize uncertainty and avoid diagnostic certainty.',
    },
    {
      icon: <SecurityIcon sx={{ fontSize: 48, color: 'primary.main' }} />,
      title: 'Secure & Private',
      description: 'Your health data is protected with enterprise-grade security and Firebase authentication.',
    },
    {
      icon: <VerifiedUserIcon sx={{ fontSize: 48, color: 'primary.main' }} />,
      title: 'Confidence Levels',
      description: 'Every assessment includes confidence metrics so you understand the reliability of predictions.',
    },
  ];

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Hero Section */}
      <Box
        sx={{
          background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
          color: 'white',
          py: { xs: 8, md: 12 },
          px: 2,
        }}
      >
        <Container maxWidth="lg">
          <Box
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', md: 'row' },
              alignItems: 'center',
              gap: 4,
            }}
          >
            <Box sx={{ flex: { xs: '1', md: '0 0 58%' } }}>
              <Typography
                variant="h1"
                component="h1"
                gutterBottom
                sx={{
                  fontWeight: 700,
                  mb: 3,
                }}
              >
                AI Health Intelligence Platform
              </Typography>
              <Typography
                variant="h5"
                component="p"
                sx={{
                  mb: 4,
                  opacity: 0.95,
                  lineHeight: 1.6,
                }}
              >
                Your personal health assessment companion. Get AI-powered risk assessments
                with transparent confidence levels and multi-system treatment insights.
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  mb: 4,
                  opacity: 0.9,
                  fontStyle: 'italic',
                }}
              >
                Note: This platform provides educational health information and is not a
                substitute for professional medical diagnosis or treatment.
              </Typography>
              <Stack
                direction={{ xs: 'column', sm: 'row' }}
                spacing={2}
                sx={{ mb: 2 }}
              >
                <Button
                  variant="contained"
                  size="large"
                  onClick={() => navigate('/register')}
                  sx={{
                    bgcolor: 'white',
                    color: 'primary.main',
                    px: 4,
                    py: 1.5,
                    fontSize: '1.1rem',
                    '&:hover': {
                      bgcolor: 'grey.100',
                    },
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
                    px: 4,
                    py: 1.5,
                    fontSize: '1.1rem',
                    '&:hover': {
                      borderColor: 'white',
                      bgcolor: 'rgba(255, 255, 255, 0.1)',
                    },
                  }}
                >
                  Sign In
                </Button>
              </Stack>
            </Box>
            <Box sx={{ flex: { xs: '1', md: '0 0 42%' } }}>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                }}
              >
                <Box
                  sx={{
                    width: '100%',
                    maxWidth: 400,
                    height: 300,
                    bgcolor: 'rgba(255, 255, 255, 0.1)',
                    borderRadius: 4,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backdropFilter: 'blur(10px)',
                  }}
                >
                  <LocalHospitalIcon sx={{ fontSize: 120, opacity: 0.8 }} />
                </Box>
              </Box>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* Features Section */}
      <Box sx={{ py: { xs: 6, md: 10 }, bgcolor: 'background.default' }}>
        <Container maxWidth="lg">
          <Typography
            variant="h2"
            component="h2"
            align="center"
            gutterBottom
            sx={{ mb: 2 }}
          >
            Key Features
          </Typography>
          <Typography
            variant="body1"
            align="center"
            color="text.secondary"
            sx={{ mb: 6, maxWidth: 700, mx: 'auto' }}
          >
            Our platform combines advanced AI technology with transparent communication
            to help you understand your health better.
          </Typography>

          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                sm: 'repeat(2, 1fr)',
                md: 'repeat(3, 1fr)',
              },
              gap: 4,
            }}
          >
            {features.map((feature, index) => (
              <Card
                key={index}
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4,
                  },
                }}
              >
                <CardContent sx={{ flexGrow: 1, textAlign: 'center', p: 3 }}>
                  <Box sx={{ mb: 2 }}>{feature.icon}</Box>
                  <Typography variant="h5" component="h3" gutterBottom>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            ))}
          </Box>
        </Container>
      </Box>

      {/* How It Works Section */}
      <Box sx={{ py: { xs: 6, md: 10 }, bgcolor: 'background.paper' }}>
        <Container maxWidth="lg">
          <Typography
            variant="h2"
            component="h2"
            align="center"
            gutterBottom
            sx={{ mb: 6 }}
          >
            How It Works
          </Typography>

          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                md: 'repeat(3, 1fr)',
              },
              gap: 4,
            }}
          >
            <Box sx={{ textAlign: 'center' }}>
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  bgcolor: 'primary.main',
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '2rem',
                  fontWeight: 'bold',
                  mx: 'auto',
                  mb: 2,
                }}
              >
                1
              </Box>
              <Typography variant="h5" gutterBottom>
                Enter Symptoms
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Describe your symptoms with severity and duration. Add demographic
                information and optional vitals for better accuracy.
              </Typography>
            </Box>

            <Box sx={{ textAlign: 'center' }}>
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  bgcolor: 'primary.main',
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '2rem',
                  fontWeight: 'bold',
                  mx: 'auto',
                  mb: 2,
                }}
              >
                2
              </Box>
              <Typography variant="h5" gutterBottom>
                AI Analysis
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Our AI model analyzes your input and generates risk assessments with
                clear confidence indicators and data quality scores.
              </Typography>
            </Box>

            <Box sx={{ textAlign: 'center' }}>
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  bgcolor: 'primary.main',
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '2rem',
                  fontWeight: 'bold',
                  mx: 'auto',
                  mb: 2,
                }}
              >
                3
              </Box>
              <Typography variant="h5" gutterBottom>
                Review Results
              </Typography>
              <Typography variant="body2" color="text.secondary">
                View your risk assessment, explore treatment options from multiple
                systems, and track your health over time.
              </Typography>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* Call to Action Section */}
      <Box
        sx={{
          py: { xs: 6, md: 8 },
          bgcolor: 'primary.main',
          color: 'white',
        }}
      >
        <Container maxWidth="md">
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h3" component="h2" gutterBottom>
              Ready to Get Started?
            </Typography>
            <Typography variant="body1" sx={{ mb: 4, opacity: 0.95 }}>
              Create your free account today and start your journey to better health
              understanding.
            </Typography>
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={2}
              justifyContent="center"
            >
              <Button
                variant="contained"
                size="large"
                onClick={() => navigate('/register')}
                sx={{
                  bgcolor: 'white',
                  color: 'primary.main',
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  '&:hover': {
                    bgcolor: 'grey.100',
                  },
                }}
              >
                Create Account
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => navigate('/login')}
                sx={{
                  borderColor: 'white',
                  color: 'white',
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  '&:hover': {
                    borderColor: 'white',
                    bgcolor: 'rgba(255, 255, 255, 0.1)',
                  },
                }}
              >
                Sign In
              </Button>
            </Stack>
          </Box>
        </Container>
      </Box>

      {/* Footer */}
      <Box
        component="footer"
        sx={{
          py: 4,
          px: 2,
          bgcolor: 'grey.900',
          color: 'white',
          mt: 'auto',
        }}
      >
        <Container maxWidth="lg">
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                sm: 'repeat(2, 1fr)',
                md: 'repeat(3, 1fr)',
              },
              gap: 4,
            }}
          >
            <Box>
              <Typography variant="h6" gutterBottom>
                AI Health Intelligence
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Empowering individuals with transparent, AI-powered health insights.
              </Typography>
            </Box>

            <Box>
              <Typography variant="h6" gutterBottom>
                Quick Links
              </Typography>
              <Stack spacing={1}>
                <Button
                  color="inherit"
                  onClick={() => navigate('/login')}
                  sx={{ justifyContent: 'flex-start', textTransform: 'none' }}
                >
                  Sign In
                </Button>
                <Button
                  color="inherit"
                  onClick={() => navigate('/register')}
                  sx={{ justifyContent: 'flex-start', textTransform: 'none' }}
                >
                  Create Account
                </Button>
              </Stack>
            </Box>

            <Box>
              <Typography variant="h6" gutterBottom>
                Important Notice
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                This platform provides educational information only and is not a
                substitute for professional medical advice, diagnosis, or treatment.
                Always consult with qualified healthcare providers.
              </Typography>
            </Box>
          </Box>

          <Box sx={{ mt: 4, pt: 3, borderTop: '1px solid rgba(255,255,255,0.1)' }}>
            <Typography variant="body2" align="center" sx={{ opacity: 0.7 }}>
              © {new Date().getFullYear()} AI Health Intelligence Platform. All rights
              reserved.
            </Typography>
          </Box>
        </Container>
      </Box>
    </Box>
  );
};
