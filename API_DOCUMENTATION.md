# API Documentation - AI Health Intelligence System

Complete REST API documentation for frontend integration.

---

## Base URL

```
http://localhost:8000/api/
```

For production, replace with your deployed URL.

---

## Authentication

Currently, the API is open (no authentication required). For production, you should add authentication.

---

## API Endpoints

### 1. Health Assessment (Main Endpoint)

**Endpoint**: `POST /api/assess/`

**Description**: Perform complete health assessment based on symptoms. Returns disease prediction, explanation, and recommendations.

**Request Body**:
```json
{
  "symptoms": ["fever", "cough", "headache", "fatigue"],
  "age": 35,
  "gender": "male",
  "user_id": "optional_user_123",
  "additional_info": {
    "weight": 70,
    "height": 175,
    "bmi": 22.9
  }
}
```

**Request Fields**:
- `symptoms` (required): Array of symptom strings
- `age` (required): Integer, 1-120
- `gender` (required): String, one of: "male", "female", "other"
- `user_id` (optional): String, for tracking user sessions
- `additional_info` (optional): Object with additional health data

**Response** (200 OK):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "assessment_id": "698997e4b88d71bd2e8e6214",
  "prediction": {
    "disease": "Influenza",
    "probability": 0.8523,
    "probability_percent": 85.23,
    "confidence": "HIGH",
    "model_version": "1.0"
  },
  "extraction": {
    "confidence": 0.85,
    "method": "gemini_ai_extraction"
  },
  "explanation": {
    "text": "Based on your symptoms of fever, cough, headache, and fatigue, there is an 85.23% probability that you may have Influenza. This assessment has HIGH confidence...",
    "generated_by": "gemini-2.5-flash",
    "confidence": "HIGH"
  },
  "recommendations": {
    "items": [
      "Consult with a healthcare professional immediately",
      "Get plenty of rest and stay hydrated",
      "Monitor your temperature regularly",
      "Avoid contact with others to prevent spread"
    ],
    "urgency": "HIGH",
    "confidence": "HIGH"
  },
  "metadata": {
    "processing_time_seconds": 0.45,
    "timestamp": "2026-02-09T10:30:45.123456",
    "storage_ids": {
      "symptom_id": "...",
      "prediction_id": "...",
      "explanation_id": "...",
      "recommendation_id": "..."
    },
    "pipeline_version": "v1.0"
  }
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "Invalid input",
  "details": {
    "age": ["This field is required."],
    "symptoms": ["This field may not be empty."]
  }
}
```

**Example Usage (JavaScript)**:
```javascript
const response = await fetch('http://localhost:8000/api/assess/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    symptoms: ['fever', 'cough', 'headache'],
    age: 35,
    gender: 'male'
  })
});

const data = await response.json();
console.log('Predicted disease:', data.prediction.disease);
console.log('Probability:', data.prediction.probability_percent + '%');
```

---

### 2. Top N Predictions

**Endpoint**: `POST /api/predict/top/`

**Description**: Get top N disease predictions ranked by probability.

**Request Body**:
```json
{
  "symptoms": ["fever", "cough", "headache"],
  "age": 35,
  "gender": "male",
  "n": 5
}
```

**Request Fields**:
- `symptoms` (required): Array of symptom strings
- `age` (required): Integer, 1-120
- `gender` (required): String, one of: "male", "female", "other"
- `n` (optional): Integer, 1-20, default: 5

**Response** (200 OK):
```json
[
  {
    "disease": "Influenza",
    "probability": 0.8523,
    "rank": 1
  },
  {
    "disease": "Common Cold",
    "probability": 0.7234,
    "rank": 2
  },
  {
    "disease": "COVID-19",
    "probability": 0.6891,
    "rank": 3
  },
  {
    "disease": "Pneumonia",
    "probability": 0.5432,
    "rank": 4
  },
  {
    "disease": "Bronchitis",
    "probability": 0.4567,
    "rank": 5
  }
]
```

**Example Usage (JavaScript)**:
```javascript
const response = await fetch('http://localhost:8000/api/predict/top/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    symptoms: ['fever', 'cough'],
    age: 35,
    gender: 'male',
    n: 5
  })
});

