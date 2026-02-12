# ✅ Connection Checklist

Use this checklist to verify all components are properly connected.

---

## 📋 Pre-Flight Checks

### System Requirements
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] npm installed
- [ ] Git installed
- [ ] Code editor (VS Code recommended)

### Accounts & Services
- [ ] Google account (for Firebase & Gemini)
- [ ] Firebase project created
- [ ] Gemini API key obtained

---

## 🔥 Firebase Configuration

### Firebase Console
- [ ] Project "major-project-2c7c7" accessible
- [ ] Authentication enabled
- [ ] Google sign-in provider enabled
- [ ] Firestore database created
- [ ] Security rules configured

### Firebase Credentials
- [ ] `firebase-credentials.json` exists in root
- [ ] File contains valid service account credentials
- [ ] Project ID matches: `major-project-2c7c7`

### Firebase Web Config
- [ ] API Key: `AIzaSyCpLGyh7f8eZn9rf2eaRyeC2PTZh3JkPhY`
- [ ] Auth Domain: `major-project-2c7c7.firebaseapp.com`
- [ ] Project ID: `major-project-2c7c7`
- [ ] All config values in `frontend/.env`

---

## 🤖 Gemini AI Configuration

### API Key
- [ ] Gemini API key obtained
- [ ] Key: `AIzaSyDe9eF_gmXt63hIdagwaOBaqKkx4fv6MMM`
- [ ] Key added to `backend/.env`
- [ ] Key tested and working

### API Limits
- [ ] Free tier: 60 requests/minute
- [ ] Daily limit: 1,500 requests/day
- [ ] Usage monitored at: https://makersuite.google.com/app/apikey

---

## 🔧 Backend Configuration

### Environment File (`backend/.env`)
- [ ] File exists
- [ ] `DJANGO_SECRET_KEY` set
- [ ] `DEBUG=True` for development
- [ ] `ALLOWED_HOSTS=localhost,127.0.0.1`
- [ ] `FIREBASE_CREDENTIALS_PATH=firebase-credentials.json`
- [ ] `GEMINI_API_KEY` set
- [ ] `CORS_ALLOWED_ORIGINS=http://localhost:3000`

### Dependencies
- [ ] `requirements.txt` exists
- [ ] All packages installed: `pip install -r requirements.txt`
- [ ] No installation errors

### Database
- [ ] Migrations run: `python manage.py migrate`
- [ ] No migration errors
- [ ] SQLite database created: `db.sqlite3`

### Server
- [ ] Server starts: `python manage.py runserver`
- [ ] No startup errors
- [ ] Accessible at: http://localhost:8000

---

## ⚛️ Frontend Configuration

### Environment File (`frontend/.env`)
- [ ] File exists
- [ ] `VITE_API_BASE_URL=http://localhost:8000`
- [ ] `VITE_FIREBASE_API_KEY` set
- [ ] `VITE_FIREBASE_AUTH_DOMAIN` set
- [ ] `VITE_FIREBASE_PROJECT_ID=major-project-2c7c7`
- [ ] `VITE_FIREBASE_STORAGE_BUCKET` set
- [ ] `VITE_FIREBASE_MESSAGING_SENDER_ID` set
- [ ] `VITE_FIREBASE_APP_ID` set

### Dependencies
- [ ] `package.json` exists
- [ ] All packages installed: `npm install`
- [ ] No installation errors
- [ ] `node_modules/` folder created

### Server
- [ ] Server starts: `npm run dev`
- [ ] No startup errors
- [ ] Accessible at: http://localhost:3000

---

## 🔗 Connection Tests

### Backend Health Checks

**Test 1: Health Endpoint**
```bash
curl http://localhost:8000/api/health/
```
- [ ] Returns: `{"status": "healthy", ...}`
- [ ] Status code: 200

**Test 2: System Status**
```bash
curl http://localhost:8000/api/status/
```
- [ ] Returns JSON with system components
- [ ] Status code: 200

**Test 3: Model Info**
```bash
curl http://localhost:8000/api/model/info/
```
- [ ] Returns model information
- [ ] Status code: 200

**Test 4: API Documentation**
- [ ] Open: http://localhost:8000/api/docs/
- [ ] Swagger UI loads
- [ ] All endpoints visible

### Frontend Tests

**Test 1: Landing Page**
- [ ] Open: http://localhost:3000
- [ ] Page loads without errors
- [ ] No console errors (F12)

**Test 2: Login Page**
- [ ] Navigate to: http://localhost:3000/login
- [ ] Login form displays
- [ ] Google sign-in button visible

**Test 3: Browser Console**
- [ ] Open Developer Tools (F12)
- [ ] No errors in Console tab
- [ ] No CORS errors

**Test 4: Network Tab**
- [ ] Open Network tab (F12)
- [ ] Refresh page
- [ ] All resources load (200 status)

### Integration Tests

