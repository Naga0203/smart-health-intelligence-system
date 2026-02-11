"""
Multi-Disease Predictor for AI Health Intelligence System

This predictor works with a single model trained on 715 diseases.
Supports both scikit-learn and PyTorch models.

Validates: Requirements 3.1, 3.2, 3.3
"""

import numpy as np
import pandas as pd
import joblib
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

logger = logging.getLogger('health_ai.multi_disease_predictor')

# Try to import PyTorch
try:
    import torch
    import torch.nn as nn
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    logger.warning("PyTorch not available. Only scikit-learn models will be supported.")


class MultiDiseasePredictor:
    """
    Predictor for a single model trained on multiple diseases (715 diseases).
    
    Supports:
    - PyTorch models (.pt, .pth files)
    - Scikit-learn models (.pkl, .joblib files)
    """
    
    def __init__(self, model_path: str = None, config_path: str = None):
        """
        Initialize the multi-disease predictor.
        
        Args:
            model_path: Path to the trained model file (.pt, .pth, .pkl, or .joblib)
            config_path: Path to dataset configuration JSON
        """
        self.model_path = model_path or 'models/multi_disease_model.pt'
        self.config_path = config_path or 'config/dataset_config.json'
        
        self.model = None
        self.model_type = None  # 'pytorch' or 'sklearn'
        self.config = None
        self.features = []
        self.diseases = []
        self.model_version = "1.0"
        self.device = None
        
        # Set device for PyTorch
        if PYTORCH_AVAILABLE:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            logger.info(f"PyTorch device: {self.device}")
        
        self._load_config()
        self._load_model()
        
        logger.info(f"MultiDiseasePredictor initialized with {len(self.diseases)} diseases")
        logger.info(f"Model type: {self.model_type}")
    
    def _load_config(self):
        """Load dataset configuration."""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            logger.warning(f"Config file not found: {config_file}")
            logger.warning("Using default configuration")
            self.config = self._get_default_config()
            return
        
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
            
            self.features = self.config['features']['all_features']
            self.diseases = self.config['diseases']
            
            logger.info(f"Loaded config: {len(self.features)} features, {len(self.diseases)} diseases")
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = self._get_default_config()
    
    def _load_model(self):
        """Load the trained model (PyTorch or scikit-learn)."""
        model_file = Path(self.model_path)
        
        if not model_file.exists():
            logger.warning(f"Model file not found: {model_file}")
            logger.warning("Using mock model for testing")
            self.model = None
            self.model_type = 'mock'
            return
        
        try:
            # Determine model type by extension
            extension = model_file.suffix.lower()
            
            if extension in ['.pt', '.pth']:
                # PyTorch model
                if not PYTORCH_AVAILABLE:
                    raise ImportError("PyTorch is not installed. Install with: pip install torch")
                
                self.model = torch.load(model_file, map_location=self.device)
                self.model.eval()  # Set to evaluation mode
                self.model_type = 'pytorch'
                logger.info(f"PyTorch model loaded successfully from: {model_file}")
                
            elif extension in ['.pkl', '.joblib']:
                # Scikit-learn model
                self.model = joblib.load(model_file)
                self.model_type = 'sklearn'
                logger.info(f"Scikit-learn model loaded successfully from: {model_file}")
                
            else:
                raise ValueError(f"Unsupported model file extension: {extension}")
            
            # Try to get model version if available
            if hasattr(self.model, 'version'):
                self.model_version = self.model.version
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
            self.model_type = 'mock'
    
    def predict(self, features: Dict[str, Any]) -> Tuple[str, float, Dict[str, Any]]:
        """
        Make prediction using the multi-disease model.
        
        Args:
            features: Dictionary of feature values
            
        Returns:
            Tuple of (predicted_disease, probability, metadata)
        """
        if self.model is None:
            logger.warning("Model not loaded, using mock prediction")
            return self._mock_predict(features)
        
        try:
            # Convert features dict to array
            feature_array = self._prepare_features(features)
            
            if self.model_type == 'pytorch':
                return self._predict_pytorch(feature_array)
            elif self.model_type == 'sklearn':
                return self._predict_sklearn(feature_array)
            else:
                return self._mock_predict(features)
                
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            import traceback
            traceback.print_exc()
            return self._mock_predict(features)
    
    def _predict_pytorch(self, feature_array: np.ndarray) -> Tuple[str, float, Dict[str, Any]]:
        """Make prediction using PyTorch model."""
        # Convert to PyTorch tensor
        x = torch.FloatTensor(feature_array).to(self.device)
        
        # Make prediction
        with torch.no_grad():
            outputs = self.model(x)
            
            # Apply softmax to get probabilities
            probabilities = torch.softmax(outputs, dim=1).cpu().numpy()[0]
        
        # Get top prediction
        top_idx = np.argmax(probabilities)
        predicted_disease = self.diseases[top_idx]
        probability = float(probabilities[top_idx])
        
        # Get top 5 predictions
        top_5_indices = np.argsort(probabilities)[-5:][::-1]
        top_5_predictions = [
            {
                'disease': self.diseases[idx],
                'probability': float(probabilities[idx])
            }
            for idx in top_5_indices
        ]
        
        metadata = {
            'model_version': self.model_version,
            'features_used': len(self.features),
            'total_diseases': len(self.diseases),
            'model_type': 'PyTorch',
            'device': str(self.device),
            'top_5_predictions': top_5_predictions
        }
        
        logger.info(f"PyTorch prediction: {predicted_disease} ({probability:.3f})")
        
        return predicted_disease, probability, metadata
    
    def _predict_sklearn(self, feature_array: np.ndarray) -> Tuple[str, float, Dict[str, Any]]:
        """Make prediction using scikit-learn model."""
        if hasattr(self.model, 'predict_proba'):
            # Get probabilities for all diseases
            probabilities = self.model.predict_proba(feature_array)[0]
            
            # Get top prediction
            top_idx = np.argmax(probabilities)
            predicted_disease = self.diseases[top_idx]
            probability = float(probabilities[top_idx])
            
            # Get top 5 predictions
            top_5_indices = np.argsort(probabilities)[-5:][::-1]
            top_5_predictions = [
                {
                    'disease': self.diseases[idx],
                    'probability': float(probabilities[idx])
                }
                for idx in top_5_indices
            ]
            
        else:
            # For models without predict_proba
            predicted_disease = self.model.predict(feature_array)[0]
            probability = 0.8  # Default confidence
            top_5_predictions = [{'disease': predicted_disease, 'probability': probability}]
        
        metadata = {
            'model_version': self.model_version,
            'features_used': len(self.features),
            'total_diseases': len(self.diseases),
            'model_type': type(self.model).__name__,
            'top_5_predictions': top_5_predictions
        }
        
        logger.info(f"Sklearn prediction: {predicted_disease} ({probability:.3f})")
        
        return predicted_disease, probability, metadata
    
    def predict_top_n(self, features: Dict[str, Any], n: int = 5) -> List[Dict[str, Any]]:
        """
        Get top N disease predictions.
        
        Args:
            features: Dictionary of feature values
            n: Number of top predictions to return
            
        Returns:
            List of dictionaries with disease and probability
        """
        if self.model is None or not hasattr(self.model, 'predict_proba'):
            disease, prob, _ = self._mock_predict(features)
            return [{'disease': disease, 'probability': prob}]
        
        try:
            feature_array = self._prepare_features(features)
            probabilities = self.model.predict_proba(feature_array)[0]
            
            # Get top N
            top_n_indices = np.argsort(probabilities)[-n:][::-1]
            top_n_predictions = [
                {
                    'disease': self.diseases[idx],
                    'probability': float(probabilities[idx]),
                    'rank': i + 1
                }
                for i, idx in enumerate(top_n_indices)
            ]
            
            return top_n_predictions
            
        except Exception as e:
            logger.error(f"Top-N prediction error: {e}")
            disease, prob, _ = self._mock_predict(features)
            return [{'disease': disease, 'probability': prob, 'rank': 1}]
    
    def _prepare_features(self, features: Dict[str, Any]) -> np.ndarray:
        """
        Prepare features for model input.
        
        Args:
            features: Dictionary of feature values
            
        Returns:
            NumPy array of features in correct order
        """
        # Create feature array in the correct order
        feature_values = []
        
        for feature_name in self.features:
            value = features.get(feature_name, 0)  # Default to 0 if missing
            
            # Handle different data types
            if isinstance(value, (int, float)):
                feature_values.append(float(value))
            elif isinstance(value, bool):
                feature_values.append(float(value))
            elif isinstance(value, str):
                # Try to convert string to number
                try:
                    feature_values.append(float(value))
                except ValueError:
                    # For categorical strings, use 0 as default
                    feature_values.append(0.0)
            else:
                feature_values.append(0.0)
        
        return np.array([feature_values])
    
    def _mock_predict(self, features: Dict[str, Any]) -> Tuple[str, float, Dict[str, Any]]:
        """Mock prediction for testing when model is not loaded."""
        # Simple mock: return a random disease with high probability
        if self.diseases:
            disease = self.diseases[0]  # Return first disease
        else:
            disease = "Unknown Disease"
        
        probability = 0.85
        
        metadata = {
            'model_version': 'mock',
            'features_used': len(features),
            'total_diseases': len(self.diseases),
            'model_type': 'MockModel',
            'note': 'Using mock prediction - real model not loaded'
        }
        
        logger.warning(f"Mock prediction: {disease} ({probability:.3f})")
        
        return disease, probability, metadata
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when config file is not available."""
        return {
            'dataset_info': {
                'total_rows': 0,
                'total_columns': 0,
                'target_column': 'prognosis',
                'num_diseases': 715,
                'num_features': 132
            },
            'features': {
                'all_features': [],
                'numeric_features': [],
                'binary_features': [],
                'categorical_features': []
            },
            'feature_details': {},
            'diseases': []
        }
    
    def get_supported_diseases(self) -> List[str]:
        """Get list of all supported diseases."""
        return self.diseases
    
    def get_feature_names(self) -> List[str]:
        """Get list of all feature names."""
        return self.features
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            'model_loaded': self.model is not None,
            'model_path': str(self.model_path),
            'model_version': self.model_version,
            'model_type': type(self.model).__name__ if self.model else 'None',
            'num_features': len(self.features),
            'num_diseases': len(self.diseases),
            'config_loaded': self.config is not None
        }
    
    def validate_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that all required features are present.
        
        Args:
            features: Dictionary of feature values
            
        Returns:
            Validation result with missing features
        """
        missing_features = [f for f in self.features if f not in features]
        present_features = [f for f in self.features if f in features]
        
        return {
            'valid': len(missing_features) == 0,
            'missing_features': missing_features,
            'present_features': present_features,
            'missing_count': len(missing_features),
            'present_count': len(present_features),
            'total_required': len(self.features)
        }


