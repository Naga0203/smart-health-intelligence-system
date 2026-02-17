import os
import sys
import django
import logging

# Setup Django environment
# Add both 'backend' and its parent to path to handle imports correctly
sys.path.append(r'd:\Major-Project\Major_project\Backend System')
sys.path.append(r'd:\Major-Project\Major_project\Backend System\backend')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_ai_backend.settings')
django.setup()

from prediction.ml.multihot_loader import MultihotLoader

def test_inference():
    print("--- Testing Symptom Prediction Inference ---")
    
    # Test cases
    test_cases = [
        ["fever", "cough", "headache"],
        ["anxiety_and_nervousness", "depression"],
        ["polyuria", "polydipsia"]
    ]
    
    for symptoms in test_cases:
        print(f"\nTesting symptoms: {symptoms}")
        try:
            result = MultihotLoader.predict(symptoms)
            if not result['top_prediction']:
                print("  No confident prediction.")
            else:
                tp = result['top_prediction']
                print(f"  Top Prediction: {tp['disease']} ({tp['confidence']:.4f})")
                print("  Other Predictions:")
                for p in result['predictions'][1:]: # Skip top
                     print(f"    - {p['disease']}: {p['confidence']:.4f}")
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_inference()
