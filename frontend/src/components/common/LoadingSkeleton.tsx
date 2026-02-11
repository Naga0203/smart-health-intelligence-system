// ============================================================================
// Loading Skeleton Component
// ============================================================================

import { Box, Skeleton, Stack } from '@mui/material';

interface LoadingSkeletonProps {
  variant?: 'text' | 'rectangular' | 'circular' | 'card' | 'list' | 'dashboard';
  count?: number;
  height?: number | string;
  width?: number | string;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  variant = 'rectangular',
  count = 1,
  height = 40,
  width = '100%',
}) => {
  // Card skeleton for assessment cards, profile cards, etc.
  if (variant === 'card') {
    return (
      <Stack spacing={2}>
        {Array.from({ length: count }).map((_, index) => (
          <Box key={index} sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
            <Skeleton variant="text" width="60%" height={30} />
            <Skeleton variant="text" width="40%" height={20} sx={{ mt: 1 }} />
            <Skeleton variant="rectangular" width="100%" height={100} sx={{ mt: 2 }} />
            <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
              <Skeleton variant="rectangular" width={80} height={30} />
              <Skeleton variant="rectangular" width={80} height={30} />
            </Stack>
          </Box>
        ))}
      </Stack>
    );
  }

  // List skeleton for assessment history, etc.
  if (variant === 'list') {
    return (
      <Stack spacing={1}>
        {Array.from({ length: count }).map((_, index) => (
          <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 1 }}>
            <Skeleton variant="circular" width={40} height={40} />
            <Box sx={{ flex: 1 }}>
              <Skeleton variant="text" width="70%" height={20} />
              <Skeleton variant="text" width="40%" height={16} />
            </Box>
          </Box>
        ))}
      </Stack>
    );
  }

  // Dashboard skeleton with multiple sections
  if (variant === 'dashboard') {
    return (
      <Box>
        <Skeleton variant="text" width="30%" height={40} sx={{ mb: 3 }} />
        
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} sx={{ mb: 3 }}>
          <Box sx={{ flex: 1 }}>
            <Skeleton variant="rectangular" height={120} />
          </Box>
          <Box sx={{ flex: 1 }}>
            <Skeleton variant="rectangular" height={120} />
          </Box>
          <Box sx={{ flex: 1 }}>
            <Skeleton variant="rectangular" height={120} />
          </Box>
        </Stack>

        <Skeleton variant="text" width="25%" height={30} sx={{ mb: 2 }} />
        <Stack spacing={2}>
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} variant="rectangular" height={80} />
          ))}
        </Stack>
      </Box>
    );
  }

  // Basic skeleton variants
  return (
    <Stack spacing={1}>
      {Array.from({ length: count }).map((_, index) => (
        <Skeleton
          key={index}
          variant={variant}
          width={width}
          height={height}
        />
      ))}
    </Stack>
  );
};
