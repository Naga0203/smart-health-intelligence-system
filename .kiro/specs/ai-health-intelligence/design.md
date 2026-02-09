# AI Health Intelligence System - Design Document

## Architecture Overview

The AI Health Intelligence System follows an **Agent-Orchestrated, Confidence-Aware** architecture that strictly separates prediction from reasoning to ensure ethical and explainable health decision support.

### Core Design Principles
1. **Separation of Concerns**: ML models predict, AI agents reason, Django orchestrates
2. **Confidence-Aware Gating**: System behavior adapts based on prediction confidence
3. **Ethical Safeguards**: Multiple layers prevent inappropriate medical advice
4. **Explainable AI**: Every decision includes reasoning and transparency
5. **No Diagnosis**: System provides decision support, never medical diagnosis
6. **Firebase Integration**: Secure authentication and real-time data storage

## System Architecture

```
┌─────────────────┐
│   Client/UI     │
│ (Google Sign-In)│
└─────────┬───────┘
          │
┌─────────▼───────┐
│  Django REST    │
│      API        │
│ (Firebase Auth) │
└─────────┬───────┘
          │
┌─────────▼───────┐
│ Agent           │
│ Orchestrator    │
└─────┬───┬───┬───┘
      │   │   │
┌─────▼─┐ │ ┌─▼──────────┐
│Validation│ │Explanation │
│ Agent   │ │Agent(Gemini)│
└─────┬─┘ │ └─┬──────────┘
      │   │   │
┌─────▼───▼───▼───┐
│   ML Prediction │
│     Engine      │
└─────────┬───────┘
          │
┌─────────▼───────┐
│ Recommendation │
│     Agent       │
└─────────┬───────┘
          │
┌─────────▼───────┐
│Firebase Firestore│
│ (Audit & Data)  │
└─────────────────┘
```

## Component Design

### 1. Django REST API Layer
**Purpose**: Handle HTTP requests, authentication, and response formatting
**Technology**: Django REST Framework with Firebase Authentication

```python
# apps/api/views.py
class HealthAnalysisAPI(APIView):
    authentication_classes = [FirebaseAuthentication]
    
    def post(self, request):
        # request.user is FirebaseUser instance
        user_id = request.user.uid
        
        # Delegate to orchestrator
        result = OrchestratorAgent().run_pipeline({
            **request.data,
            'user_id': user_id
        })
        return self.format_response(result)
```

**Key Features**:
- Firebase ID token authentication on all requests
- Request validation and sanitization
- Response formatting with consistent structure
- Error handling and status codes
- User context from Firebase authentication

### 1.5 Firebase Authentication Layer
**Purpose**: Secure user authentication with Google Sign-In
**Technology**: Firebase Admin SDK

```python
# common/firebase_auth.py
class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Extract Bearer token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        id_token = auth_header.split('Bearer ')[1]
        
        # Verify token with Firebase
        decoded_token = auth.verify_id_token(id_token)
        
        # Create FirebaseUser instance
        user = FirebaseUser(
            uid=decoded_token['uid'],
            email=decoded_token.get('email'),
            display_name=decoded_token.get('name'),
            email_verified=decoded_token.get('email_verified')
        )
        
        return (user, decoded_token)
```

**Key Features**:
- Google Sign-In integration
- Firebase ID token verification
- Custom FirebaseUser class for Django compatibility
- Automatic user profile creation/update in Firestore
- Token expiration handling

### 2. Agent Orchestrator
**Purpose**: Control system flow and coordinate all agents
**Technology**: Python classes with clear interfaces

```python
# apps/agents/orchestrator.py
class OrchestratorAgent:
    def run_pipeline(self, user_input):
        # 1. Validate input
        validation = ValidationAgent().validate_symptoms(user_input)
        if not validation["valid"]:
            return self.blocked_response(validation["reason"])
        
        # 2. Get ML prediction
        disease = self.select_disease(user_input)
        probability = DiseasePredictor().predict(disease, user_input)
        
        # 3. Evaluate confidence
        confidence = self.evaluate_confidence(probability)
        
        # 4. Generate explanation
        explanation = ExplanationAgent().explain(disease, probability, confidence)
        
        # 5. Apply ethical gates
        treatment_allowed = RecommendationAgent().allow_treatment(confidence)
        
        return self.build_response(disease, probability, confidence, explanation, treatment_allowed)
```

