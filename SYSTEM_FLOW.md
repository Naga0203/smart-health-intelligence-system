# AI Health Intelligence System - Complete Flow Documentation

## System Architecture Overview

The AI Health Intelligence System is a comprehensive healthcare decision-support platform that uses **LangChain framework** with **Google Gemini AI** for intelligent health risk assessment.

## Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INPUT (Frontend)                            │
│  • Symptoms (natural language)                                          │
│  • Age, Gender                                                          │
│  • Additional health information                                        │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 1: INPUT VALIDATION                              │
│  Agent: LangChainValidationAgent                                        │
│  • Validates required fields (age, gender, symptoms)                    │
│  • Checks age range (1-120 years)                                       │
│  • Validates symptom format                                             │
│  • Applies safety filters (XSS, SQL injection prevention)               │
│  • Sanitizes input data                                                 │
│  • Uses LangChain for enhanced validation feedback                      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              STEP 2: DATA EXTRACTION (Gemini AI)                         │
│  Agent: DataExtractionAgent                                             │
│  • Parses natural language symptoms                                     │
│  • Maps symptoms to standardized medical terms                          │
│  • Extracts features matching ML model requirements                     │
│  • Uses Gemini AI for intelligent feature extraction                    │
│  • Handles missing/ambiguous data                                       │
│  • Provides extraction confidence score                                 │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 3: ML PREDICTION                                 │
│  Engine: DiseasePredictor                                               │
│  • Receives extracted features                                          │
│  • Selects appropriate disease model                                    │
│  • Performs pure ML prediction (no business logic)                      │
│  • Returns probability score (0.0 - 1.0)                                │
│  • Provides prediction metadata                                         │
│  Models: Diabetes, Heart Disease, Hypertension                          │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                STEP 4: CONFIDENCE EVALUATION                             │
│  Agent: OrchestratorAgent                                               │
│  • Evaluates prediction confidence                                      │
│  • LOW: probability < 0.55                                              │
│  • MEDIUM: 0.55 ≤ probability < 0.75                                    │
│  • HIGH: probability ≥ 0.75                                             │
│  • Determines response strategy                                         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│           STEP 5: EXPLANATION GENERATION (Gemini AI)                     │
│  Agent: LangChainExplanationAgent                                       │
│  • Generates human-readable explanations using Gemini                   │
│  • Provides confidence reasoning                                        │
│  • Analyzes contributing factors                                        │
│  • Adds educational content                                             │
│  • Includes medical disclaimers                                         │
│  • Uses LangChain prompt templates                                      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                STEP 6: RECOMMENDATION GENERATION                         │
│  Agent: RecommendationAgent                                             │
│  • Applies ethical gating (treatment info only for MEDIUM/HIGH)         │
│  • Generates professional referral recommendations                      │
│  • Provides immediate action guidance                                   │
│  • Includes multi-system treatment information:                         │
│    - Allopathy (conventional medicine)                                  │
│    - Ayurveda (traditional Indian medicine)                             │
│    - Homeopathy (alternative medicine)                                  │
│    - Lifestyle (preventive care)                                        │
│  • Adds comprehensive disclaimers                                       │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   STEP 7: MONGODB STORAGE                                │
│  Database: MongoDB                                                      │
│  Collections:                                                           │
│  • symptoms: User input and metadata                                    │
│  • predictions: ML prediction results                                   │
│  • explanations: Generated explanations                                 │
│  • recommendations: Treatment recommendations                           │
│  • audit_logs: Complete audit trail                                    │
│  • user_sessions: User session tracking                                │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  STEP 8: RESPONSE BUILDING                               │
│  Agent: OrchestratorAgent                                               │
│  • Builds complete assessment response                                  │
│  • Includes all pipeline results                                        │
│  • Adds metadata (processing time, IDs, timestamps)                     │
│  • Formats for frontend consumption                                     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND RESPONSE (JSON)                              │
│  {                                                                      │
│    "user_id": "...",                                                    │
│    "assessment_id": "...",                                              │
│    "prediction": {                                                      │
│      "disease": "Diabetes",                                             │
│      "probability": 0.95,                                               │
│      "confidence": "HIGH"                                               │
│    },                                                                   │
│    "extraction": {                                                      │
│      "confidence": 0.85,                                                │
│      "method": "gemini_ai_extraction"                                   │
│    },                                                                   │
│    "explanation": { ... },                                              │
│    "recommendations": { ... },                                          │
│    "metadata": { ... }                                                  │
│  }                                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. LangChain Integration
- **Framework**: LangChain for agent orchestration
- **LLM**: Google Gemini AI (gemini-1.5-flash)
- **Features**:
  - Prompt templates for consistent AI responses
  - Chain execution with error handling
  - Agent state management
  - Conversation chains for complex interactions

### 2. AI Agents (LangChain-based)

