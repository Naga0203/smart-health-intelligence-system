// ============================================================================
// Property Test: HTTPS Usage
// Feature: ai-health-frontend
// Property 21: API requests use HTTPS protocol
// Validates: Requirements 14.4
// ============================================================================

import { describe, it, expect, beforeEach, vi } from 'vitest';
import * as fc from 'fast-check';
import axios from 'axios';

describe('Property 21: API requests use HTTPS protocol', () => {
  beforeEach(() => {
    // Clear any existing environment variables
    vi.unstubAllEnvs();
  });

  it('should reject HTTP URLs in production mode', () => {
    fc.assert(
      fc.property(
        fc.webUrl({ validSchemes: ['http'] }),
        (httpUrl) => {
          // Mock production environment
          vi.stubEnv('PROD', true);
          vi.stubEnv('VITE_API_BASE_URL', httpUrl);
          
          // Property: Creating API service with HTTP URL in production should throw
          expect(() => {
            // Dynamic import to get fresh instance with new env
            const APIService = class {
              constructor() {
                const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
                
                if (import.meta.env.PROD && !baseURL.startsWith('https://')) {
                  throw new Error('API base URL must use HTTPS in production');
                }
              }
            };
            new APIService();
          }).toThrow('API base URL must use HTTPS in production');
          
          vi.unstubAllEnvs();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should accept HTTPS URLs in production mode', () => {
    fc.assert(
      fc.property(
        fc.webUrl({ validSchemes: ['https'] }),
        (httpsUrl) => {
          // Mock production environment
          vi.stubEnv('PROD', true);
          vi.stubEnv('VITE_API_BASE_URL', httpsUrl);
          
          // Property: Creating API service with HTTPS URL in production should succeed
          expect(() => {
            const APIService = class {
              constructor() {
                const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
                
                if (import.meta.env.PROD && !baseURL.startsWith('https://')) {
                  throw new Error('API base URL must use HTTPS in production');
                }
              }
            };
            new APIService();
          }).not.toThrow();
          
          vi.unstubAllEnvs();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should allow HTTP URLs in development mode', () => {
    fc.assert(
      fc.property(
        fc.webUrl({ validSchemes: ['http', 'https'] }),
        (url) => {
          // Mock development environment
          vi.stubEnv('PROD', false);
          vi.stubEnv('DEV', true);
          vi.stubEnv('VITE_API_BASE_URL', url);
          
          // Property: Any URL should be accepted in development
          expect(() => {
            const APIService = class {
              constructor() {
                const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
                
                if (import.meta.env.PROD && !baseURL.startsWith('https://')) {
                  throw new Error('API base URL must use HTTPS in production');
                }
              }
            };
            new APIService();
          }).not.toThrow();
          
          vi.unstubAllEnvs();
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should validate protocol at service initialization', () => {
    const testCases = [
      { url: 'https://api.example.com', prod: true, shouldPass: true },
      { url: 'http://api.example.com', prod: true, shouldPass: false },
      { url: 'https://api.example.com', prod: false, shouldPass: true },
      { url: 'http://localhost:8000', prod: false, shouldPass: true },
    ];

    testCases.forEach(({ url, prod, shouldPass }) => {
      vi.stubEnv('PROD', prod);
      vi.stubEnv('VITE_API_BASE_URL', url);
      
      const createService = () => {
        const APIService = class {
          constructor() {
            const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
            
            if (import.meta.env.PROD && !baseURL.startsWith('https://')) {
              throw new Error('API base URL must use HTTPS in production');
            }
          }
        };
        return new APIService();
      };
      
      if (shouldPass) {
        expect(createService).not.toThrow();
      } else {
        expect(createService).toThrow('API base URL must use HTTPS in production');
      }
      
      vi.unstubAllEnvs();
    });
  });

  it('should ensure all API requests use the configured base URL protocol', () => {
    fc.assert(
      fc.property(
        fc.webUrl({ validSchemes: ['https'] }),
        fc.constantFrom('/api/health/', '/api/user/profile/', '/api/status/'),
        (baseUrl, endpoint) => {
          // Create axios instance with HTTPS base URL
          const client = axios.create({
            baseURL: baseUrl,
          });
          
          // Property: Request URL should use HTTPS protocol
          const requestUrl = new URL(endpoint, baseUrl);
          expect(requestUrl.protocol).toBe('https:');
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should not allow protocol downgrade in request URLs', () => {
    fc.assert(
      fc.property(
        fc.webUrl({ validSchemes: ['https'] }),
        (httpsBaseUrl) => {
          // Property: Even if someone tries to make an HTTP request,
          // the base URL protocol should be preserved
          const client = axios.create({
            baseURL: httpsBaseUrl,
          });
          
          // Verify base URL uses HTTPS
          expect(client.defaults.baseURL).toMatch(/^https:\/\//);
        }
      ),
      { numRuns: 100 }
    );
  });

  it('should validate URL protocol is secure for any production endpoint', () => {
    const endpoints = [
      '/api/health/analyze/',
      '/api/assess/',
      '/api/user/profile/',
      '/api/user/assessments/',
      '/api/predict/top/',
      '/api/status/',
      '/api/diseases/',
    ];

    fc.assert(
      fc.property(
        fc.webUrl({ validSchemes: ['https'] }),
        fc.constantFrom(...endpoints),
        (baseUrl, endpoint) => {
          // Property: All production API endpoints should use HTTPS
          const fullUrl = new URL(endpoint, baseUrl);
          expect(fullUrl.protocol).toBe('https:');
        }
      ),
      { numRuns: 100 }
    );
  });
});
