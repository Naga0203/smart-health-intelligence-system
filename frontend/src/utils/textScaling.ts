// ============================================================================
// Text Scaling Utilities
// ============================================================================

/**
 * Check if browser zoom level is at or above 200%
 */
export const getZoomLevel = (): number => {
  // Calculate zoom based on device pixel ratio and window dimensions
  const devicePixelRatio = window.devicePixelRatio || 1;
  const zoom = Math.round((devicePixelRatio / 1) * 100);
  return zoom;
};

/**
 * Check if text scaling is enabled (200% or more)
 */
export const isTextScaled = (): boolean => {
  return getZoomLevel() >= 200;
};

/**
 * Detect if content is overflowing horizontally
 */
export const hasHorizontalOverflow = (element: HTMLElement): boolean => {
  return element.scrollWidth > element.clientWidth;
};

/**
 * Detect if content is cut off vertically
 */
export const hasVerticalOverflow = (element: HTMLElement): boolean => {
  return element.scrollHeight > element.clientHeight;
};

/**
 * Check if element is fully visible in viewport
 */
export const isElementFullyVisible = (element: HTMLElement): boolean => {
  const rect = element.getBoundingClientRect();
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  );
};

/**
 * Validate text scaling compliance for an element
 */
export const validateTextScaling = (element: HTMLElement): {
  passes: boolean;
  issues: string[];
} => {
  const issues: string[] = [];

  // Check for horizontal overflow
  if (hasHorizontalOverflow(element)) {
    issues.push('Content has horizontal overflow (horizontal scrolling required)');
  }

  // Check if interactive elements are accessible
  const interactiveElements = element.querySelectorAll(
    'button, a, input, select, textarea'
  );

  interactiveElements.forEach((el) => {
    const htmlEl = el as HTMLElement;
    if (!isElementFullyVisible(htmlEl)) {
      issues.push(`Interactive element "${htmlEl.tagName}" is not fully visible`);
    }
  });

  // Check for text truncation
  const textElements = element.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6');
  textElements.forEach((el) => {
    const htmlEl = el as HTMLElement;
    const style = window.getComputedStyle(htmlEl);
    
    if (style.overflow === 'hidden' && style.textOverflow === 'ellipsis') {
      if (htmlEl.scrollWidth > htmlEl.clientWidth) {
        issues.push(`Text is truncated in ${htmlEl.tagName}`);
      }
    }
  });

  return {
    passes: issues.length === 0,
    issues,
  };
};

/**
 * Test text scaling at different zoom levels
 */
export const testTextScalingLevels = async (
  element: HTMLElement,
  levels: number[] = [100, 150, 200]
): Promise<Map<number, ReturnType<typeof validateTextScaling>>> => {
  const results = new Map();

  for (const level of levels) {
    // Note: Programmatically changing zoom is not possible in browsers
    // This function documents the expected behavior
    // Manual testing is required
    console.log(`Test at ${level}% zoom level manually`);
    const result = validateTextScaling(element);
    results.set(level, result);
  }

  return results;
};

/**
 * Get recommended font size adjustments for better scaling
 */
export const getRecommendedFontSizes = () => {
  return {
    base: '16px', // Never go below 16px for body text
    small: '0.875rem', // 14px - minimum for secondary text
    body: '1rem', // 16px - standard body text
    large: '1.125rem', // 18px - large text
    h6: '1.25rem', // 20px
    h5: '1.5rem', // 24px
    h4: '1.875rem', // 30px
    h3: '2.25rem', // 36px
    h2: '3rem', // 48px
    h1: '3.75rem', // 60px
  };
};

/**
 * Check if element uses relative units (rem, em, %)
 */
export const usesRelativeUnits = (element: HTMLElement): boolean => {
  const style = window.getComputedStyle(element);
  const fontSize = style.fontSize;
  
  // Check if computed font size is relative to root
  // This is a simplified check - in practice, we'd inspect the CSS
  return !fontSize.includes('px') || fontSize === '16px'; // 16px is often the root
};

/**
 * Recommendations for text scaling compliance
 */
export const TEXT_SCALING_GUIDELINES = {
  useSizes: [
    'Use relative units (rem, em) for font sizes',
    'Set base font size to 16px on html element',
    'Use rem for consistent scaling across components',
  ],
  avoidSizes: [
    'Avoid fixed pixel values for font sizes',
    'Avoid viewport units (vw, vh) for text',
    'Avoid absolute positioning that breaks at zoom',
  ],
  layout: [
    'Use flexbox or grid for responsive layouts',
    'Avoid fixed widths on text containers',
    'Allow content to reflow at different zoom levels',
    'Ensure no horizontal scrolling at 200% zoom',
  ],
  testing: [
    'Test at 100%, 150%, and 200% zoom',
    'Verify all content is readable',
    'Check that no functionality is lost',
    'Ensure interactive elements remain accessible',
  ],
} as const;

/**
 * Log text scaling test results
 */
export const logTextScalingResults = (
  componentName: string,
  result: ReturnType<typeof validateTextScaling>
) => {
  console.group(`📏 Text Scaling Test: ${componentName}`);
  console.log(`Status: ${result.passes ? '✅ Pass' : '❌ Fail'}`);
  
  if (result.issues.length > 0) {
    console.log('Issues found:');
    result.issues.forEach((issue, index) => {
      console.log(`  ${index + 1}. ${issue}`);
    });
  } else {
    console.log('No issues found - component scales properly');
  }
  
  console.groupEnd();
};
