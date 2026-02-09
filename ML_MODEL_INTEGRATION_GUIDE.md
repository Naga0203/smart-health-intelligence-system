# ML Model Integration Guide

This guide explains how to integrate your trained ML models into the AI Health Intelligence System.

---

## Current Status

✅ **System is working with mock models**  
⏳ **Waiting for real trained models to be uploaded**

The mock models currently return a fixed 95% probability for all predictions. Once you upload your real models, the system will provide accurate risk assessments based on actual patient data.

---

## Step-by-Step Integration

### Step 1: Prepare Your Models

Your trained models should be saved in a format that can be loaded by Python. Common formats:

- **Scikit-learn models**: `.pkl` or `.joblib` files
- **TensorFlow/Keras models**: `.h5` or SavedModel format
- **PyTorch models**: `.pt` or `.pth` files

**Example: Saving a scikit-learn model**
```python
import joblib
from sklearn.ensemble import RandomForestClassifier

# After training your model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, 'diabetes_model.pkl')
```

### Step 2: Create Models Directory

Create a `models/` directory in your project root:

```bash
mkdir models
```

### Step 3: Upload Your Models

Place your trained models in the `models/` directory with these names:

```
models/
├── diabetes_model.pkl          # Diabetes prediction model
├── heart_disease_model.pkl     # Heart disease prediction model
└── hypertension_model.pkl      # Hypertension prediction model
```

**Optional**: Also save feature names and model metadata:
```
models/
├── diabetes_model.pkl
├── diabetes_features.json      # List of feature names
├── diabetes_metadata.json      # Model version, accuracy, etc.
├── heart_disease_model.pkl
├── heart_disease_features.json
├── heart_disease_metadata.json
├── hypertension_model.pkl
├── hypertension_features.json
└── hypertension_metadata.json
```

### Step 4: Update the Predictor

Modify `prediction/predictor.py` to load your real models instead of mock models.

**Current code (mock models)**:
```python
def _load_models(self):
    """Load ML models for disease prediction."""
    # Mock models for testing
    self.models = {
        "diabetes": MockDiabetesModel(),
        "heart_disease": MockHeartDiseaseModel(),
        "hypertension": MockHypertensionModel()
    }
```

**Updated code (real models)**:
```python
import joblib
from pathlib import Path

def _load_models(self):
    """Load ML models for disease prediction."""
    models_dir = Path(__file__).parent.parent / 'models'
    
    try:
        self.models = {
            "diabetes": joblib.load(models_dir / 'diabetes_model.pkl'),
            "heart_disease": joblib.load(models_dir / 'heart_disease_model.pkl'),
            "hypertension": joblib.load(models_dir / 'hypertension_model.pkl')
        }
        logger.info(f"Loaded {len(self.models)} real ML models")
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {e}")
        # Fallback to mock models
        self.models = {
            "diabetes": MockDiabetesModel(),
            "heart_disease": MockHeartDiseaseModel(),
            "hypertension": MockHypertensionModel()
        }
        logger.warning("Using mock models as fallback")
```

### Step 5: Update Feature Extraction

Ensure your feature extraction matches your model's expected input.

**Check your model's expected features**:
```python
# In data_extraction.py, update model_features to match your trained models
self.model_features = {
    "diabetes": [
        # List the exact features your diabetes model expects
        "age", "gender", "bmi", "glucose", "insulin", ...
    ],
    "heart_disease": [
        # List the exact features your heart disease model expects
        "age", "gender", "chest_pain_type", "blood_pressure", ...
    ],
    "hypertension": [
        # List the exact features your hypertension model expects
        "age", "gender", "systolic_bp", "diastolic_bp", ...
    ]
}
```

### Step 6: Update Prediction Logic

Modify the prediction method to work with your real models:

```python
def predict(self, disease: str, features: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    Make prediction using real ML model.
    
    Args:
        disease: Disease to predict
        features: Dictionary of features
        
    Returns:
        Tuple of (probability, metadata)
    """
    if disease not in self.models:
        raise ValueError(f"Unknown disease: {disease}")
    
    model = self.models[disease]
    
    # Convert features dict to array in correct order
    feature_names = self.model_features[disease]
    feature_array = np.array([[features.get(f, 0) for f in feature_names]])
    
    # Get prediction probability
    if hasattr(model, 'predict_proba'):
        # For classification models
        probability = model.predict_proba(feature_array)[0][1]  # Probability of positive class
    else:
        # For regression models
        probability = model.predict(feature_array)[0]
    
    # Ensure probability is between 0 and 1
    probability = np.clip(probability, 0.0, 1.0)
    
    metadata = {
        "model_version": self.model_version,
        "features_used": len(feature_names),
        "model_type": type(model).__name__
    }
    
    logger.info(f"Prediction completed: {disease} = {probability:.3f}")
    
    return float(probability), metadata
```

### Step 7: Test Your Models

Run the test suite to ensure everything works:

```bash
# Test with real models
py test_with_api_keys.py

# Test various scenarios
py test_scenarios.py
```

---

