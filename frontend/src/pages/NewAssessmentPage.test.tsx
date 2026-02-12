// ============================================================================
// New Assessment Page Unit Tests
// Tests for submission gating when model unavailable
// ============================================================================

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { NewAssessmentPage } from './NewAssessmentPage';
import { useSystemStore } from '@/stores/systemStore';
import { useAssessmentStore } from '@/stores/assessmentStore';
import { useAuthStore } from '@/stores/authStore';
import { useNotificationStore } from '@/stores/notificationStore';

// Mock stores
vi.mock('@/stores/systemStore');
vi.mock('@/stores/assessmentStore');
vi.mock('@/stores/authStore');
vi.mock('@/stores/notificationStore');

// Mock AssessmentStepper component
vi.mock('@/components/assessment/AssessmentStepper', () => ({
  AssessmentStepper: ({ disabled, loading }: any) => (
    <div data-testid="assessment-stepper">
      <button disabled={disabled || loading}>Submit Assessment</button>
      <div>Disabled: {disabled ? 'true' : 'false'}</div>
      <div>Loading: {loading ? 'true' : 'false'}</div>
    </div>
  ),
}));

describe('NewAssessmentPage - Submission Gating', () => {
  const mockFetchSystemStatus = vi.fn();
  const mockFetchModelInfo = vi.fn();
  const mockSubmitAssessment = vi.fn();
  const mockAddNotification = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    // Default mock implementations
    vi.mocked(useSystemStore).mockReturnValue({
      status: null,
      modelInfo: null,
      fetchSystemStatus: mockFetchSystemStatus,
      fetchModelInfo: mockFetchModelInfo,
    } as any);

    vi.mocked(useAssessmentStore).mockReturnValue({
      submitAssessment: mockSubmitAssessment,
      loading: false,
    } as any);

    vi.mocked(useAuthStore).mockReturnValue({
      user: { uid: 'test-user', email: 'test@example.com' },
    } as any);

    vi.mocked(useNotificationStore).mockReturnValue({
      addNotification: mockAddNotification,
    } as any);
  });

  /**
   * Test: Submission gating when model unavailable
   * Requirements: 10.6, 10.7
   */
  describe('Model Unavailable Gating', () => {
    it('should disable submission when system status is error', async () => {
      mockFetchSystemStatus.mockResolvedValue(undefined);
      mockFetchModelInfo.mockResolvedValue(undefined);

      vi.mocked(useSystemStore).mockReturnValue({
        status: { status: 'error', version: '1.0.0' },
        modelInfo: { model_loaded: true },
        fetchSystemStatus: mockFetchSystemStatus,
        fetchModelInfo: mockFetchModelInfo,
      } as any);

      render(
        <MemoryRouter>
          <NewAssessmentPage />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.queryByText('Checking system status...')).not.toBeInTheDocument();
      });

      // Should display error alert
      expect(screen.getByText(/assessment system is currently unavailable/i)).toBeInTheDocument();

      // Should disable the stepper
      const stepper = screen.getByTestId('assessment-stepper');
      expect(stepper).toHaveTextContent('Disabled: true');

      // Submit button should be disabled
      const submitButton = screen.getByRole('button', { name: /Submit Assessment/i });
      expect(submitButton).toBeDisabled();
    });

    it('should disable submission when model is not loaded', async () => {
      mockFetchSystemStatus.mockResolvedValue(undefined);
      mockFetchModelInfo.mockResolvedValue(undefined);

      vi.mocked(useSystemStore).mockReturnValue({
        status: { status: 'operational', version: '1.0.0' },
        modelInfo: { model_loaded: false, model_type: 'RandomForest' },
        fetchSystemStatus: mockFetchSystemStatus,
        fetchModelInfo: mockFetchModelInfo,
      } as any);

      render(
        <MemoryRouter>
          <NewAssessmentPage />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.queryByText('Checking system status...')).not.toBeInTheDocument();
      });

      // Should display model unavailable alert
      expect(screen.getByText(/prediction model is currently unavailable/i)).toBeInTheDocument();

      // Should disable the stepper
      const stepper = screen.getByTestId('assessment-stepper');
      expect(stepper).toHaveTextContent('Disabled: true');

      // Submit button should be disabled
      const submitButton = screen.getByRole('button', { name: /Submit Assessment/i });
      expect(submitButton).toBeDisabled();
    });

    it('should enable submission when system is operational and model is loaded', async () => {
      mockFetchSystemStatus.mockResolvedValue(undefined);
      mockFetchModelInfo.mockResolvedValue(undefined);

      vi.mocked(useSystemStore).mockReturnValue({
        status: { status: 'operational', version: '1.0.0' },
        modelInfo: { model_loaded: true, model_type: 'RandomForest' },
        fetchSystemStatus: mockFetchSystemStatus,
        fetchModelInfo: mockFetchModelInfo,
      } as any);

      render(
        <MemoryRouter>
          <NewAssessmentPage />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.queryByText('Checking system status...')).not.toBeInTheDocument();
      });

      // Should not display error alerts
      expect(screen.queryByText(/assessment system is currently unavailable/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/prediction model is currently unavailable/i)).not.toBeInTheDocument();

      // Should enable the stepper
      const stepper = screen.getByTestId('assessment-stepper');
      expect(stepper).toHaveTextContent('Disabled: false');

      // Submit button should be enabled
      const submitButton = screen.getByRole('button', { name: /Submit Assessment/i });
      expect(submitButton).not.toBeDisabled();
    });

    it('should enable submission when system is degraded but model is loaded', async () => {
      mockFetchSystemStatus.mockResolvedValue(undefined);
      mockFetchModelInfo.mockResolvedValue(undefined);

      vi.mocked(useSystemStore).mockReturnValue({
        status: { status: 'degraded', version: '1.0.0' },
        modelInfo: { model_loaded: true, model_type: 'RandomForest' },
        fetchSystemStatus: mockFetchSystemStatus,
        fetchModelInfo: mockFetchModelInfo,
      } as any);

      render(
        <MemoryRouter>
          <NewAssessmentPage />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.queryByText('Checking system status...')).not.toBeInTheDocument();
      });

      // Should display degraded warning but allow submission
      expect(screen.getByText(/system is experiencing degraded performance/i)).toBeInTheDocument();

      // Should enable the stepper
      const stepper = screen.getByTestId('assessment-stepper');
      expect(stepper).toHaveTextContent('Disabled: false');

      // Submit button should be enabled
      const submitButton = screen.getByRole('button', { name: /Submit Assessment/i });
      expect(submitButton).not.toBeDisabled();
    });
  });

  /**
   * Test: System health check before submission
   * Requirements: 10.7
   */
  describe('System Health Check', () => {
    it('should check system status on mount', async () => {
      mockFetchSystemStatus.mockResolvedValue(undefined);
      mockFetchModelInfo.mockResolvedValue(undefined);

      render(
        <MemoryRouter>
          <NewAssessmentPage />
        </MemoryRouter>
      );

      // Should display loading state initially
      expect(screen.getByText('Checking system status...')).toBeInTheDocument();

      await waitFor(() => {
        expect(mockFetchSystemStatus).toHaveBeenCalled();
        expect(mockFetchModelInfo).toHaveBeenCalled();
      });
    });

    it('should handle system check failure gracefully', async () => {
      mockFetchSystemStatus.mockRejectedValue(new Error('Network error'));
      mockFetchModelInfo.mockRejectedValue(new Error('Network error'));

      render(
        <MemoryRouter>
          <NewAssessmentPage />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.queryByText('Checking system status...')).not.toBeInTheDocument();
      });

      // Should disable submission when check fails
      const stepper = screen.getByTestId('assessment-stepper');
      expect(stepper).toHaveTextContent('Disabled: true');
    });
  });

  /**
   * Test: Maintenance message display
   * Requirements: 10.6
   */
  describe('Maintenance Messages', () => {
    it('should display maintenance message when system is unavailable', async () => {
      mockFetchSystemStatus.mockResolvedValue(undefined);
      mockFetchModelInfo.mockResolvedValue(undefined);

      vi.mocked(useSystemStore).mockReturnValue({
        status: { status: 'error', version: '1.0.0' },
        modelInfo: null,
        fetchSystemStatus: mockFetchSystemStatus,
        fetchModelInfo: mockFetchModelInfo,
      } as any);

      render(
        <MemoryRouter>
          <NewAssessmentPage />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.queryByText('Checking system status...')).not.toBeInTheDocument();
      });

      // Should display maintenance message
      expect(screen.getByText(/assessment system is currently unavailable/i)).toBeInTheDocument();
      expect(screen.getByText(/Please try again later or contact support/i)).toBeInTheDocument();
    });

    it('should display model maintenance message when model is not loaded', async () => {
      mockFetchSystemStatus.mockResolvedValue(undefined);
      mockFetchModelInfo.mockResolvedValue(undefined);

      vi.mocked(useSystemStore).mockReturnValue({
        status: { status: 'operational', version: '1.0.0' },
        modelInfo: { model_loaded: false },
        fetchSystemStatus: mockFetchSystemStatus,
        fetchModelInfo: mockFetchModelInfo,
      } as any);

      render(
        <MemoryRouter>
          <NewAssessmentPage />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.queryByText('Checking system status...')).not.toBeInTheDocument();
      });

      // Should display model maintenance message
      expect(screen.getByText(/prediction model is currently unavailable/i)).toBeInTheDocument();
      expect(screen.getByText(/system is undergoing maintenance/i)).toBeInTheDocument();
    });

    it('should display degraded performance warning', async () => {
      mockFetchSystemStatus.mockResolvedValue(undefined);
      mockFetchModelInfo.mockResolvedValue(undefined);

      vi.mocked(useSystemStore).mockReturnValue({
        status: { status: 'degraded', version: '1.0.0' },
        modelInfo: { model_loaded: true },
        fetchSystemStatus: mockFetchSystemStatus,
        fetchModelInfo: mockFetchModelInfo,
      } as any);

      render(
        <MemoryRouter>
          <NewAssessmentPage />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.queryByText('Checking system status...')).not.toBeInTheDocument();
      });

      // Should display degraded performance warning
      expect(screen.getByText(/system is experiencing degraded performance/i)).toBeInTheDocument();
      expect(screen.getByText(/Assessments may take longer than usual/i)).toBeInTheDocument();
    });
  });
});
