// ============================================================================
// Focus Trap Component - For Modal Accessibility
// ============================================================================

import { useEffect, useRef, ReactNode } from 'react';
import { trapFocus, getFocusableElements } from '@/utils/keyboardNavigation';

interface FocusTrapProps {
  children: ReactNode;
  active?: boolean;
}

/**
 * Component that traps focus within its children
 * Useful for modals and dialogs to ensure keyboard navigation stays within
 */
export const FocusTrap: React.FC<FocusTrapProps> = ({ children, active = true }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!active || !containerRef.current) return;

    const container = containerRef.current;

    // Focus first focusable element when trap activates
    const focusableElements = getFocusableElements(container);
    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      trapFocus(container, event);
    };

    container.addEventListener('keydown', handleKeyDown);

    return () => {
      container.removeEventListener('keydown', handleKeyDown);
    };
  }, [active]);

  return (
    <div ref={containerRef} style={{ outline: 'none' }} tabIndex={-1}>
      {children}
    </div>
  );
};
