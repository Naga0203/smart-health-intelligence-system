// ============================================================================
// Google OAuth Button Component Tests
// ============================================================================

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { GoogleAuthButton } from './GoogleAuthButton';
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

describe('GoogleAuthButton', () => {
  const mockLoginWithGoogle = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Default mock implementation
    useAuthStore.mockReturnValue({
      loginWithGoogle: mockLoginWithGoogle,
    });
  });

  const renderWithRouter = () => {
    return render(
      <BrowserRouter>
        <GoogleAuthButton />
      </BrowserRouter>
    );
  };

  describe('Google OAuth button click', () => {
    it('should call loginWithGoogle when button is clicked', async () => {
      const user = userEvent.setup();
      mockLoginWithGoogle.mockResolvedValue();

      renderWithRouter();

      const button = screen.getByRole('button', { name: /continue with google/i });
      await user.click(button);

      await waitFor(() => {
        expect(mockLoginWithGoogle).toHaveBeenCalledTimes(1);
      });
    });

    it('should navigate to dashboard after successful Google login', async () => {
      const user = userEvent.setup();
      mockLoginWithGoogle.mockResolvedValue();

      renderWithRouter();

      const button = screen.getByRole('button', { name: /continue with google/i });
      await user.click(button);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/app/dashboard');
      });
    });

    it('should handle Google login failure gracefully', async () => {
      const user = userEvent.setup();
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      mockLoginWithGoogle.mockRejectedValue(new Error('Google auth failed'));

      renderWithRouter();

      const button = screen.getByRole('button', { name: /continue with google/i });
      await user.click(button);

      await waitFor(() => {
        expect(mockLoginWithGoogle).toHaveBeenCalledTimes(1);
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          'Google login failed:',
          expect.any(Error)
        );
      });

      // Should not navigate on failure
      expect(mockNavigate).not.toHaveBeenCalled();

      consoleErrorSpy.mockRestore();
    });
  });

  describe('loading state', () => {
    it('should show loading text when button is clicked', async () => {
      const user = userEvent.setup();
      // Make the promise not resolve immediately
      mockLoginWithGoogle.mockImplementation(() => new Promise(() => {}));

      renderWithRouter();

      const button = screen.getByRole('button', { name: /continue with google/i });
      await user.click(button);

      // Button should show loading text
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /signing in/i })).toBeInTheDocument();
      });
    });

    it('should disable button during loading', async () => {
      const user = userEvent.setup();
      mockLoginWithGoogle.mockImplementation(() => new Promise(() => {}));

      renderWithRouter();

      const button = screen.getByRole('button', { name: /continue with google/i });
      await user.click(button);

      await waitFor(() => {
        const loadingButton = screen.getByRole('button', { name: /signing in/i });
        expect(loadingButton).toBeDisabled();
      });
    });

    it('should re-enable button after successful login', async () => {
      const user = userEvent.setup();
      mockLoginWithGoogle.mockResolvedValue();

      renderWithRouter();

      const button = screen.getByRole('button', { name: /continue with google/i });
      await user.click(button);

      // Wait for login to complete
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalled();
      });

      // Button should be enabled again
      const finalButton = screen.getByRole('button', { name: /continue with google/i });
      expect(finalButton).not.toBeDisabled();
    });

    it('should re-enable button after failed login', async () => {
      const user = userEvent.setup();
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      mockLoginWithGoogle.mockRejectedValue(new Error('Failed'));

      renderWithRouter();

      const button = screen.getByRole('button', { name: /continue with google/i });
      await user.click(button);

      // Wait for error handling
      await waitFor(() => {
        expect(consoleErrorSpy).toHaveBeenCalled();
      });

      // Button should be enabled again
      const finalButton = screen.getByRole('button', { name: /continue with google/i });
      expect(finalButton).not.toBeDisabled();

      consoleErrorSpy.mockRestore();
    });
  });

  describe('button rendering', () => {
    it('should render button with Google icon', () => {
      renderWithRouter();

      const button = screen.getByRole('button', { name: /continue with google/i });
      expect(button).toBeInTheDocument();
      
      // Check for Google icon (MUI Google icon renders as svg)
      const icon = button.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });

    it('should have correct initial text', () => {
      renderWithRouter();

      expect(screen.getByRole('button', { name: /continue with google/i })).toBeInTheDocument();
    });
  });
});