const predictions = await response.json();
predictions.forEach(pred => {
  console.log(`${pred.rank}. ${pred.disease}: ${(pred.probability * 100).toFixed(1)}%`);
});
```

---

### 3. System Status

**Endpoint**: `GET /api/status/`

**Description**: Get system status and component health.

**Response** (200 OK):
```json
{
  "status": "operational",
  "version": "1.0",
  "components": {
    "orchestrator": {
      "status": "operational",
      "agent_type": "OrchestratorAgent"
    },
    "validation_agent": {
      "status": "operational",
      "llm_available": false
    },
    "extraction_agent": {
      "status": "operational",
      "llm_available": false
    },
    "explanation_agent": {
      "status": "operational",
      "llm_available": false
    },
    "prediction_engine": {
      "supported_diseases": ["Fungal infection", "Allergy", ...],
      "model_version": "1.0"
    },
    "database": {
      "connected": true
    }
  },
  "timestamp": "2026-02-09T10:30:45.123456"
}
```

**Example Usage (JavaScript)**:
```javascript
const response = await fetch('http://localhost:8000/api/status/');
const status = await response.json();

if (status.status === 'operational') {
  console.log('System is operational');
} else {
  console.log('System has issues');
}
```

---

### 4. Health Check

**Endpoint**: `GET /api/health/`

**Description**: Simple health check endpoint for monitoring.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-02-09T10:30:45.123456"
}
```

**Example Usage (JavaScript)**:
```javascript
const response = await fetch('http://localhost:8000/api/health/');
const health = await response.json();
console.log('API Status:', health.status);
```

---

### 5. Model Information

**Endpoint**: `GET /api/model/info/`

**Description**: Get information about the loaded ML model.

**Response** (200 OK):
```json
{
  "model_loaded": true,
  "model_type": "pytorch",
  "num_features": 132,
  "num_diseases": 715,
  "device": "cuda",
  "model_version": "1.0",
  "config_loaded": true
}
```

**Example Usage (JavaScript)**:
```javascript
const response = await fetch('http://localhost:8000/api/model/info/');
const modelInfo = await response.json();

console.log('Model Type:', modelInfo.model_type);
console.log('Diseases:', modelInfo.num_diseases);
console.log('Device:', modelInfo.device);
```

---

### 6. Diseases List

**Endpoint**: `GET /api/diseases/`

**Description**: Get list of all supported diseases.

**Response** (200 OK):
```json
{
  "total": 715,
  "diseases": [
    "Fungal infection",
    "Allergy",
    "GERD",
    "Chronic cholestasis",
    "Drug Reaction",
    "Peptic ulcer disease",
    "AIDS",
    "Diabetes",
    "Gastroenteritis",
    "Bronchial Asthma",
    ...
  ]
}
```

**Example Usage (JavaScript)**:
```javascript
const response = await fetch('http://localhost:8000/api/diseases/');
const data = await response.json();

console.log(`Total diseases: ${data.total}`);
data.diseases.forEach(disease => {
  console.log(`- ${disease}`);
});
```

---

## API Documentation UI

### Swagger UI
Interactive API documentation with "Try it out" feature:
```
http://localhost:8000/api/docs/
```

### ReDoc
Clean, responsive API documentation:
```
http://localhost:8000/api/redoc/
```

### OpenAPI Schema
Raw OpenAPI 3.0 schema (JSON):
```
http://localhost:8000/api/schema/
```

---

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:3000` (React default)
- `http://localhost:5173` (Vite default)
- `http://localhost:8080` (Vue default)

To add more origins, update `CORS_ALLOWED_ORIGINS` in `settings.py`.

---

## Rate Limiting

Default rate limits:
- **Anonymous users**: 100 requests/hour
- **Authenticated users**: 1000 requests/hour

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid input",
  "details": {
    "field_name": ["Error message"]
  }
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "details": "Error description"
}
```

---

## Frontend Integration Examples

### React Example

```javascript
import { useState } from 'react';