**Confidence Evaluation Logic**:
- LOW: probability < 0.55 (block or heavily limit response)
- MEDIUM: 0.55 ≤ probability < 0.75 (provide cautious guidance)
- HIGH: probability ≥ 0.75 (provide full information with disclaimers)

### 3. Validation Agent
**Purpose**: First-line defense against incomplete or unsafe inputs
**Technology**: Rule-based validation with extensible framework

```python
# apps/agents/validation_agent.py
class ValidationAgent:
    REQUIRED_FIELDS = ["age", "gender", "symptoms"]
    
    def validate_symptoms(self, symptoms):
        # Check required fields
        missing = [f for f in self.REQUIRED_FIELDS if f not in symptoms]
        if missing:
            return {"valid": False, "reason": "Missing critical fields", "missing": missing}
        
        # Validate age range
        if not (0 < symptoms["age"] < 120):
            return {"valid": False, "reason": "Invalid age range"}
        
        # Validate symptom format
        if not isinstance(symptoms["symptoms"], list) or len(symptoms["symptoms"]) == 0:
            return {"valid": False, "reason": "No symptoms provided"}
        
        return {"valid": True}
```

### 4. ML Prediction Engine
**Purpose**: Pure machine learning inference with no business logic
**Technology**: Scikit-learn models loaded at startup

```python
# apps/prediction/inference.py
class DiseasePredictor:
    def __init__(self):
        self.models = {
            "diabetes": joblib.load("models/diabetes.pkl"),
            "heart_disease": joblib.load("models/heart.pkl"),
            "hypertension": joblib.load("models/hypertension.pkl")
        }
    
    def predict(self, disease, features):
        """Pure prediction - no confidence logic, no database access"""
        model = self.models[disease]
        feature_vector = self.prepare_features(features)
        probability = model.predict_proba([feature_vector])[0][1]
        return probability
    
    def prepare_features(self, raw_features):
        """Convert raw input to model-ready feature vector"""
        # Feature engineering logic here
        return feature_vector
```

**Key Constraints**:
- No database access
- No confidence evaluation
- No business logic
- Pure mathematical prediction only

### 5. Explanation Agent (Gemini Integration)
**Purpose**: Generate human-readable explanations using Google Gemini
**Technology**: Google Gemini API for natural language generation

```python
# apps/agents/explanation_agent.py
class ExplanationAgent:
    def __init__(self):
        self.gemini_client = GeminiClient()
    
    def explain(self, disease, probability, confidence):
        prompt = f"""
        Explain a health risk assessment in simple terms:
        - Disease: {disease}
        - Risk probability: {probability:.2%}
        - Confidence level: {confidence}
        
        Requirements:
        - Use simple, non-medical language
        - Emphasize this is NOT a diagnosis
        - Explain what the confidence level means
        - Suggest consulting healthcare professionals
        """
        
        explanation = self.gemini_client.generate(prompt)
        
        return {
            "summary": f"Risk assessment for {disease}",
            "probability_percent": round(probability * 100, 2),
            "confidence": confidence,
            "explanation": explanation,
            "disclaimer": "This is not a medical diagnosis. Consult healthcare professionals for medical advice."
        }
```

**Gemini Usage Boundaries**:
- ✅ Generate explanations and educational content
- ✅ Interpret confidence levels for users
- ✅ Provide reasoning about risk factors
- ❌ Never perform medical diagnosis
- ❌ Never make treatment recommendations
- ❌ Never predict diseases or conditions

### 6. Recommendation Agent
**Purpose**: Ethical gating for treatment information
**Technology**: Rule-based decision engine