#### ValidationAgent
- **Purpose**: First-line defense against invalid input
- **Features**: Input validation, safety filters, sanitization
- **LangChain**: Enhanced validation feedback

#### DataExtractionAgent
- **Purpose**: Extract and map user input to ML features
- **Features**: Natural language parsing, feature mapping, Gemini AI integration
- **LangChain**: Intelligent symptom-to-feature mapping

#### ExplanationAgent
- **Purpose**: Generate human-readable explanations
- **Features**: Confidence reasoning, educational content, medical disclaimers
- **LangChain**: Natural language explanation generation with Gemini

#### RecommendationAgent
- **Purpose**: Ethical gating and treatment recommendations
- **Features**: Confidence-based gating, multi-system treatment info, professional referrals
- **LangChain**: Intelligent recommendation generation

#### OrchestratorAgent
- **Purpose**: Coordinate entire pipeline
- **Features**: Pipeline flow control, confidence evaluation, database storage
- **LangChain**: Complete workflow orchestration

### 3. ML Prediction Engine
- **Models**: Diabetes, Heart Disease, Hypertension
- **Type**: Mock models (can be replaced with trained models)
- **Features**: Pure prediction, no business logic, feature preparation

### 4. MongoDB Database
- **Collections**: symptoms, predictions, explanations, recommendations, audit_logs
- **Features**: Complete audit trail, user history, statistics
- **Indexes**: Optimized for performance

## Data Flow Example

### Input:
```json
{
  "user_id": "user123",
  "age": 45,
  "gender": "male",
  "symptoms": [
    "increased thirst",
    "frequent urination",
    "fatigue",
    "blurred vision"
  ]
}
```

### Processing:
1. **Validation**: ✓ All fields valid
2. **Extraction**: Maps to diabetes features (polyuria, polydipsia, etc.)
3. **Prediction**: Diabetes probability = 0.85 (85%)
4. **Confidence**: HIGH (≥ 0.75)
5. **Explanation**: Generated by Gemini AI
6. **Recommendations**: Treatment info provided (HIGH confidence)
7. **Storage**: Saved to MongoDB
8. **Response**: Complete assessment returned

### Output:
```json
{
  "user_id": "user123",
  "assessment_id": "pred_abc123",
  "prediction": {
    "disease": "Diabetes",
    "probability": 0.85,
    "probability_percent": 85.0,
    "confidence": "HIGH"
  },
  "extraction": {
    "confidence": 0.85,
    "method": "gemini_ai_extraction"
  },
  "explanation": {
    "summary": "Risk assessment for Diabetes",
    "main_explanation": "Based on your symptoms...",
    "confidence_reasoning": {...},
    "disclaimer": "This is not a medical diagnosis..."
  },
  "recommendations": {
    "treatment_information": {
      "available": true,
      "systems": {
        "allopathy": {...},
        "ayurveda": {...},
        "homeopathy": {...},
        "lifestyle": {...}
      }
    },
    "professional_referral": {...}
  },
  "metadata": {
    "processing_time_seconds": 0.5,
    "timestamp": "2026-02-09T12:00:00Z"
  }
}
```

## Ethical Safeguards

1. **Confidence-Based Gating**: Treatment info only for MEDIUM/HIGH confidence
2. **Medical Disclaimers**: All responses include disclaimers
3. **Professional Referrals**: Always recommend consulting healthcare professionals
4. **No Diagnosis Claims**: System never claims to diagnose
5. **Audit Trail**: Complete logging of all operations
6. **Input Validation**: Multiple layers of security filters

## Technology Stack

- **Backend Framework**: Django 6.0.1
- **AI Framework**: LangChain 0.3.13
- **LLM**: Google Gemini AI (gemini-1.5-flash)
- **Database**: MongoDB
- **ML Framework**: Scikit-learn, NumPy, Pandas
- **API**: Django REST Framework

## Environment Variables

```bash
# Django
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True

# MongoDB
MONGO_URI=mongodb://localhost:27017/health_ai_db
MONGO_DB_NAME=health_ai_db

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## API Endpoint

```
POST /api/health/analyze
Content-Type: application/json

Request Body:
{
  "user_id": "string",
  "age": integer,
  "gender": "string",
  "symptoms": ["string"],
  "additional_info": {}
}

Response: Complete assessment (see Output example above)
```

## Performance Metrics

- **Average Processing Time**: < 1 second
- **Extraction Confidence**: 60-90% (depending on input quality)
- **Prediction Accuracy**: Depends on trained models
- **Concurrent Users**: Scalable with proper infrastructure

## Future Enhancements

1. Replace mock models with trained ML models
2. Add more disease types
3. Implement real-time monitoring
4. Add user authentication
5. Implement caching for better performance
6. Add multi-language support
7. Integrate with EHR systems (future scope)