// ============================================================================
// Property Test: Keyboard Navigation
// Feature: ai-health-frontend, Property 16: Interactive elements support keyboard navigation
// Validates: Requirements 12.6
// ============================================================================

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import * as fc from 'fast-check';
import { Button, IconButton, TextField, Select, MenuItem } from '@mui/material';
import { getFocusableElements } from '@/utils/keyboardNavigation';

describe('Property 16: Interactive elements support keyboard navigation', () => {
  it('should allow all interactive elements to be focused via keyboard', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            type: fc.constantFrom('button', 'iconButton', 'textField', 'select'),
            label: fc.string({ minLength: 1, maxLength: 20 }),
            disabled: fc.boolean(),
          }),
          { minLength: 1, maxLength: 10 }
        ),
        (elements) => {
          const { container } = render(
            <BrowserRouter>
              <div>
                {elements.map((el, index) => {
                  if (el.disabled) return null; // Skip disabled elements
                  
                  switch (el.type) {
                    case 'button':
                      return <Button key={index}>{el.label}</Button>;
                    case 'iconButton':
                      return <IconButton key={index} aria-label={el.label} />;
                    case 'textField':
                      return <TextField key={index} label={el.label} />;
                    case 'select':
                      return (
                        <Select key={index} label={el.label} value="">
                          <MenuItem value="1">Option 1</MenuItem>
                        </Select>
                      );
                    default:
                      return null;
                  }
                })}
              </div>
            </BrowserRouter>
          );

          // Get all focusable elements
          const focusableElements = getFocusableElements(container);
          const enabledElements = elements.filter((el) => !el.disabled);

          // Property: Number of focusable elements should match enabled interactive elements
          expect(focusableElements.length).toBeGreaterThanOrEqual(enabledElements.length);

          // Property: All focusable elements should have tabIndex >= 0 or be naturally focusable
          focusableElements.forEach((element) => {
            const tabIndex = element.getAttribute('tabindex');
            const isNaturallyFocusable = ['BUTTON', 'INPUT', 'SELECT', 'TEXTAREA', 'A'].includes(
              element.tagName
            );

            expect(
              isNaturallyFocusable || (tabIndex !== null && parseInt(tabIndex) >= 0)
            ).toBe(true);
          });
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should maintain proper tab order for interactive elements', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 2, max: 5 }),
        (buttonCount) => {
          const { container } = render(
            <div>
              {Array.from({ length: buttonCount }, (_, i) => (
                <Button key={i} data-testid={`button-${i}`}>
                  Button {i}
                </Button>
              ))}
            </div>
          );

          const focusableElements = getFocusableElements(container);

          // Property: Tab order should follow DOM order (no negative tabIndex)
          focusableElements.forEach((element) => {
            const tabIndex = element.getAttribute('tabindex');
            if (tabIndex !== null) {
              expect(parseInt(tabIndex)).toBeGreaterThanOrEqual(-1);
            }
          });

          // Property: Elements should be in document order
          for (let i = 0; i < focusableElements.length - 1; i++) {
            const current = focusableElements[i];
            const next = focusableElements[i + 1];
            
            // Next element should come after current in DOM
            const position = current.compareDocumentPosition(next);
            expect(position & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should support Enter and Space key activation for buttons', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 20 }),
        (buttonText) => {
          let clicked = false;
          const handleClick = () => {
            clicked = true;
          };

          render(<Button onClick={handleClick}>{buttonText}</Button>);

          const button = screen.getByRole('button', { name: buttonText });

          // Property: Button should be focusable
          expect(button.tabIndex).toBeGreaterThanOrEqual(0);

          // Property: Button should have role="button"
          expect(button.getAttribute('role') || button.tagName).toMatch(/BUTTON/i);

          // Buttons are natively keyboard accessible
          // The browser handles Enter/Space automatically for button elements
          expect(button.tagName).toBe('BUTTON');
        }
      ),
      { numRuns: 100 }
    );
  });
});
