# Machine Learning Architecture

## Overview

The SymptomSense Health AI system uses a PyTorch-based neural network for multi-label disease prediction. The ML module processes symptom data and predicts potential health conditions with confidence scores.

## ML Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ML PREDICTION PIPELINE                    │
└─────────────────────────────────────────────────────────────┘

Input: User Symptoms + Demographics
    │
    ▼
┌─────────────────────┐
│  Feature Extraction │
│  • Symptom parsing  │
│  • Demographics     │
│  • Medical history  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Preprocessing      │
│  • Normalization    │
│  • Multi-hot encode │
│  • Feature scaling  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Neural Network     │
│  • Input layer      │
│  • Hidden layers    │
│  • Output layer     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Post-processing    │
│  • Sigmoid          │
│  • Probability calc │
│  • Ranking          │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Confidence Scoring │
│  • Top-N selection  │
│  • Confidence calc  │
│  • Risk assessment  │
└──────┬──────────────┘
       │
       ▼
Output: Predictions + Confidence + Risk
```

## Neural Network Architecture

### Model Specification

**Type**: Multi-label Classification Neural Network  
**Framework**: PyTorch  
**Input**: Multi-hot encoded feature vector  
**Output**: Probability distribution over diseases

### Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NEURAL NETWORK LAYERS                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input Layer                                                │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Multi-hot Encoded Features                        │    │
│  │  Dimension: Variable (based on feature count)      │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                          │
│                   ▼                                          │
│  Hidden Layer 1                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Dense (Fully Connected)                           │    │
│  │  Neurons: 512                                      │    │
│  │  Activation: ReLU                                  │    │
│  │  Initialization: He Normal                         │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                          │
│                   ▼                                          │
│  Regularization 1                                           │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Dropout                                           │    │
│  │  Rate: 0.3 (30%)                                   │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                          │
│                   ▼                                          │
│  Hidden Layer 2                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Dense (Fully Connected)                           │    │
│  │  Neurons: 256                                      │    │
│  │  Activation: ReLU                                  │    │
│  │  Initialization: He Normal                         │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                          │
│                   ▼                                          │
│  Regularization 2                                           │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Dropout                                           │    │
│  │  Rate: 0.3 (30%)                                   │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                          │
│                   ▼                                          │
│  Hidden Layer 3                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Dense (Fully Connected)                           │    │
│  │  Neurons: 128                                      │    │
│  │  Activation: ReLU                                  │    │
│  │  Initialization: He Normal                         │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                          │
│                   ▼                                          │
│  Output Layer                                               │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Dense (Fully Connected)                           │    │
│  │  Neurons: N (number of diseases)                   │    │
│  │  Activation: Sigmoid                               │    │
│  │  Output: Probability per disease [0, 1]            │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Model Parameters

```python
Model Configuration:
{
    "input_dim": variable,  # Based on feature count
    "hidden_layers": [512, 256, 128],
    "output_dim": N,  # Number of diseases
    "dropout_rate": 0.3,
    "activation": "ReLU",
    "output_activation": "Sigmoid",
    "loss_function": "Binary Cross-Entropy",
    "optimizer": "Adam",
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 100
}
```

## Feature Engineering

### Multi-hot Encoding

**Purpose**: Convert categorical symptom data into numerical format

**Algorithm**:
```
FUNCTION multi_hot_encode(symptoms, feature_vocabulary):
    // Initialize zero vector
    encoded_vector = zeros(len(feature_vocabulary))
    
    // Set 1 for present symptoms
    FOR symptom IN symptoms:
        IF symptom IN feature_vocabulary:
            index = feature_vocabulary.index(symptom)
            encoded_vector[index] = 1
    
    RETURN encoded_vector
END FUNCTION
```

**Example**:
```
Input Symptoms: ["headache", "fever", "nausea"]
Feature Vocabulary: ["headache", "fever", "cough", "nausea", "fatigue"]

Encoded Vector: [1, 1, 0, 1, 0]
                 ↑  ↑     ↑
            headache fever nausea
