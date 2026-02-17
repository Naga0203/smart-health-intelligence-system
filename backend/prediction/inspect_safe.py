import torch
import os
import sys

assets_dir = r"d:\Major-Project\Major_project\Backend System\backend\prediction\assets"

def inspect_safe():
    filename = "tuned_multihot_full.pt"
    path = os.path.join(assets_dir, filename)
    print(f"--- Inspecting keys of {filename} ---")
    try:
        data = torch.load(path, map_location=torch.device('cpu'))
        if isinstance(data, dict):
            keys = sorted(list(data.keys()))
            for k in keys:
                print(f"Key: {k}")
                val = data[k]
                if isinstance(val, (list, tuple)):
                    print(f"  Type: {type(val)}, Length: {len(val)}")
                else:
                    print(f"  Type: {type(val)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_safe()
