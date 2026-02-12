// ============================================================================
// Treatment Panels Property-Based Tests
// Feature: ai-health-frontend
// ============================================================================

import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import * as fc from 'fast-check';
import { AllopathyPanel } from './AllopathyPanel';
import { AyurvedaPanel } from './AyurvedaPanel';
import { HomeopathyPanel } from './HomeopathyPanel';
import { LifestylePanel } from './LifestylePanel';

/**
 * Property 13: Treatment information avoids outcome guarantees
 * Validates: Requirements 7.7
 * 
 * For any text displayed in treatment information sections, the content should not
 * contain words implying guaranteed outcomes such as "guaranteed", "will cure",
 * "definitely works", "100% effective".
 */
describe('Feature: ai-health-frontend, Property 13: Treatment information avoids outcome guarantees', () => {
  // Words and phrases that imply guaranteed outcomes
  const prohibitedPhrases = [
    'guaranteed',
    'will cure',
    'definitely works',
    '100% effective',
    'always works',
    'never fails',
    'certain cure',
    'guaranteed results',
    'guaranteed success',
    'will definitely',
    'absolutely cures',
    'completely eliminates',
    'permanent cure',
    'guaranteed to work',
    'guaranteed to cure',
    'will eliminate',
    'ensures cure',
    'promises cure',
    'guarantees recovery',
  ];

  // Generator for treatment details with various text content
  const treatmentDetailArbitrary = fc.record({
    category: fc.string({ minLength: 5, maxLength: 50 }),
    recommendations: fc.array(fc.string({ minLength: 10, maxLength: 200 }), { minLength: 1, maxLength: 5 }),
    notes: fc.string({ minLength: 10, maxLength: 200 }),
    approach: fc.option(fc.string({ minLength: 10, maxLength: 100 })),
    focus: fc.option(fc.string({ minLength: 10, maxLength: 100 })),
  });

  const treatmentsArrayArbitrary = fc.array(treatmentDetailArbitrary, { minLength: 1, maxLength: 3 });

  /**
   * Helper function to check if text contains prohibited phrases
   */
  const containsProhibitedPhrases = (text: string): { found: boolean; phrase?: string } => {
    const lowerText = text.toLowerCase();
    for (const phrase of prohibitedPhrases) {
      if (lowerText.includes(phrase.toLowerCase())) {
        return { found: true, phrase };
      }
    }
    return { found: false };
  };

  /**
   * Helper function to extract all text content from a rendered component
   */
  const extractTextContent = (container: HTMLElement): string => {
    return container.textContent || '';
  };

  it('should not display outcome guarantees in AllopathyPanel', () => {
    fc.assert(
      fc.property(treatmentsArrayArbitrary, (treatments) => {
        const { container } = render(<AllopathyPanel treatments={treatments} />);
        const textContent = extractTextContent(container);
        
        const result = containsProhibitedPhrases(textContent);
        
        // If prohibited phrases are found in the input data, that's expected
        // We're testing that the component doesn't ADD such phrases
        // So we check that any prohibited phrases in output came from input
        if (result.found) {
          // Check if the phrase exists in the input data
          const inputText = JSON.stringify(treatments).toLowerCase();
          const phraseInInput = inputText.includes(result.phrase!.toLowerCase());
          
          // If phrase is in output but not in input, the component added it (violation)
          expect(phraseInInput).toBe(true);
        }
      }),
      { numRuns: 100 }
    );
  });

  it('should not display outcome guarantees in AyurvedaPanel', () => {
    fc.assert(
      fc.property(treatmentsArrayArbitrary, (treatments) => {
        const { container } = render(<AyurvedaPanel treatments={treatments} />);
        const textContent = extractTextContent(container);
        
        const result = containsProhibitedPhrases(textContent);
        
        if (result.found) {
          const inputText = JSON.stringify(treatments).toLowerCase();
          const phraseInInput = inputText.includes(result.phrase!.toLowerCase());
          expect(phraseInInput).toBe(true);
        }
      }),
      { numRuns: 100 }
    );
  });

  it('should not display outcome guarantees in HomeopathyPanel', () => {
    fc.assert(
      fc.property(treatmentsArrayArbitrary, (treatments) => {
        const { container } = render(<HomeopathyPanel treatments={treatments} />);
        const textContent = extractTextContent(container);
        
        const result = containsProhibitedPhrases(textContent);
        
        if (result.found) {
          const inputText = JSON.stringify(treatments).toLowerCase();
          const phraseInInput = inputText.includes(result.phrase!.toLowerCase());
          expect(phraseInInput).toBe(true);
        }
      }),
      { numRuns: 100 }
    );
  });

  it('should not display outcome guarantees in LifestylePanel', () => {
    fc.assert(
      fc.property(treatmentsArrayArbitrary, (treatments) => {
        const { container } = render(<LifestylePanel treatments={treatments} />);
        const textContent = extractTextContent(container);
        
        const result = containsProhibitedPhrases(textContent);
        
        if (result.found) {
          const inputText = JSON.stringify(treatments).toLowerCase();
          const phraseInInput = inputText.includes(result.phrase!.toLowerCase());
          expect(phraseInInput).toBe(true);
        }
      }),
      { numRuns: 100 }
    );
  });

  it('should verify disclaimer text does not contain outcome guarantees', () => {
    // Test with empty treatments to focus on static disclaimer text
    const emptyTreatments: any[] = [];
    
    const panels = [
      { component: AllopathyPanel, name: 'AllopathyPanel' },
      { component: AyurvedaPanel, name: 'AyurvedaPanel' },
      { component: HomeopathyPanel, name: 'HomeopathyPanel' },
      { component: LifestylePanel, name: 'LifestylePanel' },
    ];

    panels.forEach(({ component: Panel, name }) => {
      const { container } = render(<Panel treatments={emptyTreatments} />);
      const textContent = extractTextContent(container);
      
      // Check that the disclaimer and static text don't contain prohibited phrases
      const result = containsProhibitedPhrases(textContent);
      
      expect(result.found).toBe(false);
    });
  });

  it('should handle treatments with mixed content without adding guarantees', () => {
    fc.assert(
      fc.property(
        fc.record({
          category: fc.constantFrom('Medication', 'Therapy', 'Lifestyle Changes', 'Supplements'),
          recommendations: fc.array(
            fc.oneof(
              fc.constant('Consult with a healthcare provider'),
              fc.constant('May help reduce symptoms'),
              fc.constant('Could provide relief'),
              fc.constant('Might improve condition'),
              fc.constant('Consider discussing with your doctor'),
            ),
            { minLength: 1, maxLength: 3 }
          ),
          notes: fc.constantFrom(
            'Individual results may vary',
            'Effectiveness depends on various factors',
            'Consult a professional for personalized advice',
            'This is general information only'
          ),
        }),
        (treatment) => {
          const treatments = [treatment];
          
          // Test all panels
          const panels = [
            { component: AllopathyPanel, name: 'AllopathyPanel' },
            { component: AyurvedaPanel, name: 'AyurvedaPanel' },
            { component: HomeopathyPanel, name: 'HomeopathyPanel' },
            { component: LifestylePanel, name: 'LifestylePanel' },
          ];

          panels.forEach(({ component: Panel }) => {
            const { container } = render(<Panel treatments={treatments} />);
            const textContent = extractTextContent(container);
            
            const result = containsProhibitedPhrases(textContent);
            
            // Should not find any prohibited phrases since input doesn't contain them
            expect(result.found).toBe(false);
          });
        }
      ),
      { numRuns: 100 }
    );
  });
});
