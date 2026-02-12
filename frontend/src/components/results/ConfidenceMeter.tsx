import React from 'react';
import { Box, Card, CardContent, Typography, LinearProgress } from '@mui/material';

interface ConfidenceMeterProps {
  confidence: 'LOW' | 'MEDIUM' | 'HIGH';
  confidenceScore: number;
}

const confidenceColors = {
  LOW: '#9E9E9E',    // gray
  MEDIUM: '#FF9800', // orange
  HIGH: '#4CAF50'    // green
};

const confidenceDescriptions = {
  LOW: 'Limited data available. Results should be interpreted with caution.',
  MEDIUM: 'Moderate confidence. Consider additional medical consultation.',
  HIGH: 'High confidence based on comprehensive data analysis.'
};

export const ConfidenceMeter: React.FC<ConfidenceMeterProps> = ({
  confidence,
  confidenceScore
}) => {
  const color = confidenceColors[confidence];
  const description = confidenceDescriptions[confidence];

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Confidence Level
        </Typography>
        
        <Box sx={{ mt: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              {confidence}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {confidenceScore.toFixed(0)}%
            </Typography>
          </Box>
          
          <LinearProgress
            variant="determinate"
            value={confidenceScore}
            sx={{
              height: 10,
              borderRadius: 5,
              backgroundColor: '#E0E0E0',
              '& .MuiLinearProgress-bar': {
                backgroundColor: color,
                borderRadius: 5
              }
            }}
          />
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          {description}
        </Typography>
      </CardContent>
    </Card>
  );
};
