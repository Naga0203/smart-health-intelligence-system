import React from 'react';
import { Box, Card, CardContent, Typography, LinearProgress, Alert } from '@mui/material';
import { Info as InfoIcon } from '@mui/icons-material';

interface DataQualityScoreProps {
  dataQualityScore: number;
}

export const DataQualityScore: React.FC<DataQualityScoreProps> = ({ dataQualityScore }) => {
  const isLowQuality = dataQualityScore < 60;
  
  const getQualityLabel = (score: number): string => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Limited';
  };

  const getQualityColor = (score: number): string => {
    if (score >= 80) return '#4CAF50'; // green
    if (score >= 60) return '#2196F3'; // blue
    if (score >= 40) return '#FF9800'; // orange
    return '#F44336'; // red
  };

  const qualityLabel = getQualityLabel(dataQualityScore);
  const qualityColor = getQualityColor(dataQualityScore);

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Data Quality Score
        </Typography>
        
        <Box sx={{ mt: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              {qualityLabel}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {dataQualityScore.toFixed(0)}%
            </Typography>
          </Box>
          
          <LinearProgress
            variant="determinate"
            value={dataQualityScore}
            sx={{
              height: 10,
              borderRadius: 5,
              backgroundColor: '#E0E0E0',
              '& .MuiLinearProgress-bar': {
                backgroundColor: qualityColor,
                borderRadius: 5
              }
            }}
          />
        </Box>

        {isLowQuality && (
          <Alert severity="warning" icon={<InfoIcon />} sx={{ mt: 2 }}>
            <Typography variant="body2">
              Limited data quality detected. Consider providing additional information such as:
            </Typography>
            <ul style={{ margin: '8px 0 0 0', paddingLeft: '20px' }}>
              <li>More detailed symptom descriptions</li>
              <li>Duration and severity of symptoms</li>
              <li>Relevant medical history</li>
              <li>Vital signs measurements</li>
            </ul>
          </Alert>
        )}

        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          This score reflects the completeness and reliability of the input data used for the assessment.
        </Typography>
      </CardContent>
    </Card>
  );
};
