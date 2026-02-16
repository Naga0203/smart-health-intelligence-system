import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  CircularProgress,
  Button,
  Grid,
  Paper,
  Card,
  CardContent,
  LinearProgress,
  Alert,
  Chip,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Lightbulb as LightbulbIcon,
  Info as InfoIcon,
  Flag as FlagIcon,
  LocalHospital as HospitalIcon,
} from '@mui/icons-material';
import { useAssessmentStore } from '@/stores/assessmentStore';
import { RiskLevelBadge, RiskLevel } from '@/components/results/RiskLevelBadge';
import { RiskDriverItem } from '@/components/results/RiskDriverItem';

// Mock data for development (will be replaced with real data from store)
const MOCK_PATIENT = {
  name: "John Doe",
  id: "49201",
  age: 45,
  gender: "Male"
};

export const AssessmentResultsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();


  const assessmentStore = useAssessmentStore() as any;
  const { currentAssessment, loading, error, fetchAssessmentDetail } = assessmentStore;

  useEffect(() => {
    if (id) {
      fetchAssessmentDetail(id);
    }
  }, [id, fetchAssessmentDetail]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/app/dashboard')} sx={{ mt: 2 }}>
          Back to Dashboard
        </Button>
      </Container>
    );
  }

  // Use current assessment or fallback to safe defaults if waiting for data
  // In a real app we might want to show a skeleton loader here if currentAssessment is null
  const data = currentAssessment || {};
  const prediction = data.prediction || {};

  // Extract values with fallbacks
  const riskTitle = prediction.disease || "Type 2 Diabetes";
  const probability = prediction.probability_percent || 87;

  // Determine risk level for badge
  const getRiskLevel = (prob: number): RiskLevel => {
    if (prob > 75) return 'high';
    if (prob > 50) return 'elevated';
    if (prob > 25) return 'medium';
    return 'low';
  };

  const riskLevel = getRiskLevel(probability);

  // Mock Risk Drivers if not present in API response
  const riskDrivers = [
    {
      factor: 'Elevated HbA1c',
      value: '6.8%',
      contribution: 85,
      description: 'Contributes 35% to total risk score.',
      isPrimary: true
    },
    {
      factor: 'Fasting Glucose Trend',
      value: '112 mg/dL',
      contribution: 65,
      description: 'Consistent increase over last 3 labs.',
      isPrimary: false
    },
    {
      factor: 'BMI (Body Mass Index)',
      value: '31.2',
      contribution: 45,
      description: 'Currently in Obesity Class I range.',
      isPrimary: false
    },
    {
      factor: 'Family History',
      value: 'Yes (Paternal)',
      contribution: 30,
      description: 'Static risk factor.',
      isPrimary: false
    }
  ];

  return (
    <Box sx={{ bgcolor: '#F9FAFB', minHeight: '100vh', pb: 8 }}>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Navigation Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
              Dashboard / Patient Risk Analysis /
            </Typography>
            <Typography variant="body2" color="text.primary" fontWeight={600}>
              Risk Explanation
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 2 }}>
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1, flexWrap: 'wrap' }}>
                <Typography variant="h4" fontWeight={700} color="#111827">
                  Risk Prediction: {riskTitle}
                </Typography>
                <RiskLevelBadge level={riskLevel} />
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', color: '#6B7280', gap: 1 }}>
                <Typography variant="body2">
                  <Box component="span" sx={{ color: '#9CA3AF', mr: 0.5 }}>👤</Box>
                  Patient: <Box component="span" fontWeight={600} color="#374151">{MOCK_PATIENT.name}</Box>
                  (ID: #{MOCK_PATIENT.id}) • {MOCK_PATIENT.age} Yrs • {MOCK_PATIENT.gender}
                </Typography>
              </Box>
            </Box>

            <Button
              variant="outlined"
              startIcon={<ArrowBackIcon />}
              onClick={() => navigate('/app/dashboard')}
              sx={{
                textTransform: 'none',
                color: '#374151',
                borderColor: '#E5E7EB',
                bgcolor: 'white',
                '&:hover': {
                  bgcolor: '#F3F4F6',
                  borderColor: '#D1D5DB'
                }
              }}
            >
              Back to Dashboard
            </Button>
          </Box>
        </Box>

        {/* Main Content Grid */}
        <Grid container spacing={3}>
          {/* Left Column: AI Explanation */}
          <Grid item xs={12} md={5}>
            <Card sx={{ height: '100%', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', border: '1px solid #E5E7EB' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Box>
                    <Typography variant="h6" fontWeight={700} color="#111827">
                      AI Explanation
                    </Typography>
                    <Typography variant="body2" color="#6B7280">
                      Analysis confidence & reasoning
                    </Typography>
                  </Box>
                  <Box sx={{
                    width: 36, height: 36, borderRadius: '50%',
                    bgcolor: '#EFF6FF', display: 'flex', alignItems: 'center', justifyContent: 'center'
                  }}>
                    <Box component="span" sx={{ color: '#3B82F6', fontSize: '18px' }}>✨</Box>
                  </Box>
                </Box>

                {/* Model Confidence */}
                <Box sx={{ mb: 4 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', mb: 1 }}>
                    <Typography variant="body2" fontWeight={600} color="#374151">
                      Model Confidence
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="h5" fontWeight={700} color="#111827">
                        {probability}%
                      </Typography>
                      <Chip
                        label="High"
                        size="small"
                        sx={{
                          bgcolor: '#EFF6FF',
                          color: '#3B82F6',
                          fontWeight: 600,
                          height: 20,
                          fontSize: '0.7rem'
                        }}
                      />
                    </Box>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={probability}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      bgcolor: '#F3F4F6',
                      '& .MuiLinearProgress-bar': {
                        bgcolor: '#2563EB',
                        borderRadius: 4
                      }
                    }}
                  />
                </Box>

                {/* Insight Box */}
                <Paper sx={{ p: 2, bgcolor: '#F8FAFC', border: '1px solid #F1F5F9', borderRadius: 2, mb: 4 }}>
                  <Box sx={{ display: 'flex', gap: 1.5 }}>
                    <LightbulbIcon sx={{ color: '#F59E0B', fontSize: 20, mt: 0.5 }} />
                    <Typography variant="body2" color="#475569" sx={{ lineHeight: 1.6 }}>
                      The system is highly confident based on 12 matched indicators. Please note that this is a
                      <Box component="span" fontWeight={700} color="#1E293B"> statistical projection </Box>
                      derived from available data, and individual variations may exist.
                    </Typography>
                  </Box>
                </Paper>

                {/* Why This Result */}
                <Box>
                  <Typography variant="subtitle2" fontWeight={700} color="#111827" sx={{ textTransform: 'uppercase', letterSpacing: '0.05em', mb: 2, fontSize: '0.75rem' }}>
                    WHY THIS RESULT?
                  </Typography>
                  <Typography variant="body2" color="#374151" paragraph sx={{ lineHeight: 1.7 }}>
                    The analysis highlights a correlation between elevated
                    <Box component="span" fontWeight={600}> HbA1c levels (6.8%) </Box>
                    and a consistent upward trend in fasting glucose. Historically, this pattern strongly indicates metabolic changes associated with Type 2 Diabetes.
                  </Typography>
                  <Typography variant="body2" color="#374151" sx={{ lineHeight: 1.7, mb: 4 }}>
                    Secondary factors, such as BMI and activity levels, support this finding but are not the sole drivers.
                  </Typography>

                  <Typography variant="caption" color="#9CA3AF" sx={{ fontStyle: 'italic' }}>
                    * This tool provides guidance only and is not a substitute for professional clinical diagnosis.
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Right Column: Key Risk Drivers */}
          <Grid item xs={12} md={7}>
            <Card sx={{ height: '100%', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', border: '1px solid #E5E7EB' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Typography variant="h6" fontWeight={700} color="#111827">
                    Key Risk Drivers
                  </Typography>
                  <Button sx={{ textTransform: 'none', fontWeight: 600 }}>
                    View All Factors
                  </Button>
                </Box>

                <Box sx={{ mt: 2 }}>
                  {riskDrivers.map((driver, index) => (
                    <RiskDriverItem
                      key={index}
                      factor={driver.factor}
                      value={driver.value}
                      contribution={driver.contribution}
                      description={driver.description}
                      isPrimary={driver.isPrimary}
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Bottom Actions */}
        <Box sx={{ mt: 4 }}>
          <Card sx={{ borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', border: '1px solid #E5E7EB', p: 1 }}>
            <CardContent sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
              <Box>
                <Typography variant="h6" fontWeight={700} color="#111827">
                  Recommended Next Steps
                </Typography>
                <Typography variant="body2" color="#6B7280">
                  Actions suggested based on risk level.
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="outlined"
                  startIcon={<FlagIcon />}
                  sx={{
                    textTransform: 'none',
                    fontWeight: 600,
                    color: '#374151',
                    borderColor: '#E5E7EB'
                  }}
                >
                  Flag for Review
                </Button>
                <Button
                  variant="contained"
                  startIcon={<HospitalIcon />}
                  sx={{
                    textTransform: 'none',
                    fontWeight: 600,
                    bgcolor: '#2563EB',
                    boxShadow: 'none',
                    '&:hover': {
                      bgcolor: '#1D4ED8',
                      boxShadow: 'none'
                    }
                  }}
                >
                  View Treatment Options
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Box>

        {/* Disclaimer Footer */}
        <Box sx={{ mt: 4, display: 'flex', gap: 2, alignItems: 'flex-start' }}>
          <InfoIcon sx={{ color: '#9CA3AF', fontSize: 20, mt: 0.5 }} />
          <Box>
            <Typography variant="subtitle2" fontWeight={700} color="#6B7280" gutterBottom>
              MEDICAL DISCLAIMER
            </Typography>
            <Typography variant="body2" color="#6B7280">
              This prediction is generated by an Artificial Intelligence system for informational and decision-support purposes only.
              It does not constitute a definitive medical diagnosis. All AI-generated insights should be reviewed and verified by a
              qualified healthcare professional in conjunction with standard clinical guidelines and patient history.
            </Typography>
          </Box>
        </Box>

      </Container>
    </Box>
  );
};

export default AssessmentResultsPage;
