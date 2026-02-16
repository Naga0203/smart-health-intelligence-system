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
  primary: {
    main: '#667eea',      // Modern purple-blue
    light: '#a5b4fc',
    dark: '#4c51bf',
    contrastText: '#FFFFFF',
  },
  secondary: {
    main: '#f093fb',      // Soft pink-purple
    light: '#fbc2eb',
    dark: '#c471ed',
    contrastText: '#FFFFFF',
  },
  background: {
    default: '#f8fafc',   // Very light blue-gray
    paper: '#FFFFFF',
  },
  text: {
    primary: '#1e293b',   // Slate gray for primary text
    secondary: '#64748b', // Medium slate for secondary text
  },
  // Risk level colors with modern gradients
  success: {
    main: '#10b981',      // Emerald green
    light: '#6ee7b7',
    dark: '#059669',
  },
  warning: {
    main: '#f59e0b',      // Amber
    light: '#fcd34d',
    dark: '#d97706',
  },
  error: {
    main: '#ef4444',      // Modern red
    light: '#fca5a5',
    dark: '#dc2626',
  },
  info: {
    main: '#06b6d4',      // Cyan
    light: '#67e8f9',
    dark: '#0891b2',
  },
  // Custom gradient colors
  gradient: {
    primary: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    secondary: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    success: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    info: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    warm: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    cool: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
    sunset: 'linear-gradient(135deg, #ff6b6b 0%, #feca57 100%)',
    ocean: 'linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%)',
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
        borderRadius: '12px',
        padding: '10px 20px',
        fontWeight: 600,
        boxShadow: 'none',
        transition: 'all 0.3s ease',
        '@media (min-width:768px)': {
          padding: '12px 24px',
        },
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 10px 20px rgba(0,0,0,0.1)',
        },
      },
      contained: {
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        '&:hover': {
          background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
        },
      },
      sizeLarge: {
        padding: '14px 28px',
        fontSize: '1rem',
        borderRadius: '14px',
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
        borderRadius: '16px',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        transition: 'all 0.3s ease',
        '&:hover': {
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
          transform: 'translateY(-4px)',
        },
      },
    },
  },
  MuiAppBar: {
    styleOverrides: {
      root: {
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        backdropFilter: 'blur(10px)',
      },
    },
  },
  MuiPaper: {
    styleOverrides: {
      root: {
        borderRadius: '16px',
        backgroundImage: 'none',
      },
      elevation1: {
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
      },
      elevation2: {
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      },
      elevation3: {
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
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
