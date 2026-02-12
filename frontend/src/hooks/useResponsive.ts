// ============================================================================
// Responsive Hook - Helper for responsive behavior
// ============================================================================

import { useMediaQuery, useTheme } from '@mui/material';

/**
 * Custom hook for responsive breakpoint detection
 * Returns boolean flags for different screen sizes
 */
export const useResponsive = () => {
  const theme = useTheme();

  const isMobile = useMediaQuery(theme.breakpoints.down('md')); // <768px
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg')); // 768-1024px
  const isDesktop = useMediaQuery(theme.breakpoints.up('lg')); // >=1024px
  
  const isSmallMobile = useMediaQuery(theme.breakpoints.down('sm')); // <600px
  const isLargeDesktop = useMediaQuery(theme.breakpoints.up('xl')); // >=1440px

  return {
    isMobile,
    isTablet,
    isDesktop,
    isSmallMobile,
    isLargeDesktop,
    // Convenience flags
    isMobileOrTablet: isMobile || isTablet,
    isTabletOrDesktop: isTablet || isDesktop,
  };
};
