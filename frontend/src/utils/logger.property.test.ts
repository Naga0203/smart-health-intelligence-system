// ============================================================================
// Property Test: Token Logging Prevention
// Feature: ai-health-frontend
// Property 22: Authentication tokens are never logged
// Validates: Requirements 14.5
// ============================================================================

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as fc from 'fast-check';
import { logger } from './logger';

describe('Property 22: Authentication tokens are never logged', () => {
  let consoleInfoSpy: any;
  let consoleWarnSpy: any;
  let consoleErrorSpy: any;
  let consoleDebugSpy: any;

  beforeEach(() => {
    // Spy on console methods
    consoleInfoSpy = vi.spyOn(console, 'info').mockImplementation(() => {});
    consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    consoleDebugSpy = vi.spyOn(console, 'debug').mockImplementation(() => {});
  });

  afterEach(() => {
    // Restore console methods
    consoleInfoSpy.mockRestore();
    consoleWarnSpy.mockRestore();
    consoleErrorSpy.mockRestore();
    consoleDebugSpy.mockRestore();
  });

  it('should redact token fields from logged objects', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 20, maxLength: 100 }),
        fc.string(),
        (token, message) => {
          const data = {
            token: token,
            message: message,
          };

          logger.info('Test log', data);

          // Property: Token field should be redacted in logs
          const loggedData = consoleInfoSpy.mock.calls[0][1];
          expect(loggedData.token).toBe('[REDACTED]');
          expect(loggedData.message).toBe(message);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should redact authorization headers from logged objects', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 20, maxLength: 100 }),
        (authToken) => {
          const data = {
            headers: {
              Authorization: `Bearer ${authToken}`,
              'Content-Type': 'application/json',
            },
          };

          logger.info('API request', data);

          // Property: Authorization header should be redacted
          const loggedData = consoleInfoSpy.mock.calls[0][1];
          expect(loggedData.headers.Authorization).toBe('[REDACTED]');
          expect(loggedData.headers['Content-Type']).toBe('application/json');
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should redact password fields from logged objects', () => {
    fc.assert(
      fc.property(
        fc.string(),
        fc.string(),
        (password, username) => {
          const data = {
            username: username,
            password: password,
          };

          logger.warn('Login attempt', data);

          // Property: Password field should be redacted
          const loggedData = consoleWarnSpy.mock.calls[0][1];
          expect(loggedData.password).toBe('[REDACTED]');
          expect(loggedData.username).toBe(username);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should redact API keys from logged objects', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 20, maxLength: 50 }),
        (apiKey) => {
          const data = {
            api_key: apiKey,
            endpoint: '/api/test',
          };

          logger.error('API error', data);

          // Property: API key should be redacted
          const loggedData = consoleErrorSpy.mock.calls[0][1];
          expect(loggedData.api_key).toBe('[REDACTED]');
          expect(loggedData.endpoint).toBe('/api/test');
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should redact bearer tokens from logged strings', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 30, maxLength: 100 }).filter(s => /^[A-Za-z0-9._-]+$/.test(s)),
        (token) => {
          const data = {
            bearer: token,
            status: 'active',
          };

          logger.debug('Auth status', data);

          // Property: Bearer token should be redacted
          const loggedData = consoleDebugSpy.mock.calls[0]?.[1];
          if (loggedData) {
            expect(loggedData.bearer).toBe('[REDACTED]');
            expect(loggedData.status).toBe('active');
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should redact nested token fields in complex objects', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 20, maxLength: 100 }),
        fc.string(),
        (token, userId) => {
          const data = {
            user: {
              id: userId,
              auth: {
                token: token,
              },
            },
          };

          logger.info('User data', data);

          // Property: Nested token should be redacted
          const loggedData = consoleInfoSpy.mock.calls[0][1];
          expect(loggedData.user.auth.token).toBe('[REDACTED]');
          expect(loggedData.user.id).toBe(userId);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should redact tokens in arrays', () => {
    fc.assert(
      fc.property(
        fc.array(fc.string({ minLength: 20, maxLength: 100 }), { minLength: 1, maxLength: 5 }),
        (tokens) => {
          const data = {
            tokens: tokens,
            count: tokens.length,
          };

          logger.warn('Multiple tokens', data);

          // Property: All tokens in array should be redacted
          const loggedData = consoleWarnSpy.mock.calls[0][1];
          loggedData.tokens.forEach((token: string) => {
            expect(token).toBe('[REDACTED]');
          });
          expect(loggedData.count).toBe(tokens.length);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should preserve non-sensitive data while redacting sensitive fields', () => {
    fc.assert(
      fc.property(
        fc.record({
          token: fc.string({ minLength: 20, maxLength: 100 }),
          username: fc.string(),
          email: fc.emailAddress(),
          timestamp: fc.date(),
        }),
        (data) => {
          logger.info('User action', data);

          // Property: Sensitive fields redacted, non-sensitive preserved
          const loggedData = consoleInfoSpy.mock.calls[0][1];
          expect(loggedData.token).toBe('[REDACTED]');
          expect(loggedData.username).toBe(data.username);
          expect(loggedData.email).toBe(data.email);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should redact credentials from error objects', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 20, maxLength: 100 }),
        fc.string(),
        (credential, errorMessage) => {
          const error = {
            message: errorMessage,
            credential: credential,
            code: 'AUTH_ERROR',
          };

          logger.error('Authentication failed', error);

          // Property: Credential should be redacted from error
          const loggedError = consoleErrorSpy.mock.calls[0][1];
          expect(loggedError.credential).toBe('[REDACTED]');
          expect(loggedError.message).toBe(errorMessage);
          expect(loggedError.code).toBe('AUTH_ERROR');
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should handle case-insensitive sensitive field names', () => {
    const sensitiveFields = ['Token', 'TOKEN', 'Authorization', 'AUTHORIZATION', 'Password', 'PASSWORD'];

    fc.assert(
      fc.property(
        fc.constantFrom(...sensitiveFields),
        fc.string({ minLength: 20, maxLength: 100 }),
        (fieldName, value) => {
          const data = {
            [fieldName]: value,
            safe: 'data',
          };

          logger.info('Test', data);

          // Property: Sensitive fields should be redacted regardless of case
          const loggedData = consoleInfoSpy.mock.calls[0][1];
          expect(loggedData[fieldName]).toBe('[REDACTED]');
          expect(loggedData.safe).toBe('data');
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should redact long alphanumeric strings that look like tokens', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 30, maxLength: 100 }).filter(s => /^[A-Za-z0-9._-]+$/.test(s)),
        (tokenLikeString) => {
          const data = {
            value: tokenLikeString,
          };

          const redacted = logger.redact(data);

          // Property: Long alphanumeric strings should be treated as potential tokens
          expect(redacted.value).toBe('[REDACTED]');
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should not redact short strings or normal text', () => {
    fc.assert(
      fc.property(
        fc.string({ maxLength: 15 }),
        (shortString) => {
          const data = {
            message: shortString,
          };

          const redacted = logger.redact(data);

          // Property: Short strings should not be redacted
          expect(redacted.message).toBe(shortString);
        }
      ),
      { numRuns: 100 }
    );
  });
});
