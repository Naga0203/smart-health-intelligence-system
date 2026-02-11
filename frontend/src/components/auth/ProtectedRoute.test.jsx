// ============================================================================
// Protected Route Component Tests
// ============================================================================

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { useAuthStore } from '@/stores/authStore';

// Mock the auth store
vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn(),
}));

// Test component to render inside protected route
const TestComponent = () => <div>Protected Content</div>;

// Helper function to render ProtectedRoute with router context
const renderWithRouter = (initialRoute = '/protected') => {
  window.history.pushState({}, 'Test page', initialRoute);
  
  return render(
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<div>Login Page</div>} />
        <Route
          path="/protected"
          element={
            <ProtectedRoute>
              <TestComponent />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
};

describe('ProtectedRoute', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('redirect to login when not authenticated', () => {
    it('should redirect to /login when user is null', () => {
      // Mock unauthenticated state
      useAuthStore.mockReturnValue({
        user: null,
        loading: false,
      });

      renderWithRouter('/protected');

      // Should show login page instead of protected content
      expect(screen.getByText('Login Page')).toBeInTheDocument();
      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });

    it('should redirect to /login when user is undefined', () => {
      // Mock unauthenticated state with undefined user
      useAuthStore.mockReturnValue({
        user: undefined,
        loading: false,
      });

      renderWithRouter('/protected');

      // Should show login page
      expect(screen.getByText('Login Page')).toBeInTheDocument();
      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });
  });

  describe('access granted when authenticated', () => {
    it('should render children when user is authenticated', () => {
      // Mock authenticated state
      useAuthStore.mockReturnValue({
        user: {
          uid: 'test-uid',
          email: 'test@example.com',
          displayName: 'Test User',
          photoURL: null,
        },
        loading: false,
      });

      renderWithRouter('/protected');

      // Should show protected content
      expect(screen.getByText('Protected Content')).toBeInTheDocument();
      expect(screen.queryByText('Login Page')).not.toBeInTheDocument();
    });

    it('should render children with minimal user object', () => {
      // Mock authenticated state with minimal user data
      useAuthStore.mockReturnValue({
        user: {
          uid: 'test-uid',
          email: 'test@example.com',
        },
        loading: false,
      });

      renderWithRouter('/protected');

      // Should show protected content
      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });
  });

  describe('loading state during auth check', () => {
    it('should show loading indicator when loading is true', () => {
      // Mock loading state
      useAuthStore.mockReturnValue({
        user: null,
        loading: true,
      });

      renderWithRouter('/protected');

      // Should show loading indicator (CircularProgress)
      // CircularProgress renders an svg with role="progressbar"
      const loadingIndicator = screen.getByRole('progressbar');
      expect(loadingIndicator).toBeInTheDocument();
      
      // Should not show protected content or login page
      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
      expect(screen.queryByText('Login Page')).not.toBeInTheDocument();
    });

    it('should show loading indicator even with user data when loading', () => {
      // Mock loading state with user data (edge case during refresh)
      useAuthStore.mockReturnValue({
        user: {
          uid: 'test-uid',
          email: 'test@example.com',
        },
        loading: true,
      });

      renderWithRouter('/protected');

      // Should show loading indicator
      const loadingIndicator = screen.getByRole('progressbar');
      expect(loadingIndicator).toBeInTheDocument();
    });

    it('should not show loading indicator when loading is false', () => {
      // Mock authenticated state with loading false
      useAuthStore.mockReturnValue({
        user: {
          uid: 'test-uid',
          email: 'test@example.com',
        },
        loading: false,
      });

      renderWithRouter('/protected');

      // Should not show loading indicator
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
      
      // Should show protected content
      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });
  });
});
