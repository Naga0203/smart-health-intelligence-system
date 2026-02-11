# API Documentation Quick Start

## 🚀 Get Started in 3 Steps

### Step 1: Start the Server
```bash
python manage.py runserver
```

### Step 2: Open Interactive Documentation
Click one of these links:
- **Swagger UI**: http://localhost:8000/api/docs/ (Try endpoints live!)
- **ReDoc**: http://localhost:8000/api/redoc/ (Beautiful docs!)

### Step 3: Try Your First Request

#### In Swagger UI:
1. Click on `POST /api/assess/` (no auth needed)
2. Click "Try it out"
3. Use this example:
   ```json
   {
     "symptoms": ["fever", "cough"],
     "age": 30,
     "gender": "female"
   }
   ```
4. Click "Execute"
5. See the response!

#### With cURL:
```bash
curl -X POST http://localhost:8000/api/assess/ \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["fever", "cough"], "age": 30, "gender": "female"}'
```

## 📚 Documentation Resources

### Interactive (Best for Exploring)
- **Swagger UI**: http://localhost:8000/api/docs/
  - Try endpoints directly in browser
  - See all request/response examples
  - Test authentication

- **ReDoc**: http://localhost:8000/api/redoc/
  - Clean, readable format
  - Great for learning the API
  - Searchable

### Written (Best for Reference)
- **Comprehensive Guide**: [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md)
  - Complete API reference
  - Code examples in Python, JavaScript, cURL
  - Best practices and security

- **Quick Reference**: [`API_QUICK_REFERENCE.md`](./API_QUICK_REFERENCE.md)
  - Quick endpoint lookup
  - Common examples
  - Status codes

- **Navigation Guide**: [`API_README.md`](./API_README.md)
  - How to use all documentation
  - Getting started guide
  - Testing instructions

## 🔑 Authentication (For Protected Endpoints)

### Get Firebase Token
1. Sign in with Google via Firebase
2. Get your ID token from Firebase SDK
3. In Swagger UI, click "Authorize"
4. Enter: `Bearer <your_token>`

### Example with Token
```bash
curl -X POST http://localhost:8000/api/health/analyze/ \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["fever"], "age": 35, "gender": "male"}'
```

## 📊 All Endpoints at a Glance

| Endpoint | Auth | What It Does |
|----------|------|--------------|
| `POST /api/health/analyze/` | ✓ | Full health analysis (best rates) |
| `POST /api/assess/` | ✗ | Quick health check (limited) |
| `GET /api/user/profile/` | ✓ | Your profile |
| `GET /api/user/assessments/` | ✓ | Your history |
| `GET /api/status/` | ✗ | System health |
| `GET /api/diseases/` | ✗ | Supported diseases |

## 💡 Pro Tips

1. **Start with Swagger UI** - It's the easiest way to explore
2. **Use ReDoc for learning** - Great for understanding the full API
3. **Keep Quick Reference handy** - For fast lookups while coding
4. **Check system status first** - `GET /api/status/` to verify everything works

## ❓ Need Help?

- **Can't find something?** → Check [`API_README.md`](./API_README.md)
- **Want details?** → Read [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md)
- **Quick lookup?** → Use [`API_QUICK_REFERENCE.md`](./API_QUICK_REFERENCE.md)
- **System issues?** → Visit http://localhost:8000/api/status/

## 🎯 Common Use Cases

### Check System Status
```bash
curl http://localhost:8000/api/status/
```

### Get Supported Diseases
```bash
curl http://localhost:8000/api/diseases/
```

### Anonymous Health Check
```bash
curl -X POST http://localhost:8000/api/assess/ \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["headache"], "age": 25, "gender": "male"}'
```

### Authenticated Analysis (Better Results!)
```bash
curl -X POST http://localhost:8000/api/health/analyze/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["fatigue", "increased thirst"], "age": 45, "gender": "male"}'
```

---

**Ready to explore?** → http://localhost:8000/api/docs/

**Need the full guide?** → [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md)
