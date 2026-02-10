# API Testing Guide

## Overview

This guide explains how to test the AI Health Intelligence API endpoints using Postman and the provided test scripts.

## Quick Start

### 1. Start the Django Server

```bash
py manage.py runserver
```

The server will start on `http://localhost:8000`

### 2. Test with Python Script

```bash
py test_api_endpoints.py
```

This will test all public endpoints and show which authenticated endpoints require Firebase tokens.

### 3. Import Postman Collection

1. Open Postman
2. Click "Import" button
3. Select `postman_collection.json` from the project root
4. The collection will be imported with all endpoints organized in folders

## API Endpoints

### Public Endpoints (No Authentication Required)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Simple health check |
| `/api/status` | GET | System status and component health |
| `/api/model/info` | GET | ML model information |
| `/api/diseases` | GET | List of supported diseases |
| `/api/assess` | POST | Health assessment (anonymous) |
| `/api/predict/top` | POST | Top N disease predictions |

### Authenticated Endpoints (Require Firebase Token)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health/analyze` | POST | Primary health analysis |
| `/api/user/profile` | GET | Get user profile |
| `/api/user/profile` | PUT | Update user profile |
| `/api/user/statistics` | GET | Get user statistics |
| `/api/user/assessments` | GET | Get assessment history (paginated) |
| `/api/user/assessments/{id}` | GET | Get specific assessment details |

## Rate Limiting

The API implements comprehensive rate limiting to prevent abuse:

### Authenticated Users

- **Burst Protection**: 10 requests/minute
- **Hourly Limit**: 100 requests/hour
- **Daily Limit**: 200 requests/day
- **IP-Based**: 200 requests/hour per IP

### Anonymous Users

- **Hourly Limit**: 5 requests/hour
- **IP-Based**: 200 requests/hour per IP

### Rate Limit Response

When rate limit is exceeded, you'll receive:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests",
  "details": "Rate limit exceeded. Please try again in 60 seconds.",
  "wait_seconds": 60,
  "status_code": 429
}
```

**HTTP Status Code**: `429 Too Many Requests`

## Testing with Postman

### Setup

1. **Import Collection**: Import `postman_collection.json`
2. **Set Variables**:
   - `base_url`: `http://localhost:8000/api` (default)
   - `firebase_token`: Your Firebase ID token (for authenticated endpoints)

### Getting a Firebase Token

For testing authenticated endpoints, you need a Firebase ID token:

1. **Option 1 - From Frontend**:
   - Log in to your frontend application
   - Open browser DevTools → Console
   - Run: `firebase.auth().currentUser.getIdToken().then(token => console.log(token))`
   - Copy the token

2. **Option 2 - Firebase Admin SDK**:
   - Use Firebase Admin SDK to create a custom token
   - Exchange it for an ID token

3. **Option 3 - Firebase REST API**:
   ```bash
   curl -X POST \
     'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=YOUR_API_KEY' \
     -H 'Content-Type: application/json' \
     -d '{
       "email": "user@example.com",
       "password": "password",
       "returnSecureToken": true
     }'
   ```

### Testing Workflow

#### 1. Test Public Endpoints

Start with endpoints that don't require authentication:

1. **Health Check** - Verify server is running
2. **System Status** - Check component health
3. **Model Info** - Verify ML model is loaded
4. **Diseases List** - Get supported diseases

#### 2. Test Health Assessment (Anonymous)

```json
POST /api/assess
{
  "symptoms": ["fever", "cough", "headache"],
  "age": 28,
  "gender": "female",
  "user_id": "test_user_123"
}
```

#### 3. Test Authenticated Endpoints

Set your Firebase token in the collection variable, then test:

1. **Get User Profile** - Should create profile on first access
2. **Update User Profile** - Update profile information
3. **Health Analysis** - Complete health analysis with authentication
4. **Get Statistics** - View your assessment statistics
5. **Get Assessment History** - View past assessments

#### 4. Test Rate Limiting

Use the "Rate Limiting Tests" folder:

1. **Test Burst Rate Limit**:
   - Run the request 15 times rapidly
   - Should get 429 error after 10 requests

2. **Test Anonymous Rate Limit**:
   - Run the request 10 times
   - Should get 429 error after 5 requests

## Example Requests

### Health Analysis (Authenticated)

```bash
curl -X POST http://localhost:8000/api/health/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -d '{
    "symptoms": ["fatigue", "increased_thirst", "frequent_urination"],
    "age": 35,
    "gender": "male",
    "additional_info": {
      "weight": 75,
      "height": 175
    }
  }'
```

