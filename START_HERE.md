# 🎯 START HERE - Complete Connection Guide

## 🎉 Everything is Already Configured!

Your system has:
- ✅ Backend configured with Django
- ✅ Frontend configured with React
- ✅ Firebase authentication set up
- ✅ Gemini AI integrated

---

## 🚀 3 Simple Steps to Start

### Step 1: Install Dependencies (First Time Only)

Open PowerShell in project root:

```powershell
# Install backend dependencies
cd backend
pip install -r requirements.txt
python manage.py migrate
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Step 2: Start Everything

```powershell
.\start-all.ps1
```

This will:
- ✅ Start backend on http://localhost:8000
- ✅ Start frontend on http://localhost:3000
- ✅ Open browser automatically

### Step 3: Test the Connection

1. Browser opens to http://localhost:3000
2. Click "Login" or "Get Started"
3. Sign in with your Google account
4. You'll see the dashboard!

**That's it!** 🎉

---

## 📚 Documentation Guide

### Choose Your Path:

#### 🏃 I Want to Start NOW
→ **You're already here!** Just run `.\start-all.ps1`

#### 📖 I Want Quick Instructions
→ **[QUICK_START.md](QUICK_START.md)**
- One-page quick reference
- Essential commands
- Common issues

#### 📚 I Want Complete Details
→ **[COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)**
- Step-by-step setup
- Firebase configuration
- Gemini AI setup
- Troubleshooting

#### 🏗️ I Want to Understand Architecture
→ **[ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)**
- System diagrams
- Data flow charts
- Component structure
- Technology stack

#### ✅ I Want to Verify Everything
→ **[CONNECTION_CHECKLIST.md](CONNECTION_CHECKLIST.md)**
- Complete verification checklist
- Test commands
- Success criteria

#### 🔗 I Want Connection Details
→ **[CONNECTION_GUIDE.md](CONNECTION_GUIDE.md)**
- Connection status
- Testing endpoints
- Troubleshooting

---

## 🎯 What You'll See

### 1. Backend Terminal
```
System check identified no issues (0 silenced).
Django version 4.2.x
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### 2. Frontend Terminal
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

### 3. Browser
- Landing page loads
- "Login" button visible
- No errors in console (F12)

---

## 🧪 Quick Test

After starting, verify everything works:

### Test 1: Backend Health
```powershell
curl http://localhost:8000/api/health/
```
**Expected**: `{"status": "healthy", ...}`

### Test 2: System Status
```powershell
curl http://localhost:8000/api/status/
```
**Expected**: JSON with system components

### Test 3: Frontend
1. Open: http://localhost:3000
2. Press F12 (Developer Tools)
3. Check Console tab
4. **Expected**: No errors

### Test 4: Login
1. Click "Login"
2. Click "Sign in with Google"
3. Select your Google account
4. **Expected**: Redirected to dashboard

---

## 🔧 Your Configuration

### Backend (`.env`)
```
✅ Django Secret Key: Configured
✅ Firebase Credentials: firebase-credentials.json
✅ Gemini API Key: Configured
✅ CORS: http://localhost:3000
✅ Debug Mode: True (development)
```

### Frontend (`.env`)
```
✅ API URL: http://localhost:8000
✅ Firebase API Key: Configured
✅ Firebase Project: major-project-2c7c7
✅ All Firebase Config: Set
```

### Firebase
```
✅ Project: major-project-2c7c7
✅ Authentication: Google OAuth enabled
✅ Firestore: Database created
✅ Credentials: Service account configured
```

### Gemini AI
```
✅ API Key: Configured
✅ Model: Gemini Pro
✅ Rate Limit: 60/min, 1500/day
```

---

## 🎨 Visual Flow

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  1. Run: .\start-all.ps1                           │
│                                                     │
│  2. Backend starts → http://localhost:8000         │
│                                                     │
│  3. Frontend starts → http://localhost:3000        │
│                                                     │
│  4. Browser opens automatically                     │
│                                                     │
│  5. Click "Login" → Sign in with Google            │
│                                                     │
│  6. Dashboard loads → You're connected! 🎉         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔍 Connection Verification

