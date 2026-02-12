// ============================================================================
// Top Predictions Property-Based Tests
// Feature: ai-health-frontend
// ============================================================================

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import * as fc from 'fast-check';
import TopPredictions from './TopPredictions';

/**
 * Property 23: Prediction results display complete information
 * Validates: Requirements 15.2
 * 
 * For any prediction result, the displayed component should include:
 * - Disease name
 * - Probability percentage
 * - Confidence level (HIGH/MEDIUM/LOW)
 * - Rank number
 */
describe('Feature: ai-health-frontend, Property 23: Prediction results display complete information', () => {
  // Generator for prediction data
  const predictionArbitrary = fc.record({
    disease: fc.constantFrom(
      'Diabetes',
      'Hypertension',
      'Asthma',
      'Migraine',
      'Arthritis',
      'Bronchitis',
      'Pneumonia',
      'Gastritis'
    ),
    probability: fc.float({ min: 0, max: 1, noNaN: true }),
    rank: fc.integer({ min: 1, max: 50 }),
  });

  const predictionsArrayArbitrary = fc.array(predictionArbitrary, { minLength: 1, maxLength: 10 });

  /**
   * Helper to get expected confidence level based on probability
   */
  const getExpectedConfidence = (probability: number): string => {
    if (probability >= 0.75) return 'HIGH';
    if (probability >= 0.55) return 'MEDIUM';
    return 'LOW';
  };

  it('should display all required fields for each prediction', () => {
    fc.assert(
      fc.property(predictionsArrayArbitrary, (predictions) => {
        const mockFetch = () => {};

        const { container } = render(
          <TopPredictions
            predictions={predictions}
            loading={false}
            error={null}
            onFetchPredictions={mockFetch}
            defaultN={5}
          />
        );

        // Verify each prediction displays complete information
        predictions.forEach((prediction) => {
          // Check disease name is displayed
          expect(container.textContent).toContain(prediction.disease);

          // Check rank is displayed
          expect(container.textContent).toContain(`${prediction.rank}.`);

          // Check probability percentage is displayed
          const probabilityPercent = Math.round(prediction.probability * 100);
          expect(container.textContent).toContain(`${probabilityPercent}%`);

          // Check confidence level is displayed
          const expectedConfidence = getExpectedConfidence(prediction.probability);
          expect(container.textContent).toContain(expectedConfidence);
        });
      }),
      { numRuns: 100 }
    );
  }, 15000); // 15 second timeout

  it('should display correct confidence level for any probability value', () => {
    fc.assert(
      fc.property(
        fc.float({ min: 0, max: 1, noNaN: true }),
        fc.constantFrom('Diabetes', 'Hypertension', 'Asthma'),
        fc.integer({ min: 1, max: 10 }),
        (probability, disease, rank) => {
          const prediction = { disease, probability, rank };
          const mockFetch = () => {};

          const { container } = render(
            <TopPredictions
              predictions={[prediction]}
              loading={false}
              error={null}
              onFetchPredictions={mockFetch}
              defaultN={5}
            />
          );

          // Verify confidence level matches probability threshold
          const expectedConfidence = getExpectedConfidence(probability);
          expect(container.textContent).toContain(expectedConfidence);

          // Verify the confidence level is one of the valid values
          const hasValidConfidence =
            container.textContent?.includes('HIGH') ||
            container.textContent?.includes('MEDIUM') ||
            container.textContent?.includes('LOW');
          expect(hasValidConfidence).toBe(true);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should display probability as percentage between 0-100', () => {
    fc.assert(
      fc.property(predictionsArrayArbitrary, (predictions) => {
        const mockFetch = () => {};

        const { container } = render(
          <TopPredictions
            predictions={predictions}
            loading={false}
            error={null}
            onFetchPredictions={mockFetch}
            defaultN={5}
          />
        );

        // Verify all probabilities are displayed as percentages
        predictions.forEach((prediction) => {
          const probabilityPercent = Math.round(prediction.probability * 100);
          
          // Probability should be between 0 and 100
          expect(probabilityPercent).toBeGreaterThanOrEqual(0);
          expect(probabilityPercent).toBeLessThanOrEqual(100);

          // Probability should be displayed in the component
          expect(container.textContent).toContain(`${probabilityPercent}%`);
        });
      }),
      { numRuns: 100 }
    );
  }, 10000); // 10 second timeout

  it('should display rank numbers in order', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            disease: fc.constantFrom('Diabetes', 'Hypertension', 'Asthma', 'Migraine'),
            probability: fc.float({ min: 0, max: 1, noNaN: true }),
            rank: fc.integer({ min: 1, max: 10 }),
          }),
          { minLength: 2, maxLength: 10 }
        ),
        (predictions) => {
          const mockFetch = () => {};

          const { container } = render(
            <TopPredictions
              predictions={predictions}
              loading={false}
              error={null}
              onFetchPredictions={mockFetch}
              defaultN={5}
            />
          );

          // Verify each rank is displayed
          predictions.forEach((prediction) => {
            expect(container.textContent).toContain(`${prediction.rank}.`);
          });
        }
      ),
      { numRuns: 50 } // Reduced from 100 for performance
    );
  }, 10000); // 10 second timeout

  it('should handle edge case with single prediction', () => {
    fc.assert(
      fc.property(predictionArbitrary, (prediction) => {
        const mockFetch = () => {};

        const { container } = render(
          <TopPredictions
            predictions={[prediction]}
            loading={false}
            error={null}
            onFetchPredictions={mockFetch}
            defaultN={5}
          />
        );

        // Verify all fields are present for single prediction
        expect(container.textContent).toContain(prediction.disease);
        expect(container.textContent).toContain(`${prediction.rank}.`);
        expect(container.textContent).toContain(`${Math.round(prediction.probability * 100)}%`);
        
        const expectedConfidence = getExpectedConfidence(prediction.probability);
        expect(container.textContent).toContain(expectedConfidence);
      }),
      { numRuns: 100 }
    );
  });

  it('should display confidence thresholds correctly at boundaries', () => {
    // Test boundary values for confidence levels
    const boundaryTests = [
      { probability: 0.75, expectedConfidence: 'HIGH' },
      { probability: 0.76, expectedConfidence: 'HIGH' },
      { probability: 0.74, expectedConfidence: 'MEDIUM' },
      { probability: 0.55, expectedConfidence: 'MEDIUM' },
      { probability: 0.56, expectedConfidence: 'MEDIUM' },
      { probability: 0.54, expectedConfidence: 'LOW' },
      { probability: 0.0, expectedConfidence: 'LOW' },
      { probability: 1.0, expectedConfidence: 'HIGH' },
    ];

    boundaryTests.forEach(({ probability, expectedConfidence }) => {
      const prediction = {
        disease: 'Test Disease',
        probability,
        rank: 1,
      };
      const mockFetch = () => {};

      const { container } = render(
        <TopPredictions
          predictions={[prediction]}
          loading={false}
          error={null}
          onFetchPredictions={mockFetch}
          defaultN={5}
        />
      );

      expect(container.textContent).toContain(expectedConfidence);
    });
  });

  it('should handle predictions with very high and very low probabilities', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(0.0, 0.01, 0.99, 1.0),
        fc.constantFrom('Diabetes', 'Hypertension'),
        fc.integer({ min: 1, max: 5 }),
        (probability, disease, rank) => {
          const prediction = { disease, probability, rank };
          const mockFetch = () => {};

          const { container } = render(
            <TopPredictions
              predictions={[prediction]}
              loading={false}
              error={null}
              onFetchPredictions={mockFetch}
              defaultN={5}
            />
          );

          // Verify extreme probabilities are handled correctly
          const probabilityPercent = Math.round(probability * 100);
          expect(container.textContent).toContain(`${probabilityPercent}%`);

          const expectedConfidence = getExpectedConfidence(probability);
          expect(container.textContent).toContain(expectedConfidence);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should display all predictions when array has maximum length', () => {
    fc.assert(
      fc.property(
        fc.array(predictionArbitrary, { minLength: 10, maxLength: 10 }),
        (predictions) => {
          const mockFetch = () => {};

          const { container } = render(
            <TopPredictions
              predictions={predictions}
              loading={false}
              error={null}
              onFetchPredictions={mockFetch}
              defaultN={10}
            />
          );

          // Verify all 10 predictions are displayed
          predictions.forEach((prediction) => {
            expect(container.textContent).toContain(prediction.disease);
          });

          // Verify count message
          expect(container.textContent).toContain('Showing top 10 predictions');
        }
      ),
      { numRuns: 50 } // Reduced from 100 for performance
    );
  }, 10000); // 10 second timeout
});
