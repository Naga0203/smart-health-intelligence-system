import React from 'react';
import { Box, Card, CardContent, Typography, Chip } from '@mui/material';

interface RiskOverviewProps {
  condition: string;
  riskLevel: 'low' | 'medium' | 'elevated' | 'high';
  probability: number;
  confidence: 'LOW' | 'MEDIUM' | 'HIGH';
  confidenceScore?: number; // Optional since we're not using it in this component
}

const riskLevelColors = {
  low: '#2196F3',      // blue
  medium: '#FFC107',   // yellow
  elevated: '#FF9800', // orange
  high: '#F44336'      // red
};

const riskLevelLabels = {
  low: 'Low Risk',
  medium: 'Medium Risk',
  elevated: 'Elevated Risk',
  high: 'High Risk'
};

export const RiskOverview: React.FC<RiskOverviewProps> = ({
  condition,
  riskLevel,
  probability,
  confidence
}) => {
  const riskColor = riskLevelColors[riskLevel];
  const riskLabel = riskLevelLabels[riskLevel];

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Risk Assessment Overview
        </Typography>
        
        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Condition
          </Typography>
          <Typography variant="h6" gutterBottom>
            {condition}
          </Typography>
        </Box>

        <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Risk Level
            </Typography>
            <Chip
              label={riskLabel}
              sx={{
                backgroundColor: riskColor,
                color: '#fff',
                fontWeight: 'bold',
                fontSize: '0.875rem'
              }}
            />
          </Box>

          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Probability
            </Typography>
            <Typography variant="h6">
              {probability.toFixed(1)}%
            </Typography>
          </Box>

          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Confidence
            </Typography>
            <Chip
              label={confidence}
              color={confidence === 'HIGH' ? 'success' : confidence === 'MEDIUM' ? 'warning' : 'default'}
              sx={{ fontWeight: 'bold' }}
            />
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};