# Convenience function for quick predictions
def predict_disease(features: Dict[str, Any], 
                   model_path: str = None,
                   config_path: str = None) -> Dict[str, Any]:
    """
    Convenience function to make a disease prediction.
    
    Args:
        features: Dictionary of feature values
        model_path: Path to model file
        config_path: Path to config file
        
    Returns:
        Prediction result dictionary
    """
    predictor = MultiDiseasePredictor(model_path, config_path)
    disease, probability, metadata = predictor.predict(features)
    
    return {
        'predicted_disease': disease,
        'probability': probability,
        'probability_percent': round(probability * 100, 2),
        'metadata': metadata
    }


if __name__ == "__main__":
    # Example usage
    print("Multi-Disease Predictor Test")
    print("="*80)
    
    # Initialize predictor
    predictor = MultiDiseasePredictor()
    
    # Print model info
    info = predictor.get_model_info()
    print("\nModel Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Example prediction with mock features
    print("\nExample Prediction:")
    mock_features = {feature: 0 for feature in predictor.get_feature_names()}
    mock_features['itching'] = 1
    mock_features['skin_rash'] = 1
    mock_features['nodal_skin_eruptions'] = 1
    
    disease, prob, metadata = predictor.predict(mock_features)
    print(f"  Predicted Disease: {disease}")
    print(f"  Probability: {prob:.2%}")
    print(f"  Model Type: {metadata['model_type']}")
