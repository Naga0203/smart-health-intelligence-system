import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Box, Typography, CircularProgress, Button, Alert } from '@mui/material';
import { ArrowBack as ArrowBackIcon } from '@mui/icons-material';
import { useAssessmentStore } from '@/stores/assessmentStore';
import { RiskOverview } from '@/components/results/RiskOverview';
import { ConfidenceMeter } from '@/components/results/ConfidenceMeter';
import { RiskDrivers } from '@/components/results/RiskDrivers';
import { DataQualityScore } from '@/components/results/DataQualityScore';
import { AIInterpretation } from '@/components/results/AIInterpretation';
import { DisclaimerBanner } from '@/components/results/DisclaimerBanner';
import { TreatmentTabs } from '@/components/treatment/TreatmentTabs';

export const AssessmentResultsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const assessmentStore = useAssessmentStore() as any;
  const currentAssessment = assessmentStore.currentAssessment;
  const loading = assessmentStore.loading;
  const error = assessmentStore.error;
  const fetchAssessmentDetail = assessmentStore.fetchAssessmentDetail;

  useEffect(() => {
    // If we have an ID in the URL, fetch the assessment detail from history
    if (id) {
      fetchAssessmentDetail(id);
    }
    // If no ID, we're viewing the current assessment (just submitted)
    // currentAssessment should already be populated by submitAssessment
  }, [id, fetchAssessmentDetail]);

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/app/dashboard')}
        >
          Back to Dashboard
        </Button>
      </Container>
    );
  }

  if (!currentAssessment) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert severity="info" sx={{ mb: 2 }}>
          No assessment data available.
        </Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/app/dashboard')}
        >
          Back to Dashboard
        </Button>
      </Container>
    );
  }

  const {
    prediction,
    explanation,
    metadata,
    risk_factors,
    treatment_info
  } = currentAssessment;

  // Extract data from the assessment structure
  const condition = prediction?.disease || 'Unknown Condition';
  const probability = prediction?.probability_percent || 0;
  const confidence = prediction?.confidence || 'LOW';
  const confidenceScore = prediction?.probability || 0;
  
  // Determine risk level based on probability
  const getRiskLevel = (prob: number): 'low' | 'medium' | 'elevated' | 'high' => {
    if (prob < 25) return 'low';
    if (prob < 50) return 'medium';
    if (prob < 75) return 'elevated';
    return 'high';
  };
  
  const riskLevel = getRiskLevel(probability);
  
  // Extract interpretation
  const interpretation = explanation?.text || '';
  
  // Create risk drivers from risk_factors if available
  const riskDrivers = risk_factors?.map((factor: string, index: number) => ({
    factor: factor,
    contribution: Math.max(10, 100 - (index * 15)), // Mock contribution percentages
    description: `This factor contributes to the overall risk assessment.`
  })) || [];
  
  // Data quality score (mock for now - should come from backend)
  const dataQualityScore = 75;

  // Conditional rendering based on confidence level
  const showLimitedInfo = confidence === 'LOW';
  const showCautiousGuidance = confidence === 'MEDIUM';
  const showFullDetails = confidence === 'HIGH';

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ mb: 3 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/app/dashboard')}
          sx={{ mb: 2 }}
        >
          Back to Dashboard
        </Button>
        
        <Typography variant="h4" gutterBottom>
          Assessment Results
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Generated on {new Date(metadata?.timestamp || Date.now()).toLocaleString()}
        </Typography>
      </Box>

      {/* Always show disclaimer first */}
      <DisclaimerBanner />

      {/* Risk Overview - always shown */}
      <RiskOverview
        condition={condition}
        riskLevel={riskLevel}
        probability={probability}
        confidence={confidence}
        confidenceScore={confidenceScore}
      />

      {/* Confidence Meter - always shown */}
      <ConfidenceMeter
        confidence={confidence}
        confidenceScore={confidenceScore}
      />

      {/* Data Quality Score - always shown */}
      <DataQualityScore dataQualityScore={dataQualityScore} />

      {/* Conditional rendering based on confidence level */}
      {showLimitedInfo && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="body2" fontWeight="bold" gutterBottom>
            Limited Reliability
          </Typography>
          <Typography variant="body2">
            Due to low confidence in this assessment, we recommend providing additional information 
            or consulting with a healthcare professional for a more accurate evaluation.
          </Typography>
        </Alert>
      )}

      {(showCautiousGuidance || showFullDetails) && (
        <>
          {/* AI Interpretation */}
          {interpretation && (
            <AIInterpretation interpretation={interpretation} />
          )}

          {/* Risk Drivers - only show for MEDIUM and HIGH confidence */}
          {riskDrivers.length > 0 && (
            <RiskDrivers riskDrivers={riskDrivers} />
          )}
        </>
      )}

      {showFullDetails && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            This assessment is based on comprehensive data analysis with high confidence. 
            However, it should still be reviewed by a qualified healthcare professional.
          </Typography>
        </Alert>
      )}

      {/* Treatment Information - only show for MEDIUM and HIGH confidence */}
      {treatment_info && (showCautiousGuidance || showFullDetails) && (
        <TreatmentTabs treatmentInfo={treatment_info} confidence={confidence} />
      )}

      {/* Action buttons */}
      <Box sx={{ mt: 4, display: 'flex', gap: 2 }}>
        <Button
          variant="contained"
          onClick={() => navigate('/app/assessment/new')}
        >
          New Assessment
        </Button>
        <Button
          variant="outlined"
          onClick={() => navigate('/app/history')}
        >
          View History
        </Button>
      </Box>
    </Container>
  );
};

export default AssessmentResultsPage;
