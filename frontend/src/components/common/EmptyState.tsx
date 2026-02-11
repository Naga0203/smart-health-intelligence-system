// ============================================================================
// Empty State Component
// ============================================================================

import { Box, Typography, Button } from '@mui/material';
import { SvgIconComponent } from '@mui/icons-material';

interface EmptyStateProps {
  icon?: SvgIconComponent;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
}) => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      textAlign="center"
      py={8}
      px={3}
    >
      {Icon && (
        <Icon
          sx={{
            fontSize: 80,
            color: 'text.secondary',
            mb: 2,
            opacity: 0.5,
          }}
        />
      )}
      
      <Typography variant="h5" gutterBottom color="text.primary">
        {title}
      </Typography>
      
      {description && (
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3, maxWidth: 500 }}>
          {description}
        </Typography>
      )}
      
      {actionLabel && onAction && (
        <Button variant="contained" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </Box>
  );
};
