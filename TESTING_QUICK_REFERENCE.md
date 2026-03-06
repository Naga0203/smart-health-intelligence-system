# Testing Quick Reference Card

## 🚀 Quick Start

### Start Servers
```powershell
# Option 1: Start both servers
.\start-all.ps1

# Option 2: Manual start
# Terminal 1:
cd backend && python manage.py runserver

# Terminal 2:
cd frontend && npm run dev
```

### Run All Tests
```powershell
.\run_complete_test.ps1
```

## 📋 Individual Test Commands

### Backend Tests

```bash
# Connection Pool Unit Tests
cd backend
pytest common/test_connection_pool.py -v

# Connection Pool Integration Tests
cd backend
python test_connection_pool_integration.py

# All Backend Tests
cd backend
pytest -v

# With Coverage
cd backend
pytest --cov=. --cov-report=html
```

### Frontend Tests

```bash
# Run Tests
cd frontend
npm run test

# Run Once (CI mode)
cd frontend
npm run test:run

# With Coverage
cd frontend
npm run test:coverage
```

### End-to-End Tests

```bash
# Full Workflow Test
python test_full_workflow.py
```

## 🔍 Quick Health Checks

### Backend Health
```bash
curl http://localhost:8000/api/health/
```

Expected: `{"status": "healthy", ...}`

### Frontend Health
Open browser: http://localhost:3000

### Connection Pool Stats
```bash
curl http://localhost:8000/api/pool-stats/
```

(Requires custom endpoint - see TESTING_GUIDE.md)

## 📊 Expected Performance

| Metric | Target | With Pool |
|--------|--------|-----------|
| Simple API | < 100ms | ✓ |
| Cached Response | < 200ms | ✓ |
| ML Inference | < 2s | ✓ |
| Agent Orchestration | < 3s | ✓ |
| Concurrent (10 req) | ~1.5s | ✓ |

## 🐛 Common Issues

### Port Already in Use
```powershell
# Kill port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Module Not Found
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

### CORS Error
Add to `backend/.env`:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Connection Pool Timeout
- Increase `max_size` in pool config
- Check for connection leaks
- Verify Firestore connectivity

## 📁 Important Files

| File | Purpose |
|------|---------|
| `test_full_workflow.py` | End-to-end tests |
| `backend/test_connection_pool_integration.py` | Pool integration tests |
| `backend/common/test_connection_pool.py` | Pool unit tests |
| `TESTING_GUIDE.md` | Complete testing documentation |
| `run_complete_test.ps1` | Automated test runner |

## 🎯 Test Coverage Goals

- Backend: > 80%
- Frontend: > 70%
- Connection Pool: 100%
- API Endpoints: 100%

## 📞 Quick Links

- Backend API: http://localhost:8000/api/
- API Docs: http://localhost:8000/api/docs/
- Frontend: http://localhost:3000
- Logs: `backend/logs/health_ai.log`

## ✅ Pre-Deployment Checklist

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] End-to-end tests pass
- [ ] Performance benchmarks met
- [ ] No CORS errors
- [ ] Connection pool working
- [ ] Frontend loads without errors
- [ ] API documentation updated

## 🔄 Continuous Testing

```bash
# Watch mode (backend)
cd backend
pytest-watch

# Watch mode (frontend)
cd frontend
npm run test
```

## 📈 Monitoring

```bash
# View logs
tail -f backend/logs/health_ai.log

# Monitor pool
# Add custom endpoint and curl in loop
while true; do curl http://localhost:8000/api/pool-stats/; sleep 5; done
```

---

**Quick Command Summary:**

```bash
# Start everything
.\start-all.ps1

# Test everything
.\run_complete_test.ps1

# Backend tests
cd backend && pytest -v

# Frontend tests
cd frontend && npm run test:run

# E2E tests
python test_full_workflow.py
```

---

**Status:** 🟢 Ready to Test

**Last Updated:** 2024-01-15