function HealthAssessment() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const assessHealth = async (symptoms, age, gender) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/assess/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ symptoms, age, gender })
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Assessment failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {loading && <p>Analyzing...</p>}
      {result && (
        <div>
          <h2>Predicted Disease: {result.prediction.disease}</h2>
          <p>Probability: {result.prediction.probability_percent}%</p>
          <p>Confidence: {result.prediction.confidence}</p>
          <p>Explanation: {result.explanation.text}</p>
        </div>
      )}
    </div>
  );
}
```

### Vue Example

```vue
<template>
  <div>
    <div v-if="loading">Analyzing...</div>
    <div v-if="result">
      <h2>Predicted Disease: {{ result.prediction.disease }}</h2>
      <p>Probability: {{ result.prediction.probability_percent }}%</p>
      <p>Confidence: {{ result.prediction.confidence }}</p>
      <p>Explanation: {{ result.explanation.text }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      result: null,
      loading: false
    };
  },
  methods: {
    async assessHealth(symptoms, age, gender) {
      this.loading = true;
      try {
        const response = await fetch('http://localhost:8000/api/assess/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ symptoms, age, gender })
        });
        
        this.result = await response.json();
      } catch (error) {
        console.error('Assessment failed:', error);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

### Axios Example

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Health assessment
const assessHealth = async (symptoms, age, gender) => {
  try {
    const response = await api.post('assess/', {
      symptoms,
      age,
      gender
    });
    return response.data;
  } catch (error) {
    console.error('Assessment failed:', error);
    throw error;
  }
};

// Get top predictions
const getTopPredictions = async (symptoms, age, gender, n = 5) => {
  try {
    const response = await api.post('predict/top/', {
      symptoms,
      age,
      gender,
      n
    });
    return response.data;
  } catch (error) {
    console.error('Prediction failed:', error);
    throw error;
  }
};

// Check system status
const getSystemStatus = async () => {
  try {
    const response = await api.get('status/');
    return response.data;
  } catch (error) {
    console.error('Status check failed:', error);
    throw error;
  }
};

export { assessHealth, getTopPredictions, getSystemStatus };
```

---

## Testing the API

### Using cURL

```bash
# Health assessment
curl -X POST http://localhost:8000/api/assess/ \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["fever", "cough", "headache"],
    "age": 35,
    "gender": "male"
  }'

# Top predictions
curl -X POST http://localhost:8000/api/predict/top/ \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["fever", "cough"],
    "age": 35,
    "gender": "male",
    "n": 5
  }'

# System status
curl http://localhost:8000/api/status/

# Health check
curl http://localhost:8000/api/health/

# Model info
curl http://localhost:8000/api/model/info/

# Diseases list
curl http://localhost:8000/api/diseases/
```

### Using Python requests

```python
import requests

# Health assessment
response = requests.post('http://localhost:8000/api/assess/', json={
    'symptoms': ['fever', 'cough', 'headache'],
    'age': 35,
    'gender': 'male'
})

data = response.json()
print(f"Predicted disease: {data['prediction']['disease']}")
print(f"Probability: {data['prediction']['probability_percent']}%")
```

---

## Running the API Server

```bash
# Start Django development server
python manage.py runserver

# Or specify port
python manage.py runserver 8000

# Access API at:
# http://localhost:8000/api/
```

---

## Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/assess/` | POST | Main health assessment |
| `/api/predict/top/` | POST | Get top N predictions |
| `/api/status/` | GET | System status |
| `/api/health/` | GET | Health check |
| `/api/model/info/` | GET | Model information |
| `/api/diseases/` | GET | List all diseases |
| `/api/docs/` | GET | Swagger UI |
| `/api/redoc/` | GET | ReDoc UI |
| `/api/schema/` | GET | OpenAPI schema |

---

**Base URL**: `http://localhost:8000/api/`  
**Documentation**: `http://localhost:8000/api/docs/`  
**Version**: 1.0
