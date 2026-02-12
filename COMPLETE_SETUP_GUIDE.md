# Complete Setup Guide: Frontend + Backend + Firebase + Gemini AI

## 📋 Overview

This guide will help you connect all components of the AI Health Intelligence Platform:
- **Frontend**: React + TypeScript (Vite)
- **Backend**: Django REST API
- **Firebase**: Authentication + Firestore Database
- **Gemini AI**: Google's AI for explanations and data extraction

---

## ✅ Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ and npm installed
- [ ] Git installed
- [ ] A Google account (for Firebase and Gemini)
- [ ] Code editor (VS Code recommended)

---

## 🔥 Step 1: Firebase Setup (Already Configured!)

Your Firebase is already set up! Here's what you have:

### Firebase Project Details
- **Project ID**: `major-project-2c7c7`
- **Project Name**: Major Project
- **Credentials File**: `firebase-credentials.json` ✅

### What's Already Configured
✅ Service account credentials
✅ Authentication enabled
✅ Firestore database
✅ Web app configuration

### Verify Firebase Setup

1. **Check Firebase Console**
   - Visit: https://console.firebase.google.com/
   - Select project: "major-project-2c7c7"
   - Verify Authentication is enabled
   - Verify Firestore Database is created

2. **Enable Google Sign-In** (if not already enabled)
   ```
   Firebase Console → Authentication → Sign-in method
   → Enable "Google" provider
   → Add authorized domain: localhost
   ```

3. **Firestore Security Rules** (for development)
   ```
   Firebase Console → Firestore Database → Rules
   ```
   
   Use these rules for development:
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       // Allow authenticated users to read/write their own data
       match /users/{userId} {
         allow read, write: if request.auth != null && request.auth.uid == userId;
       }
       
       // Allow authenticated users to read/write their assessments
       match /assessments/{assessmentId} {
         allow read, write: if request.auth != null;
       }
       
       // Allow anyone to read diseases (public data)
       match /diseases/{diseaseId} {
         allow read: if true;
         allow write: if false;
       }
     }
   }
   ```

---

## 🤖 Step 2: Gemini AI Setup (Already Configured!)

Your Gemini API key is already set up!

### Gemini API Details
- **API Key**: `AIzaSyDe9eF_gmXt63hIdagwaOBaqKkx4fv6MMM` ✅
- **Status**: Active

### Verify Gemini API

1. **Test the API Key**
   ```bash
   curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
     "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=AIzaSyDe9eF_gmXt63hIdagwaOBaqKkx4fv6MMM"
   ```

2. **Check Usage Limits**
   - Visit: https://makersuite.google.com/app/apikey
   - View your API key usage
   - Free tier: 60 requests/minute, 1,500/day

---

## 🔧 Step 3: Backend Setup

### 3.1 Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3.2 Verify Environment Variables

Your `backend/.env` is already configured! Verify these key settings:

```bash
# Check your .env file
cat .env
```

Should show:
- ✅ `DJANGO_SECRET_KEY` - Set
- ✅ `DEBUG=True` - For development
- ✅ `FIREBASE_CREDENTIALS_PATH=firebase-credentials.json` - Correct path
- ✅ `GEMINI_API_KEY` - Set
- ✅ `CORS_ALLOWED_ORIGINS=http://localhost:3000` - For frontend

### 3.3 Initialize Database

```bash
# Run migrations
python manage.py migrate

# Create superuser (optional, for admin panel)
python manage.py createsuperuser
```

### 3.4 Test Backend

```bash
# Start the development server
python manage.py runserver
```

**Expected Output:**
```
System check identified no issues (0 silenced).
Django version 4.2.x, using settings 'health_ai_backend.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### 3.5 Verify Backend Endpoints

Open a new terminal and test:

```bash
# Test health check
curl http://localhost:8000/api/health/

# Test system status
curl http://localhost:8000/api/status/

# Test model info
curl http://localhost:8000/api/model/info/
```

**Expected Responses:**
- All should return JSON data
- No errors in backend console
- Status code 200

---

## ⚛️ Step 4: Frontend Setup

### 4.1 Install Node Dependencies

```bash
cd frontend
npm install
```

### 4.2 Verify Environment Variables

Your `frontend/.env` is already configured! Verify:

```bash
# Check your .env file
cat .env
```

Should show:
- ✅ `VITE_API_BASE_URL=http://localhost:8000` - Backend URL
- ✅ `VITE_FIREBASE_API_KEY` - Set
- ✅ `VITE_FIREBASE_AUTH_DOMAIN` - Set
- ✅ `VITE_FIREBASE_PROJECT_ID=major-project-2c7c7` - Correct
- ✅ All other Firebase config variables

