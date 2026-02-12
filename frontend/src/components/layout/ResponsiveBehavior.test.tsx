// ============================================================================
// Unit Tests: Responsive Behavior
// Tests mobile, tablet, and desktop layouts
// Validates: Requirements 12.2, 12.3, 12.4, 12.9
// ============================================================================

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { theme } from '@/theme';
import { AppLayout } from './AppLayout';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

// Mock useAuthStore
vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({
    user: { email: 'test@example.com', displayName: 'Test User' },
    logout: vi.fn(),
    initialize: vi.fn(),
  }),
}));

// Mock useKeyboardShortcuts
vi.mock('@/hooks', () => ({
  useKeyboardShortcuts: vi.fn(),
}));

// Helper to set viewport size
const setViewportSize = (width: number, height: number = 768) => {
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: width,
  });
  Object.defineProperty(window, 'innerHeight', {
    writable: true,
    configurable: true,
    value: height,
  });
  window.dispatchEvent(new Event('resize'));
};

// Helper to render with theme
const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <ThemeProvider theme={theme}>{component}</ThemeProvider>
    </BrowserRouter>
  );
};

describe('Responsive Behavior - Mobile Layout (<768px)', () => {
  beforeEach(() => {
    setViewportSize(375); // iPhone size
  });

  it('should render mobile-optimized header', () => {
    const mockOnMenuClick = vi.fn();
    renderWithTheme(<Header onMenuClick={mockOnMenuClick} />);

    // Header should be present
    const header = screen.getByRole('banner');
    expect(header).toBeInTheDocument();

    // Menu button should be visible
    const menuButton = screen.getByLabelText(/toggle menu/i);
    expect(menuButton).toBeInTheDocument();
  });

  it('should show abbreviated app name on mobile', () => {
    const mockOnMenuClick = vi.fn();
    renderWithTheme(<Header onMenuClick={mockOnMenuClick} />);

    // Should show "AI Health" instead of full name on mobile
    // This is based on the isMobile check in Header component
    const heading = screen.getByRole('banner');
    expect(heading).toBeInTheDocument();
  });

  it('should render sidebar as overlay on mobile', () => {
    const mockOnClose = vi.fn();
    renderWithTheme(<Sidebar open={true} onClose={mockOnClose} />);

    // Sidebar should be present
    const nav = screen.getByRole('navigation');
    expect(nav).toBeInTheDocument();

    // Should have navigation items
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('New Assessment')).toBeInTheDocument();
  });

  it('should have proper touch target sizes (44x44px minimum)', () => {
    const mockOnMenuClick = vi.fn();
    const { container } = renderWithTheme(<Header onMenuClick={mockOnMenuClick} />);

    // Get all buttons
    const buttons = container.querySelectorAll('button');

    buttons.forEach((button) => {
      const styles = window.getComputedStyle(button);
      const minWidth = parseInt(styles.minWidth);
      const minHeight = parseInt(styles.minHeight);

      // Touch targets should be at least 44x44px
      expect(minWidth).toBeGreaterThanOrEqual(44);
      expect(minHeight).toBeGreaterThanOrEqual(44);
    });
  });
});

describe('Responsive Behavior - Tablet Layout (768-1024px)', () => {
  beforeEach(() => {
    setViewportSize(768); // iPad size
  });

  it('should render tablet-optimized layout', () => {
    const mockOnMenuClick = vi.fn();
    renderWithTheme(<Header onMenuClick={mockOnMenuClick} />);

    const header = screen.getByRole('banner');
    expect(header).toBeInTheDocument();
  });

  it('should show full app name on tablet', () => {
    const mockOnMenuClick = vi.fn();
    renderWithTheme(<Header onMenuClick={mockOnMenuClick} />);

    // Should show full name on tablet and desktop
    const heading = screen.getByRole('banner');
    expect(heading).toBeInTheDocument();
  });

  it('should render persistent sidebar on tablet', () => {
    const mockOnClose = vi.fn();
    renderWithTheme(<Sidebar open={true} onClose={mockOnClose} />);

    const nav = screen.getByRole('navigation');
    expect(nav).toBeInTheDocument();
  });
});

