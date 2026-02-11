# AI Health Intelligence Platform - Backend

Django REST API backend for the AI Health Intelligence Platform.

## Overview

This backend provides:
- Multi-disease prediction using ML models
- Firebase authentication integration
- Health risk assessment API
- Treatment recommendations (Allopathy, Ayurveda, Homeopathy, Lifestyle)
- User profile and assessment history management
- Rate limiting and throttling
- System health monitoring

## Technology Stack

- **Framework**: Django 4.x + Django REST Framework
- **Authentication**: Firebase Admin SDK
- **ML**: PyTorch, scikit-learn
- **AI**: Google Gemini API
- **Database**: SQLite (development), PostgreSQL (production)
- **Python**: 3.8+

## Project Structure

```
backend/
├── agents/                    # AI agent modules
│   ├── base_agent.py         # Base agent class
│   ├── orchestrator.py       # Main orchestration logic
│   ├── data_extraction.py    # Data extraction agent
│   ├── explanation.py        # Explanation generation
│   ├── recommendation.py     # Recommendation agent
│   └── validation.py         # Validation agent
│
├── api/                       # REST API endpoints
│   ├── views.py              # API views
│   ├── serializers.py        # DRF serializers
│   ├── urls.py               # URL routing
│   ├── throttling.py         # Rate limiting
│   └── tests/                # API tests
│
├── common/                    # Shared utilities
│   ├── firebase_auth.py      # Firebase authentication
│   ├── firebase_db.py        # Firebase database
│   └── gemini_client.py      # Gemini AI client
│
├── prediction/                # ML prediction module
│   ├── predictor.py          # Disease predictor
│   └── multi_disease_predictor.py
│
├── treatment/                 # Treatment information
│   └── knowledge_base.py     # Treatment knowledge base
│
├── health_ai_backend/         # Django project settings
│   ├── settings.py           # Main settings
│   ├── urls.py               # Root URL config
│   └── wsgi.py               # WSGI config
│
├── templates/                 # HTML templates
├── logs/                      # Application logs
├── utils/                     # Utility functions
├── manage.py                  # Django management
├── requirements.txt           # Python dependencies
└── .env                       # Environment variables
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### 2. Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required environment variables:
- `GEMINI_API_KEY` - Google Gemini API key
- `FIREBASE_CREDENTIALS_PATH` - Path to Firebase service account JSON
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated allowed hosts

### 4. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 5. Setup ML Model

```bash
# Setup multi-disease prediction model
python setup_multi_disease_model.py
```

### 6. Run Development Server

```bash
python manage.py runserver
```

The API will be available at: http://localhost:8000

## API Endpoints

### Health Analysis
- `POST /api/health/analyze/` - Authenticated health analysis
- `POST /api/assess/` - Anonymous health assessment

### User Management
- `GET /api/user/profile/` - Get user profile
- `PUT /api/user/profile/` - Update user profile
- `GET /api/user/statistics/` - Get user statistics
- `GET /api/user/assessments/` - Get assessment history
- `GET /api/user/assessments/{id}/` - Get assessment detail

### Predictions
- `POST /api/predict/top/` - Get top N disease predictions

### System
- `GET /api/status/` - System status
- `GET /api/health/` - Health check
- `GET /api/model/info/` - Model information
- `GET /api/diseases/` - Supported diseases list

### Documentation
- `GET /api/docs/` - API documentation (Swagger UI)
- `GET /api/schema/` - OpenAPI schema

## Rate Limits

### Authenticated Users
- 10 requests per minute (burst)
- 100 requests per hour (sustained)
- 200 requests per day (daily limit)

### Anonymous Users
- 5 requests per hour

## Testing

```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test api.tests

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Authentication

The backend uses Firebase Authentication. Clients must include a Firebase ID token in the Authorization header:

```
Authorization: Bearer <firebase-id-token>
```

## Response Format

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": { ... },
  "status_code": 400
}
```

## Confidence Levels

The system uses three confidence levels:
- **LOW** (<55%): Limited reliability, minimal information provided
- **MEDIUM** (55-75%): Moderate confidence, cautious guidance
- **HIGH** (≥75%): High confidence, full details provided

## Logging

Logs are stored in `logs/health_ai.log` with the following levels:
- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical issues

## Production Deployment

### Environment Variables
Set all required environment variables in production:
- Set `DEBUG=False`
- Configure `ALLOWED_HOSTS`
- Use PostgreSQL instead of SQLite
- Set secure `SECRET_KEY`

### Security Checklist
- [ ] DEBUG mode disabled
- [ ] Secret key is secure and not in version control
- [ ] HTTPS enabled
- [ ] CORS configured properly
- [ ] Rate limiting enabled
- [ ] Firebase credentials secured
- [ ] Database backups configured

### Recommended Hosting
- AWS EC2 / Elastic Beanstalk
- Google Cloud Run / App Engine
- Heroku
- DigitalOcean App Platform

## Troubleshooting

### Common Issues

**Issue**: Module not found errors
**Solution**: Ensure virtual environment is activated and dependencies installed

**Issue**: Firebase authentication fails
**Solution**: Verify `firebase-credentials.json` path in `.env`

**Issue**: ML model not loading
**Solution**: Run `python setup_multi_disease_model.py`

**Issue**: Database errors
**Solution**: Run `python manage.py migrate`

## Support

For issues and questions:
- Check API documentation: http://localhost:8000/api/docs/
- Review logs in `logs/health_ai.log`
- See main project README in root directory

## License

[Your License Here]
