
"""
Multihot Model and resource loader with singleton pattern.
Loads multihot model, label encoder, and normalized symptom features.
"""
import os
import re
import joblib
import torch
import numpy as np
from pathlib import Path
from .multihot_model import SymptomClassifier
import logging

logger = logging.getLogger(__name__)

# Singleton wrapper
class MultihotResources:
    _instance = None
    
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.symptom_columns = None
        self.normalized_symptoms = None

# Global instance
_resources = MultihotResources()

# Asset paths
ASSETS_DIR = Path(__file__).parent.parent / 'assets'
MODEL_CHECKPOINT_PATH = ASSETS_DIR / 'tuned_multihot_full.pt'
LABEL_ENCODER_PATH = ASSETS_DIR / 'label_encoder_multihot.pkl'

def _normalize_text(text):
    """Normalize text for matching: lowercase, remove special chars, clean spaces."""
    norm = text.replace('_', ' ').lower()
    norm = re.sub(r'[^a-z0-9 ]', '', norm)
    norm = re.sub(r'\s+', ' ', norm).strip()
    return norm

def load_inference_components():
    """
    Load all components required for inference (Singleton pattern).
    Returns:
        model, label_encoder, symptom_columns, normalized_symptoms
    """
    global _resources
    
    if _resources.model is not None:
        return _resources.model, _resources.label_encoder, _resources.symptom_columns, _resources.normalized_symptoms

    logger.info("Loading inference components...")
    try:
        device = torch.device('cpu') # Enforce CPU for backend stability
        
        if not MODEL_CHECKPOINT_PATH.exists():
            raise FileNotFoundError(f"Checkpoint not found: {MODEL_CHECKPOINT_PATH}")
            
        # 1. Load configuration and weights from full checkpoint
        checkpoint = torch.load(MODEL_CHECKPOINT_PATH, map_location=device)
        
        # 2. Rebuild model
        # Handle cases where keys might be slightly different or missing defaults
        model = SymptomClassifier(
            input_dim=checkpoint.get('input_dim', 377),
            num_classes=checkpoint.get('num_classes', 713),
            hidden_dims=checkpoint.get('hidden_dims', [512, 512, 256, 256]) # Default to user snippet if missing ?? actually checkpoint has it
        )
        
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            # Fallback if checkpoint IS the state dict (unlikely for _full.pt but possible)
            # But based on inspection, it has keys.
            pass
            
        model.to(device)
        model.eval()
        
        # 3. Load Label Encoder
        if not LABEL_ENCODER_PATH.exists():
             raise FileNotFoundError(f"Label encoder not found: {LABEL_ENCODER_PATH}")
        
        try:
            label_encoder = joblib.load(LABEL_ENCODER_PATH)
        except:
            # Fallback for joblib/pickle compatibility
            import pickle
            with open(LABEL_ENCODER_PATH, 'rb') as f:
                label_encoder = pickle.load(f)

        # 4. Process Symptom Columns
        symptom_columns = checkpoint.get('symptom_columns', [])
        if not symptom_columns and 'inference_package' in checkpoint:
             symptom_columns = checkpoint['inference_package'].get('symptom_columns', [])
             
        # Precompute normalized symptom names for matching
        normalized_symptoms = []
        for col in symptom_columns:
            norm = _normalize_text(col)
            normalized_symptoms.append(norm)

        # Update singleton
        _resources.model = model
        _resources.label_encoder = label_encoder
        _resources.symptom_columns = symptom_columns
        _resources.normalized_symptoms = normalized_symptoms
        
        logger.info("Inference components loaded successfully.")
        return model, label_encoder, symptom_columns, normalized_symptoms

    except Exception as e:
        logger.error(f"Failed to load inference components: {e}")
        raise
