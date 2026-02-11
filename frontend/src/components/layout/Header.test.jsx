// ============================================================================
// Header Component Tests - Logout Functionality
// ============================================================================

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { Header } from './Header';
import { useAuthStore } from '@/stores/authStore';

// Mock the auth store
vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn(),
}));

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('Header - Logout Functionality', () => {
  const mockLogout = vi.fn();
  const mockOnMenuClick = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Default mock implementation with authenticated user
    useAuthStore.mockReturnValue({
      user: {
        uid: 'test-uid',
        email: 'test@example.com',
        displayName: 'Test User',
        photoURL: null,
      },
      logout: mockLogout,
    });
  });

  const renderWithRouter = () => {
    return render(
      <BrowserRouter>
        <Header onMenuClick={mockOnMenuClick} />
      </BrowserRouter>
    );
  };

  describe('logout button functionality', () => {
    it('should call logout when logout menu item is clicked', async () => {
      const user = userEvent.setup();
      mockLogout.mockResolvedValue();

      renderWithRouter();

      // Open user menu - find the icon button with AccountCircle icon
      const userMenuButton = screen.getByTestId('AccountCircleIcon').closest('button');
      await user.click(userMenuButton);

      // Click logout menu item
      const logoutMenuItem = screen.getByRole('menuitem', { name: /logout/i });
      await user.click(logoutMenuItem);

      await waitFor(() => {
        expect(mockLogout).toHaveBeenCalledTimes(1);
      });
    });

    it('should navigate to landing page after successful logout', async () => {
      const user = userEvent.setup();
      mockLogout.mockResolvedValue();

      renderWithRouter();

      // Open user menu
      const userMenuButton = screen.getByTestId('AccountCircleIcon').closest('button');
      await user.click(userMenuButton);

      // Click logout
      const logoutMenuItem = screen.getByRole('menuitem', { name: /logout/i });
      await user.click(logoutMenuItem);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/');
      });
    });

    it('should handle logout failure gracefully', async () => {
      const user = userEvent.setup();
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      mockLogout.mockRejectedValue(new Error('Logout failed'));

      renderWithRouter();

      // Open user menu
      const userMenuButton = screen.getByTestId('AccountCircleIcon').closest('button');
      await user.click(userMenuButton);

      // Click logout
      const logoutMenuItem = screen.getByRole('menuitem', { name: /logout/i });
      await user.click(logoutMenuItem);

      await waitFor(() => {
        expect(mockLogout).toHaveBeenCalledTimes(1);
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          'Logout failed:',
          expect.any(Error)
        );
      });

      // Should not navigate on failure
      expect(mockNavigate).not.toHaveBeenCalled();

      consoleErrorSpy.mockRestore();
    });

    it('should close menu after logout is initiated', async () => {
      const user = userEvent.setup();
      mockLogout.mockResolvedValue();

      renderWithRouter();

      // Open user menu
      const userMenuButton = screen.getByTestId('AccountCircleIcon').closest('button');
      await user.click(userMenuButton);

      // Verify menu is open
      expect(screen.getByRole('menuitem', { name: /logout/i })).toBeInTheDocument();

      // Click logout
      const logoutMenuItem = screen.getByRole('menuitem', { name: /logout/i });
      await user.click(logoutMenuItem);

      // Menu should close
      await waitFor(() => {
        expect(screen.queryByRole('menuitem', { name: /logout/i })).not.toBeInTheDocument();
      });
    });
  });

  describe('user menu interaction', () => {
    it('should open user menu when user button is clicked', async () => {
      const user = userEvent.setup();

      renderWithRouter();

      const userMenuButton = screen.getByTestId('AccountCircleIcon').closest('button');
      await user.click(userMenuButton);

      // Menu should be visible
      expect(screen.getByRole('menuitem', { name: /profile/i })).toBeInTheDocument();
      expect(screen.getByRole('menuitem', { name: /logout/i })).toBeInTheDocument();
    });

    it('should display user email in header when no display name', () => {
      useAuthStore.mockReturnValue({
        user: {
          uid: 'test-uid',
          email: 'test@example.com',
          displayName: null,
          photoURL: null,
        },
        logout: mockLogout,
      });

      renderWithRouter();

      expect(screen.getByText('test@example.com')).toBeInTheDocument();
    });

    it('should display user display name when available', () => {
      useAuthStore.mockReturnValue({
        user: {
          uid: 'test-uid',
          email: 'test@example.com',
          displayName: 'John Doe',
          photoURL: null,
        },
        logout: mockLogout,
      });

      renderWithRouter();

      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    it('should navigate to profile page when profile menu item is clicked', async () => {
      const user = userEvent.setup();

      renderWithRouter();

      // Open user menu
      const userMenuButton = screen.getByTestId('AccountCircleIcon').closest('button');
      await user.click(userMenuButton);

      // Click profile menu item
      const profileMenuItem = screen.getByRole('menuitem', { name: /profile/i });
      await user.click(profileMenuItem);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/app/profile');
      });
    });
  });

  describe('menu icon functionality', () => {
    it('should call onMenuClick when menu icon is clicked', async () => {
      const user = userEvent.setup();

      renderWithRouter();

      // Find the menu icon button by its test id
      const menuButton = screen.getByTestId('MenuIcon').closest('button');
      await user.click(menuButton);

      expect(mockOnMenuClick).toHaveBeenCalledTimes(1);
    });
  });
});