### ✅ Backend Connected When:
- Server starts without errors
- `/api/health/` returns 200
- `/api/status/` returns JSON
- No Firebase errors in console

### ✅ Frontend Connected When:
- Server starts without errors
- Landing page loads
- No console errors (F12)
- Can navigate to /login

### ✅ Firebase Connected When:
- Can click "Sign in with Google"
- OAuth popup appears
- Can select Google account
- Redirects after login

### ✅ Full Integration When:
- Dashboard loads after login
- System status displays
- No CORS errors
- API calls visible in Network tab

---

## 🚨 Common Issues & Quick Fixes

### Issue: Port Already in Use

**Fix:**
```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Issue: CORS Error

**Fix:**
1. Check `backend/.env` has: `CORS_ALLOWED_ORIGINS=http://localhost:3000`
2. Restart backend server

### Issue: Firebase Error

**Fix:**
1. Check `firebase-credentials.json` exists
2. Check `backend/.env` has: `FIREBASE_CREDENTIALS_PATH=firebase-credentials.json`
3. Restart backend server

### Issue: Module Not Found

**Fix:**
```powershell
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

---

## 📊 System Status

```
Component          Status    Port    URL
─────────────────────────────────────────────────────
Backend (Django)   ✅ Ready  8000    http://localhost:8000
Frontend (React)   ✅ Ready  3000    http://localhost:3000
Firebase Auth      ✅ Ready  -       Cloud Service
Gemini AI          ✅ Ready  -       Cloud Service
Database           ✅ Ready  -       Firestore (Cloud)
```

---

## 🎯 Next Steps After Connection

### 1. Explore the Application
- Login with Google
- View dashboard
- Check system status
- Navigate using sidebar

### 2. Review Documentation
- Read ARCHITECTURE_DIAGRAM.md
- Understand data flow
- Review component structure

### 3. Start Development
- Check `.kiro/specs/ai-health-frontend/tasks.md`
- Implement remaining features
- Run tests regularly

### 4. Test Features
```bash
# Run frontend tests
cd frontend
npm test

# Run backend tests
cd backend
python manage.py test
```

---

## 🆘 Need Help?

### Quick Reference
1. **Can't start**: Check [QUICK_START.md](QUICK_START.md)
2. **Setup issues**: Check [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)
3. **Connection problems**: Check [CONNECTION_CHECKLIST.md](CONNECTION_CHECKLIST.md)
4. **Architecture questions**: Check [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)

### Test Commands
```bash
# Backend health
curl http://localhost:8000/api/health/

# System status
curl http://localhost:8000/api/status/

# API documentation
open http://localhost:8000/api/docs/
```

### Useful URLs
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/
- **Firebase Console**: https://console.firebase.google.com/
- **Gemini API**: https://makersuite.google.com/app/apikey

---

## ✅ Success Checklist

You're ready when you see:

- [ ] ✅ Backend terminal shows "Starting development server"
- [ ] ✅ Frontend terminal shows "Local: http://localhost:3000/"
- [ ] ✅ Browser opens automatically
- [ ] ✅ Landing page loads without errors
- [ ] ✅ Can click "Login" button
- [ ] ✅ Google OAuth works
- [ ] ✅ Dashboard displays after login
- [ ] ✅ No errors in browser console

---

## 🎉 You're All Set!

### Start Command
```powershell
.\start-all.ps1
```

### What Happens Next
1. ✅ Backend starts (port 8000)
2. ✅ Frontend starts (port 3000)
3. ✅ Browser opens automatically
4. ✅ You can login and use the app!

---

## 📞 Support Resources

- **Documentation**: All .md files in root
- **Backend Docs**: `backend/README.md`
- **Frontend Docs**: `frontend/README.md`
- **API Docs**: http://localhost:8000/api/docs/
- **Task List**: `.kiro/specs/ai-health-frontend/tasks.md`

---

**Status**: 🟢 Ready to Start!

**Command**: `.\start-all.ps1`

**Time to Start**: < 1 minute

**Let's Go!** 🚀

---

*Last Updated: 2024*
*Version: 1.0*
*All Systems: Configured ✅*
