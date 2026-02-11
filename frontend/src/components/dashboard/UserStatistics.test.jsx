import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import UserStatistics from './UserStatistics';

describe('UserStatistics', () => {
  const mockStatistics = {
    total_assessments: 15,
    assessments_by_confidence: {
      HIGH: 8,
      MEDIUM: 5,
      LOW: 2,
    },
    most_common_diseases: [
      { disease: 'Diabetes', count: 5 },
      { disease: 'Hypertension', count: 3 },
      { disease: 'Asthma', count: 2 },
    ],
    last_assessment_date: '2024-01-15T10:30:00Z',
    account_age_days: 45,
  };

  it('should display loading skeleton when loading', () => {
    render(<UserStatistics statistics={null} loading={true} />);
    expect(screen.getByText('Your Statistics')).toBeInTheDocument();
  });

  it('should display info message when no statistics available', () => {
    render(<UserStatistics statistics={null} loading={false} />);
    expect(screen.getByText('No statistics available yet')).toBeInTheDocument();
  });

  it('should display total assessments', () => {
    render(<UserStatistics statistics={mockStatistics} loading={false} />);
    expect(screen.getByText('15')).toBeInTheDocument();
    expect(screen.getByText('Total Assessments')).toBeInTheDocument();
  });

  it('should display assessments by confidence', () => {
    render(<UserStatistics statistics={mockStatistics} loading={false} />);
    
    expect(screen.getByText('Assessments by Confidence')).toBeInTheDocument();
    expect(screen.getByText('High Confidence')).toBeInTheDocument();
    expect(screen.getByText('8')).toBeInTheDocument();
    expect(screen.getByText('Medium Confidence')).toBeInTheDocument();
    // Use getAllByText for duplicate values (5 appears in both Medium Confidence and Diabetes count)
    const fiveElements = screen.getAllByText('5');
    expect(fiveElements.length).toBeGreaterThan(0);
    expect(screen.getByText('Low Confidence')).toBeInTheDocument();
    // Use getAllByText for duplicate values (2 appears in both Low Confidence and Asthma count)
    const twoElements = screen.getAllByText('2');
    expect(twoElements.length).toBeGreaterThan(0);
  });

  it('should display most common diseases', () => {
    render(<UserStatistics statistics={mockStatistics} loading={false} />);
    
    expect(screen.getByText('Most Common Conditions')).toBeInTheDocument();
    expect(screen.getByText('Diabetes')).toBeInTheDocument();
    expect(screen.getByText('Hypertension')).toBeInTheDocument();
    expect(screen.getByText('Asthma')).toBeInTheDocument();
  });

  it('should display last assessment date', () => {
    render(<UserStatistics statistics={mockStatistics} loading={false} />);
    
    expect(screen.getByText('Last Assessment')).toBeInTheDocument();
    expect(screen.getByText('Jan 15, 2024')).toBeInTheDocument();
  });

  it('should display account age', () => {
    render(<UserStatistics statistics={mockStatistics} loading={false} />);
    
    expect(screen.getByText('Member for')).toBeInTheDocument();
    expect(screen.getByText('45 days')).toBeInTheDocument();
  });

  it('should handle missing optional fields gracefully', () => {
    const minimalStats = {
      total_assessments: 5,
    };

    render(<UserStatistics statistics={minimalStats} loading={false} />);
    
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('Total Assessments')).toBeInTheDocument();
  });
});
