# AI Health Intelligence Platform

A medical-grade AI-powered health risk assessment system with multi-agent architecture, Firebase authentication, and ethical AI principles.

## 🏗️ Architecture

- **Backend**: Django REST API with Firebase Authentication
- **Frontend**: React + TypeScript with Material-UI
- **AI**: Multi-agent system with Google Gemini
- **ML**: PyTorch multi-disease prediction model
- **Database**: Firebase Firestore
- **Authentication**: Firebase Auth (Email/Password + Google OAuth)

## 📁 Project Structure

```
ai-health-intelligence/
├── backend/                   # Django REST API backend
│   ├── agents/               # AI agent modules
│   ├── api/                  # REST API endpoints
│   ├── common/               # Shared utilities
│   ├── prediction/           # ML prediction module
│   ├── treatment/            # Treatment information
│   ├── health_ai_backend/    # Django settings
│   ├── manage.py             # Django management
│   ├── requirements.txt      # Python dependencies
│   ├── .env                  # Backend environment variables
│   └── README.md             # Backend documentation
│
├── frontend/                  # React TypeScript frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API & Firebase services
│   │   ├── stores/           # Zustand state stores
│   │   ├── types/            # TypeScript definitions
│   │   └── utils/            # Utility functions
│   ├── package.json          # Node dependencies
│   ├── vite.config.ts        # Vite configuration
│   ├── .env                  # Frontend environment variables
│   └── README.md             # Frontend documentation
│
├── .kiro/                     # Kiro specs and configuration
│   └── specs/                # Feature specifications
│
├── firebase-credentials.json  # Firebase service account (shared)
├── .gitignore                # Git ignore rules
├── .env.example              # Environment template
├── README.md                 # This file
├── PROJECT_STRUCTURE.md      # Detailed structure
└── START_SERVERS.md          # Quick start guide
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed structure.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Firebase project with credentials
- Google Gemini API key

### Backend Setup

1. Navigate to backend:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Setup ML model:
```bash
python setup_multi_disease_model.py
```

6. Run server:
```bash
python manage.py runserver
```

Backend runs on: http://localhost:8000

### Frontend Setup

1. Navigate to frontend:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with Firebase Web SDK config
```

4. Start development server:
```bash
npm run dev
```

Frontend runs on: http://localhost:3000

## 📚 Documentation

- **API Documentation**: http://localhost:8000/api/docs/
- **API Schema**: http://localhost:8000/api/schema/
- **Frontend Spec**: `.kiro/specs/ai-health-frontend/`
- **Project Structure**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 🔑 Key Features

- Multi-agent AI health assessment pipeline
- Confidence-aware responses (LOW/MEDIUM/HIGH)
- Multi-system treatment information (Allopathy, Ayurveda, Homeopathy, Lifestyle)
- Firebase authentication with Google OAuth
- Rate limiting (10/min, 100/hr, 200/day for authenticated users)
- Assessment history tracking
- Medical report upload support
- WCAG 2.1 AA accessibility compliance

## 🔒 Security

- Firebase authentication
- Rate limiting
- CSRF protection
- XSS prevention
- Secure token storage
- HTTPS required in production

## 📄 License

Proprietary - All rights reserved
