"""
Reflection Agent for AI Health Intelligence System

This agent performs hidden quality assurance checks on health assessments
before delivering results to users. It verifies:
- Appropriate confidence levels (no overconfidence)
- Emergency symptom detection (red flags)
- Logical consistency between components
- Appropriate medical claim hedging

Validates: Requirements 4.2, 4.5, 8.5 (Safety & Quality Assurance)
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from agents.base_agent import BaseHealthAgent
import re

logger = logging.getLogger('health_ai.reflection')


class ReflectionAgent(BaseHealthAgent):
    """
    Hidden quality assurance agent for cross-verification of health assessments.
    
    This agent runs as the final step before user delivery to ensure:
    - Safety (emergency detection, appropriate urgency)
    - Quality (logical consistency, accurate confidence)
    - Responsibility (proper disclaimers, medical hedging)
    """
    
    # Confidence thresholds for verification
    CONFIDENCE_THRESHOLDS = {
        "LOW": 0.55,
        "MEDIUM": 0.75,
        "HIGH": 0.75
    }
    
    # Emergency symptoms requiring immediate care
    EMERGENCY_SYMPTOMS = [
        "severe chest pain",
        "chest pain",
        "difficulty breathing",
        "shortness of breath",
        "loss of consciousness",
        "unconscious",
        "severe bleeding",
        "heavy bleeding",
        "stroke symptoms",
        "slurred speech",
        "facial drooping",
        "severe head injury",
        "head trauma",
        "seizure",
        "severe abdominal pain",
        "coughing blood",
        "vomiting blood",
        "sudden confusion",
        "sudden severe headache",
        "high fever with stiff neck"
    ]
    
    # Prohibited definitive phrases (medical AI should not diagnose)
    PROHIBITED_PHRASES = [
        "you have",
        "you are diagnosed with",
        "this is definitely",
        "you definitely have",
        "you must take",
        "you need to take",
        "this confirms",
        "confirmed diagnosis"
    ]
    
    # Required disclaimer elements
    REQUIRED_ELEMENTS = [
        "not a substitute",
        "consult",
        "healthcare professional",
        "medical advice"
    ]
    
    def __init__(self):
        """Initialize the reflection agent."""
        super().__init__("ReflectionAgent")
        logger.info("ReflectionAgent initialized for quality assurance")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method - verify a complete assessment.
        
        Args:
            input_data: Complete assessment to verify
            
        Returns:
            Verification result with any issues and corrections
        """
        try:
            result = self.verify_assessment(input_data)
            
            return self.format_agent_response(
                success=True,
                data=result,
                message="Assessment verification completed"
            )
            
        except Exception as e:
            logger.error(f"Reflection agent error: {str(e)}")
            return self.format_agent_response(
                success=False,
                message=f"Verification error: {str(e)}",
                data={"error": str(e)}
            )
    
    def verify_assessment(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cross-verify complete assessment for quality and safety.
        
        Args:
            assessment: Complete assessment with prediction, explanation, recommendations
            
        Returns:
            Verification result with issues, severity, and revised assessment if needed
        """
        verification_start = datetime.utcnow()
        
        logger.info("Starting cross-verification of assessment")
        
        # Extract components
        prediction = assessment.get("prediction", {})
        explanation = assessment.get("explanation", {})
        recommendations = assessment.get("recommendations", {})
        lifestyle = assessment.get("lifestyle_recommendations", {})
        symptoms = assessment.get("symptoms", [])
        
        # Run all verification checks
        all_issues = []
        
        # Check 1: Confidence verification
        confidence_issues = self._verify_confidence_level(
            prediction, explanation, symptoms
        )
        all_issues.extend(confidence_issues)
        
        # Check 2: Red flag detection (emergency symptoms)
        red_flag_issues = self._detect_red_flags(
            symptoms, recommendations
        )
        all_issues.extend(red_flag_issues)
        
        # Check 3: Logical consistency
        consistency_issues = self._check_logical_consistency(
            prediction, explanation, recommendations
        )
        all_issues.extend(consistency_issues)
        
        # Check 4: Medical claim verification
        claim_issues = self._verify_medical_claims(
            explanation, recommendations
        )
        all_issues.extend(claim_issues)
        
        # Determine overall severity
        severity = self._determine_severity(all_issues)
        
        # Determine recommended action
        recommended_action = self._determine_action(severity, all_issues)
        
        # Apply auto-corrections if needed
        revised_assessment = assessment
        if recommended_action in ["revise", "escalate"]:
            revised_assessment = self._revise_assessment(assessment, all_issues)
        
        verification_end = datetime.utcnow()
        verification_time = (verification_end - verification_start).total_seconds()
        
        # Log results
        self._log_verification_results(all_issues, severity, recommended_action)
        
        return {
            "verification_passed": len(all_issues) == 0,
            "issues_found": all_issues,
            "issue_count": len(all_issues),
            "severity": severity,
            "recommended_action": recommended_action,
            "revised_assessment": revised_assessment,
            "verification_metadata": {
                "verified": True,
                "verification_time_ms": round(verification_time * 1000, 2),
                "agent_version": "v1.0",
                "timestamp": verification_end.isoformat()
            }
        }
    
    def _verify_confidence_level(self, prediction: Dict, explanation: Dict, 
                                 symptoms: List[str]) -> List[Dict]:
        """
        Verify confidence level is appropriate for evidence.
        
        Checks:
        - Confidence aligns with probability threshold
        - Sufficient symptoms for high confidence
        - No overconfidence with weak evidence
        """
        issues = []
        
        confidence = prediction.get("confidence", "MEDIUM")
        probability = prediction.get("probability", 0.5)
        
        # Check probability-confidence alignment
        if confidence == "HIGH" and probability < self.CONFIDENCE_THRESHOLDS["HIGH"]:
            issues.append({
                "type": "overconfidence",
                "severity": "major",
                "component": "confidence_level",
                "message": f"HIGH confidence with probability {probability:.2f} below threshold {self.CONFIDENCE_THRESHOLDS['HIGH']}",
                "current_value": confidence,
                "recommended_value": "MEDIUM",
                "action": "downgrade_confidence"
            })
        
        # Check sufficient evidence for high confidence
        if confidence == "HIGH" and len(symptoms) < 3:
            issues.append({
                "type": "insufficient_evidence",
                "severity": "major",
                "component": "confidence_level",
                "message": f"HIGH confidence with only {len(symptoms)} symptom(s)",
                "action": "downgrade_confidence",
                "recommended_value": "MEDIUM"
            })
        
        # Check for low confidence with high probability (underconfidence)
        if confidence == "LOW" and probability >= self.CONFIDENCE_THRESHOLDS["MEDIUM"]:
            issues.append({
                "type": "underconfidence",
                "severity": "minor",
                "component": "confidence_level",
                "message": f"LOW confidence with probability {probability:.2f} suggests MEDIUM",
                "action": "upgrade_confidence",
                "recommended_value": "MEDIUM"
            })
        
        return issues
    
    def _detect_red_flags(self, symptoms: List[str], 
                         recommendations: Dict) -> List[Dict]:
        """
        Detect emergency symptoms and verify appropriate response.
        
        Checks:
        - Emergency symptoms present in input
        - Immediate care warning included
        - Urgency level appropriate
        """
        issues = []
        
        # Check for emergency symptoms
        emergency_detected = []
        symptoms_text = " ".join(str(s).lower() for s in symptoms)
        
        for emergency in self.EMERGENCY_SYMPTOMS:
            if emergency in symptoms_text:
                emergency_detected.append(emergency)
        
        if not emergency_detected:
            return issues  # No red flags
        
        # Emergency symptoms detected - verify response
        immediate_actions = recommendations.get("immediate_actions", {})
        actions_list = immediate_actions.get("actions", [])
        actions_text = " ".join(str(a).lower() for a in actions_list)
        
        # Check if emergency warning present
        has_emergency_warning = any([
            "immediate emergency" in actions_text,
            "emergency care" in actions_text,
            "911" in actions_text,
            immediate_actions.get("emergency_warning", False)
        ])
        
        if not has_emergency_warning:
            issues.append({
                "type": "missing_emergency_warning",
                "severity": "critical",
                "component": "recommendations",
                "message": f"Emergency symptoms detected ({', '.join(emergency_detected)}) but no immediate care warning",
                "emergency_symptoms": emergency_detected,
                "action": "add_emergency_warning",
                "required_text": "⚠️ SEEK IMMEDIATE EMERGENCY MEDICAL CARE"
            })
        
        # Check urgency level
        referral = recommendations.get("professional_referral", {})
        urgency = referral.get("urgency", "moderate")
        
        if urgency not in ["high", "immediate", "emergency"]:
            issues.append({
                "type": "inappropriate_urgency",
                "severity": "critical",
                "component": "referral_urgency",
                "message": f"Emergency symptoms but urgency is '{urgency}'",
                "action": "upgrade_urgency",
                "recommended_value": "immediate_emergency"
            })
        
        return issues
    
    def _check_logical_consistency(self, prediction: Dict, explanation: Dict,
                                   recommendations: Dict) -> List[Dict]:
        """
        Verify logical consistency between assessment components.
        
        Checks:
        - Explanation matches predicted disease
        - Recommendations align with confidence
        - Urgency matches confidence level
        """
        issues = []
        
        disease = prediction.get("disease", "").lower()
        confidence = prediction.get("confidence", "MEDIUM")
        
        # Check explanation-prediction alignment
        explanation_text = str(explanation.get("main_explanation", "")).lower()
        
        # Extract disease mentions from explanation
        if disease and disease not in explanation_text.replace("_", " "):
            # Disease name should appear in explanation
            issues.append({
                "type": "explanation_disease_mismatch",
                "severity": "major",
                "component": "explanation",
                "message": f"Predicted disease '{disease}' not clearly discussed in explanation",
                "action": "verify_disease_match"
            })
        
        # Check confidence-urgency alignment
        referral = recommendations.get("professional_referral", {})
        urgency = referral.get("urgency", "moderate")
        
        if confidence == "HIGH" and urgency == "non-urgent":
            issues.append({
                "type": "confidence_urgency_mismatch",
                "severity": "minor",
                "component": "referral_urgency",
                "message": "HIGH confidence should not have 'non-urgent' referral",
                "action": "upgrade_urgency",
                "recommended_value": "high"
            })
        
        if confidence == "LOW" and urgency == "high":
            issues.append({
                "type": "confidence_urgency_mismatch",
                "severity": "minor",
                "component": "referral_urgency",
                "message": "LOW confidence with 'high' urgency is inconsistent",
                "action": "moderate_urgency"
            })
        
        return issues
    
    def _verify_medical_claims(self, explanation: Dict, 
                               recommendations: Dict) -> List[Dict]:
        """
        Verify appropriate medical hedging and disclaimers.
        
        Checks:
        - No definitive diagnostic statements
        - Required disclaimer elements present
        - Appropriate hedging language used
        """
        issues = []
        
        # Combine all text for checking
        full_text = str(explanation) + str(recommendations)
        full_text_lower = full_text.lower()
        
        # Check for prohibited definitive statements
        for phrase in self.PROHIBITED_PHRASES:
            if phrase in full_text_lower:
                issues.append({
                    "type": "definitive_claim",
                    "severity": "critical",
                    "component": "medical_claims",
                    "message": f"Inappropriate definitive statement: '{phrase}'",
                    "prohibited_phrase": phrase,
                    "action": "add_hedging",
                    "recommendation": "Rephrase with 'may have', 'risk for', 'could indicate'"
                })
        
        # Check for required disclaimer elements
        disclaimers = recommendations.get("disclaimers", {})
        disclaimer_text = str(disclaimers).lower()
        
        missing_elements = []
        for required in self.REQUIRED_ELEMENTS:
            if required not in disclaimer_text and required not in full_text_lower:
                missing_elements.append(required)
        
        if missing_elements:
            issues.append({
                "type": "missing_disclaimer_elements",
                "severity": "major",
                "component": "disclaimers",
                "message": f"Missing required disclaimer elements: {', '.join(missing_elements)}",
                "missing_elements": missing_elements,
                "action": "ensure_disclaimers"
            })
        
        return issues
    
    def _determine_severity(self, issues: List[Dict]) -> str:
        """Determine overall severity from all issues."""
        if not issues:
            return "none"
        
        severities = [issue.get("severity", "minor") for issue in issues]
        
        if "critical" in severities:
            return "critical"
        elif "major" in severities:
            return "major"
        elif "minor" in severities:
            return "minor"
        else:
            return "none"
    
    def _determine_action(self, severity: str, issues: List[Dict]) -> str:
        """Determine recommended action based on severity."""
        if severity == "none":
            return "proceed"
        elif severity == "minor":
            return "proceed_with_log"
        elif severity == "major":
            return "revise"
        elif severity == "critical":
            return "escalate"
        else:
            return "proceed"
    
    def _revise_assessment(self, assessment: Dict, issues: List[Dict]) -> Dict:
        """
        Automatically revise assessment to address identified issues.
        
        Applies auto-corrections for:
        - Confidence adjustments
        - Emergency warnings
        - Urgency upgrades
        """
        revised = assessment.copy()
        corrections_made = []
        
        for issue in issues:
            action = issue.get("action", "")
            
            # Handle overconfidence
            if action == "downgrade_confidence":
                if "prediction" in revised:
                    old_confidence = revised["prediction"].get("confidence")
                    revised["prediction"]["confidence"] = issue.get("recommended_value", "MEDIUM")
                    corrections_made.append(f"Confidence: {old_confidence} → {revised['prediction']['confidence']}")
                    logger.warning(f"Auto-corrected: {issue['message']}")
            
            # Handle underconfidence
            elif action == "upgrade_confidence":
                if "prediction" in revised:
                    old_confidence = revised["prediction"].get("confidence")
                    revised["prediction"]["confidence"] = issue.get("recommended_value", "MEDIUM")
                    corrections_made.append(f"Confidence: {old_confidence} → {revised['prediction']['confidence']}")
            
            # Handle missing emergency warning
            elif action == "add_emergency_warning":
                if "recommendations" in revised:
                    immediate = revised["recommendations"].get("immediate_actions", {})
                    actions = immediate.get("actions", [])
                    
                    # Add emergency warning at the top
                    emergency_text = issue.get("required_text", "⚠️ SEEK IMMEDIATE EMERGENCY MEDICAL CARE")
                    if emergency_text not in str(actions):
                        actions.insert(0, emergency_text)
                        immediate["actions"] = actions
                        immediate["emergency_warning"] = True
                        immediate["emergency_symptoms"] = issue.get("emergency_symptoms", [])
                        revised["recommendations"]["immediate_actions"] = immediate
                        corrections_made.append("Added emergency care warning")
                        logger.critical(f"Emergency warning added: {issue['message']}")
            
            # Handle urgency upgrades
            elif action in ["upgrade_urgency", "moderate_urgency"]:
                if "recommendations" in revised and "professional_referral" in revised["recommendations"]:
                    referral = revised["recommendations"]["professional_referral"]
                    old_urgency = referral.get("urgency")
                    new_urgency = issue.get("recommended_value", "high")
                    referral["urgency"] = new_urgency
                    referral["timeframe"] = "immediately" if new_urgency in ["immediate_emergency", "emergency"] else "as soon as possible"
                    corrections_made.append(f"Urgency: {old_urgency} → {new_urgency}")
        
        # Add verification metadata to revised assessment
        if corrections_made:
            revised["_verification_info"] = {
                "auto_corrected": True,
                "corrections_applied": corrections_made,
                "issues_addressed": len(issues),
                "correction_timestamp": datetime.utcnow().isoformat()
            }
        
        return revised
    
    def _log_verification_results(self, issues: List[Dict], severity: str, 
                                  action: str):
        """Log verification results for monitoring."""
        if not issues:
            logger.info("✓ Assessment verified: No issues found")
        else:
            issue_summary = {}
            for issue in issues:
                issue_type = issue.get("type", "unknown")
                issue_summary[issue_type] = issue_summary.get(issue_type, 0) + 1
            
            log_message = (
                f"Assessment verification: {len(issues)} issue(s) found "
                f"(severity: {severity}, action: {action}) - "
                f"Issues: {issue_summary}"
            )
            
            if severity == "critical":
                logger.critical(log_message)
            elif severity == "major":
                logger.error(log_message)
            elif severity == "minor":
                logger.warning(log_message)
            else:
                logger.info(log_message)
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """Get summary of reflection agent capabilities."""
        return {
            "agent": "ReflectionAgent",
            "purpose": "Quality assurance and safety verification",
            "verification_checks": [
                "Confidence level appropriateness",
                "Emergency symptom detection",
                "Logical consistency",
                "Medical claim hedging"
            ],
            "auto_corrections": [
                "Confidence adjustments",
                "Emergency warning addition",
                "Urgency level upgrades"
            ],
            "severity_levels": ["none", "minor", "major", "critical"],
            "actions": ["proceed", "proceed_with_log", "revise", "escalate"]
        }
