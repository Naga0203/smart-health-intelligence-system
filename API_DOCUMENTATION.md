# AI Health Intelligence API Documentation

## Overview

The AI Health Intelligence System provides a REST API for health risk assessment using AI agents and machine learning. The system is designed as a **decision-support tool**, not a diagnostic engine, with built-in ethical safeguards and confidence-aware responses.

**Important**: This system provides decision support only, NOT medical diagnosis. Always consult healthcare professionals for medical advice.

## Base URL

- **Development**: `http://localhost:8000/api/`
- **Production**: `https://api.healthai.example.com/api/`

## Interactive Documentation

The API provides interactive documentation through Swagger UI and ReDoc:

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

## Authentication

Most endpoints require Firebase Authentication. Include your Firebase ID token in the Authorization header:

```http
Authorization: Bearer <your_firebase_id_token>
```

### Getting a Firebase ID Token

1. Sign in with Google through Firebase Authentication
2. Obtain the ID token from the Firebase SDK
3. Include the token in the Authorization header

## Rate Limiting

The API implements rate limiting to prevent abuse:

### Authenticated Users
- **Burst Protection**: 10 requests per minute
- **Sustained Usage**: 100 requests per hour
- **Daily Limit**: 200 requests per day
- **IP-based Limit**: 200 requests per hour

### Anonymous Users
- **Hourly Limit**: 5 requests per hour
- **IP-based Limit**: 200 requests per hour

### Rate Limit Headers

