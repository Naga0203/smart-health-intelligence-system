// ============================================================================
// Confidence Warning Unit Tests
// Tests for confidence warning display
// ============================================================================
// Requirements: 11.2

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ConfidenceWarning } from './ConfidenceWarning';

describe('ConfidenceWarning Component', () => {
  /**
   * Test: Confidence warning display
   * Requirements: 11.2
   */
  describe('Warning Display', () => {
    it('should display warning when confidence level is LOW', () => {
      render(<ConfidenceWarning confidence="LOW" />);

      // Should display warning title
      expect(screen.getByText(/Low Confidence Assessment/i)).toBeInTheDocument();

      // Should display warning message about limited reliability
      expect(screen.getByText(/limited reliability/i)).toBeInTheDocument();
    });

    it('should not display warning when confidence level is MEDIUM', () => {
      const { container } = render(<ConfidenceWarning confidence="MEDIUM" />);

      // Should not render anything
      expect(container.firstChild).toBeNull();
    });

    it('should not display warning when confidence level is HIGH', () => {
      const { container } = render(<ConfidenceWarning confidence="HIGH" />);

      // Should not render anything
      expect(container.firstChild).toBeNull();
    });

    it('should display confidence score when provided', () => {
      render(<ConfidenceWarning confidence="LOW" confidenceScore={45} />);

      // Should display confidence score in title
      expect(screen.getByText(/Low Confidence Assessment \(45%\)/i)).toBeInTheDocument();
    });

    it('should display warning without score when score is not provided', () => {
      render(<ConfidenceWarning confidence="LOW" />);

      // Should display title without score
      expect(screen.getByText(/Low Confidence Assessment/i)).toBeInTheDocument();
      
      // Should not display percentage
      expect(screen.queryByText(/\(\d+%\)/)).not.toBeInTheDocument();
    });
  });

  /**
   * Test: Warning content
   * Requirements: 11.2
   */
  describe('Warning Content', () => {
    it('should display warning about limited reliability', () => {
      render(<ConfidenceWarning confidence="LOW" />);

      // Should display reliability warning
      expect(screen.getByText(/limited reliability due to insufficient or ambiguous information/i)).toBeInTheDocument();
    });

    it('should display caution message', () => {
      render(<ConfidenceWarning confidence="LOW" />);

      // Should display caution message
      expect(screen.getByText(/should be interpreted with caution/i)).toBeInTheDocument();
    });

    it('should display recommendations header', () => {
      render(<ConfidenceWarning confidence="LOW" />);

      // Should display recommendations header
      expect(screen.getByText(/We strongly recommend:/i)).toBeInTheDocument();
    });

    it('should display recommendation to consult healthcare professional', () => {
      render(<ConfidenceWarning confidence="LOW" />);

      // Should recommend consulting healthcare professional
      expect(screen.getByText(/Consulting with a qualified healthcare professional/i)).toBeInTheDocument();
    });

    it('should display recommendation to provide more information', () => {
      render(<ConfidenceWarning confidence="LOW" />);

      // Should recommend providing more information
      expect(screen.getByText(/Providing more detailed symptom information/i)).toBeInTheDocument();
    });

    it('should display recommendation to upload medical reports', () => {
      render(<ConfidenceWarning confidence="LOW" />);

      // Should recommend uploading reports
      expect(screen.getByText(/Uploading relevant medical reports or test results/i)).toBeInTheDocument();
    });

    it('should display warning about not making health decisions', () => {
      render(<ConfidenceWarning confidence="LOW" />);

      // Should warn about health decisions
      expect(screen.getByText(/Not making health decisions based solely on this assessment/i)).toBeInTheDocument();
    });
  });

  /**
   * Test: Alert styling and prominence
   * Requirements: 11.2
   */
  describe('Alert Styling', () => {
    it('should display warning severity alert', () => {
      const { container } = render(<ConfidenceWarning confidence="LOW" />);

      // Should have warning severity class
      const alert = container.querySelector('.MuiAlert-standardWarning');
      expect(alert).toBeInTheDocument();
    });

    it('should display prominent border for emphasis', () => {
      const { container } = render(<ConfidenceWarning confidence="LOW" />);

      // Should have alert element
      const alert = container.querySelector('.MuiAlert-root');
      expect(alert).toBeInTheDocument();
    });

    it('should display warning icon', () => {
      render(<ConfidenceWarning confidence="LOW" />);

      // Should have warning icon (MUI Alert with warning severity includes icon)
      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
    });
  });

  /**
   * Test: Different confidence scores
   * Requirements: 11.2
   */
  describe('Confidence Score Display', () => {
    it('should display very low confidence score', () => {
      render(<ConfidenceWarning confidence="LOW" confidenceScore={20} />);

      // Should display score
      expect(screen.getByText(/Low Confidence Assessment \(20%\)/i)).toBeInTheDocument();
    });

    it('should display confidence score at threshold', () => {
      render(<ConfidenceWarning confidence="LOW" confidenceScore={54} />);

      // Should display score
      expect(screen.getByText(/Low Confidence Assessment \(54%\)/i)).toBeInTheDocument();
    });

    it('should display confidence score of 0', () => {
      render(<ConfidenceWarning confidence="LOW" confidenceScore={0} />);

      // Should display score
      expect(screen.getByText(/Low Confidence Assessment \(0%\)/i)).toBeInTheDocument();
    });
  });

  /**
   * Test: Component visibility based on confidence
   * Requirements: 11.2
   */
  describe('Conditional Rendering', () => {
    it('should only render for LOW confidence', () => {
      const { container: lowContainer } = render(<ConfidenceWarning confidence="LOW" />);
      const { container: mediumContainer } = render(<ConfidenceWarning confidence="MEDIUM" />);
      const { container: highContainer } = render(<ConfidenceWarning confidence="HIGH" />);

      // Only LOW should render
      expect(lowContainer.firstChild).not.toBeNull();
      expect(mediumContainer.firstChild).toBeNull();
      expect(highContainer.firstChild).toBeNull();
    });

    it('should render complete warning content for LOW confidence', () => {
      render(<ConfidenceWarning confidence="LOW" confidenceScore={45} />);

      // Should have all key elements
      expect(screen.getByText(/Low Confidence Assessment/i)).toBeInTheDocument();
      expect(screen.getByText(/limited reliability/i)).toBeInTheDocument();
      expect(screen.getByText(/We strongly recommend:/i)).toBeInTheDocument();
      expect(screen.getByText(/Consulting with a qualified healthcare professional/i)).toBeInTheDocument();
    });
  });
});
