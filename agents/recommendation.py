"""
Recommendation Agent for AI Health Intelligence System

This agent applies ethical gating for treatment information and ensures
appropriate professional referrals based on confidence levels.

Validates: Requirements 4.2, 4.5
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from treatment.knowledge_base import TreatmentKnowledgeBase

logger = logging.getLogger('health_ai.recommendation')


class RecommendationAgent:
    """
    Ethical gating agent for treatment recommendations and professional referrals.
    
    Key responsibilities:
    - Apply confidence-based treatment gating
    - Ensure appropriate professional referrals
    - Add safety disclaimers
    - Prevent inappropriate medical advice
    """
    
    def __init__(self):
        """Initialize the recommendation agent."""
        self.treatment_kb = TreatmentKnowledgeBase()
        
        # Confidence-based gating rules
        self.confidence_gates = {
            "LOW": {
                "allow_treatment_info": False,
                "referral_urgency": "routine",
                "message": "Please consult with a healthcare professional for proper evaluation"
            },
            "MEDIUM": {
                "allow_treatment_info": True,
                "referral_urgency": "recommended",
                "message": "We recommend discussing these symptoms with a healthcare professional"
            },
            "HIGH": {
                "allow_treatment_info": True,
                "referral_urgency": "strongly_recommended",
                "message": "We strongly recommend consulting with a healthcare professional promptly"
            }
        }
        
        # Professional referral templates
        self.referral_templates = {
            "routine": {
                "message": "Consider scheduling a routine appointment with your healthcare provider to discuss these symptoms.",
                "urgency": "non-urgent",
                "timeframe": "within a few weeks"
            },
            "recommended": {
                "message": "We recommend scheduling an appointment with your healthcare provider to evaluate these symptoms.",
                "urgency": "moderate",
                "timeframe": "within a week"
            },
            "strongly_recommended": {
                "message": "We strongly recommend consulting with a healthcare professional promptly for proper evaluation and care.",
                "urgency": "high",
                "timeframe": "as soon as possible"
            }
        }
        
        logger.info("RecommendationAgent initialized")
    
    def allow_treatment(self, confidence: str) -> bool:
        """
        Ethical gate - only allow treatment info for sufficient confidence.
        
        Args:
            confidence: Confidence level (LOW, MEDIUM, HIGH)
            
        Returns:
            Boolean indicating if treatment information should be provided
        """
        gate_info = self.confidence_gates.get(confidence, self.confidence_gates["LOW"])
        allowed = gate_info["allow_treatment_info"]
        
        logger.info(f"Treatment information {'allowed' if allowed else 'blocked'} for {confidence} confidence")
        return allowed
    
    def get_recommendations(self, disease: str, probability: float, confidence: str, 
                          symptoms: List[str], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate comprehensive recommendations based on assessment results.
        
        Args:
            disease: The assessed disease/condition
            probability: Risk probability (0.0 to 1.0)
            confidence: Confidence level
            symptoms: List of user symptoms
            user_context: Optional additional user context
            
        Returns:
            Dictionary containing recommendations and referral information
        """
        logger.info(f"Generating recommendations for {disease} with {confidence} confidence")
        
        try:
            recommendations = {
                "assessment_summary": {
                    "disease": disease.replace("_", " ").title(),
                    "probability": probability,
                    "confidence": confidence,
                    "assessment_date": datetime.utcnow().isoformat()
                },
                "treatment_information": self._get_treatment_recommendations(disease, confidence),
                "professional_referral": self._get_professional_referral(confidence, disease, probability),
                "immediate_actions": self._get_immediate_actions(confidence, symptoms),
                "follow_up_guidance": self._get_follow_up_guidance(confidence, disease),
                "disclaimers": self._get_comprehensive_disclaimers(),
                "generated_by": "recommendation_agent"
            }
            
            logger.info("Recommendations generated successfully")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return self._get_fallback_recommendations(disease, confidence)
    
    def _get_treatment_recommendations(self, disease: str, confidence: str) -> Dict[str, Any]:
        """Get treatment recommendations based on confidence level."""
        if not self.allow_treatment(confidence):
            return {
                "available": False,
                "reason": "Confidence level too low for treatment information",
                "alternative": "Please consult with healthcare professionals for treatment guidance"
            }
        
        # Get treatment information from knowledge base
        treatment_info = self.treatment_kb.format_treatment_response(disease, confidence)
        
        if treatment_info["available"]:
            # Add recommendation-specific context
            treatment_info["recommendation_context"] = {
                "confidence_level": confidence,
                "suitability_note": (
                    "Treatment approaches may vary in effectiveness for different individuals. "
                    "Professional guidance is essential for selecting appropriate treatments."
                ),
                "integration_note": (
                    "Different medical systems can often be integrated under professional supervision. "
                    "Discuss all treatment options with qualified practitioners."
                )
            }
        
        return treatment_info
    
    def _get_professional_referral(self, confidence: str, disease: str, probability: float) -> Dict[str, Any]:
        """Generate professional referral recommendations."""
        gate_info = self.confidence_gates.get(confidence, self.confidence_gates["MEDIUM"])
        referral_info = self.referral_templates.get(gate_info["referral_urgency"])
        
        # Disease-specific referral suggestions
        specialist_suggestions = {
            "diabetes": ["Endocrinologist", "Primary Care Physician", "Diabetes Educator"],
            "heart_disease": ["Cardiologist", "Primary Care Physician", "Cardiac Rehabilitation Specialist"],
            "hypertension": ["Primary Care Physician", "Cardiologist", "Hypertension Specialist"]
        }
        
        return {
            "urgency": referral_info["urgency"],
            "timeframe": referral_info["timeframe"],
            "message": referral_info["message"],
            "suggested_specialists": specialist_suggestions.get(disease, ["Primary Care Physician"]),
            "preparation_tips": [
                "List all current symptoms and when they started",
                "Bring any previous medical records or test results",
                "List current medications and supplements",
                "Prepare questions about your symptoms and concerns",
                "Consider bringing a family member or friend for support"
            ],
            "questions_to_ask": [
                "What could be causing these symptoms?",
                "What tests or evaluations do you recommend?",
                "What are my treatment options?",
                "How can I monitor my condition at home?",
                "When should I schedule follow-up appointments?"
            ]
        }
    
    def _get_immediate_actions(self, confidence: str, symptoms: List[str]) -> Dict[str, Any]:
        """Get immediate actions based on confidence and symptoms."""
        immediate_actions = {
            "LOW": [
                "Monitor symptoms and note any changes",
                "Maintain a symptom diary",
                "Continue normal activities unless symptoms worsen",
                "Schedule routine healthcare appointment if symptoms persist"
            ],
            "MEDIUM": [
                "Monitor symptoms closely and document changes",
                "Avoid activities that worsen symptoms",
                "Schedule healthcare appointment within a week",
                "Consider lifestyle modifications that may help",
                "Seek immediate care if symptoms significantly worsen"
            ],
            "HIGH": [
                "Seek healthcare consultation promptly",
                "Monitor symptoms closely and document any changes",
                "Avoid strenuous activities until evaluated",
                "Have emergency contact information readily available",
                "Seek immediate emergency care if symptoms become severe"
            ]
        }
        
        # Add symptom-specific emergency warnings
        emergency_symptoms = [
            "severe chest pain", "difficulty breathing", "severe headache",
            "loss of consciousness", "severe abdominal pain", "high fever"
        ]
        
        has_emergency_symptoms = any(
            any(emergency in symptom.lower() for emergency in emergency_symptoms)
            for symptom in symptoms
        )
        
        actions = immediate_actions.get(confidence, immediate_actions["MEDIUM"])
        
        if has_emergency_symptoms:
            actions.insert(0, "⚠️ SEEK IMMEDIATE EMERGENCY MEDICAL CARE if experiencing severe symptoms")
        
        return {
            "actions": actions,
            "emergency_warning": has_emergency_symptoms,
            "emergency_contact": "Call emergency services (911) for severe or life-threatening symptoms"
        }
    
    def _get_follow_up_guidance(self, confidence: str, disease: str) -> Dict[str, Any]:
        """Get follow-up guidance based on assessment."""
        follow_up_schedules = {
            "LOW": {
                "initial_follow_up": "4-6 weeks if symptoms persist",
                "monitoring_frequency": "As needed based on symptom changes",
                "reassessment": "If symptoms worsen or new symptoms develop"
            },
            "MEDIUM": {
                "initial_follow_up": "1-2 weeks",
                "monitoring_frequency": "Weekly symptom monitoring",
                "reassessment": "If no improvement in 2-3 weeks"
            },
            "HIGH": {
                "initial_follow_up": "Within a few days",
                "monitoring_frequency": "Daily symptom monitoring",
                "reassessment": "Immediate if symptoms worsen"
            }
        }
        
        return follow_up_schedules.get(confidence, follow_up_schedules["MEDIUM"])
    
    def _get_comprehensive_disclaimers(self) -> Dict[str, str]:
        """Get comprehensive disclaimers for recommendations."""
        return {
            "medical_disclaimer": (
                "This assessment and recommendations are for informational and educational "
                "purposes only. They are not intended to be a substitute for professional "
                "medical advice, diagnosis, or treatment. Always seek the advice of your "
                "physician or other qualified health provider with any questions you may "
                "have regarding a medical condition."
            ),
            "treatment_disclaimer": (
                "Treatment information provided represents general educational content about "
                "various medical approaches. Individual treatment plans should always be "
                "developed in consultation with qualified healthcare professionals who can "
                "consider your complete medical history and individual circumstances."
            ),
            "emergency_disclaimer": (
                "This system cannot replace emergency medical services. If you are "
                "experiencing a medical emergency, call emergency services immediately. "
                "Do not rely on this assessment for emergency medical decisions."
            ),
            "accuracy_disclaimer": (
                "While this system uses advanced AI technology, it has limitations and "
                "may not identify all possible conditions or provide complete assessments. "
                "Professional medical evaluation remains essential for accurate diagnosis "
                "and appropriate treatment."
            )
        }
    
    def _get_fallback_recommendations(self, disease: str, confidence: str) -> Dict[str, Any]:
        """Generate fallback recommendations when main generation fails."""
        logger.warning("Using fallback recommendations due to generation failure")
        
        return {
            "assessment_summary": {
                "disease": disease.replace("_", " ").title(),
                "confidence": confidence,
                "note": "Detailed recommendations unavailable"
            },
            "treatment_information": {
                "available": False,
                "reason": "Treatment information generation failed",
                "alternative": "Please consult with healthcare professionals for treatment guidance"
            },
            "professional_referral": {
                "urgency": "recommended",
                "message": "We recommend consulting with a healthcare professional for proper evaluation",
                "timeframe": "as soon as convenient"
            },
            "immediate_actions": {
                "actions": [
                    "Consult with a healthcare professional",
                    "Monitor symptoms and document changes",
                    "Seek immediate care if symptoms worsen"
                ]
            },
            "disclaimers": self._get_comprehensive_disclaimers(),
            "generated_by": "fallback_system"
        }
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """Get summary of recommendation agent capabilities."""
        return {
            "confidence_gates": self.confidence_gates,
            "supported_diseases": self.treatment_kb.get_supported_diseases(),
            "supported_systems": self.treatment_kb.get_supported_systems(),
            "features": [
                "Confidence-based treatment gating",
                "Professional referral recommendations",
                "Immediate action guidance",
                "Follow-up scheduling",
                "Comprehensive disclaimers",
                "Emergency symptom detection"
            ],
            "ethical_safeguards": [
                "No treatment information for LOW confidence",
                "Mandatory professional referrals",
                "Emergency symptom warnings",
                "Comprehensive medical disclaimers"
            ]
        }