// ============================================================================
// Assessment Card Component
// ============================================================================

import React from 'react';
import {
  Card,
  CardContent,
  CardActionArea,
  Typography,
  Chip,
  Box,
  useTheme,
  alpha,
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
  const theme = useTheme();
  const formattedDate = format(new Date(date), 'MMM dd, yyyy HH:mm');

  return (
    <Card
      sx={{
        mb: 2,
        borderRadius: 4,
        background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.4)} 0%, ${alpha(theme.palette.background.paper, 0.1)} 100%)`,
        backdropFilter: 'blur(10px)',
        border: '1px solid',
        borderColor: alpha(theme.palette.divider, 0.2),
        transition: 'all 0.3s ease-in-out',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: `0 8px 24px ${alpha(theme.palette.primary.main, 0.15)}`,
          borderColor: alpha(theme.palette.primary.main, 0.3),
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

          <Box display="flex" gap={1} mt={2} flexWrap="wrap">
            <Chip
              label={`Confidence: ${confidence}`}
              size="small"
              sx={{
                background: alpha(confidenceColors[confidence], 0.15),
                color: confidenceColors[confidence],
                fontWeight: 600,
                border: '1px solid',
                borderColor: alpha(confidenceColors[confidence], 0.3),
              }}
            />
            <Chip
              label={`Probability: ${probability.toFixed(1)}%`}
              size="small"
              variant="outlined"
              sx={{
                fontWeight: 600,
                borderColor: alpha(theme.palette.text.primary, 0.2),
                color: theme.palette.text.primary,
              }}
            />
          </Box>
        </CardContent>
      </CardActionArea>
    </Card>
  );
};
