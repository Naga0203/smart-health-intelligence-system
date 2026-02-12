import React from 'react';
import { Box, Typography, Paper, Alert, List, ListItem, ListItemText, Divider } from '@mui/material';
import { TreatmentDetail } from '@/types';

interface AllopathyPanelProps {
  treatments: TreatmentDetail[];
}

export const AllopathyPanel: React.FC<AllopathyPanelProps> = ({ treatments }) => {
  return (
    <Box>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2" fontWeight="bold">
          Educational Information Only
        </Typography>
        <Typography variant="body2">
          This information is educational only and should not replace professional medical advice. 
          Always consult with a qualified healthcare provider before starting any treatment.
        </Typography>
      </Alert>

      {treatments && treatments.length > 0 ? (
        treatments.map((treatment, index) => (
          <Paper key={index} elevation={1} sx={{ p: 3, mb: 2 }}>
            <Typography variant="h6" gutterBottom color="primary">
              {treatment.category}
            </Typography>
            
            {treatment.approach && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                <strong>Approach:</strong> {treatment.approach}
              </Typography>
            )}
            
            {treatment.focus && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                <strong>Focus:</strong> {treatment.focus}
              </Typography>
            )}

            {treatment.recommendations && treatment.recommendations.length > 0 && (
              <>
                <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                  Recommendations:
                </Typography>
                <List dense>
                  {treatment.recommendations.map((rec, recIndex) => (
                    <ListItem key={recIndex} sx={{ pl: 0 }}>
                      <ListItemText 
                        primary={rec}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </>
            )}

            {treatment.notes && (
              <>
                <Divider sx={{ my: 2 }} />
                <Typography variant="body2" color="text.secondary">
                  <strong>Note:</strong> {treatment.notes}
                </Typography>
              </>
            )}
          </Paper>
        ))
      ) : (
        <Paper elevation={1} sx={{ p: 3 }}>
          <Typography variant="body2" color="text.secondary">
            No modern medicine treatment information available for this assessment.
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default AllopathyPanel;
