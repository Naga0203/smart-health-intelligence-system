import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { FirebaseService } from './firebase';

// Mock Firebase Auth
vi.mock('firebase/app', () => ({
  initializeApp: vi.fn(() => ({})),
}));

vi.mock('firebase/auth', () => {
  const mockUser = {
    uid: 'test-uid',
    email: 'test@example.com',
    displayName: 'Test User',
    photoURL: null,
    getIdToken: vi.fn(),
  };

  const mockGoogleProvider = function() {
    this.setCustomParameters = vi.fn();
  };

  return {
    getAuth: vi.fn(() => ({
      currentUser: mockUser,
    })),
    signInWithEmailAndPassword: vi.fn(),
    signInWithPopup: vi.fn(),
    GoogleAuthProvider: mockGoogleProvider,
    signOut: vi.fn(),
    onAuthStateChanged: vi.fn(),
    createUserWithEmailAndPassword: vi.fn(),
  };
});

describe('FirebaseService', () => {
  let firebaseService;
  let mockAuth;
  let mockSignInWithEmailAndPassword;
  let mockSignInWithPopup;
  let mockSignOut;
  let mockOnAuthStateChanged;

  beforeEach(async () => {
    // Reset mocks
    vi.clearAllMocks();

    // Import mocked functions
    const authModule = await import('firebase/auth');
    mockSignInWithEmailAndPassword = authModule.signInWithEmailAndPassword;
    mockSignInWithPopup = authModule.signInWithPopup;
    mockSignOut = authModule.signOut;
    mockOnAuthStateChanged = authModule.onAuthStateChanged;
    mockAuth = authModule.getAuth();

    // Create service instance
    firebaseService = new FirebaseService();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('loginWithEmail', () => {
    it('should sign in with email and password', async () => {
      const email = 'test@example.com';
      const password = 'password123';
      const mockUserCredential = {
        user: {
          uid: 'test-uid',
          email: email,
        },
      };

      mockSignInWithEmailAndPassword.mockResolvedValue(mockUserCredential);

      const result = await firebaseService.loginWithEmail(email, password);

      expect(mockSignInWithEmailAndPassword).toHaveBeenCalledWith(
        expect.anything(),
        email,
        password
      );
      expect(result).toEqual(mockUserCredential);
    });

    it('should throw error on invalid credentials', async () => {
      const email = 'test@example.com';
      const password = 'wrongpassword';
      const error = new Error('Invalid credentials');

      mockSignInWithEmailAndPassword.mockRejectedValue(error);

      await expect(
        firebaseService.loginWithEmail(email, password)
      ).rejects.toThrow('Invalid credentials');
    });
  });

  describe('loginWithGoogle', () => {
    it('should sign in with Google OAuth', async () => {
      const mockUserCredential = {
        user: {
          uid: 'google-uid',
          email: 'google@example.com',
          displayName: 'Google User',
        },
      };

      mockSignInWithPopup.mockResolvedValue(mockUserCredential);

      const result = await firebaseService.loginWithGoogle();

      expect(mockSignInWithPopup).toHaveBeenCalledWith(
        expect.anything(),
        expect.anything()
      );
      expect(result).toEqual(mockUserCredential);
    });

    it('should handle Google OAuth cancellation', async () => {
      const error = new Error('Popup closed by user');
      error.code = 'auth/popup-closed-by-user';

      mockSignInWithPopup.mockRejectedValue(error);

      await expect(firebaseService.loginWithGoogle()).rejects.toThrow(
        'Popup closed by user'
      );
    });
  });

  describe('logout', () => {
    it('should sign out current user', async () => {
      mockSignOut.mockResolvedValue();

      await firebaseService.logout();

      expect(mockSignOut).toHaveBeenCalledWith(expect.anything());
    });

    it('should handle logout errors', async () => {
      const error = new Error('Logout failed');
      mockSignOut.mockRejectedValue(error);

      await expect(firebaseService.logout()).rejects.toThrow('Logout failed');
    });
  });

  describe('getIdToken', () => {
    it('should retrieve Firebase ID token', async () => {
      const mockToken = 'mock-firebase-token';
      mockAuth.currentUser.getIdToken.mockResolvedValue(mockToken);

      const token = await firebaseService.getIdToken();

      expect(mockAuth.currentUser.getIdToken).toHaveBeenCalledWith(false);
      expect(token).toBe(mockToken);
    });

    it('should force refresh token when requested', async () => {
      const mockToken = 'refreshed-token';
      mockAuth.currentUser.getIdToken.mockResolvedValue(mockToken);

      const token = await firebaseService.getIdToken(true);

      expect(mockAuth.currentUser.getIdToken).toHaveBeenCalledWith(true);
      expect(token).toBe(mockToken);
    });

    it('should return null when no user is logged in', async () => {
      // We need to test the actual behavior by importing the auth module
      // and checking that it properly handles null currentUser
      const firebaseModule = await import('./firebase');
      
      // Temporarily override the auth.currentUser
      const originalCurrentUser = firebaseModule.auth.currentUser;
      Object.defineProperty(firebaseModule.auth, 'currentUser', {
        get: () => null,
        configurable: true,
      });

      const token = await firebaseService.getIdToken();

      expect(token).toBeNull();
      
      // Restore
      Object.defineProperty(firebaseModule.auth, 'currentUser', {
        get: () => originalCurrentUser,
        configurable: true,
      });
    });
  });

  describe('onAuthStateChange', () => {
    it('should register auth state change listener', () => {
      const callback = vi.fn();
      const mockUnsubscribe = vi.fn();
      mockOnAuthStateChanged.mockReturnValue(mockUnsubscribe);

      const unsubscribe = firebaseService.onAuthStateChange(callback);

      expect(mockOnAuthStateChanged).toHaveBeenCalledWith(
        expect.anything(),
        callback
      );
      expect(unsubscribe).toBe(mockUnsubscribe);
    });

    it('should call callback when auth state changes', () => {
      const callback = vi.fn();
      let authStateCallback;

      mockOnAuthStateChanged.mockImplementation((auth, cb) => {
        authStateCallback = cb;
        return vi.fn();
      });

      firebaseService.onAuthStateChange(callback);

      // Simulate auth state change
      const mockUser = { uid: 'new-user', email: 'new@example.com' };
      authStateCallback(mockUser);

      expect(callback).toHaveBeenCalledWith(mockUser);
    });
  });

  describe('getCurrentUser', () => {
    it('should return current user', () => {
      const user = firebaseService.getCurrentUser();

      expect(user).toBe(mockAuth.currentUser);
      expect(user.uid).toBe('test-uid');
      expect(user.email).toBe('test@example.com');
    });
  });
});
