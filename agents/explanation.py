"""
Explanation Agent for AI Health Intelligence System

This agent generates human-readable explanations for health risk assessments
using Google Gemini AI while maintaining strict ethical boundaries.

Validates: Requirements 5.1, 5.2, 5.3, 5.4
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime
from common.gemini_client import GeminiClient

logger = logging.getLogger('health_ai.explanation')


class ExplanationAgent:
    """
    Generates human-readable explanations for health risk assessments.
    
    Key responsibilities:
    - Generate clear explanations using Gemini AI
    - Provide confidence reasoning
    - Add appropriate medical disclaimers
    - Maintain educational focus (never diagnostic)
    """
    
    def __init__(self):
        """Initialize the explanation agent."""
        self.gemini_client = GeminiClient()
        
        # Confidence level explanations
        self.confidence_explanations = {
            "LOW": {
                "meaning": "The system has limited confidence in this assessment",
                "reason": "The symptoms provided are either too general, insufficient, or don't strongly indicate any specific condition",
                "recommendation": "Consider providing more specific symptoms or consulting a healthcare professional"
            },
            "MEDIUM": {
                "meaning": "The system has moderate confidence in this assessment",
                "reason": "The symptoms show some patterns that suggest this condition, but additional factors should be considered",
                "recommendation": "This warrants attention and professional medical evaluation"
            },
            "HIGH": {
                "meaning": "The system has high confidence in this assessment",
                "reason": "The symptoms strongly align with patterns associated with this condition",
                "recommendation": "We strongly recommend consulting with a healthcare professional for proper evaluation"
            }
        }
        
        # Standard medical disclaimers
        self.medical_disclaimer = (
            "IMPORTANT DISCLAIMER: This assessment is for educational and informational "
            "purposes only. It is not intended to be a substitute for professional medical "
            "advice, diagnosis, or treatment. Always seek the advice of your physician or "
            "other qualified health provider with any questions you may have regarding a "
            "medical condition."
        )
        
        logger.info("ExplanationAgent initialized")
    
    def explain(self, disease: str, probability: float, confidence: str, 
                symptoms: list, additional_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive explanation for a health risk assessment.
        
        Args:
            disease: The disease/condition being assessed
            probability: Risk probability (0.0 to 1.0)
            confidence: Confidence level (LOW, MEDIUM, HIGH)
            symptoms: List of symptoms provided by user
            additional_context: Optional additional context for explanation
            
        Returns:
            Dictionary containing explanation components
        """
        logger.info(f"Generating explanation for {disease} with {confidence} confidence")
        
        try:
            # Generate the main explanation using Gemini
            main_explanation = self.gemini_client.generate_explanation(
                disease, probability, confidence, symptoms
            )
            
            # Build comprehensive explanation structure
            explanation_data = {
                "summary": f"Risk assessment for {disease.replace('_', ' ').title()}",
                "probability_percent": round(probability * 100, 2),
                "confidence": confidence,
                "main_explanation": main_explanation,
                "confidence_reasoning": self._get_confidence_reasoning(confidence),
                "contributing_factors": self._analyze_contributing_factors(symptoms, disease),
                "educational_content": self._get_educational_content(disease),
                "disclaimer": self.medical_disclaimer,
                "generated_at": datetime.utcnow().isoformat(),
                "generated_by": "gemini_ai"
            }
            
            logger.info("Explanation generated successfully")
            return explanation_data
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return self._get_fallback_explanation(disease, probability, confidence)
    
    def _get_confidence_reasoning(self, confidence: str) -> Dict[str, str]:
        """Get reasoning for the confidence level."""
        return self.confidence_explanations.get(confidence, self.confidence_explanations["MEDIUM"])
    
    def _analyze_contributing_factors(self, symptoms: list, disease: str) -> Dict[str, Any]:
        """Analyze which factors contributed to the assessment."""
        # This is a simplified analysis - in a real system, this would be more sophisticated
        factor_analysis = {
            "primary_symptoms": [],
            "supporting_symptoms": [],
            "general_symptoms": []
        }
        
        # Disease-specific symptom categorization
        disease_patterns = {
            "diabetes": {
                "primary": ["increased_thirst", "frequent_urination", "unexplained_weight_loss", "fatigue"],
                "supporting": ["blurred_vision", "slow_healing", "tingling", "hunger"]
            },
            "heart_disease": {
                "primary": ["chest_pain", "shortness_of_breath", "fatigue", "irregular_heartbeat"],
                "supporting": ["dizziness", "nausea", "sweating", "arm_pain"]
            },
            "hypertension": {
                "primary": ["headaches", "dizziness", "chest_pain", "shortness_of_breath"],
                "supporting": ["fatigue", "vision_problems", "nosebleeds", "nausea"]
            }
        }
        
        patterns = disease_patterns.get(disease, {"primary": [], "supporting": []})
        
        for symptom in symptoms:
            symptom_clean = symptom.replace(" ", "_").lower()
            if symptom_clean in patterns["primary"]:
                factor_analysis["primary_symptoms"].append(symptom)
            elif symptom_clean in patterns["supporting"]:
                factor_analysis["supporting_symptoms"].append(symptom)
            else:
                factor_analysis["general_symptoms"].append(symptom)
        
        return factor_analysis
    
    def _get_educational_content(self, disease: str) -> Dict[str, str]:
        """Get educational content about the disease/condition."""
        educational_content = {
            "diabetes": {
                "about": "Diabetes is a group of metabolic disorders characterized by high blood sugar levels.",
                "risk_factors": "Family history, obesity, sedentary lifestyle, age, and certain ethnicities increase risk.",
                "prevention": "Maintaining healthy weight, regular exercise, and balanced diet can help prevent type 2 diabetes."
            },
            "heart_disease": {
                "about": "Heart disease refers to several types of heart conditions that affect heart function.",
                "risk_factors": "High blood pressure, high cholesterol, smoking, diabetes, and family history increase risk.",
                "prevention": "Regular exercise, healthy diet, not smoking, and managing stress can help prevent heart disease."
            },
            "hypertension": {
                "about": "Hypertension (high blood pressure) is a condition where blood pressure is consistently elevated.",
                "risk_factors": "Age, family history, obesity, high sodium intake, and lack of exercise increase risk.",
                "prevention": "Maintaining healthy weight, reducing sodium intake, regular exercise, and limiting alcohol can help."
            }
        }
        
        return educational_content.get(disease, {
            "about": "This condition requires professional medical evaluation for proper understanding.",
            "risk_factors": "Various factors can contribute to health conditions.",
            "prevention": "Maintaining a healthy lifestyle is generally beneficial for overall health."
        })
    
    def _get_fallback_explanation(self, disease: str, probability: float, confidence: str) -> Dict[str, Any]:
        """Generate fallback explanation when main generation fails."""
        logger.warning("Using fallback explanation due to generation failure")
        
        return {
            "summary": f"Risk assessment for {disease.replace('_', ' ').title()}",
            "probability_percent": round(probability * 100, 2),
            "confidence": confidence,
            "main_explanation": (
                f"Based on the symptoms provided, our system assessed a {probability:.1%} "
                f"risk level with {confidence} confidence. This assessment is for informational "
                f"purposes only and should be discussed with a healthcare professional."
            ),
            "confidence_reasoning": self._get_confidence_reasoning(confidence),
            "contributing_factors": {"note": "Detailed analysis unavailable"},
            "educational_content": self._get_educational_content(disease),
            "disclaimer": self.medical_disclaimer,
            "generated_at": datetime.utcnow().isoformat(),
            "generated_by": "fallback_system"
        }
    
    def create_confidence_specific_explanation(self, confidence: str, disease: str, 
                                             probability: float) -> str:
        """Create explanation templates specific to confidence levels."""
        templates = {
            "LOW": (
                f"Our assessment suggests a {probability:.1%} risk for {disease.replace('_', ' ')}. "
                f"However, we have low confidence in this assessment because the symptoms "
                f"provided are quite general and could be associated with many different conditions. "
                f"We recommend consulting with a healthcare professional who can perform a "
                f"proper evaluation considering your complete medical history."
            ),
            "MEDIUM": (
                f"Based on your symptoms, we've assessed a {probability:.1%} risk for "
                f"{disease.replace('_', ' ')} with moderate confidence. While the symptoms "
                f"show some patterns consistent with this condition, additional factors "
                f"should be considered. We recommend discussing these symptoms with a "
                f"healthcare professional for proper evaluation."
            ),
            "HIGH": (
                f"Our analysis indicates a {probability:.1%} risk for {disease.replace('_', ' ')} "
                f"with high confidence. The symptoms you've provided align strongly with "
                f"patterns associated with this condition. We strongly recommend consulting "
                f"with a healthcare professional promptly for proper diagnosis and "
                f"appropriate care."
            )
        }
        
        return templates.get(confidence, templates["MEDIUM"])
    
    def get_explanation_summary(self) -> Dict[str, Any]:
        """Get summary of explanation capabilities."""
        return {
            "ai_integration": "Google Gemini",
            "supported_confidence_levels": list(self.confidence_explanations.keys()),
            "features": [
                "Natural language explanations",
                "Confidence reasoning",
                "Contributing factor analysis",
                "Educational content",
                "Medical disclaimers",
                "Fallback explanations"
            ],
            "gemini_status": self.gemini_client.get_client_status()
        }