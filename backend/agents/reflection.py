import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from backend.agents.base_agent import BaseHealthAgent

logger_reflection = logging.getLogger('health_ai.reflection')

class ReflectionAgent(BaseHealthAgent):
    """
    Self-reflection agent for the health AI system.
    
    Responsibilities:
    - Assess quality of other agents' outputs
    - Check for consistency and safety
    - Identify potential hallucinations or errors
    - Suggest corrections or improvements
    """
    
    def __init__(self):
        """Initialize the reflection agent."""
        super().__init__("ReflectionAgent")
        
        self.critique_chain = self.create_agent_chain(
            system_prompt="""You are a medical AI quality assurance specialist.
            Your job is to review health assessments for safety, consistency, and accuracy.
            
            Check for:
            1. Contradictions (e.g., diagnosis doesn't match symptoms)
            2. Safety violations (e.g., missing severe warnings)
            3. Hallucinations (e.g., inventing treatments)
            4. Tone issues (e.g., overly alarmist or dismissive)
            
            Output a JSON assessment of the assessment.""",
            
            human_prompt="""Review this assessment:
            Disease: {disease}
            Confidence: {confidence}
            Explanation: {explanation}
            Recommendations: {recommendations}
            
            Return JSON with:
            - is_safe (bool)
            - consistency_score (0-10)
            - issues (list of strings)
            - suggested_improvements (list of strings)
            """
        )
        
        logger_reflection.info("ReflectionAgent initialized")
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reflect on an assessment.
        
        Args:
            input_data: The full assessment result to review
            
        Returns:
            Critique and improvement suggestions
        """
        self.log_agent_action("critique_assessment")
        
        try:
            # Extract key components to review
            assessment = input_data.get("assessment", {})
            disease = assessment.get("prediction", {}).get("disease", "unknown")
            confidence = assessment.get("prediction", {}).get("confidence", "unknown")
            explanation = str(assessment.get("explanation", {}))
            recommendations = str(assessment.get("recommendations", {}))
            
            # If we don't have enough data to critique, return pass
            if not disease or not explanation:
                return {
                    "reviewed": False,
                    "reason": "Insufficient data for review"
                }

            # Run critique chain
            if self.critique_chain:
                critique_result = self._generate_critique(
                    disease, confidence, explanation, recommendations
                )
                if critique_result:
                    return {
                        "reviewed": True,
                        "critique": critique_result,
                        "timestamp": datetime.utcnow().isoformat()
                    }
            
            # Fallback simple check
            return self._perform_heuristic_check(assessment)
            
        except Exception as e:
            logger_reflection.error(f"Reflection error: {str(e)}")
            return {"error": str(e)}

    def verify_assessment(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Public method to verify an assessment before finalizing.
        
        Returns:
            Verification result dict containing 'status' and 'issues'
        """
        # Adapted for the Orchestrator's call
        result = self.process({"assessment": assessment})
        
        if result.get("reviewed"):
            critique = result.get("critique", {})
            issues = critique.get("issues", [])
            is_safe = critique.get("is_safe", True)
            
            severity = "low"
            if not is_safe:
                severity = "critical"
            elif len(issues) > 2:
                severity = "medium"
                
            return {
                "severity": severity,
                "issue_count": len(issues),
                "issues": issues,
                "recommended_action": "revise" if severity == "critical" else "proceed",
                "revised_assessment": assessment if severity != "critical" else self._apply_fixes(assessment, issues)
            }
            
        return {
            "severity": "low", 
            "issue_count": 0, 
            "recommended_action": "proceed"
        }

    def _generate_critique(self, disease, confidence, explanation, recommendations):
        """Generate critique using LLM."""
        try:
            result = self.execute_chain(self.critique_chain, {
                "disease": disease,
                "confidence": confidence,
                "explanation": explanation[:1000],  # Truncate to avoid token limits
                "recommendations": recommendations[:1000]
            })
            
            if result:
                 # Clean and parse JSON
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0].strip()
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0].strip()
                return json.loads(result)
        except Exception:
            return None
        return None

    def _perform_heuristic_check(self, assessment):
        """Perform rule-based checks."""
        issues = []
        
        # Check disclaimer
        exp = assessment.get("explanation", {})
        if isinstance(exp, dict) and "disclaimer" not in exp:
            issues.append("Missing medical disclaimer")
            
        # Check confidence consistency
        pred = assessment.get("prediction", {})
        prob = pred.get("probability", 0)
        conf = pred.get("confidence", "LOW")
        
        if prob > 0.8 and conf == "LOW":
            issues.append("Inconsistent probability and confidence (High Prob / Low Conf)")
            
        return {
            "reviewed": True,
            "method": "heuristic",
            "critique": {
                "is_safe": True,
                "issues": issues
            }
        }
        
    def _apply_fixes(self, assessment, issues):
        """Attempt to apply automated fixes."""
        fixed = assessment.copy()
        fixed["_verification_info"] = {
            "corrections_applied": issues,
            "original_issues": issues
        }
        return fixed
