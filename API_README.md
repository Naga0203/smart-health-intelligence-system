# API Documentation Guide

Welcome to the AI Health Intelligence API documentation!

## Documentation Resources

We provide multiple formats of API documentation to suit different needs:

### 1. Interactive Documentation (Recommended)

**Swagger UI** - Interactive API explorer with live testing
- URL: `http://localhost:8000/api/docs/`
- Features:
  - Try out API endpoints directly in the browser
  - See request/response examples
  - Test authentication
  - View all available endpoints
  - Auto-generated from code

**ReDoc** - Beautiful, responsive API documentation
- URL: `http://localhost:8000/api/redoc/`
- Features:
  - Clean, readable interface
  - Detailed endpoint descriptions
  - Code examples in multiple languages
  - Searchable documentation

**OpenAPI Schema** - Machine-readable API specification
- URL: `http://localhost:8000/api/schema/`
- Format: OpenAPI 3.0 (JSON)
- Use for: Code generation, testing tools, API clients

### 2. Written Documentation

**Comprehensive Guide** - [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md)
- Complete API reference
- Authentication guide
- Rate limiting details
- Code examples in Python, JavaScript, cURL
- Best practices
- Error handling
- Security considerations

**Quick Reference** - [`API_QUICK_REFERENCE.md`](./API_QUICK_REFERENCE.md)
- Quick endpoint reference
- Common request/response examples
- Rate limits summary
- HTTP status codes
- Quick start examples

### 3. Postman Collection

**Postman Collection** - [`postman_collection.json`](./postman_collection.json)
- Pre-configured API requests
- Environment variables setup
- Easy testing and exploration
- Import into Postman to get started

## Getting Started

### Step 1: Start the Server

```bash
python manage.py runserver
```

### Step 2: Access Interactive Documentation

Open your browser and navigate to:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

### Step 3: Authenticate (for protected endpoints)

1. Get a Firebase ID token from Firebase Authentication
2. Click "Authorize" in Swagger UI
3. Enter: `Bearer <your_firebase_id_token>`
4. Click "Authorize" to save

### Step 4: Try an Endpoint

1. Navigate to `/api/health/analyze/` in Swagger UI
2. Click "Try it out"
3. Modify the request body:
   ```json
   {
     "symptoms": ["fever", "cough"],
     "age": 35,
     "gender": "male"
   }
   ```
4. Click "Execute"
5. View the response

## Documentation Features

### Request Examples

All endpoints include multiple request examples:
- Basic usage
- Advanced usage with optional parameters
- Edge cases

### Response Examples

Each endpoint shows example responses for:
- Success scenarios (200)
- Different confidence levels (LOW, MEDIUM, HIGH)
- Error scenarios (400, 401, 403, 404, 429, 500, 503)

### Code Samples

Documentation includes code examples in:
- Python (requests library)
- JavaScript (Fetch API)
- cURL (command line)

### Authentication Guide

Detailed instructions for:
- Firebase Authentication setup
- Getting ID tokens
- Including tokens in requests
- Handling token expiration

### Rate Limiting

Complete information about:
- Rate limits for different user types
- Rate limit headers
- Handling rate limit errors
- Best practices for rate limit management

## API Overview

### Core Endpoints

**Health Analysis**
- `POST /api/health/analyze/` - Authenticated health analysis
- `POST /api/assess/` - Anonymous health analysis

**User Management**
- `GET /api/user/profile/` - Get user profile
- `PUT /api/user/profile/` - Update user profile
- `GET /api/user/statistics/` - Get user statistics

**Assessment History**
- `GET /api/user/assessments/` - List assessments (paginated)
- `GET /api/user/assessments/{id}/` - Get assessment details

**Predictions**
- `POST /api/predict/top/` - Get top N disease predictions

**System Information**
- `GET /api/status/` - System status
- `GET /api/health/` - Health check
- `GET /api/model/info/` - Model information
- `GET /api/diseases/` - List supported diseases

## Key Concepts

### Confidence Levels

The system uses three confidence levels:

- **LOW** (< 55%): Limited response, no treatment info
- **MEDIUM** (55-75%): Cautious guidance with treatment info
- **HIGH** (≥ 75%): Full information with comprehensive details

### Multi-System Treatment Information

Treatment information includes:
- **Allopathy**: Modern medicine approach
- **Ayurveda**: Traditional Indian medicine
- **Homeopathy**: Homeopathic approach
- **Lifestyle**: Diet, exercise, and wellness

### Ethical Safeguards

- System never claims to provide medical diagnosis
- All responses include medical disclaimers
- Treatment information only shown for MEDIUM/HIGH confidence
- Encourages professional consultation

## Testing the API

### Using Swagger UI

1. Navigate to http://localhost:8000/api/docs/
2. Authenticate with Firebase token
3. Try endpoints interactively
4. View responses in real-time

### Using Postman

1. Import `postman_collection.json`
2. Set `firebase_token` environment variable
3. Run requests from the collection

### Using cURL

```bash
# Health analysis
curl -X POST http://localhost:8000/api/health/analyze/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["fever"], "age": 35, "gender": "male"}'

# System status
curl http://localhost:8000/api/status/
```

### Using Python

```python
import requests

url = "http://localhost:8000/api/health/analyze/"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
data = {
    "symptoms": ["fever", "cough"],
    "age": 35,
    "gender": "male"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

## Documentation Updates

The API documentation is automatically generated from the code using drf-spectacular. When you update the API:

1. Add/update `@extend_schema` decorators in views
2. Update serializers with help text
3. Restart the server
4. Documentation updates automatically

### Regenerating OpenAPI Schema

```bash
python manage.py spectacular --file schema.yml
```

## Support

### Documentation Issues

If you find issues with the documentation:
1. Check the interactive docs for the latest information
2. Refer to the code comments in `api/views.py`
3. Review the serializers in `api/serializers.py`

### API Issues

For API functionality issues:
1. Check system status: `GET /api/status/`
2. Review error responses for details
3. Check server logs for detailed error information

## Additional Resources

- **Design Document**: `.kiro/specs/ai-health-intelligence/design.md`
- **Requirements**: `.kiro/specs/ai-health-intelligence/requirements.md`
- **Implementation Tasks**: `.kiro/specs/ai-health-intelligence/tasks.md`

## Version Information

- **API Version**: 1.0.0
- **Documentation Version**: 1.0.0
- **Last Updated**: 2026-02-10

## Legal Notice

This API provides health risk assessment for informational purposes only. It is NOT a substitute for professional medical advice. Always consult qualified healthcare providers for medical decisions.
