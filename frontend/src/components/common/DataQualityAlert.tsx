// ============================================================================
// Data Quality Alert Component
// ============================================================================
// Requirements: 11.1
// - Display alert when data quality score is below 60%
// - Suggest additional information to improve quality

import { Alert, AlertTitle, Box, Typography, List, ListItem, ListItemText } from '@mui/material';
import { Warning as WarningIcon } from '@mui/icons-material';

interface DataQualityAlertProps {
  dataQualityScore: number;
  suggestions?: string[];
}

export const DataQualityAlert: React.FC<DataQualityAlertProps> = ({
  dataQualityScore,
  suggestions = [
    'Add more detailed symptom descriptions',
    'Include symptom duration and severity',
    'Provide relevant medical history',
    'Add vital signs if available (temperature, blood pressure, etc.)',
    'Upload medical reports or test results',
  ],
}) => {
  // Only show alert if data quality is below 60%
  if (dataQualityScore >= 60) {
    return null;
  }

  return (
    <Alert 
      severity="warning" 
      icon={<WarningIcon />}
      sx={{ mb: 2 }}
    >
      <AlertTitle>Low Data Quality Score ({dataQualityScore}%)</AlertTitle>
      <Typography variant="body2" sx={{ mb: 1 }}>
        The assessment has limited information, which may affect the accuracy of results. 
        Consider providing additional details to improve the quality of the analysis:
      </Typography>
      <List dense sx={{ pl: 2 }}>
        {suggestions.map((suggestion, index) => (
          <ListItem key={index} sx={{ py: 0, px: 0 }}>
            <ListItemText 
              primary={`• ${suggestion}`}
              primaryTypographyProps={{ variant: 'body2' }}
            />
          </ListItem>
        ))}
      </List>
    </Alert>
  );
};
