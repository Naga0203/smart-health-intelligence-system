"""
ML Prediction Engine for AI Health Intelligence System

This module provides disease prediction using machine learning models.
Currently uses mock models for development; can be replaced with trained models.

Validates: Requirements 7.3, 7.4
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
import numpy as np
from datetime import datetime

logger = logging.getLogger('health_ai.prediction')


class DiseasePredictor:
    """
    ML-based disease prediction engine.
    
    Key constraints:
    - Pure prediction only (no business logic)
    - No database access
    - No confidence evaluation (handled by agents)
    - Mathematical prediction only
    """
    
    def __init__(self):
        """Initialize the disease predictor with mock models."""
        self.models = {}
        self.model_version = "v1.0_mock"
        self._initialize_mock_models()
        logger.info("DiseasePredictor initialized with mock models")
    
    def _initialize_mock_models(self):
        """Initialize mock ML models for development."""
        # In production, these would be loaded from .pkl files
        # For now, we'll use rule-based mock models
        
        self.models = {
            "diabetes": MockDiabetesModel(),
            "heart_disease": MockHeartDiseaseModel(),
            "hypertension": MockHypertensionModel()
        }
        
        logger.info(f"Loaded {len(self.models)} mock models")
    
    def predict(self, disease: str, features: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Pure prediction method - no business logic.
        
        Args:
            disease: Disease to predict
            features: Feature dictionary from data extraction
            
        Returns:
            Tuple of (probability, metadata)
        """
        logger.info(f"Predicting {disease} with {len(features)} features")
        
        try:
            # Get the appropriate model
            model = self.models.get(disease)
            if not model:
                logger.error(f"No model found for disease: {disease}")
                return 0.5, {"error": "Model not found", "model_version": self.model_version}
            
            # Prepare features for the model
            feature_vector = self._prepare_features(features, disease)
            
            # Get prediction
            probability = model.predict_proba(feature_vector)
            
            # Prepare metadata
            metadata = {
                "model_version": self.model_version,
                "model_type": model.get_model_type(),
                "features_used": len(feature_vector),
                "prediction_timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Prediction completed: {disease} = {probability:.3f}")
            return probability, metadata
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return 0.5, {"error": str(e), "model_version": self.model_version}
    
    def _prepare_features(self, features: Dict[str, Any], disease: str) -> np.ndarray:
        """
        Convert feature dictionary to numpy array for model input.
        
        Args:
            features: Feature dictionary
            disease: Disease being predicted
            
        Returns:
            Numpy array of features
        """
        # Get expected feature order for the disease
        model = self.models.get(disease)
        if not model:
            return np.array([])
        
        expected_features = model.get_feature_names()
        
        # Build feature vector in correct order
        feature_vector = []
        for feature_name in expected_features:
            value = features.get(feature_name, 0)
            
            # Convert to numeric
            if isinstance(value, bool):
                value = 1 if value else 0
            elif isinstance(value, str):
                # Try to convert string to number
                try:
                    value = float(value)
                except ValueError:
                    value = 0
            
            feature_vector.append(value)
        
        return np.array(feature_vector)
    
    def get_supported_diseases(self) -> List[str]:
        """Get list of supported diseases."""
        return list(self.models.keys())
    
    def get_model_info(self, disease: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        model = self.models.get(disease)
        if not model:
            return {"error": "Model not found"}
        
        return {
            "disease": disease,
            "model_type": model.get_model_type(),
            "model_version": self.model_version,
            "features": model.get_feature_names(),
            "feature_count": len(model.get_feature_names())
        }


class MockDiabetesModel:
    """Mock diabetes prediction model."""
    
    def __init__(self):
        self.feature_names = [
            "age", "gender", "polyuria", "polydipsia", "sudden_weight_loss",
            "weakness", "polyphagia", "genital_thrush", "visual_blurring",
            "itching", "irritability", "delayed_healing", "partial_paresis",
            "muscle_stiffness", "alopecia", "obesity"
        ]
        
        # Feature weights for mock prediction
        self.weights = {
            "polyuria": 0.15,
            "polydipsia": 0.15,
            "sudden_weight_loss": 0.12,
            "weakness": 0.08,
            "polyphagia": 0.10,
            "visual_blurring": 0.10,
            "age": 0.05,
            "obesity": 0.08
        }
    
    def predict_proba(self, features: np.ndarray) -> float:
        """Mock prediction based on weighted features."""
        if len(features) == 0:
            return 0.5
        
        # Calculate weighted score
        score = 0.0
        for i, feature_name in enumerate(self.feature_names):
            if i < len(features):
                weight = self.weights.get(feature_name, 0.02)
                score += features[i] * weight
        
        # Add some randomness for realism
        noise = np.random.normal(0, 0.05)
        score = max(0.1, min(0.95, score + noise + 0.3))  # Clamp between 0.1 and 0.95
        
        return float(score)
    
    def get_model_type(self) -> str:
        return "MockRandomForest"
    
    def get_feature_names(self) -> List[str]:
        return self.feature_names


class MockHeartDiseaseModel:
    """Mock heart disease prediction model."""
    
    def __init__(self):
        self.feature_names = [
            "age", "gender", "chest_pain_type", "resting_blood_pressure",
            "cholesterol", "fasting_blood_sugar", "resting_ecg",
            "max_heart_rate", "exercise_angina", "oldpeak", "slope",
            "ca", "thal"
        ]
        
        self.weights = {
            "chest_pain_type": 0.18,
            "exercise_angina": 0.15,
            "oldpeak": 0.12,
            "ca": 0.12,
            "thal": 0.10,
            "age": 0.08,
            "max_heart_rate": 0.08
        }
    
    def predict_proba(self, features: np.ndarray) -> float:
        """Mock prediction based on weighted features."""
        if len(features) == 0:
            return 0.5
        
        score = 0.0
        for i, feature_name in enumerate(self.feature_names):
            if i < len(features):
                weight = self.weights.get(feature_name, 0.02)
                score += features[i] * weight
        
        noise = np.random.normal(0, 0.05)
        score = max(0.1, min(0.95, score + noise + 0.25))
        
        return float(score)
    
    def get_model_type(self) -> str:
        return "MockLogisticRegression"
    
    def get_feature_names(self) -> List[str]:
        return self.feature_names


class MockHypertensionModel:
    """Mock hypertension prediction model."""
    
    def __init__(self):
        self.feature_names = [
            "age", "gender", "systolic_bp", "diastolic_bp", "bmi",
            "smoking", "alcohol", "physical_activity", "stress_level",
            "family_history", "salt_intake", "sleep_hours"
        ]
        
        self.weights = {
            "systolic_bp": 0.20,
            "diastolic_bp": 0.18,
            "bmi": 0.12,
            "age": 0.10,
            "family_history": 0.10,
            "salt_intake": 0.08,
            "stress_level": 0.08
        }
    
    def predict_proba(self, features: np.ndarray) -> float:
        """Mock prediction based on weighted features."""
        if len(features) == 0:
            return 0.5
        
        score = 0.0
        for i, feature_name in enumerate(self.feature_names):
            if i < len(features):
                weight = self.weights.get(feature_name, 0.02)
                score += features[i] * weight
        
        noise = np.random.normal(0, 0.05)
        score = max(0.1, min(0.95, score + noise + 0.28))
        
        return float(score)
    
    def get_model_type(self) -> str:
        return "MockSVM"
    
    def get_feature_names(self) -> List[str]:
        return self.feature_names