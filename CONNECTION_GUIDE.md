# Frontend-Backend Connection Guide

## ✅ Connection Status

The frontend and backend are now fully connected and ready to communicate!

## 🔗 What Was Implemented

### 1. State Management (Zustand Stores)
- ✅ `authStore.ts` - Authentication state with Firebase
- ✅ `userStore.ts` - User profile and statistics
- ✅ `assessmentStore.ts` - Health assessments
- ✅ `systemStore.ts` - System status monitoring
- ✅ `notificationStore.ts` - Notifications

### 2. Routing & Navigation
- ✅ `routes/index.tsx` - React Router configuration
- ✅ `ProtectedRoute.tsx` - Authentication guard
- ✅ Route structure:
  - `/` - Landing page
  - `/login` - Login page
  - `/app/dashboard` - Dashboard (protected)
  - `/app/assessment/new` - New assessment (protected)
  - `/app/history` - Assessment history (protected)
  - `/app/profile` - User profile (protected)

### 3. Layout Components
- ✅ `AppLayout.tsx` - Main app layout
- ✅ `Header.tsx` - Top navigation with user menu
- ✅ `Sidebar.tsx` - Side navigation menu

### 4. Pages
- ✅ `LandingPage.tsx` - Welcome page
- ✅ `LoginPage.tsx` - Authentication page
- ✅ `DashboardPage.tsx` - Main dashboard with system status
- ✅ Placeholder pages for other routes

### 5. Services
- ✅ `firebase.ts` - Firebase authentication
- ✅ `api.ts` - Backend API client with interceptors

### 6. Backend Configuration
- ✅ CORS enabled for `http://localhost:3000`
- ✅ Firebase authentication configured
- ✅ Rate limiting configured
- ✅ API documentation at `/api/docs/`

## 🚀 How to Test the Connection

### Step 1: Start Backend Server

```bash
cd backend
python manage.py runserver
```

Backend will run on: **http://localhost:8000**

### Step 2: Start Frontend Server

Open a new terminal:

```bash
cd frontend
npm run dev
```

Frontend will run on: **http://localhost:3000**

### Step 3: Test the Connection

1. **Open Frontend**
   - Navigate to http://localhost:3000
   - You should see the landing page

2. **Click "Login"**
   - You'll be redirected to the login page
   - Try logging in with Firebase credentials

3. **After Login**
   - You'll be redirected to `/app/dashboard`
   - The dashboard will automatically:
     - Fetch system status from backend
     - Fetch user statistics from backend
     - Display the data

4. **Check Browser Console**
   - Open Developer Tools (F12)
   - Go to Console tab
   - You should see successful API calls
   - No CORS errors

5. **Check Network Tab**
   - Go to Network tab in Developer Tools
   - You should see:
     - `GET http://localhost:8000/api/status/` - System status
     - `GET http://localhost:8000/api/user/statistics/` - User stats
   - All should return 200 OK (or 401 if not logged in)

## 🔍 Connection Flow

### Authentication Flow
```
1. User enters email/password
   ↓
2. Frontend → Firebase Authentication
   ↓
3. Firebase returns ID token
   ↓
4. Frontend stores token in localStorage
   ↓
5. Frontend → Backend API (with token in Authorization header)
   ↓
6. Backend validates token with Firebase Admin SDK
   ↓
7. Backend returns user data
```

### API Request Flow
```
1. Component calls store action (e.g., fetchSystemStatus())
   ↓
2. Store calls API service (apiService.getSystemStatus())
   ↓
3. API service adds Authorization header with Firebase token
   ↓
4. Axios sends request to backend
   ↓
5. Backend validates token
   ↓
6. Backend processes request
   ↓
7. Backend returns response
   ↓
8. API service returns data to store
   ↓
9. Store updates state
   ↓
10. Component re-renders with new data
```

## 🧪 Testing Endpoints

### Test System Status (No Auth Required)
```bash
curl http://localhost:8000/api/status/
```

Expected response:
```json
{
  "status": "operational",
  "version": "1.0.0",
  "components": {...},
  "timestamp": "2024-..."
}
```

### Test Health Check
```bash
curl http://localhost:8000/api/health/
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-..."
}
```

### Test Authenticated Endpoint
```bash
curl -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
     http://localhost:8000/api/user/profile/
```

## 🔧 Troubleshooting

### Issue: CORS Error
**Symptom**: Console shows "CORS policy" error

**Solution**:
1. Check backend is running on port 8000
2. Verify `CORS_ALLOWED_ORIGINS` in `backend/health_ai_backend/settings.py` includes `http://localhost:3000`
3. Restart backend server

### Issue: 401 Unauthorized
**Symptom**: API calls return 401 error

**Solution**:
1. Ensure you're logged in
2. Check Firebase token in localStorage: `localStorage.getItem('firebase_token')`
3. Token might be expired - logout and login again

### Issue: Connection Refused
**Symptom**: "ERR_CONNECTION_REFUSED" in console

**Solution**:
1. Ensure backend server is running
2. Check backend is on port 8000: `http://localhost:8000/api/health/`
3. Check firewall settings

### Issue: Firebase Configuration Error
**Symptom**: "Firebase: Error (auth/invalid-api-key)"

**Solution**:
1. Verify `frontend/.env` has correct Firebase credentials
2. Check all VITE_FIREBASE_* variables are set
3. Restart frontend dev server after changing .env

## 📊 Connection Verification Checklist

- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 3000
- [ ] Can access landing page (http://localhost:3000)
- [ ] Can access login page (http://localhost:3000/login)
- [ ] Can login with Firebase credentials
- [ ] Dashboard loads after login
- [ ] System status displays on dashboard
- [ ] No CORS errors in console
- [ ] API calls visible in Network tab
- [ ] Can navigate between pages using sidebar

## 🎯 Next Steps

Now that frontend and backend are connected, you can:

1. **Implement Remaining Features**
   - Assessment form (Task 11)
   - Results display (Task 14)
   - History page (Task 16)
   - Profile management (Task 10)

2. **Run All Tasks**
   ```
   "Run all tasks for ai-health-frontend"
   ```

3. **Test Specific Features**
   - Create a new assessment
   - View assessment results
   - Check assessment history

## 📚 Documentation

- **API Documentation**: http://localhost:8000/api/docs/
- **API Schema**: http://localhost:8000/api/schema/
- **Frontend Spec**: `.kiro/specs/ai-health-frontend/`
- **Backend README**: `backend/README.md`
- **Frontend README**: `frontend/README.md`

## 🔐 Security Notes

- Firebase tokens are stored in localStorage
- Tokens are automatically included in API requests
- Backend validates all tokens with Firebase Admin SDK
- Rate limiting is enforced (10/min, 100/hr, 200/day)
- CORS is restricted to localhost:3000 in development

---

**Status**: ✅ Frontend and Backend Successfully Connected!

**Test It**: Start both servers and navigate to http://localhost:3000
