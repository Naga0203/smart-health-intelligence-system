"""
Simple API endpoint testing script.

Tests the newly implemented user profile and assessment history endpoints.
Run this after starting the Django server.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
FIREBASE_TOKEN = ""  # Add your Firebase token here for authenticated endpoints

# Headers
headers_no_auth = {
    "Content-Type": "application/json"
}

headers_with_auth = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {FIREBASE_TOKEN}"
}


def test_health_check():
    """Test simple health check endpoint."""
    print("\n" + "="*60)
    print("Testing: Health Check")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_system_status():
    """Test system status endpoint."""
    print("\n" + "="*60)
    print("Testing: System Status")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/status")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code in [200, 503]


def test_model_info():
    """Test model info endpoint."""
    print("\n" + "="*60)
    print("Testing: Model Info")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/model/info")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code in [200, 503]


def test_diseases_list():
    """Test diseases list endpoint."""
    print("\n" + "="*60)
    print("Testing: Diseases List")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/diseases")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total Diseases: {data.get('total', 0)}")
        print(f"First 5 Diseases: {data.get('diseases', [])[:5]}")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code in [200, 503]


def test_user_profile_get():
    """Test get user profile endpoint (requires auth)."""
    print("\n" + "="*60)
    print("Testing: Get User Profile (Authenticated)")
    print("="*60)
    
    if not FIREBASE_TOKEN:
        print("⚠️  Skipped: No Firebase token provided")
        return None
    
    response = requests.get(f"{BASE_URL}/user/profile", headers=headers_with_auth)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_user_profile_update():
    """Test update user profile endpoint (requires auth)."""
    print("\n" + "="*60)
    print("Testing: Update User Profile (Authenticated)")
    print("="*60)
    
    if not FIREBASE_TOKEN:
        print("⚠️  Skipped: No Firebase token provided")
        return None
    
    update_data = {
        "display_name": "Test User",
        "phone_number": "+1234567890",
        "gender": "male",
        "medical_history": ["test condition"],
        "allergies": ["test allergy"]
    }
    
    response = requests.put(
        f"{BASE_URL}/user/profile",
        headers=headers_with_auth,
        json=update_data
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_user_statistics():
    """Test user statistics endpoint (requires auth)."""
    print("\n" + "="*60)
    print("Testing: User Statistics (Authenticated)")
    print("="*60)
    
    if not FIREBASE_TOKEN:
        print("⚠️  Skipped: No Firebase token provided")
        return None
    
    response = requests.get(f"{BASE_URL}/user/statistics", headers=headers_with_auth)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_assessment_history():
    """Test assessment history endpoint (requires auth)."""
    print("\n" + "="*60)
    print("Testing: Assessment History (Authenticated)")
    print("="*60)
    
    if not FIREBASE_TOKEN:
        print("⚠️  Skipped: No Firebase token provided")
        return None
    
    params = {
        "page": 1,
        "page_size": 10,
        "sort": "created_at",
        "order": "desc"
    }
    
    response = requests.get(
        f"{BASE_URL}/user/assessments",
        headers=headers_with_auth,
        params=params
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_health_assessment_no_auth():
    """Test health assessment without authentication."""
    print("\n" + "="*60)
    print("Testing: Health Assessment (No Auth)")
    print("="*60)
    
    assessment_data = {
        "symptoms": ["fever", "cough", "headache"],
        "age": 28,
        "gender": "female",
        "user_id": "test_user_123"
    }
    
    response = requests.post(
        f"{BASE_URL}/assess",
        headers=headers_no_auth,
        json=assessment_data
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_rate_limiting():
    """Test rate limiting by making multiple rapid requests."""
    print("\n" + "="*60)
    print("Testing: Rate Limiting (Anonymous)")
    print("="*60)
    print("Making 10 rapid requests to test 5/hour anonymous limit...")
    
    assessment_data = {
        "symptoms": ["test"],
        "age": 30,
        "gender": "male"
    }
    
    success_count = 0
    rate_limited_count = 0
    
    for i in range(10):
        response = requests.post(
            f"{BASE_URL}/assess",
            headers=headers_no_auth,
            json=assessment_data
        )
        
        if response.status_code == 200:
            success_count += 1
            print(f"Request {i+1}: ✓ Success (200)")
        elif response.status_code == 429:
            rate_limited_count += 1
            data = response.json()
            wait_time = data.get('wait_seconds', 'unknown')
            print(f"Request {i+1}: ✗ Rate Limited (429) - Wait {wait_time}s")
        else:
            print(f"Request {i+1}: ? Unexpected ({response.status_code})")
    
    print(f"\nResults: {success_count} successful, {rate_limited_count} rate limited")
    print(f"Rate limiting is {'WORKING' if rate_limited_count > 0 else 'NOT WORKING'}")
    
    return rate_limited_count > 0


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("AI Health Intelligence API - Endpoint Testing")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Firebase Token: {'Provided' if FIREBASE_TOKEN else 'Not Provided (some tests will be skipped)'}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test public endpoints
    results['Health Check'] = test_health_check()
    results['System Status'] = test_system_status()
    results['Model Info'] = test_model_info()
    results['Diseases List'] = test_diseases_list()
    results['Health Assessment (No Auth)'] = test_health_assessment_no_auth()
    
    # Test authenticated endpoints
    results['Get User Profile'] = test_user_profile_get()
    results['Update User Profile'] = test_user_profile_update()
    results['User Statistics'] = test_user_statistics()
    results['Assessment History'] = test_assessment_history()
    
    # Test rate limiting
    results['Rate Limiting'] = test_rate_limiting()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    for test_name, result in results.items():
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⚠ SKIP"
        print(f"{status:10} {test_name}")
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    
    if failed == 0 and passed > 0:
        print("\n✅ All tests passed!")
    elif failed > 0:
        print(f"\n❌ {failed} test(s) failed")
    
    print("\n" + "="*60)
    print("Note: To test authenticated endpoints, add your Firebase token")
    print("to the FIREBASE_TOKEN variable at the top of this script.")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API server.")
        print("Make sure the Django server is running on http://localhost:8000")
        print("\nStart the server with: py manage.py runserver")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
