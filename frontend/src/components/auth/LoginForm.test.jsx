// ============================================================================
// LoginForm Component Tests
// ============================================================================

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('login form submission with valid credentials', () => {
    it('should call onSubmit with email and password when form is submitted with valid data', async () => {
      const user = userEvent.setup();
      mockOnSubmit.mockResolvedValue();

      render(
        <LoginForm
          onSubmit={mockOnSubmit}
          error={null}
          loading={false}
        />
      );

      // Fill in the form
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      // Verify onSubmit was called with correct credentials
      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledTimes(1);
        expect(mockOnSubmit).toHaveBeenCalledWith('test@example.com', 'password123');
      });
    });

    it('should handle successful submission with different valid credentials', async () => {
      const user = userEvent.setup();
      mockOnSubmit.mockResolvedValue();

      render(
        <LoginForm
          onSubmit={mockOnSubmit}
          error={null}
          loading={false}
        />
      );

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, 'another@test.com');
      await user.type(passwordInput, 'securepass456');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith('another@test.com', 'securepass456');
      });
    });
  });

  describe('login form validation with invalid inputs', () => {
    it('should show validation error for invalid email format', async () => {
      const user = userEvent.setup();

      render(
        <LoginForm
          onSubmit={mockOnSubmit}
          error={null}
          loading={false}
        />
      );

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // Enter invalid email
      await user.type(emailInput, 'invalid-email');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      // Should show email validation error
      await waitFor(() => {
        expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
      });

      // Should not call onSubmit
      expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    it('should show validation error for password shorter than 6 characters', async () => {
      const user = userEvent.setup();

      render(
        <LoginForm
          onSubmit={mockOnSubmit}
          error={null}
          loading={false}
        />
      );

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, '12345'); // Only 5 characters
      await user.click(submitButton);

      // Should show password validation error
      await waitFor(() => {
        expect(screen.getByText(/password must be at least 6 characters/i)).toBeInTheDocument();
      });

      // Should not call onSubmit
      expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    it('should show validation errors for both invalid email and short password', async () => {
      const user = userEvent.setup();

      render(
        <LoginForm
          onSubmit={mockOnSubmit}
          error={null}
          loading={false}
        />
      );

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, 'not-an-email');
      await user.type(passwordInput, '123');
      await user.click(submitButton);

      // Should show both validation errors
      await waitFor(() => {
        expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
        expect(screen.getByText(/password must be at least 6 characters/i)).toBeInTheDocument();
      });

      // Should not call onSubmit
      expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    it('should not submit when fields are empty', async () => {
      const user = userEvent.setup();

      render(
        <LoginForm
          onSubmit={mockOnSubmit}
          error={null}
          loading={false}
        />
      );

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      await user.click(submitButton);

      // Should show validation errors for empty fields
      await waitFor(() => {
        expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
        expect(screen.getByText(/password must be at least 6 characters/i)).toBeInTheDocument();
      });

      // Should not call onSubmit
      expect(mockOnSubmit).not.toHaveBeenCalled();
    });
  });

  describe('error display', () => {
    it('should display error message when error prop is provided', () => {
      render(
        <LoginForm
          onSubmit={mockOnSubmit}
          error="Invalid credentials"
          loading={false}
        />
      );

      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    });

    it('should not display error when error prop is null', () => {
      render(
        <LoginForm
          onSubmit={mockOnSubmit}
          error={null}
          loading={false}
        />
      );

      // Alert should not be present
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });
  });

  describe('loading state', () => {
    it('should disable inputs and button when loading is true', () => {
      render(
        <LoginForm
          onSubmit={mockOnSubmit}
          error={null}
          loading={true}
        />
      );

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /signing in/i });

      expect(emailInput).toBeDisabled();
      expect(passwordInput).toBeDisabled();
      expect(submitButton).toBeDisabled();
    });

    it('should show "Signing in..." text when loading', () => {
      render(
        <LoginForm
          onSubmit={mockOnSubmit}
          error={null}
          loading={true}
        />
      );

      expect(screen.getByRole('button', { name: /signing in/i })).toBeInTheDocument();
    });

    it('should enable inputs and button when loading is false', () => {
      render(
        <LoginForm
          onSubmit={mockOnSubmit}
          error={null}
          loading={false}
        />
      );

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      expect(emailInput).not.toBeDisabled();
      expect(passwordInput).not.toBeDisabled();
      expect(submitButton).not.toBeDisabled();
    });
  });
});
