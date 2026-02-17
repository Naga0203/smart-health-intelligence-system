import torch
import os
import pandas as pd
import pickle

assets_dir = r"d:\Major-Project\Major_project\Backend System\backend\prediction\assets"

def inspect_full_checkpoint_robust():
    filename = "tuned_multihot_full.pt"
    path = os.path.join(assets_dir, filename)
    print(f"--- Inspecting {filename} ---")
    try:
        data = torch.load(path, map_location=torch.device('cpu'))
        if isinstance(data, dict):
            for k in data.keys():
                val = data[k]
                if hasattr(val, '__len__'):
                     print(f"Key: {k}, Type: {type(val)}, Len: {len(val)}")
                else:
                     print(f"Key: {k}, Type: {type(val)}, Value: {val}")
                
                if k == 'classes':
                    print(f"  First 5 classes: {val[:5]}")
    except Exception as e:
        print(f"Error: {e}")

def try_pandas_load():
    filename = "label_encoder_multihot.pkl"
    path = os.path.join(assets_dir, filename)
    print(f"\n--- Trying pandas load for {filename} ---")
    try:
        data = pd.read_pickle(path)
        print("Success with pandas!")
        if hasattr(data, 'classes_'):
             print(f"Classes length: {len(data.classes_)}")
    except Exception as e:
        print(f"Pandas load failed: {e}")

if __name__ == "__main__":
    inspect_full_checkpoint_robust()
    try_pandas_load()
