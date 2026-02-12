// ============================================================================
// Keyboard Navigation Utilities
// ============================================================================

/**
 * Keyboard shortcuts configuration
 */
export const KEYBOARD_SHORTCUTS = {
  // Navigation shortcuts
  DASHBOARD: { key: 'd', ctrlKey: true, altKey: false, description: 'Go to Dashboard' },
  NEW_ASSESSMENT: { key: 'n', ctrlKey: true, altKey: false, description: 'New Assessment' },
  HISTORY: { key: 'h', ctrlKey: true, altKey: false, description: 'View History' },
  PROFILE: { key: 'p', ctrlKey: true, altKey: false, description: 'View Profile' },
  
  // Action shortcuts
  SUBMIT: { key: 'Enter', ctrlKey: true, altKey: false, description: 'Submit Form' },
  CANCEL: { key: 'Escape', ctrlKey: false, altKey: false, description: 'Cancel/Close' },
  SEARCH: { key: 'k', ctrlKey: true, altKey: false, description: 'Search' },
} as const;

/**
 * Check if a keyboard event matches a shortcut
 */
export const matchesShortcut = (
  event: KeyboardEvent,
  shortcut: { key: string; ctrlKey: boolean; altKey: boolean }
): boolean => {
  const key = event.key.toLowerCase();
  const shortcutKey = shortcut.key.toLowerCase();
  
  return (
    key === shortcutKey &&
    event.ctrlKey === shortcut.ctrlKey &&
    event.altKey === shortcut.altKey
  );
};

/**
 * Format shortcut for display
 */
export const formatShortcut = (shortcut: {
  key: string;
  ctrlKey: boolean;
  altKey: boolean;
}): string => {
  const parts: string[] = [];
  
  if (shortcut.ctrlKey) parts.push('Ctrl');
  if (shortcut.altKey) parts.push('Alt');
  parts.push(shortcut.key);
  
  return parts.join('+');
};

/**
 * Get all focusable elements within a container
 */
export const getFocusableElements = (container: HTMLElement): HTMLElement[] => {
  const selector = [
    'a[href]',
    'button:not([disabled])',
    'textarea:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
  ].join(', ');
  
  return Array.from(container.querySelectorAll(selector));
};

/**
 * Trap focus within a container (useful for modals)
 */
export const trapFocus = (container: HTMLElement, event: KeyboardEvent) => {
  if (event.key !== 'Tab') return;
  
  const focusableElements = getFocusableElements(container);
  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];
  
  if (event.shiftKey) {
    // Shift + Tab
    if (document.activeElement === firstElement) {
      event.preventDefault();
      lastElement?.focus();
    }
  } else {
    // Tab
    if (document.activeElement === lastElement) {
      event.preventDefault();
      firstElement?.focus();
    }
  }
};

/**
 * Handle arrow key navigation in a list
 */
export const handleArrowNavigation = (
  event: KeyboardEvent,
  currentIndex: number,
  totalItems: number,
  onNavigate: (newIndex: number) => void
) => {
  if (!['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.key)) {
    return;
  }
  
  event.preventDefault();
  
  let newIndex = currentIndex;
  
  if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
    newIndex = currentIndex > 0 ? currentIndex - 1 : totalItems - 1;
  } else if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
    newIndex = currentIndex < totalItems - 1 ? currentIndex + 1 : 0;
  }
  
  onNavigate(newIndex);
};

/**
 * Ensure element is visible in viewport (for keyboard navigation)
 */
export const scrollIntoViewIfNeeded = (element: HTMLElement) => {
  const rect = element.getBoundingClientRect();
  const isVisible =
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <= window.innerHeight &&
    rect.right <= window.innerWidth;
  
  if (!isVisible) {
    element.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
      inline: 'nearest',
    });
  }
};