### Get User Profile

```bash
curl -X GET http://localhost:8000/api/user/profile \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

### Update User Profile

```bash
curl -X PUT http://localhost:8000/api/user/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -d '{
    "display_name": "John Doe",
    "phone_number": "+1234567890",
    "gender": "male",
    "medical_history": ["diabetes"],
    "allergies": ["penicillin"]
  }'
```

### Get Assessment History

```bash
curl -X GET "http://localhost:8000/api/user/assessments?page=1&page_size=10&sort=created_at&order=desc" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

## Testing Rate Limiting

### Python Script

```python
import requests

base_url = "http://localhost:8000/api"
data = {"symptoms": ["test"], "age": 30, "gender": "male"}

# Make 10 rapid requests
for i in range(10):
    response = requests.post(f"{base_url}/assess", json=data)
    print(f"Request {i+1}: {response.status_code}")
    if response.status_code == 429:
        print(f"Rate limited! Wait: {response.json()['wait_seconds']}s")
```

### Postman Runner

1. Select "Test Burst Rate Limit" request
2. Click "Run" → "Run manually"
3. Set iterations to 15
4. Run the collection
5. Observe 429 errors after 10 requests

## Troubleshooting

### Server Not Running

```
❌ Error: Could not connect to the API server.
```

**Solution**: Start the Django server:
```bash
py manage.py runserver
```

### Authentication Failed

```json
{
  "error": "authentication_error",
  "message": "Authentication failed",
  "status_code": 401
}
```

**Solutions**:
1. Verify Firebase token is valid and not expired
2. Check Authorization header format: `Bearer YOUR_TOKEN`
3. Ensure Firebase credentials are configured in `.env`

### Rate Limit Exceeded

```json
{
  "error": "rate_limit_exceeded",
  "wait_seconds": 60
}
```

**Solution**: Wait for the specified time before making more requests, or clear the cache:
```bash
py manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

### Model Not Loaded

```json
{
  "error": "service_unavailable",
  "message": "Service temporarily unavailable"
}
```

**Solution**: Ensure ML models are properly set up. Check logs for model loading errors.

## Response Formats

### Success Response (HIGH Confidence)

```json
{
  "status": "success",
  "confidence": "HIGH",
  "message": "Assessment completed with high confidence",
  "user_id": "firebase_uid",
  "assessment_id": "assessment_123",
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
    "text": "Based on the symptoms provided...",
    "generated_by": "gemini",
    "confidence": "HIGH"
  },
  "recommendations": {
    "items": ["Consult healthcare professional", ...],
    "urgency": "medium",
    "confidence": "HIGH"
  },
  "treatment_info": {
    "allopathy": {...},
    "ayurveda": {...},
    "homeopathy": {...},
    "lifestyle": {...}
  },
  "metadata": {
    "processing_time_seconds": 2.5,
    "timestamp": "2026-02-10T12:00:00Z"
  }
}
```

### Low Confidence Response

```json
{
  "status": "low_confidence",
  "confidence": "LOW",
  "message": "Insufficient information for reliable assessment",
  "suggestion": "Please provide more specific symptoms or consult a healthcare professional",
  "prediction": {
    "disease": "Unknown",
    "probability_percent": 45.0,
    "confidence": "LOW"
  },
  "disclaimer": "This is not a medical diagnosis..."
}
```

### Error Response

```json
{
  "error": "validation_error",
  "message": "Invalid input data",
  "details": {
    "age": ["This field is required."],
    "symptoms": ["This field is required."]
  },
  "status_code": 400
}
```

## Best Practices

1. **Always Check Health Endpoint First**: Verify server is running
2. **Handle Rate Limits Gracefully**: Implement exponential backoff
3. **Cache Responses**: Don't make duplicate requests
4. **Use Appropriate Endpoints**: Use authenticated endpoints for user-specific data
5. **Monitor Rate Limit Headers**: Track remaining requests
6. **Test Error Scenarios**: Test with invalid data to verify error handling
7. **Secure Tokens**: Never commit Firebase tokens to version control

## Next Steps

1. **Set up Firebase Authentication** in your frontend
2. **Implement Token Refresh** to handle expired tokens
3. **Add Error Handling** in your client application
4. **Monitor API Usage** through logs and analytics
5. **Configure Production Settings** for deployment

## Additional Resources

- [API Rate Limiting Documentation](./API_RATE_LIMITING.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Firebase Authentication Guide](https://firebase.google.com/docs/auth)
- [Django REST Framework](https://www.django-rest-framework.org/)
