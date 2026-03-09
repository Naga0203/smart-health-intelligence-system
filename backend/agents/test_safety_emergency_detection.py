"""
Safety tests for emergency detection.

Tests that emergency indicators are detected correctly
and that escalation for emergencies works properly.

Requirements: 17.3 - Detect emergency indicators and escalate
"""

import pytest
from agents.infrastructure.safety_guardrails import SafetyGuardrails


class TestEmergencyDetection:
    """Test suite for emergency detection safety guardrails."""
    
    @pytest.fixture
    def guardrails(self):
        """Create SafetyGuardrails instance."""
        return SafetyGuardrails()
    
    def test_detects_chest_pain(self, guardrails):
        """Test that chest pain is detected as emergency."""
        text = "Patient is experiencing severe chest pain."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_difficulty_breathing(self, guardrails):
        """Test that difficulty breathing is detected as emergency."""
        text = "I'm having difficulty breathing and feel short of breath."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_severe_bleeding(self, guardrails):
        """Test that severe bleeding is detected as emergency."""
        text = "There is severe bleeding that won't stop."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_loss_of_consciousness(self, guardrails):
        """Test that loss of consciousness is detected as emergency."""
        text = "Patient experienced loss of consciousness earlier today."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_stroke_symptoms(self, guardrails):
        """Test that stroke symptoms are detected as emergency."""
        text = "Experiencing stroke symptoms including facial drooping."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_heart_attack(self, guardrails):
        """Test that heart attack is detected as emergency."""
        text = "Symptoms suggest possible heart attack."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_severe_headache(self, guardrails):
        """Test that severe headache is detected as emergency."""
        text = "Patient has severe headache unlike any before."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_sudden_weakness(self, guardrails):
        """Test that sudden weakness is detected as emergency."""
        text = "Experiencing sudden weakness on one side of body."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_slurred_speech(self, guardrails):
        """Test that slurred speech is detected as emergency."""
        text = "Patient has slurred speech and confusion."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_severe_abdominal_pain(self, guardrails):
        """Test that severe abdominal pain is detected as emergency."""
        text = "Severe abdominal pain that started suddenly."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_severe_allergic_reaction(self, guardrails):
        """Test that severe allergic reaction is detected as emergency."""
        text = "Having severe allergic reaction with swelling."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_seizure(self, guardrails):
        """Test that seizure is detected as emergency."""
        text = "Patient had a seizure lasting several minutes."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_poisoning(self, guardrails):
        """Test that poisoning is detected as emergency."""
        text = "Suspected poisoning from unknown substance."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_overdose(self, guardrails):
        """Test that overdose is detected as emergency."""
        text = "Possible medication overdose occurred."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_suicide_mention(self, guardrails):
        """Test that suicide mention is detected as emergency."""
        text = "Patient mentioned thoughts of suicide."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_self_harm(self, guardrails):
        """Test that self-harm is detected as emergency."""
        text = "Patient engaged in self-harm behavior."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_choking(self, guardrails):
        """Test that choking is detected as emergency."""
        text = "Person is choking and cannot breathe."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_severe_burn(self, guardrails):
        """Test that severe burn is detected as emergency."""
        text = "Patient has severe burn covering large area."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_head_injury(self, guardrails):
        """Test that head injury is detected as emergency."""
        text = "Sustained head injury with loss of consciousness."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_detects_spinal_injury(self, guardrails):
        """Test that spinal injury is detected as emergency."""
        text = "Possible spinal injury from fall."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_case_insensitive_detection(self, guardrails):
        """Test that emergency detection is case insensitive."""
        texts = [
            "CHEST PAIN",
            "Chest Pain",
            "chest pain",
            "ChEsT pAiN"
        ]
        
        for text in texts:
            is_emergency = guardrails.check_emergency_indicators(text)
            assert is_emergency is True
    
    def test_detects_emergency_in_context(self, guardrails):
        """Test that emergency keywords are detected within larger text."""
        text = """
        Patient came in today complaining of various symptoms.
        Most concerning is the severe chest pain that started this morning.
        Also reports some fatigue and mild nausea.
        """
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True
    
    def test_no_false_positive_for_normal_symptoms(self, guardrails):
        """Test that normal symptoms don't trigger emergency detection."""
        texts = [
            "Patient has mild headache.",
            "Experiencing some fatigue.",
            "Minor bruising on arm.",
            "Slight cough for a few days.",
            "Mild stomach discomfort."
        ]
        
        for text in texts:
            is_emergency = guardrails.check_emergency_indicators(text)
            assert is_emergency is False
    
    def test_logs_emergency_detection(self, guardrails):
        """Test that emergency detection is logged."""
        guardrails.clear_interventions_log()
        text = "Patient has severe chest pain."
        guardrails.check_emergency_indicators(text)
        
        log = guardrails.get_interventions_log()
        assert len(log) > 0
        assert any('emergency' in entry['type'] for entry in log)
    
    def test_validation_flags_emergency_without_notice(self, guardrails):
        """Test that validation flags emergency indicators without emergency notice."""
        response = "You are experiencing severe chest pain. Please rest."
        validation = guardrails.validate_response_safety(response)
        
        assert validation['is_emergency']
        assert any('emergency' in issue.lower() for issue in validation['issues'])
    
    def test_validation_passes_emergency_with_notice(self, guardrails):
        """Test that validation passes when emergency notice is present."""
        response = """
        Severe chest pain detected.
        ⚠️ EMERGENCY NOTICE: Please seek immediate medical attention by calling 911.
        IMPORTANT MEDICAL DISCLAIMER: This is for educational purposes only.
        """
        validation = guardrails.validate_response_safety(response)
        
        assert validation['is_emergency']
        # Should not flag as issue if emergency notice is present
        emergency_issues = [i for i in validation['issues'] if 'emergency' in i.lower() and 'no emergency notice' in i.lower()]
        assert len(emergency_issues) == 0
    
    def test_statistics_track_emergency_detections(self, guardrails):
        """Test that statistics track emergency detections."""
        guardrails.clear_interventions_log()
        
        texts = [
            "Chest pain",
            "Difficulty breathing",
            "Severe bleeding"
        ]
        
        for text in texts:
            guardrails.check_emergency_indicators(text)
        
        stats = guardrails.get_statistics()
        assert stats['emergency_detections'] >= 3
    
    def test_empty_text_no_emergency(self, guardrails):
        """Test that empty text doesn't trigger emergency detection."""
        text = ""
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is False
    
    def test_multiple_emergency_indicators(self, guardrails):
        """Test detection when multiple emergency indicators present."""
        text = "Patient has chest pain, difficulty breathing, and severe headache."
        is_emergency = guardrails.check_emergency_indicators(text)
        
        assert is_emergency is True


