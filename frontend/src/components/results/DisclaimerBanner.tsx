import React from 'react';
import { Alert, Typography, Box } from '@mui/material';
import { Warning as WarningIcon } from '@mui/icons-material';

export const DisclaimerBanner: React.FC = () => {
  return (
    <Alert 
      severity="warning" 
      icon={<WarningIcon />}
      sx={{ 
        mb: 3,
        backgroundColor: '#FFF3E0',
        border: '2px solid #FF9800',
        '& .MuiAlert-icon': {
          color: '#F57C00'
        }
      }}
    >
      <Typography variant="body1" fontWeight="bold" gutterBottom>
        Important Medical Disclaimer
      </Typography>
      <Typography variant="body2">
        This is not a medical diagnosis. The information provided is for educational purposes only 
        and should not replace professional medical advice, diagnosis, or treatment. Always seek 
        the advice of your physician or other qualified health provider with any questions you may 
        have regarding a medical condition.
      </Typography>
      <Box sx={{ mt: 1 }}>
        <Typography variant="body2" fontWeight="medium">
          If you are experiencing a medical emergency, call your local emergency services immediately.
        </Typography>
      </Box>
    </Alert>
  );
};
