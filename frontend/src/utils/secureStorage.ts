// ============================================================================
// Secure Storage Utility
// ============================================================================
// Provides secure storage for sensitive data like authentication tokens
// Uses localStorage with basic obfuscation (not true encryption in browser)
// For production, consider using httpOnly cookies via backend

/**
 * Simple obfuscation for localStorage (not cryptographically secure)
 * In production, tokens should be stored in httpOnly cookies set by backend
 */
function obfuscate(value: string): string {
  return btoa(encodeURIComponent(value));
}

function deobfuscate(value: string): string {
  try {
    return decodeURIComponent(atob(value));
  } catch {
    return '';
  }
}

/**
 * Secure storage interface for sensitive data
 */
export const secureStorage = {
  /**
   * Store a value securely
   */
  setItem(key: string, value: string): void {
    try {
      const obfuscated = obfuscate(value);
      localStorage.setItem(key, obfuscated);
    } catch (error) {
      console.error('Failed to store item securely:', error);
    }
  },

  /**
   * Retrieve a value securely
   */
  getItem(key: string): string | null {
    try {
      const obfuscated = localStorage.getItem(key);
      if (!obfuscated) return null;
      return deobfuscate(obfuscated);
    } catch (error) {
      console.error('Failed to retrieve item securely:', error);
      return null;
    }
  },

  /**
   * Remove a value
   */
  removeItem(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Failed to remove item:', error);
    }
  },

  /**
   * Clear all secure storage
   */
  clear(): void {
    try {
      // Only clear auth-related items, not all localStorage
      const authKeys = ['firebase_token', 'auth-storage'];
      authKeys.forEach(key => localStorage.removeItem(key));
    } catch (error) {
      console.error('Failed to clear secure storage:', error);
    }
  },

  /**
   * Check if storage is available
   */
  isAvailable(): boolean {
    try {
      const test = '__storage_test__';
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      return true;
    } catch {
      return false;
    }
  }
};

/**
 * Token-specific storage utilities
 */
export const tokenStorage = {
  /**
   * Store authentication token securely
   */
  setToken(token: string): void {
    secureStorage.setItem('firebase_token', token);
  },

  /**
   * Retrieve authentication token
   */
  getToken(): string | null {
    return secureStorage.getItem('firebase_token');
  },

  /**
   * Remove authentication token
   */
  removeToken(): void {
    secureStorage.removeItem('firebase_token');
  },

  /**
   * Clear all authentication data
   */
  clearAuth(): void {
    secureStorage.clear();
  }
};
