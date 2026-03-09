"""
Safety tests for dosage prevention.

Tests that agent responses never recommend specific medication dosages
and that dosage filtering works correctly.

Requirements: 17.4 - Prevent specific medication dosages
"""

import pytest
from agents.infrastructure.safety_guardrails import SafetyGuardrails


class TestDosagePrevention:
    """Test suite for dosage prevention safety guardrails."""
    
    @pytest.fixture
    def guardrails(self):
        """Create SafetyGuardrails instance."""
        return SafetyGuardrails()
    
    def test_filters_mg_dosage(self, guardrails):
        """Test that milligram dosage recommendations are filtered."""
        response = "Take 500 mg of metformin daily."
        filtered = guardrails.prevent_dosage_recommendation(response)
        
        assert "500 mg" not in filtered
        assert "consult your doctor for appropriate dosage" in filtered.lower()
    
    def test_filters_mcg_dosage(self, guardrails):
        """Test that microgram dosage recommendations are filtered."""
        response = "Take 25 mcg of levothyroxine once daily."
        filtered = guardrails.prevent_dosage_recommendation(response)
        
        assert "25 mcg" not in filtered
        assert "consult your doctor" in filtered.lower()
    
    def test_filters_ml_dosage(self, guardrails):
        """Test that milliliter dosage recommendations are filtered."""
        response = "Take 10 ml of cough syrup twice daily."
        filtered = guardrails.prevent_dosage_recommendation(response)
        
        assert "10 ml" not in filtered
        assert "appropriate dosage" in filtered.lower()
    
    def test_filters_units_dosage(self, guardrails):
        """Test that unit-based dosage recommendations are filtered."""
        response = "Inject 20 units of insulin before meals."
        filtered = guardrails.prevent_dosage_recommendation(response)
        
        assert "20 units" not in filtered
        assert "consult your doctor" in filtered.lower()
    
    def test_filters_gram_dosage(self, guardrails):
        """Test that gram dosage recommendations are filtered."""
        response = "Take 2 g of amoxicillin per day."
        filtered = guardrails.prevent_dosage_recommendation(response)
        
        assert "2 g" not in filtered
        assert "appropriate dosage" in filtered.lower()
    
    def test_filters_dosage_with_frequency(self, guardrails):
        """Test filtering dosage with frequency (daily, twice, etc.)."""
        dosages = [
            "Take 100 mg daily",
            "Take 50 mg twice per day",
            "Take 200 mg once daily",
            "Take 10 mg per day"
        ]
        
        for dosage in dosages:
            filtered = guardrails.prevent_dosage_recommendation(dosage)
            # Should not contain the specific dosage
            assert not any(d in filtered for d in ["100 mg", "50 mg", "200 mg", "10 mg"])
            assert "consult your doctor" in filtered.lower()
    
    def test_filters_dosage_of_pattern(self, guardrails):
        """Test filtering 'dosage of X mg' pattern."""
        response = "The recommended dosage of 500 mg should be taken with food."
        filtered = guardrails.prevent_dosage_recommendation(response)
        
        assert "dosage of 500 mg" not in filtered
        assert "consult your doctor" in filtered.lower()
    
    def test_filters_prescribe_dosage(self, guardrails):
        """Test filtering 'prescribe X mg' pattern."""
        response = "Your doctor may prescribe 10 mg of the medication."
        filtered = guardrails.prevent_dosage_recommendation(response)
        
        assert "prescribe 10 mg" not in filtered
        assert "appropriate dosage" in filtered.lower()
    
    def test_filters_multiple_dosages(self, guardrails):
        """Test filtering multiple dosage recommendations in one response."""
        response = (
            "Take 500 mg of metformin twice daily and 10 mg of lisinopril once daily. "
            "Also take 20 units of insulin before meals."
        )
        filtered = guardrails.prevent_dosage_recommendation(response)
        
        assert "500 mg" not in filtered
        assert "10 mg" not in filtered
        assert "20 units" not in filtered
        assert filtered.count("consult your doctor") >= 1
    
    def test_preserves_non_dosage_numbers(self, guardrails):
        """Test that non-dosage numbers are preserved."""
        response = (
            "Your blood pressure is 120/80 mmHg. "
            "Your glucose level is 100 mg/dL. "
            "You should aim for 30 minutes of exercise daily."
        )
        filtered = guardrails.prevent_dosage_recommendation(response)
        
        # These should be preserved as they're not dosage recommendations
        assert "120/80" in filtered
        assert "100 mg/dL" in filtered
        assert "30 minutes" in filtered
    
    def test_logs_dosage_filtering(self, guardrails):
        """Test that dosage filtering is logged."""
        guardrails.clear_interventions_log()
        response = "Take 500 mg daily."
        guardrails.prevent_dosage_recommendation(response)
        
        log = guardrails.get_interventions_log()
        assert len(log) > 0
        assert any('dosage' in entry['type'] for entry in log)
    
    def test_validation_detects_dosage_recommendations(self, guardrails):
        """Test that validation detects dosage recommendations."""
        response = "Take 100 mg of aspirin daily for your condition."
        validation = guardrails.validate_response_safety(response)
        
        assert not validation['is_safe']
        assert any('dosage' in issue.lower() for issue in validation['issues'])
    
    def test_validation_passes_without_dosage(self, guardrails):
        """Test that validation passes responses without dosage recommendations."""
        response = (
            "Consult your doctor about appropriate medication and dosage. "
            "Please consult with a qualified healthcare professional. "
            "IMPORTANT MEDICAL DISCLAIMER: This is for educational purposes only."
        )
        validation = guardrails.validate_response_safety(response)
        
        dosage_issues = [i for i in validation['issues'] if 'dosage' in i.lower()]
        assert len(dosage_issues) == 0
    
    def test_apply_all_guardrails_removes_dosage(self, guardrails):
        """Test that apply_all_guardrails removes dosage recommendations."""
        response = "Take 500 mg of metformin twice daily for diabetes management."
        safe_response = guardrails.apply_all_guardrails(response)
        
        assert "500 mg" not in safe_response
        assert "MEDICAL DISCLAIMER" in safe_response
        assert "consult" in safe_response.lower()
    
    def test_case_insensitive_dosage_filtering(self, guardrails):
        """Test that dosage filtering works regardless of case."""
        responses = [
            "Take 100 MG daily",
            "Take 100 Mg daily",
            "Take 100 mg daily",
            "TAKE 100 MG DAILY"
        ]
        
        for response in responses:
            filtered = guardrails.prevent_dosage_recommendation(response)
            assert "100" not in filtered or "consult" in filtered.lower()
    
    def test_filters_various_medication_units(self, guardrails):
        """Test filtering dosages with various medication units."""
        units = ["mg", "mcg", "g", "ml", "units", "unit"]
        
        for unit in units:
            response = f"Take 50 {unit} of medication daily."
            filtered = guardrails.prevent_dosage_recommendation(response)
            assert f"50 {unit}" not in filtered
            assert "consult your doctor" in filtered.lower()
    
    def test_statistics_track_dosage_filtering(self, guardrails):
        """Test that statistics track dosage filtering."""
        guardrails.clear_interventions_log()
        
        responses = [
            "Take 100 mg daily.",
            "Take 50 mcg twice daily.",
            "Inject 20 units before meals."
        ]
        
        for response in responses:
            guardrails.prevent_dosage_recommendation(response)
        
        stats = guardrails.get_statistics()
        assert stats['dosage_filtered'] > 0
    
    def test_empty_response_handling(self, guardrails):
        """Test that empty responses are handled gracefully."""
        response = ""
        filtered = guardrails.prevent_dosage_recommendation(response)
        assert filtered == ""
    
    def test_response_without_dosage_unchanged(self, guardrails):
        """Test that responses without dosage remain unchanged."""
        response = "Consult your doctor about appropriate medication for your condition."
        filtered = guardrails.prevent_dosage_recommendation(response)
        assert filtered == response
    
    def test_filters_dosage_in_context(self, guardrails):
        """Test filtering dosage within larger medical context."""
        response = """
        For managing your blood pressure, your doctor may recommend medication.
        A typical starting dose might be 5 mg daily, adjusted based on response.
        Regular monitoring is important.
        """
        filtered = guardrails.prevent_dosage_recommendation(response)
        
        assert "5 mg daily" not in filtered
        assert "consult your doctor" in filtered.lower()
        assert "Regular monitoring" in filtered  # Non-dosage content preserved


