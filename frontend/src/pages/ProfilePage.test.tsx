// ============================================================================
// ProfilePage Unit Tests
// ============================================================================

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ProfilePage } from './ProfilePage';
import { useUserStore } from '@/stores/userStore';
import { useNotificationStore } from '@/stores/notificationStore';

// Mock the stores
vi.mock('@/stores/userStore');
vi.mock('@/stores/notificationStore');

describe('ProfilePage', () => {
  const mockProfile = {
    email: 'test@example.com',
    display_name: 'Test User',
    date_of_birth: '1990-01-01',
    gender: 'male',
    phone_number: '+1234567890',
    medical_history: ['Diabetes'],
    allergies: ['Peanuts'],
    current_medications: ['Insulin'],
    email_verified: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  const mockFetchProfile = vi.fn();
  const mockAddNotification = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Setup default mock implementations
    (useUserStore as any).mockReturnValue({
      profile: mockProfile,
      loading: false,
      error: null,
      fetchProfile: mockFetchProfile,
    });

    (useNotificationStore as any).mockReturnValue({
      addNotification: mockAddNotification,
    });
  });

  /**
   * Test: Profile data fetching and display
   * Requirements: 2.1
   */
  it('should fetch and display profile data on mount', async () => {
    render(<ProfilePage />);

    // Should call fetchProfile on mount
    expect(mockFetchProfile).toHaveBeenCalledTimes(1);

    // Should display profile information
    await waitFor(() => {
      expect(screen.getByText('Test User')).toBeInTheDocument();
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
    });
  });

  /**
   * Test: Loading state
   * Requirements: 2.1
   */
  it('should display loading indicator while fetching profile', () => {
    (useUserStore as any).mockReturnValue({
      profile: null,
      loading: true,
      error: null,
      fetchProfile: mockFetchProfile,
    });

    render(<ProfilePage />);

    // Should show loading spinner
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  /**
   * Test: Error handling on fetch failure
   * Requirements: 2.4
   */
  it('should display error message when profile fetch fails', () => {
    const errorMessage = 'Failed to fetch profile';
    (useUserStore as any).mockReturnValue({
      profile: null,
      loading: false,
      error: errorMessage,
      fetchProfile: mockFetchProfile,
    });

    render(<ProfilePage />);

    // Should display error alert
    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  /**
   * Test: Toggle to edit mode
   * Requirements: 2.2
   */
  it('should switch to edit mode when edit button is clicked', async () => {
    render(<ProfilePage />);
    const user = userEvent.setup();

    // Should initially show view mode
    await waitFor(() => {
      expect(screen.getByText('Profile Information')).toBeInTheDocument();
    });

    // Click edit button
    const editButton = screen.getByRole('button', { name: /edit profile/i });
    await user.click(editButton);

    // Should switch to edit mode
    await waitFor(() => {
      expect(screen.getByText('Edit Profile')).toBeInTheDocument();
      expect(screen.getByLabelText(/display name/i)).toBeInTheDocument();
    });
  });

  /**
   * Test: Cancel edit mode
   * Requirements: 2.2
   */
  it('should return to view mode when cancel button is clicked', async () => {
    render(<ProfilePage />);
    const user = userEvent.setup();

    // Switch to edit mode
    const editButton = screen.getByRole('button', { name: /edit profile/i });
    await user.click(editButton);

    await waitFor(() => {
      expect(screen.getByText('Edit Profile')).toBeInTheDocument();
    });

    // Click cancel button
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelButton);

    // Should return to view mode
    await waitFor(() => {
      expect(screen.getByText('Profile Information')).toBeInTheDocument();
    });
  });

  /**
   * Test: Successful profile update
   * Requirements: 2.2, 2.3
   */
  it('should display success notification after successful profile update', async () => {
    const mockUpdateProfile = vi.fn().mockResolvedValue(undefined);
    (useUserStore as any).mockReturnValue({
      profile: mockProfile,
      loading: false,
      error: null,
      fetchProfile: mockFetchProfile,
      updateProfile: mockUpdateProfile,
    });

    render(<ProfilePage />);
    const user = userEvent.setup();

    // Switch to edit mode
    const editButton = screen.getByRole('button', { name: /edit profile/i });
    await user.click(editButton);

    // Update a field
    const nameInput = screen.getByLabelText(/display name/i);
    await user.clear(nameInput);
    await user.type(nameInput, 'Updated Name');

    // Submit the form
    const saveButton = screen.getByRole('button', { name: /save changes/i });
    await user.click(saveButton);

    // Should call updateProfile
    await waitFor(() => {
      expect(mockUpdateProfile).toHaveBeenCalled();
    });

    // Should display success notification
    await waitFor(() => {
      expect(mockAddNotification).toHaveBeenCalledWith({
        type: 'success',
        message: 'Profile updated successfully',
        dismissible: true,
      });
    });

    // Should return to view mode
    await waitFor(() => {
      expect(screen.getByText('Profile Information')).toBeInTheDocument();
    });
  });

  /**
   * Test: Form validation with invalid inputs
   * Requirements: 2.3, 2.4
   */
  it('should show validation errors for invalid inputs', async () => {
    render(<ProfilePage />);
    const user = userEvent.setup();

    // Switch to edit mode
    const editButton = screen.getByRole('button', { name: /edit profile/i });
    await user.click(editButton);

    // Clear required field
    const nameInput = screen.getByLabelText(/display name/i);
    await user.clear(nameInput);

    // Try to submit
    const saveButton = screen.getByRole('button', { name: /save changes/i });
    await user.click(saveButton);

    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText(/name is required/i)).toBeInTheDocument();
    });
  });

  /**
   * Test: Error handling on update failure
   * Requirements: 2.4
   */
  it('should display error message when profile update fails', async () => {
    const errorMessage = 'Failed to update profile';
    const mockUpdateProfile = vi.fn().mockRejectedValue(new Error(errorMessage));
    (useUserStore as any).mockReturnValue({
      profile: mockProfile,
      loading: false,
      error: errorMessage,
      fetchProfile: mockFetchProfile,
      updateProfile: mockUpdateProfile,
    });

    render(<ProfilePage />);
    const user = userEvent.setup();

    // Switch to edit mode
    const editButton = screen.getByRole('button', { name: /edit profile/i });
    await user.click(editButton);

    // Should display error in form
    await waitFor(() => {
      const alerts = screen.getAllByRole('alert');
      expect(alerts.length).toBeGreaterThan(0);
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });
});
