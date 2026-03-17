// ============================================================================
// Risk Trend Chart Component
// ============================================================================

import React from 'react';
import {
  Paper,
  Typography,
  useTheme,
  alpha,
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
          sx={{
            p: 2,
            borderRadius: 3,
            background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.8)} 0%, ${alpha(theme.palette.background.paper, 0.6)} 100%)`,
            backdropFilter: 'blur(12px)',
            border: '1px solid',
            borderColor: alpha(theme.palette.divider, 0.2),
            boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.1)}`,
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
      <Paper 
        sx={{ 
          p: 3, 
          textAlign: 'center',
          borderRadius: 4,
          background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.4)} 0%, ${alpha(theme.palette.background.paper, 0.1)} 100%)`,
          backdropFilter: 'blur(10px)',
          border: '1px solid',
          borderColor: alpha(theme.palette.divider, 0.2),
        }}
      >
        <Typography variant="body1" color="text.secondary">
          No data available for trend visualization
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper 
      sx={{ 
        p: { xs: 2, sm: 4 }, 
        mb: 4,
        borderRadius: 4,
        background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.4)} 0%, ${alpha(theme.palette.background.paper, 0.1)} 100%)`,
        backdropFilter: 'blur(10px)',
        border: '1px solid',
        borderColor: alpha(theme.palette.divider, 0.2),
        boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.05)}`,
      }}
    >
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 700 }}>
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
          
          {/* Custom legend payload using type casting to bypass strict Recharts types */}
          <Legend
            wrapperStyle={{ fontSize: '12px' }}
            {...({
              payload: [
                { value: 'High Confidence', type: 'circle', color: confidenceColors.HIGH },
                { value: 'Medium Confidence', type: 'circle', color: confidenceColors.MEDIUM },
                { value: 'Low Confidence', type: 'circle', color: confidenceColors.LOW },
              ]
            } as any)}
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
