# Environment Setup Guide

## Overview

This guide explains how to set up all environment variables required for the AI Health Intelligence System. Each variable is mapped to its usage in the codebase.

## Quick Start

1. Copy `.env.example` to `.env`
2. Fill in the three REQUIRED variables
3. Run the server

```bash
cp .env.example .env
# Edit .env with your values
python manage.py runserver
```

## Required Environment Variables

### 1. DJANGO_SECRET_KEY

**Purpose**: Cryptographic signing for sessions, cookies, and security features

**How to Get**:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Where Used in Code**:
- `health_ai_backend/settings.py` → `SECRET_KEY`
- Used by Django for: sessions, CSRF tokens, password reset tokens

**Example**:
```bash
DJANGO_SECRET_KEY=django-insecure-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
```

**Security Notes**:
- Must be at least 50 characters
- Use different keys for development and production
- Never commit to version control
- Rotate every 90 days in production

---

### 2. FIREBASE_CREDENTIALS_PATH

**Purpose**: Authentication and data storage using Firebase

**How to Get**:

1. **Create Firebase Project**:
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Click "Add Project"
   - Enter project name (e.g., "health-ai-system")
   - Follow setup wizard

2. **Enable Authentication**:
   - Go to Authentication → Get Started
   - Enable "Google" sign-in method
   - Add authorized domains (localhost for dev)

3. **Enable Firestore**:
   - Go to Firestore Database → Create Database
   - Choose "Start in test mode" (development)
   - Select a location

4. **Download Credentials**:
   - Go to Project Settings (gear icon)
   - Click "Service Accounts" tab
   - Click "Generate New Private Key"
   - Save JSON file as `firebase-credentials.json`
   - Create `config/` folder in project root
   - Move file to `config/firebase-credentials.json`

**Where Used in Code**:
- `health_ai_backend/settings.py` → `FIREBASE_CREDENTIALS_PATH`
- `common/firebase_db.py` → `get_firebase_db()` function
- `common/firebase_auth.py` → `FirebaseAuthentication` class
- `api/views.py` → All authenticated endpoints

**Example**:
```bash
FIREBASE_CREDENTIALS_PATH=config/firebase-credentials.json
```

**File Structure**:
```
project-root/
├── config/
│   └── firebase-credentials.json  ← Place file here
├── .env
└── manage.py
```

**Security Notes**:
- Never commit credentials JSON to version control
- Add `config/` to `.gitignore`
- Use separate projects for dev/staging/production
- Set up Firestore security rules in production

**Cost**: Free tier includes:
- 50,000 document reads/day
- 20,000 document writes/day
- 1 GB storage

---

### 3. GEMINI_API_KEY

**Purpose**: AI-powered features (explanations, extraction, validation)

**How to Get**:

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Select or create a Google Cloud project
5. Copy the generated API key

**Where Used in Code**:
- `health_ai_backend/settings.py` → `GEMINI_API_KEY`
- `common/gemini_client.py` → `GeminiClient.__init__()`
- `agents/explanation.py` → `ExplanationAgent.explain()`
- `agents/data_extraction.py` → `DataExtractionAgent.extract()`

**Example**:
```bash
GEMINI_API_KEY=AIzaSyDe9eF_gmXt63hIdagwaOBaqKkx4fv6MMM
```

**Features Using Gemini**:
- Natural language symptom parsing
- Intelligent feature extraction
- Explanation generation
- Enhanced validation feedback

**Rate Limits** (Free Tier):
- 60 requests per minute
- 1,500 requests per day

**Security Notes**:
- Keep key secret
- Monitor usage at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Use separate keys for dev/production
- Implement caching to reduce API calls

---

## Optional Environment Variables

### 4. DEBUG

**Purpose**: Enable/disable debug mode

**Where Used in Code**:
- `health_ai_backend/settings.py` → `DEBUG`

**Values**:
- `True`: Development (shows detailed errors)
- `False`: Production (generic error pages)

**Default**: `True`

---

### 5. ALLOWED_HOSTS

**Purpose**: Security - which domains can serve the app

**Where Used in Code**:
- `health_ai_backend/settings.py` → `ALLOWED_HOSTS`

**Format**: Comma-separated list
```bash
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

**Default**: `localhost,127.0.0.1`

---

### 6. CORS_ALLOWED_ORIGINS

**Purpose**: Which frontend URLs can make API requests

**Where Used in Code**:
- `health_ai_backend/settings.py` → `CORS_ALLOWED_ORIGINS`

**Format**: Comma-separated list with protocols
```bash
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

**Default**: `http://localhost:3000,http://127.0.0.1:3000`

---

## Environment Variable to Code Mapping

### Complete Mapping Table

| Environment Variable | Settings Variable | Used In Files | Purpose |
|---------------------|-------------------|---------------|---------|
| `DJANGO_SECRET_KEY` | `settings.SECRET_KEY` | Django core | Cryptographic signing |
| `DEBUG` | `settings.DEBUG` | Django core | Debug mode |
| `ALLOWED_HOSTS` | `settings.ALLOWED_HOSTS` | Django core | Host validation |
| `FIREBASE_CREDENTIALS_PATH` | `settings.FIREBASE_CREDENTIALS_PATH` | `common/firebase_db.py`<br>`common/firebase_auth.py` | Firebase connection |
| `GEMINI_API_KEY` | `settings.GEMINI_API_KEY` | `common/gemini_client.py`<br>`agents/explanation.py`<br>`agents/data_extraction.py` | AI features |
| `CORS_ALLOWED_ORIGINS` | `settings.CORS_ALLOWED_ORIGINS` | Django CORS | Frontend access |

