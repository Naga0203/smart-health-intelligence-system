# AI Health Intelligence Platform - Project Structure

## Overview

This document provides a comprehensive overview of the project structure, organized into three main sections:
1. **Backend** - Django REST API
2. **Frontend** - React TypeScript application
files and configuration

## Root Directory Structure

```
ai-health-intelligence/
├── backend/                   # Django REST API backend
├── frontend/                  # React TypeScript frontend
├── .kiro/                     # Kiro specs and configuration
├── firebase-credentials.json  # Firebase service account (shared)
├── .gitignore                # Git ignore rules
├── .env.example              # Environment template
├── README.md                 # Main documentation
├── PROJECT_STRUCTURE.md      # This file
└── START_SERVERS.md          # Quick start guide
```

---

## Backend Structure (`backend/`)

### Overview
Django REST API with multi-agent AI architecture for health risk assessment.

### Directory Layout

```
backend/
├── agents/                    # AI Agent Modules
│   ├── __init__.py
│   ├── base_agent.py         # Base agent class with common functionality
│   ├── orchestrator.py       # Main orchestration logic
│   ├── data_extraction.py    # Extract data from inputs
│   ├── explanation.py        # Generate AI explanations
│   ├── recommendation.py     # Generate recommendations
│   ├── validation.py         # Validate inputs and outputs
│py             # Django models
│   ├── views.py              # Agent-related views
│   ├── admin.py              # Django admin configuration
│   ├── apps.py               # App configuration
│   ├── tests.py              # Agent tests
│   └── migrations/           # Database migraions
│
├── api/                       # REST API Layer
│   ├── __init__.py
│   ├── views.py              # API view functions
│   ├── serializers.py        # DRF serializers
│   ├── urls.py               # URL routing
│ttling.py         # Rate limiting configuration
│   ├── landing.py            # Landing page view
│   ├── models.py             # API models
│   ├── admin.py              # Django admin
│   ├── apps.py               # App configuration
│   ├── tests.py              # General API tests
│   ├── test_health_analysis_api.py  # Health analysis tests
│   ├── test_rate_limiting.py        # Rate limit tests
│   ├── test_throttling_unit.py      # Throttling unitests
│   └── migrations/           # Database migrations
│
├── common/                    # Shared Utilities
│   ├── __init__.py
│   ├── firebase_auth.py      # Firebase authentication backend
│   ├── firebase_db.py        # Firebase database operations
│   ├── gemini_client.py      # Google Gemini AI client
│   ├── models.py             # Common models
│   ├── views.py              # Common views
│   ├── admin.py              # Django admin
│   ├── apps.py               # App configuration
│   ├── tests.py              # Common tests
rations/           # Database migrations
│
├── prediction/                # ML Prediction Module
│   ├── __init__.py
│   ├── predictor.py          # Single disease predictor
│   ├── multi_disease_predictor.py  # Multi-disease predictor
│   ├── models.py             # Prediction models
│   ├── views.py              # Prediction views
│   ├── admin.py              # Django admin
│   ├── apps.py            figuration
│   ├── tests.py              # Prediction tests
│   └── migrations/           # Database migrations
│
├── treatment/                 # Treatment Information
│   ├── __init__.py
│   ├── knowledge_base.py     # Treatment knowledge base
│   ├── models.py             # Treatment models
│   ├── views.py              # Treatment views
│   ├── admin.py              # Django admin
│   ├── apps.py               # App configuration
│   ├── tests.py              # Treatment tests
    # Database migrations
│
├── health_ai_backend/         # Django Project Settings
│   ├── __init__.py
│   ├── settings.py           # Main Django settings
│   ├── urls.py               # Root URL configuration
│   ├── wsgi.py               # WSGI application
│   └── asgi.py               # ASGI application
│
├── templates/                 # HTML Templates
│   └── landing.html          # Landing page template
│
├── logs/                      # Application Logs
│   └── he log
│
├── utils/                     # Utility Functions
│   ├── __init__.py
│   └── dataset_analyzer.py   # Dataset analysis utilities
│
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not in git)
├── .env.example              # Environment template
├── db.sqlite3                # SQLite database (development)
├── check_models.py           # Model verification script
├── setup__model.py  # ML model setup script
├── test_api_endpoints.py     # API endpoint tests
├── test_application.py       # Application tests
├── test_comprehensive.py     # Comprehensive tests
├── test_scenarios.py         # Scenario tests
├── test_with_api_keys.py     # API key tests
├── test_requests.json        # Test request data
└── README.md                 # Backend documentation
```