## Model Requirements

### Input Format
Your models should accept:
- **Input**: NumPy array or pandas DataFrame
- **Shape**: (n_samples, n_features)
- **Features**: Numeric values (categorical features should be encoded)

### Output Format
Your models should return:
- **Classification**: Probability between 0 and 1
- **Method**: `predict_proba()` for classification, `predict()` for regression

### Feature Engineering
Ensure your features match what the model was trained on:
- Same feature names
- Same feature order
- Same encoding (one-hot, label encoding, etc.)
- Same scaling (if applicable)

---

## Example: Complete Integration

Here's a complete example of integrating a diabetes model:

**1. Train and save your model**:
```python
# train_diabetes_model.py
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Load your training data
data = pd.read_csv('diabetes_data.csv')
X = data.drop('diabetes', axis=1)
y = data['diabetes']

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model and feature names
joblib.dump(model, 'models/diabetes_model.pkl')
joblib.dump(list(X.columns), 'models/diabetes_features.pkl')

print(f"Model trained with accuracy: {model.score(X, y):.2f}")
print(f"Features: {list(X.columns)}")
```

**2. Update predictor.py**:
```python
# prediction/predictor.py
import joblib
from pathlib import Path

class DiseasePredictor:
    def __init__(self):
        self.models_dir = Path(__file__).parent.parent / 'models'
        self.models = {}
        self.feature_names = {}
        self._load_models()
    
    def _load_models(self):
        """Load real ML models."""
        diseases = ['diabetes', 'heart_disease', 'hypertension']
        
        for disease in diseases:
            model_path = self.models_dir / f'{disease}_model.pkl'
            features_path = self.models_dir / f'{disease}_features.pkl'
            
            if model_path.exists():
                self.models[disease] = joblib.load(model_path)
                if features_path.exists():
                    self.feature_names[disease] = joblib.load(features_path)
                logger.info(f"Loaded {disease} model")
            else:
                logger.warning(f"Model not found: {model_path}")
```

**3. Test the integration**:
```bash
py test_with_api_keys.py
```

---

## Troubleshooting

### Issue: Model file not found
**Error**: `FileNotFoundError: [Errno 2] No such file or directory: 'models/diabetes_model.pkl'`

**Solution**:
1. Ensure `models/` directory exists
2. Check model file names match exactly
3. Verify file paths are correct

### Issue: Feature mismatch
**Error**: `ValueError: X has 10 features, but RandomForestClassifier is expecting 15 features`

**Solution**:
1. Check feature names in `data_extraction.py` match your training data
2. Ensure all features are being extracted
3. Verify feature order matches training data

### Issue: Prediction out of range
**Error**: Probability > 1.0 or < 0.0

**Solution**:
1. Use `predict_proba()` for classification models
2. Add `np.clip(probability, 0.0, 1.0)` to ensure valid range
3. Check if model output needs transformation

### Issue: Low accuracy
**Problem**: Model predictions don't match expected results

**Solution**:
1. Verify feature extraction is correct
2. Check if features need scaling/normalization
3. Ensure categorical features are encoded properly
4. Validate model was trained correctly

---

## Model Performance Monitoring

After integration, monitor your models:

### 1. Log Predictions
```python
logger.info(f"Prediction: {disease} = {probability:.3f} (confidence: {confidence})")
```

### 2. Track Accuracy
Store predictions and actual outcomes (if available) for later analysis.

### 3. Monitor Confidence Distribution
Check if confidence levels (HIGH/MEDIUM/LOW) are distributed appropriately.

### 4. Review Edge Cases
Pay attention to predictions with very high or very low probabilities.

---

## Best Practices

1. **Version Your Models**: Include version numbers in model filenames
   - `diabetes_model_v1.0.pkl`
   - `diabetes_model_v1.1.pkl`

2. **Save Model Metadata**: Store training accuracy, date, features used
   ```json
   {
     "version": "1.0",
     "accuracy": 0.92,
     "trained_date": "2026-02-09",
     "features": ["age", "bmi", "glucose", ...],
     "training_samples": 10000
   }
   ```

3. **Implement Fallbacks**: Always have a fallback if model loading fails

4. **Test Thoroughly**: Test with various input scenarios before production

5. **Monitor Performance**: Track prediction accuracy and model drift over time

---

## Next Steps After Integration

Once your models are integrated:

1. ✅ Run all tests to ensure everything works
2. ✅ Compare predictions with expected outcomes
3. ✅ Adjust confidence thresholds if needed
4. ✅ Update documentation with model details
5. ✅ Deploy to staging environment
6. ✅ Conduct user acceptance testing
7. ✅ Deploy to production

---

## Need Help?

If you encounter issues during integration:

1. Check the logs in `logs/health_ai.log`
2. Run tests with verbose logging: `py test_with_api_keys.py`
3. Review the error messages carefully
4. Ensure all dependencies are installed: `pip install -r requirements.txt`

---

**Current Status**: Ready for model upload  
**System**: Fully operational with mock models  
**Next Step**: Upload your trained models and update predictor.py
