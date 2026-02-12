// ============================================================================
// CSRF Protection Utility
// ============================================================================
// Provides CSRF token management for state-changing requests

/**
 * Get CSRF token from cookie
 * Django sets csrftoken cookie that we need to read
 */
export function getCsrfToken(): string | null {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');
  
  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith(name + '=')) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }
  
  return null;
}

/**
 * Generate a CSRF token if one doesn't exist
 * This is a fallback for when the backend doesn't set one
 */
export function generateCsrfToken(): string {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
}

/**
 * Set CSRF token in cookie
 */
export function setCsrfToken(token: string): void {
  document.cookie = `csrftoken=${token}; path=/; SameSite=Strict`;
}

/**
 * Ensure CSRF token exists, generate if needed
 */
export function ensureCsrfToken(): string {
  let token = getCsrfToken();
  
  if (!token) {
    token = generateCsrfToken();
    setCsrfToken(token);
  }
  
  return token;
}

/**
 * Check if request method requires CSRF protection
 */
export function requiresCsrfProtection(method: string): boolean {
  const safeMethods = ['GET', 'HEAD', 'OPTIONS', 'TRACE'];
  return !safeMethods.includes(method.toUpperCase());
}
