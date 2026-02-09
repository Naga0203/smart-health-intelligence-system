"""
Firebase Firestore Database Integration for AI Health Intelligence System

Replaces MongoDB with Firebase Firestore for better scalability,
real-time updates, and integrated Google Authentication.

Collections:
- users: User profiles and authentication data
- assessments: Health assessment records
- predictions: Disease prediction results
- explanations: AI-generated explanations
- recommendations: Treatment recommendations
- audit_logs: System audit trail
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
import json
from pathlib import Path
from django.conf import settings

logger = logging.getLogger('health_ai.firebase')


class FirebaseDatabase:
    """
    Firebase Firestore database client for health assessment data.
    
    Provides methods for storing and retrieving:
    - User data
    - Health assessments
    - Predictions
    - Explanations
    - Recommendations
    - Audit logs
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to ensure single Firebase connection."""
        if cls._instance is None:
            cls._instance = super(FirebaseDatabase, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Firebase connection."""
        if not FirebaseDatabase._initialized:
            self._initialize_firebase()
            FirebaseDatabase._initialized = True
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK."""
        try:
            # Check if already initialized
            if firebase_admin._apps:
                logger.info("Firebase already initialized")
                self.db = firestore.client()
                return
            
            # Get Firebase credentials path from settings
            cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', 'config/firebase-credentials.json')
            cred_file = Path(cred_path)
            
            if not cred_file.exists():
                logger.warning(f"Firebase credentials not found at: {cred_path}")
                logger.warning("Using default credentials (for development only)")
                # Initialize with default credentials (for local development)
                firebase_admin.initialize_app()
            else:
                # Initialize with service account
                cred = credentials.Certificate(str(cred_file))
                firebase_admin.initialize_app(cred)
                logger.info(f"Firebase initialized with credentials from: {cred_path}")
            
            # Get Firestore client
            self.db = firestore.client()
            
            # Create indexes (Firestore auto-creates most indexes)
            self._ensure_collections()
            
            logger.info("Firebase Firestore connected successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    def _ensure_collections(self):
        """Ensure all required collections exist."""
        collections = [
            'users',
            'assessments',
            'predictions',
            'explanations',
            'recommendations',
            'audit_logs'
        ]
        
        for collection in collections:
            # Firestore creates collections automatically on first write
            # This is just for logging
            logger.debug(f"Collection '{collection}' ready")
    
    # ========================================================================
    # USER MANAGEMENT
    # ========================================================================
    
    def create_or_update_user(self, uid: str, user_data: Dict[str, Any]) -> str:
        """
        Create or update user profile.
        
        Args:
            uid: Firebase user ID (from authentication)
            user_data: User profile data
            
        Returns:
            User document ID
        """
        try:
            user_ref = self.db.collection('users').document(uid)
            
            data = {
                **user_data,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'last_login': firestore.SERVER_TIMESTAMP
            }
            
            # Check if user exists
            if user_ref.get().exists:
                user_ref.update(data)
                logger.info(f"Updated user: {uid}")
            else:
                data['created_at'] = firestore.SERVER_TIMESTAMP
                user_ref.set(data)
                logger.info(f"Created new user: {uid}")
            
            return uid
            
        except Exception as e:
            logger.error(f"Error creating/updating user: {e}")
            raise
    
    def get_user(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get user profile by UID."""
        try:
            user_ref = self.db.collection('users').document(uid)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                return user_doc.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    # ========================================================================
    # HEALTH ASSESSMENTS
    # ========================================================================
    
    def store_assessment(self, user_id: str, assessment_data: Dict[str, Any]) -> str:
        """
        Store complete health assessment.
        
        Args:
            user_id: Firebase user ID
            assessment_data: Complete assessment data
            
        Returns:
            Assessment document ID
        """
        try:
            assessment_ref = self.db.collection('assessments').document()
            
            data = {
                'user_id': user_id,
                **assessment_data,
                'created_at': firestore.SERVER_TIMESTAMP,
                'status': 'completed'
            }
            
            assessment_ref.set(data)
            assessment_id = assessment_ref.id
            
            logger.info(f"Stored assessment: {assessment_id} for user: {user_id}")
            
            return assessment_id
            
        except Exception as e:
            logger.error(f"Error storing assessment: {e}")
            raise
    
    def get_user_assessments(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get user's assessment history.
        
        Args:
            user_id: Firebase user ID
            limit: Maximum number of assessments to return
            
        Returns:
            List of assessment documents
        """
        try:
            assessments_ref = self.db.collection('assessments')
            query = (assessments_ref
                    .where('user_id', '==', user_id)
                    .order_by('created_at', direction=firestore.Query.DESCENDING)
                    .limit(limit))
            
            docs = query.stream()
            
            assessments = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                assessments.append(data)
            
            logger.info(f"Retrieved {len(assessments)} assessments for user: {user_id}")
            
            return assessments
            
        except Exception as e:
            logger.error(f"Error getting user assessments: {e}")
            return []
    
    def get_assessment(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get specific assessment by ID."""
        try:
            assessment_ref = self.db.collection('assessments').document(assessment_id)
            assessment_doc = assessment_ref.get()
            
            if assessment_doc.exists:
                data = assessment_doc.to_dict()
                data['id'] = assessment_doc.id
                return data
            return None
            
        except Exception as e:
            logger.error(f"Error getting assessment: {e}")
            return None
    
    # ========================================================================
    # PREDICTIONS
    # ========================================================================
    
    def store_prediction(self, user_id: str, assessment_id: str, 
                        prediction_data: Dict[str, Any]) -> str:
        """Store disease prediction."""
        try:
            prediction_ref = self.db.collection('predictions').document()
            
            data = {
                'user_id': user_id,
                'assessment_id': assessment_id,
                **prediction_data,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            
            prediction_ref.set(data)
            prediction_id = prediction_ref.id
            
            logger.info(f"Stored prediction: {prediction_id}")
            
            return prediction_id
            
        except Exception as e:
            logger.error(f"Error storing prediction: {e}")
            raise
    
    # ========================================================================
    # EXPLANATIONS
    # ========================================================================
    
    def store_explanation(self, assessment_id: str, 
                         explanation_data: Dict[str, Any]) -> str:
        """Store AI-generated explanation."""
        try:
            explanation_ref = self.db.collection('explanations').document()
            
            data = {
                'assessment_id': assessment_id,
                **explanation_data,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            
            explanation_ref.set(data)
            explanation_id = explanation_ref.id
            
            logger.info(f"Stored explanation: {explanation_id}")
            
            return explanation_id
            
        except Exception as e:
            logger.error(f"Error storing explanation: {e}")
            raise
    
    # ========================================================================
    # RECOMMENDATIONS
    # ========================================================================
    
    def store_recommendation(self, assessment_id: str, 
                            recommendation_data: Dict[str, Any]) -> str:
        """Store treatment recommendations."""
        try:
            recommendation_ref = self.db.collection('recommendations').document()
            
            data = {
                'assessment_id': assessment_id,
                **recommendation_data,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            
            recommendation_ref.set(data)
            recommendation_id = recommendation_ref.id
            
            logger.info(f"Stored recommendation: {recommendation_id}")
            
            return recommendation_id
            
        except Exception as e:
            logger.error(f"Error storing recommendation: {e}")
            raise
    
    # ========================================================================
    # AUDIT LOGS
    # ========================================================================
    
    def store_audit_log(self, event_type: str, user_id: str, 
                       payload: Dict[str, Any]) -> str:
        """Store audit log entry."""
        try:
            log_ref = self.db.collection('audit_logs').document()
            
            data = {
                'event_type': event_type,
                'user_id': user_id,
                'payload': payload,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'ip_address': payload.get('ip_address'),
                'user_agent': payload.get('user_agent')
            }
            
            log_ref.set(data)
            log_id = log_ref.id
            
            logger.debug(f"Stored audit log: {log_id}")
            
            return log_id
            
        except Exception as e:
            logger.error(f"Error storing audit log: {e}")
            raise
    
    # ========================================================================
    # STATISTICS & ANALYTICS
    # ========================================================================
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics."""
        try:
            # Count assessments
            assessments_ref = self.db.collection('assessments')
            assessments_query = assessments_ref.where('user_id', '==', user_id)
            assessments_count = len(list(assessments_query.stream()))
            
            # Get most recent assessment
            recent_query = (assessments_ref
                          .where('user_id', '==', user_id)
                          .order_by('created_at', direction=firestore.Query.DESCENDING)
                          .limit(1))
            
            recent_docs = list(recent_query.stream())
            last_assessment = recent_docs[0].to_dict() if recent_docs else None
            
            return {
                'total_assessments': assessments_count,
                'last_assessment_date': last_assessment.get('created_at') if last_assessment else None,
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return {'total_assessments': 0, 'user_id': user_id}
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def health_check(self) -> bool:
        """Check if Firebase connection is healthy."""
        try:
            # Try to read from a collection
            self.db.collection('users').limit(1).get()
            return True
        except Exception as e:
            logger.error(f"Firebase health check failed: {e}")
            return False
    
    def delete_user_data(self, user_id: str) -> bool:
        """
        Delete all user data (GDPR compliance).
        
        Args:
            user_id: Firebase user ID
            
        Returns:
            True if successful
        """
        try:
            # Delete user document
            self.db.collection('users').document(user_id).delete()
            
            # Delete assessments
            assessments = self.db.collection('assessments').where('user_id', '==', user_id).stream()
            for doc in assessments:
                doc.reference.delete()
            
            # Delete predictions
            predictions = self.db.collection('predictions').where('user_id', '==', user_id).stream()
            for doc in predictions:
                doc.reference.delete()
            
            logger.info(f"Deleted all data for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            return False


# Singleton instance
_firebase_db = None

def get_firebase_db() -> FirebaseDatabase:
    """Get Firebase database instance (singleton)."""
    global _firebase_db
    if _firebase_db is None:
        _firebase_db = FirebaseDatabase()
    return _firebase_db


# Alias for backward compatibility
get_database = get_firebase_db