class TestDosagePreventionIntegration:
    """Integration tests for dosage prevention across agent responses."""
    
    @pytest.fixture
    def guardrails(self):
        """Create SafetyGuardrails instance."""
        return SafetyGuardrails()
    
    def test_complete_medication_response_filtering(self, guardrails):
        """Test filtering a complete medication response with dosages."""
        response = """
        Based on your condition, take 500 mg of metformin twice daily with meals.
        Also take 10 mg of lisinopril once daily in the morning.
        Inject 20 units of insulin before each meal.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        # Should not contain specific dosages
        assert "500 mg" not in safe_response
        assert "10 mg" not in safe_response
        assert "20 units" not in safe_response
        
        # Should contain safety elements
        assert "MEDICAL DISCLAIMER" in safe_response
        assert "consult" in safe_response.lower()
    
    def test_medication_discussion_without_dosage(self, guardrails):
        """Test that medication discussions without dosage are preserved."""
        response = """
        Your doctor may prescribe metformin for blood sugar management.
        The dosage will be determined based on your individual needs and response.
        Regular monitoring and follow-up appointments are important.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        # Should preserve the content
        assert "metformin" in safe_response.lower()
        assert "dosage will be determined" in safe_response.lower()
        
        # Should add safety elements
        assert "MEDICAL DISCLAIMER" in safe_response
    
    def test_mixed_dosage_and_diagnosis_filtering(self, guardrails):
        """Test filtering both dosage and diagnosis in same response."""
        response = """
        You have diabetes type 2. Take 1000 mg of metformin daily.
        You are diagnosed with hypertension. Take 5 mg of lisinopril daily.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        # Should filter both diagnosis and dosage
        assert "you have diabetes" not in safe_response.lower()
        assert "1000 mg" not in safe_response
        assert "you are diagnosed with" not in safe_response.lower()
        assert "5 mg" not in safe_response
        
        # Should contain safety elements
        assert "MEDICAL DISCLAIMER" in safe_response
    
    def test_treatment_plan_with_multiple_medications(self, guardrails):
        """Test filtering treatment plan with multiple medication dosages."""
        response = """
        Treatment plan:
        1. Metformin 500 mg twice daily
        2. Lisinopril 10 mg once daily
        3. Atorvastatin 20 mg at bedtime
        4. Aspirin 81 mg daily
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        # Should filter all dosages
        assert "500 mg" not in safe_response
        assert "10 mg" not in safe_response
        assert "20 mg" not in safe_response
        assert "81 mg" not in safe_response
        
        # Should still mention medications in safe way
        assert "metformin" in safe_response.lower() or "consult" in safe_response.lower()
    
    def test_lab_values_preserved_dosages_filtered(self, guardrails):
        """Test that lab values are preserved while dosages are filtered."""
        response = """
        Your glucose is 150 mg/dL and cholesterol is 220 mg/dL.
        Take 500 mg of metformin daily to manage glucose levels.
        Your blood pressure is 140/90 mmHg.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        # Lab values should be preserved
        assert "150 mg/dL" in safe_response
        assert "220 mg/dL" in safe_response
        assert "140/90" in safe_response
        
        # Dosage should be filtered
        assert "500 mg of metformin daily" not in safe_response
        assert "consult your doctor" in safe_response.lower()
