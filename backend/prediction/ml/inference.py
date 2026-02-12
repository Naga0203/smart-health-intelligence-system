"""
Inference logic for disease prediction.
"""
import torch
from .preprocessing import clean_text, tokenize_text, pad_sequence
from .loader import get_model, get_vocabulary, get_label_encoder, get_max_seq_len


def predict_disease(symptoms_text):
    """
    Predict disease from symptom text.
    
    Args:
        symptoms_text (str): Raw symptom description
        
    Returns:
        dict: Prediction results with disease name and confidence
    """
    # Load model and resources
    model = get_model()
    vocabulary = get_vocabulary()
    label_encoder = get_label_encoder()
    max_seq_len = get_max_seq_len()
    
    # Preprocess input
    cleaned_text = clean_text(symptoms_text)
    tokens = tokenize_text(cleaned_text, vocabulary)
    padded_tokens = pad_sequence(tokens, max_seq_len)
    
    # Convert to tensor
    input_tensor = torch.tensor([padded_tokens], dtype=torch.long)
    
    # Predict
    model.eval()
    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.softmax(output, dim=1)
        confidence, predicted_idx = torch.max(probabilities, dim=1)
    
    # Decode prediction
    disease = label_encoder.inverse_transform([predicted_idx.item()])[0]
    
    return {
        'disease': disease,
        'confidence': confidence.item(),
        'probabilities': probabilities[0].tolist()
    }
