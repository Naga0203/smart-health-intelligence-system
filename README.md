# AI Health Intelligence Platform

A comprehensive health risk assessment platform combining machine learning predictions with multi-system treatment recommendations (Modern Medicine, Ayurveda, Homeopathy, and Lifestyle).

## 🏗️ Project Structure

```
.
├── backend/              # Django REST API backend
│   ├── agents/          # AI agent modules (orchestrator, explanation, etc.)
│   ├── api/             # API endpoints and views
│   ├── common/          # Shared utilities (Firebase, Gemini, cache)
│   ├── prediction/      # ML model integration
│   ├── treatment/       # Treatment knowledge base
│   ├── manage.py        # Django management script
│   ├── requirements.txt # Python dependencies
│   └── test_backend.py  # Comprehensive backend tests
│
├── frontend/            # React + TypeScript frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API and Firebase services
│   │   ├── stores/      # Zustand state management
│   │   ├── utils/       # Utility functions
│   │   └── theme/       # Material-UI theme
│   ├── package.json     # Node dependencies
│   └── README.md        # Frontend-specific documentation
│
└── .gitignore           # Git ignore rules
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Firebase account (for authentication)
- Google Gemini API key (for AI features)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with required variables:
```env
# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Django Settings
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start development server:
```bash
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file with required variables:
```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Firebase Configuration
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

4. Start development server:
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

## 🧪 Testing

### Backend Tests

Run comprehensive backend tests:
```bash
cd backend
python test_backend.py
```

This will test:
- Health check endpoints
- System status
- Authentication requirements
- API validation
- Anonymous assessments
- All public endpoints

### Frontend Tests

Frontend tests have been removed for production. The application has been thoroughly tested during development.

## 📚 API Documentation

API documentation is available at:
- Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
- ReDoc: `http://localhost:8000/api/schema/redoc/`
- OpenAPI Schema: `backend/api_schema.yml`

## 🔐 Security Features

- Firebase Authentication integration
- JWT token-based API authentication
- CSRF protection for state-changing operations
- Rate limiting (10/min, 100/hour, 200/day for authenticated users)
- Input sanitization and validation
- HTTPS enforcement in production
- Secure token storage

## 🎨 Key Features

### Backend
- Multi-agent AI system for health analysis
- ML-based disease prediction
- Treatment recommendations from 4 medical systems
- Firebase integration for user management
- Gemini AI for natural language explanations
- Comprehensive error handling and logging
- Rate limiting and throttling

### Frontend
- React 18 with TypeScript
- Material-UI component library
- Zustand state management
- Firebase authentication (Email/Password + Google OAuth)
- Responsive design (mobile, tablet, desktop)
- WCAG 2.1 AA accessibility compliance
- Progressive Web App features
- Offline support with service workers

## 🌐 Deployment

### Backend Deployment

1. Set environment variables in production
2. Set `DEBUG=False`
3. Configure `ALLOWED_HOSTS`
4. Set up PostgreSQL database (recommended for production)
5. Collect static files: `python manage.py collectstatic`
6. Use Gunicorn or uWSGI as WSGI server
7. Set up Nginx as reverse proxy

### Frontend Deployment

1. Build production bundle:
```bash
npm run build
```

2. Deploy `dist/` folder to:
   - Vercel
   - Netlify
   - AWS S3 + CloudFront
   - Any static hosting service

3. Configure environment variables in hosting platform

## 📝 Environment Variables

### Backend Required Variables
- `FIREBASE_CREDENTIALS_PATH` - Path to Firebase service account JSON
- `GEMINI_API_KEY` - Google Gemini API key
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed origins

### Frontend Required Variables
- `VITE_API_BASE_URL` - Backend API URL
- `VITE_FIREBASE_API_KEY` - Firebase API key
- `VITE_FIREBASE_AUTH_DOMAIN` - Firebase auth domain
- `VITE_FIREBASE_PROJECT_ID` - Firebase project ID
- `VITE_FIREBASE_STORAGE_BUCKET` - Firebase storage bucket
- `VITE_FIREBASE_MESSAGING_SENDER_ID` - Firebase messaging sender ID
- `VITE_FIREBASE_APP_ID` - Firebase app ID

## 🤝 Contributing

This is a private project. For any questions or issues, please contact the development team.

## 📄 License

Proprietary - All rights reserved

## 🔗 Additional Resources

- Backend API Documentation: `backend/API_DOCUMENTATION.md`
- Frontend Documentation: `frontend/README.md`
- Architecture Diagram: `ARCHITECTURE_DIAGRAM.md`

## ⚠️ Important Notes

1. **Never commit sensitive files:**
   - `.env` files
   - `firebase-credentials.json`
   - `db.sqlite3` database file
   - API keys or secrets

2. **Before pushing to GitHub:**
   - Verify `.gitignore` is properly configured
   - Remove any test data or logs
   - Ensure no credentials are in code
   - Check that `node_modules/` and `venv/` are ignored

3. **Production checklist:**
   - Set `DEBUG=False` in backend
   - Use environment variables for all secrets
   - Enable HTTPS
   - Configure proper CORS settings
   - Set up proper database (PostgreSQL recommended)
   - Configure CDN for frontend assets
   - Set up monitoring and logging

## 📞 Support

For technical support or questions, please contact the development team.
