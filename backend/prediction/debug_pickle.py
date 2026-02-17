import pickle
import sys
import os
import joblib

assets_dir = r"d:\Major-Project\Major_project\Backend System\backend\prediction\assets"
filename = "label_encoder_multihot.pkl"
path = os.path.join(assets_dir, filename)

print(f"--- Debugging {filename} ---")

# Check header
with open(path, 'rb') as f:
    header = f.read(10)
    print(f"Header (hex): {header.hex()}")
    print(f"Header (bytes): {header}")

# Try loading with pickle
print("\nAttempting pickle.load...")
try:
    with open(path, 'rb') as f:
        data = pickle.load(f)
        print("Success with pickle!")
        print(f"Type: {type(data)}")
except Exception as e:
    print(f"pickle.load failed: {e}")

# Try loading with joblib
print("\nAttempting joblib.load...")
try:
    data = joblib.load(path)
    print("Success with joblib!")
    print(f"Type: {type(data)}")
except Exception as e:
    print(f"joblib.load failed: {e}")

# Try to see if it's just a text file (git pointer?)
print("\nChecking if it's a text file...")
try:
    with open(path, 'r') as f:
        content = f.read(100)
        print(f"Content: {content}")
except Exception as e:
    print(f"Text read failed: {e}")
