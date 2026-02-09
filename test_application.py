"""
Complete Application Test with API Keys
Tests the AI Health Intelligence System with configured Gemini API
"""

import sys
import os
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_ai_backend.settings')
django.setup()

from agents.orchestrator import OrchestratorAgent
from common.gemini_client import LangChainGeminiClient
from django.conf import settings
import json


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_section(text):
    """Print a formatted section."""
    print("\n" + "-" * 80)
    print(f"  {text}")
    print("-" * 80)


def test_api_configuration():
    """Test if API keys are configured."""
    print_header("STEP 1: TESTING API CONFIGURATION")
    
    # Check Gemini API Key
    gemini_key = settings.GEMINI_API_KEY
    if gemini_key and gemini_key != "your_gemini_api_key_here":
        print("✓ Gemini API Key: CONFIGURED")
        print(f"  Key Preview: {gemini_key[:10]}...{gemini_key[-5:]}")
    else:
        print("✗ Gemini API Key: NOT CONFIGURED")
        print("  Please add your Gemini API key to .env file")
        return False
    
    # Check MongoDB URI
    mongo_uri = settings.MONGODB_SETTINGS['URI']
    print(f"\n✓ MongoDB URI: {mongo_uri}")
    
    # Check Django Secret Key
    if settings.SECRET_KEY:
        print("✓ Django Secret Key: CONFIGURED")
    
    print("\n✓ All API configurations loaded successfully!")
    return True


def test_gemini_connection():
    """Test Gemini AI connection."""
    print_header("STEP 2: TESTING GEMINI AI CONNECTION")
    
    try:
        client = LangChainGeminiClient()
        status = client.get_client_status()
        
        print(f"API Configured: {status['api_configured']}")
        print(f"Model Initialized: {status['model_initialized']}")
        print(f"Framework: {status['framework']}")
        print(f"Model Name: {status['model_name']}")
        
        if not status['model_initialized']:
            print("\n✗ Gemini model failed to initialize")
            print("  Check if your API key is valid")
            return False
        
        # Test connection
        print("\nTesting Gemini AI connection...")
        connection_test = client.test_connection()
        
        if connection_test['success']:
            print("✓ Gemini AI Connection: SUCCESS")
            print(f"  Response: {connection_test['response'][:100]}...")
            return True
        else:
            print("✗ Gemini AI Connection: FAILED")
            print(f"  Error: {connection_test['error']}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing Gemini connection: {str(e)}")
        return False


