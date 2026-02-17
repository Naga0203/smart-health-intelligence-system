import torch
import os

assets_dir = r"d:\Major-Project\Major_project\Backend System\backend\prediction\assets"

def inspect_full_checkpoint():
    filename = "tuned_multihot_full.pt"
    path = os.path.join(assets_dir, filename)
    print(f"--- Inspecting {filename} ---")
    try:
        data = torch.load(path, map_location=torch.device('cpu'))
        if isinstance(data, dict):
            print(f"Keys: {list(data.keys())}")
            if 'classes' in data:
                print(f"Found 'classes'! Length: {len(data['classes'])}")
                print(f"First 5 classes: {data['classes'][:5]}")
            if 'label_encoder' in data:
                print("Found 'label_encoder' object")
            if 'vocab' in data:
                print("Found 'vocab'")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_full_checkpoint()