class TestEmergencyEscalation:
    """Test suite for emergency escalation behavior."""
    
    @pytest.fixture
    def guardrails(self):
        """Create SafetyGuardrails instance."""
        return SafetyGuardrails()
    
    def test_emergency_response_includes_emergency_notice(self, guardrails):
        """Test that emergency responses include emergency notice."""
        response = "You are experiencing severe chest pain."
        safe_response = guardrails.apply_all_guardrails(response)
        
        assert "EMERGENCY NOTICE" in safe_response
        assert "immediate medical attention" in safe_response.lower()
    
    def test_emergency_notice_mentions_911(self, guardrails):
        """Test that emergency notice mentions calling 911."""
        response = "Severe symptoms detected."
        safe_response = guardrails.apply_all_guardrails(response)
        
        if guardrails.check_emergency_indicators(response):
            assert "911" in safe_response or "emergency services" in safe_response.lower()
    
    def test_emergency_notice_recommends_emergency_room(self, guardrails):
        """Test that emergency notice recommends emergency room."""
        response = "Patient has difficulty breathing."
        safe_response = guardrails.apply_all_guardrails(response)
        
        assert "emergency room" in safe_response.lower() or "emergency" in safe_response.lower()
    
    def test_emergency_notice_is_prominent(self, guardrails):
        """Test that emergency notice is prominently formatted."""
        response = "Chest pain detected."
        safe_response = guardrails.apply_all_guardrails(response)
        
        # Should have warning symbol or prominent formatting
        assert "⚠️" in safe_response or "WARNING" in safe_response or "EMERGENCY" in safe_response
    
    def test_emergency_and_medical_disclaimers_both_present(self, guardrails):
        """Test that both emergency and medical disclaimers are present."""
        response = "Severe chest pain and difficulty breathing."
        safe_response = guardrails.apply_all_guardrails(response)
        
        assert "EMERGENCY NOTICE" in safe_response
        assert "MEDICAL DISCLAIMER" in safe_response
    
    def test_non_emergency_no_emergency_notice(self, guardrails):
        """Test that non-emergency responses don't get emergency notice."""
        response = "Your lab results show normal glucose levels."
        safe_response = guardrails.apply_all_guardrails(response)
        
        assert "EMERGENCY NOTICE" not in safe_response
        # But should still have medical disclaimer
        assert "MEDICAL DISCLAIMER" in safe_response
    
    def test_emergency_escalation_logged(self, guardrails):
        """Test that emergency escalation is logged."""
        guardrails.clear_interventions_log()
        response = "Severe chest pain."
        guardrails.apply_all_guardrails(response)
        
        log = guardrails.get_interventions_log()
        emergency_logs = [e for e in log if 'emergency' in e['type']]
        assert len(emergency_logs) > 0


