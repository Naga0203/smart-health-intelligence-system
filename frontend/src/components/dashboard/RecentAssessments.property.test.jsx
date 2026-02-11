// ============================================================================
// RecentAssessments Property-Based Tests
// ============================================================================

import { describe, it, expect, vi } from 'vitest';
import * as fc from 'fast-check';
import { render, screen } from '@testing-library/react';
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

describe('RecentAssessments - Property-Based Tests', () => {
  // ============================================================================
  // Property 3: Assessment cards display complete information
  // ============================================================================

  /**
   * Feature: ai-health-frontend
   * Property 3: Assessment cards display complete information
   * 
   * For any assessment displayed in a list or timeline, the rendered component 
   * should include assessment date, primary condition, risk level, and confidence level.
   * 
   * Validates: Requirements 3.2
   */
  describe('Property 3: Assessment cards display complete information', () => {
    it('should display all required fields for any valid assessment', async () => {
      await fc.assert(
        fc.asyncProperty(
          // Generate arbitrary assessments with all required fields
          fc.array(
            fc.record({
              id: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
              created_at: fc.integer({ min: new Date('2020-01-01').getTime(), max: new Date('2025-12-31').getTime() })
                .map(timestamp => new Date(timestamp).toISOString()),
              disease: fc.string({ minLength: 3, maxLength: 100 }).filter(s => s.trim().length >= 3),
              probability: fc.double({ min: 0, max: 1 }),
              confidence: fc.constantFrom('LOW', 'MEDIUM', 'HIGH'),
              symptoms: fc.array(fc.string({ minLength: 1, maxLength: 50 }), { minLength: 1, maxLength: 10 }),
              status: fc.constantFrom('completed', 'pending', 'processing'),
            }),
            { minLength: 1, maxLength: 5 }
          ),
          async (assessments) => {
            // Render the component with generated assessments
            const { container } = render(
              <BrowserRouter>
                <RecentAssessments assessments={assessments} loading={false} />
              </BrowserRouter>
            );

            // Verify each assessment displays all required information
            for (const assessment of assessments) {
              // 1. Check disease/condition is displayed (use container query to avoid normalization issues)
              const diseaseText = assessment.disease.trim();
              const diseaseElements = container.querySelectorAll(`span:not([class*="Chip"])`);
              const hasDiseaseText = Array.from(diseaseElements).some(el => 
                el.textContent === assessment.disease || el.textContent.trim() === diseaseText
              );
              expect(hasDiseaseText).toBe(true);

              // 2. Check confidence level is displayed
              const confidenceElements = screen.getAllByText(assessment.confidence);
              expect(confidenceElements.length).toBeGreaterThan(0);

              // 3. Check probability is displayed (as percentage)
              const probabilityPercent = Math.round(assessment.probability * 100);
              const probabilityElements = screen.getAllByText(`Probability: ${probabilityPercent}%`);
              expect(probabilityElements.length).toBeGreaterThan(0);

              // 4. Check date is displayed (format: MMM dd, yyyy HH:mm)
              // We verify the date exists by checking for the formatted date pattern
              const dateElements = screen.getAllByText((content, element) => {
                // Check if the element contains a date-like pattern
                return element?.textContent?.match(/[A-Z][a-z]{2} \d{2}, \d{4} \d{2}:\d{2}/) !== null;
              });
              expect(dateElements.length).toBeGreaterThan(0);
            }

            // Verify the number of list items matches the number of assessments
            const listItems = container.querySelectorAll('.MuiListItem-root');
            expect(listItems.length).toBe(assessments.length);
          }
        ),
        { numRuns: 100, timeout: 30000 }
      );
    }, 60000);

    it('should display complete information for assessments with edge case values', async () => {
      await fc.assert(
        fc.asyncProperty(
          // Generate assessments with edge case values
          fc.array(
            fc.record({
              id: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
              created_at: fc.constantFrom(
                new Date('2020-01-01T00:00:00Z').toISOString(), // Very old date
                new Date('2025-12-31T23:59:59Z').toISOString(), // Future date
                new Date().toISOString() // Current date
              ),
              disease: fc.constantFrom(
                'Flu', // Short name
                'Very Long Disease Name That Might Wrap To Multiple Lines In The UI',
                'Disease-With-Special-Characters!@#',
                'Disease123'
              ),
              probability: fc.constantFrom(
                0.0,   // Minimum probability
                0.01,  // Very low probability
                0.5,   // Medium probability
                0.99,  // Very high probability
                1.0    // Maximum probability
              ),
              confidence: fc.constantFrom('LOW', 'MEDIUM', 'HIGH'),
              symptoms: fc.array(fc.string({ minLength: 1, maxLength: 50 }), { minLength: 1, maxLength: 10 }),
              status: fc.constantFrom('completed', 'pending', 'processing'),
            }),
            { minLength: 1, maxLength: 3 }
          ),
          async (assessments) => {
            // Render the component
            const { container } = render(
              <BrowserRouter>
                <RecentAssessments assessments={assessments} loading={false} />
              </BrowserRouter>
            );

            // Verify all assessments display complete information
            for (const assessment of assessments) {
              // Disease name should be present (use container query to avoid normalization issues)
              const diseaseText = assessment.disease.trim();
              const diseaseElements = container.querySelectorAll(`span:not([class*="Chip"])`);
              const hasDiseaseText = Array.from(diseaseElements).some(el => 
                el.textContent === assessment.disease || el.textContent.trim() === diseaseText
              );
              expect(hasDiseaseText).toBe(true);

              // Confidence should be present
              const confidenceElements = screen.getAllByText(assessment.confidence);
              expect(confidenceElements.length).toBeGreaterThan(0);

              // Probability should be present and correctly formatted
              const probabilityPercent = Math.round(assessment.probability * 100);
              const probabilityElements = screen.getAllByText(`Probability: ${probabilityPercent}%`);
              expect(probabilityElements.length).toBeGreaterThan(0);

              // Date should be present
              const dateElements = screen.getAllByText((content, element) => {
                return element?.textContent?.match(/[A-Z][a-z]{2} \d{2}, \d{4} \d{2}:\d{2}/) !== null;
              });
              expect(dateElements.length).toBeGreaterThan(0);
            }

            // Verify the number of list items matches the number of assessments
            const listItems = container.querySelectorAll('.MuiListItem-root');
            expect(listItems.length).toBe(assessments.length);
          }
        ),
        { numRuns: 100, timeout: 30000 }
      );
    }, 60000);

    it('should display complete information for single assessment', async () => {
      await fc.assert(
        fc.asyncProperty(
          // Generate a single assessment
          fc.record({
            id: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
            created_at: fc.integer({ min: new Date('2020-01-01').getTime(), max: new Date('2025-12-31').getTime() })
              .map(timestamp => new Date(timestamp).toISOString()),
            disease: fc.string({ minLength: 3, maxLength: 100 }).filter(s => s.trim().length >= 3),
            probability: fc.double({ min: 0, max: 1 }),
            confidence: fc.constantFrom('LOW', 'MEDIUM', 'HIGH'),
            symptoms: fc.array(fc.string({ minLength: 1, maxLength: 50 }), { minLength: 1, maxLength: 10 }),
            status: fc.constantFrom('completed', 'pending', 'processing'),
          }),
          async (assessment) => {
            // Render with single assessment
            const { container } = render(
              <BrowserRouter>
                <RecentAssessments assessments={[assessment]} loading={false} />
              </BrowserRouter>
            );

            // Verify all four required fields are present:
            // 1. Date
            const dateElements = screen.getAllByText((content, element) => {
              return element?.textContent?.match(/[A-Z][a-z]{2} \d{2}, \d{4} \d{2}:\d{2}/) !== null;
            });
            expect(dateElements.length).toBeGreaterThan(0);

            // 2. Primary condition (disease) - use container query to avoid normalization issues
            const diseaseText = assessment.disease.trim();
            const diseaseElements = container.querySelectorAll(`span:not([class*="Chip"])`);
            const hasDiseaseText = Array.from(diseaseElements).some(el => 
              el.textContent === assessment.disease || el.textContent.trim() === diseaseText
            );
            expect(hasDiseaseText).toBe(true);

            // 3. Risk level (probability)
            const probabilityPercent = Math.round(assessment.probability * 100);
            const probabilityElements = screen.getAllByText(`Probability: ${probabilityPercent}%`);
            expect(probabilityElements.length).toBeGreaterThan(0);

            // 4. Confidence level
            const confidenceElements = screen.getAllByText(assessment.confidence);
            expect(confidenceElements.length).toBeGreaterThan(0);

            // Verify exactly one list item
            const listItems = container.querySelectorAll('.MuiListItem-root');
            expect(listItems.length).toBe(1);
          }
        ),
        { numRuns: 100, timeout: 30000 }
      );
    }, 60000);
  });
});