```python
# apps/agents/recommendation_agent.py
class RecommendationAgent:
    def allow_treatment(self, confidence):
        """Ethical gate - only allow treatment info for sufficient confidence"""
        return confidence in ["MEDIUM", "HIGH"]
    
    def get_treatment_info(self, disease, confidence):
        if not self.allow_treatment(confidence):
            return {"message": "Confidence too low for treatment information"}
        
        return TREATMENTS.get(disease, {})
```

### 7. Treatment Knowledge Base
**Purpose**: Informational treatment data across multiple medical systems
**Technology**: Static data structure with clear disclaimers

```python
# apps/treatment/knowledge_base.py
TREATMENTS = {
    "diabetes": {
        "allopathy": {
            "approach": "Blood sugar monitoring and medication management",
            "focus": "Insulin regulation and glucose control",
            "disclaimer": "Requires medical supervision"
        },
        "ayurveda": {
            "approach": "Diet regulation and lifestyle balance",
            "focus": "Holistic body constitution and natural remedies",
            "disclaimer": "Consult qualified Ayurvedic practitioner"
        },
        "homeopathy": {
            "approach": "Individualized symptom-based treatment",
            "focus": "Constitutional remedies and symptom patterns",
            "disclaimer": "Requires qualified homeopathic consultation"
        },
        "lifestyle": {
            "approach": "Diet, exercise, and stress management",
            "focus": "Preventive care and healthy habits",
            "disclaimer": "General wellness information only"
        }
    }
}
```

**Important Constraints**:
- No specific prescriptions or dosages
- No direct medical advice
- Educational information only
- Clear disclaimers for each system

## Data Architecture

### Firebase Firestore Collections

```javascript
// users collection
{
  "uid": "firebase_user_id",
  "email": "user@example.com",
  "display_name": "John Doe",
  "photo_url": "https://...",
  "email_verified": true,
  "created_at": Timestamp,
  "updated_at": Timestamp,
  "last_login": Timestamp
}

// assessments collection
{
  "id": "auto_generated_id",
  "user_id": "firebase_user_id",
  "symptoms": ["symptom1", "symptom2"],
  "age": 35,
  "gender": "female",
  "disease": "diabetes",
  "probability": 0.73,
  "confidence": "MEDIUM",
  "extraction_data": {...},
  "prediction_metadata": {...},
  "explanation": {...},
  "recommendations": {...},
  "created_at": Timestamp,
  "status": "completed"
}

// predictions collection
{
  "id": "auto_generated_id",
  "user_id": "firebase_user_id",
  "assessment_id": "assessment_doc_id",
  "disease": "diabetes",
  "probability": 0.73,
  "confidence": "MEDIUM",
  "model_version": "v1.2",
  "created_at": Timestamp
}

// explanations collection
{
  "id": "auto_generated_id",
  "assessment_id": "assessment_doc_id",
  "explanation": "string",
  "generated_by": "gemini",
  "created_at": Timestamp
}

// recommendations collection
{
  "id": "auto_generated_id",
  "assessment_id": "assessment_doc_id",
  "recommendations": {...},
  "created_at": Timestamp
}

// audit_logs collection
{
  "id": "auto_generated_id",
  "event_type": "health_assessment_completed",
  "user_id": "firebase_user_id",
  "payload": {...},
  "timestamp": Timestamp,
  "ip_address": "string",
  "user_agent": "string"
}
```

### Firebase Authentication
- Google Sign-In integration for user authentication
- Firebase ID tokens verified on each API request
- Custom FirebaseUser class for Django compatibility
- Token-based authentication with Bearer tokens

## Security Architecture

### Environment Variables
```bash
# .env file (never committed to version control)
DJANGO_SECRET_KEY=your_django_secret_key
DEBUG=False
FIREBASE_CREDENTIALS_PATH=config/firebase-credentials.json
GEMINI_API_KEY=your_gemini_api_key
```

