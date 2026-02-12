"""
Text preprocessing utilities for symptom input.
"""
import re


def clean_text(text):
    """
    Clean and normalize input text.
    
    Args:
        text (str): Raw input text
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and extra whitespace
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def tokenize_text(text, vocabulary):
    """
    Convert text to token indices using vocabulary.
    
    Args:
        text (str): Cleaned input text
        vocabulary (dict): Word to index mapping
        
    Returns:
        list: List of token indices
    """
    words = text.split()
    return [vocabulary.get(word, vocabulary.get('<UNK>', 0)) for word in words]


def pad_sequence(tokens, max_length, pad_value=0):
    """
    Pad or truncate token sequence to fixed length.
    
    Args:
        tokens (list): List of token indices
        max_length (int): Target sequence length
        pad_value (int): Padding value
        
    Returns:
        list: Padded sequence
    """
    if len(tokens) > max_length:
        return tokens[:max_length]
    return tokens + [pad_value] * (max_length - len(tokens))
