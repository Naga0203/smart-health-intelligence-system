"""
MongoDB Database Connection Layer for AI Health Intelligence System

This module provides database connectivity and operations for storing
health assessments, predictions, and audit logs.

Validates: Requirements 7.2, 6.3
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from django.conf import settings

logger = logging.getLogger('health_ai.database')


class MongoDBConnection:
    """
    MongoDB connection manager for health intelligence system.
    
    Provides methods for storing and retrieving:
    - User symptoms and inputs
    - ML predictions and confidence scores
    - Agent explanations and recommendations
    - Audit logs for all operations
    """
    
    def __init__(self):
        """Initialize MongoDB connection."""
        self.client = None
        self.db = None
        self.collections = {}
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB."""
        try:
            mongo_uri = settings.MONGODB_SETTINGS['URI']
            db_name = settings.MONGODB_SETTINGS['DATABASE_NAME']
            
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            
            # Test connection
            self.client.admin.command('ping')
            
            self.db = self.client[db_name]
            
            # Initialize collections
            self.collections = {
                'symptoms': self.db['symptoms'],
                'predictions': self.db['predictions'],
                'explanations': self.db['explanations'],
                'recommendations': self.db['recommendations'],
                'audit_logs': self.db['audit_logs'],
                'user_sessions': self.db['user_sessions']
            }
            
            # Create indexes for better performance
            self._create_indexes()
            
            logger.info(f"MongoDB connected successfully to database: {db_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            self.client = None
            self.db = None
        except Exception as e:
            logger.error(f"MongoDB initialization error: {str(e)}")
            self.client = None
            self.db = None
    
    def _create_indexes(self):
        """Create indexes for collections."""
        try:
            # Symptoms collection indexes
            self.collections['symptoms'].create_index([('user_id', ASCENDING), ('timestamp', DESCENDING)])
            self.collections['symptoms'].create_index([('timestamp', DESCENDING)])
            
            # Predictions collection indexes
            self.collections['predictions'].create_index([('user_id', ASCENDING), ('timestamp', DESCENDING)])
            self.collections['predictions'].create_index([('disease', ASCENDING)])
            self.collections['predictions'].create_index([('confidence', ASCENDING)])
            
            # Audit logs indexes
            self.collections['audit_logs'].create_index([('event_type', ASCENDING), ('timestamp', DESCENDING)])
            self.collections['audit_logs'].create_index([('user_id', ASCENDING)])
            
            logger.info("MongoDB indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
    
    def store_symptom_input(self, user_id: str, symptoms: List[str], metadata: Dict[str, Any]) -> Optional[str]:
        """
        Store user symptom input.
        
        Args:
            user_id: User identifier
            symptoms: List of symptoms
            metadata: Additional metadata (age, gender, etc.)
            
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            document = {
                'user_id': user_id,
                'symptoms': symptoms,
                'metadata': metadata,
                'timestamp': datetime.utcnow(),
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.collections['symptoms'].insert_one(document)
            logger.info(f"Stored symptom input for user: {user_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing symptom input: {str(e)}")
            return None
    
    def store_prediction(self, user_id: str, symptom_id: str, disease: str, 
                        probability: float, confidence: str, model_version: str = "v1.0") -> Optional[str]:
        """
        Store ML prediction result.
        
        Args:
            user_id: User identifier
            symptom_id: Reference to symptom document
            disease: Predicted disease
            probability: Prediction probability
            confidence: Confidence level (LOW, MEDIUM, HIGH)
            model_version: ML model version used
            
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            document = {
                'user_id': user_id,
                'symptom_id': symptom_id,
                'disease': disease,
                'probability': probability,
                'confidence': confidence,
                'model_version': model_version,
                'timestamp': datetime.utcnow(),
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.collections['predictions'].insert_one(document)
            logger.info(f"Stored prediction for user: {user_id}, disease: {disease}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing prediction: {str(e)}")
            return None
    
    def store_explanation(self, prediction_id: str, explanation_data: Dict[str, Any]) -> Optional[str]:
        """
        Store explanation generated by ExplanationAgent.
        
        Args:
            prediction_id: Reference to prediction document
            explanation_data: Explanation data from agent
            
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            document = {
                'prediction_id': prediction_id,
                'explanation': explanation_data,
                'generated_by': explanation_data.get('generated_by', 'unknown'),
                'timestamp': datetime.utcnow(),
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.collections['explanations'].insert_one(document)
            logger.info(f"Stored explanation for prediction: {prediction_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing explanation: {str(e)}")
            return None
    
    def store_recommendation(self, prediction_id: str, recommendation_data: Dict[str, Any]) -> Optional[str]:
        """
        Store recommendation generated by RecommendationAgent.
        
        Args:
            prediction_id: Reference to prediction document
            recommendation_data: Recommendation data from agent
            
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            document = {
                'prediction_id': prediction_id,
                'recommendation': recommendation_data,
                'timestamp': datetime.utcnow(),
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.collections['recommendations'].insert_one(document)
            logger.info(f"Stored recommendation for prediction: {prediction_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing recommendation: {str(e)}")
            return None
    
    def store_audit_log(self, event_type: str, user_id: str, payload: Dict[str, Any], 
                       ip_address: Optional[str] = None) -> Optional[str]:
        """
        Store audit log entry.
        
        Args:
            event_type: Type of event (e.g., 'prediction_request', 'validation_failed')
            user_id: User identifier
            payload: Event payload data
            ip_address: User IP address
            
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            document = {
                'event_type': event_type,
                'user_id': user_id,
                'payload': payload,
                'ip_address': ip_address,
                'timestamp': datetime.utcnow(),
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.collections['audit_logs'].insert_one(document)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing audit log: {str(e)}")
            return None
    
    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get user's assessment history.
        
        Args:
            user_id: User identifier
            limit: Maximum number of records to return
            
        Returns:
            List of assessment records
        """
        try:
            predictions = list(
                self.collections['predictions']
                .find({'user_id': user_id})
                .sort('timestamp', DESCENDING)
                .limit(limit)
            )
            
            # Convert ObjectId to string for JSON serialization
            for pred in predictions:
                pred['_id'] = str(pred['_id'])
                if 'symptom_id' in pred:
                    pred['symptom_id'] = str(pred['symptom_id'])
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error retrieving user history: {str(e)}")
            return []
    
    def get_complete_assessment(self, prediction_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete assessment including prediction, explanation, and recommendation.
        
        Args:
            prediction_id: Prediction document ID
            
        Returns:
            Complete assessment data or None
        """
        try:
            from bson.objectid import ObjectId
            
            # Get prediction
            prediction = self.collections['predictions'].find_one({'_id': ObjectId(prediction_id)})
            if not prediction:
                return None
            
            # Get explanation
            explanation = self.collections['explanations'].find_one({'prediction_id': prediction_id})
            
            # Get recommendation
            recommendation = self.collections['recommendations'].find_one({'prediction_id': prediction_id})
            
            # Get original symptoms
            symptom_data = None
            if 'symptom_id' in prediction:
                symptom_data = self.collections['symptoms'].find_one({'_id': ObjectId(prediction['symptom_id'])})
            
            # Build complete assessment
            assessment = {
                'prediction': self._convert_objectid(prediction),
                'explanation': self._convert_objectid(explanation) if explanation else None,
                'recommendation': self._convert_objectid(recommendation) if recommendation else None,
                'symptoms': self._convert_objectid(symptom_data) if symptom_data else None
            }
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error retrieving complete assessment: {str(e)}")
            return None
    
    def _convert_objectid(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ObjectId fields to strings for JSON serialization."""
        if document:
            for key, value in document.items():
                if hasattr(value, '__class__') and value.__class__.__name__ == 'ObjectId':
                    document[key] = str(value)
        return document
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get system statistics.
        
        Returns:
            Dictionary with system statistics
        """
        try:
            stats = {
                'total_assessments': self.collections['predictions'].count_documents({}),
                'total_users': len(self.collections['predictions'].distinct('user_id')),
                'assessments_by_confidence': {},
                'assessments_by_disease': {},
                'recent_assessments': self.collections['predictions'].count_documents({
                    'timestamp': {'$gte': datetime.utcnow().replace(hour=0, minute=0, second=0)}
                })
            }
            
            # Count by confidence
            for confidence in ['LOW', 'MEDIUM', 'HIGH']:
                count = self.collections['predictions'].count_documents({'confidence': confidence})
                stats['assessments_by_confidence'][confidence] = count
            
            # Count by disease
            diseases = self.collections['predictions'].distinct('disease')
            for disease in diseases:
                count = self.collections['predictions'].count_documents({'disease': disease})
                stats['assessments_by_disease'][disease] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error retrieving statistics: {str(e)}")
            return {}
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global database instance
_db_instance = None

def get_database() -> MongoDBConnection:
    """Get or create database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = MongoDBConnection()
    return _db_instance