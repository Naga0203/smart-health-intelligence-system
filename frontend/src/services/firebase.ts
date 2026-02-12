// ============================================================================
// Firebase Authentication Service
// ============================================================================

import { initializeApp } from 'firebase/app';
import {
  getAuth,
  signInWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signOut,
  onAuthStateChanged,
  createUserWithEmailAndPassword,
} from 'firebase/auth';

// Firebase configuration from environment variables
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();

// Configure Google provider
googleProvider.setCustomParameters({
  prompt: 'select_account',
});

export class FirebaseService {
  /**
   * Sign in with email and password
   */
  async loginWithEmail(email, password) {
    return signInWithEmailAndPassword(auth, email, password);
  }

  /**
   * Create new user with email and password
   */
  async registerWithEmail(email, password) {
    return createUserWithEmailAndPassword(auth, email, password);
  }

  /**
   * Sign in with Google OAuth
   */
  async loginWithGoogle() {
    return signInWithPopup(auth, googleProvider);
  }

  /**
   * Sign out current user
   */
  async logout() {
    return signOut(auth);
  }

  /**
   * Get Firebase ID token for API authentication
   */
  async getIdToken(forceRefresh = false) {
    const user = auth.currentUser;
    if (!user) return null;
    return user.getIdToken(forceRefresh);
  }

  /**
   * Listen to authentication state changes
   */
  onAuthStateChange(callback) {
    return onAuthStateChanged(auth, callback);
  }

  /**
   * Get current user
   */
  getCurrentUser() {
    return auth.currentUser;
  }
}

export const firebaseService = new FirebaseService();
