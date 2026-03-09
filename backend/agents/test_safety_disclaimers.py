"""
Safety tests for medical disclaimers.

Tests that all medical information includes appropriate disclaimers
and that disclaimer content is correct.

Requirements: 17.2 - Add medical disclaimers to all responses
"""

import pytest
from agents.infrastructure.safety_guardrails import SafetyGuardrails


class TestDisclaimers:
    """Test suite for medical disclaimer safety guardrails."""
    
    @pytest.fixture
    def guardrails(self):
        """Create SafetyGuardrails instance."""
        return SafetyGuardrails()
    
    def test_adds_medical_disclaimer(self, guardrails):
        """Test that medical disclaimer is added to responses."""
        response = "Your lab results show elevated glucose levels."
        with_disclaimer = guardrails.add_medical_disclaimer(response)
        
        assert "MEDICAL DISCLAIMER" in with_disclaimer
        assert "educational purposes only" in with_disclaimer.lower()
        assert "does not constitute medical advice" in with_disclaimer.lower()
    
    def test_disclaimer_includes_consultation_recommendation(self, guardrails):
        """Test that disclaimer recommends consulting healthcare professional."""
        response = "Your results suggest further evaluation."
        with_disclaimer = guardrails.add_medical_disclaimer(response)
        
        assert "consult" in with_disclaimer.lower()
        assert "healthcare professional" in with_disclaimer.lower()
    
    def test_disclaimer_mentions_no_diagnosis(self, guardrails):
        """Test that disclaimer mentions it's not medical advice or diagnosis."""
        response = "Your symptoms may indicate various conditions."
        with_disclaimer = guardrails.add_medical_disclaimer(response)
        
        assert "does not constitute medical advice" in with_disclaimer.lower()
        assert "diagnosis" in with_disclaimer.lower()
        assert "treatment" in with_disclaimer.lower()
    
    def test_does_not_add_duplicate_disclaimer(self, guardrails):
        """Test that duplicate disclaimers are not added."""
        response = "Your results are ready. IMPORTANT MEDICAL DISCLAIMER: This is educational."
        with_disclaimer = guardrails.add_medical_disclaimer(response)
        
        # Should only have one disclaimer
        assert with_disclaimer.count("MEDICAL DISCLAIMER") == 1
    
    def test_adds_emergency_disclaimer_when_needed(self, guardrails):
        """Test that emergency disclaimer is added for emergency situations."""
        response = "You are experiencing chest pain."
        with_disclaimer = guardrails.add_medical_disclaimer(response, is_emergency=True)
        
        assert "EMERGENCY NOTICE" in with_disclaimer
        assert "seek immediate medical attention" in with_disclaimer.lower()
        assert "911" in with_disclaimer or "emergency" in with_disclaimer.lower()
    
    def test_emergency_disclaimer_includes_medical_disclaimer(self, guardrails):
        """Test that emergency responses include both disclaimers."""
        response = "Severe symptoms detected."
        with_disclaimer = guardrails.add_medical_disclaimer(response, is_emergency=True)
        
        assert "EMERGENCY NOTICE" in with_disclaimer
        assert "MEDICAL DISCLAIMER" in with_disclaimer
    
    def test_disclaimer_logs_intervention(self, guardrails):
        """Test that adding disclaimer is logged."""
        guardrails.clear_interventions_log()
        response = "Your results are available."
        guardrails.add_medical_disclaimer(response)
        
        log = guardrails.get_interventions_log()
        assert len(log) > 0
        assert any('disclaimer' in entry['type'] for entry in log)
    
    def test_validation_detects_missing_disclaimer(self, guardrails):
        """Test that validation detects missing disclaimer."""
        response = "Your glucose levels are elevated. Consult your doctor."
        validation = guardrails.validate_response_safety(response)
        
        # Should flag missing disclaimer
        assert any('disclaimer' in issue.lower() for issue in validation['issues'])
    
    def test_validation_passes_with_disclaimer(self, guardrails):
        """Test that validation passes when disclaimer is present."""
        response = (
            "Your results suggest consulting a healthcare professional. "
            "Please consult with a qualified healthcare professional. "
            "IMPORTANT MEDICAL DISCLAIMER: This information is for educational purposes only."
        )
        validation = guardrails.validate_response_safety(response)
        
        assert validation['has_disclaimer']
    
    def test_apply_all_guardrails_adds_disclaimer(self, guardrails):
        """Test that apply_all_guardrails adds disclaimer."""
        response = "Your lab results show normal values."
        safe_response = guardrails.apply_all_guardrails(response)
        
        assert "MEDICAL DISCLAIMER" in safe_response
    
    def test_disclaimer_format_is_prominent(self, guardrails):
        """Test that disclaimer is formatted prominently."""
        response = "Your results are ready."
        with_disclaimer = guardrails.add_medical_disclaimer(response)
        
        # Should have bold/prominent formatting
        assert "**" in with_disclaimer or "IMPORTANT" in with_disclaimer
    
    def test_emergency_disclaimer_format_is_prominent(self, guardrails):
        """Test that emergency disclaimer is formatted prominently."""
        response = "Severe symptoms."
        with_disclaimer = guardrails.add_medical_disclaimer(response, is_emergency=True)
        
        # Should have warning symbol and prominent formatting
        assert "⚠️" in with_disclaimer or "WARNING" in with_disclaimer or "EMERGENCY" in with_disclaimer
    
    def test_disclaimer_at_end_of_response(self, guardrails):
        """Test that disclaimer is added at the end of response."""
        response = "Your lab results show elevated glucose levels."
        with_disclaimer = guardrails.add_medical_disclaimer(response)
        
        # Disclaimer should be at the end
        assert with_disclaimer.endswith("treatment recommendations.")
    
    def test_statistics_track_disclaimer_additions(self, guardrails):
        """Test that statistics track disclaimer additions."""
        guardrails.clear_interventions_log()
        
        responses = [
            "Result 1",
            "Result 2",
            "Result 3"
        ]
        
        for response in responses:
            guardrails.add_medical_disclaimer(response)
        
        stats = guardrails.get_statistics()
        assert stats['disclaimers_added'] >= 3
    
    def test_empty_response_gets_disclaimer(self, guardrails):
        """Test that even empty responses get disclaimer when processed."""
        response = ""
        with_disclaimer = guardrails.add_medical_disclaimer(response)
        
        assert "MEDICAL DISCLAIMER" in with_disclaimer
    
    def test_disclaimer_content_completeness(self, guardrails):
        """Test that disclaimer contains all required elements."""
        response = "Your results."
        with_disclaimer = guardrails.add_medical_disclaimer(response)
        
        required_elements = [
            "educational purposes",
            "does not constitute",
            "medical advice",
            "diagnosis",
            "treatment",
            "consult",
            "healthcare professional",
            "qualified"
        ]
        
        disclaimer_lower = with_disclaimer.lower()
        for element in required_elements:
            assert element in disclaimer_lower, f"Missing required element: {element}"
    
    def test_emergency_disclaimer_content_completeness(self, guardrails):
        """Test that emergency disclaimer contains all required elements."""
        response = "Chest pain detected."
        with_disclaimer = guardrails.add_medical_disclaimer(response, is_emergency=True)
        
        emergency_elements = [
            "emergency",
            "immediate",
            "medical attention",
            "911"
        ]
        
        disclaimer_lower = with_disclaimer.lower()
        emergency_found = any(element in disclaimer_lower for element in emergency_elements)
        assert emergency_found, "Missing emergency elements"