Rate limit information is included in response headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1644508800
```

### Rate Limit Exceeded Response

```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests",
  "details": "Rate limit exceeded. Please try again in 60 seconds.",
  "wait_seconds": 60,
  "status_code": 429
}
```

## Confidence Levels

The system provides three confidence levels for predictions:

### LOW Confidence (< 55%)
- Limited response with minimal information
- Encourages providing more specific symptoms
- Suggests consulting healthcare professionals
- **No treatment information provided**

### MEDIUM Confidence (55-75%)
- Cautious guidance with explanations
- Treatment information across multiple medical systems
- Clear disclaimers about educational nature
- Recommendations for professional consultation

### HIGH Confidence (≥ 75%)
- Full information with comprehensive details
- Detailed treatment information
- Risk factors and contributing factors
- Strong recommendations for professional consultation

## Response Structure

All successful health assessment responses include:

```json
{
  "status": "success",
  "confidence": "HIGH|MEDIUM|LOW",
  "message": "Assessment completed",
  "user_id": "firebase_user_uid",
  "assessment_id": "unique_assessment_id",
  "prediction": {
    "disease": "Disease Name",
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
    "text": "Detailed explanation...",
    "generated_by": "gemini",
    "confidence": "HIGH"
  },
  "recommendations": {
    "items": ["Recommendation 1", "Recommendation 2"],
    "urgency": "low|medium|high",
    "confidence": "HIGH"
  },
  "treatment_info": {
    "allopathy": {...},
    "ayurveda": {...},
    "homeopathy": {...},
    "lifestyle": {...}
  },
  "disclaimer": "Medical disclaimer text",
  "metadata": {
    "processing_time_seconds": 2.5,
    "timestamp": "2026-02-10T12:00:00Z",
    "storage_ids": {...},
    "pipeline_version": "v1.0"
  }
}
```

## Error Handling

The API uses standard HTTP status codes:

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Invalid input data |
| 401 | Authentication failed |
| 403 | Permission denied |
| 404 | Resource not found |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
| 503 | Service unavailable |

### Error Response Format

```json
{
  "error": "error_type",
  "message": "Human-readable error message",
  "details": "Detailed error information",
  "status_code": 400
}
```

## API Endpoints

### Health Analysis

#### POST /health/analyze (Authenticated)

Perform complete health analysis with Firebase authentication.

**Authentication**: Required

**Rate Limits**: 10/min, 100/hour, 200/day

**Request Body**:
```json
{
  "symptoms": ["increased thirst", "frequent urination", "fatigue"],
  "age": 45,
  "gender": "male",
  "additional_info": {
    "weight": 85,
    "height": 175,
    "family_history": ["diabetes"]
  }
}
```

**Response** (HIGH confidence):
```json
{
  "status": "success",
  "confidence": "HIGH",
  "user_id": "firebase_uid",
  "assessment_id": "assessment_123",
  "prediction": {
    "disease": "Diabetes",
    "probability": 0.78,
    "probability_percent": 78.0,
    "confidence": "HIGH"
  },
  "explanation": {
    "text": "Based on the symptoms provided...",
    "confidence": "HIGH"
  },
  "recommendations": {
    "items": ["Consult endocrinologist", "Get blood glucose testing"],
    "urgency": "medium"
  },
  "treatment_info": {
    "allopathy": {...},
    "ayurveda": {...},
    "lifestyle": {...}
  }
}
```

#### POST /assess (Unauthenticated)

Perform health assessment without authentication.

**Authentication**: Not required

**Rate Limits**: 5/hour (anonymous)

**Request Body**: Same as authenticated endpoint

**Response**: Similar to authenticated endpoint but with limited rate limits

### User Profile

#### GET /user/profile

Retrieve authenticated user's profile.

**Authentication**: Required

**Response**:
```json
{
  "uid": "firebase_uid",
  "email": "user@example.com",
  "display_name": "John Doe",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "medical_history": ["diabetes"],
  "allergies": ["penicillin"],
  "current_medications": ["metformin"]
}
```

#### PUT /user/profile

Update authenticated user's profile.

**Authentication**: Required

**Request Body**:
```json
{
  "display_name": "John Doe",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "medical_history": ["diabetes", "hypertension"],
  "allergies": ["penicillin"],
  "current_medications": ["metformin"]
}
```

#### GET /user/statistics

Get user statistics and assessment summary.

**Authentication**: Required

**Response**:
```json
{
  "total_assessments": 25,
  "assessments_by_confidence": {
    "LOW": 5,
    "MEDIUM": 10,
    "HIGH": 10
  },
  "most_common_diseases": [
    {"disease": "Diabetes", "count": 8},
    {"disease": "Hypertension", "count": 5}
  ],
  "last_assessment_date": "2026-02-10T12:00:00Z",
  "account_age_days": 45
}
```

### Assessment History

#### GET /user/assessments

Retrieve paginated assessment history.

**Authentication**: Required

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 50)
- `sort`: Sort field - created_at, confidence, disease (default: created_at)
- `order`: Sort order - asc, desc (default: desc)

**Example Request**:
```
GET /api/user/assessments?page=1&page_size=10&sort=created_at&order=desc
```

**Response**:
```json
{
  "total": 25,
  "page": 1,
  "page_size": 10,
  "assessments": [
    {
      "id": "assessment_1",
      "created_at": "2026-02-10T12:00:00Z",
      "disease": "Diabetes",
      "probability": 0.78,
      "confidence": "HIGH",
      "symptoms": ["increased thirst", "frequent urination"],
      "status": "completed"
    }
  ]
}
```

#### GET /user/assessments/{assessment_id}

Get detailed information about a specific assessment.

**Authentication**: Required

**Authorization**: Users can only access their own assessments

**Response**:
```json
{
  "id": "assessment_123",
  "user_id": "firebase_uid",
  "created_at": "2026-02-10T12:00:00Z",
  "symptoms": ["increased thirst", "frequent urination"],
  "age": 45,
  "gender": "male",
  "disease": "Diabetes",
  "probability": 0.78,
  "confidence": "HIGH",
  "extraction_data": {...},
  "explanation": {...},
  "recommendations": {...}
}
```

### Predictions

#### POST /predict/top

Get top N disease predictions ranked by probability.

**Authentication**: Not required

**Request Body**:
```json
{
  "symptoms": ["fever", "cough", "headache"],
  "age": 35,
  "gender": "male",
  "n": 5
}
```

**Response**:
```json
[
  {"disease": "Influenza", "probability": 0.85, "rank": 1},
  {"disease": "Common Cold", "probability": 0.72, "rank": 2},
  {"disease": "Bronchitis", "probability": 0.68, "rank": 3},
  {"disease": "Pneumonia", "probability": 0.55, "rank": 4},
  {"disease": "Allergic Rhinitis", "probability": 0.48, "rank": 5}
]
```

### System Information

#### GET /status

Get system status and component health.

**Authentication**: Not required

**Response**:
```json
{
  "status": "operational",
  "version": "1.0",
  "components": {
    "orchestrator": {"status": "healthy"},
    "predictor": {"status": "healthy", "models_loaded": 3},
    "database": {"status": "connected"},
    "gemini_ai": {"status": "available"}
  },
  "timestamp": "2026-02-10T12:00:00Z"
}
```

#### GET /health

Simple health check endpoint.

**Authentication**: Not required

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-10T12:00:00Z"
}
```

#### GET /model/info

Get information about the ML model.

**Authentication**: Not required

**Response**:
```json
{
  "model_loaded": true,
  "model_type": "pytorch",
  "num_features": 132,
  "num_diseases": 715,
  "device": "cuda"
}
```

#### GET /diseases

Get list of all supported diseases.

**Authentication**: Not required

