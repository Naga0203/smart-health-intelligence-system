import { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  Stack,
  Chip,
  LinearProgress,
  TextField,
  Button,
  Alert,
} from '@mui/material';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { EmptyState } from '@/components/common/EmptyState';

/**
 * @typedef {import('@/types').Prediction} Prediction
 */

/**
 * Get color for confidence level based on probability
 * @param {number} probability - Probability value (0-1)
 * @returns {'success'|'warning'|'error'}
 */
const getConfidenceColor = (probability: number): 'success' | 'warning' | 'error' => {
  if (probability >= 0.75) return 'success';
  if (probability >= 0.55) return 'warning';
  return 'error';
};

/**
 * Get confidence level label based on probability
 * @param {number} probability - Probability value (0-1)
 * @returns {'HIGH'|'MEDIUM'|'LOW'}
 */
const getConfidenceLevel = (probability: number): 'HIGH' | 'MEDIUM' | 'LOW' => {
  if (probability >= 0.75) return 'HIGH';
  if (probability >= 0.55) return 'MEDIUM';
  return 'LOW';
};

interface TopPredictionsProps {
  predictions: any[] | null;
  loading: boolean;
  error?: string | null;
  onFetchPredictions: (n: number) => void;
  defaultN?: number;
}

/**
 * Top Predictions Component
 * Displays top N disease predictions with probability percentages and confidence levels
 */
export default function TopPredictions({ 
  predictions, 
  loading, 
  error,
  onFetchPredictions,
  defaultN = 5 
}: TopPredictionsProps) {
  const [inputValue, setInputValue] = useState(String(defaultN));

  const handleFetch = () => {
    const n = parseInt(inputValue, 10);
    if (n > 0 && n <= 50) {
      onFetchPredictions(n);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Top Predictions
          </Typography>
          <LoadingSkeleton />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            Top Predictions
          </Typography>
          <Stack direction="row" spacing={1} alignItems="center">
            <TextField
              size="small"
              type="number"
              value={inputValue}
              onChange={handleInputChange}
              inputProps={{ min: 1, max: 50 }}
              sx={{ width: 80 }}
              label="N"
            />
            <Button 
              variant="outlined" 
              size="small" 
              onClick={handleFetch}
              disabled={loading}
            >
              Fetch
            </Button>
          </Stack>
        </Stack>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {!predictions || predictions.length === 0 ? (
          <EmptyState
            title="No predictions available"
            description="Enter symptoms and demographic information to see top disease predictions"
          />
        ) : (
          <List>
            {predictions.map((prediction: any, index: number) => {
              const probabilityPercent = Math.round(prediction.probability * 100);
              const confidenceLevel = getConfidenceLevel(prediction.probability);
              const confidenceColor = getConfidenceColor(prediction.probability);

              return (
                <ListItem 
                  key={`${prediction.disease}-${index}`}
                  sx={{ 
                    flexDirection: 'column', 
                    alignItems: 'stretch',
                    py: 2,
                    borderBottom: index < predictions.length - 1 ? '1px solid' : 'none',
                    borderColor: 'divider'
                  }}
                >
                  <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Typography variant="body1" fontWeight="medium">
                        {prediction.rank}. {prediction.disease}
                      </Typography>
                      <Chip
                        label={confidenceLevel}
                        size="small"
                        color={confidenceColor}
                      />
                    </Stack>
                    <Typography variant="h6" color="primary">
                      {probabilityPercent}%
                    </Typography>
                  </Stack>
                  <Box sx={{ width: '100%' }}>
                    <LinearProgress 
                      variant="determinate" 
                      value={probabilityPercent} 
                      sx={{ 
                        height: 8, 
                        borderRadius: 1,
                        backgroundColor: 'action.hover',
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 1,
                        }
                      }}
                    />
                  </Box>
                </ListItem>
              );
            })}
          </List>
        )}

        {predictions && predictions.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="caption" color="text.secondary">
              Showing top {predictions.length} predictions. Confidence levels: HIGH ≥75%, MEDIUM 55-75%, LOW &lt;55%
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
