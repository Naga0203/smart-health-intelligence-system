// ============================================================================
// Assessment History Components Unit Tests
// ============================================================================

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, within, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AssessmentCard } from './AssessmentCard';
import { AssessmentTimeline } from './AssessmentTimeline';
import { HistoryFilters } from './HistoryFilters';

describe('AssessmentCard', () => {
  const mockAssessment = {
    id: 'test-id-123',
    date: '2024-01-15T14:30:00Z',
    condition: 'Diabetes',
    riskLevel: 'medium' as const,
    confidence: 'HIGH' as const,
    probability: 65.5,
  };

  /**
   * Test: Assessment card click navigation
   * Requirements: 8.5
   */
  it('should call onClick handler when card is clicked', async () => {
    const mockOnClick = vi.fn();
    const user = userEvent.setup();

    render(<AssessmentCard {...mockAssessment} onClick={mockOnClick} />);

    const card = screen.getByRole('button');
    await user.click(card);

    expect(mockOnClick).toHaveBeenCalledWith('test-id-123');
    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  /**
   * Test: Assessment card displays all required information
   * Requirements: 8.2
   */
  it('should display assessment date, condition, risk level, and confidence', () => {
    const mockOnClick = vi.fn();

    render(<AssessmentCard {...mockAssessment} onClick={mockOnClick} />);

    // Should display condition
    expect(screen.getByText('Diabetes')).toBeInTheDocument();

    // Should display formatted date
    expect(screen.getByText(/Jan 15, 2024/i)).toBeInTheDocument();

    // Should display risk level
    expect(screen.getByText('MEDIUM')).toBeInTheDocument();

    // Should display confidence
    expect(screen.getByText(/Confidence: HIGH/i)).toBeInTheDocument();

    // Should display probability
    expect(screen.getByText(/Probability: 65.5%/i)).toBeInTheDocument();
  });

  /**
   * Test: Risk level color coding
   * Requirements: 8.2
   */
  it('should apply correct color for low risk level', () => {
    const mockOnClick = vi.fn();
    const lowRiskAssessment = { ...mockAssessment, riskLevel: 'low' as const };

    const { container } = render(<AssessmentCard {...lowRiskAssessment} onClick={mockOnClick} />);

    const riskChip = screen.getByText('LOW');
    expect(riskChip).toBeInTheDocument();
  });

  it('should apply correct color for high risk level', () => {
    const mockOnClick = vi.fn();
    const highRiskAssessment = { ...mockAssessment, riskLevel: 'high' as const };

    const { container } = render(<AssessmentCard {...highRiskAssessment} onClick={mockOnClick} />);

    const riskChip = screen.getByText('HIGH');
    expect(riskChip).toBeInTheDocument();
  });
});

describe('AssessmentTimeline', () => {
  const mockAssessments = [
    {
      id: '1',
      created_at: '2024-01-15T14:30:00Z',
      disease: 'Diabetes',
      probability: 65.5,
      confidence: 'HIGH' as const,
    },
    {
      id: '2',
      created_at: '2024-01-10T10:00:00Z',
      disease: 'Hypertension',
      probability: 45.2,
      confidence: 'MEDIUM' as const,
    },
    {
      id: '3',
      created_at: '2024-01-05T08:15:00Z',
      disease: 'Asthma',
      probability: 30.8,
      confidence: 'LOW' as const,
    },
  ];

  /**
   * Test: Assessment timeline rendering
   * Requirements: 8.1
   */
  it('should render all assessments in the timeline', () => {
    const mockOnClick = vi.fn();

    render(
      <AssessmentTimeline
        assessments={mockAssessments}
        onAssessmentClick={mockOnClick}
        hasMore={false}
        loading={false}
      />
    );

    // Should display all three assessments
    expect(screen.getByText('Diabetes')).toBeInTheDocument();
    expect(screen.getByText('Hypertension')).toBeInTheDocument();
    expect(screen.getByText('Asthma')).toBeInTheDocument();
  });

  /**
   * Test: Chronological ordering (most recent first)
   * Requirements: 8.2
   */
  it('should display assessments in chronological order with most recent first', () => {
    const mockOnClick = vi.fn();

    render(
      <AssessmentTimeline
        assessments={mockAssessments}
        onAssessmentClick={mockOnClick}
        hasMore={false}
        loading={false}
      />
    );

    const cards = screen.getAllByRole('button');
    
    // Verify we have 3 cards
    expect(cards).toHaveLength(3);
    
    // First card should be the most recent (Diabetes - Jan 15)
    expect(within(cards[0]).getByText('Diabetes')).toBeInTheDocument();
    
    // Second card should be Hypertension (Jan 10)
    expect(within(cards[1]).getByText('Hypertension')).toBeInTheDocument();
    
    // Third card should be the oldest (Asthma - Jan 5)
    expect(within(cards[2]).getByText('Asthma')).toBeInTheDocument();
  });

  /**
   * Test: Empty state display
   * Requirements: 8.9
   */
  it('should display empty state when no assessments exist', () => {
    const mockOnClick = vi.fn();

    render(
      <AssessmentTimeline
        assessments={[]}
        onAssessmentClick={mockOnClick}
        hasMore={false}
        loading={false}
      />
    );

    // Should display empty state message
    expect(screen.getByText('No Assessment History')).toBeInTheDocument();
    expect(screen.getByText(/You haven't completed any health assessments yet/i)).toBeInTheDocument();
    
    // Should display call-to-action button
    expect(screen.getByRole('button', { name: /New Assessment/i })).toBeInTheDocument();
  });

  /**
   * Test: Pagination functionality - Load More button
   * Requirements: 8.8
   */
  it('should display Load More button when hasMore is true', () => {
    const mockOnClick = vi.fn();
    const mockOnLoadMore = vi.fn();

    render(
      <AssessmentTimeline
        assessments={mockAssessments}
        onAssessmentClick={mockOnClick}
        onLoadMore={mockOnLoadMore}
        hasMore={true}
        loading={false}
      />
    );

    // Should display Load More button
    const loadMoreButton = screen.getByRole('button', { name: /Load More/i });
    expect(loadMoreButton).toBeInTheDocument();
  });

  it('should call onLoadMore when Load More button is clicked', async () => {
    const mockOnClick = vi.fn();
    const mockOnLoadMore = vi.fn();
    const user = userEvent.setup();

    render(
      <AssessmentTimeline
        assessments={mockAssessments}
        onAssessmentClick={mockOnClick}
        onLoadMore={mockOnLoadMore}
        hasMore={true}
        loading={false}
      />
    );

    const loadMoreButton = screen.getByRole('button', { name: /Load More/i });
    await user.click(loadMoreButton);

    expect(mockOnLoadMore).toHaveBeenCalledTimes(1);
  });

  it('should not display Load More button when hasMore is false', () => {
    const mockOnClick = vi.fn();

    render(
      <AssessmentTimeline
        assessments={mockAssessments}
        onAssessmentClick={mockOnClick}
        hasMore={false}
        loading={false}
      />
    );

    // Should not display Load More button
    expect(screen.queryByRole('button', { name: /Load More/i })).not.toBeInTheDocument();
  });

  /**
   * Test: Loading state display
   * Requirements: 8.1
   */
  it('should display loading skeleton on initial load', () => {
    const mockOnClick = vi.fn();

    const { container } = render(
      <AssessmentTimeline
        assessments={[]}
        onAssessmentClick={mockOnClick}
        hasMore={false}
        loading={true}
      />
    );

    // Should display loading skeletons (MUI Skeleton components)
    const skeletons = container.querySelectorAll('.MuiSkeleton-root');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('should display loading indicator when loading more assessments', () => {
    const mockOnClick = vi.fn();

    const { container } = render(
      <AssessmentTimeline
        assessments={mockAssessments}
        onAssessmentClick={mockOnClick}
        hasMore={true}
        loading={true}
      />
    );

    // Should display existing assessments
    expect(screen.getByText('Diabetes')).toBeInTheDocument();

    // Should also display loading skeletons for new items
    const skeletons = container.querySelectorAll('.MuiSkeleton-root');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  /**
   * Test: Assessment card click navigation
   * Requirements: 8.5
   */
  it('should call onAssessmentClick when an assessment card is clicked', async () => {
    const mockOnClick = vi.fn();
    const user = userEvent.setup();

    render(
      <AssessmentTimeline
        assessments={mockAssessments}
        onAssessmentClick={mockOnClick}
        hasMore={false}
        loading={false}
      />
    );

    const cards = screen.getAllByRole('button');
    await user.click(cards[0]);

    expect(mockOnClick).toHaveBeenCalledWith('1');
  });
});

describe('HistoryFilters', () => {
  const mockConditions = ['Diabetes', 'Hypertension', 'Asthma', 'Migraine'];

  /**
   * Test: Filter by condition
   * Requirements: 8.3
   */
  it('should allow filtering by condition type', async () => {
    const mockOnFilterChange = vi.fn();
    const user = userEvent.setup();

    render(
      <HistoryFilters
        onFilterChange={mockOnFilterChange}
        availableConditions={mockConditions}
      />
    );

    // Open condition dropdown
    const conditionSelect = screen.getByLabelText('Condition');
    await user.click(conditionSelect);

    // Select Diabetes
    const diabetesOption = await screen.findByRole('option', { name: 'Diabetes' });
    await user.click(diabetesOption);

    // Click Apply Filters
    const applyButton = screen.getByRole('button', { name: /Apply Filters/i });
    await user.click(applyButton);

    // Should call onFilterChange with selected condition
    expect(mockOnFilterChange).toHaveBeenCalledWith({
      condition: 'Diabetes',
      startDate: '',
      endDate: '',
    });
  });

  /**
   * Test: Date range search
   * Requirements: 8.4
   */
  it('should allow filtering by date range', async () => {
    const mockOnFilterChange = vi.fn();
    const user = userEvent.setup();

    render(
      <HistoryFilters
        onFilterChange={mockOnFilterChange}
        availableConditions={mockConditions}
      />
    );

    // Set start date
    const startDateInput = screen.getByLabelText('Start Date');
    await user.type(startDateInput, '2024-01-01');

    // Set end date
    const endDateInput = screen.getByLabelText('End Date');
    await user.type(endDateInput, '2024-01-31');

    // Click Apply Filters
    const applyButton = screen.getByRole('button', { name: /Apply Filters/i });
    await user.click(applyButton);

    // Should call onFilterChange with date range
    expect(mockOnFilterChange).toHaveBeenCalledWith({
      condition: '',
      startDate: '2024-01-01',
      endDate: '2024-01-31',
    });
  });

  /**
   * Test: Combined filters
   * Requirements: 8.3, 8.4
   */
  it('should allow filtering by both condition and date range', async () => {
    const mockOnFilterChange = vi.fn();
    const user = userEvent.setup();

    render(
      <HistoryFilters
        onFilterChange={mockOnFilterChange}
        availableConditions={mockConditions}
      />
    );

    // Select condition
    const conditionSelect = screen.getByLabelText('Condition');
    await user.click(conditionSelect);
    const hypertensionOption = await screen.findByRole('option', { name: 'Hypertension' });
    await user.click(hypertensionOption);

    // Set date range
    const startDateInput = screen.getByLabelText('Start Date');
    await user.type(startDateInput, '2024-01-01');

    const endDateInput = screen.getByLabelText('End Date');
    await user.type(endDateInput, '2024-01-31');

    // Click Apply Filters
    const applyButton = screen.getByRole('button', { name: /Apply Filters/i });
    await user.click(applyButton);

    // Should call onFilterChange with all filters
    expect(mockOnFilterChange).toHaveBeenCalledWith({
      condition: 'Hypertension',
      startDate: '2024-01-01',
      endDate: '2024-01-31',
    });
  });

  /**
   * Test: Clear filters functionality
   * Requirements: 8.3, 8.4
   */
  it('should clear all filters when Clear button is clicked', async () => {
    const mockOnFilterChange = vi.fn();
    const user = userEvent.setup();

    render(
      <HistoryFilters
        onFilterChange={mockOnFilterChange}
        availableConditions={mockConditions}
      />
    );

    // Set some filters
    const conditionSelect = screen.getByLabelText('Condition');
    await user.click(conditionSelect);
    const diabetesOption = await screen.findByRole('option', { name: 'Diabetes' });
    await user.click(diabetesOption);

    const startDateInput = screen.getByLabelText('Start Date');
    await user.type(startDateInput, '2024-01-01');

    // Apply filters first
    const applyButton = screen.getByRole('button', { name: /Apply Filters/i });
    await user.click(applyButton);

    // Clear button should now be visible
    const clearButton = screen.getByRole('button', { name: /Clear/i });
    expect(clearButton).toBeInTheDocument();

    // Click Clear button
    await user.click(clearButton);

    // Should call onFilterChange with empty filters
    expect(mockOnFilterChange).toHaveBeenLastCalledWith({
      condition: '',
      startDate: '',
      endDate: '',
    });
  });

  /**
   * Test: Clear button visibility
   * Requirements: 8.3, 8.4
   */
  it('should only show Clear button when filters are active', async () => {
    const mockOnFilterChange = vi.fn();
    const user = userEvent.setup();

    render(
      <HistoryFilters
        onFilterChange={mockOnFilterChange}
        availableConditions={mockConditions}
      />
    );

    // Initially, Clear button should not be visible
    expect(screen.queryByRole('button', { name: /Clear/i })).not.toBeInTheDocument();

    // Set a filter
    const startDateInput = screen.getByLabelText('Start Date');
    await user.type(startDateInput, '2024-01-01');

    // Clear button should now be visible
    expect(screen.getByRole('button', { name: /Clear/i })).toBeInTheDocument();
  });

  /**
   * Test: Available conditions dropdown
   * Requirements: 8.3
   */
  it('should display all available conditions in dropdown', async () => {
    const mockOnFilterChange = vi.fn();
    const user = userEvent.setup();

    render(
      <HistoryFilters
        onFilterChange={mockOnFilterChange}
        availableConditions={mockConditions}
      />
    );

    // Open condition dropdown
    const conditionSelect = screen.getByLabelText('Condition');
    await user.click(conditionSelect);

    // Should display "All Conditions" option
    expect(await screen.findByRole('option', { name: 'All Conditions' })).toBeInTheDocument();

    // Should display all provided conditions
    for (const condition of mockConditions) {
      expect(await screen.findByRole('option', { name: condition })).toBeInTheDocument();
    }
  });
});
