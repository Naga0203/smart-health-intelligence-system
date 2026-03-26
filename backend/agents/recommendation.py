"""
Recommendation Agent - Migrated to Enhanced Architecture.

Provides personalized health recommendations based on clinical guidelines,
user profile, and comprehensive health assessment data.

Requirements: 1.1, 1.2, 1.3, 1.5, 2.3, 15.1, 15.2, 15.3, 15.5, 15.6, 15.7, 15.8, 1.6
"""

import logging
from typing import Dict, Any, Optional, List
import json

from .infrastructure.enhanced_base_agent import EnhancedBaseHealthAgent
from .infrastructure.config import AgentConfig

logger = logging.getLogger('health_ai.recommendation')


class RecommendationAgent(EnhancedBaseHealthAgent):
    """
    AI agent for generating personalized health recommendations.
    
    Migrated to use:
    - Enhanced BaseHealthAgent with autonomous capabilities
    - Web search for current clinical guidelines
    - Personalization based on user profile (age, gender, medical history)
    - Contraindication searches specific to user profile
    - Recommendation prioritization by clinical importance
    - Actionable steps for each recommendation
    - Medication conflict detection
    - Source citations
    - Safety guardrails
    
    Requirements:
    - 1.1, 1.2, 1.3: LangChain framework with Gemini AI
    - 1.5: Autonomous decision-making
    - 1.6: Preserve existing functionality
    - 2.3: Web search for clinical guidelines
    - 15.1: Search for current clinical guidelines
    - 15.2: Personalize based on user profile
    - 15.3: Search for contraindications
    - 15.5: Prioritize recommendations
    - 15.6: Include actionable steps
    - 15.7: Cite sources
    - 15.8: Flag medication conflicts
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the recommendation agent.
        
        Args:
            config: Agent configuration (uses defaults if not provided)
        """
        # Initialize with enhanced base agent
        if config is None:
            config = AgentConfig(
                agent_name="RecommendationAgent",
                enable_web_search=True,
                enable_caching=True,
                monitoring_enabled=True
            )
        
        super().__init__("RecommendationAgent", config)
        
        # Create LangChain chain for recommendation generation
        self.recommendation_chain = self.create_agent_chain(
            system_prompt="""You are an expert clinical decision support system specializing in evidence-based health recommendations.
            Your role is to synthesize comprehensive health assessment data and provide personalized, prioritized recommendations.
            
            Core Responsibilities:
            1. Analyze health assessment data (disease risk, severity, symptoms, lab results)
            2. Search for current clinical practice guidelines
            3. Personalize recommendations based on patient profile (age, gender, medical history, current medications)
            4. Identify contraindications and medication conflicts
            5. Prioritize recommendations by clinical importance and evidence strength
            6. Provide actionable steps for each recommendation
            7. Cite all sources and evidence levels
            
            Guidelines:
            - Base all recommendations on current clinical guidelines and evidence
            - Consider patient-specific factors (age, gender, comorbidities, medications)
            - Flag potential medication conflicts and contraindications
            - Prioritize by urgency and clinical importance (URGENT, HIGH, MEDIUM, LOW)
            - Provide clear, actionable steps
            - Include evidence levels (Level A: Strong evidence, Level B: Moderate, Level C: Limited)
            - Cite sources for all recommendations
            - Apply safety guardrails (no diagnoses, no specific dosages)
            - Emphasize consulting healthcare professionals for medical decisions
            
            CRITICAL: This is clinical decision support, not medical advice. Always recommend professional consultation for medical decisions.
            """,
            
            human_prompt="""Generate personalized health recommendations based on comprehensive assessment:

PATIENT PROFILE:
- Age: {age} years
- Gender: {gender}
- Medical History: {medical_history}
- Current Medications: {current_medications}
- Allergies: {allergies}

HEALTH ASSESSMENT:
- Primary Condition: {disease}
- Risk Level: {risk_level}
- Confidence: {confidence}
- Severity: {severity}
- Symptoms: {symptoms}
- Lab Results: {lab_results}

CLINICAL GUIDELINES CONTEXT:
{guidelines_context}

CONTRAINDICATIONS CONTEXT:
{contraindications_context}

MEDICATION INTERACTIONS:
{medication_interactions}

Generate a structured JSON response with prioritized recommendations:
{{
  "urgent_actions": [
    {{
      "recommendation": "specific urgent action",
      "rationale": "why this is urgent",
      "actionable_steps": ["step 1", "step 2", ...],
      "evidence_level": "A/B/C",
      "source": "citation",
      "priority": "URGENT"
    }}
  ],
  "high_priority": [
    {{
      "recommendation": "specific high priority recommendation",
      "rationale": "clinical reasoning",
      "actionable_steps": ["step 1", "step 2", ...],
      "evidence_level": "A/B/C",
      "source": "citation",
      "priority": "HIGH",
      "contraindications": ["if any"],
      "personalization_note": "how this is tailored to patient"
    }}
  ],
  "medium_priority": [
    {{
      "recommendation": "specific medium priority recommendation",
      "rationale": "clinical reasoning",
      "actionable_steps": ["step 1", "step 2", ...],
      "evidence_level": "A/B/C",
      "source": "citation",
      "priority": "MEDIUM"
    }}
  ],
  "low_priority": [
    {{
      "recommendation": "specific low priority recommendation",
      "rationale": "clinical reasoning",
      "actionable_steps": ["step 1", "step 2", ...],
      "evidence_level": "A/B/C",
      "source": "citation",
      "priority": "LOW"
    }}
  ],
  "medication_conflicts": [
    {{
      "conflict": "description of conflict",
      "medications_involved": ["med1", "med2"],
      "severity": "HIGH/MEDIUM/LOW",
      "recommendation": "what to do",
      "source": "citation"
    }}
  ],
  "contraindications": [
    {{
      "item": "medication/treatment/activity",
      "reason": "why contraindicated for this patient",
      "severity": "HIGH/MEDIUM/LOW",
      "source": "citation"
    }}
  ],
  "follow_up": {{
    "timeline": "when to follow up",
    "monitoring": ["what to monitor"],
    "red_flags": ["warning signs to watch for"]
  }},
  "summary": "brief summary of key recommendations",
  "disclaimer": "appropriate medical disclaimer"
}}

Ensure all recommendations are evidence-based, personalized, and include clear actionable steps."""
        )
        
        logger.info("RecommendationAgent initialized with enhanced architecture")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process health assessment data and generate personalized recommendations.
        
        Requirements: 1.6 - Preserve existing functionality
        
        Args:
            input_data: Dictionary containing:
                - disease: Primary condition (required)
                - confidence: Confidence level (optional)
                - risk_level: Risk level (optional)
                - severity: Severity assessment (optional)
                - symptoms: List of symptoms (optional)
                - lab_results: Lab test results (optional)
                - user_context: User profile data (optional)
                    - age: Patient age
                    - gender: Patient gender
                    - medical_history: Past conditions
                    - current_medications: List of current medications
                    - allergies: List of allergies
                
        Returns:
            Dictionary with personalized recommendations
        """
        return self.process_with_monitoring(input_data)
    
    def _process_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal processing method called by process_with_monitoring.
        
        Args:
            input_data: Health assessment data
            
        Returns:
            Dictionary with recommendations
        """
        # Validate request
        if not self._validate_request(input_data):
            return self.format_agent_response(
                success=False,
                message="Invalid request: 'disease' is required"
            )
        
        disease = input_data.get("disease", "").strip()
        user_context = input_data.get("user_context", {})
        
        self.log_agent_action("generate_recommendations", {
            "disease": disease,
            "age": user_context.get("age"),
            "has_medications": bool(user_context.get("current_medications"))
        })
        
        try:
            # Execute with retry logic
            recommendations = self.execute_with_retry(
                lambda: self._generate_recommendations(input_data)
            )
            
            if recommendations:
                # Apply safety guardrails
                recommendations = self._apply_safety_guardrails(recommendations)
                
                return self.format_agent_response(
                    success=True,
                    data=recommendations,
                    message="Personalized recommendations generated successfully"
                )
            else:
                # Fallback to basic recommendations
                return self._generate_fallback_recommendations(input_data)
                
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}", exc_info=True)
            return self._generate_fallback_recommendations(input_data)
    
    def _validate_request(self, input_data: Dict[str, Any]) -> bool:
        """Validate that required fields are present."""
        return bool(input_data.get("disease"))
    
    def _generate_recommendations(self, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate personalized recommendations using LangChain with web search.
        
        Requirements:
        - 15.1: Search for current clinical guidelines
        - 15.2: Personalize based on user profile
        - 15.3: Search for contraindications
        - 15.5: Prioritize recommendations
        - 15.6: Include actionable steps
        - 15.7: Cite sources
        - 15.8: Flag medication conflicts
        
        Args:
            input_data: Health assessment data
            
        Returns:
            Dictionary with recommendations or None if generation fails
        """
        disease = input_data.get("disease", "").strip()
        user_context = input_data.get("user_context", {})
        
        # Extract patient profile
        age = user_context.get("age", "unknown")
        gender = user_context.get("gender", "unknown")
        medical_history = user_context.get("medical_history", "Not provided")
        current_medications = user_context.get("current_medications", [])
        allergies = user_context.get("allergies", [])
        
        # Extract assessment data
        risk_level = input_data.get("risk_level", "MEDIUM")
        confidence = input_data.get("confidence", "MEDIUM")
        severity = input_data.get("severity", "MEDIUM")
        symptoms = input_data.get("symptoms", [])
        lab_results = input_data.get("lab_results", "Not provided")
        
        logger.info(f"Generating recommendations for {disease} with web search for guidelines")
        
        # Step 1: Search for current clinical guidelines
        # Requirement 15.1: Search for current clinical guidelines
        guidelines_context = self._search_clinical_guidelines(disease, age, gender)
        
        # Step 2: Search for contraindications specific to patient profile
        # Requirement 15.3: Search for contraindications
        contraindications_context = self._search_contraindications(
            disease, age, gender, medical_history, current_medications, allergies
        )
        
        # Step 3: Check for medication interactions
        # Requirement 15.8: Flag medication conflicts
        medication_interactions = self._check_medication_interactions(current_medications, disease)
        
        # Step 4: Generate recommendations using LangChain
        try:
            # Prepare context for LangChain
            chain_input = {
                "age": age,
                "gender": gender,
                "medical_history": medical_history,
                "current_medications": ", ".join(current_medications) if current_medications else "None",
                "allergies": ", ".join(allergies) if allergies else "None",
                "disease": disease,
                "risk_level": risk_level,
                "confidence": confidence,
                "severity": severity,
                "symptoms": ", ".join(symptoms) if symptoms else "None",
                "lab_results": lab_results,
                "guidelines_context": guidelines_context,
                "contraindications_context": contraindications_context,
                "medication_interactions": medication_interactions
            }
            
            # Execute chain with circuit breaker
            if not self.recommendation_chain:
                logger.warning("recommendation_chain is None (LLM unavailable), using fallback")
                return None

            response = self.execute_with_circuit_breaker(
                lambda: self.recommendation_chain.invoke(chain_input)
            )
            
            # Parse JSON response
            recommendations = self._parse_llm_response(response)
            
            if recommendations:
                # Add metadata
                recommendations["generated_at"] = self._get_timestamp()
                recommendations["agent"] = self.agent_name
                recommendations["personalized_for"] = {
                    "age": age,
                    "gender": gender,
                    "has_medical_history": bool(medical_history and medical_history != "Not provided"),
                    "has_medications": bool(current_medications)
                }
                
                logger.info(f"Successfully generated recommendations for {disease}")
                return recommendations
            else:
                logger.warning("Failed to parse LLM response")
                return None
                
        except Exception as e:
            logger.error(f"Error in recommendation generation: {str(e)}", exc_info=True)
            return None
    
    def _search_clinical_guidelines(
        self, 
        disease: str, 
        age: Any, 
        gender: str
    ) -> str:
        """
        Search for current clinical practice guidelines.
        
        Requirement 15.1: Search for current clinical guidelines
        
        Args:
            disease: The condition
            age: Patient age
            gender: Patient gender
            
        Returns:
            Formatted context string with guidelines
        """
        if not self.web_search_tool:
            return "Web search not available"
        
        try:
            # Search for clinical guidelines
            query = f"clinical practice guidelines {disease} treatment management {age} years {gender}"
            
            search_results = self.search_web(
                query=query,
                filters={
                    "source_types": ["clinical_guidelines", "medical_literature"],
                    "max_results": 5
                }
            )
            
            if search_results:
                # Format guidelines context
                context_parts = []
                for result in search_results[:3]:  # Top 3 results
                    context_parts.append(
                        f"- {result.title}\n"
                        f"  Source: {result.url}\n"
                        f"  Summary: {result.snippet}\n"
                    )
                
                return "\n".join(context_parts)
            else:
                return "No specific clinical guidelines found"
                
        except Exception as e:
            logger.error(f"Error searching clinical guidelines: {str(e)}")
            return "Clinical guidelines search unavailable"
    
    def _search_contraindications(
        self,
        disease: str,
        age: Any,
        gender: str,
        medical_history: str,
        current_medications: List[str],
        allergies: List[str]
    ) -> str:
        """
        Search for contraindications specific to patient profile.
        
        Requirement 15.3: Search for contraindications
        
        Args:
            disease: The condition
            age: Patient age
            gender: Patient gender
            medical_history: Past medical conditions
            current_medications: Current medications
            allergies: Known allergies
            
        Returns:
            Formatted context string with contraindications
        """
        if not self.web_search_tool:
            return "Web search not available"
        
        try:
            # Build contraindication search query
            query_parts = [f"{disease} contraindications"]
            
            if current_medications:
                query_parts.append(f"with {' '.join(current_medications[:3])}")
            
            if allergies:
                query_parts.append(f"allergies {' '.join(allergies[:2])}")
            
            query = " ".join(query_parts)
            
            search_results = self.search_web(
                query=query,
                filters={
                    "source_types": ["medical_literature", "drug_information"],
                    "max_results": 5
                }
            )
            
            if search_results:
                # Format contraindications context
                context_parts = []
                for result in search_results[:3]:
                    context_parts.append(
                        f"- {result.title}\n"
                        f"  Source: {result.url}\n"
                        f"  Details: {result.snippet}\n"
                    )
                
                return "\n".join(context_parts)
            else:
                return "No specific contraindications found"
                
        except Exception as e:
            logger.error(f"Error searching contraindications: {str(e)}")
            return "Contraindications search unavailable"
    
    def _check_medication_interactions(
        self,
        current_medications: List[str],
        disease: str
    ) -> str:
        """
        Check for medication interactions.
        
        Requirement 15.8: Flag medication conflicts
        
        Args:
            current_medications: List of current medications
            disease: The condition
            
        Returns:
            Formatted context string with interaction information
        """
        if not current_medications or not self.web_search_tool:
            return "No medications to check" if not current_medications else "Web search not available"
        
        try:
            # Search for drug interactions
            medications_str = " ".join(current_medications[:5])  # Limit to 5 medications
            query = f"drug interactions {medications_str} {disease}"
            
            search_results = self.search_web(
                query=query,
                filters={
                    "source_types": ["drug_information"],
                    "max_results": 5
                }
            )
            
            if search_results:
                # Format interactions context
                context_parts = []
                for result in search_results[:3]:
                    context_parts.append(
                        f"- {result.title}\n"
                        f"  Source: {result.url}\n"
                        f"  Details: {result.snippet}\n"
                    )
                
                return "\n".join(context_parts)
            else:
                return "No significant drug interactions found"
                
        except Exception as e:
            logger.error(f"Error checking medication interactions: {str(e)}")
            return "Medication interaction check unavailable"
    
    def _parse_llm_response(self, response: Any) -> Optional[Dict[str, Any]]:
        """
        Parse LLM response to extract recommendations.
        
        Args:
            response: LLM response object
            
        Returns:
            Parsed recommendations dictionary or None
        """
        try:
            # Extract content from response
            if hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, dict) and 'content' in response:
                content = response['content']
            elif isinstance(response, str):
                content = response
            else:
                logger.error(f"Unexpected response type: {type(response)}")
                return None
            
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            # Parse JSON
            recommendations = json.loads(content)
            return recommendations
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.debug(f"Response content: {content[:500]}")
            return None
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return None
    
    def _apply_safety_guardrails(self, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply safety guardrails to recommendations.
        
        Args:
            recommendations: Generated recommendations
            
        Returns:
            Recommendations with safety guardrails applied
        """
        try:
            # Apply safety guardrails to all text fields
            for priority_level in ["urgent_actions", "high_priority", "medium_priority", "low_priority"]:
                if priority_level in recommendations:
                    for rec in recommendations[priority_level]:
                        if "recommendation" in rec:
                            rec["recommendation"] = self.apply_safety_guardrails(rec["recommendation"])
                        if "rationale" in rec:
                            rec["rationale"] = self.apply_safety_guardrails(rec["rationale"])
            
            # Apply to summary
            if "summary" in recommendations:
                recommendations["summary"] = self.apply_safety_guardrails(recommendations["summary"])
            
            # Ensure disclaimer is present
            if "disclaimer" not in recommendations or not recommendations["disclaimer"]:
                recommendations["disclaimer"] = self._get_medical_disclaimer()
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error applying safety guardrails: {str(e)}")
            return recommendations
    
    def _generate_fallback_recommendations(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate basic fallback recommendations when main generation fails.
        
        Args:
            input_data: Health assessment data
            
        Returns:
            Basic recommendations
        """
        disease = input_data.get("disease", "unknown condition")
        risk_level = input_data.get("risk_level", "MEDIUM")
        severity = input_data.get("severity", "MEDIUM")
        
        # Determine urgency
        is_urgent = risk_level == "HIGH" or severity == "HIGH"
        
        recommendations = {
            "urgent_actions": [],
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
            "medication_conflicts": [],
            "contraindications": [],
            "follow_up": {
                "timeline": "Consult healthcare provider soon",
                "monitoring": ["Monitor symptoms", "Track any changes"],
                "red_flags": ["Worsening symptoms", "New symptoms", "Severe pain"]
            },
            "summary": f"Recommendations for {disease}. Please consult a healthcare professional for personalized medical advice.",
            "disclaimer": self._get_medical_disclaimer(),
            "generated_at": self._get_timestamp(),
            "agent": self.agent_name,
            "fallback": True
        }
        
        if is_urgent:
            recommendations["urgent_actions"].append({
                "recommendation": "Seek immediate medical attention",
                "rationale": f"High risk level detected for {disease}",
                "actionable_steps": [
                    "Contact your healthcare provider immediately",
                    "Visit emergency department if symptoms worsen",
                    "Do not delay seeking medical care"
                ],
                "evidence_level": "A",
                "source": "Clinical best practices",
                "priority": "URGENT"
            })
        else:
            recommendations["high_priority"].append({
                "recommendation": "Schedule appointment with healthcare provider",
                "rationale": f"Professional evaluation needed for {disease}",
                "actionable_steps": [
                    "Contact your doctor's office",
                    "Prepare list of symptoms and questions",
                    "Bring any relevant medical records"
                ],
                "evidence_level": "A",
                "source": "Clinical best practices",
                "priority": "HIGH"
            })
        
        recommendations["medium_priority"].append({
            "recommendation": "Monitor symptoms and maintain health records",
            "rationale": "Tracking helps healthcare providers make better decisions",
            "actionable_steps": [
                "Keep a symptom diary",
                "Note any changes in condition",
                "Record any new symptoms"
            ],
            "evidence_level": "B",
            "source": "Clinical best practices",
            "priority": "MEDIUM"
        })
        
        return self.format_agent_response(
            success=True,
            data=recommendations,
            message="Basic recommendations generated (fallback mode)"
        )
    
    def _get_medical_disclaimer(self) -> str:
        """Get standard medical disclaimer."""
        return (
            "IMPORTANT: This information is for educational purposes only and does not constitute medical advice. "
            "Always consult with qualified healthcare professionals for diagnosis, treatment, and medical decisions. "
            "Do not start, stop, or change any medications without consulting your doctor. "
            "In case of emergency, call emergency services immediately."
        )
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    # Legacy method for backward compatibility
    def get_recommendations(
        self,
        disease: str,
        probability: float,
        confidence: str,
        symptoms: List[str],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Legacy method for backward compatibility with orchestrator.
        
        Requirement 1.6: Preserve existing functionality
        
        Args:
            disease: Primary condition
            probability: Disease probability
            confidence: Confidence level
            symptoms: List of symptoms
            user_context: User profile data
            
        Returns:
            Recommendations data
        """
        # Convert to new format
        risk_level = "HIGH" if probability > 0.7 else "MEDIUM" if probability > 0.4 else "LOW"
        
        result = self.process({
            "disease": disease,
            "confidence": confidence,
            "risk_level": risk_level,
            "symptoms": symptoms,
            "user_context": user_context
        })
        
        return result.get("data", {})
