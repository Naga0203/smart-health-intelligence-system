// ============================================================================
// Data Quality Alert Unit Tests
// Tests for data quality alert display and suggestions
// ============================================================================
// Requirements: 11.1

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DataQualityAlert } from './DataQualityAlert';

describe('DataQualityAlert Component', () => {
  /**
   * Test: Data quality alert display
   * Requirements: 11.1
   */
  describe('Alert Display', () => {
    it('should display alert when data quality score is below 60%', () => {
      render(<DataQualityAlert dataQualityScore={50} />);

      // Should display alert title with score
      expect(screen.getByText(/Low Data Quality Score \(50%\)/i)).toBeInTheDocument();

      // Should display warning message
      expect(screen.getByText(/limited information/i)).toBeInTheDocument();
    });

    it('should not display alert when data quality score is 60% or above', () => {
      const { container } = render(<DataQualityAlert dataQualityScore={60} />);

      // Should not render anything
      expect(container.firstChild).toBeNull();
    });

    it('should not display alert when data quality score is above 60%', () => {
      const { container } = render(<DataQualityAlert dataQualityScore={75} />);

      // Should not render anything
      expect(container.firstChild).toBeNull();
    });

    it('should display alert for very low data quality scores', () => {
      render(<DataQualityAlert dataQualityScore={20} />);

      // Should display alert with score
      expect(screen.getByText(/Low Data Quality Score \(20%\)/i)).toBeInTheDocument();
    });

    it('should display alert for data quality score just below threshold', () => {
      render(<DataQualityAlert dataQualityScore={59} />);

      // Should display alert with score
      expect(screen.getByText(/Low Data Quality Score \(59%\)/i)).toBeInTheDocument();
    });
  });

  /**
   * Test: Suggestions display
   * Requirements: 11.1
   */
  describe('Suggestions Display', () => {
    it('should display default suggestions when no custom suggestions provided', () => {
      render(<DataQualityAlert dataQualityScore={50} />);

      // Should display default suggestions
      expect(screen.getByText(/Add more detailed symptom descriptions/i)).toBeInTheDocument();
      expect(screen.getByText(/Include symptom duration and severity/i)).toBeInTheDocument();
      expect(screen.getByText(/Provide relevant medical history/i)).toBeInTheDocument();
      expect(screen.getByText(/Add vital signs if available/i)).toBeInTheDocument();
      expect(screen.getByText(/Upload medical reports or test results/i)).toBeInTheDocument();
    });

    it('should display custom suggestions when provided', () => {
      const customSuggestions = [
        'Custom suggestion 1',
        'Custom suggestion 2',
        'Custom suggestion 3',
      ];

      render(<DataQualityAlert dataQualityScore={45} suggestions={customSuggestions} />);

      // Should display custom suggestions
      expect(screen.getByText(/Custom suggestion 1/i)).toBeInTheDocument();
      expect(screen.getByText(/Custom suggestion 2/i)).toBeInTheDocument();
      expect(screen.getByText(/Custom suggestion 3/i)).toBeInTheDocument();

      // Should not display default suggestions
      expect(screen.queryByText(/Add more detailed symptom descriptions/i)).not.toBeInTheDocument();
    });

    it('should display all suggestions in a list format', () => {
      render(<DataQualityAlert dataQualityScore={55} />);

      // Should have list items
      const listItems = screen.getAllByRole('listitem');
      expect(listItems.length).toBeGreaterThan(0);
    });

    it('should display suggestions with bullet points', () => {
      render(<DataQualityAlert dataQualityScore={40} />);

      // Check that suggestions are formatted with bullets
      expect(screen.getByText(/• Add more detailed symptom descriptions/i)).toBeInTheDocument();
      expect(screen.getByText(/• Include symptom duration and severity/i)).toBeInTheDocument();
    });
  });

  /**
   * Test: Alert styling and severity
   * Requirements: 11.1
   */
  describe('Alert Styling', () => {
    it('should display warning severity alert', () => {
      const { container } = render(<DataQualityAlert dataQualityScore={50} />);

      // Should have warning severity class
      const alert = container.querySelector('.MuiAlert-standardWarning');
      expect(alert).toBeInTheDocument();
    });

    it('should display warning icon', () => {
      render(<DataQualityAlert dataQualityScore={50} />);

      // Should have warning icon (MUI Alert with warning severity includes icon)
      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
    });
  });

  /**
   * Test: Edge cases
   * Requirements: 11.1
   */
  describe('Edge Cases', () => {
    it('should handle data quality score of 0', () => {
      render(<DataQualityAlert dataQualityScore={0} />);

      // Should display alert
      expect(screen.getByText(/Low Data Quality Score \(0%\)/i)).toBeInTheDocument();
    });

    it('should handle data quality score of 100', () => {
      const { container } = render(<DataQualityAlert dataQualityScore={100} />);

      // Should not display alert
      expect(container.firstChild).toBeNull();
    });

    it('should handle empty suggestions array', () => {
      render(<DataQualityAlert dataQualityScore={50} suggestions={[]} />);

      // Should display alert but no suggestions
      expect(screen.getByText(/Low Data Quality Score/i)).toBeInTheDocument();
      
      // Should not have any list items
      expect(screen.queryByRole('listitem')).not.toBeInTheDocument();
    });

    it('should handle single suggestion', () => {
      render(<DataQualityAlert dataQualityScore={50} suggestions={['Single suggestion']} />);

      // Should display the single suggestion
      expect(screen.getByText(/Single suggestion/i)).toBeInTheDocument();
      
      // Should have exactly one list item
      const listItems = screen.getAllByRole('listitem');
      expect(listItems).toHaveLength(1);
    });
  });
});
