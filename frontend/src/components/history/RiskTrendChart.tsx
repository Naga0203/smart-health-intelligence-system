// ============================================================================
// Risk Trend Chart Component
// ============================================================================

import React from 'react';
import {
  Box,
  Paper,
  Typography,
  useTheme,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { format } from 'date-fns';

interface Assessment {
  id: string;
  created_at: string;
  disease: string;
  probability: number;
  confidence: 'LOW' | 'MEDIUM' | 'HIGH';
}

interface RiskTrendChartProps {
  assessments: Assessment[];
}

interface ChartDataPoint {
  date: string;
  displayDate: string;
  probability: number;
  confidence: string;
  disease: string;
}

const confidenceColors = {
  LOW: '#9E9E9E',
  MEDIUM: '#FF9800',
  HIGH: '#4CAF50',
};

export const RiskTrendChart: React.FC<RiskTrendChartProps> = ({ assessments }) => {
  const theme = useTheme();

  // Prepare chart data - sort by date and format
  const chartData: ChartDataPoint[] = [...assessments]
    .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
    .map((assessment) => ({
      date: assessment.created_at,
      displayDate: format(new Date(assessment.created_at), 'MMM dd'),
      probability: assessment.probability,
      confidence: assessment.confidence,
      disease: assessment.disease,
    }));

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <Paper
          elevation={3}
          sx={{
            p: 1.5,
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
          }}
        >
          <Typography variant="body2" fontWeight="bold">
            {data.disease}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {format(new Date(data.date), 'MMM dd, yyyy')}
          </Typography>
          <Typography variant="body2" sx={{ mt: 0.5 }}>
            Probability: {data.probability.toFixed(1)}%
          </Typography>
          <Typography
            variant="body2"
            sx={{
              color: confidenceColors[data.confidence as keyof typeof confidenceColors],
              fontWeight: 'bold',
            }}
          >
            Confidence: {data.confidence}
          </Typography>
        </Paper>
      );
    }
    return null;
  };

  // Custom dot to show confidence level
  const CustomDot = (props: any) => {
    const { cx, cy, payload } = props;
    const color = confidenceColors[payload.confidence as keyof typeof confidenceColors];
    
    return (
      <circle
        cx={cx}
        cy={cy}
        r={5}
        fill={color}
        stroke="#fff"
        strokeWidth={2}
      />
    );
  };

  if (chartData.length === 0) {
    return (
      <Paper elevation={1} sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No data available for trend visualization
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Risk Trend Over Time
      </Typography>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Track changes in your health risk assessments. Dot colors indicate confidence levels.
      </Typography>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          
          <XAxis
            dataKey="displayDate"
            stroke={theme.palette.text.secondary}
            style={{ fontSize: '12px' }}
          />
          
          <YAxis
            label={{
              value: 'Probability (%)',
              angle: -90,
              position: 'insideLeft',
              style: { fontSize: '12px', fill: theme.palette.text.secondary },
            }}
            domain={[0, 100]}
            stroke={theme.palette.text.secondary}
            style={{ fontSize: '12px' }}
          />
          
          <Tooltip content={<CustomTooltip />} />
          
          <Legend
            wrapperStyle={{ fontSize: '12px' }}
            payload={[
              { value: 'High Confidence', type: 'circle', color: confidenceColors.HIGH },
              { value: 'Medium Confidence', type: 'circle', color: confidenceColors.MEDIUM },
              { value: 'Low Confidence', type: 'circle', color: confidenceColors.LOW },
            ]}
          />
          
          {/* Reference lines for risk thresholds */}
          <ReferenceLine
            y={25}
            stroke="#2196F3"
            strokeDasharray="3 3"
            label={{ value: 'Low Risk', position: 'right', fontSize: 10 }}
          />
          <ReferenceLine
            y={50}
            stroke="#FFC107"
            strokeDasharray="3 3"
            label={{ value: 'Medium Risk', position: 'right', fontSize: 10 }}
          />
          <ReferenceLine
            y={75}
            stroke="#FF9800"
            strokeDasharray="3 3"
            label={{ value: 'Elevated Risk', position: 'right', fontSize: 10 }}
          />
          
          <Line
            type="monotone"
            dataKey="probability"
            stroke={theme.palette.primary.main}
            strokeWidth={2}
            dot={<CustomDot />}
            activeDot={{ r: 7 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Paper>
  );
};
