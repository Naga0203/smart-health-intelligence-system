# Postman Quick Start Guide

## Setup (5 Minutes)

### Step 1: Import Collection

1. Open Postman
2. Click **Import** button (top left)
3. Drag and drop `postman_collection.json` or click **Upload Files**
4. Collection "AI Health Intelligence API" will appear in your sidebar

### Step 2: Set Environment Variables

1. Click the **Environment** dropdown (top right)
2. Click **+** to create new environment
3. Name it "Local Development"
4. Add variables:

| Variable | Initial Value | Current Value |
|----------|--------------|---------------|
| `base_url` | `http://localhost:8000/api` | `http://localhost:8000/api` |
| `firebase_token` | (leave empty) | (your token here) |

5. Click **Save**
6. Select "Local Development" from environment dropdown

### Step 3: Start Django Server

```bash
py manage.py runserver
```

Server will start on `http://localhost:8000`

## Quick Test (No Authentication Required)

### 1. Health Check

- Open: **System & Model Info** → **Health Check**
- Click **Send**
- Expected: `200 OK` with `{"status": "healthy", "timestamp": "..."}`

### 2. System Status

- Open: **System & Model Info** → **System Status**
- Click **Send**
- Expected: `200 OK` with component status

### 3. List Diseases

- Open: **System & Model Info** → **List Diseases**
- Click **Send**
- Expected: `200 OK` with list of supported diseases

## Testing with Authentication

### Get Firebase Token

**Option 1: From Browser Console (if you have a frontend)**
```javascript
firebase.auth().currentUser.getIdToken().then(token => console.log(token))
```

**Option 2: Firebase REST API**
```bash
curl -X POST \
  'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "user@example.com",
    "password": "password",
    "returnSecureToken": true
  }'
```

Copy the `idToken` from the response.

### Set Token in Postman

1. Click **Environments** → **Local Development**
2. Paste token in `firebase_token` **Current Value**
3. Click **Save**

### Test Authenticated Endpoints

#### 1. Get User Profile

- Open: **User Profile** → **Get User Profile**
- Click **Send**
- Expected: `200 OK` with user profile (creates profile if first time)

#### 2. Update User Profile

- Open: **User Profile** → **Update User Profile**
- Modify the JSON body as needed
- Click **Send**
- Expected: `200 OK` with updated profile

#### 3. Get User Statistics

- Open: **User Profile** → **Get User Statistics**
- Click **Send**
- Expected: `200 OK` with assessment statistics

#### 4. Health Analysis

- Open: **Health Analysis** → **Health Analysis (Authenticated)**
- Modify symptoms/age/gender as needed
- Click **Send**
- Expected: `200 OK` with complete health analysis

#### 5. Assessment History

- Open: **Assessment History** → **Get Assessment History**
- Click **Send**
- Expected: `200 OK` with paginated assessment list

## Testing Rate Limiting

### Test Burst Limit (10/minute)

1. Open: **Rate Limiting Tests** → **Test Burst Rate Limit**
2. Click **Send** 15 times rapidly
3. After 10 requests, you should get:
   ```json
   {
     "error": "rate_limit_exceeded",
     "message": "Too many requests",
     "wait_seconds": 60,
     "status_code": 429
   }
   ```

### Test Anonymous Limit (5/hour)

1. Open: **Rate Limiting Tests** → **Test Anonymous Rate Limit**
2. Click **Send** 10 times
3. After 5 requests, you should get `429 Too Many Requests`

### Using Collection Runner

1. Click **Collections** → **AI Health Intelligence API**
2. Click **Run** button
3. Select folder: **Rate Limiting Tests**
4. Set **Iterations**: 15
5. Click **Run AI Health Intelligence API**
6. Observe rate limiting in action

## Common Requests

### Create Health Assessment

```http
POST {{base_url}}/health/analyze
Authorization: Bearer {{firebase_token}}
Content-Type: application/json

{
  "symptoms": ["fatigue", "increased_thirst", "frequent_urination"],
  "age": 35,
  "gender": "male",
  "additional_info": {
    "weight": 75,
    "height": 175
  }
}
```

### Update Profile