### Code References

#### settings.py
```python
from decouple import config

SECRET_KEY = config('DJANGO_SECRET_KEY', default='...')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', 
                       cast=lambda v: [s.strip() for s in v.split(',')])

FIREBASE_CREDENTIALS_PATH = config('FIREBASE_CREDENTIALS_PATH', 
                                   default='config/firebase-credentials.json')
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')

CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', 
                              default='http://localhost:3000',
                              cast=lambda v: [s.strip() for s in v.split(',')])
```

#### common/firebase_db.py
```python
import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings

def get_firebase_db():
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
    return firestore.client()
```

#### common/gemini_client.py
```python
import google.generativeai as genai
from django.conf import settings

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
```

---

## Configuration Files

### .env (Your Configuration)
- Contains actual values
- **Never commit to version control**
- Specific to your environment

### .env.example (Template)
- Contains placeholder values
- **Safe to commit to version control**
- Template for other developers

### .gitignore (Already Configured)
```
.env
config/firebase-credentials.json
*.json
```

---

## Setup Checklist

### Development Setup

- [ ] Copy `.env.example` to `.env`
- [ ] Generate Django secret key
- [ ] Create Firebase project
- [ ] Enable Firebase Authentication (Google)
- [ ] Enable Firestore Database
- [ ] Download Firebase credentials
- [ ] Place credentials in `config/firebase-credentials.json`
- [ ] Get Gemini API key
- [ ] Update `.env` with all three required variables
- [ ] Run `python manage.py runserver`
- [ ] Test with `curl http://localhost:8000/api/health/`

### Production Setup

- [ ] Generate new Django secret key (different from dev)
- [ ] Set `DEBUG=False`
- [ ] Configure production `ALLOWED_HOSTS`
- [ ] Create production Firebase project
- [ ] Download production Firebase credentials
- [ ] Get production Gemini API key
- [ ] Configure production `CORS_ALLOWED_ORIGINS`
- [ ] Enable HTTPS/SSL
- [ ] Set security cookies (`SESSION_COOKIE_SECURE=True`)
- [ ] Configure Firestore security rules
- [ ] Set up Redis for caching (optional)
- [ ] Configure monitoring and logging
- [ ] Set up automated backups

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'firebase_admin'"

**Solution**:
```bash
pip install firebase-admin
```

---

### Error: "Your default credentials were not found"

**Cause**: Firebase credentials not configured

**Solution**:
1. Check `FIREBASE_CREDENTIALS_PATH` in `.env`
2. Verify file exists at that path
3. Verify JSON file is valid
4. Check file permissions

---

### Error: "Authentication credentials were not provided"

**Cause**: Missing Firebase ID token

**Solution**:
1. Get Firebase ID token from frontend
2. Add to request header:
   ```
   Authorization: Bearer <firebase_id_token>
   ```

---

### Error: "Rate limit exceeded"

**Cause**: Too many requests to Gemini API

**Solution**:
1. Wait for rate limit to reset
2. Implement caching
3. Upgrade to paid tier if needed

---

### Error: "CORS error"

**Cause**: Frontend URL not in allowed origins

**Solution**:
1. Add frontend URL to `CORS_ALLOWED_ORIGINS`
2. Include protocol (http:// or https://)
3. Restart Django server

---

## Security Best Practices

### Development

1. **Use separate credentials** for dev/staging/production
2. **Never commit** `.env` or credentials files
3. **Rotate keys** regularly (every 90 days)
4. **Monitor usage** of API keys
5. **Use test mode** for Firebase in development

### Production

1. **Enable HTTPS** (SSL/TLS certificate)
2. **Set `DEBUG=False`**
3. **Use strong secret keys** (50+ characters)
4. **Configure Firestore security rules**
5. **Enable security cookies**
6. **Set up monitoring** and alerts
7. **Implement rate limiting**
8. **Regular security audits**
9. **Keep dependencies updated**
10. **Automated backups** for Firestore

---

## Cost Estimates

### Free Tier (Development)

**Firebase**:
- 50,000 reads/day
- 20,000 writes/day
- 1 GB storage
- **Cost**: $0/month

**Gemini API**:
- 60 requests/minute
- 1,500 requests/day
- **Cost**: $0/month

**Total**: $0/month for development

### Production Estimates

**Firebase** (Blaze Plan):
- $0.06 per 100,000 reads
- $0.18 per 100,000 writes
- $0.18/GB storage
- Estimated: $10-50/month

**Gemini API** (Pay-as-you-go):
- Varies by model and usage
- Estimated: $20-100/month

**Total**: $30-150/month for small-medium production

---

## Additional Resources

- [Firebase Console](https://console.firebase.google.com/)
- [Google AI Studio](https://makersuite.google.com/app/apikey)
- [Django Settings Documentation](https://docs.djangoproject.com/en/6.0/ref/settings/)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Gemini API Documentation](https://ai.google.dev/docs)

---

## Support

For issues or questions:
1. Check this guide
2. Review `API_TESTING_GUIDE.md`
3. Check server logs in `logs/health_ai.log`
4. Review Django error pages (if DEBUG=True)

---

**Last Updated**: February 10, 2026  
**Version**: 1.0
