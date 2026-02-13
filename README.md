# 🧠 AI Health Intelligence Platform

> AI-powered health risk assessment with explainable predictions and multi-system treatment recommendations.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Django](https://img.shields.io/badge/Django-REST-green)
![React](https://img.shields.io/badge/React-18-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-Enabled-blue)
![Firebase](https://img.shields.io/badge/Auth-Firebase-orange)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## 🚀 Overview

A full-stack AI-driven health intelligence system that:

- 🔬 Predicts disease risk using Machine Learning  
- 🧠 Explains predictions using AI agents  
- 💊 Recommends treatments from:
  - Modern Medicine  
  - Ayurveda  
  - Homeopathy  
  - Lifestyle interventions  
- 🔐 Secures users with Firebase Authentication  
- 📱 Works across mobile, tablet, and desktop  

This is not just a model wrapper — it’s a structured AI system with orchestration, explainability, and production-grade architecture.

---

# 🏗️ Architecture

```
User
  ↓
React Frontend
  ↓
Django REST API
  ↓
ML Prediction Engine
  ↓
AI Agent Orchestrator
  ↓
Multi-System Treatment Engine
```

---

# 📁 Project Structure

```
.
├── backend/              # Django REST API
│   ├── agents/           # AI orchestration modules
│   ├── api/              # REST endpoints
│   ├── common/           # Firebase, Gemini, caching
│   ├── prediction/       # ML integration
│   ├── treatment/        # Medical knowledge base
│   └── test_backend.py
│
├── frontend/             # React + TypeScript
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── stores/           # Zustand
│   └── theme/
│
└── README.md
```

---

# ⚙️ Tech Stack

## 🖥 Backend
- Python 3.9+
- Django REST Framework
- Firebase Admin SDK
- Google Gemini API
- JWT Authentication
- Rate Limiting & Throttling

## 🎨 Frontend
- React 18
- TypeScript
- Material UI
- Zustand
- Firebase Authentication
- PWA + Offline Support

---

# 🛠️ Local Setup

## 📌 Prerequisites

- Python 3.9+
- Node.js 18+
- Firebase Project
- Gemini API Key

---

## 🔧 Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`:

```env
FIREBASE_CREDENTIALS_PATH=path/to/firebase.json
GEMINI_API_KEY=your_key
SECRET_KEY=your_secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Run server:

```bash
python manage.py migrate
python manage.py runserver
```

Backend → http://localhost:8000

---

## 🎨 Frontend Setup

```bash
cd frontend
npm install
```

Create `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_id
VITE_FIREBASE_STORAGE_BUCKET=your_bucket
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender
VITE_FIREBASE_APP_ID=your_app_id
```

Run:

```bash
npm run dev
```

Frontend → http://localhost:5173

---

# 🔐 Security Features

- 🔑 Firebase Authentication
- 🪪 JWT-secured APIs
- 🛡 CSRF Protection
- 🚦 Rate limiting:
  - 10/min
  - 100/hour
  - 200/day
- 🔒 HTTPS enforcement in production
- 🧹 Input validation & sanitization

---

# 🧪 Testing

### Backend

```bash
cd backend
python test_backend.py
```

Covers:

- Health checks
- API validation
- Authentication
- Public endpoints
- System status

---

# 📚 API Documentation

- Swagger UI  
  `http://localhost:8000/api/schema/swagger-ui/`

- ReDoc  
  `http://localhost:8000/api/schema/redoc/`

- OpenAPI Schema  
  `backend/api_schema.yml`

---

# 🌍 Deployment

## Backend Checklist

- Set `DEBUG=False`
- Configure `ALLOWED_HOSTS`
- Use PostgreSQL
- Collect static files
- Deploy with Gunicorn
- Configure Nginx
- Enable HTTPS

## Frontend

```bash
npm run build
```

Deploy `/dist` to:

- Vercel
- Netlify
- AWS S3
- Any static hosting provider

---

# ⚠️ Important Rules

❌ Never commit:
- `.env`
- Firebase credentials
- API keys
- `db.sqlite3`
- `node_modules/`
- `venv/`

✅ Before pushing:
- Verify `.gitignore`
- Remove logs
- Check secrets
- Clean test data

---

# 📌 Project Status

✔ Modular AI Architecture  
✔ Production-ready structure  
✔ Secure authentication  
✔ Multi-system treatment logic  

---

# 📄 License

Proprietary — All Rights Reserved

---

## 👨‍💻 Author

Built with a focus on AI system design, scalability, and real-world usability.

---

