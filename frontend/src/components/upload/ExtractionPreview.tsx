import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Divider,
  Chip,
  Alert,
  List,
  ListItem,
  ListItemText,
  Button,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';

export interface ExtractedData {
  fileName: string;
  confidence: number; // 0-100
  method: string;
  extractedFeatures: string[];
  symptoms?: string[];
  vitals?: {
    temperature?: number;
    bloodPressureSystolic?: number;
    bloodPressureDiastolic?: number;
    heartRate?: number;
    respiratoryRate?: number;
  };
  demographics?: {
    age?: number;
    gender?: string;
  };
  medicalHistory?: string[];
  notes?: string;
}

interface ExtractionPreviewProps {
  extractedData: ExtractedData[];
  onConfirm: () => void;
  onCancel: () => void;
  loading?: boolean;
}

const ConfidenceIndicator: React.FC<{ confidence: number }> = ({ confidence }) => {
  const getColor = () => {
    if (confidence >= 75) return 'success';
    if (confidence >= 50) return 'warning';
    return 'error';
  };

  const getLabel = () => {
    if (confidence >= 75) return 'High Confidence';
    if (confidence >= 50) return 'Medium Confidence';
    return 'Low Confidence';
  };

  return (
    <Chip
      icon={confidence >= 50 ? <CheckCircleIcon /> : <WarningIcon />}
      label={`${getLabel()} (${confidence}%)`}
      color={getColor()}
      size="small"
    />
  );
};

const ExtractedDataCard: React.FC<{ data: ExtractedData }> = ({ data }) => {
  return (
    <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="subtitle1" fontWeight={600}>
          {data.fileName}
        </Typography>
        <ConfidenceIndicator confidence={data.confidence} />
      </Box>

      <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
        Extraction Method: {data.method}
      </Typography>

      {data.confidence < 50 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Low confidence extraction. Please review the data carefully before proceeding.
        </Alert>
      )}

      {data.symptoms && data.symptoms.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" fontWeight={500} gutterBottom>
            Symptoms Detected:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {data.symptoms.map((symptom, index) => (
              <Chip key={index} label={symptom} size="small" variant="outlined" />
            ))}
          </Box>
        </Box>
      )}

      {data.vitals && Object.keys(data.vitals).length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" fontWeight={500} gutterBottom>
            Vitals:
          </Typography>
          <List dense disablePadding>
            {data.vitals.temperature && (
              <ListItem disablePadding>
                <ListItemText
                  primary={`Temperature: ${data.vitals.temperature}°F`}
                  primaryTypographyProps={{ variant: 'body2' }}
                />
              </ListItem>
            )}
            {data.vitals.bloodPressureSystolic && data.vitals.bloodPressureDiastolic && (
              <ListItem disablePadding>
                <ListItemText
                  primary={`Blood Pressure: ${data.vitals.bloodPressureSystolic}/${data.vitals.bloodPressureDiastolic} mmHg`}
                  primaryTypographyProps={{ variant: 'body2' }}
                />
              </ListItem>
            )}
            {data.vitals.heartRate && (
              <ListItem disablePadding>
                <ListItemText
                  primary={`Heart Rate: ${data.vitals.heartRate} bpm`}
                  primaryTypographyProps={{ variant: 'body2' }}
                />
              </ListItem>
            )}
            {data.vitals.respiratoryRate && (
              <ListItem disablePadding>
                <ListItemText
                  primary={`Respiratory Rate: ${data.vitals.respiratoryRate} breaths/min`}
                  primaryTypographyProps={{ variant: 'body2' }}
                />
              </ListItem>
            )}
          </List>
        </Box>
      )}

      {data.demographics && Object.keys(data.demographics).length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" fontWeight={500} gutterBottom>
            Demographics:
          </Typography>
          <List dense disablePadding>
            {data.demographics.age && (
              <ListItem disablePadding>
                <ListItemText
                  primary={`Age: ${data.demographics.age}`}
                  primaryTypographyProps={{ variant: 'body2' }}
                />
              </ListItem>
            )}
            {data.demographics.gender && (
              <ListItem disablePadding>
                <ListItemText
                  primary={`Gender: ${data.demographics.gender}`}
                  primaryTypographyProps={{ variant: 'body2' }}
                />
              </ListItem>
            )}
          </List>
        </Box>
      )}

      {data.medicalHistory && data.medicalHistory.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" fontWeight={500} gutterBottom>
            Medical History:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {data.medicalHistory.map((item, index) => (
              <Chip key={index} label={item} size="small" variant="outlined" color="secondary" />
            ))}
          </Box>
        </Box>
      )}

      {data.notes && (
        <Box>
          <Typography variant="body2" fontWeight={500} gutterBottom>
            Additional Notes:
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {data.notes}
          </Typography>
        </Box>
      )}

      {data.extractedFeatures && data.extractedFeatures.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
            Extracted Features: {data.extractedFeatures.join(', ')}
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export const ExtractionPreview: React.FC<ExtractionPreviewProps> = ({
  extractedData,
  onConfirm,
  onCancel,
  loading = false,
}) => {
  if (extractedData.length === 0) {
    return null;
  }

  const hasLowConfidence = extractedData.some((data) => data.confidence < 50);

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h6" gutterBottom>
        Extracted Data Preview
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Please review the extracted information before submitting for analysis.
      </Typography>

      {hasLowConfidence && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Some files have low confidence extractions. Please verify the data carefully.
        </Alert>
      )}

      <Divider sx={{ mb: 2 }} />

      {extractedData.map((data, index) => (
        <ExtractedDataCard key={index} data={data} />
      ))}

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 3 }}>
        <Button
          variant="outlined"
          onClick={onCancel}
          disabled={loading}
        >
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={onConfirm}
          disabled={loading}
        >
          {loading ? 'Submitting...' : 'Confirm and Submit for Analysis'}
        </Button>
      </Box>
    </Box>
  );
};
