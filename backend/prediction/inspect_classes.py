import pickle
import os

assets_dir = r"d:\Major-Project\Major_project\Backend System\backend\prediction\assets"

def inspect_inference_pkg():
    filename = "inference_package_multihot.pkl"
    path = os.path.join(assets_dir, filename)
    print(f"--- Inspecting {filename} for classes ---")
    try:
        with open(path, 'rb') as f:
            data = pickle.load(f)
            if isinstance(data, dict):
                print(f"Keys: {list(data.keys())}")
                for key, value in data.items():
                    if isinstance(value, list) and len(value) > 100: # Classes should be around 713
                        print(f"Key '{key}' has length {len(value)}")
                        print(f"First 5 items: {value[:5]}")
                    if key == 'model_config':
                        print(f"model_config: {value}")
    except Exception as e:
        print(f"Error: {e}")

def try_load_le():
    filename = "label_encoder_multihot.pkl"
    path = os.path.join(assets_dir, filename)
    print(f"--- Trying to load {filename} with encoding options ---")
    try:
        with open(path, 'rb') as f:
            data = pickle.load(f, encoding='latin1')
            print("Loaded with encoding='latin1'")
            if hasattr(data, 'classes_'):
                 print(f"Classes length: {len(data.classes_)}")
    except Exception as e:
        print(f"Failed with latin1: {e}")

if __name__ == "__main__":
    inspect_inference_pkg()
    try_load_le()
