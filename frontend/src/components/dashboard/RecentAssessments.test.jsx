import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import RecentAssessments from './RecentAssessments';

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('RecentAssessments', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockAssessments = [
    {
      id: 'assessment-1',
      disease: 'Common Cold',
      confidence: 'HIGH',
      probability: 0.85,
      created_at: '2024-01-15T10:30:00Z',
    },
    {
      id: 'assessment-2',
      disease: 'Flu',
      confidence: 'MEDIUM',
      probability: 0.65,
      created_at: '2024-01-14T14:20:00Z',
    },
    {
      id: 'assessment-3',
      disease: 'Migraine',
      confidence: 'LOW',
      probability: 0.45,
      created_at: '2024-01-13T09:15:00Z',
    },
  ];

  it('should render loading skeleton when loading', () => {
    render(
      <BrowserRouter>
        <RecentAssessments assessments={[]} loading={true} />
      </BrowserRouter>
    );

    expect(screen.getByText('Recent Assessments')).toBeInTheDocument();
  });

  it('should render empty state when no assessments', () => {
    render(
      <BrowserRouter>
        <RecentAssessments assessments={[]} loading={false} />
      </BrowserRouter>
    );

    expect(screen.getByText('Recent Assessments')).toBeInTheDocument();
    expect(screen.getByText('No assessments yet')).toBeInTheDocument();
    expect(screen.getByText('Start your first health assessment to see results here')).toBeInTheDocument();
  });

  it('should render empty state when assessments is null', () => {
    render(
      <BrowserRouter>
        <RecentAssessments assessments={null} loading={false} />
      </BrowserRouter>
    );

    expect(screen.getByText('No assessments yet')).toBeInTheDocument();
  });

  it('should render list of assessments with all required information', () => {
    render(
      <BrowserRouter>
        <RecentAssessments assessments={mockAssessments} loading={false} />
      </BrowserRouter>
    );

    // Check that all assessments are rendered
    expect(screen.getByText('Common Cold')).toBeInTheDocument();
    expect(screen.getByText('Flu')).toBeInTheDocument();
    expect(screen.getByText('Migraine')).toBeInTheDocument();

    // Check confidence levels
    expect(screen.getByText('HIGH')).toBeInTheDocument();
    expect(screen.getByText('MEDIUM')).toBeInTheDocument();
    expect(screen.getByText('LOW')).toBeInTheDocument();

    // Check probabilities
    expect(screen.getByText(/Probability: 85%/)).toBeInTheDocument();
    expect(screen.getByText(/Probability: 65%/)).toBeInTheDocument();
    expect(screen.getByText(/Probability: 45%/)).toBeInTheDocument();
  });

  it('should navigate to assessment detail when assessment card is clicked', () => {
    render(
      <BrowserRouter>
        <RecentAssessments assessments={mockAssessments} loading={false} />
      </BrowserRouter>
    );

    // Click on the first assessment - find by role button
    const buttons = screen.getAllByRole('button');
    const firstAssessmentButton = buttons.find(btn => btn.textContent.includes('Common Cold'));
    fireEvent.click(firstAssessmentButton);

    // Verify navigation was called with correct ID
    expect(mockNavigate).toHaveBeenCalledWith('/app/assessment/assessment-1');
  });

  it('should navigate to correct assessment when different cards are clicked', () => {
    render(
      <BrowserRouter>
        <RecentAssessments assessments={mockAssessments} loading={false} />
      </BrowserRouter>
    );

    const buttons = screen.getAllByRole('button');

    // Click on the second assessment
    const secondAssessmentButton = buttons.find(btn => btn.textContent.includes('Flu'));
    fireEvent.click(secondAssessmentButton);

    expect(mockNavigate).toHaveBeenCalledWith('/app/assessment/assessment-2');

    // Click on the third assessment
    const thirdAssessmentButton = buttons.find(btn => btn.textContent.includes('Migraine'));
    fireEvent.click(thirdAssessmentButton);

    expect(mockNavigate).toHaveBeenCalledWith('/app/assessment/assessment-3');
  });

  it('should display formatted dates correctly', () => {
    render(
      <BrowserRouter>
        <RecentAssessments assessments={mockAssessments} loading={false} />
      </BrowserRouter>
    );

    // Check that dates are formatted (format: MMM dd, yyyy HH:mm)
    expect(screen.getByText(/Jan 15, 2024/)).toBeInTheDocument();
    expect(screen.getByText(/Jan 14, 2024/)).toBeInTheDocument();
    expect(screen.getByText(/Jan 13, 2024/)).toBeInTheDocument();
  });
});
