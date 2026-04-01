// ============================================================================
// BurgerMenu - Animated hamburger toggle for sidebar
// ============================================================================

import React from 'react';
import './BurgerMenu.css';

interface BurgerMenuProps {
  open: boolean;
  onClick: () => void;
  'aria-label'?: string;
}

export const BurgerMenu: React.FC<BurgerMenuProps> = ({
  open,
  onClick,
  'aria-label': ariaLabel = 'Toggle navigation menu',
}) => {
  return (
    <button
      className="burger-btn"
      onClick={onClick}
      aria-label={ariaLabel}
      aria-expanded={open}
    >
      <span className={`burger-line burger-line--1 ${open ? 'open' : ''}`} />
      <span className={`burger-line burger-line--2 ${open ? 'open' : ''}`} />
      <span className={`burger-line burger-line--3 ${open ? 'open' : ''}`} />
    </button>
  );
};