class TestEmergencyDetectionIntegration:
    """Integration tests for emergency detection across complete responses."""
    
    @pytest.fixture
    def guardrails(self):
        """Create SafetyGuardrails instance."""
        return SafetyGuardrails()
    
    def test_complete_emergency_response(self, guardrails):
        """Test complete emergency response with all safety elements."""
        response = """
        Based on your symptoms of severe chest pain and difficulty breathing,
        these are serious indicators that require immediate evaluation.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        # Should have emergency notice
        assert "EMERGENCY NOTICE" in safe_response
        assert "immediate medical attention" in safe_response.lower()
        assert "911" in safe_response or "emergency" in safe_response.lower()
        
        # Should have medical disclaimer
        assert "MEDICAL DISCLAIMER" in safe_response
        
        # Should have consultation recommendation
        assert "consult" in safe_response.lower() or "healthcare professional" in safe_response.lower()
    
    def test_mixed_emergency_and_normal_symptoms(self, guardrails):
        """Test response with both emergency and normal symptoms."""
        response = """
        Your symptoms include:
        - Severe chest pain (concerning)
        - Mild fatigue (common)
        - Normal blood pressure
        
        The chest pain requires immediate attention.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        # Should trigger emergency notice due to chest pain
        assert "EMERGENCY NOTICE" in safe_response
    
    def test_emergency_with_lab_results(self, guardrails):
        """Test emergency detection with lab results context."""
        response = """
        Your lab results show:
        - Troponin: Elevated (concerning)
        - ECG: Abnormal
        
        Combined with your severe chest pain, these findings are serious.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        assert "EMERGENCY NOTICE" in safe_response
        assert "MEDICAL DISCLAIMER" in safe_response
    
    def test_potential_stroke_response(self, guardrails):
        """Test response for potential stroke symptoms."""
        response = """
        Your symptoms of sudden weakness, slurred speech, and facial drooping
        are concerning for possible stroke. Time is critical.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        # Should detect multiple emergency indicators
        assert "EMERGENCY NOTICE" in safe_response
        assert "immediate" in safe_response.lower()
    
    def test_mental_health_emergency(self, guardrails):
        """Test response for mental health emergency."""
        response = """
        Your mention of thoughts of self-harm is very concerning.
        Support and professional help are available.
        """
        
        safe_response = guardrails.apply_all_guardrails(response)
        
        assert "EMERGENCY NOTICE" in safe_response
        assert "immediate" in safe_response.lower()
