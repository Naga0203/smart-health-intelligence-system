import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import DashboardPage from './DashboardPage';
import { useAssessmentStore } from '@/stores/assessmentStore';
import { useSystemStore } from '@/stores/systemStore';
import { useUserStore } from '@/stores/userStore';

// Mock the stores
vi.mock('@/stores/assessmentStore');
vi.mock('@/stores/systemStore');
vi.mock('@/stores/userStore');

// Mock the child components
vi.mock('@/components/dashboard/RecentAssessments', () => ({
  default: () => <div data-testid="recent-assessments">Recent Assessments</div>,
}));
vi.mock('@/components/dashboard/SystemStatus', () => ({
  default: () => <div data-testid="system-status">System Status</div>,
}));
vi.mock('@/components/dashboard/QuickActions', () => ({
  default: () => <div data-testid="quick-actions">Quick Actions</div>,
}));
vi.mock('@/components/dashboard/UserStatistics', () => ({
  default: () => <div data-testid="user-statistics">User Statistics</div>,
}));

describe('DashboardPage', () => {
  const mockFetchAssessmentHistory = vi.fn();
  const mockFetchSystemStatus = vi.fn();
  const mockFetchStatistics = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    useAssessmentStore.mockReturnValue({
      fetchAssessmentHistory: mockFetchAssessmentHistory,
      assessmentHistory: { assessments: [] },
      loading: false,
    });

    useSystemStore.mockReturnValue({
      fetchSystemStatus: mockFetchSystemStatus,
      status: { status: 'operational' },
      loading: false,
    });

    useUserStore.mockReturnValue({
      fetchStatistics: mockFetchStatistics,
      statistics: { total_assessments: 0 },
      loading: false,
    });
  });

  it('should fetch dashboard data on mount', async () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(mockFetchAssessmentHistory).toHaveBeenCalledWith(1, 5);
      expect(mockFetchSystemStatus).toHaveBeenCalled();
      expect(mockFetchStatistics).toHaveBeenCalled();
    });
  });

  it('should render all dashboard components', async () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByTestId('quick-actions')).toBeInTheDocument();
      expect(screen.getByTestId('system-status')).toBeInTheDocument();
      expect(screen.getByTestId('user-statistics')).toBeInTheDocument();
      expect(screen.getByTestId('recent-assessments')).toBeInTheDocument();
    });
  });

  it('should display loading skeleton when data is loading', () => {
    useAssessmentStore.mockReturnValue({
      fetchAssessmentHistory: mockFetchAssessmentHistory,
      assessmentHistory: null,
      loading: true,
    });

    useSystemStore.mockReturnValue({
      fetchSystemStatus: mockFetchSystemStatus,
      status: null,
      loading: true,
    });

    useUserStore.mockReturnValue({
      fetchStatistics: mockFetchStatistics,
      statistics: null,
      loading: true,
    });

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    // Should show loading skeleton when all data is null and loading
    expect(screen.queryByText('Dashboard')).not.toBeInTheDocument();
  });
});