```http
PUT {{base_url}}/user/profile
Authorization: Bearer {{firebase_token}}
Content-Type: application/json

{
  "display_name": "John Doe",
  "phone_number": "+1234567890",
  "gender": "male",
  "medical_history": ["diabetes"],
  "allergies": ["penicillin"]
}
```

### Get Assessment History (Paginated)

```http
GET {{base_url}}/user/assessments?page=1&page_size=10&sort=created_at&order=desc
Authorization: Bearer {{firebase_token}}
```

## Troubleshooting

### 401 Unauthorized

**Problem**: `{"error": "authentication_error", "message": "Authentication failed"}`

**Solutions**:
1. Check Firebase token is set in environment variables
2. Verify token hasn't expired (tokens expire after 1 hour)
3. Get a fresh token
4. Ensure Authorization header format: `Bearer YOUR_TOKEN`

### 429 Too Many Requests

**Problem**: `{"error": "rate_limit_exceeded", "wait_seconds": 60}`

**Solutions**:
1. Wait for the specified time
2. Clear cache (for testing):
   ```bash
   py manage.py shell
   >>> from django.core.cache import cache
   >>> cache.clear()
   ```

### Connection Refused

**Problem**: Cannot connect to `http://localhost:8000`

**Solution**: Start Django server:
```bash
py manage.py runserver
```

### 500 Internal Server Error

**Problem**: Server error

**Solutions**:
1. Check Django server console for error details
2. Verify Firebase credentials are configured
3. Check database connection
4. Review server logs in `logs/health_ai.log`

## Tips & Tricks

### Save Responses

1. After sending a request, click **Save Response**
2. Click **Save as Example**
3. Name it (e.g., "Success Response")
4. Examples appear under each request

### Use Pre-request Scripts

Add to request **Pre-request Script** tab:
```javascript
// Auto-refresh timestamp
pm.environment.set("timestamp", new Date().toISOString());

// Log request details
console.log("Sending request to:", pm.request.url);
```

### Use Tests

Add to request **Tests** tab:
```javascript
// Check status code
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Check response time
pm.test("Response time < 5000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(5000);
});

// Check response structure
pm.test("Response has user_id", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('user_id');
});
```

### Organize Requests

Create folders:
1. Right-click collection
2. **Add Folder**
3. Name it (e.g., "Development", "Testing")
4. Drag requests into folders

### Share Collection

1. Click collection **...** menu
2. **Share**
3. Generate link or export JSON
4. Share with team

## Next Steps

1. **Explore All Endpoints**: Try each request in the collection
2. **Customize Requests**: Modify request bodies for your use cases
3. **Add Tests**: Add test scripts to verify responses
4. **Create Workflows**: Chain requests using Collection Runner
5. **Monitor API**: Use Postman Monitors for automated testing

## Resources

- [Full API Testing Guide](./API_TESTING_GUIDE.md)
- [Rate Limiting Documentation](./API_RATE_LIMITING.md)
- [Implementation Summary](./IMPLEMENTATION_SUMMARY_USER_ENDPOINTS.md)
- [Postman Documentation](https://learning.postman.com/docs/)

## Quick Reference

### Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Health check |
| `/status` | GET | No | System status |
| `/model/info` | GET | No | Model info |
| `/diseases` | GET | No | List diseases |
| `/assess` | POST | No | Health assessment |
| `/health/analyze` | POST | Yes | Full analysis |
| `/user/profile` | GET | Yes | Get profile |
| `/user/profile` | PUT | Yes | Update profile |
| `/user/statistics` | GET | Yes | User stats |
| `/user/assessments` | GET | Yes | Assessment history |
| `/user/assessments/{id}` | GET | Yes | Assessment detail |

### Rate Limits

| User Type | Burst | Hourly | Daily |
|-----------|-------|--------|-------|
| Authenticated | 10/min | 100/hr | 200/day |
| Anonymous | - | 5/hr | - |
| IP-based | - | 200/hr | - |

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `base_url` | API base URL | `http://localhost:8000/api` |
| `firebase_token` | Firebase ID token | `eyJhbGciOiJSUzI1...` |
| `assessment_id` | Assessment ID for detail endpoint | `abc123` |

---

**Happy Testing! 🚀**
