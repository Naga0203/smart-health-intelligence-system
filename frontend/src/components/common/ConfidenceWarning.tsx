// ============================================================================
// Confidence Warning Component
// ============================================================================
// Requirements: 11.2
// - Display prominent warning when confidence level is LOW
// - Display warning about limited reliability

import { Alert, AlertTitle, Typography, Box } from '@mui/material';
import { Warning as WarningIcon } from '@mui/icons-material';

interface ConfidenceWarningProps {
  confidence: 'LOW' | 'MEDIUM' | 'HIGH';
  confidenceScore?: number;
}

export const ConfidenceWarning: React.FC<ConfidenceWarningProps> = ({
  confidence,
  confidenceScore,
}) => {
  // Only show warning for LOW confidence
  if (confidence !== 'LOW') {
    return null;
  }

  return (
    <Alert 
      severity="warning" 
      icon={<WarningIcon />}
      sx={{ 
        mb: 2,
        border: 2,
        borderColor: 'warning.main',
      }}
    >
      <AlertTitle>
        <Box component="span" fontWeight="bold">
          Low Confidence Assessment
          {confidenceScore !== undefined && ` (${confidenceScore}%)`}
        </Box>
      </AlertTitle>
      <Typography variant="body2" sx={{ mb: 1 }}>
        This assessment has limited reliability due to insufficient or ambiguous information. 
        The results should be interpreted with caution.
      </Typography>
      <Typography variant="body2" fontWeight="medium">
        We strongly recommend:
      </Typography>
      <Typography variant="body2" component="div" sx={{ pl: 2 }}>
        • Consulting with a qualified healthcare professional
        <br />
        • Providing more detailed symptom information
        <br />
        • Uploading relevant medical reports or test results
        <br />
        • Not making health decisions based solely on this assessment
      </Typography>
    </Alert>
  );
};