### Firebase Configuration
1. **Service Account**: Firebase Admin SDK credentials in JSON file
2. **Authentication**: Firebase ID token verification on each request
3. **Firestore**: Real-time database with automatic scaling
4. **Security Rules**: Firestore security rules to protect user data

### Security Measures
1. **No Hardcoded Secrets**: All sensitive data in environment variables
2. **Input Validation**: Comprehensive validation at multiple layers
3. **Audit Logging**: Complete trail of all system operations
4. **Rate Limiting**: Prevent abuse of AI services
5. **Data Encryption**: Firebase handles encryption in transit and at rest
6. **Token Verification**: Firebase ID tokens verified on each API request

## API Design

### Health Analysis Endpoint
```
POST /api/health/analyze
Content-Type: application/json

Request:
{
  "symptoms": ["fatigue", "increased_thirst", "frequent_urination"],
  "metadata": {
    "age": 35,
    "gender": "female",
    "medical_history": []
  }
}

Response (HIGH confidence):
{
  "prediction": {
    "disease": "diabetes",
    "probability": 0.78,
    "confidence": "HIGH"
  },
  "explanation": {
    "summary": "Risk assessment for diabetes",
    "probability_percent": 78,
    "confidence": "HIGH",
    "explanation": "Based on the symptoms provided...",
    "disclaimer": "This is not a medical diagnosis..."
  },
  "treatment": {
    "allopathy": {...},
    "ayurveda": {...},
    "homeopathy": {...},
    "lifestyle": {...}
  }
}

Response (LOW confidence):
{
  "prediction": {
    "disease": "diabetes",
    "probability": 0.45,
    "confidence": "LOW"
  },
  "explanation": {
    "summary": "Insufficient information for reliable assessment",
    "confidence": "LOW",
    "explanation": "The provided symptoms are too general...",
    "disclaimer": "This is not a medical diagnosis..."
  },
  "message": "Please provide more specific symptoms or consult a healthcare professional"
}
```

## Correctness Properties

The system must maintain these invariant properties:

### Property 1: Confidence-Treatment Gating
**Validates: Requirements 4.2**
For all system responses, if confidence level is "LOW", then treatment information must not be included in the response.

### Property 2: Explanation Completeness
**Validates: Requirements 5.1, 5.3**
For all predictions with confidence "MEDIUM" or "HIGH", the response must include a non-empty explanation and confidence reasoning.

### Property 3: Disclaimer Presence
**Validates: Requirements 3.4, 4.3**
All system responses containing health assessments must include appropriate medical disclaimers.

### Property 4: Input Validation Consistency
**Validates: Requirements 1.2, 1.3**
All requests missing required fields (age, gender, symptoms) must be rejected before reaching the ML prediction layer.

### Property 5: Audit Trail Completeness
**Validates: Requirements 6.3**
Every user interaction that reaches the prediction stage must generate corresponding audit log entries.

## Testing Strategy

### Unit Tests
- Individual agent functionality
- ML model prediction accuracy
- Input validation logic
- Response formatting

### Integration Tests
- End-to-end API workflows
- Agent orchestration flow
- Database operations
- External service integration

### Property-Based Tests
- Confidence-treatment gating invariants
- Input validation boundaries
- Response structure consistency
- Audit logging completeness

## Deployment Architecture

### Local Development
- Django development server
- Local MongoDB instance
- Environment variables in .env file

### Production Considerations
- Containerized deployment (Docker)
- MongoDB Atlas or managed MongoDB
- Secure secret management
- Load balancing for concurrent users
- Monitoring and alerting

## Ethical Considerations

### Built-in Safeguards
1. **No Diagnosis Claims**: System never claims to diagnose medical conditions
2. **Confidence Gating**: Low confidence predictions are heavily limited
3. **Professional Referral**: All responses encourage consulting healthcare professionals
4. **Transparency**: Clear explanation of how assessments are made
5. **Multi-System Approach**: Acknowledges different medical traditions

### Risk Mitigation
- Clear disclaimers on all outputs
- Confidence-based response limitation
- Audit trail for accountability
- Regular model validation and updates
- User education about system limitations