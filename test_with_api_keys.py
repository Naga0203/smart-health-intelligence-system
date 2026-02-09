"""
Test script for AI Health Intelligence System with configured API keys.
This version handles LangChain/Pydantic compatibility issues.
"""

import os
import sys
import django
from pathlib import Path
import json

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_ai_backend.settings')
django.setup()

from decouple import config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_success(message):
    """Print success message."""
    print(f"[OK] {message}")


def print_error(message):
    """Print error message."""
    print(f"[ERROR] {message}")


def test_api_configuration():
    """Test if API keys are configured."""
    print_header("STEP 1: TESTING API CONFIGURATION")
    
    try:
        gemini_key = config('GEMINI_API_KEY', default='')
        mongo_uri = config('MONGO_URI', default='')
        secret_key = config('SECRET_KEY', default='')
        
        if gemini_key:
            print_success(f"Gemini API Key: CONFIGURED")
            print(f"  Key Preview: {gemini_key[:10]}...{gemini_key[-5:]}")
        else:
            print_error("Gemini API Key: NOT CONFIGURED")
            return False
        
        if mongo_uri:
            print_success(f"MongoDB URI: {mongo_uri}")
        else:
            print_error("MongoDB URI: NOT CONFIGURED")
        
        if secret_key:
            print_success("Django Secret Key: CONFIGURED")
        else:
            print_error("Django Secret Key: NOT CONFIGURED")
        
        print_success("All API configurations loaded successfully!")
        return True
        
    except Exception as e:
        print_error(f"Configuration error: {str(e)}")
        return False


def test_gemini_direct():
    """Test Gemini AI using direct google-generativeai library."""
    print_header("STEP 2: TESTING GEMINI AI (DIRECT)")
    
    try:
        import google.generativeai as genai
        
        api_key = config('GEMINI_API_KEY', default='')
        if not api_key:
            print_error("Gemini API key not configured")
            return False
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Create model (using correct model name for API v1)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        print_success("Gemini model initialized successfully")
        
        # Test simple generation
        print("\nTesting simple text generation...")
        response = model.generate_content("Say 'Hello from Gemini AI' if you can read this.")
        
        if response and response.text:
            print_success("Gemini AI connection successful!")
            print(f"  Response: {response.text[:100]}...")
            return True
        else:
            print_error("No response from Gemini AI")
            return False
            
    except Exception as e:
        print_error(f"Gemini AI test failed: {str(e)}")
        return False


