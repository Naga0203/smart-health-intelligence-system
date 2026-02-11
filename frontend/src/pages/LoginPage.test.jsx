// ============================================================================
// Login Page Tests - Redirect After Successful Login
// ============================================================================

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { LoginPage } from './LoginPage';
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

// Mock child components to simplify testing
vi.mock('@/components/auth/LoginForm', () => ({
  LoginForm: ({ onSubmit, error, loading }) => (
    <div data-testid="login-form">
      <button onClick={() => onSubmit('test@example.com', 'password123')}>
        Submit Login
      </button>
      {error && <div data-testid="error">{error}</div>}
      {loading && <div data-testid="loading">Loading...</div>}
    </div>
  ),
}));

vi.mock('@/components/auth/GoogleAuthButton', () => ({
  GoogleAuthButton: () => <button data-testid="google-button">Google Login</button>,
}));

describe('LoginPage - Redirect After Successful Login', () => {
  const mockLogin = vi.fn();
  const mockClearError = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
  });

  const renderWithRouter = () => {
    return render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
  };

  describe('redirect after successful login', () => {
    it('should redirect to dashboard when user is already authenticated', () => {
      // Mock authenticated state
      useAuthStore.mockReturnValue({
        user: {
          uid: 'test-uid',
          email: 'test@example.com',
          displayName: 'Test User',
          photoURL: null,
        },
        login: mockLogin,
        error: null,
        loading: false,
        clearError: mockClearError,
      });

      renderWithRouter();

      // Should redirect to dashboard
      expect(mockNavigate).toHaveBeenCalledWith('/app/dashboard');
    });

    it('should redirect to dashboard after successful login', async () => {
      const user = userEvent.setup();
      
      // Start with unauthenticated state
      const mockStoreState = {
        user: null,
        login: mockLogin,
        error: null,
        loading: false,
        clearError: mockClearError,
      };

      useAuthStore.mockReturnValue(mockStoreState);

      // Mock login to update user state
      mockLogin.mockImplementation(() => {
        // Simulate successful login by updating the mock
        mockStoreState.user = {
          uid: 'test-uid',
          email: 'test@example.com',
          displayName: 'Test User',
          photoURL: null,
        };
        useAuthStore.mockReturnValue(mockStoreState);
        return Promise.resolve();
      });

      const { rerender } = renderWithRouter();

      // Trigger login
      const submitButton = screen.getByText('Submit Login');
      await user.click(submitButton);

      // Wait for login to complete
      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
      });

      // Force re-render to trigger useEffect with updated user
      rerender(
        <BrowserRouter>
          <LoginPage />
        </BrowserRouter>
      );

      // Should redirect to dashboard
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/app/dashboard');
      });
    });

    it('should not redirect when login fails', async () => {
      const user = userEvent.setup();
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      useAuthStore.mockReturnValue({
        user: null,
        login: mockLogin,
        error: 'Invalid credentials',
        loading: false,
        clearError: mockClearError,
      });

      mockLogin.mockRejectedValue(new Error('Invalid credentials'));

      renderWithRouter();

      // Trigger login
      const submitButton = screen.getByText('Submit Login');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalled();
      });

      // Should not redirect
      expect(mockNavigate).not.toHaveBeenCalled();

      consoleErrorSpy.mockRestore();
    });

    it('should not redirect when user is null', () => {
      useAuthStore.mockReturnValue({
        user: null,
        login: mockLogin,
        error: null,
        loading: false,
        clearError: mockClearError,
      });

      renderWithRouter();

      // Should not redirect
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  describe('error handling', () => {
    it('should display error from auth store', () => {
      useAuthStore.mockReturnValue({
        user: null,
        login: mockLogin,
        error: 'Authentication failed',
        loading: false,
        clearError: mockClearError,
      });

      renderWithRouter();

      expect(screen.getByTestId('error')).toHaveTextContent('Authentication failed');
    });

    it('should clear error on component unmount', () => {
      useAuthStore.mockReturnValue({
        user: null,
        login: mockLogin,
        error: 'Some error',
        loading: false,
        clearError: mockClearError,
      });

      const { unmount } = renderWithRouter();

      unmount();

      expect(mockClearError).toHaveBeenCalled();
    });
  });

  describe('loading state', () => {
    it('should pass loading state to LoginForm', () => {
      useAuthStore.mockReturnValue({
        user: null,
        login: mockLogin,
        error: null,
        loading: true,
        clearError: mockClearError,
      });

      renderWithRouter();

      expect(screen.getByTestId('loading')).toBeInTheDocument();
    });

    it('should not show loading when loading is false', () => {
      useAuthStore.mockReturnValue({
        user: null,
        login: mockLogin,
        error: null,
        loading: false,
        clearError: mockClearError,
      });

      renderWithRouter();

      expect(screen.queryByTestId('loading')).not.toBeInTheDocument();
    });
  });

  describe('page rendering', () => {
    it('should render login form and Google button', () => {
      useAuthStore.mockReturnValue({
        user: null,
        login: mockLogin,
        error: null,
        loading: false,
        clearError: mockClearError,
      });

      renderWithRouter();

      expect(screen.getByTestId('login-form')).toBeInTheDocument();
      expect(screen.getByTestId('google-button')).toBeInTheDocument();
    });

    it('should render page title', () => {
      useAuthStore.mockReturnValue({
        user: null,
        login: mockLogin,
        error: null,
        loading: false,
        clearError: mockClearError,
      });

      renderWithRouter();

      expect(screen.getByText('AI Health Intelligence')).toBeInTheDocument();
    });

    it('should render sign in description', () => {
      useAuthStore.mockReturnValue({
        user: null,
        login: mockLogin,
        error: null,
        loading: false,
        clearError: mockClearError,
      });

      renderWithRouter();

      expect(screen.getByText(/sign in to access your health assessments/i)).toBeInTheDocument();
    });
  });
});
