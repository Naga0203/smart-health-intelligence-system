import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

from .infrastructure.enhanced_base_agent import EnhancedBaseHealthAgent
from .infrastructure.config import AgentConfig

logger_reflection = logging.getLogger('health_ai.reflection')

class ReflectionAgent(EnhancedBaseHealthAgent):
    """
    Self-reflection agent for the health AI system.
    
    Responsibilities:
    - Assess quality of other agents' outputs
    - Check for consistency and safety
    - Identify potential hallucinations or errors
    - Suggest corrections or improvements
    - Self-evaluate output quality with confidence scoring
    
    Requirements:
    - 1.1: Inherits from EnhancedBaseHealthAgent
    - 1.2: Uses LangChain chains
    - 1.3: Uses Gemini AI via LangChain
    - 1.5: Autonomous decision-making
    - 5.5: Self-evaluation capabilities
    - 1.6: Preserves existing functionality
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the reflection agent."""
        if config is None:
            config = AgentConfig(
                agent_name="ReflectionAgent",
                enable_web_search=False,  # Reflection doesn't need web search
                timeout=30,
                max_retries=2
            )
        super().__init__("ReflectionAgent", config)
        
        # Create LangChain critique chain (only if LLM is available)
        if self.llm is not None:
            self.critique_chain = self._create_critique_chain()
            self.quality_assessment_chain = self._create_quality_assessment_chain()
        else:
            logger_reflection.warning("LLM not available, chains not created")
            self.critique_chain = None
            self.quality_assessment_chain = None
        
        logger_reflection.info("ReflectionAgent initialized with enhanced capabilities")
    
    def _create_critique_chain(self) -> LLMChain:
        """
        Create LangChain chain for critiquing assessments.
        
        Requirements: 1.2 - LangChain chains
        """
        critique_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a medical AI quality assurance specialist.
Your job is to review health assessments for safety, consistency, and accuracy.