**Test 1: CORS**
```javascript
// In browser console at http://localhost:3000
fetch('http://localhost:8000/api/status/')
  .then(r => r.json())
  .then(console.log)
```
- [ ] Returns system status JSON
- [ ] No CORS error

**Test 2: Firebase Authentication**
- [ ] Click "Login" button
- [ ] Click "Sign in with Google"
- [ ] Google OAuth popup appears
- [ ] Can select Google account
- [ ] Redirects to dashboard after login

**Test 3: Authenticated API Call**
- [ ] Login with Google
- [ ] Dashboard loads
- [ ] Check Network tab
- [ ] See: `GET /api/user/profile/` with Authorization header
- [ ] See: `GET /api/user/statistics/`

**Test 4: Token Storage**
```javascript
// In browser console after login
localStorage.getItem('auth-storage')
```
- [ ] Returns stored auth state
- [ ] Contains user object
- [ ] Contains token string

**Test 5: System Status Display**
- [ ] Dashboard shows system status
- [ ] Status indicator visible (green/yellow/red)
- [ ] Model information displayed

---

## 🧪 End-to-End Test

### Complete User Flow

1. **Start Servers**
   - [ ] Backend running on port 8000
   - [ ] Frontend running on port 3000

2. **Landing Page**
   - [ ] Open http://localhost:3000
   - [ ] Landing page loads
   - [ ] "Login" button visible

3. **Login**
   - [ ] Click "Login"
   - [ ] Redirected to /login
   - [ ] Click "Sign in with Google"
   - [ ] Google OAuth popup
   - [ ] Select account
   - [ ] Popup closes

4. **Dashboard**
   - [ ] Redirected to /app/dashboard
   - [ ] Dashboard loads
   - [ ] System status displays
   - [ ] User menu in header
   - [ ] Sidebar navigation visible

5. **Navigation**
   - [ ] Click sidebar items
   - [ ] Pages load without errors
   - [ ] URL changes correctly

6. **Logout**
   - [ ] Click user menu
   - [ ] Click "Logout"
   - [ ] Redirected to landing page
   - [ ] Token cleared from localStorage

---

## 🔍 Troubleshooting Checklist

### If Backend Won't Start

- [ ] Check Python version: `python --version`
- [ ] Check dependencies: `pip list`
- [ ] Check .env file exists
- [ ] Check firebase-credentials.json exists
- [ ] Check port 8000 not in use
- [ ] Check error messages in console

### If Frontend Won't Start

- [ ] Check Node version: `node --version`
- [ ] Check dependencies: `npm list`
- [ ] Check .env file exists
- [ ] Check port 3000 not in use
- [ ] Check error messages in console
- [ ] Try: `npm install` again

### If CORS Errors Occur

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] CORS_ALLOWED_ORIGINS includes http://localhost:3000
- [ ] Restart backend after .env changes
- [ ] Clear browser cache

### If Authentication Fails

- [ ] Firebase config correct in frontend/.env
- [ ] Firebase credentials file exists
- [ ] Google sign-in enabled in Firebase Console
- [ ] localhost added to authorized domains
- [ ] Check browser console for errors

### If API Calls Fail

- [ ] Backend server running
- [ ] Correct API base URL in frontend/.env
- [ ] Token present in Authorization header
- [ ] Token not expired
- [ ] Check Network tab for error details

---

## 📊 Success Criteria

All of these should be true:

- [ ] ✅ Backend starts without errors
- [ ] ✅ Frontend starts without errors
- [ ] ✅ Landing page loads
- [ ] ✅ Can login with Google
- [ ] ✅ Dashboard displays after login
- [ ] ✅ System status shows on dashboard
- [ ] ✅ No CORS errors in console
- [ ] ✅ API calls visible in Network tab
- [ ] ✅ Can navigate between pages
- [ ] ✅ Can logout successfully

---

## 🎯 Quick Verification Commands

Run these commands to quickly verify everything:

```bash
# Check backend
curl http://localhost:8000/api/health/

# Check system status
curl http://localhost:8000/api/status/

# Check frontend (in browser)
# Open: http://localhost:3000
# Console: No errors
# Network: All resources load
```

---

## 📚 Reference Documents

- [ ] Read: `QUICK_START.md`
- [ ] Read: `COMPLETE_SETUP_GUIDE.md`
- [ ] Read: `ARCHITECTURE_DIAGRAM.md`
- [ ] Read: `CONNECTION_GUIDE.md`

---

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review error messages carefully
3. Check browser console (F12)
4. Check backend terminal output
5. Verify all environment variables
6. Restart both servers
7. Clear browser cache and localStorage

---

## ✅ Final Status

Once all items are checked:

**Status**: 🟢 All Systems Connected and Operational!

**Ready to**: Start developing features!

**Next Step**: Run `.\start-all.ps1` and begin coding!

---

**Last Updated**: 2024
**Version**: 1.0
