// ============================================================================
// Property Test: Color Contrast
// Feature: ai-health-frontend, Property 18: Text contrast meets accessibility standards
// Validates: Requirements 12.8
// ============================================================================

import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import { checkContrastCompliance, getContrastRatio } from '@/utils/colorContrast';

// Arbitraries for generating valid hex colors
const hexColorArbitrary = fc
  .tuple(fc.integer({ min: 0, max: 255 }), fc.integer({ min: 0, max: 255 }), fc.integer({ min: 0, max: 255 }))
  .map(([r, g, b]) => {
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  });

describe('Property 18: Text contrast meets accessibility standards', () => {
  it('should calculate contrast ratios correctly (always between 1:1 and 21:1)', () => {
    fc.assert(
      fc.property(hexColorArbitrary, hexColorArbitrary, (color1, color2) => {
        const ratio = getContrastRatio(color1, color2);

        // Property: Contrast ratio must be between 1 and 21
        expect(ratio).toBeGreaterThanOrEqual(1);
        expect(ratio).toBeLessThanOrEqual(21);

        // Property: Contrast ratio must be a positive number
        expect(ratio).toBeGreaterThan(0);
        expect(Number.isFinite(ratio)).toBe(true);
      }),
      { numRuns: 100 }
    );
  });

  it('should have symmetric contrast ratios', () => {
    fc.assert(
      fc.property(hexColorArbitrary, hexColorArbitrary, (color1, color2) => {
        const ratio1 = getContrastRatio(color1, color2);
        const ratio2 = getContrastRatio(color2, color1);

        // Property: Contrast ratio should be the same regardless of order
        expect(Math.abs(ratio1 - ratio2)).toBeLessThan(0.01);
      }),
      { numRuns: 100 }
    );
  });

  it('should have maximum contrast between black and white', () => {
    const blackWhiteRatio = getContrastRatio('#000000', '#FFFFFF');

    // Property: Black and white should have 21:1 contrast (maximum)
    expect(blackWhiteRatio).toBeCloseTo(21, 1);
  });

  it('should have minimum contrast (1:1) for identical colors', () => {
    fc.assert(
      fc.property(hexColorArbitrary, (color) => {
        const ratio = getContrastRatio(color, color);

        // Property: Identical colors should have 1:1 contrast (minimum)
        expect(ratio).toBeCloseTo(1, 1);
      }),
      { numRuns: 100 }
    );
  });

  it('should correctly identify WCAG AA compliance for normal text', () => {
    // Test with known compliant colors
    const compliantPairs = [
      { fg: '#1F2937', bg: '#FFFFFF', expected: true }, // 11.5:1
      { fg: '#6B7280', bg: '#FFFFFF', expected: true }, // 4.6:1
      { fg: '#059669', bg: '#FFFFFF', expected: true }, // 4.5:1
    ];

    compliantPairs.forEach(({ fg, bg, expected }) => {
      const result = checkContrastCompliance(fg, bg, false);

      // Property: Known compliant colors should pass
      expect(result.passes).toBe(expected);
      expect(result.ratio).toBeGreaterThanOrEqual(4.5);
      expect(result.level).toBe('AA');
    });
  });

  it('should correctly identify WCAG AA compliance for large text', () => {
    fc.assert(
      fc.property(hexColorArbitrary, hexColorArbitrary, (fg, bg) => {
        const result = checkContrastCompliance(fg, bg, true);

        // Property: Large text requires 3:1 ratio
        expect(result.required).toBe(3.0);

        // Property: Pass/fail should match ratio vs requirement
        if (result.ratio >= 3.0) {
          expect(result.passes).toBe(true);
        } else {
          expect(result.passes).toBe(false);
        }
      }),
      { numRuns: 100 }
    );
  });

  it('should verify theme colors meet WCAG AA standards', () => {
    // Theme colors that must meet standards
    const themeColors = [
      { name: 'Primary text on white', fg: '#1F2937', bg: '#FFFFFF', isLarge: false },
      { name: 'Secondary text on white', fg: '#6B7280', bg: '#FFFFFF', isLarge: false },
      { name: 'Success dark on white', fg: '#059669', bg: '#FFFFFF', isLarge: false },
      { name: 'Warning dark on white', fg: '#D97706', bg: '#FFFFFF', isLarge: false },
      { name: 'Error dark on white', fg: '#DC2626', bg: '#FFFFFF', isLarge: false },
      { name: 'Primary text on light bg', fg: '#1F2937', bg: '#F9FAFB', isLarge: false },
    ];

    themeColors.forEach(({ name, fg, bg, isLarge }) => {
      const result = checkContrastCompliance(fg, bg, isLarge);

      // Property: All theme colors must pass WCAG AA
      expect(result.passes).toBe(true);
      expect(result.level).toBe('AA');
      expect(result.ratio).toBeGreaterThanOrEqual(isLarge ? 3.0 : 4.5);
    });
  });

  it('should have consistent compliance results', () => {
    fc.assert(
      fc.property(hexColorArbitrary, hexColorArbitrary, fc.boolean(), (fg, bg, isLarge) => {
        const result1 = checkContrastCompliance(fg, bg, isLarge);
        const result2 = checkContrastCompliance(fg, bg, isLarge);

        // Property: Multiple checks should return same result
        expect(result1.passes).toBe(result2.passes);
        expect(result1.ratio).toBeCloseTo(result2.ratio, 2);
        expect(result1.level).toBe(result2.level);
      }),
      { numRuns: 100 }
    );
  });

  it('should have higher requirements for normal text than large text', () => {
    fc.assert(
      fc.property(hexColorArbitrary, hexColorArbitrary, (fg, bg) => {
        const normalText = checkContrastCompliance(fg, bg, false);
        const largeText = checkContrastCompliance(fg, bg, true);

        // Property: Normal text requirement (4.5) > Large text requirement (3.0)
        expect(normalText.required).toBeGreaterThan(largeText.required);
        expect(normalText.required).toBe(4.5);
        expect(largeText.required).toBe(3.0);

        // Property: If normal text passes, large text must also pass
        if (normalText.passes) {
          expect(largeText.passes).toBe(true);
        }
      }),
      { numRuns: 100 }
    );
  });
});
