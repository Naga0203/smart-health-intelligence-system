import pickle
import torch
import sys
import os

assets_dir = r"d:\Major-Project\Major_project\Backend System\backend\prediction\assets"

def inspect_pickle(filename):
    path = os.path.join(assets_dir, filename)
    print(f"--- Inspecting {filename} ---")
    try:
        with open(path, 'rb') as f:
            data = pickle.load(f)
            if isinstance(data, dict):
                print(f"Keys: {list(data.keys())}")
                if 'symptom_columns' in data:
                    print(f"symptom_columns length: {len(data['symptom_columns'])}")
                    # print first few to verify
                    print(f"First 5 symptoms: {data['symptom_columns'][:5]}")
                if 'model_config' in data:
                    print(f"model_config: {data['model_config']}")
            else:
                if hasattr(data, 'classes_'):
                    print(f"LabelEncoder classes length: {len(data.classes_)}")
                    print(f"First 5 classes: {data.classes_[:5]}")
                else:
                    print("Unknown data structure")
    except Exception as e:
        print(f"Error reading {filename}: {e}")
    print("\n")

if __name__ == "__main__":
    inspect_pickle("inference_package_multihot.pkl")
    inspect_pickle("label_encoder_multihot.pkl")
