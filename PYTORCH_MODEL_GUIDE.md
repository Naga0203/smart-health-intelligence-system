# PyTorch Model Integration Guide

Complete guide for integrating your PyTorch model trained on 715 diseases.

---

## Prerequisites

✅ PyTorch model trained on 715 diseases  
✅ Dataset CSV with features and disease labels  
✅ Python environment with PyTorch installed  

---

## Step 1: Install PyTorch

```bash
# Install PyTorch (CPU version)
pip install torch torchvision

# Or install with CUDA support (GPU)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Update all requirements
pip install -r requirements.txt
```

---

## Step 2: Save Your PyTorch Model

Your PyTorch model should be saved in the correct format:

### Option A: Save Entire Model (Recommended)
```python
import torch

# After training your model
model = YourModelClass(input_size=132, num_classes=715)
# ... training code ...

# Save the entire model
torch.save(model, 'models/multi_disease_model.pt')
print("Model saved successfully!")
```

### Option B: Save State Dict
```python
import torch

# Save only the state dict
torch.save(model.state_dict(), 'models/multi_disease_model_state.pth')

# To load later, you'll need to define the model architecture first
```

### Model Requirements

Your PyTorch model should:
1. **Input**: Tensor of shape `(batch_size, num_features)` - e.g., `(1, 132)`
2. **Output**: Tensor of shape `(batch_size, num_classes)` - e.g., `(1, 715)`
3. **Output Type**: Raw logits (softmax will be applied automatically)

**Example Model Architecture**:
```python
import torch
import torch.nn as nn

class DiseaseClassifier(nn.Module):
    def __init__(self, input_size=132, num_classes=715):
        super(DiseaseClassifier, self).__init__()
        
        self.network = nn.Sequential(
            nn.Linear(input_size, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        return self.network(x)

# Create and train model
model = DiseaseClassifier(input_size=132, num_classes=715)

# After training, save it
torch.save(model, 'models/multi_disease_model.pt')
```

---

## Step 3: Prepare Your Dataset

Your dataset CSV should have:
- **Features**: All symptom columns (binary 0/1 or numeric)
- **Target**: One column with disease names

**Example**:
```csv
itching,skin_rash,nodal_skin_eruptions,continuous_sneezing,...,prognosis
1,1,1,0,...,Fungal infection
0,0,0,1,...,Allergy
1,0,1,0,...,Drug Reaction
```

---

## Step 4: Run Setup Script

```bash
python setup_multi_disease_model.py data/disease_symptoms.csv models/multi_disease_model.pt
```

This will:
- ✅ Analyze your dataset
- ✅ Extract 132 features (or your actual count)
- ✅ Extract 715 disease names
- ✅ Generate configuration files
- ✅ Update system components

---

## Step 5: Update System Files

### Update `agents/orchestrator.py`

**Line ~20** - Change import:
```python
from prediction.multi_disease_predictor import MultiDiseasePredictor
```

**Line ~50** - Change initialization:
```python
self.prediction_engine = MultiDiseasePredictor(
    model_path='models/multi_disease_model.pt',  # PyTorch model
    config_path='config/dataset_config.json'
)
```

**Line ~120** - Change prediction call:
```python
# Old (3 disease models):
# probability, prediction_metadata = self.prediction_engine.predict(disease, extracted_features)

# New (single multi-disease model):
disease, probability, prediction_metadata = self.prediction_engine.predict(extracted_features)
```

**Line ~230** - Update `_select_disease` method:
```python
def _select_disease(self, symptoms: list) -> str:
    """Multi-disease model predicts from all 715 diseases."""
    return 'multi_disease'
```

---

## Step 6: Test Your PyTorch Model

### Quick Test
```python
from prediction.multi_disease_predictor import MultiDiseasePredictor

# Initialize predictor
predictor = MultiDiseasePredictor(
    model_path='models/multi_disease_model.pt',
    config_path='config/dataset_config.json'
)

# Check model info
info = predictor.get_model_info()
print(f"Model Type: {info['model_type']}")  # Should show 'PyTorch'
print(f"Device: {info.get('device', 'N/A')}")  # Shows 'cuda' or 'cpu'
print(f"Features: {info['num_features']}")
print(f"Diseases: {info['num_diseases']}")

# Test prediction
features = {f: 0 for f in predictor.get_feature_names()}
features['itching'] = 1
features['skin_rash'] = 1
features['nodal_skin_eruptions'] = 1

disease, prob, metadata = predictor.predict(features)
print(f"\nPredicted Disease: {disease}")
print(f"Probability: {prob:.2%}")
print(f"Device Used: {metadata.get('device', 'N/A')}")

# Get top 5 predictions
top_5 = predictor.predict_top_n(features, n=5)
print("\nTop 5 Predictions:")
for pred in top_5:
    print(f"  {pred['rank']}. {pred['disease']}: {pred['probability']:.2%}")
```

### Full System Test
```bash
# Test complete pipeline
python test_with_api_keys.py

# Test various scenarios
python test_scenarios.py
```

---

## PyTorch-Specific Features

### GPU Acceleration

The predictor automatically uses GPU if available:

```python
# Check device
predictor = MultiDiseasePredictor()
info = predictor.get_model_info()
print(f"Using device: {info.get('device', 'cpu')}")

# Output:
# Using device: cuda  (if GPU available)
# Using device: cpu   (if no GPU)
```

