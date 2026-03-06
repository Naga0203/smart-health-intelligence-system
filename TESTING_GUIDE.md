# Complete Testing Guide - AI Health Intelligence Platform

## Overview

This guide covers testing the entire workflow combining frontend and backend, including the new Connection Pool Manager optimization.

## Prerequisites

Before running tests, ensure:

1. ✅ Backend server is running: `python manage.py runserver`
2. ✅ Frontend server is running: `npm run dev`
3. ✅ Firebase credentials are configured
4. ✅ All dependencies are installed

## Quick Start

### 1. Start Both Servers

**Option A: Use PowerShell Script (Windows)**
```powershell
.\start-all.ps1
```

**Option B: Manual Start**

Terminal 1 - Backend:
```bash
cd backend
python manage.py runserver
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### 2. Run End-to-End Tests

```bash
python test_full_workflow.py
```

This will test:
- ✅ Backend health and API endpoints
- ✅ Frontend availability
- ✅ CORS configuration
- ✅ Connection pool performance
- ✅ Response times
- ✅ Integration between frontend and backend

## Test Suites

### 1. Connection Pool Unit Tests

Tests the Connection Pool Manager in isolation with mocked Firestore.

```bash
cd backend
pytest common/test_connection_pool.py -v
```

**What it tests:**
- Pool initialization with min/max connections
- Connection acquisition and release
- Pool size management
- Health checks
- Idle connection cleanup
- Error handling
- Singleton pattern

**Expected output:**
```
test_connection_pool.py::TestConnectionPoolInitialization::test_init_with_valid_params PASSED
test_connection_pool.py::TestConnectionPoolInitialization::test_initialize_creates_min_connections PASSED
test_connection_pool.py::TestConnectionAcquisitionAndRelease::test_get_connection_success PASSED
...
======================== 24 passed in 2.34s ========================
```

### 2. Connection Pool Integration Tests

Tests the Connection Pool Manager with real Firestore connections.

```bash
cd backend
python test_connection_pool_integration.py
```

**What it tests:**
- Real Firestore connection pooling
- Concurrent connection usage
- Pool scaling under load
- Health check with real connections
- Connection reuse
- Performance improvements
- Pool statistics accuracy

**Expected output:**
```
============================================================
CONNECTION POOL MANAGER - INTEGRATION TESTS
============================================================

✓ PASS - Pool Initialization
  Created 5 connections
✓ PASS - Connection Acquisition & Release
  Connection acquired and released successfully
✓ PASS - Concurrent Connections
  10/10 operations succeeded in 1.23s
...
============================================================
TEST SUMMARY
============================================================

Total Tests: 8
Passed: 8
Failed: 0

✓ ALL TESTS PASSED
```

### 3. End-to-End Workflow Tests

Tests the complete system integration.

```bash
python test_full_workflow.py
```

**What it tests:**
- Backend health endpoint
- API endpoints (status, docs, schema)
- Frontend availability
- CORS configuration
- Connection pool with concurrent requests
- Response time performance
- Frontend-backend integration

**Expected output:**
```
======================================================================
                    AI HEALTH INTELLIGENCE PLATFORM                    
======================================================================

End-to-End Workflow Test
Timestamp: 2024-01-15 10:30:45

======================================================================
                          1. BACKEND TESTS                            
======================================================================

✓ Backend Health Check (0.15s)
  Status: healthy
✓ System Status (0.23s)
✓ API Documentation (0.18s)
✓ API Schema (0.21s)
✓ Connection Pool - Concurrent Requests (1.45s)
  10/10 requests succeeded (avg: 0.145s per request)
✓ Response Time - Health Check (0.12s)
  Target: <0.2s
✓ Response Time - System Status (0.45s)
  Target: <1.0s

======================================================================
                         2. FRONTEND TESTS                            
======================================================================

✓ Frontend Availability (0.34s)
  Frontend is accessible

======================================================================
                       3. INTEGRATION TESTS                           
======================================================================

✓ CORS Configuration (0.08s)
  Allowed origin: http://localhost:3000

======================================================================
                           TEST SUMMARY                               
======================================================================

Total Tests: 10
Passed: 10
Failed: 0
Warnings: 0

Total Duration: 3.21s

Overall Status: ✓ ALL TESTS PASSED
```

### 4. Backend Unit Tests (All)

Run all backend unit tests:

```bash
cd backend
pytest -v
```

Run with coverage:

```bash
cd backend
pytest --cov=. --cov-report=html
```

### 5. Frontend Tests

Run frontend tests:

```bash
cd frontend
npm run test
```

Run with coverage:

```bash
cd frontend
npm run test:coverage
```

## Manual Testing Workflow

### 1. Test Backend API

**Health Check:**
```bash
curl http://localhost:8000/api/health/
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456Z"
}
```

**System Status:**
```bash
curl http://localhost:8000/api/status/
```

**API Documentation:**
Open in browser: http://localhost:8000/api/docs/

### 2. Test Frontend

**Landing Page:**
Open in browser: http://localhost:3000

**Check Console:**
- Press F12 to open developer tools
- Check Console tab for errors
- Check Network tab for API calls

### 3. Test Connection Pool

**Monitor Pool Statistics:**

Create a test endpoint in `backend/api/views.py`:

```python
from django.http import JsonResponse
from common.connection_pool import get_connection_pool

