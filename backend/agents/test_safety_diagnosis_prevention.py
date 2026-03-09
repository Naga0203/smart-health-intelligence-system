"""
Safety tests for diagnosis prevention.

Tests that agent responses never contain specific diagnoses
and that diagnosis filtering works correctly.

Requirements: 17.1 - Prevent specific medical diagnoses
"""

import pytest
from agents.infrastructure.safety_guardrails import SafetyGuardrails


class TestDiagnosisPrevention:
    """Test suite for diagnosis prevention safety guardrails."""
    
    @pytest.fixture
    def guardrails(self):
        """Create SafetyGuardrails instance."""
        return SafetyGuardrails()
    
    def test_filters_you_have_diagnosis(self, guardrails):
        """Test that 'you have' diagnosis statements are filtered."""
        response = "Based on your results, you have diabetes type 2."
        filtered = guardrails.prevent_diagnosis(response)
        
        assert "you have" not in filtered.lower()
        assert "your results" in filtered.lower()
        assert "diabetes" in filtered.lower()
    
    def test_filters_diagnosed_with_statement(self, guardrails):
        """Test that 'diagnosed with' statements are filtered."""
        response = "You are diagnosed with hypertension."
        filtered = guardrails.prevent_diagnosis(response)
        
        assert "diagnosed with" not in filtered.lower()
        assert "your results suggest" in filtered.lower()
    
    def test_filters_you_definitely_have(self, guardrails):
        """Test that 'you definitely have' statements are filtered."""
        response = "You definitely have a thyroid disorder."
        filtered = guardrails.prevent_diagnosis(response)
        
        assert "definitely have" not in filtered.lower()
        assert "may suggest" in filtered.lower() or "may indicate" in filtered.lower()
    
    def test_filters_this_is_diagnosis(self, guardrails):
        """Test that 'this is' diagnosis statements are filtered."""
        response = "This is clearly a case of rheumatoid arthritis."
        filtered = guardrails.prevent_diagnosis(response)
        
        assert "this is" not in filtered.lower() or "may be related to" in filtered.lower()
    
    def test_filters_youve_got_diagnosis(self, guardrails):
        """Test that 'you've got' diagnosis statements are filtered."""
        response = "You've got high cholesterol and need treatment."
        filtered = guardrails.prevent_diagnosis(response)
        
        assert "you've got" not in filtered.lower() or "may indicate" in filtered.lower()
    
    def test_filters_suffering_from_statement(self, guardrails):
        """Test that 'suffering from' statements are filtered."""
        response = "You are suffering from chronic kidney disease."
        filtered = guardrails.prevent_diagnosis(response)
        
        assert "suffering from" not in filtered.lower()
    
    def test_filters_multiple_diagnosis_statements(self, guardrails):
        """Test filtering multiple diagnosis statements in one response."""
        response = (
            "You have diabetes and you are diagnosed with hypertension. "
            "This is a serious condition that requires immediate attention."
        )
        filtered = guardrails.prevent_diagnosis(response)
        
        assert "you have" not in filtered.lower() or "may indicate" in filtered.lower()
        assert "diagnosed with" not in filtered.lower()
    
    def test_preserves_non_diagnosis_language(self, guardrails):
        """Test that non-diagnosis language is preserved."""
        response = (
            "Your lab results show elevated glucose levels. "
            "This may indicate a need for further testing. "
            "Please consult your doctor for proper evaluation."
        )
        filtered = guardrails.prevent_diagnosis(response)
        
        assert "lab results show" in filtered.lower()
        assert "may indicate" in filtered.lower()
        assert "consult your doctor" in filtered.lower()
    
    def test_logs_diagnosis_filtering(self, guardrails):
        """Test that diagnosis filtering is logged."""
        guardrails.clear_interventions_log()
        response = "You have diabetes."
        guardrails.prevent_diagnosis(response)
        
        log = guardrails.get_interventions_log()
        assert len(log) > 0
        assert any('diagnosis' in entry['type'] for entry in log)
    
    def test_validation_detects_diagnosis_statements(self, guardrails):
        """Test that validation detects diagnosis statements."""
        response = "You have cancer and need treatment immediately."
        validation = guardrails.validate_response_safety(response)
        
        assert not validation['is_safe']
        assert any('diagnosis' in issue.lower() for issue in validation['issues'])
    
    def test_validation_passes_safe_language(self, guardrails):
        """Test that validation passes responses with safe language."""
        response = (
            "Your results may suggest consulting a healthcare professional. "
            "Please consult with a qualified healthcare professional for proper evaluation. "
            "IMPORTANT MEDICAL DISCLAIMER: This is for educational purposes only."
        )
        validation = guardrails.validate_response_safety(response)
        
        # Should have minimal issues (might flag missing emergency notice but that's ok)
        diagnosis_issues = [i for i in validation['issues'] if 'diagnosis' in i.lower()]
        assert len(diagnosis_issues) == 0
    
    def test_apply_all_guardrails_removes_diagnosis(self, guardrails):
        """Test that apply_all_guardrails removes diagnosis statements."""
        response = "You have diabetes type 2 and need medication."
        safe_response = guardrails.apply_all_guardrails(response)
        
        assert "you have" not in safe_response.lower() or "may indicate" in safe_response.lower()
        assert "MEDICAL DISCLAIMER" in safe_response
    
    def test_filters_confirmed_diagnosis(self, guardrails):
        """Test that 'confirmed diagnosis' statements are filtered."""
        response = "The confirmed diagnosis of lupus requires treatment."
        filtered = guardrails.prevent_diagnosis(response)
        
        assert "confirmed diagnosis" not in filtered.lower()
    
    def test_case_insensitive_filtering(self, guardrails):
        """Test that filtering works regardless of case."""
        responses = [
            "You Have Diabetes",
            "YOU HAVE DIABETES",
            "you have diabetes",
            "You HaVe DiAbEtEs"
        ]
        
        for response in responses:
            filtered = guardrails.prevent_diagnosis(response)
            assert "you have" not in filtered.lower() or "may" in filtered.lower()
    
    def test_filters_diagnosis_with_medical_terms(self, guardrails):
        """Test filtering diagnosis statements with various medical terms."""
        medical_terms = [
            "diabetes", "cancer", "disease", "condition", 
            "disorder", "syndrome"
        ]
        
        for term in medical_terms:
            response = f"You have {term} and need treatment."
            filtered = guardrails.prevent_diagnosis(response)
            assert "you have" not in filtered.lower() or "may" in filtered.lower()
    
    def test_statistics_track_diagnosis_filtering(self, guardrails):
        """Test that statistics track diagnosis filtering."""
        guardrails.clear_interventions_log()
        
        responses = [
            "You have diabetes.",
            "You are diagnosed with hypertension.",
            "You definitely have cancer."
        ]
        
        for response in responses:
            guardrails.prevent_diagnosis(response)
        
        stats = guardrails.get_statistics()
        assert stats['diagnosis_filtered'] > 0
    
    def test_empty_response_handling(self, guardrails):
        """Test that empty responses are handled gracefully."""
        response = ""
        filtered = guardrails.prevent_diagnosis(response)
        assert filtered == ""
    
    def test_response_without_diagnosis_unchanged(self, guardrails):
        """Test that responses without diagnosis statements remain unchanged."""
        response = "Your lab results are available. Please review them with your doctor."
        filtered = guardrails.prevent_diagnosis(response)
        assert filtered == response
    
    def test_partial_diagnosis_phrases_handled(self, guardrails):
        """Test that partial diagnosis phrases are handled correctly."""
        # Should not filter "have" when not part of diagnosis statement
        response = "You have received your test results."
        filtered = guardrails.prevent_diagnosis(response)
        # This should remain unchanged as it's not a diagnosis
        assert "received your test results" in filtered.lower()


