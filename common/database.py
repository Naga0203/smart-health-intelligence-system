"""
MongoDB Database Layer for AI Health Intelligence System

Handles all database operations including storage and retrieval of:
- User inputs
- Predictions
- Explanations
- Recommendations
- Audit logs

Validates: Requirements 6.3, 6.4, 7.2
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from django.conf import settings

logger = logging.getLogger('health_ai.database')


class HealthAIDatabase:
    """
    MongoDB database manager for Health AI system.
    
    Manages collections:
    - user_inputs: Raw user input data
    - predictions: ML model predictions
    - explanations: AI-generated explanations
    - recommendations: Treatment recommendations
    - audit_logs: Complete audit trail
    """
    
    def __init__(self):
        """Initialize MongoDB connection."""
        self.client = None
        self.db = None
        self.collections = {}
        self._connect()
    
    def _connect(self):
        """Establish MongoDB connection."""
        try:
            mongo_uri = settings.MONGODB_SETTINGS['URI']
            db_name = settings.MONGODB_SETTINGS['DATABASE_NAME']
            
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            
            # Test connection
            self.client.admin.command('ping')
            
            self.db = self.client[db_name]
            
            # Initialize collections
            self.collections = {
                'user_inputs': self.db['user_inputs'],
                'predictions': self.db['predictions'],
                'explanations': self.db['explanations'],
                'recommendations': self.db['recommendations'],
                'audit_logs': self.db['audit_logs']
            }
            
            # Create indexes
            self._create_indexes()
            
            logger.info(f"MongoDB connected successfully to database: {db_name}")
            
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {str(e