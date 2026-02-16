// ============================================================================
// Authentication Store - Zustand
// ============================================================================

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { firebaseService } from '@/services/firebase';
import { tokenStorage } from '@/utils/secureStorage';
import { logger } from '@/utils/logger';

interface User {
  uid: string;
  email: string;
  displayName: string | null;
  photoURL: string | null;
}

interface AuthStore {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  initialize: () => void;
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      loading: false,
      error: null,

      // Initialize auth state listener
      initialize: () => {
        firebaseService.onAuthStateChange(async (firebaseUser) => {
          if (firebaseUser) {
            const token = await firebaseUser.getIdToken();
            const user = {
              uid: firebaseUser.uid,
              email: firebaseUser.email || '',
              displayName: firebaseUser.displayName,
              photoURL: firebaseUser.photoURL,
            };

            set({ user, token, loading: false });
            tokenStorage.setToken(token);
          } else {
            set({ user: null, token: null, loading: false });
            tokenStorage.removeToken();
          }
        });
      },

      // Login with email and password
      login: async (email, password) => {
        set({ loading: true, error: null });
        try {
          const userCredential = await firebaseService.loginWithEmail(email, password);
          const token = await userCredential.user.getIdToken();

          const user = {
            uid: userCredential.user.uid,
            email: userCredential.user.email || '',
            displayName: userCredential.user.displayName,
            photoURL: userCredential.user.photoURL,
          };

          set({ user, token, loading: false, error: null });
          tokenStorage.setToken(token);
        } catch (error) {
          set({
            loading: false,
            error: error.message || 'Login failed'
          });
          throw error;
        }
      },

      // Login with Google OAuth
      loginWithGoogle: async () => {
        set({ loading: true, error: null });
        try {
          const userCredential = await firebaseService.loginWithGoogle();
          const token = await userCredential.user.getIdToken();

          const user = {
            uid: userCredential.user.uid,
            email: userCredential.user.email || '',
            displayName: userCredential.user.displayName,
            photoURL: userCredential.user.photoURL,
          };

          set({ user, token, loading: false, error: null });
          tokenStorage.setToken(token);
        } catch (error: any) {
          console.error('Google Login Error:', error);
          console.error('Error Code:', error.code);
          console.error('Error Message:', error.message);
          set({
            loading: false,
            error: error.message || 'Google login failed'
          });
          throw error;
        }
      },

      // Logout
      logout: async () => {
        set({ loading: true, error: null });
        try {
          await firebaseService.logout();
          set({ user: null, token: null, loading: false, error: null });
          tokenStorage.clearAuth();
        } catch (error) {
          set({
            loading: false,
            error: error.message || 'Logout failed'
          });
          throw error;
        }
      },

      // Refresh token
      refreshToken: async () => {
        try {
          const token = await firebaseService.getIdToken(true);
          if (token) {
            set({ token });
            tokenStorage.setToken(token);
          }
        } catch (error) {
          logger.error('Token refresh failed', error);
          set({ user: null, token: null });
          tokenStorage.clearAuth();
        }
      },

      // Set user
      setUser: (user) => {
        set({ user });
      },

      // Set token
      setToken: (token) => {
        set({ token });
        if (token) {
          tokenStorage.setToken(token);
        } else {
          tokenStorage.removeToken();
        }
      },

      // Clear error
      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token
      }),
    }
  )
);