### Key Backend Files

| File | Purpose |
|------|---------|
| `manage.py` | Django management commands |
| `requirements.txt` | Python package dependencies |
| `.env` | Environment configuration (secrets) |
| `db.sqlite3` | SQLite database (development) |
| `agents/orchestrator.py` | Main AI orchestration logic |
| `api/views.py` | REST API endpoints |
| `api/throttling.py` | Rate limiting configuration |
| `common/firebase_auth.py` | Firebase authentication |
| `common/gemini_client.py` | Gemini AI integration |
| `prediction/multi_disease_predictor.py` | ML prediction engine |

---

## Frontend Structure (`frontend/`)

### Overview
React 18 + TypeScript single-page application with Material-UI components.

### Directory Layout

```
frontend/
├── src/                       # Source Code
│   ├── components/           # React Components
│   │   ├── assessment/       # Assessment flow components
│   │   ├── auth/             # Authentication components
│   │   ├── common/           # Reusable common components
│   │   ├── dashboard/        # Dashboard components
│   │   ├── history/          # Assessment history components
│   │   ├── layout/           # Layout components (Header, Sidebar, Footer)
│   │   ├── profile/          # User profile components
│   │   ├── results/          # Results display components
│   │   ├── treatment/        # Treatment information components
│   │   └── upload/           # File upload components
│   │
│   ├── pages/                # Page Components
│   │   ├── LandingPage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── NewAssessmentPage.tsx
│   │   ├── AssessmentResultsPage.tsx
sessmentHistoryPage.tsx
│   │   ├── ProfilePage.tsx
│   │   ├── UploadReportPage.tsx
│   │   └── DiseasesPage.tsx
│   │
│   ├── services/             # External Services
│   │   ├── firebase.ts       # Firebase authentication service
│   │   └── api.ts            # Backend API service
│   │
│   ├── stores/               # Zustand State Stores
│   │   ├── authStore.ts      # Authentication state
│   │   ├── userStore.ts      # User profile state
│   │   ├── assessmentStore.ts # Assessment state
│   │   ├── systemStore.ts    # System status state
│   │   └── notificationStore.ts # Notification state
│   │
│   ├── routes/               # Routing Configuration
│   │   └── index.tsx         # React Router setup
│   │
│   ├── types/                # TypeScript Definitions
│   │   └── index.ts          # All type definitions
│   │
│   ├── utils/                # Utility Functions
│   │   ├── errorHandler.ts   # Error handling utilities
│   │   ├── validators.ts     # Input validation
│   │  a formatting
│   │
│   ├── App.tsx               # Root application component
│   ├── App.css               # Global application styles
│   ├── main.tsx              # Application entry point
│   ├── index.css             # Global CSS
│   └── vite-env.d.ts         # Vite environment types
│
├── public/                    # Static Assets
│   └── vite.svg              # Vite logo
│
├── node_modules/             # Node dependencies (not in git)
├── package.json              # Node dependencies and scripts
├── package-lock.json         # Locked dependency versions
├── tsconfig.json             # TypeScript configuration
├── tsconfig.app.json         # App-specific TS config
├── tsconfig.node.json        # Node-specific TS config
├── vite.config.ts            # Vite build configuration
├── eslint.config.js          # ESLint configuration
├── .env                      # Environment variables (not in git)
├── .env.example              # Environment template
d/README.md`
- **Frontend Documentation**: `frontend/README.md`
- **API Documentation**: http://localhost:8000/api/docs/
- **Frontend Spec**: `.kiro/specs/ai-health-frontend/`
- **Quick Start**: `START_SERVERS.md`
te
```

### Frontend Build
```bash
cd frontend
npm install
npm run build
# Output: frontend/dist/
```

---

## Version Control

### Ignored Files
- `backend/.env`
- `frontend/.env`
- `backend/db.sqlite3`
- `frontend/node_modules/`
- `backend/__pycache__/`
- `backend/*.pyc`
- `frontend/dist/`
- `logs/*.log`

### Tracked Files
- All source code
- Configuration templates (`.env.example`)
- Documentation
- `firebase-credentials.json` (if not sensitive)

---

## Additional Resources

- **Backend Documentation**: `backenpy
│   └── test_throttling_unit.py
├── common/tests.py
├── prediction/tests.py
├── treatment/tests.py
├── test_api_endpoints.py
├── test_application.py
├── test_comprehensive.py
└── test_scenarios.py
```

### Frontend Tests (To be implemented)
```
frontend/src/
├── components/__tests__/
├── services/__tests__/
├── stores/__tests__/
└── utils/__tests__/
```

---

## Build and Deployment

### Backend Build
```bash
cd backend
pip install -r requirements.txt
python manage.py collectstatic
python manage.py migra
- `GET /api/user/assessments/` - Get history
- `GET /api/user/assessments/{id}/` - Get detail

### System
- `GET /api/status/` - System status
- `GET /api/health/` - Health check
- `GET /api/model/info/` - Model info
- `GET /api/diseases/` - Disease list

### Documentation
- `GET /api/docs/` - Swagger UI
- `GET /api/schema/` - OpenAPI schema

---

## Testing Structure

### Backend Tests
```
backend/
├── agents/tests.py
├── api/
│   ├── tests.py
│   ├── test_health_analysis_api.py
│   ├── test_rate_limiting.MAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
```

---

## API Endpoints

### Health Analysis
- `POST /api/health/analyze/` - Authenticated analysis
- `POST /api/assess/` - Anonymous assessment

### User Management
- `GET /api/user/profile/` - Get profile
- `PUT /api/user/profile/` - Update profile
- `GET /api/user/statistics/` - Get statisticsend
                ↓
            UI Update
```

---

## Environment Variables

### Backend (`.env`)
```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Firebase
FIREBASE_CREDENTIALS_PATH=../firebase-credentials.json

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# Database
DATABASE_URL=sqlite:///db.sqlite3
```

### Frontend (`.env`)
```env
# Backend API
VITE_API_BASE_URL=http://localhost:8000

# Firebase Web SDK
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOtion tasks
```

---

## Data Flow

### Authentication Flow
```
User → Frontend (Firebase Web SDK) → Firebase Auth → Backend (Firebase Admin SDK) → API
```

### Assessment Flow
```
User Input → Frontend → Backend API → Orchestrator Agent → 
  ├── Data Extraction Agent
  ├── Prediction Agent (ML Model)
  ├── Explanation Agent (Gemini AI)
  ├── Recommendation Agent
  └── Validation Agent
→ Response → Frontend → User
```

### State Management Flow (Frontend)
```
User Action → Component → Zustand Store → API Service → BackRVERS.md` | Quick start guide |
| `SETUP_COMPLETE.md` | Setup completion summary |

### Kiro Specifications

```
.kiro/
└── specs/
    ├── ai-health-frontend/
    │   ├── requirements.md    # Frontend requirements
    │   ├── design.md          # Frontend design document
    │   └── tasks.md           # Implementation tasks
    │
    └── ai-health-intelligence/
        ├── requirements.md    # Backend requirements
        ├── design.md          # Backend design document
        └── tasks.md           # ImplementaDependencies and scripts |
| `.env` | Environment variables |

---

## Shared Files (Root Level)

### Configuration Files

| File | Purpose |
|------|---------|
| `firebase-credentials.json` | Firebase service account credentials (backend) |
| `.gitignore` | Git ignore patterns |
| `.env.example` | Environment variable template |

### Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Main project documentation |
| `PROJECT_STRUCTURE.md` | This file - detailed structure |
| `START_SE           # HTML entry point
└── README.md                 # Frontend documentation
```

### Key Frontend Files

| File | Purpose |
|------|---------|
| `src/main.tsx` | Application entry point |
| `src/App.tsx` | Root component |
| `src/services/firebase.ts` | Firebase authentication |
| `src/services/api.ts` | Backend API client |
| `src/types/index.ts` | TypeScript type definitions |
| `src/stores/authStore.ts` | Authentication state management |
| `vite.config.ts` | Build configuration |
| `package.json` | ├── .gitignore                # Git ignore rules
├── index.html     