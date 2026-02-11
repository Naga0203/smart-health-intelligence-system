# API Quick Reference

Quick reference guide for the AI Health Intelligence API.

## Base URLs

- **Development**: `http://localhost:8000/api/`
- **Interactive Docs**: `http://localhost:8000/api/docs/`

## Authentication

```http
Authorization: Bearer <firebase_id_token>
```

## Quick Start

### 1. Health Analysis (Authenticated)

```bash
curl -X POST http://localhost:8000/api/health/analyze/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["fever", "cough"],
    "age": 35,
    "gender": "male"
  }'
```

### 2. Health Analysis (Anonymous)

```bash
curl -X POST http://localhost:8000/api/assess/ \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["fever", "cough"],
    "age": 35,
    "gender": "male"
  }'
```

### 3. Get User Profile

```bash
curl -X GET http://localhost:8000/api/user/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Get Assessment History

```bash
curl -X GET "http://localhost:8000/api/user/assessments/?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Endpoints Summary

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health/analyze/` | POST | ✓ | Primary health analysis (authenticated) |
| `/assess/` | POST | ✗ | Health analysis (anonymous) |
| `/user/profile/` | GET | ✓ | Get user profile |
| `/user/profile/` | PUT | ✓ | Update user profile |
| `/user/statistics/` | GET | ✓ | Get user statistics |
| `/user/assessments/` | GET | ✓ | Get assessment history |
| `/user/assessments/{id}/` | GET | ✓ | Get assessment details |
| `/predict/top/` | POST | ✗ | Get top N predictions |
| `/status/` | GET | ✗ | System status |
| `/health/` | GET | ✗ | Health check |
| `/model/info/` | GET | ✗ | Model information |
| `/diseases/` | GET | ✗ | List supported diseases |

## Rate Limits

| User Type | Limit |
|-----------|-------|
| Authenticated | 10/min, 100/hour, 200/day |
| Anonymous | 5/hour |
| IP-based | 200/hour |

## Confidence Levels

| Level | Probability | Treatment Info |
|-------|-------------|----------------|
| LOW | < 55% | ✗ No |
| MEDIUM | 55-75% | ✓ Yes |
| HIGH | ≥ 75% | ✓ Yes |

## Common Request Bodies

### Health Assessment

```json
{
  "symptoms": ["symptom1", "symptom2"],
  "age": 35,
  "gender": "male",
  "additional_info": {
    "weight": 70,
    "height": 175
  }
}
```

### Profile Update

```json
{
  "display_name": "John Doe",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "medical_history": ["diabetes"],
  "allergies": ["penicillin"],
  "current_medications": ["metformin"]
}
```

## Common Response Structures

### Success Response

```json
{
  "status": "success",
  "confidence": "HIGH",
  "prediction": {
    "disease": "Disease Name",
    "probability": 0.78,
    "confidence": "HIGH"
  },
  "explanation": {...},
  "recommendations": {...},
  "treatment_info": {...}
}
```

### Error Response

```json
{
  "error": "error_type",
  "message": "Error message",
  "details": "Detailed information",
  "status_code": 400
}
```

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

## Python Example

```python
import requests

url = "http://localhost:8000/api/health/analyze/"
headers = {
    "Authorization": f"Bearer {firebase_token}",
    "Content-Type": "application/json"
}
data = {
    "symptoms": ["fever", "cough"],
    "age": 35,
    "gender": "male"
}

response = requests.post(url, json=data, headers=headers)
result = response.json()
```

## JavaScript Example

```javascript
const response = await fetch('http://localhost:8000/api/health/analyze/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${firebaseToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    symptoms: ['fever', 'cough'],
    age: 35,
    gender: 'male'
  })
});

const result = await response.json();
```

## Testing with Postman

1. Import collection from `postman_collection.json`
2. Set environment variable `firebase_token`
3. Run requests from the collection

## Interactive Documentation

Visit these URLs for interactive API exploration:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Need Help?

- Full documentation: See `API_DOCUMENTATION.md`
- Interactive docs: http://localhost:8000/api/docs/
- System status: http://localhost:8000/api/status/
