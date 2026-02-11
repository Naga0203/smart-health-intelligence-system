"""
Comprehensive scenario testing for AI Health Intelligence System.
Tests various user input scenarios and edge cases.
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

from agents.orchestrator import OrchestratorAgent
from decouple import config
import logging

logging.basicConfig(level=logging.WARNING)  # Reduce noise


def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def print_test(name):
    print(f"\n[TEST] {name}")


def print_result(success, message):
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} {message}")


def test_scenario(orchestrator, scenario_name, input_data, expected_disease=None):
    """Test a specific scenario."""
    print_test(scenario_name)
    
    try:
        result = orchestrator.process(input_data)
        
        if result and result.get('success'):
            data = result['data']
            disease = data['prediction']['disease']
            probability = data['prediction']['probability_percent']
            confidence = data['prediction']['confidence']
            
            print_result(True, f"Disease: {disease}, Probability: {probability:.1f}%, Confidence: {confidence}")
            
            if expected_disease and disease.lower() != expected_disease.lower():
                print(f"  [NOTE] Expected {expected_disease}, got {disease}")
            
            return True
        else:
            print_result(False, f"Pipeline failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False


def main():
    print("\n" + "="*80)
    print("  AI HEALTH INTELLIGENCE SYSTEM - COMPREHENSIVE SCENARIO TESTING")
    print("="*80)
    print("\nNote: Using mock ML models - real models to be uploaded later")
    
    # Initialize orchestrator
    print("\n[INIT] Initializing orchestrator...")
    orchestrator = OrchestratorAgent()
    print("[OK] Orchestrator initialized")
    
    results = {}
    
    # ========================================================================
    # DIABETES SCENARIOS
    # ========================================================================
    print_header("DIABETES SCENARIOS")
    
    # Scenario 1: Classic diabetes symptoms
    results['diabetes_classic'] = test_scenario(
        orchestrator,
        "Classic Diabetes Symptoms",
        {
            "symptoms": ["increased thirst", "frequent urination", "fatigue", "blurred vision"],
            "age": 45,
            "gender": "male"
        },
        expected_disease="diabetes"
    )
    
    # Scenario 2: Diabetes with weight loss
    results['diabetes_weight_loss'] = test_scenario(
        orchestrator,
        "Diabetes with Weight Loss",
        {
            "symptoms": ["excessive thirst", "weight loss", "always hungry", "tired"],
            "age": 52,
            "gender": "female"
        },
        expected_disease="diabetes"
    )
    
    # Scenario 3: Young person with diabetes symptoms
    results['diabetes_young'] = test_scenario(
        orchestrator,
        "Young Person with Diabetes Symptoms",
        {
            "symptoms": ["thirst", "urination", "fatigue"],
            "age": 25,
            "gender": "male"
        },
        expected_disease="diabetes"
    )
    
    # ========================================================================
    # HEART DISEASE SCENARIOS
    # ========================================================================
    print_header("HEART DISEASE SCENARIOS")
    
    # Scenario 4: Classic heart disease symptoms
    results['heart_classic'] = test_scenario(
        orchestrator,
        "Classic Heart Disease Symptoms",
        {
            "symptoms": ["chest pain", "shortness of breath", "fatigue"],
            "age": 60,
            "gender": "male"
        },
        expected_disease="heart disease"
    )
    
    # Scenario 5: Heart disease with exercise symptoms
    results['heart_exercise'] = test_scenario(
        orchestrator,
        "Heart Disease with Exercise Symptoms",
        {
            "symptoms": ["chest discomfort", "breathing difficulty", "pain during exercise"],
            "age": 55,
            "gender": "female"
        },
        expected_disease="heart disease"
    )
    
    # ========================================================================
    # HYPERTENSION SCENARIOS
    # ========================================================================
    print_header("HYPERTENSION SCENARIOS")
    
    # Scenario 6: Classic hypertension symptoms
    results['hypertension_classic'] = test_scenario(
        orchestrator,
        "Classic Hypertension Symptoms",
        {
            "symptoms": ["headache", "dizziness", "fatigue"],
            "age": 50,
            "gender": "male"
        },
        expected_disease="hypertension"
    )
    
    # Scenario 7: Hypertension with stress
    results['hypertension_stress'] = test_scenario(
        orchestrator,
        "Hypertension with Stress",
        {
            "symptoms": ["headache", "dizziness", "stress", "sleep problems"],
            "age": 48,
            "gender": "female"
        },
        expected_disease="hypertension"
    )
    
    # ========================================================================
    # EDGE CASES
    # ========================================================================
    print_header("EDGE CASES")
    
    # Scenario 8: Minimal symptoms
    results['minimal_symptoms'] = test_scenario(
        orchestrator,
        "Minimal Symptoms",
        {
            "symptoms": ["fatigue"],
            "age": 35,
            "gender": "male"
        }
    )
    
    # Scenario 9: Multiple disease indicators
    results['mixed_symptoms'] = test_scenario(
        orchestrator,
        "Mixed Symptoms (Multiple Diseases)",
        {
            "symptoms": ["chest pain", "thirst", "headache", "fatigue"],
            "age": 55,
            "gender": "male"
        }
    )
    
    # Scenario 10: Elderly patient
    results['elderly_patient'] = test_scenario(
        orchestrator,
        "Elderly Patient",
        {
            "symptoms": ["fatigue", "weakness", "dizziness"],
            "age": 75,
            "gender": "female"
        }
    )
    
    # Scenario 11: Young patient with vague symptoms
    results['young_vague'] = test_scenario(
        orchestrator,
        "Young Patient with Vague Symptoms",
        {
            "symptoms": ["tired", "headache"],
            "age": 22,
            "gender": "female"
        }
    )
    
    # ========================================================================
    # ADDITIONAL INFO SCENARIOS
    # ========================================================================
    print_header("SCENARIOS WITH ADDITIONAL INFO")
    
    # Scenario 12: With BMI and weight info
    results['with_bmi'] = test_scenario(
        orchestrator,
        "Diabetes with BMI Info",
        {
            "symptoms": ["thirst", "urination", "fatigue"],
            "age": 45,
            "gender": "male",
            "additional_info": {
                "weight": 95,
                "height": 175,
                "bmi": 31.0
            }
        },
        expected_disease="diabetes"
    )
    
    # Scenario 13: With family history
    results['with_family_history'] = test_scenario(
        orchestrator,
        "Heart Disease with Family History",
        {
            "symptoms": ["chest pain", "shortness of breath"],
            "age": 50,
            "gender": "male",
            "additional_info": {
                "family_history": "heart disease",
                "smoking": True
            }
        },
        expected_disease="heart disease"
    )
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_header("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n" + "="*80)
    
    if passed_tests == total_tests:
        print("[SUCCESS] All scenario tests passed!")
    elif passed_tests > total_tests * 0.8:
        print("[GOOD] Most scenario tests passed!")
    else:
        print("[WARNING] Some scenario tests failed. Review above for details.")
    
    print("="*80 + "\n")
    
    # Detailed results
    print("\nDetailed Results:")
    for scenario, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {scenario}")


if __name__ == "__main__":
    main()
