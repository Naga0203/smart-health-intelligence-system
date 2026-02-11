import {
  Box,
  Card,
  CardContent,
  Typography,
  Stack,
  Divider,
  Alert,
} from '@mui/material';
import { format } from 'date-fns';
import { LoadingSkeleton } from '@/components/common/LoadingSkeleton';

/**
 * @typedef {import('@/types').UserStatistics} UserStatistics
 */

/**
 * User Statistics Component
 * Displays user assessment statistics and account information
 * @param {Object} props
 * @param {UserStatistics|null} props.statistics - User statistics object
 * @param {boolean} props.loading - Loading state
 */
export default function UserStatistics({ statistics, loading }) {
  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Your Statistics
          </Typography>
          <LoadingSkeleton />
        </CardContent>
      </Card>
    );
  }

  if (!statistics) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Your Statistics
          </Typography>
          <Alert severity="info">No statistics available yet</Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Your Statistics
        </Typography>

        <Stack spacing={2}>
          {/* Total Assessments */}
          <Box>
            <Typography variant="h3" color="primary">
              {statistics.total_assessments}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Assessments
            </Typography>
          </Box>

          <Divider />

          {/* Assessments by Confidence */}
          {statistics.assessments_by_confidence && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Assessments by Confidence
              </Typography>
              <Stack spacing={1}>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2">High Confidence</Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {statistics.assessments_by_confidence.HIGH || 0}
                  </Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2">Medium Confidence</Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {statistics.assessments_by_confidence.MEDIUM || 0}
                  </Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2">Low Confidence</Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {statistics.assessments_by_confidence.LOW || 0}
                  </Typography>
                </Stack>
              </Stack>
            </Box>
          )}

          {/* Most Common Diseases */}
          {statistics.most_common_diseases && statistics.most_common_diseases.length > 0 && (
            <>
              <Divider />
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Most Common Conditions
                </Typography>
                <Stack spacing={1}>
                  {statistics.most_common_diseases.slice(0, 3).map((item, index) => (
                    <Stack key={index} direction="row" justifyContent="space-between">
                      <Typography variant="body2">{item.disease}</Typography>
                      <Typography variant="body2" fontWeight="medium">
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
              <Divider />
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Last Assessment
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {format(new Date(statistics.last_assessment_date), 'MMM dd, yyyy')}
                </Typography>
              </Box>
            </>
          )}

          {/* Account Age */}
          {statistics.account_age_days !== undefined && (
            <Box>
              <Typography variant="body2" color="text.secondary">
                Member for
              </Typography>
              <Typography variant="body2" fontWeight="medium">
                {statistics.account_age_days} days
              </Typography>
            </Box>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
