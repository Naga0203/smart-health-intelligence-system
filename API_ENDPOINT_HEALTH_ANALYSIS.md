# Health Analysis API Endpoint

## Overview
The Health Analysis API endpoint provides authenticated health risk assessments using Firebase authentication and the complete AI agent pipeline.

## Endpoint Details

**URL**: `POST /api/health/analyze/`  
**Authentication**: Firebase ID Token (Required)  
**Content-Type**: `application/json`

## Authentication

All requests must include a valid Firebase ID token in the Authorization header:

```
Authorization: Bearer <firebase_id_token>
```

### How to Get Firebase ID Token

1. **Frontend (JavaScript/React)**:
```javascript
import { getAuth } from 'firebase/auth';

const auth = getAuth();
const user = auth.currentUser;
const idToken = await user.getIdToken();

// Use idToken in API request
fetch('http://localhost:8000/api/health/analyze/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${idToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    symptoms: ['fever', 'cough'],
    age: 35,
    gender: 'male'
  })
});
```

2. **Python (for testing)**:
```python
import firebase_admin
from firebase_admin import auth

# Initialize Firebase Admin SDK
cred = firebase_admin.credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

# Create custom token for testing
uid = 'test_user_123'
custom_token = auth.create_custom_token(uid)

# Exchange custom token for ID token (requires Firebase Auth REST API)
```

## Request Format

### Required Fields
- `symptoms` (array of strings): List of symptoms
- `age` (integer): Patient age (1-120)
- `gender` (string): Patient gender ('male', 'female', or 'other')

### Optional Fields
- `additional_info` (object): Additional health information

### Example Request

```json
{
  "symptoms": ["fever", "cough", "headache", "fatigue"],
  "age": 35,
  "gender": "male",
  "additional_info": {
    "weight": 70,
    "height": 175,
    "medical_history": ["diabetes"]
  }
}
```

## Response Formats

### Success Response (HIGH/MEDIUM Confidence)

**Status Code**: `200 OK`

```json
{
  "user_id": "firebase_uid_abc123",
  "assessment_id": "assessment_xyz789",
  "prediction": {
    "disease": "Diabetes",
    "probability": 0.78,
    "probability_percent": 78.0,
    "confidence": "HIGH",
    "model_version": "v1.0"
  },
  "extraction": {
    "confidence": 0.85,
    "method": "gemini_ai_extraction"
  },
  "explanation": {
    "text": "Based on the symptoms provided (fever, cough, headache, fatigue), the system has identified a high probability of diabetes. The key factors contributing to this assessment include...",
    "generated_by": "gemini",
    "confidence": "HIGH"
  },
  "recommendations": {
    "items": [
      "Consult a healthcare professional immediately",
      "Monitor blood sugar levels",
      "Maintain a balanced diet",
      "Regular exercise recommended"
    ],
    "urgency": "medium",
    "confidence": "HIGH"
  },
  "metadata": {
    "processing_time_seconds": 2.5,
    "timestamp": "2026-02-09T12:34:56.789Z",
    "storage_ids": {
      "assessment_id": "assessment_xyz789",
      "prediction_id": "pred_123",
      "explanation_id": "exp_456",
      "recommendation_id": "rec_789"
    },
    "pipeline_version": "v1.0"
  }
}
```

### Blocked Response (LOW Confidence)

**Status Code**: `200 OK`

```json
{
  "blocked": true,
  "reason": "low_confidence",
  "message": "Insufficient information for reliable assessment. Please provide more specific symptoms or consult a healthcare professional.",
  "details": {
    "probability": 0.42,
    "confidence": "LOW",
    "symptoms_provided": ["fever"]
  },
  "timestamp": "2026-02-09T12:34:56.789Z"
}
```

### Validation Error Response

**Status Code**: `400 Bad Request`

```json
{
  "error": "Invalid input",
  "details": {
    "age": ["This field is required."],
    "gender": ["This field is required."]
  },
  "message": "Please provide valid symptoms, age, and gender"
}
```

### Authentication Error Response

**Status Code**: `401 Unauthorized`

```json
{
  "detail": "Authentication credentials were not provided."
}
```

or

```json
{
  "detail": "Invalid authentication token"
}
```

### Internal Server Error Response

**Status Code**: `500 Internal Server Error`

```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred during assessment",
  "details": "Error description here"
}
```

## Confidence Levels

The system uses three confidence levels to determine response behavior:

| Confidence | Probability Range | Behavior |
|------------|------------------|----------|
| **LOW** | < 0.55 | Blocked response, no treatment information |
| **MEDIUM** | 0.55 - 0.74 | Cautious guidance with disclaimers |
| **HIGH** | ≥ 0.75 | Full information with treatment options |

## Complete Request Example (cURL)

```bash
curl -X POST http://localhost:8000/api/health/analyze/ \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6..." \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["fever", "cough", "headache", "fatigue"],
    "age": 35,
    "gender": "male",
    "additional_info": {
      "weight": 70,
      "height": 175
    }
  }'
```

## Complete Request Example (Python)

```python
import requests

url = "http://localhost:8000/api/health/analyze/"
headers = {
    "Authorization": f"Bearer {firebase_id_token}",
    "Content-Type": "application/json"
}
data = {
    "symptoms": ["fever", "cough", "headache", "fatigue"],
    "age": 35,
    "gender": "male",
    "additional_info": {
        "weight": 70,
        "height": 175
    }
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    result = response.json()
    
    if result.get('blocked'):
        print(f"Assessment blocked: {result['message']}")
    else:
        print(f"Disease: {result['prediction']['disease']}")
        print(f"Confidence: {result['prediction']['confidence']}")
        print(f"Probability: {result['prediction']['probability_percent']}%")
        print(f"Explanation: {result['explanation']['text']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

## Important Notes

### Medical Disclaimer
- This system provides **decision support only**, not medical diagnosis
- All responses include appropriate medical disclaimers
- Users should always consult healthcare professionals for medical advice

### Data Privacy
- All requests are tied to authenticated Firebase users
- Complete audit trail maintained for all assessments
- User data stored securely in Firebase Firestore
- Complies with healthcare data privacy best practices

### Rate Limiting
- Rate limiting may be applied to prevent abuse
- Excessive requests may result in temporary blocking

### Pipeline Processing
The endpoint orchestrates the following pipeline:
1. **Validation**: Input validation and sanitization
2. **Data Extraction**: AI-powered feature extraction using Gemini
3. **Prediction**: ML model prediction
4. **Confidence Evaluation**: Confidence level determination
5. **Explanation**: AI-generated explanation using Gemini
6. **Recommendations**: Ethical gating and recommendation generation
7. **Storage**: Firebase Firestore storage with audit logging

## Testing

Run the test suite:
```bash
python manage.py test api.test_health_analysis_api
```

## Related Endpoints

- `GET /api/status/` - System status and health check
- `GET /api/health/` - Simple health check
- `POST /api/assess/` - Legacy assessment endpoint (no auth required)
- `GET /api/diseases/` - List of supported diseases

## Support

For issues or questions:
1. Check the logs: `logs/health_ai.log`
2. Review the implementation: `api/views.py` (HealthAnalysisAPI class)
3. Check Firebase authentication: `common/firebase_auth.py`
4. Review orchestrator: `agents/orchestrator.py`
