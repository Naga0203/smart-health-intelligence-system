// ============================================================================
// Authentication Store - Zustand
// ============================================================================

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { firebaseService } from '@/services/firebase';

export const useAuthStore = create(
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
            localStorage.setItem('firebase_token', token);
          } else {
            set({ user: null, token: null, loading: false });
            localStorage.removeItem('firebase_token');
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
          localStorage.setItem('firebase_token', token);
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
          localStorage.setItem('firebase_token', token);
        } catch (error) {
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
            localStorage.setItem('firebase_token', token);
          }
        } catch (error) {
          console.error('Token refresh failed:', error);
          set({ user: null, token: null });
          localStorage.removeItem('firebase_token');
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