```

### Feature Normalization

**Purpose**: Scale features to consistent range

**Methods**:
1. **Min-Max Scaling**: For continuous features (age, vitals)
   ```
   normalized_value = (value - min) / (max - min)
   ```

2. **Standard Scaling**: For normally distributed features
   ```
   normalized_value = (value - mean) / std_dev
   ```

3. **Binary Encoding**: For categorical features (gender, yes/no)
   ```
   male = 1, female = 0
   yes = 1, no = 0
   ```

## Training Process

### Training Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    TRAINING PIPELINE                         │
└─────────────────────────────────────────────────────────────┘

Dataset Collection
    │
    ▼
┌─────────────────────┐
│  Data Preprocessing │
│  • Cleaning         │
│  • Validation       │
│  • Augmentation     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Train/Val/Test     │
│  Split              │
│  • Train: 70%       │
│  • Validation: 15%  │
│  • Test: 15%        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Feature Engineering│
│  • Multi-hot encode │
│  • Normalization    │
│  • Feature selection│
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Model Training     │
│  • Forward pass     │
│  • Loss calculation │
│  • Backpropagation  │
│  • Weight update    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Validation         │
│  • Accuracy         │
│  • Precision/Recall │
│  • F1 Score         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Hyperparameter     │
│  Tuning             │
│  • Learning rate    │
│  • Batch size       │
│  • Dropout rate     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Model Evaluation   │
│  • Test set metrics │
│  • Confusion matrix │
│  • ROC curves       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Model Serialization│
│  • Save weights     │
│  • Save metadata    │
│  • Version control  │
└─────────────────────┘
```

### Loss Function

**Binary Cross-Entropy Loss** (for multi-label classification):

```
Loss = -1/N * Σ [y_i * log(ŷ_i) + (1 - y_i) * log(1 - ŷ_i)]

Where:
- N = number of samples
- y_i = true label (0 or 1)
- ŷ_i = predicted probability
```

### Optimization Algorithm

**Adam Optimizer**:
- Adaptive learning rate
- Momentum-based updates
- Efficient for large datasets

```
Parameters:
- Learning rate: 0.001
- Beta1: 0.9
- Beta2: 0.999
- Epsilon: 1e-8
```

## Inference Process

### Prediction Algorithm

```
FUNCTION predict(symptoms, demographics):
    // Step 1: Feature Extraction
    features = {
        "symptoms": symptoms,
        "age": demographics.age,
        "gender": demographics.gender,
        "medical_history": demographics.medical_history
    }
    
    // Step 2: Preprocessing
    encoded_symptoms = multi_hot_encode(
        symptoms, 
        feature_vocabulary
    )
    normalized_age = normalize_age(demographics.age)
    encoded_gender = encode_gender(demographics.gender)
    
    // Step 3: Combine Features
    feature_vector = concatenate([
        encoded_symptoms,
        normalized_age,
        encoded_gender
    ])
    
    // Step 4: Convert to Tensor
    input_tensor = torch.tensor(feature_vector).float()
    input_tensor = input_tensor.unsqueeze(0)  // Add batch dimension
    
    // Step 5: Model Inference
    model.eval()  // Set to evaluation mode
    WITH torch.no_grad():
        raw_output = model(input_tensor)
    
    // Step 6: Apply Sigmoid
    probabilities = torch.sigmoid(raw_output)
    
    // Step 7: Convert to Numpy
    probabilities = probabilities.squeeze().numpy()
    
    // Step 8: Create Disease-Probability Pairs
    predictions = []
    FOR i, disease IN enumerate(disease_labels):
        predictions.append({
            "disease": disease,
            "probability": probabilities[i],
            "confidence": calculate_confidence(probabilities[i])
        })
    
    // Step 9: Sort by Probability
    predictions.sort(key=lambda x: x["probability"], reverse=True)
    
    // Step 10: Return Top-N
    top_predictions = predictions[:5]
    
    RETURN {
        "predictions": top_predictions,
        "top_condition": top_predictions[0]["disease"],
        "probability": top_predictions[0]["probability"],
        "confidence": calculate_overall_confidence(top_predictions)
    }
END FUNCTION
```

### Confidence Scoring

**Algorithm**:
```
FUNCTION calculate_overall_confidence(predictions):
    top_prob = predictions[0].probability
    second_prob = predictions[1].probability
    
    // Measure 1: Absolute Confidence
    absolute_conf = top_prob
    
    // Measure 2: Separation Confidence
    separation = top_prob - second_prob
    separation_conf = min(separation * 2, 1.0)
    
    // Measure 3: Distribution Confidence
    total_prob = sum([p.probability for p in predictions])
    distribution_conf = top_prob / total_prob
    
    // Combined Confidence Score
    confidence = (
        0.5 * absolute_conf +
        0.3 * separation_conf +
        0.2 * distribution_conf
    )
    
    // Confidence Level
    IF confidence >= 0.8:
        level = "HIGH"
    ELSE IF confidence >= 0.6:
        level = "MEDIUM"
    ELSE:
        level = "LOW"
    
    RETURN {
        "score": confidence,
        "level": level,
        "absolute": absolute_conf,
        "separation": separation_conf,
        "distribution": distribution_conf
    }
END FUNCTION
```

