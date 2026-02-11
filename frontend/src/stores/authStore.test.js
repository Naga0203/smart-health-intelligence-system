// ============================================================================
// Authentication Store Tests
// ============================================================================

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useAuthStore } from './authStore';
import { firebaseService } from '@/services/firebase';

// Mock Firebase service
vi.mock('@/services/firebase', () => ({
  firebaseService: {
    loginWithEmail: vi.fn(),
    loginWithGoogle: vi.fn(),
    logout: vi.fn(),
    getIdToken: vi.fn(),
    onAuthStateChange: vi.fn(),
  },
}));

describe('AuthStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.setState({
      user: null,
      token: null,
      loading: false,
      error: null,
    });
    
    // Clear all mocks
    vi.clearAllMocks();
    
    // Clear localStorage
    localStorage.clear();
  });

  describe('login', () => {
    it('should successfully login with email and password', async () => {
      const mockUser = {
        uid: 'test-uid',
        email: 'test@example.com',
        displayName: 'Test User',
        photoURL: null,
        getIdToken: vi.fn().mockResolvedValue('test-token'),
      };

      firebaseService.loginWithEmail.mockResolvedValue({
        user: mockUser,
      });

      const store = useAuthStore.getState();
      await store.login('test@example.com', 'password123');

      const state = useAuthStore.getState();
      expect(state.user).toEqual({
        uid: 'test-uid',
        email: 'test@example.com',
        displayName: 'Test User',
        photoURL: null,
      });
      expect(state.token).toBe('test-token');
      expect(state.loading).toBe(false);
      expect(state.error).toBe(null);
      expect(localStorage.getItem('firebase_token')).toBe('test-token');
    });

    it('should handle login failure', async () => {
      const mockError = new Error('Invalid credentials');
      firebaseService.loginWithEmail.mockRejectedValue(mockError);

      const store = useAuthStore.getState();
      
      await expect(store.login('test@example.com', 'wrong')).rejects.toThrow();

      const state = useAuthStore.getState();
      expect(state.loading).toBe(false);
      expect(state.error).toBe('Invalid credentials');
      expect(state.user).toBe(null);
      expect(state.token).toBe(null);
    });
  });

  describe('loginWithGoogle', () => {
    it('should successfully login with Google OAuth', async () => {
      const mockUser = {
        uid: 'google-uid',
        email: 'google@example.com',
        displayName: 'Google User',
        photoURL: 'https://example.com/photo.jpg',
        getIdToken: vi.fn().mockResolvedValue('google-token'),
      };

      firebaseService.loginWithGoogle.mockResolvedValue({
        user: mockUser,
      });

      const store = useAuthStore.getState();
      await store.loginWithGoogle();

      const state = useAuthStore.getState();
      expect(state.user).toEqual({
        uid: 'google-uid',
        email: 'google@example.com',
        displayName: 'Google User',
        photoURL: 'https://example.com/photo.jpg',
      });
      expect(state.token).toBe('google-token');
      expect(state.loading).toBe(false);
      expect(state.error).toBe(null);
    });

    it('should handle Google login failure', async () => {
      const mockError = new Error('Google auth failed');
      firebaseService.loginWithGoogle.mockRejectedValue(mockError);

      const store = useAuthStore.getState();
      
      await expect(store.loginWithGoogle()).rejects.toThrow();

      const state = useAuthStore.getState();
      expect(state.loading).toBe(false);
      expect(state.error).toBe('Google auth failed');
    });
  });

  describe('logout', () => {
    it('should successfully logout', async () => {
      // Set initial authenticated state
      useAuthStore.setState({
        user: { uid: 'test-uid', email: 'test@example.com' },
        token: 'test-token',
      });
      localStorage.setItem('firebase_token', 'test-token');

      firebaseService.logout.mockResolvedValue();

      const store = useAuthStore.getState();
      await store.logout();

      const state = useAuthStore.getState();
      expect(state.user).toBe(null);
      expect(state.token).toBe(null);
      expect(state.loading).toBe(false);
      expect(state.error).toBe(null);
      expect(localStorage.getItem('firebase_token')).toBe(null);
    });

    it('should handle logout failure', async () => {
      const mockError = new Error('Logout failed');
      firebaseService.logout.mockRejectedValue(mockError);

      const store = useAuthStore.getState();
      
      await expect(store.logout()).rejects.toThrow();

      const state = useAuthStore.getState();
      expect(state.loading).toBe(false);
      expect(state.error).toBe('Logout failed');
    });
  });

  describe('refreshToken', () => {
    it('should successfully refresh token', async () => {
      firebaseService.getIdToken.mockResolvedValue('new-token');

      const store = useAuthStore.getState();
      await store.refreshToken();

      const state = useAuthStore.getState();
      expect(state.token).toBe('new-token');
      expect(localStorage.getItem('firebase_token')).toBe('new-token');
    });

    it('should clear auth state on refresh failure', async () => {
      useAuthStore.setState({
        user: { uid: 'test-uid', email: 'test@example.com' },
        token: 'old-token',
      });

      firebaseService.getIdToken.mockRejectedValue(new Error('Token expired'));

      const store = useAuthStore.getState();
      await store.refreshToken();

      const state = useAuthStore.getState();
      expect(state.user).toBe(null);
      expect(state.token).toBe(null);
      expect(localStorage.getItem('firebase_token')).toBe(null);
    });
  });

  describe('setUser', () => {
    it('should set user', () => {
      const mockUser = {
        uid: 'test-uid',
        email: 'test@example.com',
        displayName: 'Test User',
        photoURL: null,
      };

      const store = useAuthStore.getState();
      store.setUser(mockUser);

      const state = useAuthStore.getState();
      expect(state.user).toEqual(mockUser);
    });
  });

  describe('setToken', () => {
    it('should set token and store in localStorage', () => {
      const store = useAuthStore.getState();
      store.setToken('new-token');

      const state = useAuthStore.getState();
      expect(state.token).toBe('new-token');
      expect(localStorage.getItem('firebase_token')).toBe('new-token');
    });

    it('should clear token from localStorage when set to null', () => {
      localStorage.setItem('firebase_token', 'old-token');

      const store = useAuthStore.getState();
      store.setToken(null);

      const state = useAuthStore.getState();
      expect(state.token).toBe(null);
      expect(localStorage.getItem('firebase_token')).toBe(null);
    });
  });

  describe('clearError', () => {
    it('should clear error', () => {
      useAuthStore.setState({ error: 'Some error' });

      const store = useAuthStore.getState();
      store.clearError();

      const state = useAuthStore.getState();
      expect(state.error).toBe(null);
    });
  });
});