### 4.3 Start Frontend Development Server

```bash
npm run dev
```

**Expected Output:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

---

## 🔗 Step 5: Test the Complete Connection

### 5.1 Open Frontend

1. Open browser: http://localhost:3000
2. You should see the landing page

### 5.2 Test System Status Connection

Open browser console (F12) and check:

1. **Navigate to Dashboard** (if you can access it)
2. **Check Network Tab**:
   - Should see: `GET http://localhost:8000/api/status/`
   - Status: 200 OK
   - Response: JSON with system status

3. **Check Console Tab**:
   - No CORS errors
   - No connection errors

### 5.3 Test Firebase Authentication

1. **Click "Login" or "Get Started"**
2. **Try Google Sign-In**:
   - Click "Sign in with Google"
   - Select your Google account
   - Should redirect to dashboard

3. **Check Browser Console**:
   - Should see Firebase authentication success
   - Token should be stored in localStorage

4. **Check Backend Console**:
   - Should see authentication requests
   - No Firebase errors

### 5.4 Test Authenticated API Calls

After logging in:

1. **Dashboard should load**:
   - System status displayed
   - User statistics displayed (if available)

2. **Check Network Tab**:
   - `GET /api/user/profile/` - Should have Authorization header
   - `GET /api/user/statistics/` - Should return user data
   - All requests should include: `Authorization: Bearer <token>`

---

## 🧪 Step 6: Comprehensive Testing

### Test 1: Backend Health Check

```bash
# Terminal 1: Backend should be running
curl http://localhost:8000/api/health/
```

**Expected**: `{"status": "healthy", "timestamp": "..."}`

### Test 2: System Status

```bash
curl http://localhost:8000/api/status/
```

**Expected**: JSON with system components status

### Test 3: Frontend-Backend Connection

```bash
# In browser console (F12)
fetch('http://localhost:8000/api/status/')
  .then(r => r.json())
  .then(console.log)
```

**Expected**: System status JSON, no CORS errors

### Test 4: Firebase Authentication

1. Login with Google
2. Check localStorage:
   ```javascript
   // In browser console
   localStorage.getItem('auth-storage')
   ```
3. Should see stored auth state with token

### Test 5: Authenticated API Call

```javascript
// In browser console (after login)
const token = JSON.parse(localStorage.getItem('auth-storage')).state.token;

fetch('http://localhost:8000/api/user/profile/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
  .then(r => r.json())
  .then(console.log)
```

**Expected**: User profile data

### Test 6: Gemini AI Integration

```bash
# Test symptom analysis (requires authentication)
curl -X POST http://localhost:8000/api/health/analyze/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "symptoms": ["fever", "cough"],
    "age": 30,
    "gender": "male"
  }'
```

**Expected**: Risk assessment with AI-generated explanation

---

## 📊 Step 7: Verify All Components

### Backend Checklist
- [ ] Server running on port 8000
- [ ] No errors in console
- [ ] `/api/health/` returns 200
- [ ] `/api/status/` returns system status
- [ ] Firebase credentials loaded successfully
- [ ] Gemini API key configured

### Frontend Checklist
- [ ] Server running on port 3000
- [ ] Landing page loads
- [ ] No console errors
- [ ] Can navigate to login page
- [ ] Firebase SDK initialized
- [ ] API base URL configured correctly

### Firebase Checklist
- [ ] Project accessible in console
- [ ] Authentication enabled
- [ ] Google sign-in provider enabled
- [ ] Firestore database created
- [ ] Security rules configured
- [ ] Service account credentials valid

### Gemini AI Checklist
- [ ] API key valid
- [ ] Within rate limits
- [ ] Backend can make requests
- [ ] Responses are generated

---

## 🚀 Step 8: Run the Application

### Start Everything

**Terminal 1 - Backend:**
```bash
cd backend
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Access the Application

1. **Frontend**: http://localhost:3000
2. **Backend API**: http://localhost:8000
3. **API Docs**: http://localhost:8000/api/docs/
4. **Admin Panel**: http://localhost:8000/admin/

---

## 🔍 Step 9: Troubleshooting

### Issue: CORS Error

**Symptom**: Console shows "blocked by CORS policy"

**Solution**:
```bash
# Check backend settings.py
cd backend
grep CORS_ALLOWED_ORIGINS health_ai_backend/settings.py
```

Should include: `'http://localhost:3000'`

If not, add to `backend/.env`:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Restart backend server.

### Issue: Firebase Authentication Error

**Symptom**: "Firebase: Error (auth/invalid-api-key)"

**Solution**:
1. Verify `frontend/.env` has correct Firebase config
2. Check Firebase console for correct API key
3. Restart frontend dev server: `npm run dev`

### Issue: Backend Can't Find Firebase Credentials

**Symptom**: "Your default credentials were not found"

**Solution**:
```bash
# Check file exists
ls firebase-credentials.json

