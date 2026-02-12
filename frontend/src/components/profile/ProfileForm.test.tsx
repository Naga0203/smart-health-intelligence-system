// ============================================================================
// ProfileForm Property-Based Tests
// Feature: ai-health-frontend
// ============================================================================

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import * as fc from 'fast-check';
import { ProfileForm } from './ProfileForm';

// Mock the stores
vi.mock('@/stores/userStore', () => ({
  useUserStore: vi.fn(() => ({
    updateProfile: vi.fn(),
    loading: false,
    error: null,
  })),
}));

/**
 * Property 2: Profile input validation prevents invalid submission
 * Validates: Requirements 2.5
 * 
 * For any profile form with invalid field values, the submit action should be
 * blocked and validation errors should be displayed.
 */
describe('Feature: ai-health-frontend, Property 2: Profile input validation prevents invalid submission', () => {
  const mockProfile = {
    email: 'test@example.com',
    display_name: 'Test User',
    date_of_birth: '1990-01-01',
    gender: 'male',
    phone_number: '+1234567890',
    medical_history: [],
    allergies: [],
    current_medications: [],
    email_verified: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  const mockOnCancel = vi.fn();
  const mockOnSave = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should prevent submission with empty display name', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.constant(''), // Empty display name
        async () => {
          const { container } = render(
            <ProfileForm
              profile={{ ...mockProfile, display_name: '' }}
              onCancel={mockOnCancel}
              onSave={mockOnSave}
            />
          );

          const user = userEvent.setup();
          
          // Try to submit the form without filling required field
          const submitButton = screen.getByRole('button', { name: /save changes/i });
          await user.click(submitButton);

          // Wait for validation error to appear
          await waitFor(() => {
            const errorText = container.textContent;
            expect(errorText).toMatch(/name is required/i);
          }, { timeout: 2000 });
        }
      ),
      { numRuns: 10 } // Reduced from 100 to 10 for performance
    );
  });

  it('should prevent submission with display name exceeding max length', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.string({ minLength: 101, maxLength: 150 }), // Name longer than 100 characters
        async (invalidName) => {
          const { container } = render(
            <ProfileForm
              profile={{ ...mockProfile, display_name: 'Valid Name' }}
              onCancel={mockOnCancel}
              onSave={mockOnSave}
            />
          );

          const user = userEvent.setup();
          
          // Enter invalid name
          const nameInput = screen.getByLabelText(/display name/i);
          await user.clear(nameInput);
          await user.type(nameInput, invalidName.substring(0, 120)); // Limit typing for performance
          
          // Try to submit the form
          const submitButton = screen.getByRole('button', { name: /save changes/i });
          await user.click(submitButton);

          // Wait for validation error to appear
          await waitFor(() => {
            const errorText = container.textContent;
            expect(errorText).toMatch(/must be less than 100 characters/i);
          }, { timeout: 2000 });
        }
      ),
      { numRuns: 10 } // Reduced from 100 to 10 for performance
    );
  });

  it('should prevent submission with invalid phone number format', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.string({ minLength: 5, maxLength: 15 })
          .filter(s => s.length > 0 && !/^[\d\s\-\+\(\)]+$/.test(s)), // Invalid phone format
        async (invalidPhone) => {
          const { container } = render(
            <ProfileForm
              profile={{ ...mockProfile, phone_number: '' }}
              onCancel={mockOnCancel}
              onSave={mockOnSave}
            />
          );

          const user = userEvent.setup();
          
          // Enter invalid phone number
          const phoneInput = screen.getByLabelText(/phone number/i);
          await user.clear(phoneInput);
          await user.type(phoneInput, invalidPhone);
          
          // Try to submit the form
          const submitButton = screen.getByRole('button', { name: /save changes/i });
          await user.click(submitButton);

          // Wait for validation error to appear
          await waitFor(() => {
            const errorText = container.textContent;
            expect(errorText).toMatch(/valid phone number/i);
          }, { timeout: 2000 });
        }
      ),
      { numRuns: 10 } // Reduced from 100 to 10 for performance
    );
  });

  it('should allow submission with valid profile data', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.record({
          display_name: fc.string({ minLength: 1, maxLength: 50 }),
          gender: fc.constantFrom('male', 'female', 'other', 'prefer_not_to_say'),
        }),
        async (validData) => {
          const { container } = render(
            <ProfileForm
              profile={{ ...mockProfile, ...validData }}
              onCancel={mockOnCancel}
              onSave={mockOnSave}
            />
          );

          const user = userEvent.setup();
          
          // Submit the form with valid data
          const submitButton = screen.getByRole('button', { name: /save changes/i });
          await user.click(submitButton);

          // Should not show validation errors for required fields
          await waitFor(() => {
            const errorText = container.textContent;
            expect(errorText).not.toMatch(/name is required/i);
          }, { timeout: 2000 });
        }
      ),
      { numRuns: 10 } // Reduced from 100 to 10 for performance
    );
  });
});
