import React from 'react';
import { Box, Card, CardContent, Typography, LinearProgress, List, ListItem } from '@mui/material';

interface RiskDriver {
  factor: string;
  contribution: number;
  description: string;
}

interface RiskDriversProps {
  riskDrivers: RiskDriver[];
}

export const RiskDrivers: React.FC<RiskDriversProps> = ({ riskDrivers }) => {
  if (!riskDrivers || riskDrivers.length === 0) {
    return null;
  }

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Key Risk Factors
        </Typography>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          These factors contribute most significantly to the risk assessment:
        </Typography>

        <List sx={{ p: 0 }}>
          {riskDrivers.map((driver, index) => (
            <ListItem
              key={index}
              sx={{
                display: 'block',
                px: 0,
                py: 2,
                borderBottom: index < riskDrivers.length - 1 ? '1px solid #E0E0E0' : 'none'
              }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body1" fontWeight="medium">
                  {driver.factor}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {driver.contribution.toFixed(0)}%
                </Typography>
              </Box>
              
              <LinearProgress
                variant="determinate"
                value={driver.contribution}
                sx={{
                  height: 6,
                  borderRadius: 3,
                  backgroundColor: '#E0E0E0',
                  mb: 1,
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: '#2196F3',
                    borderRadius: 3
                  }
                }}
              />
              
              <Typography variant="body2" color="text.secondary">
                {driver.description}
              </Typography>
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};