def test_complete_pipeline():
    """Test the complete health assessment pipeline with real AI."""
    print_header("STEP 3: TESTING COMPLETE PIPELINE WITH REAL AI")
    
    # Initialize orchestrator
    print("Initializing Orchestrator Agent...")
    orchestrator = OrchestratorAgent()
    print("✓ Orchestrator initialized\n")
    
    # Prepare test cases
    test_cases = [
        {
            "name": "Diabetes Symptoms",
            "input": {
                "user_id": "test_user_diabetes",
                "age": 45,
                "gender": "male",
                "symptoms": [
                    "increased thirst",
                    "frequent urination",
                    "unexplained weight loss",
                    "fatigue",
                    "blurred vision"
                ],
                "additional_info": {
                    "family_history": "diabetes"
                }
            }
        },
        {
            "name": "Heart Disease Symptoms",
            "input": {
                "user_id": "test_user_heart",
                "age": 55,
                "gender": "female",
                "symptoms": [
                    "chest pain",
                    "shortness of breath",
                    "fatigue",
                    "irregular heartbeat"
                ]
            }
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print_section(f"TEST CASE {i}: {test_case['name']}")
        
        print(f"\nInput:")
        print(f"  Age: {test_case['input']['age']}")
        print(f"  Gender: {test_case['input']['gender']}")
        print(f"  Symptoms: {', '.join(test_case['input']['symptoms'])}")
        
        print(f"\nRunning pipeline...")
        print("  → Validation")
        print("  → Data Extraction (Gemini AI)")
        print("  → ML Prediction")
        print("  → Confidence Evaluation")
        print("  → Explanation Generation (Gemini AI)")
        print("  → Recommendation Generation")
        print("  → MongoDB Storage")
        print("  → Response Building")
        
        # Run pipeline
        result = orchestrator.process(test_case['input'])
        
        if result["success"]:
            print("\n✓ Pipeline completed successfully!")
            
            data = result["data"]
            
            # Display results
            print("\nRESULTS:")
            
            # Prediction
            if "prediction" in data:
                pred = data["prediction"]
                print(f"\n  PREDICTION:")
                print(f"    Disease: {pred.get('disease', 'N/A')}")
                print(f"    Probability: {pred.get('probability_percent', 0)}%")
                print(f"    Confidence: {pred.get('confidence', 'N/A')}")
            
            # Data Extraction
            if "extraction" in data:
                ext = data["extraction"]
                print(f"\n  DATA EXTRACTION (Gemini AI):")
                print(f"    Confidence: {ext.get('confidence', 0):.1%}")
                print(f"    Method: {ext.get('method', 'N/A')}")
            
            # Explanation
            if "explanation" in data:
                exp = data["explanation"]
                print(f"\n  EXPLANATION (Gemini AI):")
                print(f"    Generated By: {exp.get('generated_by', 'N/A')}")
                if "main_explanation" in exp:
                    explanation_text = exp["main_explanation"]
                    # Show first 200 characters
                    if len(explanation_text) > 200:
                        print(f"    Text: {explanation_text[:200]}...")
                    else:
                        print(f"    Text: {explanation_text}")
            
            # Treatment
            if "recommendations" in data:
                rec = data["recommendations"]
                if "treatment_information" in rec:
                    treat = rec["treatment_information"]
                    if treat.get('available'):
                        print(f"\n  TREATMENT INFORMATION:")
                        print(f"    Available: Yes")
                        print(f"    Systems: {', '.join(treat.get('systems', {}).keys())}")
            
            # Metadata
            if "metadata" in data:
                meta = data["metadata"]
                print(f"\n  METADATA:")
                print(f"    Processing Time: {meta.get('processing_time_seconds', 0)}s")
                print(f"    Timestamp: {meta.get('timestamp', 'N/A')}")
            
            results.append({
                "test_case": test_case['name'],
                "success": True,
                "data": data
            })
            
        else:
            print(f"\n✗ Pipeline failed!")
            print(f"  Error: {result.get('message', 'Unknown error')}")
            results.append({
                "test_case": test_case['name'],
                "success": False,
                "error": result.get('message')
            })
    
    return results


def test_individual_ai_features():
    """Test individual AI features."""
    print_header("STEP 4: TESTING INDIVIDUAL AI FEATURES")
    
    from agents.data_extraction import DataExtractionAgent
    from agents.explanation import LangChainExplanationAgent
    
    # Test Data Extraction with Gemini
    print_section("Testing Data Extraction Agent (Gemini AI)")
    
    extraction_agent = DataExtractionAgent()
    extraction_input = {
        "symptoms": ["increased thirst", "frequent urination", "fatigue"],
        "age": 45,
        "gender": "male",
        "disease": "diabetes"
    }
    
    extraction_result = extraction_agent.process(extraction_input)
    
    if extraction_result['success']:
        print("✓ Data Extraction: SUCCESS")
        print(f"  Method: {extraction_result['data']['extraction_method']}")
        print(f"  Confidence: {extraction_result['data']['extraction_confidence']:.1%}")
        print(f"  Features Extracted: {len(extraction_result['data']['features'])}")
    else:
        print("✗ Data Extraction: FAILED")
    
    # Test Explanation Generation with Gemini
    print_section("Testing Explanation Agent (Gemini AI)")
    
    explanation_agent = LangChainExplanationAgent()
    explanation_input = {
        "disease": "diabetes",
        "probability": 0.85,
        "confidence": "HIGH",
        "symptoms": ["increased thirst", "frequent urination", "fatigue"]
    }
    
    explanation_result = explanation_agent.process(explanation_input)
    
    if explanation_result['success']:
        print("✓ Explanation Generation: SUCCESS")
        exp_data = explanation_result['data']
        print(f"  Generated By: {exp_data.get('generated_by', 'N/A')}")
        print(f"  Agent: {exp_data.get('agent', 'N/A')}")
        if 'main_explanation' in exp_data:
            print(f"  Explanation Length: {len(exp_data['main_explanation'])} characters")
    else:
        print("✗ Explanation Generation: FAILED")


def generate_test_report(results):
    """Generate a test report."""
    print_header("TEST REPORT SUMMARY")
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - successful_tests
    
    print(f"Total Test Cases: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for i, result in enumerate(results, 1):
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        print(f"  {i}. {result['test_case']}: {status}")
        if not result['success']:
            print(f"     Error: {result.get('error', 'Unknown')}")
    
    if successful_tests == total_tests:
        print("\n" + "=" * 80)
        print("  🎉 ALL TESTS PASSED! APPLICATION IS WORKING CORRECTLY!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("  ⚠️  SOME TESTS FAILED - CHECK ERRORS ABOVE")
        print("=" * 80)


def main():
    """Main test function."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "AI HEALTH INTELLIGENCE SYSTEM - API TEST" + " " * 23 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        # Step 1: Test API Configuration
        if not test_api_configuration():
            print("\n✗ API configuration test failed. Please configure your API keys.")
            return
        
        # Step 2: Test Gemini Connection
        if not test_gemini_connection():
            print("\n✗ Gemini AI connection test failed. Please check your API key.")
            return
        
        # Step 3: Test Complete Pipeline
        results = test_complete_pipeline()
        
        # Step 4: Test Individual AI Features
        test_individual_ai_features()
        
        # Generate Report
        generate_test_report(results)
        
    except Exception as e:
        print(f"\n✗ TEST SUITE FAILED WITH ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()