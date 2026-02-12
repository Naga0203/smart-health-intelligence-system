// ============================================================================
// Theme Configuration - Medical-grade with Responsive Breakpoints
// ============================================================================

import { createTheme, ThemeOptions } from '@mui/material/styles';

// Define responsive breakpoints
// Mobile: <768px, Tablet: 768-1024px, Desktop: >1024px
const breakpoints = {
  values: {
    xs: 0,      // Mobile small
    sm: 600,    // Mobile large
    md: 768,    // Tablet
    lg: 1024,   // Desktop
    xl: 1440,   // Large desktop
  },
};

// Medical-grade color palette - calm, professional, non-alarming
const palette = {
  primary: {
    main: '#4A90E2',      // Calm blue
    light: '#7AB3F5',
    dark: '#2E5C8A',
    contrastText: '#FFFFFF',
  },
  secondary: {
    main: '#6B7280',      // Professional gray
    light: '#9CA3AF',
    dark: '#4B5563',
    contrastText: '#FFFFFF',
  },
  background: {
    default: '#F9FAFB',   // Light gray background
    paper: '#FFFFFF',
  },
  text: {
    primary: '#1F2937',   // Dark gray for primary text (4.5:1 contrast)
    secondary: '#6B7280', // Medium gray for secondary text
  },
  // Risk level colors - calm, not alarming
  success: {
    main: '#10B981',      // Calm green for low risk
    light: '#6EE7B7',
    dark: '#059669',
  },
  warning: {
    main: '#F59E0B',      // Amber for medium risk
    light: '#FCD34D',
    dark: '#D97706',
  },
  error: {
    main: '#EF4444',      // Soft red for high risk
    light: '#FCA5A5',
    dark: '#DC2626',
  },
  info: {
    main: '#3B82F6',      // Blue for informational
    light: '#93C5FD',
    dark: '#2563EB',
  },
};

// Typography with responsive sizing
const typography = {
  fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  // Responsive font sizes
  h1: {
    fontSize: '2rem',     // 32px mobile
    '@media (min-width:768px)': {
      fontSize: '2.5rem', // 40px tablet
    },
    '@media (min-width:1024px)': {
      fontSize: '3rem',   // 48px desktop
    },
    fontWeight: 600,
    lineHeight: 1.2,
  },
  h2: {
    fontSize: '1.5rem',   // 24px mobile
    '@media (min-width:768px)': {
      fontSize: '1.875rem', // 30px tablet
    },
    '@media (min-width:1024px)': {
      fontSize: '2.25rem', // 36px desktop
    },
    fontWeight: 600,
    lineHeight: 1.3,
  },
  h3: {
    fontSize: '1.25rem',  // 20px mobile
    '@media (min-width:768px)': {
      fontSize: '1.5rem', // 24px tablet
    },
    '@media (min-width:1024px)': {
      fontSize: '1.875rem', // 30px desktop
    },
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h4: {
    fontSize: '1.125rem', // 18px mobile
    '@media (min-width:768px)': {
      fontSize: '1.25rem', // 20px tablet
    },
    '@media (min-width:1024px)': {
      fontSize: '1.5rem', // 24px desktop
    },
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h5: {
    fontSize: '1rem',     // 16px mobile
    '@media (min-width:768px)': {
      fontSize: '1.125rem', // 18px tablet
    },
    '@media (min-width:1024px)': {
      fontSize: '1.25rem', // 20px desktop
    },
    fontWeight: 600,
    lineHeight: 1.5,
  },
  h6: {
    fontSize: '0.875rem', // 14px mobile
    '@media (min-width:768px)': {
      fontSize: '1rem',   // 16px tablet
    },
    '@media (min-width:1024px)': {
      fontSize: '1.125rem', // 18px desktop
    },
    fontWeight: 600,
    lineHeight: 1.5,
  },
  body1: {
    fontSize: '1rem',     // 16px
    lineHeight: 1.5,
  },
  body2: {
    fontSize: '0.875rem', // 14px
    lineHeight: 1.5,
  },
  button: {
    textTransform: 'none' as const, // Don't uppercase buttons
    fontWeight: 500,
  },
};

// Component overrides for responsive behavior
const components = {
  MuiContainer: {
    styleOverrides: {
      root: {
        paddingLeft: '16px',
        paddingRight: '16px',
        '@media (min-width:768px)': {
          paddingLeft: '24px',
          paddingRight: '24px',
        },
        '@media (min-width:1024px)': {
          paddingLeft: '32px',
          paddingRight: '32px',
        },
      },
    },
  },
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: '8px',
        padding: '8px 16px',
        '@media (min-width:768px)': {
          padding: '10px 20px',
        },
      },
      sizeLarge: {
        padding: '12px 24px',
        fontSize: '1rem',
        '@media (min-width:768px)': {
          padding: '14px 28px',
          fontSize: '1.125rem',
        },
      },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: '12px',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
      },
    },
  },
  MuiAppBar: {
    styleOverrides: {
      root: {
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
      },
    },
  },
  // Ensure proper focus indicators for accessibility
  MuiButtonBase: {
    defaultProps: {
      disableRipple: false,
    },
    styleOverrides: {
      root: {
        '&:focus-visible': {
          outline: '2px solid',
          outlineColor: palette.primary.main,
          outlineOffset: '2px',
        },
      },
    },
  },
};

// Spacing scale (8px base)
const spacing = 8;

const themeOptions: ThemeOptions = {
  breakpoints,
  palette,
  typography,
  components,
  spacing,
  shape: {
    borderRadius: 8,
  },
};

export const theme = createTheme(themeOptions);

// Export breakpoint values for use in components
export const BREAKPOINTS = {
  MOBILE: 768,
  TABLET: 1024,
} as const;

// Helper function to check if viewport is mobile
export const isMobile = () => window.innerWidth < BREAKPOINTS.MOBILE;

// Helper function to check if viewport is tablet
export const isTablet = () => 
  window.innerWidth >= BREAKPOINTS.MOBILE && 
  window.innerWidth < BREAKPOINTS.TABLET;

// Helper function to check if viewport is desktop
export const isDesktop = () => window.innerWidth >= BREAKPOINTS.TABLET;