### Model Evaluation Mode

The model is automatically set to evaluation mode:
```python
# This is done automatically in _load_model()
self.model.eval()  # Disables dropout, batch norm, etc.
```

### Batch Predictions

For multiple predictions at once:
```python
# Single prediction (current implementation)
disease, prob, meta = predictor.predict(features)

# For batch predictions, you can modify the predictor:
# feature_array shape: (batch_size, num_features)
```

---

## Model File Formats

The predictor supports:

| Format | Extension | Description |
|--------|-----------|-------------|
| **Full Model** | `.pt` | Complete model with architecture (recommended) |
| **State Dict** | `.pth` | Model weights only (requires architecture definition) |
| **Scikit-learn** | `.pkl`, `.joblib` | For comparison/fallback |

**Recommended**: Use `.pt` format with full model for simplicity.

---

## Common PyTorch Issues

### Issue 1: "PyTorch not installed"
```
ImportError: PyTorch is not installed
```

**Solution**:
```bash
pip install torch torchvision
```

### Issue 2: "CUDA out of memory"
```
RuntimeError: CUDA out of memory
```

**Solution**: Use CPU instead:
```python
# Force CPU usage
predictor = MultiDiseasePredictor()
predictor.device = torch.device('cpu')
```

### Issue 3: "Model architecture mismatch"
```
RuntimeError: Error loading state dict
```

**Solution**: Save the full model, not just state dict:
```python
# Save full model
torch.save(model, 'model.pt')

# Not just state dict
# torch.save(model.state_dict(), 'model.pth')  # Avoid this
```

### Issue 4: "Input size mismatch"
```
RuntimeError: mat1 and mat2 shapes cannot be multiplied
```

**Solution**: Ensure your model's input size matches your dataset features:
```python
# Check feature count
print(f"Dataset features: {len(predictor.get_feature_names())}")
print(f"Model expects: {model.network[0].in_features}")  # Should match
```

---

## Performance Optimization

### Use GPU for Faster Predictions
```python
# Automatic GPU detection
predictor = MultiDiseasePredictor()

# Check if using GPU
if predictor.device.type == 'cuda':
    print("✓ Using GPU acceleration")
else:
    print("Using CPU (slower)")
```

### Batch Processing
For multiple predictions, process in batches:
```python
# Process 32 predictions at once
batch_size = 32
features_batch = [features1, features2, ..., features32]

# Convert to tensor
x = torch.FloatTensor(features_batch).to(device)

# Single forward pass
with torch.no_grad():
    outputs = model(x)
    probabilities = torch.softmax(outputs, dim=1)
```

---

## Model Training Tips

### Recommended Architecture
```python
class DiseaseClassifier(nn.Module):
    def __init__(self, input_size=132, num_classes=715):
        super().__init__()
        
        self.network = nn.Sequential(
            # Input layer
            nn.Linear(input_size, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            # Hidden layers
            nn.Linear(256, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            # Output layer
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        return self.network(x)
```

### Training Loop
```python
import torch.optim as optim
from torch.utils.data import DataLoader

# Setup
model = DiseaseClassifier(input_size=132, num_classes=715)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training
for epoch in range(100):
    for batch_x, batch_y in train_loader:
        # Forward pass
        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
    print(f"Epoch {epoch+1}, Loss: {loss.item():.4f}")

# Save trained model
torch.save(model, 'models/multi_disease_model.pt')
```

---

## Verification Checklist

Before deploying:

- [ ] PyTorch installed (`pip install torch`)
- [ ] Model saved as `.pt` file
- [ ] Model file placed in `models/` directory
- [ ] Dataset analyzed with setup script
- [ ] Configuration files generated
- [ ] Orchestrator updated (3 lines)
- [ ] Test script runs successfully
- [ ] GPU detected (if available)
- [ ] Predictions return correct format
- [ ] Top-5 predictions working

---

## Example: Complete Integration

```python
# 1. Train your PyTorch model
model = DiseaseClassifier(input_size=132, num_classes=715)
# ... training code ...
torch.save(model, 'models/multi_disease_model.pt')

# 2. Run setup
# python setup_multi_disease_model.py data/symptoms.csv models/multi_disease_model.pt

# 3. Test integration
from prediction.multi_disease_predictor import MultiDiseasePredictor

predictor = MultiDiseasePredictor()
print(f"Model type: {predictor.model_type}")  # Should show 'pytorch'
print(f"Device: {predictor.device}")  # Shows cuda or cpu

# 4. Make prediction
features = {f: 0 for f in predictor.get_feature_names()}
features['itching'] = 1
features['fever'] = 1

disease, prob, meta = predictor.predict(features)
print(f"Predicted: {disease} ({prob:.1%})")
print(f"Top 5: {meta['top_5_predictions']}")
```

---

## Next Steps

1. ✅ Train your PyTorch model
2. ✅ Save model as `.pt` file
3. ✅ Run setup script
4. ✅ Update orchestrator
5. ✅ Test predictions
6. ✅ Deploy to production

Your PyTorch model is now fully integrated! 🚀

---

**Model Format**: PyTorch `.pt` file  
**Supported Devices**: CPU and CUDA GPU  
**Diseases**: 715 classes  
**Features**: 132 inputs (or your dataset size)
