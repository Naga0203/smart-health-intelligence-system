// ============================================================================
// Property Test: ARIA Labels
// Feature: ai-health-frontend, Property 17: Interactive elements have ARIA labels
// Validates: Requirements 12.7
// ============================================================================

import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import * as fc from 'fast-check';
import { IconButton, Button } from '@mui/material';
import { Delete, Edit, Add } from '@mui/icons-material';
import { hasAccessibleName } from '@/utils/accessibility';

describe('Property 17: Interactive elements have ARIA labels', () => {
  it('should have accessible names for icon buttons without visible text', () => {
    fc.assert(
      fc.property(
        fc.record({
          label: fc.string({ minLength: 1, maxLength: 30 }),
          icon: fc.constantFrom('delete', 'edit', 'add'),
        }),
        ({ label, icon }) => {
          const IconComponent = icon === 'delete' ? Delete : icon === 'edit' ? Edit : Add;

          const { container } = render(
            <IconButton aria-label={label}>
              <IconComponent />
            </IconButton>
          );

          const button = container.querySelector('button');
          expect(button).toBeTruthy();

          // Property: Icon button must have accessible name
          if (button) {
            expect(hasAccessibleName(button)).toBe(true);

            // Property: Must have aria-label attribute
            const ariaLabel = button.getAttribute('aria-label');
            expect(ariaLabel).toBeTruthy();
            expect(ariaLabel).toBe(label);
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should have accessible names for all interactive elements', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            type: fc.constantFrom('iconButton', 'buttonWithText', 'link'),
            label: fc.string({ minLength: 1, maxLength: 20 }),
          }),
          { minLength: 1, maxLength: 5 }
        ),
        (elements) => {
          const { container } = render(
            <div>
              {elements.map((el, index) => {
                switch (el.type) {
                  case 'iconButton':
                    return (
                      <IconButton key={index} aria-label={el.label}>
                        <Delete />
                      </IconButton>
                    );
                  case 'buttonWithText':
                    return <Button key={index}>{el.label}</Button>;
                  case 'link':
                    return (
                      <a key={index} href="#" aria-label={el.label}>
                        Link
                      </a>
                    );
                  default:
                    return null;
                }
              })}
            </div>
          );

          // Get all interactive elements
          const interactiveElements = container.querySelectorAll('button, a, [role="button"]');

          // Property: All interactive elements must have accessible names
          interactiveElements.forEach((element) => {
            expect(hasAccessibleName(element as HTMLElement)).toBe(true);
          });
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should use aria-labelledby when referencing another element', () => {
    fc.assert(
      fc.property(
        fc.record({
          id: fc.string({ minLength: 5, maxLength: 15 }).map((s) => `label-${s}`),
          labelText: fc.string({ minLength: 1, maxLength: 30 }),
        }),
        ({ id, labelText }) => {
          const { container } = render(
            <div>
              <span id={id}>{labelText}</span>
              <IconButton aria-labelledby={id}>
                <Delete />
              </IconButton>
            </div>
          );

          const button = container.querySelector('button');
          expect(button).toBeTruthy();

          if (button) {
            // Property: Button must have aria-labelledby attribute
            const ariaLabelledBy = button.getAttribute('aria-labelledby');
            expect(ariaLabelledBy).toBe(id);

            // Property: Referenced element must exist
            const labelElement = container.querySelector(`#${id}`);
            expect(labelElement).toBeTruthy();
            expect(labelElement?.textContent).toBe(labelText);
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should have proper role attributes for custom interactive elements', () => {
    fc.assert(
      fc.property(
        fc.record({
          role: fc.constantFrom('button', 'link', 'tab'),
          label: fc.string({ minLength: 1, maxLength: 20 }),
        }),
        ({ role, label }) => {
          const { container } = render(
            <div role={role} aria-label={label} tabIndex={0}>
              Custom Element
            </div>
          );

          const element = container.firstChild as HTMLElement;

          // Property: Custom interactive element must have role
          expect(element.getAttribute('role')).toBe(role);

          // Property: Custom interactive element must have accessible name
          expect(hasAccessibleName(element)).toBe(true);

          // Property: Custom interactive element must be keyboard accessible
          expect(element.tabIndex).toBeGreaterThanOrEqual(0);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should not have empty aria-label attributes', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 30 }),
        (label) => {
          const { container } = render(
            <IconButton aria-label={label}>
              <Delete />
            </IconButton>
          );

          const button = container.querySelector('button');
          const ariaLabel = button?.getAttribute('aria-label');

          // Property: aria-label must not be empty
          if (ariaLabel !== null) {
            expect(ariaLabel.trim().length).toBeGreaterThan(0);
          }
        }
      ),
      { numRuns: 100 }
    );
  });
});
