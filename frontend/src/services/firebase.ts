// ============================================================================
// Firebase Authentication Service
// ============================================================================

import { initializeApp } from 'firebase/app';
import {
  getAuth,
  signInWithEmailAndPassword,
  signInWithPopup,
  signInWithRedirect,
  getRedirectResult,
  GoogleAuthProvider,
  signOut,
  onAuthStateChanged,
  createUserWithEmailAndPassword,
} from 'firebase/auth';
import { 
  getFirestore, 
  collection, 
  addDoc, 
  setDoc, 
  doc, 
  serverTimestamp,
  getDoc,
  updateDoc
} from 'firebase/firestore';


// Firebase configuration from environment variables
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

// Debug config loading (safe)
console.log('Firebase Config Loading:', {
  apiKey: !!firebaseConfig.apiKey,
  authDomain: !!firebaseConfig.authDomain,
  projectId: !!firebaseConfig.projectId,
  storageBucket: !!firebaseConfig.storageBucket,
  messagingSenderId: !!firebaseConfig.messagingSenderId,
  appId: !!firebaseConfig.appId,
});

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
export const googleProvider = new GoogleAuthProvider();


// Configure Google provider
// googleProvider.setCustomParameters({
//   prompt: 'select_account',
// });

export class FirebaseService {
  /**
   * Sign in with email and password
   */
  async loginWithEmail(email: string, password: string) {
    return signInWithEmailAndPassword(auth, email, password);
  }

  /**
   * Register with email and password
   */
  async registerWithEmail(email: string, password: string) {
    return createUserWithEmailAndPassword(auth, email, password);
  }

  /**
   * Sign in with Google OAuth (Popup)
   */
  async loginWithGoogle() {
    try {
      return await signInWithPopup(auth, googleProvider);
    } catch (error: any) {
      if (error.code === 'auth/popup-blocked' || error.code === 'auth/cancelled-popup-request') {
        // Fallback to redirect
        return signInWithRedirect(auth, googleProvider);
      }
      throw error;
    }
  }

  /**
   * Sign in with Google OAuth (Redirect)
   */
  async loginWithGoogleRedirect() {
    return signInWithRedirect(auth, googleProvider);
  }

  /**
   * Get redirect result
   */
  async getGoogleRedirectResult() {
    return getRedirectResult(auth);
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
  onAuthStateChange(callback: (user: any) => void) {
    return onAuthStateChanged(auth, callback);
  }

  /**
   * Get current user
   */
  getCurrentUser() {
    return auth.currentUser;
  }

  // ========================================================================
  // FIRESTORE HELPERS
  // ========================================================================

  /**
   * Simple helper to save data to a specific collection
   */
  async saveToCollection(collectionName: string, data: any, id?: string) {
    try {
      const colRef = collection(db, collectionName);
      const docData = {
        ...data,
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp(),
      };

      if (id) {
        const docRef = doc(db, collectionName, id);
        await setDoc(docRef, docData);
        return id;
      } else {
        const docRef = await addDoc(colRef, docData);
        return docRef.id;
      }
    } catch (error) {
      console.error(`Error saving to ${collectionName}:`, error);
      throw error;
    }
  }

  /**
   * Update an existing document
   */
  async updateDocument(collectionName: string, id: string, data: any) {
    try {
      const docRef = doc(db, collectionName, id);
      await updateDoc(docRef, {
        ...data,
        updatedAt: serverTimestamp(),
      });
    } catch (error) {
      console.error(`Error updating document ${id} in ${collectionName}:`, error);
      throw error;
    }
  }

  /**
   * Get a single document
   */
  async getDocument(collectionName: string, id: string) {
    try {
      const docRef = doc(db, collectionName, id);
      const docSnap = await getDoc(docRef);
      if (docSnap.exists()) {
        return { id: docSnap.id, ...docSnap.data() };
      }
      return null;
    } catch (error) {
      console.error(`Error getting document ${id} from ${collectionName}:`, error);
      throw error;
    }
  }

  /**
   * Log an error to the 'errors' collection
   */
  async logError(error: any, context: string) {
    const user = auth.currentUser;
    return this.saveToCollection('errors', {
      userId: user?.uid || 'anonymous',
      error: error.message || String(error),
      context,
      timestamp: serverTimestamp(),
      userAgent: navigator.userAgent,
    });
  }
}


export const firebaseService = new FirebaseService();
