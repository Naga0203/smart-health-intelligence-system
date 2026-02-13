# 🚀 Frontend + Backend + Firebase + Gemini Connection Guide

## 📖 Quick Navigation

Choose your path:

### 🏃 I Want to Start Immediately
→ **[QUICK_START.md](QUICK_START.md)** - One command to start everything

### 📚 I Want Complete Instructions
→ **[COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)** - Detailed step-by-step guide

### 🏗️ I Want to Understand the Architecture
→ **[ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)** - Visual diagrams and flows

### ✅ I Want to Verify Everything Works
→ **[CONNECTION_CHECKLIST.md](CONNECTION_CHECKLIST.md)** - Complete verification checklist

### 🔗 I Want Connection Status
→ **[CONNECTION_GUIDE.md](CONNECTION_GUIDE.md)** - Current connection status

---

## 🎯 What You Have

Your system is **already configured** with:

### ✅ Backend (Django)
- **Location**: `backend/`
- **Port**: 8000
- **URL**: http://localhost:8000
- **Status**: ✅ Configured

### ✅ Frontend (React)
- **Location**: `frontend/`
- **Port**: 3000
- **URL**: http://localhost:3000
- **Status**: ✅ Configured

### ✅ Firebase
- **Project**: major-project-2c7c7
- **Auth**: Google OAuth enabled
- **Database**: Firestore
- **Status**: ✅ Configured

### ✅ Gemini AI
- **API Key**: Configured
- **Model**: Gemini Pro
- **Usage**: Explanations & Extraction
- **Status**: ✅ Configured

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
```

**Frontend:**
```bash
cd frontend
npm install
```

### Step 2: Start Servers

**Option A - Automatic (Windows):**
```powershell
.\start-all.ps1
```

**Option B - Manual:**

Terminal 1:
```bash
cd backend
python manage.py runserver
```

Terminal 2:
```bash
cd frontend
npm run dev
```

### Step 3: Test

1. Open: http://localhost:3000
2. Click "Login"
3. Sign in with Google
4. View Dashboard

**Done!** 🎉

---

## 📊 System Overview

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  Frontend (React)          Backend (Django)        │
│  localhost:3000     ←→     localhost:8000          │
│                                                     │
│       ↓                          ↓                  │
│                                                     │
│  Firebase Auth            Gemini AI                │
│  (Google OAuth)           (Explanations)           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔑 Key Configuration Files

### Backend Configuration
- **`.env`** - Environment variables
  - Django secret key
  - Firebase credentials path
  - Gemini API key
  - CORS settings

- **`firebase-credentials.json`** - Firebase service account
  - Authentication
  - Firestore access

### Frontend Configuration
- **`.env`** - Environment variables
  - API base URL
  - Firebase web config
  - All Firebase keys

---

## 🧪 Quick Test Commands

### Test Backend
```bash
# Health check
curl http://localhost:8000/api/health/

# System status
curl http://localhost:8000/api/status/

# API docs
open http://localhost:8000/api/docs/
```

### Test Frontend
```bash
# Open in browser
open http://localhost:3000

# Check console (F12)
# Should see no errors
```

### Test Connection
```javascript
// In browser console at http://localhost:3000
fetch('http://localhost:8000/api/status/')
  .then(r => r.json())
  .then(console.log)
