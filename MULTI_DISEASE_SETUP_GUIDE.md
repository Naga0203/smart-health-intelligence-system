## Multi-Disease Model Integration Guide

This guide explains how to integrate your single model trained on 715 diseases into the AI Health Intelligence System.

---

## Overview

Instead of using separate models for each disease, you'll use:
- **Single Model**: One model trained on 715 diseases
- **Automatic Feature Extraction**: Features extracted from your dataset
- **Unified Prediction**: One prediction call returns disease and probability

---

## Prerequisites

You should have:
1. ✅ A CSV dataset with symptoms/features and disease labels
2. ✅ A trained model file (`.pkl`, `.joblib`, or `.h5`)
3. ✅ Python environment with all dependencies installed

---

## Step-by-Step Integration

### Step 1: Prepare Your Files

Place your files in the project:

```
Backend System/
├── data/
│   └── disease_symptoms.csv          # Your dataset
├── models/
│   └── multi_disease_model.pkl       # Your trained model (you'll add this)
```

**Dataset Format Expected**:
- CSV file with headers
- One column for disease/prognosis (target)
- All other columns are features (symptoms)
- Binary features (0/1) or numeric values

**Example**:
```csv
itching,skin_rash,nodal_skin_eruptions,continuous_sneezing,...,prognosis
1,1,1,0,...,Fungal infection
0,0,0,1,...,Allergy
1,0,1,0,...,Drug Reaction
```

### Step 2: Run the Setup Script

The setup script will automatically:
- Analyze your dataset
- Extract all features
- Identify all 715 diseases
- Generate configuration files
- Update the system

**Command**:
```bash
python setup_multi_disease_model.py data/disease_symptoms.csv models/multi_disease_model.pkl
```

**What it does**:
1. Loads and analyzes your dataset
2. Extracts feature names and types
3. Identifies the target column (disease/prognosis)
4. Counts unique diseases
5. Generates `config/dataset_config.json`
6. Generates `config/dataset_report.txt`
7. Updates data extraction agent configuration
8. Updates orchestrator configuration

**Output**:
```
================================================================================
MULTI-DISEASE MODEL SETUP
================================================================================

[1/5] Analyzing dataset...
--------------------------------------------------------------------------------
✓ Dataset analyzed successfully
  - Rows: 4,920
  - Features: 132
  - Diseases: 715

[2/5] Saving configuration...
--------------------------------------------------------------------------------
✓ Configuration saved to: config/dataset_config.json
✓ Report saved to: config/dataset_report.txt

[3/5] Updating data extraction agent...
--------------------------------------------------------------------------------
✓ Data extraction agent updated
  - Features configured: 132

[4/5] Updating orchestrator...
--------------------------------------------------------------------------------
✓ Orchestrator updated to use multi-disease predictor

[5/5] Verifying model setup...
--------------------------------------------------------------------------------
✓ Model file found: models/multi_disease_model.pkl

================================================================================
SETUP COMPLETE!
================================================================================
```

### Step 3: Review Generated Files

**config/dataset_config.json** - Complete dataset configuration:
```json
{
  "dataset_info": {
    "total_rows": 4920,
    "total_columns": 133,
    "target_column": "prognosis",
    "num_diseases": 715,
    "num_features": 132
  },
  "features": {
    "all_features": ["itching", "skin_rash", "nodal_skin_eruptions", ...],
    "numeric_features": [...],
    "binary_features": [...],
    "categorical_features": [...]
  },
  "feature_details": {
    "itching": {
      "name": "itching",
      "dtype": "int64",
      "type": "binary",
      "values": [0, 1],
      ...
    },
    ...
  },
  "diseases": ["Fungal infection", "Allergy", "GERD", ...]
}
```

**config/dataset_report.txt** - Human-readable summary:
```
================================================================================
DATASET ANALYSIS REPORT
================================================================================

DATASET OVERVIEW
--------------------------------------------------------------------------------
Total Rows: 4,920
Total Columns: 133
Target Column: prognosis
Number of Diseases: 715
Number of Features: 132

FEATURE SUMMARY
--------------------------------------------------------------------------------
Numeric Features: 0
Binary Features: 132
Categorical Features: 0

FEATURE DETAILS
--------------------------------------------------------------------------------
itching:
  Type: binary
  Missing: 0 (0.0%)
  Unique Values: 2
  Values: [0, 1]
...
```

### Step 4: Update System Components

The system needs to be updated to use the multi-disease predictor. Here's what to modify:

#### A. Update `agents/orchestrator.py`

Replace the predictor initialization:

**Find this**:
```python
from prediction.predictor import DiseasePredictor

class OrchestratorAgent(BaseHealthAgent):
    def __init__(self):
        super().__init__("OrchestratorAgent")
        self.prediction_engine = DiseasePredictor()
```

**Replace with**:
```python
from prediction.multi_disease_predictor import MultiDiseasePredictor

class OrchestratorAgent(BaseHealthAgent):
    def __init__(self):
        super().__init__("OrchestratorAgent")
        self.prediction_engine = MultiDiseasePredictor()
```

#### B. Update `agents/data_extraction.py`

Load features from configuration:

**Add at the top of `__init__`**:
```python
def __init__(self):
    super().__init__("DataExtractionAgent")
    
    # Load features from configuration
    self._load_feature_config()
    
    # Rest of initialization...
```

**Add this method**:
```python
def _load_feature_config(self):
    """Load feature configuration from dataset config."""
    config_path = Path('config/dataset_config.json')
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update model features for multi-disease model
        self.model_features = {
            'multi_disease': config['features']['all_features']
        }
        
        logger.info(f"Loaded {len(config['features']['all_features'])} features from config")
    else:
        logger.warning("Dataset config not found, using default features")
```

