// ============================================================================
// Keyboard Shortcuts Hook
// ============================================================================

import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { matchesShortcut, KEYBOARD_SHORTCUTS } from '@/utils/keyboardNavigation';

/**
 * Hook to enable global keyboard shortcuts
 */
export const useKeyboardShortcuts = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in input fields
      const target = event.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return;
      }

      // Navigation shortcuts
      if (matchesShortcut(event, KEYBOARD_SHORTCUTS.DASHBOARD)) {
        event.preventDefault();
        navigate('/app/dashboard');
      } else if (matchesShortcut(event, KEYBOARD_SHORTCUTS.NEW_ASSESSMENT)) {
        event.preventDefault();
        navigate('/app/assessment/new');
      } else if (matchesShortcut(event, KEYBOARD_SHORTCUTS.HISTORY)) {
        event.preventDefault();
        navigate('/app/history');
      } else if (matchesShortcut(event, KEYBOARD_SHORTCUTS.PROFILE)) {
        event.preventDefault();
        navigate('/app/profile');
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [navigate]);
};

/**
 * Hook for custom keyboard shortcuts in specific components
 */
export const useCustomShortcut = (
  shortcut: { key: string; ctrlKey: boolean; altKey: boolean },
  callback: () => void,
  enabled: boolean = true
) => {
  useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in input fields
      const target = event.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return;
      }

      if (matchesShortcut(event, shortcut)) {
        event.preventDefault();
        callback();
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [shortcut, callback, enabled]);
};