// Should return system status, no CORS error
```

---

## 🔧 Configuration Summary

### Backend Environment (`.env`)
```bash
DJANGO_SECRET_KEY=<configured>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
GEMINI_API_KEY=your-api key
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend Environment (`.env`)
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project
# ... other Firebase config
```

### Firebase Project
```
Project ID: major-project-2c7c7
Auth: Google OAuth ✅
Database: Firestore ✅
Credentials: firebase-credentials.json ✅
```

---

## 📋 Connection Flow

### 1. User Login
```
User → Frontend → Firebase Auth → Get Token → Store Token
```

### 2. API Request
```
Frontend → Add Token → Backend → Validate Token → Process → Response
```

### 3. Health Assessment
```
User Input → Backend → Gemini AI → ML Model → Gemini AI → Response
```

---

## 🎯 What Works Now

✅ **Authentication**
- Google OAuth login
- Token management
- Protected routes

✅ **API Communication**
- Frontend ↔ Backend
- CORS configured
- Token validation

✅ **Firebase Integration**
- Authentication
- Firestore database
- User management

✅ **Gemini AI**
- Explanation generation
- Data extraction
- Validation

---

## 🚧 What to Implement Next

Follow the task list in `.kiro/specs/ai-health-frontend/tasks.md`:

1. ⏳ Assessment input flow (Task 11)
2. ⏳ Assessment history (Task 16)
3. ⏳ User profile management (Task 10)
4. ⏳ Responsive design (Task 22)
5. ⏳ Security features (Task 23)

---

## 📚 Documentation Structure

```
Root/
├── README_CONNECTION.md          ← You are here
├── QUICK_START.md               ← Start immediately
├── COMPLETE_SETUP_GUIDE.md      ← Detailed guide
├── ARCHITECTURE_DIAGRAM.md      ← Visual diagrams
├── CONNECTION_CHECKLIST.md      ← Verification
├── CONNECTION_GUIDE.md          ← Status & testing
├── start-all.ps1                ← Auto-start script
│
├── backend/
│   ├── .env                     ← Backend config
│   ├── requirements.txt         ← Python packages
│   └── README.md                ← Backend docs
│
├── frontend/
│   ├── .env                     ← Frontend config
│   ├── package.json             ← Node packages
│   └── README.md                ← Frontend docs
│
└── firebase-credentials.json    ← Firebase service account
```

---

## 🔍 Troubleshooting Quick Reference

### Backend Won't Start
```bash
# Check Python
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Check .env file
cat backend/.env
```

### Frontend Won't Start
```bash
# Check Node
node --version

# Reinstall dependencies
npm install

# Check .env file
cat frontend/.env
```

### CORS Errors
```bash
# Verify CORS setting
grep CORS backend/.env

# Should be: CORS_ALLOWED_ORIGINS=http://localhost:3000
# Restart backend after changes
```

### Authentication Fails
```bash
# Check Firebase config
cat frontend/.env | grep FIREBASE

# Verify credentials file
ls firebase-credentials.json

# Check Firebase Console
# https://console.firebase.google.com/
```

---

## 🆘 Getting Help

### Check These First
1. ✅ Both servers running?
2. ✅ Correct ports (3000, 8000)?
3. ✅ No console errors?
4. ✅ Environment files configured?
5. ✅ Dependencies installed?

### Review Documentation
- **Quick issues**: QUICK_START.md
- **Setup problems**: COMPLETE_SETUP_GUIDE.md
- **Connection issues**: CONNECTION_CHECKLIST.md
- **Architecture questions**: ARCHITECTURE_DIAGRAM.md

### Common Solutions
```bash
# Restart everything
# Kill both servers (Ctrl+C)
# Then run:
.\start-all.ps1

# Clear cache
# Browser: Ctrl+Shift+Delete
# Clear localStorage in console:
localStorage.clear()

# Reinstall dependencies
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

---

## ✅ Success Checklist

You're ready when:

- [ ] Backend starts on port 8000
- [ ] Frontend starts on port 3000
- [ ] Landing page loads
- [ ] Can login with Google
- [ ] Dashboard displays
- [ ] No CORS errors
- [ ] API calls work

---

## 🎉 You're All Set!

### Start Developing

```bash
# Start both servers
.\start-all.ps1

# Open browser
http://localhost:3000

# Start coding!
```

### Useful URLs

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs/
- **Admin**: http://localhost:8000/admin/

### Next Steps

1. ✅ Verify connection (CONNECTION_CHECKLIST.md)
2. ✅ Understand architecture (ARCHITECTURE_DIAGRAM.md)
3. ✅ Start implementing features (tasks.md)
4. ✅ Run tests regularly
5. ✅ Deploy when ready

---

## 📞 Support

- **Documentation**: See files listed above
- **API Docs**: http://localhost:8000/api/docs/
- **Firebase Console**: https://console.firebase.google.com/
- **Gemini API**: https://makersuite.google.com/app/apikey

---

**Status**: 🟢 Ready to Connect!

**Command**: `.\start-all.ps1`

**Documentation**: Complete ✅

**Configuration**: Complete ✅

**Let's Build!** 🚀