# Check .env points to correct path
cat backend/.env | grep FIREBASE_CREDENTIALS_PATH
```

Should be: `FIREBASE_CREDENTIALS_PATH=firebase-credentials.json`

### Issue: Gemini API Error

**Symptom**: "Gemini API request failed"

**Solution**:
1. Check API key in `backend/.env`
2. Verify quota at: https://makersuite.google.com/app/apikey
3. Test API key with curl (see Step 2)

### Issue: Port Already in Use

**Symptom**: "Address already in use"

**Solution**:
```bash
# Windows - Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Issue: Module Not Found

**Symptom**: "ModuleNotFoundError: No module named 'X'"

**Solution**:
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

---

## 🎯 Step 10: Next Steps

### Development Workflow

1. **Start Both Servers**:
   ```bash
   # Terminal 1
   cd backend && python manage.py runserver
   
   # Terminal 2
   cd frontend && npm run dev
   ```

2. **Make Changes**:
   - Frontend changes auto-reload
   - Backend changes auto-reload (with DEBUG=True)

3. **Test Changes**:
   - Use browser for frontend
   - Use curl/Postman for backend API

### Implement Features

Follow the task list in `.kiro/specs/ai-health-frontend/tasks.md`:

```bash
# View tasks
cat .kiro/specs/ai-health-frontend/tasks.md
```

Current progress:
- ✅ Task 1-4: Core infrastructure
- ✅ Task 12: Medical report upload
- ✅ Task 14: Assessment results display
- ✅ Task 15: Treatment information display
- ⏳ Remaining tasks: Assessment input, history, profile, etc.

### Run Tests

```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
python manage.py test
```

---

## 📚 Documentation

### API Documentation
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Project Documentation
- **Backend README**: `backend/README.md`
- **Frontend README**: `frontend/README.md`
- **API Documentation**: `backend/API_DOCUMENTATION.md`
- **Connection Guide**: `CONNECTION_GUIDE.md`

### Useful Commands

```bash
# Backend
python manage.py runserver          # Start server
python manage.py migrate            # Run migrations
python manage.py createsuperuser    # Create admin user
python manage.py test               # Run tests

# Frontend
npm run dev                         # Start dev server
npm run build                       # Build for production
npm test                            # Run tests
npm run lint                        # Lint code
```

---

## ✅ Connection Verification

Run this checklist to verify everything is connected:

### Quick Test Script

```bash
# Test backend
curl http://localhost:8000/api/health/

# Test system status
curl http://localhost:8000/api/status/

# Test frontend (in browser)
# Open: http://localhost:3000
# Check console for errors
```

### Expected Results

✅ Backend responds on port 8000
✅ Frontend loads on port 3000
✅ No CORS errors in console
✅ Can login with Google
✅ Dashboard loads after login
✅ System status displays
✅ API calls visible in Network tab

---

## 🎉 Success!

If all steps completed successfully, you now have:

✅ **Backend** running with Django REST API
✅ **Frontend** running with React + TypeScript
✅ **Firebase** authentication and database
✅ **Gemini AI** integrated for explanations
✅ **Full connection** between all components

### What You Can Do Now

1. **Login** with Google account
2. **View Dashboard** with system status
3. **Create Assessments** (when implemented)
4. **View Results** with AI explanations
5. **Track History** of assessments
6. **Manage Profile** information

---

## 🆘 Need Help?

### Check Logs

**Backend Logs**:
```bash
# In backend terminal
# Logs appear automatically
```

**Frontend Logs**:
```bash
# Browser console (F12)
# Check Console and Network tabs
```

**Firebase Logs**:
- Firebase Console → Authentication → Users
- Firebase Console → Firestore → Data

### Common Issues

1. **Port conflicts**: Change ports in config
2. **CORS errors**: Check CORS_ALLOWED_ORIGINS
3. **Auth errors**: Verify Firebase config
4. **API errors**: Check backend logs

### Resources

- Django Docs: https://docs.djangoproject.com/
- React Docs: https://react.dev/
- Firebase Docs: https://firebase.google.com/docs
- Gemini API Docs: https://ai.google.dev/docs

---

**Status**: 🟢 All Systems Connected and Operational!

**Test URL**: http://localhost:3000

**API URL**: http://localhost:8000/api/

**Last Updated**: 2024
