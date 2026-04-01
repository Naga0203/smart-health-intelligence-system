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

// Modern gradient-rich color palette with medical professionalism
const palette = {
  mode: 'dark' as const,
  primary: {
    main: '#0ea5e9',   // Accent Blue
    light: '#38bdf8',
    dark: '#0284c7',
  },
  secondary: {
    main: '#8b5cf6',   // Accent Violet
    light: '#a78bfa',
    dark: '#7c3aed',
  },
  background: {
    default: 'transparent', // Root background handled by GlobalLayout via tailwind classes
    paper: 'transparent',   // Handled by component overrides
  },
  text: {
    primary: '#ffffff',
    secondary: 'rgba(255, 255, 255, 0.8)',
    disabled: 'rgba(255, 255, 255, 0.6)',
  },
  success: {
    main: '#27AE60',
  },
  info: {
    main: '#0ea5e9',
  },
  warning: {
    main: '#F2994A',
    light: '#F2C94C',
  },
  error: {
    main: '#EB5757',
  },
  // Custom gradient colors
  gradient: {
    primary: 'linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%)', // Blue -> Violet
    secondary: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)', // Glass
    success: 'linear-gradient(135deg, #27AE60 0%, #2ECC71 100%)',
    info: 'linear-gradient(135deg, #1FA2FF 0%, #12D8FA 100%)',
    warm: 'linear-gradient(135deg, #F2994A 0%, #F2C94C 100%)',
    cool: 'linear-gradient(135deg, #56CCF2 0%, #2F80ED 100%)',
    sunset: 'linear-gradient(135deg, #EB5757 0%, #F2994A 100%)',
    ocean: 'linear-gradient(180deg, #EAF6FB 0%, #F5FBFF 100%)',
  },
};

// Typography with responsive sizing using clamp() for fluid typography
const typography = {
  fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  h1: {
    fontSize: 'clamp(2rem, 5vw, 3rem)',
    fontWeight: 600,
    lineHeight: 1.2,
  },
  h2: {
    fontSize: 'clamp(1.5rem, 4vw, 2.25rem)',
    fontWeight: 600,
    lineHeight: 1.3,
  },
  h3: {
    fontSize: 'clamp(1.25rem, 3vw, 1.875rem)',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h4: {
    fontSize: 'clamp(1.125rem, 2vw, 1.5rem)',
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h5: {
    fontSize: 'clamp(1rem, 1.5vw, 1.25rem)',
    fontWeight: 600,
    lineHeight: 1.5,
  },
  h6: {
    fontSize: 'clamp(0.875rem, 1.2vw, 1.125rem)',
    fontWeight: 600,
    lineHeight: 1.5,
  },
  body1: {
    fontSize: '1rem',
    lineHeight: 1.5,
  },
  body2: {
    fontSize: '0.875rem',
    lineHeight: 1.5,
  },
  button: {
    textTransform: 'none' as const,
    fontWeight: 500,
  },
};

// Component overrides for modern, responsive design with gradients
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
        borderRadius: '8px', // Slightly sharper for modern feel
        padding: '10px 20px',
        fontWeight: 600,
        boxShadow: 'none',
        textTransform: 'none',
        transition: 'all 0.2s ease-in-out',
        '@media (min-width:768px)': {
          padding: '12px 24px',
        },
        '&:hover': {
          transform: 'translateY(-1px)',
          boxShadow: '0 4px 12px rgba(47, 128, 237, 0.25)', // Blue shadow
        },
      },
      contained: {
        background: 'linear-gradient(to right, #3b82f6, #7c3aed)', /* from-blue-500 to-violet-600 */
        color: '#FFFFFF',
        border: 'none',
        transition: 'all 0.3s ease',
        '&:hover': {
          filter: 'brightness(1.1)',
          boxShadow: '0 0 20px rgba(14, 165, 233, 0.4)',
        },
      },
      outlined: {
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(12px)',
        color: '#ffffff',
        border: 'none',
        transition: 'all 0.3s ease',
        '&:hover': {
          backgroundColor: 'rgba(255, 255, 255, 0.2)',
          border: 'none',
        },
      },
      sizeLarge: {
        padding: '14px 28px',
        fontSize: '1rem',
        borderRadius: '10px',
        '@media (min-width:768px)': {
          padding: '16px 32px',
          fontSize: '1.125rem',
        },
      },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(24px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '16px',
        color: '#ffffff',
        transition: 'all 0.3s ease',
        boxShadow: 'none',
        '&:hover': {
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          boxShadow: '0 0 30px rgba(14, 165, 233, 0.2)',
          transform: 'translateY(-4px)',
        },
      },
    },
  },
  MuiAppBar: {
    styleOverrides: {
      root: {
        backgroundColor: 'rgba(7, 6, 18, 0.8)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        boxShadow: 'none',
      },
    },
  },
  MuiPaper: {
    styleOverrides: {
      root: {
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(24px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '16px',
        color: '#ffffff',
        backgroundImage: 'none',
        boxShadow: 'none',
        transition: 'all 0.3s ease',
      },
      elevation1: {
        boxShadow: 'none',
      },
      elevation2: {
        boxShadow: 'none',
      },
      elevation3: {
        boxShadow: 'none',
      },
    },
  },
  MuiChip: {
    styleOverrides: {
      root: {
        borderRadius: '8px',
        fontWeight: 500,
      },
      colorPrimary: {
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      },
      colorSecondary: {
        background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      },
    },
  },
  MuiTextField: {
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': {
          borderRadius: '12px',
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
          },
          '&.Mui-focused': {
            boxShadow: '0 0 0 3px rgba(102, 126, 234, 0.1)',
          },
        },
      },
    },
  },
  MuiLinearProgress: {
    styleOverrides: {
      root: {
        borderRadius: '8px',
        height: '8px',
      },
      bar: {
        borderRadius: '8px',
        background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
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
          outline: '3px solid',
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


// TypeScript module augmentation for custom theme properties
declare module '@mui/material/styles' {
  interface Palette {
    gradient: {
      primary: string;
      secondary: string;
      success: string;
      info: string;
      warm: string;
      cool: string;
      sunset: string;
      ocean: string;
    };
  }
  interface PaletteOptions {
    gradient?: {
      primary?: string;
      secondary?: string;
      success?: string;
      info?: string;
      warm?: string;
      cool?: string;
      sunset?: string;
      ocean?: string;
    };
  }
}
