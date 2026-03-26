import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
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
import { useAuthStore } from '@/stores/authStore';
import { useUserStore } from '@/stores/userStore';
import { RiskLevelBadge, RiskLevel } from '@/components/results/RiskLevelBadge';
import { RiskDriverItem } from '@/components/results/RiskDriverItem';

export const AssessmentResultsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  const assessmentStore = useAssessmentStore() as any;
  const { currentAssessment, loading, error, fetchAssessmentDetail } = assessmentStore;

  const { user } = useAuthStore();
  const { profile } = useUserStore();

  // Use state data if available (from prediction), otherwise fetch from API
  const [localAssessment, setLocalAssessment] = useState((location.state as any)?.result || null);
  const [showAllFactors, setShowAllFactors] = useState(false);

  useEffect(() => {
    // Only fetch from API if we don't have local data
    if (id && !localAssessment) {
      fetchAssessmentDetail(id).catch((err: any) => {
        // If fetch fails (e.g., not authenticated), keep using local data
        console.warn('Could not fetch assessment:', err);
      });
    }
  }, [id, localAssessment, fetchAssessmentDetail]);

  // Use local data if available, otherwise use store data
  const data = localAssessment || currentAssessment || {};

  if (loading && !localAssessment) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error && !localAssessment) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/app/dashboard')} sx={{ mt: 2 }}>
          Back to Dashboard
        </Button>
      </Container>
    );
  }

  // Use local assessment or current assessment from store
  // In a real app we might want to show a skeleton loader here if both are null
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

  // Extract explanation data from API response
  const explanation = data.explanation || {};
  const contributingFactors = explanation.contributing_factors || {};
  
  // Build risk drivers from actual API data
  const buildRiskDrivers = () => {
    const drivers = [];
    
    // Add primary symptoms as risk drivers
    if (contributingFactors.primary_symptoms && contributingFactors.primary_symptoms.length > 0) {
      contributingFactors.primary_symptoms.forEach((symptom: string, index: number) => {
        drivers.push({
          factor: symptom.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
          value: 'Present',
          contribution: 80 - (index * 10),
          description: 'Primary indicator for this condition.',
          isPrimary: true
        });
      });
    }
    
    // Add supporting symptoms as risk drivers
    if (contributingFactors.supporting_symptoms && contributingFactors.supporting_symptoms.length > 0) {
      contributingFactors.supporting_symptoms.forEach((symptom: string, index: number) => {
        drivers.push({
          factor: symptom.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
          value: 'Present',
          contribution: 60 - (index * 10),
          description: 'Supporting indicator.',
          isPrimary: false
        });
      });
    }
    
    // Add general symptoms
    if (contributingFactors.general_symptoms && contributingFactors.general_symptoms.length > 0) {
      contributingFactors.general_symptoms.forEach((symptom: string, index: number) => {
        drivers.push({
          factor: symptom.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
          value: 'Present',
          contribution: 40 - (index * 10),
          description: 'General symptom.',
          isPrimary: false
        });
      });
    }
    
    // If no symptoms data, return empty array
    return drivers;
  };
  
  const riskDrivers = buildRiskDrivers();

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
                  {user?.displayName || user?.email || 'User'}
                  {profile?.age ? ` • ${profile.age} Yrs` : ''}
                  {profile?.gender ? ` • ${profile.gender}` : ''}
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
                      {explanation.confidence_reasoning?.meaning || 
                        `The system has ${prediction.confidence?.toLowerCase() || 'moderate'} confidence in this assessment based on the provided symptoms.`}
                      {' '}Please note that this is a
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
                    {explanation.main_explanation || 'Analysis based on provided symptoms and medical patterns.'}
                  </Typography>
                  
                  {explanation.confidence_reasoning && (
                    <Typography variant="body2" color="#374151" sx={{ lineHeight: 1.7, mb: 4 }}>
                      <Box component="span" fontWeight={600}>Confidence Reasoning: </Box>
                      {explanation.confidence_reasoning.reason || explanation.confidence_reasoning.meaning}
                    </Typography>
                  )}

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
                  <Button 
                    sx={{ textTransform: 'none', fontWeight: 600 }}
                    onClick={() => setShowAllFactors(!showAllFactors)}
                  >
                    {showAllFactors ? 'Show Key Factors' : 'View All Factors'}
                  </Button>
                </Box>

                <Box sx={{ mt: 2 }}>
                  {riskDrivers.slice(0, showAllFactors ? undefined : 3).map((driver, index) => (
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
                  onClick={() => {
                    // TODO: Implement flag for review functionality
                    console.log('Flag for review clicked');
                  }}
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
                  onClick={() => {
                    // Navigate to treatment page with disease from prediction
                    const disease = prediction.disease || 'Diabetes';
                    // Convert disease name to URL-friendly format (e.g., "Type 2 Diabetes" -> "type-2-diabetes")
                    const diseaseId = disease.toLowerCase().replace(/\s+/g, '-');
                    navigate(`/app/diseases/${diseaseId}/treatment`, {
                      state: { 
                        disease,
                        assessmentId: id,
                        assessmentData: data
                      }
                    });
                  }}
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