def pool_stats(request):
    """Get connection pool statistics."""
    pool = get_connection_pool()
    stats = pool.get_pool_stats()
    return JsonResponse(stats)
```

Add to `backend/api/urls.py`:

```python
path('pool-stats/', views.pool_stats, name='pool_stats'),
```

Then test:
```bash
curl http://localhost:8000/api/pool-stats/
```

Expected response:
```json
{
  "total": 10,
  "active": 0,
  "idle": 10,
  "waiting": 0,
  "failed": 0,
  "min_size": 10,
  "max_size": 50
}
```

### 4. Test Concurrent Load

Use Apache Bench or similar tool:

```bash
# Install Apache Bench (if not installed)
# Windows: Download from Apache website
# Linux: sudo apt-get install apache2-utils
# macOS: brew install httpd

# Run load test
ab -n 1000 -c 10 http://localhost:8000/api/health/
```

Expected output should show:
- No failed requests
- Consistent response times
- Connection pool handling concurrent requests efficiently

### 5. Test Frontend-Backend Integration

**Test User Flow:**

1. Open http://localhost:3000
2. Click "Login" button
3. Sign in with Google (if Firebase Auth configured)
4. Navigate to Dashboard
5. Check that data loads from backend
6. Check browser console for errors
7. Check Network tab for API calls

**Verify CORS:**

In browser console:
```javascript
fetch('http://localhost:8000/api/health/')
  .then(r => r.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));
```

Should return health status without CORS errors.

## Performance Benchmarks

### Expected Performance Metrics

**With Connection Pool:**
- Simple API calls: < 100ms
- Cached responses: < 200ms
- ML inference: < 2s
- Agent orchestration: < 3s
- Concurrent requests (10): ~1.5s total

**Connection Pool Benefits:**
- Connection reuse: ~50-100ms saved per request
- Concurrent handling: 10x improvement
- Resource efficiency: 80% reduction in connection overhead

### Monitoring Performance

**Backend Logs:**
```bash
tail -f backend/logs/health_ai.log
```

**Connection Pool Logs:**
Look for:
- `Connection acquired: conn_X`
- `Connection released: conn_X`
- `Health check complete`
- `Cleaned up X idle connections`

## Troubleshooting

### Backend Not Starting

**Issue:** `ModuleNotFoundError`
```bash
cd backend
pip install -r requirements.txt
```

**Issue:** `django.db.utils.OperationalError`
```bash
cd backend
python manage.py migrate
```

**Issue:** Firebase authentication fails
- Check `firebase-credentials.json` exists
- Verify path in `backend/.env`

### Frontend Not Starting

**Issue:** `Cannot find module`
```bash
cd frontend
npm install
```

**Issue:** `VITE_FIREBASE_API_KEY is not defined`
- Check `frontend/.env` exists
- Copy from `frontend/.env.example`

### Connection Pool Issues

**Issue:** `TimeoutError` when getting connections
- Increase `max_size` in pool configuration
- Check for connection leaks (not releasing connections)
- Verify Firestore connectivity

**Issue:** High number of failed connections
- Check network connectivity
- Verify Firebase credentials
- Check Firestore service status

### CORS Errors

**Issue:** `Access-Control-Allow-Origin` error

Add to `backend/.env`:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Restart backend server.

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

## Continuous Integration

### GitHub Actions Workflow

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest -v
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: 18
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm run test:run
```

## Test Coverage Goals

- **Backend:** > 80% code coverage
- **Frontend:** > 70% code coverage
- **Connection Pool:** 100% coverage (critical component)
- **API Endpoints:** 100% coverage

## Next Steps

After successful testing:

1. ✅ Review test results
2. ✅ Fix any failing tests
3. ✅ Monitor performance metrics
4. ✅ Deploy to staging environment
5. ✅ Run tests in staging
6. ✅ Deploy to production

## Additional Resources

- **Backend README:** `backend/README.md`
- **Frontend README:** `frontend/README.md`
- **Connection Pool README:** `backend/common/CONNECTION_POOL_README.md`
- **API Documentation:** http://localhost:8000/api/docs/
- **Project Structure:** `PROJECT_STRUCTURE.md`

## Support

For issues or questions:
1. Check logs: `backend/logs/health_ai.log`
2. Review documentation
3. Check GitHub issues
4. Contact development team

---

**Status:** 🟢 Ready for Testing

**Last Updated:** 2024-01-15
