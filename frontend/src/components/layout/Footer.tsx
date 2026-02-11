// ============================================================================
// Footer Component
// ============================================================================

import { Box, Container, Typography, Link } from '@mui/material';

export const Footer = () => {
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        backgroundColor: (theme) =>
          theme.palette.mode === 'light'
            ? theme.palette.grey[200]
            : theme.palette.grey[800],
      }}
    >
      <Container maxWidth="xl">
        <Typography variant="body2" color="text.secondary" align="center">
          {'© '}
          {new Date().getFullYear()}
          {' AI Health Intelligence Platform. '}
          <Typography variant="caption" component="span" color="text.secondary">
            This platform provides educational information only and is not a substitute for professional medical advice.
          </Typography>
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
          <Link color="inherit" href="/privacy" underline="hover">
            Privacy Policy
          </Link>
          {' | '}
          <Link color="inherit" href="/terms" underline="hover">
            Terms of Service
          </Link>
        </Typography>
      </Container>
    </Box>
  );
};