**Response**:
```json
{
  "total": 715,
  "diseases": [
    "Fungal infection",
    "Allergy",
    "GERD",
    "Diabetes",
    "Hypertension",
    "..."
  ]
}
```

## Code Examples

### Python

```python
import requests

# Get Firebase ID token (from Firebase SDK)
id_token = "your_firebase_id_token"

# Perform health analysis
url = "http://localhost:8000/api/health/analyze/"
headers = {
    "Authorization": f"Bearer {id_token}",
    "Content-Type": "application/json"
}
data = {
    "symptoms": ["increased thirst", "frequent urination", "fatigue"],
    "age": 45,
    "gender": "male"
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

print(f"Disease: {result['prediction']['disease']}")
print(f"Confidence: {result['confidence']}")
print(f"Probability: {result['prediction']['probability_percent']}%")
```

### JavaScript (Fetch API)

```javascript
// Get Firebase ID token (from Firebase SDK)
const idToken = await firebase.auth().currentUser.getIdToken();

// Perform health analysis
const response = await fetch('http://localhost:8000/api/health/analyze/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${idToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    symptoms: ['increased thirst', 'frequent urination', 'fatigue'],
    age: 45,
    gender: 'male'
  })
});

const result = await response.json();
console.log('Disease:', result.prediction.disease);
console.log('Confidence:', result.confidence);
console.log('Probability:', result.prediction.probability_percent + '%');
```

### cURL

```bash
# Perform health analysis (authenticated)
curl -X POST http://localhost:8000/api/health/analyze/ \
  -H "Authorization: Bearer YOUR_FIREBASE_ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["increased thirst", "frequent urination", "fatigue"],
    "age": 45,
    "gender": "male"
  }'

# Get user profile
curl -X GET http://localhost:8000/api/user/profile/ \
  -H "Authorization: Bearer YOUR_FIREBASE_ID_TOKEN"

# Get assessment history
curl -X GET "http://localhost:8000/api/user/assessments/?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_FIREBASE_ID_TOKEN"
```

## Best Practices

### 1. Error Handling

Always handle errors appropriately:

```python
try:
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        # Handle rate limit
        wait_time = e.response.json().get('wait_seconds', 60)
        print(f"Rate limit exceeded. Wait {wait_time} seconds.")
    elif e.response.status_code == 401:
        # Handle authentication error
        print("Authentication failed. Please sign in again.")
    else:
        print(f"Error: {e.response.json()}")
```

### 2. Rate Limit Management

Implement exponential backoff for rate limits:

```python
import time

def make_request_with_retry(url, data, headers, max_retries=3):
    for attempt in range(max_retries):
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 429:
            wait_time = response.json().get('wait_seconds', 60)
            time.sleep(wait_time)
            continue
        
        return response
    
    raise Exception("Max retries exceeded")
```

### 3. Token Refresh

Refresh Firebase ID tokens before they expire:

```javascript
// Refresh token if needed
const user = firebase.auth().currentUser;
if (user) {
  const idToken = await user.getIdToken(/* forceRefresh */ true);
  // Use refreshed token
}
```

### 4. Confidence-Based UI

Adapt your UI based on confidence levels:

```javascript
function displayResults(result) {
  const confidence = result.confidence;
  
  if (confidence === 'LOW') {
    // Show limited information
    // Encourage user to provide more details
    showWarning('Insufficient information for reliable assessment');
  } else if (confidence === 'MEDIUM') {
    // Show cautious guidance
    showResults(result);
    showDisclaimer('Consult healthcare professional');
  } else if (confidence === 'HIGH') {
    // Show full information
    showDetailedResults(result);
    showTreatmentInfo(result.treatment_info);
  }
}
```

## Security Considerations

1. **Never expose Firebase credentials** in client-side code
2. **Always use HTTPS** in production
3. **Validate and sanitize** all user inputs
4. **Implement proper error handling** to avoid information leakage
5. **Monitor rate limits** to prevent abuse
6. **Rotate API keys** regularly
7. **Use environment variables** for sensitive configuration

## Support and Resources

- **Interactive API Docs**: http://localhost:8000/api/docs/
- **ReDoc Documentation**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Changelog

### Version 1.0.0 (2026-02-10)
- Initial API release
- Firebase Authentication integration
- Multi-agent health assessment pipeline
- Confidence-aware responses
- Rate limiting implementation
- User profile management
- Assessment history tracking
- Comprehensive error handling

## Legal Disclaimer

This API provides health risk assessment for informational and educational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare providers with any questions regarding medical conditions. Never disregard professional medical advice or delay seeking it because of information provided by this API.
