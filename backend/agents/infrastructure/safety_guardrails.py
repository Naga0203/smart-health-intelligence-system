"""
Safety Guardrails for medical information.

Ensures all agent responses follow medical safety guidelines,
including preventing diagnoses, adding disclaimers, and detecting emergencies.

Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.8
"""

import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger('health_ai.agents.infrastructure')


class SafetyGuardrails:
    """
    Safety guardrails for medical information.
    
    Requirements:
    - 17.1: Prevent specific medical diagnoses
    - 17.2: Add medical disclaimers
    - 17.3: Detect emergency indicators
    - 17.4: Prevent specific medication dosages
    - 17.5: Recommend professional consultation
    - 17.8: Log safety interventions
    """
    
    # Emergency keywords that require immediate medical attention
    EMERGENCY_KEYWORDS = [
        'chest pain', 'difficulty breathing', 'severe bleeding',
        'loss of consciousness', 'stroke symptoms', 'heart attack',
        'severe headache', 'sudden weakness', 'slurred speech',
        'severe abdominal pain', 'severe allergic reaction',
        'seizure', 'uncontrolled bleeding', 'severe burn',
        'poisoning', 'overdose', 'suicide', 'self-harm',
        'choking', 'drowning', 'severe trauma', 'broken bone',
        'head injury', 'spinal injury', 'severe pain'
    ]
    
    # Diagnosis patterns to filter
    DIAGNOSIS_PATTERNS = [
        r'\byou have\b.*\b(diabetes|cancer|disease|condition|disorder|syndrome)\b',
        r'\bdiagnosed with\b',
        r'\byou are suffering from\b',
        r'\byou\'ve got\b.*\b(diabetes|cancer|disease|condition)\b',
        r'\bthis is\b.*\b(diabetes|cancer|disease|condition)\b',
        r'\byou definitely have\b',
        r'\bconfirmed diagnosis of\b'
    ]
    
    # Dosage patterns to filter
    DOSAGE_PATTERNS = [
        r'\btake\s+\d+\s*(mg|mcg|g|ml|units?)\b',
        r'\b\d+\s*(mg|mcg|g|ml|units?)\s+(daily|twice|once|per day)\b',
        r'\bdosage of\s+\d+\s*(mg|mcg|g|ml)\b',
        r'\bprescribe\s+\d+\s*(mg|mcg|g|ml)\b'
    ]
    
    # Medical disclaimer template
    MEDICAL_DISCLAIMER = (
        "\n\n**IMPORTANT MEDICAL DISCLAIMER**: This information is for educational "
        "purposes only and does not constitute medical advice, diagnosis, or treatment. "
        "Always consult with a qualified healthcare professional for proper medical "
        "evaluation, diagnosis, and treatment recommendations."
    )
    
    # Emergency disclaimer
    EMERGENCY_DISCLAIMER = (
        "\n\n**⚠️ EMERGENCY NOTICE**: The symptoms described may indicate a medical emergency. "
        "Please seek immediate medical attention by calling emergency services (911) or "
        "visiting the nearest emergency room."
    )
    
    def __init__(self):
        """Initialize safety guardrails."""
        self.interventions_log: List[Dict[str, Any]] = []
        logger.info("SafetyGuardrails initialized")
    
    def check_emergency_indicators(self, text: str) -> bool:
        """
        Check if text contains emergency medical indicators.
        
        Requirements: 17.3 - Detect emergency indicators
        
        Args:
            text: Text to check
            
        Returns:
            True if emergency indicators found
        """
        text_lower = text.lower()
        
        for keyword in self.EMERGENCY_KEYWORDS:
            if keyword in text_lower:
                logger.warning(f"Emergency indicator detected: {keyword}")
                self._log_intervention('emergency_detected', keyword)
                return True
        
        return False
    
    def add_medical_disclaimer(self, response: str, is_emergency: bool = False) -> str:
        """
        Add appropriate medical disclaimer to response.
        
        Requirements: 17.2 - Add medical disclaimers to all responses
        
        Args:
            response: Original response text
            is_emergency: Whether emergency indicators were detected
            
        Returns:
            Response with disclaimer added
        """
        # Don't add duplicate disclaimers
        if 'MEDICAL DISCLAIMER' in response or 'EMERGENCY NOTICE' in response:
            return response
        
        if is_emergency:
            response += self.EMERGENCY_DISCLAIMER
            self._log_intervention('emergency_disclaimer_added', 'Emergency disclaimer')
        
        response += self.MEDICAL_DISCLAIMER
        self._log_intervention('disclaimer_added', 'Medical disclaimer')
        
        return response
    
    def prevent_diagnosis(self, response: str) -> str:
        """
        Ensure response doesn't provide specific medical diagnosis.
        
        Requirements: 17.1 - Prevent specific medical diagnoses
        
        Args:
            response: Original response text
            
        Returns:
            Filtered response
        """
        original_response = response
        
        for pattern in self.DIAGNOSIS_PATTERNS:
            if re.search(pattern, response, re.IGNORECASE):
                # Replace diagnosis statements with softer language
                response = re.sub(
                    pattern,
                    'your results suggest consulting a healthcare professional about',
                    response,
                    flags=re.IGNORECASE
                )
                logger.warning(f"Diagnosis statement filtered: {pattern}")
                self._log_intervention('diagnosis_filtered', pattern)
        
        # Additional filtering for direct diagnosis statements
        diagnosis_replacements = {
            'you have': 'your results may indicate',
            'you are diagnosed with': 'your results suggest',
            'you definitely have': 'your results may suggest',
            'this is': 'this may be related to',
            'you\'ve got': 'your results may indicate'
        }
        
        for original, replacement in diagnosis_replacements.items():
            if original in response.lower():
                response = re.sub(
                    re.escape(original),
                    replacement,
                    response,
                    flags=re.IGNORECASE
                )
        
        if response != original_response:
            self._log_intervention('diagnosis_language_softened', 'Diagnosis language modified')
        
        return response
    
    def prevent_dosage_recommendation(self, response: str) -> str:
        """
        Ensure response doesn't recommend specific medication dosages.
        
        Requirements: 17.4 - Prevent specific medication dosages
        
        Args:
            response: Original response text
            
        Returns:
            Filtered response
        """
        original_response = response
        
        for pattern in self.DOSAGE_PATTERNS:
            if re.search(pattern, response, re.IGNORECASE):
                # Remove specific dosage recommendations
                response = re.sub(
                    pattern,
                    '[consult your doctor for appropriate dosage]',
                    response,
                    flags=re.IGNORECASE
                )
                logger.warning(f"Dosage recommendation filtered: {pattern}")
                self._log_intervention('dosage_filtered', pattern)
        
        if response != original_response:
            self._log_intervention('dosage_removed', 'Specific dosages removed')
        
        return response
    
    def validate_response_safety(self, response: str) -> Dict[str, Any]:
        """
        Validate that response meets safety requirements.
        
        Requirements: 17.1, 17.2, 17.4, 17.5 - Comprehensive safety validation
        
        Args:
            response: Response to validate
            
        Returns:
            Validation result dictionary
        """
        issues = []
        
        # Check for diagnosis statements
        for pattern in self.DIAGNOSIS_PATTERNS:
            if re.search(pattern, response, re.IGNORECASE):
                issues.append(f"Contains diagnosis statement: {pattern}")
        
        # Check for dosage recommendations
        for pattern in self.DOSAGE_PATTERNS:
            if re.search(pattern, response, re.IGNORECASE):
                issues.append(f"Contains dosage recommendation: {pattern}")
        
        # Check for disclaimer
        has_disclaimer = 'MEDICAL DISCLAIMER' in response or 'disclaimer' in response.lower()
        if not has_disclaimer:
            issues.append("Missing medical disclaimer")
        
        # Check for professional consultation recommendation
        consultation_keywords = ['consult', 'healthcare professional', 'doctor', 'physician']
        has_consultation = any(keyword in response.lower() for keyword in consultation_keywords)
        if not has_consultation:
            issues.append("Missing professional consultation recommendation")
        
        # Check for emergency indicators
        is_emergency = self.check_emergency_indicators(response)
        if is_emergency and 'EMERGENCY NOTICE' not in response:
            issues.append("Emergency indicators present but no emergency notice")
        
        is_safe = len(issues) == 0
        
        result = {
            'is_safe': is_safe,
            'issues': issues,
            'has_disclaimer': has_disclaimer,
            'has_consultation_recommendation': has_consultation,
            'is_emergency': is_emergency
        }
        
        if not is_safe:
            logger.warning(f"Response safety validation failed: {issues}")
            self._log_intervention('validation_failed', str(issues))
        
        return result
    
    def apply_all_guardrails(self, response: str) -> str:
        """
        Apply all safety guardrails to response.
        
        Requirements: 17.1, 17.2, 17.3, 17.4, 17.5 - Apply all safety measures
        
        Args:
            response: Original response
            
        Returns:
            Safe response with all guardrails applied
        """
        # Check for emergencies first
        is_emergency = self.check_emergency_indicators(response)
        
        # Filter diagnosis statements
        response = self.prevent_diagnosis(response)
        
        # Filter dosage recommendations
        response = self.prevent_dosage_recommendation(response)
        
        # Add professional consultation if not present
        if not any(keyword in response.lower() for keyword in ['consult', 'healthcare professional', 'doctor']):
            response += "\n\nPlease consult with a qualified healthcare professional for proper evaluation and treatment."
            self._log_intervention('consultation_added', 'Professional consultation recommendation')
        
        # Add disclaimers
        response = self.add_medical_disclaimer(response, is_emergency)
        
        logger.info("All safety guardrails applied to response")
        
        return response
    
    def _log_intervention(self, intervention_type: str, details: str):
        """
        Log safety intervention for audit purposes.
        
        Requirements: 17.8 - Log all safety interventions
        
        Args:
            intervention_type: Type of intervention
            details: Intervention details
        """
        from datetime import datetime
        
        intervention = {
            'type': intervention_type,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.interventions_log.append(intervention)
        logger.info(f"Safety intervention logged: {intervention_type} - {details}")
    
    def get_interventions_log(self) -> List[Dict[str, Any]]:
        """
        Get log of all safety interventions.
        
        Requirements: 17.8 - Audit log of safety interventions
        
        Returns:
            List of intervention records
        """
        return self.interventions_log.copy()
    
    def clear_interventions_log(self):
        """Clear interventions log."""
        self.interventions_log.clear()
        logger.info("Safety interventions log cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about safety interventions.
        
        Returns:
            Statistics dictionary
        """
        from collections import Counter
        
        intervention_types = Counter(i['type'] for i in self.interventions_log)
        
        return {
            'total_interventions': len(self.interventions_log),
            'intervention_types': dict(intervention_types),
            'emergency_detections': intervention_types.get('emergency_detected', 0),
            'diagnosis_filtered': intervention_types.get('diagnosis_filtered', 0),
            'dosage_filtered': intervention_types.get('dosage_filtered', 0),
            'disclaimers_added': intervention_types.get('disclaimer_added', 0)
        }
