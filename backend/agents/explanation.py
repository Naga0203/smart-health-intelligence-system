"""
LangChain-based Explanation Agent for AI Health Intelligence System

This agent generates human-readable explanations for health risk assessments
using LangChain framework with Google Gemini AI while maintaining strict ethical boundaries.

Validates: Requirements 5.1, 5.2, 5.3, 5.4
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime
from agents.base_agent import BaseHealthAgent

logger = logging.getLogger('health_ai.explanation')


class LangChainExplanationAgent(BaseHealthAgent):
    """
    LangChain-based explanation agent for health risk assessments.
    
    Key responsibilities:
    - Generate clear explanations using LangChain and Gemini AI
    - Provide confidence reasoning
    - Add appropriate medical disclaimers
    - Maintain educational focus (never diagnostic)
    """
    
    def __init__(self):
        """Initialize the LangChain explanation agent."""
        super().__init__("ExplanationAgent")
        
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
        
        # Standard medical disclaimer
        self.medical_disclaimer = (
            "IMPORTANT DISCLAIMER: This assessment is for educational and informational "
            "purposes only. It is not intended to be a substitute for professional medical "
            "advice, diagnosis, or treatment. Always seek the advice of your physician or "
            "other qualified health provider with any questions you may have regarding a "
            "medical condition."
        )
        
        # Create LangChain chain for explanation generation
        self.explanation_chain = self.create_agent_chain(
            system_prompt="""You are an AI assistant helping to explain health risk assessments. Your role is to provide clear, educational explanations while emphasizing that this is NOT medical diagnosis.

CRITICAL REQUIREMENTS:
- This is NOT a medical diagnosis
- Always emphasize consulting healthcare professionals
- Use simple, non-medical language
- Be supportive but not alarming
- Focus on education, not treatment advice
- Keep explanations under 300 words
- Maintain a supportive, educational tone""",
            
            human_prompt="""Please explain this health risk assessment:

Condition assessed: {disease}
Risk probability: {probability_percent}%
Confidence level: {confidence}
Symptoms provided: {symptoms}

Please explain:
1. What this risk assessment means in simple terms
2. Why the confidence level is {confidence}
3. What factors contributed to this assessment
4. The importance of professional medical consultation

Remember: This is for educational purposes only and not a medical diagnosis."""
        )
        
        logger.info("LangChain ExplanationAgent initialized")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for explanation generation.
        
        Args:
            input_data: Contains disease, probability, confidence, symptoms, etc.
            
        Returns:
            Comprehensive explanation result
        """
        # Validate required input fields
        required_fields = ["disease", "probability", "confidence", "symptoms"]
        validation = self.validate_input(input_data, required_fields)
        
        if not validation["valid"]:
            return self.format_agent_response(
                success=False,
                message=validation["message"],
                data=validation
            )
        
        self.log_agent_action("generate_explanation", {
            "disease": input_data["disease"],
            "confidence": input_data["confidence"]
        })
        
        try:
            explanation_data = self.explain(
                disease=input_data["disease"],
                probability=input_data["probability"],
                confidence=input_data["confidence"],
                symptoms=input_data["symptoms"],
                additional_context=input_data.get("additional_context")
            )
            
            return self.format_agent_response(
                success=True,
                data=explanation_data,
                message="Explanation generated successfully"
            )
            
        except Exception as e:
            logger.error(f"Error in explanation processing: {str(e)}")
            return self.get_fallback_response(input_data)
    
    def explain(self, disease: str, probability: float, confidence: str, 
                symptoms: list, additional_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive explanation for a health risk assessment using LangChain.
        
        Args:
            disease: The disease/condition being assessed
            probability: Risk probability (0.0 to 1.0)
            confidence: Confidence level (LOW, MEDIUM, HIGH)
            symptoms: List of symptoms provided by user
            additional_context: Optional additional context for explanation
            
        Returns:
            Dictionary containing explanation components
        """
        logger.info(f"Generating explanation for {disease} with {confidence} confidence using LangChain")
        
        try:
            # Generate the main explanation using LangChain
            main_explanation = self._generate_langchain_explanation(
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
                "generated_by": "langchain_gemini_ai",
                "agent": "LangChainExplanationAgent"
            }
            
            logger.info("LangChain explanation generated successfully")
            return explanation_data
            
        except Exception as e:
            logger.error(f"Error generating LangChain explanation: {str(e)}")
            return self._get_fallback_explanation(disease, probability, confidence)
    
    def _generate_langchain_explanation(self, disease: str, probability: float, 
                                      confidence: str, symptoms: list) -> str:
        """
        Generate explanation using LangChain chain.
        
        Args:
            disease: Disease being assessed
            probability: Risk probability
            confidence: Confidence level
            symptoms: List of symptoms
            
        Returns:
            Generated explanation text
        """
        try:
            if not self.explanation_chain:
                return self._get_simple_explanation(disease, probability, confidence)
            
            # Prepare input for LangChain
            chain_input = {
                "disease": disease.replace('_', ' ').title(),
                "probability_percent": round(probability * 100, 1),
                "confidence": confidence,
                "symptoms": ", ".join(symptoms)
            }
            
            # Execute LangChain chain
            explanation = self.execute_chain(self.explanation_chain, chain_input)
            
            if explanation:
                return explanation
            else:
                return self._get_simple_explanation(disease, probability, confidence)
                
        except Exception as e:
            logger.error(f"LangChain explanation generation failed: {str(e)}")
            return self._get_simple_explanation(disease, probability, confidence)
    
    def _get_simple_explanation(self, disease: str, probability: float, confidence: str) -> str:
        """Get simple explanation when LangChain is unavailable."""
        return (
            f"Based on the symptoms provided, our system assessed a {probability:.1%} "
            f"risk level for {disease.replace('_', ' ')} with {confidence} confidence. "
            f"This assessment is for informational purposes only and should be discussed "
            f"with a healthcare professional for proper evaluation and guidance."
        )
    
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
        logger.warning("Using fallback explanation due to LangChain generation failure")
        
        return {
            "summary": f"Risk assessment for {disease.replace('_', ' ').title()}",
            "probability_percent": round(probability * 100, 2),
            "confidence": confidence,
            "main_explanation": self._get_simple_explanation(disease, probability, confidence),
            "confidence_reasoning": self._get_confidence_reasoning(confidence),
            "contributing_factors": {"note": "Detailed analysis unavailable"},
            "educational_content": self._get_educational_content(disease),
            "disclaimer": self.medical_disclaimer,
            "generated_at": datetime.utcnow().isoformat(),
            "generated_by": "fallback_system",
            "agent": "LangChainExplanationAgent"
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
            "agent_type": "LangChainExplanationAgent",
            "framework": "LangChain",
            "ai_integration": "Google Gemini",
            "supported_confidence_levels": list(self.confidence_explanations.keys()),
            "features": [
                "LangChain-powered natural language explanations",
                "Confidence reasoning",
                "Contributing factor analysis",
                "Educational content",
                "Medical disclaimers",
                "Fallback explanations"
            ],
            "llm_available": bool(self.llm),
            "gemini_status": self.gemini_client.get_client_status() if hasattr(self, 'gemini_client') else None
        }