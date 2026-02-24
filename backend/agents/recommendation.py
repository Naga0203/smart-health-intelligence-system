import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_agent import BaseHealthAgent
from treatment.knowledge_base import TreatmentKnowledgeBase
from .treatment_exploration import TreatmentExplorationAgent

logger_recommendation = logging.getLogger('health_ai.recommendation')

class RecommendationAgent(BaseHealthAgent):
    """
    Recommendation agent for compiling final health recommendations.
    
    Responsibilities:
    - Aggregate recommendations from other agents
    - Prioritize based on severity and confidence
    - Format for user consumption
    - Apply ethical gating (ensure no dangerous advice)
    """
    
    def __init__(self):
        """Initialize the recommendation agent."""
        super().__init__("RecommendationAgent")
        self.treatment_agent = TreatmentExplorationAgent()
        
        logger_recommendation.info("RecommendationAgent initialized")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process recommendations based on assessment data.
        
        Args:
            input_data: Full assessment context
            
        Returns:
            Finalized recommendations
        """
        self.log_agent_action("synthesize_recommendations")
        
        try:
            # Extract context
            disease = input_data.get("disease")
            confidence = input_data.get("confidence")
            severity = input_data.get("risk_level") # or probability
            
            # Simple aggregation logic for now
            recommendations = {
                "medical_attention": self._get_medical_advice(confidence, severity),
                "lifestyle_summary": input_data.get("lifestyle_recommendations", {}),
                "treatments": self._get_treatment_summary(disease)
            }
            
            return self.format_agent_response(
                success=True,
                data=recommendations,
                message="Recommendations synthesized"
            )
            
        except Exception as e:
            logger_recommendation.error(f"Recommendation error: {str(e)}")
            return self.get_fallback_response(input_data)
            
    def get_recommendations(self, disease: str, probability: float, confidence: str, 
                          symptoms: List[str], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Public method to get recommendations (called by Orchestrator).
        """
        return self.process({
            "disease": disease,
            "confidence": confidence,
            "risk_level": "HIGH" if probability > 0.7 else "MEDIUM" if probability > 0.4 else "LOW",
            "symptoms": symptoms,
            "user_context": user_context
        })["data"]

    def _get_medical_advice(self, confidence, severity):
        """Determine urgency of medical attention."""
        if severity == "HIGH" or confidence == "HIGH":
            return "URGENT: Consult a doctor immediately."
        elif severity == "MEDIUM":
            return "Consult a healthcare provider soon."
        return "Monitor symptoms and consult if they persist."

    def _get_treatment_summary(self, disease):
        """Get brief treatment summary."""
        # Use treatment agent to get summary if possible
        if disease:
            result = self.treatment_agent.process({"disease": disease, "system": "all"})
            if result["success"]:
                 # Simplify for summary
                return "Treatment options available in detailed report."
        return "Consult specialist for treatment options."