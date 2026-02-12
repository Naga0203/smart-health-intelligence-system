# 🚀 Quick Start Guide

## One-Command Start

### Windows (PowerShell)

```powershell
.\start-all.ps1
```

This will:
1. ✅ Check Python and Node.js installation
2. ✅ Start backend server (port 8000)
3. ✅ Start frontend server (port 3000)
4. ✅ Open browser automatically

---

## Manual Start (If Script Doesn't Work)

### Terminal 1 - Backend

```bash
cd backend
python manage.py runserver
```

**Expected Output:**
```
Starting development server at http://127.0.0.1:8000/
```

### Terminal 2 - Frontend

```bash
cd frontend
npm run dev
```

**Expected Output:**
```
Local:   http://localhost:3000/
```

---

## First Time Setup

### 1. Install Dependencies

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

### 2. Verify Configuration

**Check Backend `.env`:**
```bash
cd backend
cat .env
```

Should have:
- ✅ `FIREBASE_CREDENTIALS_PATH=firebase-credentials.json`
- ✅ `GEMINI_API_KEY=AIzaSy...`
- ✅ `CORS_ALLOWED_ORIGINS=http://localhost:3000`

**Check Frontend `.env`:**
```bash
cd frontend
cat .env
```

Should have:
- ✅ `VITE_API_BASE_URL=http://localhost:8000`
- ✅ `VITE_FIREBASE_API_KEY=AIzaSy...`
- ✅ All Firebase config variables

### 3. Test Connection

**Test Backend:**
```bash
curl http://localhost:8000/api/health/
```

**Test Frontend:**
Open browser: http://localhost:3000

---

## Quick Test Checklist

After starting both servers:

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] Landing page loads without errors
- [ ] Can click "Login" button
- [ ] No CORS errors in console (F12)
- [ ] System status API works: http://localhost:8000/api/status/

---

## Troubleshooting

### Port Already in Use

**Kill process on port 8000:**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Kill process on port 3000:**
```powershell
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### CORS Error

Add to `backend/.env`:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Restart backend.

### Module Not Found

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

---

## What's Next?

1. **Login**: Click "Login" → Sign in with Google
2. **Dashboard**: View system status and statistics
3. **Explore**: Navigate using the sidebar
4. **Develop**: Make changes and see them live!

---

## Useful URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **API Docs**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

---

## Need More Help?

See the complete guide: `COMPLETE_SETUP_GUIDE.md`

---

**Status**: 🟢 Ready to Start!

**Command**: `.\start-all.ps1`
