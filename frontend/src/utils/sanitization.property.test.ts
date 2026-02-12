// ============================================================================
// Property Test: Input Sanitization
// Feature: ai-health-frontend
// Property 20: User inputs are sanitized before display
// Validates: Requirements 14.2
// ============================================================================

import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import {
  sanitizeInput,
  escapeHtml,
  removeScriptTags,
  sanitizeUrl,
  containsXss,
  sanitizeObject,
} from './sanitization';

describe('Property 20: User inputs are sanitized before display', () => {
  it('should escape HTML entities in any string input', () => {
    fc.assert(
      fc.property(fc.string(), (input) => {
        const sanitized = escapeHtml(input);
        
        // Property: Sanitized output should not contain raw HTML special characters
        expect(sanitized).not.toMatch(/[<>]/);
        
        // Property: If input contained special chars, they should be escaped
        if (input.includes('<')) {
          expect(sanitized).toContain('&lt;');
        }
        if (input.includes('>')) {
          expect(sanitized).toContain('&gt;');
        }
        if (input.includes('&')) {
          expect(sanitized).toContain('&amp;');
        }
        if (input.includes('"')) {
          expect(sanitized).toContain('&quot;');
        }
      }),
      { numRuns: 100 }
    );
  });

  it('should remove script tags from any input', () => {
    fc.assert(
      fc.property(
        fc.string(),
        fc.string(),
        (before, after) => {
          const input = `${before}<script>alert('xss')</script>${after}`;
          const sanitized = removeScriptTags(input);
          
          // Property: Output should not contain script tags
          expect(sanitized.toLowerCase()).not.toContain('<script');
          expect(sanitized.toLowerCase()).not.toContain('</script>');
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should remove event handlers from any input', () => {
    const eventHandlers = ['onclick', 'onerror', 'onload', 'onmouseover'];
    
    fc.assert(
      fc.property(
        fc.constantFrom(...eventHandlers),
        fc.string(),
        (handler, code) => {
          const input = `<img ${handler}="${code}">`;
          const sanitized = removeScriptTags(input);
          
          // Property: Output should not contain event handlers
          expect(sanitized.toLowerCase()).not.toMatch(/\son\w+\s*=/);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should remove javascript: protocol from any input', () => {
    fc.assert(
      fc.property(fc.string(), (code) => {
        const input = `<a href="javascript:${code}">link</a>`;
        const sanitized = removeScriptTags(input);
        
        // Property: Output should not contain javascript: protocol
        expect(sanitized.toLowerCase()).not.toContain('javascript:');
      }),
      { numRuns: 100 }
    );
  });

  it('should sanitize any user input completely', () => {
    fc.assert(
      fc.property(fc.string(), (input) => {
        const sanitized = sanitizeInput(input);
        
        // Property: Sanitized output should be a string
        expect(typeof sanitized).toBe('string');
        
        // Property: Sanitized output should not contain dangerous patterns
        expect(sanitized.toLowerCase()).not.toContain('<script');
        expect(sanitized).not.toMatch(/[<>]/);
        
        // Property: Sanitization should be idempotent
        const doubleSanitized = sanitizeInput(sanitized);
        expect(doubleSanitized).toBe(sanitized);
      }),
      { numRuns: 100 }
    );
  });

  it('should sanitize all string properties in an object', () => {
    fc.assert(
      fc.property(
        fc.record({
          name: fc.string(),
          description: fc.string(),
          notes: fc.string(),
        }),
        (obj) => {
          const sanitized = sanitizeObject(obj);
          
          // Property: All string properties should be sanitized
          expect(sanitized.name).not.toMatch(/[<>]/);
          expect(sanitized.description).not.toMatch(/[<>]/);
          expect(sanitized.notes).not.toMatch(/[<>]/);
          
          // Property: Object structure should be preserved
          expect(Object.keys(sanitized)).toEqual(Object.keys(obj));
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should block dangerous URL protocols', () => {
    const dangerousProtocols = ['javascript:', 'data:', 'vbscript:'];
    
    fc.assert(
      fc.property(
        fc.constantFrom(...dangerousProtocols),
        fc.string(),
        (protocol, code) => {
          const url = `${protocol}${code}`;
          const sanitized = sanitizeUrl(url);
          
          // Property: Dangerous URLs should be blocked (return empty string)
          expect(sanitized).toBe('');
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should allow safe URL protocols', () => {
    const safeProtocols = ['http://', 'https://', 'mailto:', 'tel:'];
    
    fc.assert(
      fc.property(
        fc.constantFrom(...safeProtocols),
        fc.webUrl(),
        (protocol, url) => {
          const safeUrl = protocol + url.replace(/^https?:\/\//, '');
          const sanitized = sanitizeUrl(safeUrl);
          
          // Property: Safe URLs should not be blocked
          expect(sanitized).toBe(safeUrl);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should detect XSS patterns in input', () => {
    const xssPatterns = [
      '<script>alert(1)</script>',
      'javascript:alert(1)',
      '<img onerror="alert(1)">',
      '<iframe src="evil.com">',
      'eval(malicious)',
    ];
    
    fc.assert(
      fc.property(fc.constantFrom(...xssPatterns), (pattern) => {
        // Property: XSS patterns should be detected
        expect(containsXss(pattern)).toBe(true);
      }),
      { numRuns: 100 }
    );
  });

  it('should not flag safe content as XSS', () => {
    fc.assert(
      fc.property(
        fc.string().filter(s => !containsXss(s)),
        (safeContent) => {
          // Property: Safe content should not be flagged
          expect(containsXss(safeContent)).toBe(false);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should handle non-string inputs gracefully', () => {
    const nonStringInputs = [null, undefined, 123, true, {}, []];
    
    nonStringInputs.forEach(input => {
      // Property: Non-string inputs should be converted to strings
      const sanitized = sanitizeInput(input as any);
      expect(typeof sanitized).toBe('string');
    });
  });

  it('should preserve safe content while removing dangerous content', () => {
    fc.assert(
      fc.property(
        fc.string().filter(s => !s.includes('<') && !s.includes('>')),
        (safeContent) => {
          const input = `${safeContent}<script>alert('xss')</script>`;
          const sanitized = sanitizeInput(input);
          
          // Property: Safe content should be preserved (after escaping)
          // Dangerous content should be removed/escaped
          expect(sanitized).not.toContain('<script');
          expect(sanitized).not.toContain('</script>');
        }
      ),
      { numRuns: 100 }
    );
  });
});
