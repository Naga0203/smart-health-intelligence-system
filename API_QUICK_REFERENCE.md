# API Quick Reference

## Base URL
```
http://localhost:8000/api/
```

## Main Endpoints

### 1. Health Assessment ⭐ MAIN ENDPOINT
```http
POST /api/assess/
```
```json
{
  "symptoms": ["fever", "cough", "headache"],
  "age": 35,
  "gender": "male"
}
```
**Returns**: Complete assessment with disease prediction, explanation, and recommendations

---

### 2. Top N Predictions
```http
POST /api/predict/top/
```
```json
{
  "symptoms": ["fever", "cough"],
  "age": 35,
  "gender": "male",
  "n": 5
}
```
**Returns**: Top 5 disease predictions with probabilities

---

### 3. System Status
```http
GET /api/status/
```
**Returns**: System health and component status

---

### 4. Health Check
```http
GET /api/health/
```
**Returns**: Simple health status

---

### 5. Model Info
```http
GET /api/model/info/
```
**Returns**: Model type, features, diseases count

---

### 6. Diseases List
```http
GET /api/diseases/
```
**Returns**: All 715 supported diseases

---

## Quick Start (JavaScript)

```javascript
// Health Assessment
const response = await fetch('http://localhost:8000/api/assess/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    symptoms: ['fever', 'cough', 'headache'],
    age: 35,
    gender: 'male'
  })
});

const data = await response.json();
console.log(data.prediction.disease);
console.log(data.prediction.probability_percent + '%');
console.log(data.explanation.text);
```

---

## Response Format

```json
{
  "user_id": "...",
  "assessment_id": "...",
  "prediction": {
    "disease": "Influenza",
    "probability": 0.85,
    "probability_percent": 85.0,
    "confidence": "HIGH"
  },
  "explanation": {
    "text": "...",
    "confidence": "HIGH"
  },
  "recommendations": {
    "items": ["...", "..."],
    "urgency": "HIGH"
  },
  "metadata": {
    "processing_time_seconds": 0.45,
    "timestamp": "..."
  }
}
```

---

## Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Full Docs**: `API_DOCUMENTATION.md`

---

## CORS Enabled For

- http://localhost:3000 (React)
- http://localhost:5173 (Vite)
- http://localhost:8080 (Vue)

---

## Rate Limits

- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour
