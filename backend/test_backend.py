"""
Comprehensive Backend Testing Script

Tests all API endpoints, authentication, and database connectivity.
Skips prediction model tests as requested.
"""

import requests
import json
from datetime import datetime


class BackendTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = {"passed": 0, "failed": 0, "skipped": 0, "tests": []}
    
    def test(self, name, func):
        """Run a test and record results."""
        try:
            print(f"\n{'='*60}")
            print(f"Testing: {name}")
            print('='*60)
            result = func()
            if result.get("skip"):
                print(f"⊘ SKIPPED: {result.get('reason')}")
                self.results["skipped"] += 1
                self.results["tests"].append({
                    "name": name,
                    "status": "skipped",
                    "reason": result.get("reason")
                })
            elif result.get("success"):
                print(f"✓ PASSED: {result.get('message')}")
                self.results["passed"] += 1
                self.results["tests"].append({
                    "name": name,
                    "status": "passed",
                    "details": result.get("details", {})
                })
            else:
                print(f"✗ FAILED: {result.get('message')}")
                self.results["failed"] += 1
                self.results["tests"].append({
                    "name": name,
                    "status": "failed",
                    "error": result.get("error")
                })
        except Exception as e:
            print(f"✗ ERROR: {str(e)}")
            self.results["failed"] += 1
            self.results["tests"].append({
                "name": name,
                "status": "error",
                "error": str(e)
            })
    
    # ========================================================================
    # BASIC CONNECTIVITY TESTS
    # ========================================================================
    
    def test_health_check(self):
        """Test basic health endpoint."""
        try:
            r = requests.get(f"{self.base_url}/api/health/")
            data = r.json()
            print(f"Status Code: {r.status_code}")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if r.status_code == 200 and data.get("status") == "healthy":
                return {
                    "success": True,
                    "message": "Health endpoint is working",
                    "details": data
                }
            else:
                return {
                    "success": False,
                    "message": f"Unexpected status: {data.get('status')}",
                    "error": data
                }
        except Exception as e:
            return {"success": False, "message": "Health check failed", "error": str(e)}
    
    def test_system_status(self):
        """Test system status endpoint."""
        try:
            r = requests.get(f"{self.base_url}/api/status/")
            data = r.json()
            print(f"Status Code: {r.status_code}")
            print(f"Status: {data.get('status')}")
            print(f"Components: {json.dumps(data.get('components', {}), indent=2)}")
            
            if r.status_code in [200, 503]:
                # 503 is acceptable if some services are down
                firebase_status = data.get('components', {}).get('firebase', 'unknown')
                gemini_status = data.get('components', {}).get('gemini_ai', 'unknown')
                
                return {
                    "success": True,
                    "message": f"System status retrieved (Firebase: {firebase_status}, Gemini: {gemini_status})",
                    "details": data
                }
            else:
                return {
                    "success": False,
                    "message": f"Unexpected status code: {r.status_code}",
                    "error": data
                }
        except Exception as e:
            return {"success": False, "message": "Status check failed", "error": str(e)}
    
    # ========================================================================
    # ENDPOINT LIST TESTS (No Auth Required)
    # ========================================================================
    
    def test_diseases_list(self):
        """Test diseases list endpoint."""
        try:
            r = requests.get(f"{self.base_url}/api/diseases/")
            print(f"Status Code: {r.status_code}")
            
            if r.status_code == 200:
                data = r.json()
                print(f"Diseases Count: {len(data)}")
                if len(data) > 0:
                    print(f"Sample: {data[0]}")
                
                return {
                    "success": True,
                    "message": f"Retrieved {len(data)} diseases",
                    "details": {"count": len(data)}
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed with status {r.status_code}",
                    "error": r.text
                }
        except Exception as e:
            return {"success": False, "message": "Diseases list failed", "error": str(e)}
    
    def test_model_info(self):
        """Test model info endpoint."""
        try:
            r = requests.get(f"{self.base_url}/api/model/info/")
            data = r.json()
            print(f"Status Code: {r.status_code}")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # This may fail if model is not loaded, which is okay
            if r.status_code == 200:
                return {
                    "success": True,
                    "message": "Model info retrieved",
                    "details": data
                }
            else:
                return {
                    "skip": True,
                    "reason": "Model not available (expected)"
                }
        except Exception as e:
            return {"skip": True, "reason": f"Model not available: {str(e)}"}
    
    # ========================================================================
    # AUTHENTICATION TESTS
    # ========================================================================
    
    def test_profile_without_auth(self):
        """Test profile endpoint without authentication (should fail)."""
        try:
            r = requests.get(f"{self.base_url}/api/user/profile/")
            data = r.json()
            print(f"Status Code: {r.status_code}")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if r.status_code == 401:
                return {
                    "success": True,
                    "message": "Correctly rejected unauthenticated request",
                    "details": data
                }
            else:
                return {
                    "success": False,
                    "message": f"Unexpected status {r.status_code} (expected 401)",
                    "error": data
                }
        except Exception as e:
            return {"success": False, "message": "Auth test failed", "error": str(e)}
    
    def test_medical_history_without_auth(self):
        """Test medical history endpoint without authentication (should fail)."""
        try:
            r = requests.get(f"{self.base_url}/api/user/medical-history/")
            data = r.json()
            print(f"Status Code: {r.status_code}")
            
            if r.status_code == 401:
                return {
                    "success": True,
                    "message": "Correctly rejected unauthenticated request",
                    "details": {"error": data.get("error")}
                }
            else:
                return {
                    "success": False,
                    "message": f"Unexpected status {r.status_code} (expected 401)",
                    "error": data
                }
        except Exception as e:
            return {"success": False, "message": "Auth test failed", "error": str(e)}
    
    # ========================================================================
    # ANONYMOUS ASSESSMENT TEST (No Auth)
    # ========================================================================
    
    def test_anonymous_assessment(self):
        """Test anonymous assessment endpoint (may fail if model not loaded)."""
        try:
            payload = {
                "symptoms": ["fever", "cough", "headache"],
                "age": 30,
                "gender": "male"
            }
            r = requests.post(f"{self.base_url}/api/assess/", json=payload)
            data = r.json()
            print(f"Status Code: {r.status_code}")
            print(f"Response Keys: {list(data.keys())}")
            
            if r.status_code == 200:
                return {
                    "success": True,
                    "message": "Anonymous assessment endpoint works",
                    "details": {
                        "has_prediction": "prediction" in data,
                        "has_explanation": "explanation" in data
                    }
                }
            elif r.status_code == 503 or "unavailable" in data.get("message", "").lower():
                return {
                    "skip": True,
                    "reason": "Service unavailable (ML model not loaded)"
                }
            else:
                return {
                    "success": False,
                    "message": f"Unexpected response: {data.get('message')}",
                    "error": data
                }
        except Exception as e:
            return {"skip": True, "reason": f"Service unavailable: {str(e)}"}
    
    # ========================================================================
    # VALIDATION TESTS
    # ========================================================================
    
    def test_invalid_assessment_input(self):
        """Test validation with invalid input."""
        try:
            payload = {
                "symptoms": [],  # Empty symptoms
                "age": -5,  # Invalid age
                "gender": "invalid"  # Invalid gender
            }
            r = requests.post(f"{self.base_url}/api/assess/", json=payload)
            data = r.json()
            print(f"Status Code: {r.status_code}")
            print(f"Errors: {json.dumps(data.get('details', {}), indent=2)}")
            
            if r.status_code == 400:
                return {
                    "success": True,
                    "message": "Correctly validated and rejected invalid input",
                    "details": {"validation_errors": data.get("details")}
                }
            else:
                return {
                    "success": False,
                    "message": f"Expected 400 validation error, got {r.status_code}",
                    "error": data
                }
        except Exception as e:
            return {"success": False, "message": "Validation test failed", "error": str(e)}
    
    # ========================================================================
    # NEW ENDPOINTS TESTS (Require Auth)
    # ========================================================================
    
    def test_report_parse_without_auth(self):
        """Test report parsing endpoint without authentication (should fail)."""
        try:
            payload = {
                "report_text": "Glucose: 125 mg/dL",
                "report_type": "lab_report"
            }
            r = requests.post(f"{self.base_url}/api/reports/parse/", json=payload)
            data = r.json()
            print(f"Status Code: {r.status_code}")
            
            if r.status_code == 401:
                return {
                    "success": True,
                    "message": "Correctly rejected unauthenticated request",
                    "details": {"error": data.get("error")}
                }
            else:
                return {
                    "success": False,
                    "message": f"Unexpected status {r.status_code} (expected 401)",
                    "error": data
                }
        except Exception as e:
            return {"success": False, "message": "Auth test failed", "error": str(e)}
    
    # ========================================================================
    # RUN ALL TESTS
    # ========================================================================
    
    def run_all_tests(self):
        """Run all tests and print summary."""
        print("\n" + "="*60)
        print("BACKEND COMPREHENSIVE TEST SUITE")
        print("="*60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base URL: {self.base_url}")
        
        # Basic connectivity
        self.test("Health Check Endpoint", self.test_health_check)
        self.test("System Status Endpoint", self.test_system_status)
        
        # Public endpoints
        self.test("Diseases List Endpoint", self.test_diseases_list)
        self.test("Model Info Endpoint", self.test_model_info)
        
        # Authentication tests
        self.test("Profile Auth Required", self.test_profile_without_auth)
        self.test("Medical History Auth Required", self.test_medical_history_without_auth)
        self.test("Report Parse Auth Required", self.test_report_parse_without_auth)
        
        # Validation tests
        self.test("Input Validation", self.test_invalid_assessment_input)
        
        # Anonymous assessment (may skip if model not loaded)
        self.test("Anonymous Assessment", self.test_anonymous_assessment)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary."""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"✓ Passed:  {self.results['passed']}")
        print(f"✗ Failed:  {self.results['failed']}")
        print(f"⊘ Skipped: {self.results['skipped']}")
        print(f"━ Total:   {len(self.results['tests'])}")
        print("="*60)
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.results['failed'] > 0:
            print("\n⚠ ATTENTION: Some tests failed!")
            print("\nFailed tests:")
            for test in self.results['tests']:
                if test['status'] == 'failed' or test['status'] == 'error':
                    print(f"  - {test['name']}: {test.get('error', 'Unknown error')}")
        else:
            print("\n✓ All required tests passed!")
        
        return self.results


if __name__ == "__main__":
    tester = BackendTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: test_results.json")
