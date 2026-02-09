"""
Firebase Authentication Middleware and Utilities

Handles Firebase token verification and Google Sign-In integration.
"""

from firebase_admin import auth
from rest_framework import authentication, exceptions
from django.contrib.auth.models import AnonymousUser
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger('health_ai.firebase_auth')


class FirebaseUser:
    """
    Custom user class for Firebase authenticated users.
    
    Mimics Django User but uses Firebase UID.
    """
    
    def __init__(self, uid: str, email: str, display_name: str = None, 
                 photo_url: str = None, email_verified: bool = False):
        self.uid = uid
        self.email = email
        self.display_name = display_name
        self.photo_url = photo_url
        self.email_verified = email_verified
        self.is_authenticated = True
        self.is_anonymous = False
    
    def __str__(self):
        return f"FirebaseUser({self.email})"
    
    @property
    def username(self):
        """Return email as username for compatibility."""
        return self.email
    
    @property
    def is_active(self):
        """User is active if email is verified."""
        return self.email_verified


class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Django REST Framework authentication class for Firebase tokens.
    
    Verifies Firebase ID tokens from Authorization header.
    """
    
    def authenticate(self, request):
        """
        Authenticate request using Firebase ID token.
        
        Expected header format:
        Authorization: Bearer <firebase_id_token>
        
        Returns:
            Tuple of (user, token) if authenticated, None otherwise
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        # Extract token
        id_token = auth_header.split('Bearer ')[1]
        
        try:
            # Verify token with Firebase
            decoded_token = auth.verify_id_token(id_token)
            
            # Extract user info
            uid = decoded_token['uid']
            email = decoded_token.get('email', '')
            display_name = decoded_token.get('name', '')
            photo_url = decoded_token.get('picture', '')
            email_verified = decoded_token.get('email_verified', False)
            
            # Create FirebaseUser instance
            user = FirebaseUser(
                uid=uid,
                email=email,
                display_name=display_name,
                photo_url=photo_url,
                email_verified=email_verified
            )
            
            logger.info(f"Authenticated user: {email} (UID: {uid})")
            
            return (user, decoded_token)
            
        except auth.InvalidIdTokenError:
            logger.warning("Invalid Firebase ID token")
            raise exceptions.AuthenticationFailed('Invalid authentication token')
        
        except auth.ExpiredIdTokenError:
            logger.warning("Expired Firebase ID token")
            raise exceptions.AuthenticationFailed('Authentication token has expired')
        
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise exceptions.AuthenticationFailed('Authentication failed')
    
    def authenticate_header(self, request):
        """Return authentication header for 401 responses."""
        return 'Bearer realm="api"'


def verify_firebase_token(id_token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Firebase ID token and return decoded token.
    
    Args:
        id_token: Firebase ID token string
        
    Returns:
        Decoded token dict if valid, None otherwise
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return None


def get_user_from_token(id_token: str) -> Optional[FirebaseUser]:
    """
    Get FirebaseUser instance from ID token.
    
    Args:
        id_token: Firebase ID token string
        
    Returns:
        FirebaseUser instance if valid, None otherwise
    """
    decoded_token = verify_firebase_token(id_token)
    
    if decoded_token:
        return FirebaseUser(
            uid=decoded_token['uid'],
            email=decoded_token.get('email', ''),
            display_name=decoded_token.get('name', ''),
            photo_url=decoded_token.get('picture', ''),
            email_verified=decoded_token.get('email_verified', False)
        )
    
    return None


def create_custom_token(uid: str) -> str:
    """
    Create custom Firebase token for a user.
    
    Args:
        uid: User ID
        
    Returns:
        Custom token string
    """
    try:
        custom_token = auth.create_custom_token(uid)
        return custom_token.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to create custom token: {e}")
        raise


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Get Firebase user by email.
    
    Args:
        email: User email address
        
    Returns:
        User record dict if found, None otherwise
    """
    try:
        user = auth.get_user_by_email(email)
        return {
            'uid': user.uid,
            'email': user.email,
            'display_name': user.display_name,
            'photo_url': user.photo_url,
            'email_verified': user.email_verified,
            'disabled': user.disabled
        }
    except auth.UserNotFoundError:
        return None
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None


def delete_user(uid: str) -> bool:
    """
    Delete Firebase user account.
    
    Args:
        uid: User ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        auth.delete_user(uid)
        logger.info(f"Deleted user: {uid}")
        return True
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return False


class OptionalFirebaseAuthentication(FirebaseAuthentication):
    """
    Optional Firebase authentication.
    
    Allows both authenticated and anonymous requests.
    Sets request.user to FirebaseUser if authenticated, AnonymousUser otherwise.
    """
    
    def authenticate(self, request):
        """Authenticate if token present, otherwise allow anonymous."""
        try:
            result = super().authenticate(request)
            if result:
                return result
        except exceptions.AuthenticationFailed:
            pass
        
        # Return anonymous user if no valid token
        return (AnonymousUser(), None)