class TestDiagnosisPreventionIntegration:
    """Integration tests for diagnosis prevention across agent responses."""
    
    @pytest.fixture
    def guardrails(self):
        """Create SafetyGuardrails instance."""
        return SafetyGuardrails()
    
    def test_complete_agent_response_filtering(self, guardrails):
        """Test filtering a complete agent response with diagnosis."""
        response = """
        Based on your lab results, you have type 2 diabetes. Your glucose levels 
        are elevated at 180 mg/dL. You are diagnosed with prediabetes and should 
        start treatment immediately. This is a serious condition.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        # Should not contain diagnosis statements
        assert "you have type 2 diabetes" not in safe_response.lower()
        assert "you are diagnosed with" not in safe_response.lower()
        
        # Should contain safety elements
        assert "MEDICAL DISCLAIMER" in safe_response
        assert "consult" in safe_response.lower()
    
    def test_treatment_recommendation_without_diagnosis(self, guardrails):
        """Test that treatment recommendations without diagnosis are preserved."""
        response = """
        Your results suggest elevated glucose levels. Consider discussing with 
        your healthcare provider about lifestyle modifications including diet 
        and exercise. Further testing may be recommended.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        # Should preserve the content
        assert "elevated glucose levels" in safe_response.lower()
        assert "lifestyle modifications" in safe_response.lower()
        
        # Should add safety elements
        assert "MEDICAL DISCLAIMER" in safe_response
    
    def test_multiple_conditions_mentioned(self, guardrails):
        """Test filtering when multiple conditions are mentioned."""
        response = """
        You have diabetes, hypertension, and high cholesterol. You are diagnosed 
        with metabolic syndrome. This is a serious combination of conditions.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        # Should filter all diagnosis statements
        assert "you have diabetes" not in safe_response.lower()
        assert "you are diagnosed with" not in safe_response.lower()
        
        # Should still mention the conditions in safe language
        assert "diabetes" in safe_response.lower()
        assert "hypertension" in safe_response.lower()