def test_data_extraction():
    """Test data extraction agent with Gemini."""
    print_header("STEP 3: TESTING DATA EXTRACTION AGENT")
    
    try:
        from agents.data_extraction import DataExtractionAgent
        
        agent = DataExtractionAgent()
        
        # Test case 1: Diabetes symptoms
        print("\nTest Case 1: Diabetes symptoms")
        symptoms = ["increased thirst", "frequent urination", "fatigue"]
        
        result = agent.extract_and_map(
            symptoms=symptoms,
            age=45,
            gender="male",
            disease="diabetes"
        )
        
        print(f"DEBUG - Result type: {type(result)}")
        print(f"DEBUG - Result: {result if not isinstance(result, dict) or len(str(result)) < 200 else 'dict with keys: ' + str(list(result.keys()))}")
        
        # Result can be either a tuple or a dict
        if isinstance(result, tuple) and len(result) == 2:
            features, confidence = result
            print_success("Data extraction successful")
            print(f"  Extracted features: {len(features)} features")
            print(f"  Confidence: {confidence:.2f}")
        elif isinstance(result, dict):
            # Dict format from agent
            features = result.get('features', {})
            confidence = result.get('extraction_confidence', 0)
            print_success("Data extraction successful")
            print(f"  Extracted features: {len(features)} features")
            print(f"  Confidence: {confidence:.2f}")
            print(f"  Extraction method: {result.get('extraction_method', 'N/A')}")
        else:
            print_error(f"Data extraction returned unexpected format: {type(result)}")
            return False
        
        # Test case 2: Heart disease symptoms
        print("\nTest Case 2: Heart disease symptoms")
        symptoms = ["chest pain", "shortness of breath"]
        
        result = agent.extract_and_map(
            symptoms=symptoms,
            age=55,
            gender="male",
            disease="heart_disease"
        )
        
        if isinstance(result, tuple) and len(result) == 2:
            features, confidence = result
            print_success("Data extraction successful")
            print(f"  Extracted features: {len(features)} features")
            print(f"  Confidence: {confidence:.2f}")
        elif isinstance(result, dict):
            features = result.get('features', {})
            confidence = result.get('extraction_confidence', 0)
            print_success("Data extraction successful")
            print(f"  Extracted features: {len(features)} features")
            print(f"  Confidence: {confidence:.2f}")
            print(f"  Extraction method: {result.get('extraction_method', 'N/A')}")
        else:
            print_error(f"Data extraction returned unexpected format: {type(result)}")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Data extraction test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_ml_prediction():
    """Test ML prediction models."""
    print_header("STEP 4: TESTING ML PREDICTION")
    
    try:
        from prediction.predictor import DiseasePredictor
        
        predictor = DiseasePredictor()
        
        # Test diabetes prediction
        print("\nTest Case: Diabetes prediction")
        features = {
            'glucose': 150,
            'bmi': 32.5,
            'age': 45,
            'blood_pressure': 85,
            'insulin': 120
        }
        
        probability, metadata = predictor.predict('diabetes', features)
        
        if probability is not None:
            print_success("Prediction successful")
            print(f"  Disease: diabetes")
            print(f"  Probability: {probability:.2%}")
            print(f"  Confidence: {metadata.get('confidence', 'N/A')}")
        else:
            print_error("Prediction failed")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"ML prediction test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_explanation_generation():
    """Test explanation generation with Gemini."""
    print_header("STEP 5: TESTING EXPLANATION GENERATION")
    
    try:
        import google.generativeai as genai
        
        api_key = config('GEMINI_API_KEY', default='')
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Test explanation generation
        print("\nGenerating explanation for diabetes risk assessment...")
        
        prompt = """You are an AI assistant helping to explain health risk assessments. 

Please explain this health risk assessment:

Condition assessed: Diabetes
Risk probability: 65.5%
Confidence level: MEDIUM
Symptoms provided: increased thirst, frequent urination, fatigue

Please explain:
1. What this risk assessment means in simple terms
2. Why the confidence level is MEDIUM
3. What factors contributed to this assessment
4. The importance of professional medical consultation

Keep it under 200 words and use simple language. This is NOT a medical diagnosis."""

        response = model.generate_content(prompt)
        
        if response and response.text:
            print_success("Explanation generated successfully")
            print(f"\n{response.text}\n")
            return True
        else:
            print_error("Failed to generate explanation")
            return False
            
    except Exception as e:
        print_error(f"Explanation generation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_complete_pipeline():
    """Test the complete orchestration pipeline."""
    print_header("STEP 6: TESTING COMPLETE PIPELINE")
    
    try:
        from agents.orchestrator import OrchestratorAgent
        
        orchestrator = OrchestratorAgent()
        
        # Test case: Complete pipeline
        print("\nTest Case: Complete diabetes assessment pipeline")
        input_data = {
            "symptoms": ["increased thirst", "frequent urination", "fatigue"],
            "age": 45,
            "gender": "male",
            "additional_info": {
                "weight": 85,
                "height": 175
            }
        }
        
        result = orchestrator.process(input_data)
        
        # Debug: print the actual result structure
        print(f"\nDEBUG - Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        if isinstance(result, dict):
            print(f"DEBUG - Result structure: {json.dumps({k: type(v).__name__ for k, v in result.items()}, indent=2)}")
        
        # Check if result has the expected structure (wrapped in agent response)
        if result and result.get('success') and 'data' in result:
            data = result['data']
            if 'prediction' in data:
                print_success("Pipeline execution successful")
                print(f"\n  User ID: {data.get('user_id', 'N/A')}")
                print(f"  Disease: {data['prediction'].get('disease', 'N/A')}")
                print(f"  Probability: {data['prediction'].get('probability_percent', 0):.2f}%")
                print(f"  Confidence: {data['prediction'].get('confidence', 'N/A')}")
                
                if 'explanation' in data and 'text' in data['explanation']:
                    print(f"\n  Explanation:\n  {data['explanation']['text'][:200]}...")
                
                if 'recommendations' in data and 'items' in data['recommendations']:
                    print(f"\n  Recommendations:")
                    for rec in data['recommendations']['items'][:3]:
                        print(f"    - {rec}")
                
                print(f"\n  Processing Time: {data.get('metadata', {}).get('processing_time_seconds', 0):.2f}s")
                
                return True
            else:
                print_error("Pipeline data missing prediction information")
                return False
        elif result and result.get('success') == False:
            print_error(f"Pipeline failed: {result.get('message', 'Unknown reason')}")
            return False
        else:
            print_error("Pipeline returned unexpected format")
            return False
            
    except Exception as e:
        print_error(f"Pipeline test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("  AI HEALTH INTELLIGENCE SYSTEM - API TEST")
    print("="*80)
    
    results = {
        "API Configuration": False,
        "Gemini AI Connection": False,
        "Data Extraction": False,
        "ML Prediction": False,
        "Explanation Generation": False,
        "Complete Pipeline": False
    }
    
    # Run tests
    results["API Configuration"] = test_api_configuration()
    
    if results["API Configuration"]:
        results["Gemini AI Connection"] = test_gemini_direct()
        
        if results["Gemini AI Connection"]:
            results["Data Extraction"] = test_data_extraction()
            results["ML Prediction"] = test_ml_prediction()
            results["Explanation Generation"] = test_explanation_generation()
            results["Complete Pipeline"] = test_complete_pipeline()
    
    # Print summary
    print_header("TEST SUMMARY")
    
    for test_name, passed in results.items():
        status = "[PASSED]" if passed else "[FAILED]"
        print(f"{test_name:.<50} {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\n{'='*80}")
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    print(f"{'='*80}\n")
    
    if passed_tests == total_tests:
        print("[SUCCESS] All tests passed! Your AI Health Intelligence System is ready to use.")
    elif passed_tests > 0:
        print("[WARNING] Some tests passed. Check the failed tests above for issues.")
    else:
        print("[ERROR] All tests failed. Please check your API configuration.")


if __name__ == "__main__":
    main()