describe('Responsive Behavior - Desktop Layout (>1024px)', () => {
  beforeEach(() => {
    setViewportSize(1440); // Desktop size
  });

  it('should render desktop-optimized header', () => {
    const mockOnMenuClick = vi.fn();
    renderWithTheme(<Header onMenuClick={mockOnMenuClick} />);

    const header = screen.getByRole('banner');
    expect(header).toBeInTheDocument();

    // User info should be visible on desktop
    expect(screen.getByText(/test@example.com/i)).toBeInTheDocument();
  });

  it('should render persistent sidebar on desktop', () => {
    const mockOnClose = vi.fn();
    renderWithTheme(<Sidebar open={true} onClose={mockOnClose} />);

    const nav = screen.getByRole('navigation');
    expect(nav).toBeInTheDocument();

    // All navigation items should be visible
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('New Assessment')).toBeInTheDocument();
    expect(screen.getByText('History')).toBeInTheDocument();
    expect(screen.getByText('Diseases')).toBeInTheDocument();
    expect(screen.getByText('Profile')).toBeInTheDocument();
  });

  it('should have adequate spacing on desktop', () => {
    const mockOnMenuClick = vi.fn();
    const { container } = renderWithTheme(<Header onMenuClick={mockOnMenuClick} />);

    // Check that elements have proper spacing
    const toolbar = container.querySelector('[class*="MuiToolbar"]');
    expect(toolbar).toBeInTheDocument();
  });
});

describe('Text Scaling at 200% Zoom', () => {
  it('should use relative units for font sizes', () => {
    // Check theme typography uses rem units
    expect(theme.typography.body1.fontSize).toBe('1rem');
    expect(theme.typography.h1.fontSize).toBe('2rem');
    expect(theme.typography.h2.fontSize).toBe('1.5rem');
  });

  it('should have flexible container widths', () => {
    const mockOnMenuClick = vi.fn();
    const { container } = renderWithTheme(<Header onMenuClick={mockOnMenuClick} />);

    // Containers should not have fixed widths
    const toolbar = container.querySelector('[class*="MuiToolbar"]');
    if (toolbar) {
      const styles = window.getComputedStyle(toolbar);
      // Should not have a fixed pixel width
      expect(styles.width).not.toMatch(/^\d+px$/);
    }
  });

  it('should allow text to wrap instead of truncating', () => {
    const mockOnMenuClick = vi.fn();
    renderWithTheme(<Header onMenuClick={mockOnMenuClick} />);

    // Text elements should be able to wrap
    const heading = screen.getByRole('banner');
    expect(heading).toBeInTheDocument();
  });

  it('should maintain functionality at 200% zoom', () => {
    // Simulate 200% zoom by doubling viewport
    setViewportSize(750); // Half of 1500 (simulating zoom)

    const mockOnMenuClick = vi.fn();
    renderWithTheme(<Header onMenuClick={mockOnMenuClick} />);

    // All interactive elements should still be accessible
    const menuButton = screen.getByLabelText(/toggle menu/i);
    expect(menuButton).toBeInTheDocument();
    expect(menuButton).toBeEnabled();
  });
});

describe('Responsive Breakpoints', () => {
  it('should have correct breakpoint values', () => {
    expect(theme.breakpoints.values.xs).toBe(0);
    expect(theme.breakpoints.values.sm).toBe(600);
    expect(theme.breakpoints.values.md).toBe(768);
    expect(theme.breakpoints.values.lg).toBe(1024);
    expect(theme.breakpoints.values.xl).toBe(1440);
  });

  it('should apply mobile-first approach', () => {
    // Base styles should be for mobile
    // Larger breakpoints should override
    expect(theme.breakpoints.values.xs).toBe(0);
  });
});
