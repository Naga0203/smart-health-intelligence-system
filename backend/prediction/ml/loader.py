"""
Model and resource loader with singleton pattern.
Loads model, vocabulary, label encoder, and max sequence length once.
"""
import os
import pickle
import torch
from pathlib import Path
from .model import SymptomClassifier


# Singleton instances
_model = None
_vocabulary = None
_label_encoder = None
_max_seq_len = None

# Asset paths
ASSETS_DIR = Path(__file__).parent.parent / 'assets'
MODEL_PATH = ASSETS_DIR / 'tuned_symptom_classifier_model.pth'
VOCAB_PATH = ASSETS_DIR / 'vocabulary.pkl'
LABEL_ENCODER_PATH = ASSETS_DIR / 'label_encoder.pkl'
MAX_SEQ_LEN_PATH = ASSETS_DIR / 'max_seq_len.pkl'


def get_model():
    """Load and return the trained model (singleton)."""
    global _model
    
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        
        # Load model checkpoint
        checkpoint = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
        
        # Initialize model with saved hyperparameters
        vocab_size = checkpoint.get('vocab_size', 10000)
        embedding_dim = checkpoint.get('embedding_dim', 128)
        hidden_dim = checkpoint.get('hidden_dim', 256)
        output_dim = checkpoint.get('output_dim', 41)
        
        _model = SymptomClassifier(vocab_size, embedding_dim, hidden_dim, output_dim)
        _model.load_state_dict(checkpoint['model_state_dict'])
        _model.eval()
    
    return _model


def get_vocabulary():
    """Load and return the vocabulary (singleton)."""
    global _vocabulary
    
    if _vocabulary is None:
        if not VOCAB_PATH.exists():
            raise FileNotFoundError(f"Vocabulary file not found: {VOCAB_PATH}")
        
        with open(VOCAB_PATH, 'rb') as f:
            _vocabulary = pickle.load(f)
    
    return _vocabulary


def get_label_encoder():
    """Load and return the label encoder (singleton)."""
    global _label_encoder
    
    if _label_encoder is None:
        if not LABEL_ENCODER_PATH.exists():
            raise FileNotFoundError(f"Label encoder file not found: {LABEL_ENCODER_PATH}")
        
        with open(LABEL_ENCODER_PATH, 'rb') as f:
            _label_encoder = pickle.load(f)
    
    return _label_encoder


def get_max_seq_len():
    """Load and return the max sequence length (singleton)."""
    global _max_seq_len
    
    if _max_seq_len is None:
        if not MAX_SEQ_LEN_PATH.exists():
            raise FileNotFoundError(f"Max sequence length file not found: {MAX_SEQ_LEN_PATH}")
        
        with open(MAX_SEQ_LEN_PATH, 'rb') as f:
            _max_seq_len = pickle.load(f)
    
    return _max_seq_len


def reset_cache():
    """Reset all cached resources (useful for testing)."""
    global _model, _vocabulary, _label_encoder, _max_seq_len
    _model = None
    _vocabulary = None
    _label_encoder = None
    _max_seq_len = None