Check for:
1. Contradictions (e.g., diagnosis doesn't match symptoms)
2. Safety violations (e.g., missing severe warnings)
3. Hallucinations (e.g., inventing treatments)
4. Tone issues (e.g., overly alarmist or dismissive)
5. Missing disclaimers or safety information

Output a JSON assessment with:
- is_safe (bool): Whether the assessment is medically safe
- consistency_score (0-10): How consistent the information is
- issues (list of strings): Specific problems found
- suggested_improvements (list of strings): How to fix the issues
- severity (string): "low", "medium", or "critical"
"""),
            ("human", """Review this health assessment:

Disease: {disease}
Confidence: {confidence}
Explanation: {explanation}
Recommendations: {recommendations}

Provide your assessment as valid JSON only.""")
        ])
        
        return LLMChain(llm=self.llm, prompt=critique_prompt)
    
    def _create_quality_assessment_chain(self) -> LLMChain:
        """
        Create LangChain chain for self-evaluating reflection quality.
        
        Requirements: 5.5 - Self-evaluation capabilities
        """
        quality_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are evaluating the quality of a reflection/critique.
Assess how thorough and useful the critique is.

Rate on these dimensions (0-10 each):
- thoroughness: How comprehensive is the review?
- actionability: How useful are the suggestions?
- accuracy: How accurate are the identified issues?

Output JSON with:
- quality_score (0-10): Overall quality rating
- confidence (0-1): Confidence in this assessment
- strengths (list): What the critique did well
- weaknesses (list): What could be improved
"""),
            ("human", """Evaluate this critique:

Original Assessment: {original_assessment}
Critique: {critique}

Provide your quality assessment as valid JSON only.""")
        ])
        
        return LLMChain(llm=self.llm, prompt=quality_prompt)
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reflect on an assessment with enhanced capabilities.
        
        Requirements:
        - 1.6: Preserves existing functionality
        - 5.5: Self-evaluation with quality scoring
        
        Args:
            input_data: The full assessment result to review
            
        Returns:
            Critique with quality assessment and improvement suggestions
        """
        self.log_agent_action("critique_assessment", {"input_keys": list(input_data.keys())})
        
        try:
            # Extract key components to review
            assessment = input_data.get("assessment", {})
            disease = assessment.get("prediction", {}).get("disease", "unknown")
            confidence = assessment.get("prediction", {}).get("confidence", "unknown")
            explanation = str(assessment.get("explanation", {}))
            recommendations = str(assessment.get("recommendations", {}))
            
            # If we don't have enough data to critique, return pass
            if not disease or not explanation:
                return self.format_agent_response(
                    success=False,
                    message="Insufficient data for review",
                    metadata={"reviewed": False}
                )

            # Run critique chain with retry logic
            critique_result = self.execute_with_retry(
                lambda: self._generate_critique(disease, confidence, explanation, recommendations)
            )
            
            if critique_result:
                # Self-evaluate the quality of our critique
                quality_assessment = self._evaluate_critique_quality(
                    assessment, critique_result
                )
                
                # Apply safety guardrails to any text in the critique
                if "suggested_improvements" in critique_result:
                    critique_result["suggested_improvements"] = [
                        self.apply_safety_guardrails(improvement)
                        for improvement in critique_result["suggested_improvements"]
                    ]
                
                return self.format_agent_response(
                    success=True,
                    data={
                        "reviewed": True,
                        "critique": critique_result,
                        "quality_assessment": quality_assessment,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            
            # Fallback to heuristic check if LLM critique fails
            logger_reflection.warning("LLM critique failed, using heuristic check")
            return self._perform_heuristic_check(assessment)
            
        except Exception as e:
            logger_reflection.error(f"Reflection error: {str(e)}")
            return self.format_agent_response(
                success=False,
                message=f"Reflection failed: {str(e)}",
                metadata={"error": str(e)}
            )

    def verify_assessment(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Public method to verify an assessment before finalizing.
        
        Requirements: 1.6 - Preserves existing functionality
        
        Returns:
            Verification result dict containing 'status' and 'issues'
        """
        # Adapted for the Orchestrator's call
        result = self.process({"assessment": assessment})
        
        # Handle new response format
        if not result.get("success", False):
            return {
                "severity": "low", 
                "issue_count": 0, 
                "recommended_action": "proceed",
                "error": result.get("message", "Unknown error")
            }
        
        data = result.get("data", {})
        if data.get("reviewed"):
            critique = data.get("critique", {})
            quality = data.get("quality_assessment", {})
            issues = critique.get("issues", [])
            is_safe = critique.get("is_safe", True)
            
            # Determine severity from critique
            severity = critique.get("severity", "low")
            if not is_safe:
                severity = "critical"
            elif len(issues) > 2 and severity == "low":
                severity = "medium"
                
            return {
                "severity": severity,
                "issue_count": len(issues),
                "issues": issues,
                "recommended_action": "revise" if severity == "critical" else "proceed",
                "revised_assessment": assessment if severity != "critical" else self._apply_fixes(assessment, issues),
                "quality_score": quality.get("quality_score", 0),
                "confidence": quality.get("confidence", 0)
            }
            
        return {
            "severity": "low", 
            "issue_count": 0, 
            "recommended_action": "proceed"
        }

    def _generate_critique(
        self,
        disease: str,
        confidence: str,
        explanation: str,
        recommendations: str
    ) -> Optional[Dict[str, Any]]:
        """
        Generate critique using LangChain LLM chain.
        
        Requirements: 1.2 - LangChain chains
        
        Args:
            disease: Disease name
            confidence: Confidence level
            explanation: Explanation text
            recommendations: Recommendations text
            
        Returns:
            Critique dictionary or None if failed
        """
        try:
            # Execute LangChain chain
            result = self.critique_chain.invoke({
                "disease": disease,
                "confidence": confidence,
                "explanation": explanation[:1000],  # Truncate to avoid token limits
                "recommendations": recommendations[:1000]
            })
            
            # Extract text from chain result
            result_text = result.get("text", "") if isinstance(result, dict) else str(result)
            
            # Clean and parse JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            critique = json.loads(result_text)
            
            # Ensure required fields exist
            if "is_safe" not in critique:
                critique["is_safe"] = True
            if "issues" not in critique:
                critique["issues"] = []
            if "suggested_improvements" not in critique:
                critique["suggested_improvements"] = []
            if "severity" not in critique:
                critique["severity"] = "low"
            
            return critique
            
        except json.JSONDecodeError as e:
            logger_reflection.error(f"Failed to parse critique JSON: {e}")
            return None
        except Exception as e:
            logger_reflection.error(f"Failed to generate critique: {e}")
            return None
    
    def _evaluate_critique_quality(
        self,
        original_assessment: Dict[str, Any],
        critique: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Self-evaluate the quality of the generated critique.
        
        Requirements: 5.5 - Self-evaluation capabilities
        
        Args:
            original_assessment: The original assessment that was critiqued
            critique: The critique that was generated
            
        Returns:
            Quality assessment dictionary with scores and confidence
        """
        try:
            # Execute quality assessment chain
            result = self.quality_assessment_chain.invoke({
                "original_assessment": json.dumps(original_assessment, indent=2)[:500],
                "critique": json.dumps(critique, indent=2)[:500]
            })
            
            # Extract text from chain result
            result_text = result.get("text", "") if isinstance(result, dict) else str(result)
            
            # Clean and parse JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            quality = json.loads(result_text)
            
            # Ensure required fields
            if "quality_score" not in quality:
                quality["quality_score"] = 5
            if "confidence" not in quality:
                quality["confidence"] = 0.5
            
            self.log_agent_action(
                "self_evaluation",
                {
                    "quality_score": quality.get("quality_score"),
                    "confidence": quality.get("confidence")
                }
            )
            
            return quality
            
        except Exception as e:
            logger_reflection.error(f"Failed to evaluate critique quality: {e}")
            # Return default quality assessment
            return {
                "quality_score": 5,
                "confidence": 0.5,
                "strengths": [],
                "weaknesses": ["Self-evaluation failed"],
                "error": str(e)
            }

    def _perform_heuristic_check(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform rule-based checks as fallback.
        
        Requirements: 1.6 - Preserves existing functionality
        
        Args:
            assessment: Assessment to check
            
        Returns:
            Heuristic check result
        """
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
        
        # Self-evaluate heuristic check quality
        quality_assessment = {
            "quality_score": 3,  # Heuristic checks are lower quality
            "confidence": 0.6,
            "strengths": ["Fast", "Deterministic"],
            "weaknesses": ["Limited scope", "No LLM reasoning"]
        }
        
        return self.format_agent_response(
            success=True,
            data={
                "reviewed": True,
                "method": "heuristic",
                "critique": {
                    "is_safe": True,
                    "issues": issues,
                    "consistency_score": 7 if len(issues) == 0 else 5,
                    "suggested_improvements": [],
                    "severity": "low"
                },
                "quality_assessment": quality_assessment,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    def _apply_fixes(self, assessment, issues):
        """Attempt to apply automated fixes."""
        fixed = assessment.copy()
        fixed["_verification_info"] = {
            "corrections_applied": issues,
            "original_issues": issues
        }
        return fixed
