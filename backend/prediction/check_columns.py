import joblib
import os

assets_dir = r"d:\Major-Project\Major_project\Backend System\backend\prediction\assets"
path = os.path.join(assets_dir, "inference_package_multihot.pkl")

try:
    pkg = joblib.load(path)
    cols = pkg.get('symptom_columns', [])
    print(f"Total columns: {len(cols)}")
    
    search_terms = ['polyuria', 'polydipsia', 'diabetes', 'fever']
    
    for term in search_terms:
        matches = [c for c in cols if term in c]
        print(f"Matches for '{term}': {matches}")
        
except Exception as e:
    print(f"Error: {e}")
