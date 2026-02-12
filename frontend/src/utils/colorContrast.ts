// ============================================================================
// Color Contrast Validation Utilities
// ============================================================================

/**
 * Convert hex color to RGB
 */
const hexToRgb = (hex: string): { r: number; g: number; b: number } | null => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
};

/**
 * Calculate relative luminance of a color
 * https://www.w3.org/TR/WCAG20/#relativeluminancedef
 */
const getLuminance = (r: number, g: number, b: number): number => {
  const [rs, gs, bs] = [r, g, b].map((c) => {
    const sRGB = c / 255;
    return sRGB <= 0.03928 ? sRGB / 12.92 : Math.pow((sRGB + 0.055) / 1.055, 2.4);
  });

  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
};

/**
 * Calculate contrast ratio between two colors
 * https://www.w3.org/TR/WCAG20/#contrast-ratiodef
 */
export const getContrastRatio = (color1: string, color2: string): number => {
  const rgb1 = hexToRgb(color1);
  const rgb2 = hexToRgb(color2);

  if (!rgb1 || !rgb2) {
    throw new Error('Invalid color format. Use hex colors (e.g., #FFFFFF)');
  }

  const lum1 = getLuminance(rgb1.r, rgb1.g, rgb1.b);
  const lum2 = getLuminance(rgb2.r, rgb2.g, rgb2.b);

  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);

  return (lighter + 0.05) / (darker + 0.05);
};

/**
 * Check if contrast ratio meets WCAG AA standards
 * @param foreground - Foreground color (hex)
 * @param background - Background color (hex)
 * @param isLargeText - True for text 18pt+ or 14pt+ bold
 * @returns Object with pass/fail and ratio
 */
export const checkContrastCompliance = (
  foreground: string,
  background: string,
  isLargeText: boolean = false
): { passes: boolean; ratio: number; required: number; level: string } => {
  const ratio = getContrastRatio(foreground, background);
  const requiredRatio = isLargeText ? 3.0 : 4.5;
  const passes = ratio >= requiredRatio;

  return {
    passes,
    ratio: Math.round(ratio * 100) / 100,
    required: requiredRatio,
    level: passes ? 'AA' : 'Fail',
  };
};

/**
 * Validate theme colors for WCAG compliance
 */
export const validateThemeColors = () => {
  const results: Array<{
    name: string;
    foreground: string;
    background: string;
    result: ReturnType<typeof checkContrastCompliance>;
  }> = [];

  // Define color combinations to test
  const tests = [
    {
      name: 'Primary text on white',
      foreground: '#1F2937',
      background: '#FFFFFF',
      isLargeText: false,
    },
    {
      name: 'Secondary text on white',
      foreground: '#6B7280',
      background: '#FFFFFF',
      isLargeText: false,
    },
    {
      name: 'Primary button text',
      foreground: '#FFFFFF',
      background: '#4A90E2',
      isLargeText: false,
    },
    {
      name: 'Success text on white',
      foreground: '#059669',
      background: '#FFFFFF',
      isLargeText: false,
    },
    {
      name: 'Warning text on white',
      foreground: '#D97706',
      background: '#FFFFFF',
      isLargeText: false,
    },
    {
      name: 'Error text on white',
      foreground: '#DC2626',
      background: '#FFFFFF',
      isLargeText: false,
    },
    {
      name: 'Text on light background',
      foreground: '#1F2937',
      background: '#F9FAFB',
      isLargeText: false,
    },
  ];

  tests.forEach((test) => {
    results.push({
      name: test.name,
      foreground: test.foreground,
      background: test.background,
      result: checkContrastCompliance(test.foreground, test.background, test.isLargeText),
    });
  });

  return results;
};

/**
 * Format contrast ratio for display
 */
export const formatContrastRatio = (ratio: number): string => {
  return `${ratio.toFixed(2)}:1`;
};

/**
 * Get WCAG level for contrast ratio
 */
export const getWCAGLevel = (ratio: number, isLargeText: boolean = false): string => {
  if (isLargeText) {
    if (ratio >= 4.5) return 'AAA';
    if (ratio >= 3.0) return 'AA';
    return 'Fail';
  } else {
    if (ratio >= 7.0) return 'AAA';
    if (ratio >= 4.5) return 'AA';
    return 'Fail';
  }
};

/**
 * Suggest accessible color alternatives
 */
export const suggestAccessibleColor = (
  foreground: string,
  background: string,
  targetRatio: number = 4.5
): string | null => {
  // This is a simplified version - in production, you'd want a more sophisticated algorithm
  const rgb = hexToRgb(foreground);
  if (!rgb) return null;

  // Try darkening or lightening the foreground color
  const bgLum = getLuminance(
    ...Object.values(hexToRgb(background) || { r: 255, g: 255, b: 255 })
  );

  // If background is light, darken foreground; if dark, lighten foreground
  const adjustment = bgLum > 0.5 ? -10 : 10;

  let newR = Math.max(0, Math.min(255, rgb.r + adjustment));
  let newG = Math.max(0, Math.min(255, rgb.g + adjustment));
  let newB = Math.max(0, Math.min(255, rgb.b + adjustment));

  const newHex = `#${newR.toString(16).padStart(2, '0')}${newG
    .toString(16)
    .padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;

  const newRatio = getContrastRatio(newHex, background);

  return newRatio >= targetRatio ? newHex : null;
};

// Run validation and log results (for development)
if (process.env.NODE_ENV === 'development') {
  const results = validateThemeColors();
  console.group('🎨 Color Contrast Validation');
  results.forEach((test) => {
    const icon = test.result.passes ? '✅' : '❌';
    console.log(
      `${icon} ${test.name}: ${formatContrastRatio(test.result.ratio)} (${
        test.result.level
      }) - Required: ${test.result.required}:1`
    );
  });
  console.groupEnd();
}
