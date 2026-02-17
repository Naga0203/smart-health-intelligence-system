import torch
import joblib
import pickle
import os

assets_dir = r"d:\Major-Project\Major_project\Backend System\backend\prediction\assets"

def desperate_load():
    filename = "label_encoder_multihot.pkl"
    path = os.path.join(assets_dir, filename)
    print(f"--- Desperate load of {filename} ---")
    
    # Try torch.load
    print("\nAttempting torch.load...")
    try:
        data = torch.load(path)
        print("Success with torch.load!")
        if hasattr(data, 'classes_'):
             print(f"Classes length: {len(data.classes_)}")
    except Exception as e:
        print(f"torch.load failed: {e}")

    # Try joblib with different settings
    print("\nAttempting joblib.load...")
    try:
        data = joblib.load(path)
        print("Success with joblib!")
        if hasattr(data, 'classes_'):
             print(f"Classes length: {len(data.classes_)}")
    except Exception as e:
        print(f"joblib failed: {e}")

    # Try pickle with protocol 5
    print("\nAttempting pickle load (explicit protocol)...")
    try:
        with open(path, 'rb') as f:
            # There is no option to force protocol read, it's auto-detected
            data = pickle.load(f)
            print("Success with pickle!")
    except Exception as e:
        print(f"pickle failed: {e}")

if __name__ == "__main__":
    desperate_load()
