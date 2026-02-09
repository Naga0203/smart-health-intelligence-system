# Quick Start: Multi-Disease Model Integration

## 🚀 Quick Setup (3 Steps)

### Step 1: Place Your Files
```bash
# Place your dataset
cp your_dataset.csv data/disease_symptoms.csv

# Place your trained PyTorch model
cp your_model.pt models/multi_disease_model.pt

# Or scikit-learn model
cp your_model.pkl models/multi_disease_model.pkl
```

### Step 2: Run Setup Script
```bash
# For PyTorch model
python setup_multi_disease_model.py data/disease_symptoms.csv models/multi_disease_model.pt

# For scikit-learn model
python setup_multi_disease_model.py data/disease_symptoms.csv models/multi_disease_model.pkl
```

### Step 3: Update System Files

**Update `agents/orchestrator.py`** (Line ~20):
```python
# Change this:
from prediction.predictor import DiseasePredictor
self.prediction_engine = DiseasePredictor()

# To this:
from prediction.multi_disease_predictor import MultiDiseasePredictor
self.prediction_engine = MultiDiseasePredictor()
```

**Update prediction call** (Line ~120):
```python
# Change this:
probability, prediction_metadata = self.prediction_engine.predict(disease, extracted_features)

# To this:
disease, probability, prediction_metadata = self.prediction_engine.predict(extracted_features)
```

**Update `_select_disease` method** (Line ~230):
```python
def _select_disease(self, symptoms: list) -> str:
    """Multi-disease model predicts from all 715 diseases."""
    return 'multi_disease'
```

Done! 🎉

---

## 📁 What You Need

1. **Dataset CSV**: 
   - Columns: symptoms/features (binary 0/1 or numeric)
   - One column: disease/prognosis (target)
   - Example: `itching,skin_rash,fever,prognosis`

2. **Trained Model**:
   - **PyTorch**: `.pt` or `.pth` file (recommended)
   - **Scikit-learn**: `.pkl` or `.joblib` file
   - Must have 715 output classes (diseases)
   - Input size must match your dataset features

---

## 🧪 Test Your Setup

```bash
# Test the predictor
python -c "from prediction.multi_disease_predictor import MultiDiseasePredictor; p = MultiDiseasePredictor(); print(p.get_model_info())"

# Test full system
python test_with_api_keys.py

# Test scenarios
python test_scenarios.py
```

---

## 📊 What Gets Generated

After running setup:

```
config/
├── dataset_config.json       # Complete dataset configuration
├── dataset_report.txt         # Human-readable analysis
├── agent_config.json          # Agent configuration
└── orchestrator_config.json   # Orchestrator settings
```

---

## 🔍 Verify Everything Works

```python
from prediction.multi_disease_predictor import MultiDiseasePredictor

# Initialize
predictor = MultiDiseasePredictor(
    model_path='models/multi_disease_model.pt'  # or .pkl for sklearn
)

# Check status
info = predictor.get_model_info()
print(f"Model loaded: {info['model_loaded']}")
print(f"Model type: {info.get('model_type', 'N/A')}")  # 'pytorch' or 'sklearn'
print(f"Features: {info['num_features']}")
print(f"Diseases: {info['num_diseases']}")

# For PyTorch models, check device
if 'device' in info:
    print(f"Device: {info['device']}")  # 'cuda' or 'cpu'

# Test prediction
features = {f: 0 for f in predictor.get_feature_names()}
features['itching'] = 1
features['skin_rash'] = 1

disease, prob, meta = predictor.predict(features)
print(f"Predicted: {disease} ({prob:.1%})")
```

---

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| "Config file not found" | Run setup script first |
| "Model file not found" | Place model at `models/multi_disease_model.pkl` |
| "Feature mismatch" | Ensure model trained on same features as dataset |
| "Import error" | Run `pip install -r requirements.txt` |

---

## 📚 Full Documentation

- **PyTorch Models**: `PYTORCH_MODEL_GUIDE.md` ⭐ NEW!
- **Complete Guide**: `MULTI_DISEASE_SETUP_GUIDE.md`
- **Dataset Analyzer**: `utils/dataset_analyzer.py`
- **Predictor Code**: `prediction/multi_disease_predictor.py`
- **Setup Script**: `setup_multi_disease_model.py`

---

## 🎯 Expected Results

After setup, your system will:
- ✅ Accept user symptoms in natural language
- ✅ Extract features using Gemini AI
- ✅ Predict from all 715 diseases
- ✅ Return top disease with probability
- ✅ Provide top 5 predictions
- ✅ Generate explanations with Gemini AI
- ✅ Store results in MongoDB

---

## 💡 Tips

1. **Dataset Format**: Ensure your CSV has clear column names
2. **Target Column**: Name it 'prognosis', 'disease', or 'diagnosis'
3. **Binary Features**: Use 0/1 for symptoms (present/absent)
4. **Model Type**: RandomForest or similar classifiers work best
5. **Test First**: Always test with mock data before production

---

**Ready to integrate?** Follow the 3 steps above and you're done! 🚀
