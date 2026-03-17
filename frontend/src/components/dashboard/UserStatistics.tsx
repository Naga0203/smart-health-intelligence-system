import {
  Box,
  Card,
  CardContent,
  Typography,
  Stack,
  Divider,
  Alert,
  useTheme,
  alpha
} from '@mui/material';
import { format } from 'date-fns';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';

/**
 * @typedef {import('@/types').UserStatistics} UserStatistics
 */

interface UserStatisticsProps {
  statistics: any;
  loading: boolean;
}

/**
 * User Statistics Component
 * Displays user assessment statistics and account information
 */
export default function UserStatistics({ statistics, loading }: UserStatisticsProps) {
  const theme = useTheme();

  const glassCardSx = {
    background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.4)} 0%, ${alpha(
      theme.palette.background.paper,
      0.1
    )} 100%)`,
    backdropFilter: 'blur(24px)',
    border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
    borderRadius: 4,
    boxShadow: `0 8px 32px 0 ${alpha(theme.palette.common.black, 0.05)}`,
    height: '100%'
  };

  if (loading) {
    return (
      <Card sx={glassCardSx}>
        <CardContent>
          <Typography variant="h6" gutterBottom fontWeight="600">
            Your Statistics
          </Typography>
          <LoadingSkeleton />
        </CardContent>
      </Card>
    );
  }

  if (!statistics) {
    return (
      <Card sx={glassCardSx}>
        <CardContent>
          <Typography variant="h6" gutterBottom fontWeight="600">
            Your Statistics
          </Typography>
          <Alert severity="info" sx={{ background: alpha(theme.palette.info.main, 0.1) }}>No statistics available yet</Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={glassCardSx}>
      <CardContent>
        <Typography variant="h6" gutterBottom fontWeight="600">
          Your Statistics
        </Typography>

        <Stack spacing={2} sx={{ mt: 2 }}>
          {/* Total Assessments */}
          <Box>
            <Typography variant="h3" color="primary" fontWeight="bold">
              {statistics.total_assessments}
            </Typography>
            <Typography variant="body2" color="text.secondary" fontWeight="500">
              Total Assessments
            </Typography>
          </Box>

          <Divider sx={{ borderColor: alpha(theme.palette.divider, 0.1) }} />

          {/* Assessments by Confidence */}
          {statistics.assessments_by_confidence && (
            <Box>
              <Typography variant="subtitle2" gutterBottom color="text.secondary" fontWeight="600">
                Assessments by Confidence
              </Typography>
              <Stack spacing={1}>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">High Confidence</Typography>
                  <Typography variant="body2" fontWeight="bold" color="success.main" sx={{ bgcolor: alpha(theme.palette.success.main, 0.1), px: 1, borderRadius: 1 }}>
                    {statistics.assessments_by_confidence.HIGH || 0}
                  </Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">Medium Confidence</Typography>
                  <Typography variant="body2" fontWeight="bold" color="warning.main" sx={{ bgcolor: alpha(theme.palette.warning.main, 0.1), px: 1, borderRadius: 1 }}>
                    {statistics.assessments_by_confidence.MEDIUM || 0}
                  </Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2">Low Confidence</Typography>
                  <Typography variant="body2" fontWeight="bold" color="error.main" sx={{ bgcolor: alpha(theme.palette.error.main, 0.1), px: 1, borderRadius: 1 }}>
                    {statistics.assessments_by_confidence.LOW || 0}
                  </Typography>
                </Stack>
              </Stack>
            </Box>
          )}

          {/* Most Common Diseases */}
          {statistics.most_common_diseases && statistics.most_common_diseases.length > 0 && (
            <>
              <Divider sx={{ borderColor: alpha(theme.palette.divider, 0.1) }} />
              <Box>
                <Typography variant="subtitle2" gutterBottom color="text.secondary" fontWeight="600">
                  Most Common Conditions
                </Typography>
                <Stack spacing={1.5}>
                  {statistics.most_common_diseases.slice(0, 3).map((item: any, index: number) => (
                    <Stack key={index} direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2" fontWeight="500">{item.disease}</Typography>
                      <Typography variant="body2" fontWeight="bold" color="primary.main" sx={{ bgcolor: alpha(theme.palette.primary.main, 0.1), px: 1, borderRadius: 1 }}>
                        {item.count}
                      </Typography>
                    </Stack>
                  ))}
                </Stack>
              </Box>
            </>
          )}

          {/* Last Assessment Date */}
          {statistics.last_assessment_date && (
            <>
              <Divider sx={{ borderColor: alpha(theme.palette.divider, 0.1) }} />
              <Box>
                <Typography variant="body2" color="text.secondary" fontWeight="500">
                  Last Assessment
                </Typography>
                <Typography variant="body1" fontWeight="600">
                  {format(new Date(statistics.last_assessment_date), 'MMM dd, yyyy')}
                </Typography>
              </Box>
            </>
          )}

          {/* Account Age */}
          {statistics.account_age_days !== undefined && (
            <Box>
              <Typography variant="body2" color="text.secondary" fontWeight="500">
                Member for
              </Typography>
              <Typography variant="body1" fontWeight="600">
                {statistics.account_age_days} days
              </Typography>
            </Box>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