#### C. Update orchestrator's `_select_disease` method

Since we now have a single model, we don't need disease selection:

**Replace the entire `_select_disease` method**:
```python
def _select_disease(self, symptoms: list) -> str:
    """
    For multi-disease model, we don't pre-select disease.
    The model will predict from all 715 diseases.
    
    Args:
        symptoms: List of symptoms (not used for multi-disease)
        
    Returns:
        Always returns 'multi_disease' to indicate unified prediction
    """
    return 'multi_disease'
```

#### D. Update orchestrator's prediction call

**Find this**:
```python
probability, prediction_metadata = self.prediction_engine.predict(disease, extracted_features)
```

**Replace with**:
```python
# For multi-disease model, predict returns (disease, probability, metadata)
disease, probability, prediction_metadata = self.prediction_engine.predict(extracted_features)
```

### Step 5: Test the Integration

Create a test script to verify everything works:

```bash
python test_multi_disease.py
```

**test_multi_disease.py**:
```python
from prediction.multi_disease_predictor import MultiDiseasePredictor

# Initialize predictor
predictor = MultiDiseasePredictor()

# Print model info
info = predictor.get_model_info()
print("Model Info:")
for key, value in info.items():
    print(f"  {key}: {value}")

# Test prediction
features = {feature: 0 for feature in predictor.get_feature_names()}
features['itching'] = 1
features['skin_rash'] = 1
features['nodal_skin_eruptions'] = 1

disease, prob, metadata = predictor.predict(features)
print(f"\nPrediction:")
print(f"  Disease: {disease}")
print(f"  Probability: {prob:.2%}")

# Get top 5 predictions
top_5 = predictor.predict_top_n(features, n=5)
print(f"\nTop 5 Predictions:")
for pred in top_5:
    print(f"  {pred['rank']}. {pred['disease']}: {pred['probability']:.2%}")
```

### Step 6: Run Full System Tests

Test the complete pipeline:

```bash
# Test with API keys
python test_with_api_keys.py

# Test various scenarios
python test_scenarios.py
```

---

## Configuration Files Reference

### dataset_config.json

Contains complete dataset information:
- `dataset_info`: Rows, columns, target column, disease count
- `features`: Lists of all features by type
- `feature_details`: Detailed info for each feature
- `diseases`: Complete list of all 715 diseases

### agent_config.json

Contains agent-specific configuration:
- `model_features`: Features for multi-disease model
- `feature_types`: Features grouped by type
- `diseases`: Disease list

### orchestrator_config.json

Contains orchestrator settings:
- `predictor_type`: Set to 'multi_disease'
- `model_path`: Path to model file
- `config_path`: Path to dataset config
- `confidence_thresholds`: LOW/MEDIUM/HIGH thresholds

---

## Feature Extraction

The data extraction agent will now:

1. **Load all 132 features** from your dataset configuration
2. **Map user symptoms** to these features using Gemini AI
3. **Create feature vector** with all 132 values (0 or 1 for binary)
4. **Pass to model** for prediction across all 715 diseases

**Example Flow**:
```
User Input: "I have itching and skin rash"
    ↓
Gemini AI extracts: ["itching", "skin_rash"]
    ↓
Feature Vector: [1, 1, 0, 0, 0, ..., 0]  (132 features)
    ↓
Model predicts from 715 diseases
    ↓
Top prediction: "Fungal infection" (85% probability)
```

---

## Model Requirements

Your trained model should:

1. **Accept**: NumPy array of shape `(1, 132)` with feature values
2. **Return**: 
   - For classification: `predict_proba()` returning probabilities for all 715 diseases
   - For regression: `predict()` returning disease index or name
3. **Format**: Saved as `.pkl` or `.joblib` file using scikit-learn's joblib

**Example model training**:
```python
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier

# Load data
data = pd.read_csv('disease_symptoms.csv')
X = data.drop('prognosis', axis=1)
y = data['prognosis']

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model
joblib.dump(model, 'models/multi_disease_model.pkl')

print(f"Model trained on {len(X.columns)} features")
print(f"Predicting {len(y.unique())} diseases")
```

---

## Troubleshooting

### Issue: "Config file not found"
**Solution**: Run `python setup_multi_disease_model.py <dataset_path>` first

### Issue: "Model file not found"
**Solution**: Place your trained model at `models/multi_disease_model.pkl`

### Issue: "Feature mismatch"
**Solution**: Ensure your model was trained on the same features in the dataset

### Issue: "Target column not found"
**Solution**: Specify target column: `python setup_multi_disease_model.py data.csv --target prognosis`

---

## Benefits of Multi-Disease Approach

✅ **Single Model**: One model handles all 715 diseases  
✅ **Automatic Feature Extraction**: No manual feature mapping needed  
✅ **Top-N Predictions**: Get top 5 most likely diseases  
✅ **Scalable**: Easy to add more diseases by retraining  
✅ **Consistent**: Same prediction logic for all diseases  
✅ **Efficient**: One prediction call instead of multiple  

---

## Next Steps

After successful integration:

1. ✅ Test with various symptom combinations
2. ✅ Validate predictions against known cases
3. ✅ Adjust confidence thresholds if needed
4. ✅ Build frontend to display top predictions
5. ✅ Deploy to production

---

**Status**: Ready for your dataset and model  
**Supported**: 715 diseases, 132 features  
**Framework**: Django + Gemini AI + scikit-learn
