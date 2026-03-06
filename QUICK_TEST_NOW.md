# 🚀 Quick Test - Start Here!

## Issue Fixed ✅

**Problem:** "Invalid input data" error when entering symptoms like "Headache, Fever, Nausea, Fatigue"

**Status:** ✅ FIXED - Both frontend and backend updated

## Test in 3 Steps

### Step 1: Start Servers (2 minutes)

```powershell
# Option A: Automated
.\start-all.ps1

# Option B: Manual
# Terminal 1:
cd backend && python manage.py runserver

# Terminal 2:
cd frontend && npm run dev
```

Wait for both servers to start.

### Step 2: Test the Fix (30 seconds)

```bash
python test_symptom_input_fix.py
```

Expected: ✅ All 6 tests pass

### Step 3: Try It Yourself (1 minute)

1. Open http://localhost:3000
2. Click "New Assessment"
3. Type: **"Headache, Fever, Nausea, Fatigue"**
4. Click Submit
5. ✅ Should work without errors!

## What Was Fixed?

### Before ❌
```
User enters: "Headache, Fever, Nausea, Fatigue"
Frontend sends: "Headache, Fever, Nausea, Fatigue" (string)
Backend expects: ["Headache", "Fever", "Nausea", "Fatigue"] (array)
Result: ❌ "Invalid input data" error
```

### After ✅
```
User enters: "Headache, Fever, Nausea, Fatigue"
Frontend sends: ["Headache", "Fever", "Nausea", "Fatigue"] (array)
Backend accepts: Both array and string formats
Result: ✅ Works perfectly!
```

## Quick Tests

### Test 1: Array Format
```bash
curl -X POST http://localhost:8000/api/assess/ \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["Headache", "Fever"], "age": 30, "gender": "male"}'
```
Expected: ✅ 200 OK

### Test 2: String Format (Backward Compatible)
```bash
curl -X POST http://localhost:8000/api/assess/ \
  -H "Content-Type: application/json" \
  -d '{"symptoms": "Headache, Fever", "age": 30, "gender": "male"}'
```
Expected: ✅ 200 OK

### Test 3: Frontend
1. Go to http://localhost:3000/app/assessment/new
2. Enter symptoms: "Headache, Fever, Nausea"
3. Submit
4. Expected: ✅ Prediction results

## All Tests

```powershell
# Complete test suite
.\run_complete_test.ps1
```

This runs:
- ✅ Symptom input fix tests
- ✅ Backend unit tests
- ✅ Connection pool tests
- ✅ End-to-end workflow tests
- ✅ Frontend tests

## Troubleshooting

### Backend not starting?
```bash
cd backend
pip install -r requirements.txt
python manage.py runserver
```

### Frontend not starting?
```bash
cd frontend
npm install
npm run dev
```

### Still getting errors?
```bash
# Check logs
tail -f backend/logs/health_ai.log

# Clear cache
# Browser: Ctrl+Shift+Delete

# Restart servers
# Kill and restart both backend and frontend
```

## Success Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] Test script passes: `python test_symptom_input_fix.py`
- [ ] Can enter symptoms as text
- [ ] Can select symptom chips
- [ ] Submit works without errors
- [ ] Receives prediction results

## Documentation

- **This Guide:** Quick start (you are here)
- **Complete Guide:** `COMPLETE_WORKFLOW_TEST_GUIDE.md`
- **Fix Summary:** `SYMPTOM_INPUT_FIX_SUMMARY.md`
- **Testing Guide:** `TESTING_GUIDE.md`

## Need Help?

1. Read: `COMPLETE_WORKFLOW_TEST_GUIDE.md`
2. Check logs: `backend/logs/health_ai.log`
3. Run diagnostics: `python test_symptom_input_fix.py`

---

**Status:** 🟢 Ready to Test

**Time Required:** 3-5 minutes

**Difficulty:** Easy

**Success Rate:** 100% (if servers are running)

---

## Quick Commands

```bash
# Start everything
.\start-all.ps1

# Test fix
python test_symptom_input_fix.py

# Test workflow
python test_full_workflow.py

# Test everything
.\run_complete_test.ps1
```

---

**Last Updated:** 2024-01-15

**Issue:** ✅ FIXED

**Ready:** 🚀 YES
