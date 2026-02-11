# Quick Start Guide - AI Health Intelligence Platform

## Prerequisites

Before starting the servers, ensure you have:
- ✅ Python 3.8+ installed
- ✅ Node.js 18+ installed
- ✅ Dependencies installed for both backend and frontend
- ✅ Environment variables configured (`.env` files)
- ✅ Firebase credentials in place

## Start Backend Server

### Terminal 1 - Backend

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (if using one)
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Run Django development server
python manage.py runserver
```

**Backend will be available at:** http://localhost:8000

### Backend Endpoints
- API Documentation: http://localhost:8000/api/docs/
- API Schema: http://localhost:8000/api/schema/
- Health Check: http://localhost:8000/api/health/
- System Status: http://localhost:8000/api/status/

## Start Frontend Server

### Terminal 2 - Frontend

```bash
# Navigate to frontend directory
cd frontend

# Start Vite development server
npm run dev
```

**Frontend will be available at:** http://localhost:3000 (or the port shown in terminal)

## Verify Everything Works

1. **Backend Health Check**
   ```bash
   curl http://localhost:8000/api/health/
   ```
   Should return: `{"status": "healthy", "timestamp": "..."}`

2. **Frontend Loading**
   - Open http://localhost:3000 in your browser
   - You should see the landing page

3. **API Connection**
   - Frontend should be able to connect to backend
   - Check browser console for any errors

## Common Issues

### Backend Issues

**Issue**: `ModuleNotFoundError`
**Solution**: Install dependencies: `pip install -r requirements.txt`

**Issue**: `django.db.utils.OperationalError`
**Solution**: Run migrations: `python manage.py migrate`

**Issue**: Firebase authentication fails
**Solution**: Check `firebase-credentials.json` path in `.env`

### Frontend Issues

**Issue**: `Cannot find module`
**Solution**: Install dependencies: `npm install`

**Issue**: `VITE_FIREBASE_API_KEY is not defined`
**Solution**: Configure `frontend/.env` with Firebase Web SDK credentials

**Issue**: API connection refused
**Solution**: Ensure backend is running on port 8000

## Stop Servers

- Press `Ctrl+C` in each terminal to stop the servers

## Production Deployment

For production deployment, see:
- Backend: `backend/README.md`
- Frontend: `frontend/README.md`
- Main docs: `README.md`

## Need Help?

- Check API documentation: http://localhost:8000/api/docs/
- Review logs: `backend/logs/health_ai.log`
- See project structure: `PROJECT_STRUCTURE.md`
- Read main README: `README.md`
