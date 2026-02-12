// ============================================================================
// Assessment Card Component
// ============================================================================

import React from 'react';
import {
  Card,
  CardContent,
  CardActionArea,
  Typography,
  Box,
  Chip,
} from '@mui/material';
import { format } from 'date-fns';

interface AssessmentCardProps {
  id: string;
  date: string;
  condition: string;
  riskLevel: 'low' | 'medium' | 'elevated' | 'high';
  confidence: 'LOW' | 'MEDIUM' | 'HIGH';
  probability: number;
  onClick: (id: string) => void;
}

const riskLevelColors = {
  low: '#2196F3',      // Blue
  medium: '#FFC107',   // Yellow
  elevated: '#FF9800', // Orange
  high: '#F44336',     // Red
};

const confidenceColors = {
  LOW: '#9E9E9E',      // Gray
  MEDIUM: '#FF9800',   // Orange
  HIGH: '#4CAF50',     // Green
};

export const AssessmentCard: React.FC<AssessmentCardProps> = ({
  id,
  date,
  condition,
  riskLevel,
  confidence,
  probability,
  onClick,
}) => {
  const formattedDate = format(new Date(date), 'MMM dd, yyyy HH:mm');

  return (
    <Card
      sx={{
        mb: 2,
        '&:hover': {
          boxShadow: 3,
        },
      }}
    >
      <CardActionArea onClick={() => onClick(id)}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
            <Typography variant="h6" component="div">
              {condition}
            </Typography>
            <Chip
              label={riskLevel.toUpperCase()}
              size="small"
              sx={{
                backgroundColor: riskLevelColors[riskLevel],
                color: '#fff',
                fontWeight: 'bold',
              }}
            />
          </Box>

          <Typography variant="body2" color="text.secondary" gutterBottom>
            {formattedDate}
          </Typography>

          <Box display="flex" gap={1} mt={2}>
            <Chip
              label={`Confidence: ${confidence}`}
              size="small"
              sx={{
                backgroundColor: confidenceColors[confidence],
                color: '#fff',
              }}
            />
            <Chip
              label={`Probability: ${probability.toFixed(1)}%`}
              size="small"
              variant="outlined"
            />
          </Box>
        </CardContent>
      </CardActionArea>
    </Card>
  );
};