class TestDisclaimerIntegration:
    """Integration tests for disclaimers across complete agent responses."""
    
    @pytest.fixture
    def guardrails(self):
        """Create SafetyGuardrails instance."""
        return SafetyGuardrails()
    
    def test_complete_health_assessment_has_disclaimer(self, guardrails):
        """Test that complete health assessment includes disclaimer."""
        response = """
        Based on your lab results:
        - Glucose: 150 mg/dL (elevated)
        - Cholesterol: 220 mg/dL (high)
        - Blood pressure: 140/90 mmHg (elevated)
        
        Consider discussing these results with your healthcare provider.
        Lifestyle modifications may be beneficial.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        assert "MEDICAL DISCLAIMER" in safe_response
        assert "educational purposes" in safe_response.lower()
        assert "consult" in safe_response.lower()
    
    def test_treatment_information_has_disclaimer(self, guardrails):
        """Test that treatment information includes disclaimer."""
        response = """
        Treatment options for hypertension may include:
        - Lifestyle modifications (diet, exercise)
        - Stress management
        - Regular monitoring
        
        Your doctor will determine the best approach for your situation.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        assert "MEDICAL DISCLAIMER" in safe_response
        assert "does not constitute medical advice" in safe_response.lower()
    
    def test_emergency_response_has_both_disclaimers(self, guardrails):
        """Test that emergency responses have both emergency and medical disclaimers."""
        response = """
        Your symptoms include severe chest pain and difficulty breathing.
        These are serious symptoms that require immediate evaluation.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        assert "EMERGENCY NOTICE" in safe_response
        assert "MEDICAL DISCLAIMER" in safe_response
        assert "immediate medical attention" in safe_response.lower()
        assert "911" in safe_response or "emergency" in safe_response.lower()
    
    def test_medication_information_has_disclaimer(self, guardrails):
        """Test that medication information includes disclaimer."""
        response = """
        Metformin is commonly used for blood sugar management.
        Your doctor will determine if this medication is appropriate for you
        and prescribe the correct dosage based on your individual needs.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        assert "MEDICAL DISCLAIMER" in safe_response
        assert "consult" in safe_response.lower() or "healthcare professional" in safe_response.lower()
    
    def test_lifestyle_recommendations_have_disclaimer(self, guardrails):
        """Test that lifestyle recommendations include disclaimer."""
        response = """
        Lifestyle recommendations for managing blood pressure:
        - Reduce sodium intake
        - Increase physical activity
        - Maintain healthy weight
        - Manage stress
        - Limit alcohol consumption
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        assert "MEDICAL DISCLAIMER" in safe_response
    
    def test_lab_result_explanation_has_disclaimer(self, guardrails):
        """Test that lab result explanations include disclaimer."""
        response = """
        Your HbA1c of 7.5% indicates your average blood sugar over the past 3 months.
        This value is above the target range for most people.
        Discuss these results with your healthcare provider for proper interpretation
        and management recommendations.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        assert "MEDICAL DISCLAIMER" in safe_response
        assert "educational purposes" in safe_response.lower()
    
    def test_multiple_topics_single_disclaimer(self, guardrails):
        """Test that multiple topics in one response get single disclaimer."""
        response = """
        Your results show:
        1. Elevated glucose levels
        2. High cholesterol
        3. Elevated blood pressure
        
        Each of these requires discussion with your healthcare provider.
        Lifestyle modifications and monitoring are important.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        # Should have disclaimer but not duplicated
        assert safe_response.count("MEDICAL DISCLAIMER") == 1
    
    def test_short_response_gets_disclaimer(self, guardrails):
        """Test that even short responses get disclaimer."""
        response = "Your results are ready for review."
        safe_response = guardrails.apply_all_guardrails(response)
        
        assert "MEDICAL DISCLAIMER" in safe_response
    
    def test_disclaimer_does_not_disrupt_formatting(self, guardrails):
        """Test that disclaimer addition preserves response formatting."""
        response = """
        **Lab Results Summary**
        
        - Test 1: Normal
        - Test 2: Elevated
        - Test 3: Normal
        
        Please review with your doctor.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        # Original formatting should be preserved
        assert "**Lab Results Summary**" in safe_response
        assert "- Test 1: Normal" in safe_response
        
        # Disclaimer should be added
        assert "MEDICAL DISCLAIMER" in safe_response
