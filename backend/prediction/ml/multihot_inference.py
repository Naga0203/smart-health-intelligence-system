
"""
Inference logic for Symptom Classifier using Multihot Model.
Separates prediction logic from loading and model definition.
"""
import torch
import numpy as np
import logging
import re
from .multihot_loader import load_inference_components

logger = logging.getLogger(__name__)

def text_to_multihot(symptom_text, symptom_columns, normalized_symptoms):
    """
    Convert symptom text to multi-hot vector using exact symptom name matching

    Strategy:
    1. Normalize input text (lowercase, clean)
    2. Match normalized symptom names using CONTIGUOUS PHRASE matching
    3. Sort by phrase length (longest first) to avoid partial matches
    """
    # Normalize input text
    cleaned = symptom_text.lower()
    cleaned = re.sub(r'[^a-z0-9 ]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Create list of (index, normalized_phrase, original_col) sorted by phrase length DESC
    symptom_list = sorted(
        [(i, ns, sc) for i, (ns, sc) in enumerate(zip(normalized_symptoms, symptom_columns))],
        key=lambda x: len(x[1].split()),
        reverse=True
    )

    # Initialize multi-hot vector
    multihot = np.zeros(len(symptom_columns), dtype=np.float32)
    matched_phrases = []

    # Match longest phrases first to avoid partial matches
    for idx, norm_phrase, orig_col in symptom_list:
        # Check for contiguous phrase match
        if norm_phrase in cleaned:
            # Verify it's a whole phrase match (not substring of larger word)
            pattern = r'\b' + re.escape(norm_phrase) + r'\b'
            if re.search(pattern, cleaned):
                multihot[idx] = 1.0
                matched_phrases.append(orig_col)
                # Remove matched phrase to prevent overlapping matches
                cleaned = re.sub(pattern, '', cleaned, count=1)
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return multihot, matched_phrases

device = torch.device('cpu')

@torch.no_grad()
def predict_disease(symptoms_text, top_k=5, min_confidence=0.05):
    """
    Predict disease from symptom text using multi-hot vector conversion

    Args:
        symptoms_text: String of symptoms (e.g., "fever headache stiff neck")
        top_k: Number of top predictions to return
        min_confidence: Minimum probability threshold

    Returns:
        List of prediction dictionaries + matched symptoms
    """
    # Lazy load components (cache after first call)
    if not hasattr(predict_disease, 'components'):
        predict_disease.components = load_inference_components()

    model, label_encoder, symptom_columns, normalized_symptoms = predict_disease.components

    # Convert text to multi-hot vector
    multihot, matched_symptoms = text_to_multihot(
        symptoms_text,
        symptom_columns,
        normalized_symptoms
    )

    # Convert to tensor and predict
    input_tensor = torch.tensor(multihot, dtype=torch.float32).unsqueeze(0).to(device)
    logits = model(input_tensor)
    probs = torch.softmax(logits, dim=1).cpu().numpy()[0]

    # Get top-k predictions above confidence threshold
    top_indices = np.argsort(probs)[::-1]
    results = []

    for rank, idx in enumerate(top_indices, 1):
        prob = probs[idx]
        if prob < min_confidence or len(results) >= top_k:
            break

        results.append({
            'rank': rank,
            'disease': label_encoder.classes_[idx],
            'probability': float(prob),
            'confidence': 'HIGH' if prob > 0.7 else 'MEDIUM' if prob > 0.4 else 'LOW'
        })

    # Handle no predictions above threshold
    if not results:
        idx = np.argmax(probs)
        results.append({
            'rank': 1,
            'disease': label_encoder.classes_[idx],
            'probability': float(probs[idx]),
            'confidence': 'VERY LOW',
            'warning': 'Low confidence prediction - consult healthcare professional'
        })

    # Add metadata
    results[0]['matched_symptoms'] = matched_symptoms
    results[0]['total_symptoms_matched'] = len(matched_symptoms)
    results[0]['input_text'] = symptoms_text

    return results
