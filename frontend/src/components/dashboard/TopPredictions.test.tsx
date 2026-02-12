// ============================================================================
// Top Predictions Unit Tests
// ============================================================================

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TopPredictions from './TopPredictions';

describe('TopPredictions Component', () => {
  const mockPredictions = [
    { disease: 'Diabetes', probability: 0.85, rank: 1 },
    { disease: 'Hypertension', probability: 0.72, rank: 2 },
    { disease: 'Asthma', probability: 0.45, rank: 3 },
  ];

  describe('Display Tests', () => {
    it('should display all required fields for predictions', () => {
      const mockFetch = vi.fn();

      render(
        <TopPredictions
          predictions={mockPredictions}
          loading={false}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      // Verify disease names are displayed
      expect(screen.getByText(/Diabetes/i)).toBeInTheDocument();
      expect(screen.getByText(/Hypertension/i)).toBeInTheDocument();
      expect(screen.getByText(/Asthma/i)).toBeInTheDocument();

      // Verify probabilities are displayed as percentages
      expect(screen.getByText('85%')).toBeInTheDocument();
      expect(screen.getByText('72%')).toBeInTheDocument();
      expect(screen.getByText('45%')).toBeInTheDocument();

      // Verify confidence levels are displayed
      expect(screen.getByText('HIGH')).toBeInTheDocument();
      expect(screen.getByText('MEDIUM')).toBeInTheDocument();
      expect(screen.getByText('LOW')).toBeInTheDocument();

      // Verify ranks are displayed
      expect(screen.getByText(/1\./)).toBeInTheDocument();
      expect(screen.getByText(/2\./)).toBeInTheDocument();
      expect(screen.getByText(/3\./)).toBeInTheDocument();
    });

    it('should display loading skeleton when loading', () => {
      const mockFetch = vi.fn();

      render(
        <TopPredictions
          predictions={null}
          loading={true}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      expect(screen.getByText('Top Predictions')).toBeInTheDocument();
      // LoadingSkeleton should be rendered
    });

    it('should display empty state when no predictions', () => {
      const mockFetch = vi.fn();

      render(
        <TopPredictions
          predictions={[]}
          loading={false}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      expect(screen.getByText('No predictions available')).toBeInTheDocument();
      expect(
        screen.getByText(/Enter symptoms and demographic information/i)
      ).toBeInTheDocument();
    });

    it('should display error message when error exists', () => {
      const mockFetch = vi.fn();
      const errorMessage = 'Failed to fetch predictions';

      render(
        <TopPredictions
          predictions={null}
          loading={false}
          error={errorMessage}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });

    it('should display correct confidence level for HIGH probability', () => {
      const mockFetch = vi.fn();
      const highProbPredictions = [
        { disease: 'Diabetes', probability: 0.85, rank: 1 },
      ];

      render(
        <TopPredictions
          predictions={highProbPredictions}
          loading={false}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      expect(screen.getByText('HIGH')).toBeInTheDocument();
    });

    it('should display correct confidence level for MEDIUM probability', () => {
      const mockFetch = vi.fn();
      const mediumProbPredictions = [
        { disease: 'Hypertension', probability: 0.65, rank: 1 },
      ];

      render(
        <TopPredictions
          predictions={mediumProbPredictions}
          loading={false}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      expect(screen.getByText('MEDIUM')).toBeInTheDocument();
    });

    it('should display correct confidence level for LOW probability', () => {
      const mockFetch = vi.fn();
      const lowProbPredictions = [
        { disease: 'Asthma', probability: 0.35, rank: 1 },
      ];

      render(
        <TopPredictions
          predictions={lowProbPredictions}
          loading={false}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      expect(screen.getByText('LOW')).toBeInTheDocument();
    });

    it('should display count message with correct number', () => {
      const mockFetch = vi.fn();

      render(
        <TopPredictions
          predictions={mockPredictions}
          loading={false}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      expect(screen.getByText(/Showing top 3 predictions/i)).toBeInTheDocument();
    });
  });

  describe('Interaction Tests', () => {
    it('should call onFetchPredictions when Fetch button is clicked', () => {
      const mockFetch = vi.fn();

      render(
        <TopPredictions
          predictions={mockPredictions}
          loading={false}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      const fetchButton = screen.getByRole('button', { name: /fetch/i });
      fireEvent.click(fetchButton);

      expect(mockFetch).toHaveBeenCalledWith(5);
    });

    it('should update N value and call onFetchPredictions with new value', () => {
      const mockFetch = vi.fn();

      render(
        <TopPredictions
          predictions={mockPredictions}
          loading={false}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      const input = screen.getByLabelText('N');
      const fetchButton = screen.getByRole('button', { name: /fetch/i });

      // Change N value to 10
      fireEvent.change(input, { target: { value: '10' } });
      fireEvent.click(fetchButton);

      expect(mockFetch).toHaveBeenCalledWith(10);
    });

    it('should not call onFetchPredictions with invalid N value (0)', () => {
      const mockFetch = vi.fn();

      render(
        <TopPredictions
          predictions={mockPredictions}
          loading={false}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      const input = screen.getByLabelText('N');
      const fetchButton = screen.getByRole('button', { name: /fetch/i });

      // Try to set N to 0 (invalid)
      fireEvent.change(input, { target: { value: '0' } });
      fireEvent.click(fetchButton);

      expect(mockFetch).not.toHaveBeenCalled();
    });

    it('should not call onFetchPredictions with N value > 50', () => {
      const mockFetch = vi.fn();

      render(
        <TopPredictions
          predictions={mockPredictions}
          loading={false}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      const input = screen.getByLabelText('N');
      const fetchButton = screen.getByRole('button', { name: /fetch/i });

      // Try to set N to 51 (invalid)
      fireEvent.change(input, { target: { value: '51' } });
      fireEvent.click(fetchButton);

      expect(mockFetch).not.toHaveBeenCalled();
    });

    it('should show loading skeleton when loading', () => {
      const mockFetch = vi.fn();

      const { container } = render(
        <TopPredictions
          predictions={null}
          loading={true}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      // When loading, the component shows LoadingSkeleton instead of the fetch button
      expect(screen.getByText('Top Predictions')).toBeInTheDocument();
      // Verify LoadingSkeleton is rendered (it has a skeleton class)
      const skeleton = container.querySelector('.MuiSkeleton-root');
      expect(skeleton).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle single prediction', () => {
      const mockFetch = vi.fn();
      const singlePrediction = [
        { disease: 'Diabetes', probability: 0.85, rank: 1 },
      ];

      render(
        <TopPredictions
          predictions={singlePrediction}
          loading={false}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      expect(screen.getByText(/Diabetes/i)).toBeInTheDocument();
      expect(screen.getByText('85%')).toBeInTheDocument();
      expect(screen.getByText('HIGH')).toBeInTheDocument();
    });

    it('should handle probability at boundary (0.75 = HIGH)', () => {
      const mockFetch = vi.fn();
      const boundaryPrediction = [
        { disease: 'Diabetes', probability: 0.75, rank: 1 },
      ];

      render(
        <TopPredictions
          predictions={boundaryPrediction}
          loading={false}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      expect(screen.getByText('HIGH')).toBeInTheDocument();
    });

    it('should handle probability at boundary (0.55 = MEDIUM)', () => {
      const mockFetch = vi.fn();
      const boundaryPrediction = [
        { disease: 'Hypertension', probability: 0.55, rank: 1 },
      ];

      render(
        <TopPredictions
          predictions={boundaryPrediction}
          loading={false}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      expect(screen.getByText('MEDIUM')).toBeInTheDocument();
    });

    it('should handle probability at boundary (0.54 = LOW)', () => {
      const mockFetch = vi.fn();
      const boundaryPrediction = [
        { disease: 'Asthma', probability: 0.54, rank: 1 },
      ];

      render(
        <TopPredictions
          predictions={boundaryPrediction}
          loading={false}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      expect(screen.getByText('LOW')).toBeInTheDocument();
    });

    it('should handle maximum predictions (10)', () => {
      const mockFetch = vi.fn();
      const maxPredictions = Array.from({ length: 10 }, (_, i) => ({
        disease: `Disease ${i + 1}`,
        probability: 0.9 - i * 0.05,
        rank: i + 1,
      }));

      render(
        <TopPredictions
          predictions={maxPredictions}
          loading={false}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={10}
        />
      );

      expect(screen.getByText(/Showing top 10 predictions/i)).toBeInTheDocument();
    });

    it('should round probability percentages correctly', () => {
      const mockFetch = vi.fn();
      const predictions = [
        { disease: 'Disease1', probability: 0.856, rank: 1 }, // Should round to 86%
        { disease: 'Disease2', probability: 0.854, rank: 2 }, // Should round to 85%
      ];

      render(
        <TopPredictions
          predictions={predictions}
          loading={false}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      expect(screen.getByText('86%')).toBeInTheDocument();
      expect(screen.getByText('85%')).toBeInTheDocument();
    });
  });
});