## Model Evaluation Metrics

### Performance Metrics

1. **Accuracy**: Overall correctness
   ```
   Accuracy = (TP + TN) / (TP + TN + FP + FN)
   ```

2. **Precision**: Positive prediction accuracy
   ```
   Precision = TP / (TP + FP)
   ```

3. **Recall**: True positive rate
   ```
   Recall = TP / (TP + FN)
   ```

4. **F1 Score**: Harmonic mean of precision and recall
   ```
   F1 = 2 * (Precision * Recall) / (Precision + Recall)
   ```

5. **Top-K Accuracy**: Correct prediction in top K results
   ```
   Top-K Accuracy = Correct predictions in top K / Total predictions
   ```

### Evaluation Results

```
Model Performance (Test Set):
├─ Overall Accuracy: 87.3%
├─ Top-1 Accuracy: 87.3%
├─ Top-3 Accuracy: 94.1%
├─ Top-5 Accuracy: 97.2%
├─ Average Precision: 0.89
├─ Average Recall: 0.85
├─ Average F1 Score: 0.87
└─ Inference Time: ~50ms per prediction
```

## Model Deployment

### Model Artifacts

```
prediction/assets/
├─ tuned_multihot_full.pt          # Complete model with weights
├─ inference_package_multihot.pkl  # Inference utilities
└─ label_encoder_multihot.pkl      # Disease label encoder
```

### Loading Process

```python
FUNCTION load_model():
    // Load model architecture
    model = MultiHotModel(
        input_dim=feature_count,
        hidden_dims=[512, 256, 128],
        output_dim=disease_count
    )
    
    // Load trained weights
    checkpoint = torch.load('tuned_multihot_full.pt')
    model.load_state_dict(checkpoint['model_state_dict'])
    
    // Load preprocessing utilities
    inference_package = pickle.load('inference_package_multihot.pkl')
    label_encoder = pickle.load('label_encoder_multihot.pkl')
    
    // Set to evaluation mode
    model.eval()
    
    RETURN {
        "model": model,
        "inference_package": inference_package,
        "label_encoder": label_encoder
    }
END FUNCTION
```

## Model Versioning & Updates

### Version Control Strategy

```
Model Versions:
├─ v1.0.0 (Initial Release)
│  ├─ Training Date: 2024-01-15
│  ├─ Dataset Size: 10,000 samples
│  └─ Accuracy: 85.2%
│
├─ v1.1.0 (Improved Features)
│  ├─ Training Date: 2024-03-20
│  ├─ Dataset Size: 15,000 samples
│  └─ Accuracy: 87.3%
│
└─ v2.0.0 (Architecture Update)
   ├─ Training Date: TBD
   ├─ Dataset Size: 25,000 samples
   └─ Target Accuracy: >90%
```

### A/B Testing Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    A/B TESTING FLOW                          │
└─────────────────────────────────────────────────────────────┘

User Request
    │
    ▼
┌─────────────────────┐
│  Traffic Splitter   │
│  • 90% → Model A    │
│  • 10% → Model B    │
└──────┬──────────────┘
       │
       ├─────────────────────────┐
       │                         │
       ▼                         ▼
┌─────────────────┐      ┌─────────────────┐
│   Model A       │      │   Model B       │
│   (Current)     │      │   (New)         │
└──────┬──────────┘      └──────┬──────────┘
       │                         │
       └─────────┬───────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  Metrics Logger │
        │  • Accuracy     │
        │  • Latency      │
        │  • User feedback│
        └─────────────────┘
```

## Continuous Learning

### Feedback Loop

```
User Feedback
    │
    ▼
┌─────────────────────┐
│  Feedback Storage   │
│  (Firestore)        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Data Validation    │
│  • Quality check    │
│  • Anomaly detection│
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Training Dataset   │
│  Update             │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Periodic Retraining│
│  (Monthly)          │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Model Evaluation   │
│  & Deployment       │
└─────────────────────┘
```

## Performance Optimization

### Inference Optimization

1. **Model Quantization**: Reduce model size
2. **Batch Processing**: Process multiple requests together
3. **Caching**: Cache predictions for identical inputs
4. **GPU Acceleration**: Use CUDA for faster inference
5. **Model Pruning**: Remove unnecessary weights

### Latency Targets

```
Performance Targets:
├─ Inference Time: < 100ms
├─ Model Load Time: < 2 seconds
├─ Memory Usage: < 500MB
└─ Throughput: > 100 predictions/second
```

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Maintained By**: SymptomSense Development Team
