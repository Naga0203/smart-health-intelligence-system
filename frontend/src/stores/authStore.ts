// ============================================================================
// Authentication Store - Zustand
// ============================================================================

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { firebaseService } from '@/services/firebase';
import type { User } from '@/types';

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  clearError: () => void;
  initialize: () => void;
}

export const useAuthStore = create<AuthState>()(
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
            const user: User = {
              uid: firebaseUser.uid,
              email: firebaseUser.email || '',
              displayName: firebaseUser.displayName,
              photoURL: firebaseUser.photoURL,
            };
            
            set({ user, token, loading: false });
            localStorage.setItem('firebase_token', token);
          } else {
            set({ user: null, token: null, loading: false });
            localStorage.removeItem('firebase_token');
          }
        });
      },

      // Login with email and password
      login: async (email: string, password: string) => {
        set({ loading: true, error: null });
        try {
          const userCredential = await firebaseService.loginWithEmail(email, password);
          const token = await userCredential.user.getIdToken();
          
          const user: User = {
            uid: userCredential.user.uid,
            email: userCredential.user.email || '',
            displayName: userCredential.user.displayName,
            photoURL: userCredential.user.photoURL,
          };

          set({ user, token, loading: false, error: null });
          localStorage.setItem('firebase_token', token);
        } catch (error: any) {
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
          
          const user: User = {
            uid: userCredential.user.uid,
            email: userCredential.user.email || '',
            displayName: userCredential.user.displayName,
            photoURL: userCredential.user.photoURL,
          };

          set({ user, token, loading: false, error: null });
          localStorage.setItem('firebase_token', token);
        } catch (error: any) {
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
          localStorage.removeItem('firebase_token');
        } catch (error: any) {
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
            localStorage.setItem('firebase_token', token);
          }
        } catch (error: any) {
          console.error('Token refresh failed:', error);
          set({ user: null, token: null });
          localStorage.removeItem('firebase_token');
        }
      },

      // Set user
      setUser: (user: User | null) => {
        set({ user });
      },

      // Set token
      setToken: (token: string | null) => {
        set({ token });
        if (token) {
          localStorage.setItem('firebase_token', token);
        } else {
          localStorage.removeItem('firebase_token');
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
