"""
Enhanced Severity Assessment Agent

Autonomous severity assessment agent with:
- LangChain-based intelligent severity scoring
- Web search for severity criteria and clinical guidelines
- Emergency indicator detection
- Autonomous escalation logic
- Monitoring and error handling
- Circuit breaker protection

Requirements: 1.1, 1.2, 1.3, 1.5, 5.4, 17.3, 1.6
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from .infrastructure.enhanced_base_agent import EnhancedBaseHealthAgent
from .infrastructure.config import AgentConfig
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger('health_ai.agents.severity')


class SeverityScoringAgent(EnhancedBaseHealthAgent):
    """
    Enhanced autonomous severity assessment agent.
    
    Provides intelligent severity scoring with:
    - LangChain-based severity assessment
    - Web search for clinical severity criteria
    - Emergency indicator detection
    - Autonomous escalation for critical situations
    - Monitoring and error handling
    
    Requirements:
    - 1.1: LangChain framework integration
    - 1.2: Enhanced BaseHealthAgent inheritance
    - 1.3: Web search for severity criteria
    - 1.5: Autonomous decision-making
    - 5.4: Escalation for critical situations
    - 17.3: Emergency detection
    - 1.6: Preserve functionality with enhancements
    """
    
    # Critical symptoms requiring immediate attention
    CRITICAL_SYMPTOMS = [
        "chest pain",
        "shortness of breath",
        "loss of consciousness",
        "severe headache",
        "difficulty breathing",
        "severe bleeding",
        "stroke symptoms",
        "heart attack",
        "severe abdominal pain",
        "sudden vision loss",
        "seizure",
        "severe allergic reaction"
    ]
    
    # Emergency keywords for escalation
    EMERGENCY_KEYWORDS = [
        "emergency",
        "urgent",
        "severe",
        "acute",
        "sudden",
        "intense",
        "unbearable",
        "life-threatening"
    ]
    
    # Severity thresholds
    CRITICAL_THRESHOLD = 12
    HIGH_THRESHOLD = 8
    MODERATE_THRESHOLD = 4
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the enhanced severity assessment agent.
        
        Args:
            config: Agent configuration (uses defaults if not provided)
        """
        super().__init__("SeverityAgent", config)
        
        # Create LangChain chains for severity assessment
        self.severity_assessment_chain = self._create_severity_assessment_chain()
        self.escalation_decision_chain = self._create_escalation_decision_chain()
        
        logger.info("Enhanced SeverityAgent initialized with autonomous capabilities")
    
    def _create_severity_assessment_chain(self):
        """Create LangChain chain for intelligent severity assessment."""
        if not self.llm:
            return None
        
        try:
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are a medical severity assessment expert.
                Analyze symptoms and patient data to provide severity insights.
                Consider: symptom severity, duration, progression, patient risk factors.
                Provide clear reasoning for your assessment.
                IMPORTANT: Do not provide specific diagnoses or treatment recommendations."""),
                ("human", """Assess the severity of this health situation:
                
                Symptoms: {symptoms}
                Patient Age: {age}
                Temperature: {temperature}
                Medical History: {medical_history}
                Prediction Probability: {probability}
                
                Provide a severity assessment with reasoning.""")
            ])
            
            return prompt_template | self.llm | StrOutputParser()
        except Exception as e:
            logger.error(f"Error creating severity assessment chain: {e}")
            return None
    
    def _create_escalation_decision_chain(self):
        """Create LangChain chain for escalation decisions."""
        if not self.llm:
            return None
        
        try:
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are an autonomous medical escalation decision agent.
                Determine if a situation requires immediate medical attention or escalation.
                Consider: emergency indicators, symptom severity, patient risk factors.
                Respond with: ESCALATE_EMERGENCY, ESCALATE_URGENT, MONITOR, or ROUTINE
                Include brief reasoning."""),
                ("human", """Evaluate this situation for escalation:
                
                Severity Score: {severity_score}
                Severity Level: {severity_level}
                Critical Symptoms Present: {critical_symptoms}
                Emergency Indicators: {emergency_indicators}
                Patient Context: {patient_context}
                
                Should this be escalated?""")
            ])
            
            return prompt_template | self.llm | StrOutputParser()
        except Exception as e:
            logger.error(f"Error creating escalation decision chain: {e}")
            return None
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for severity assessment with enhanced capabilities.
        
        Requirements:
        - 1.1: LangChain framework integration
        - 1.2: Enhanced BaseHealthAgent inheritance
        - 1.3: Web search for severity criteria
        - 1.5: Autonomous decision-making
        - 5.4: Escalation for critical situations
        - 17.3: Emergency detection
        - 1.6: Preserve functionality with enhancements
        
        Args:
            input_data: Dictionary containing:
                - symptoms: List of symptoms
                - probability: Model prediction probability
                - profile: Patient profile with age, temperature, medical history
                
        Returns:
            Severity assessment result with enhanced analysis
        """
        self.log_agent_action("assess_severity", {
            "symptom_count": len(input_data.get("symptoms", [])),
            "has_probability": "probability" in input_data
        })
        
        try:
            # Execute severity assessment with retry logic
            severity_result = self.execute_with_retry(
                lambda: self._perform_severity_assessment(input_data)
            )
            
            # Check for emergency indicators and escalate if needed
            severity_result = self._check_emergency_and_escalate(input_data, severity_result)
            
            # Search for clinical severity criteria if needed
            if severity_result.get("severity_level") in ["HIGH", "CRITICAL"]:
                severity_result = self._search_severity_criteria(input_data, severity_result)
            
            # Apply safety guardrails to any generated text
            if "ai_assessment" in severity_result:
                severity_result["ai_assessment"] = self.apply_safety_guardrails(
                    severity_result["ai_assessment"]
                )
            
            return self.format_agent_response(
                success=True,
                data=severity_result,
                message="Severity assessment completed with autonomous enhancements"
            )
            
        except Exception as e:
            logger.error(f"Severity assessment error: {str(e)}")
            return self.format_agent_response(
                success=False,
                message=f"Severity assessment error: {str(e)}",
                metadata={"error": str(e)}
            )
    
    def _perform_severity_assessment(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform core severity assessment logic.
        
        Maintains backward compatibility with original scoring while adding enhancements.
        
        Args:
            input_data: Input data with symptoms, probability, profile
            
        Returns:
            Severity assessment result
        """
        symptoms = input_data.get("symptoms", [])
        probability = input_data.get("probability", 0.0)
        profile = input_data.get("profile", {})
        
        # Calculate base severity score (original logic)
        score = self._calculate_base_score(symptoms, probability, profile)
        
        # Determine severity level
        severity_level = self._determine_severity_level(score)
        
        # Detect critical symptoms
        critical_symptoms_found = self._detect_critical_symptoms(symptoms)
        
        # Get AI-enhanced assessment if available
        ai_assessment = self._get_ai_assessment(symptoms, profile, probability)
        
        result = {
            "severity_score": score,
            "severity_level": severity_level,
            "critical_symptoms_detected": critical_symptoms_found,
            "assessment_timestamp": datetime.utcnow().isoformat(),
            "agent": "EnhancedSeverityAgent",
            "version": "enhanced"
        }
        
        if ai_assessment:
            result["ai_assessment"] = ai_assessment
        
        return result
    
    def _calculate_base_score(
        self,
        symptoms: List[str],
        probability: float,
        profile: Dict[str, Any]
    ) -> int:
        """
        Calculate base severity score (original logic preserved).
        
        Requirements: 1.6 - Preserve functionality
        
        Args:
            symptoms: List of symptoms
            probability: Model prediction probability
            profile: Patient profile
            
        Returns:
            Severity score
        """
        score = len(symptoms)
        
        # Check for critical symptoms
        text = " ".join(symptoms).lower()
        for red_flag in self.CRITICAL_SYMPTOMS:
            if red_flag in text:
                score += 4
        
        # Temperature scoring
        temp = profile.get("temperature")
        if isinstance(temp, (int, float)):
            if temp >= 40:
                score += 5
            elif temp >= 39:
                score += 3
        
        # Medical history scoring
        score += len(profile.get("past_health_conditions", [])) * 2
        
        # Probability scoring
        if probability >= 0.75:
            score += 3
        
        return score
    
    def _determine_severity_level(self, score: int) -> str:
        """
        Determine severity level from score.
        
        Args:
            score: Severity score
            
        Returns:
            Severity level string
        """
        if score >= self.CRITICAL_THRESHOLD:
            return "CRITICAL"
        elif score >= self.HIGH_THRESHOLD:
            return "HIGH"
        elif score >= self.MODERATE_THRESHOLD:
            return "MODERATE"
        else:
            return "LOW"
    
    def _detect_critical_symptoms(self, symptoms: List[str]) -> List[str]:
        """
        Detect critical symptoms in symptom list.
        
        Requirements: 17.3 - Emergency detection
        
        Args:
            symptoms: List of symptoms
            
        Returns:
            List of detected critical symptoms
        """
        text = " ".join(symptoms).lower()
        detected = []
        
        for critical_symptom in self.CRITICAL_SYMPTOMS:
            if critical_symptom in text:
                detected.append(critical_symptom)
        
        return detected
    
    def _get_ai_assessment(
        self,
        symptoms: List[str],
        profile: Dict[str, Any],
        probability: float
    ) -> Optional[str]:
        """
        Get AI-enhanced severity assessment using LangChain.
        
        Requirements: 1.1, 1.3 - LangChain integration
        
        Args:
            symptoms: List of symptoms
            profile: Patient profile
            probability: Model prediction probability
            
        Returns:
            AI assessment text or None
        """
        try:
            if not self.severity_assessment_chain:
                return None
            
            # Prepare input for LangChain
            assessment_input = {
                "symptoms": ", ".join(symptoms),
                "age": profile.get("age", "unknown"),
                "temperature": profile.get("temperature", "not provided"),
                "medical_history": ", ".join(profile.get("past_health_conditions", [])) or "none reported",
                "probability": f"{probability:.2%}"
            }
            
            # Get AI assessment
            ai_assessment = self.severity_assessment_chain.invoke(assessment_input)
            
            return ai_assessment.strip()
            
        except Exception as e:
            logger.error(f"Error getting AI assessment: {e}")
            return None
    
    def _check_emergency_and_escalate(
        self,
        input_data: Dict[str, Any],
        severity_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check for emergency indicators and make escalation decision.
        
        Requirements:
        - 5.4: Escalation for critical situations
        - 17.3: Emergency detection
        
        Args:
            input_data: Original input data
            severity_result: Current severity result
            
        Returns:
            Enhanced severity result with escalation decision
        """
        try:
            # Detect emergency indicators
            symptoms = input_data.get("symptoms", [])
            emergency_indicators = self._detect_emergency_indicators(symptoms)
            
            # Check if emergency detected
            has_emergency = (
                len(emergency_indicators) > 0 or
                severity_result.get("severity_level") == "CRITICAL" or
                len(severity_result.get("critical_symptoms_detected", [])) > 0
            )
            
            severity_result["emergency_indicators"] = emergency_indicators
            severity_result["requires_immediate_attention"] = has_emergency
            
            # Make autonomous escalation decision
            if self.escalation_decision_chain and has_emergency:
                escalation_decision = self._make_escalation_decision(
                    severity_result,
                    input_data.get("profile", {})
                )
                severity_result["escalation_decision"] = escalation_decision
                
                # Log escalation decision
                if "ESCALATE" in escalation_decision:
                    logger.warning(f"ESCALATION TRIGGERED: {escalation_decision}")
                    self.log_agent_action("escalate", {
                        "decision": escalation_decision,
                        "severity_level": severity_result["severity_level"]
                    })
            
            return severity_result
            
        except Exception as e:
            logger.error(f"Error in emergency check: {e}")
            return severity_result
    
    def _detect_emergency_indicators(self, symptoms: List[str]) -> List[str]:
        """
        Detect emergency keywords in symptoms.
        
        Args:
            symptoms: List of symptoms
            
        Returns:
            List of detected emergency indicators
        """
        text = " ".join(symptoms).lower()
        detected = []
        
        for keyword in self.EMERGENCY_KEYWORDS:
            if keyword in text:
                detected.append(keyword)
        
        return detected
    
    def _make_escalation_decision(
        self,
        severity_result: Dict[str, Any],
        patient_context: Dict[str, Any]
    ) -> str:
        """
        Make autonomous escalation decision using LangChain.
        
        Requirements: 1.5 - Autonomous decision-making
        
        Args:
            severity_result: Severity assessment result
            patient_context: Patient context information
            
        Returns:
            Escalation decision
        """
        try:
            if not self.escalation_decision_chain:
                # Fallback logic
                if severity_result.get("severity_level") == "CRITICAL":
                    return "ESCALATE_EMERGENCY: Critical severity detected"
                return "MONITOR: No escalation chain available"
            
            # Prepare context for decision
            decision_input = {
                "severity_score": severity_result.get("severity_score", 0),
                "severity_level": severity_result.get("severity_level", "UNKNOWN"),
                "critical_symptoms": ", ".join(severity_result.get("critical_symptoms_detected", [])) or "none",
                "emergency_indicators": ", ".join(severity_result.get("emergency_indicators", [])) or "none",
                "patient_context": f"Age: {patient_context.get('age', 'unknown')}, "
                                 f"Medical history: {len(patient_context.get('past_health_conditions', []))} conditions"
            }
            
            # Get escalation decision
            decision = self.escalation_decision_chain.invoke(decision_input)
            
            return decision.strip()
            
        except Exception as e:
            logger.error(f"Error making escalation decision: {e}")
            return "MONITOR: Error in decision process"
    
    def _search_severity_criteria(
        self,
        input_data: Dict[str, Any],
        severity_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Search web for clinical severity criteria and guidelines.
        
        Requirements: 1.3 - Web search for severity criteria
        
        Args:
            input_data: Original input data
            severity_result: Current severity result
            
        Returns:
            Enhanced severity result with search results
        """
        try:
            symptoms = input_data.get("symptoms", [])
            
            # Construct search query based on symptoms
            if symptoms:
                primary_symptom = symptoms[0] if len(symptoms) > 0 else "general"
                query = f"clinical severity criteria {primary_symptom} emergency guidelines"
            else:
                query = "clinical severity assessment criteria emergency medicine"
            
            # Perform web search
            search_results = self.search_web(query, filters={"source_type": "medical"})
            
            if search_results:
                severity_result["clinical_guidelines_sources"] = [
                    result.get_citation() for result in search_results[:3]
                ]
                logger.info(f"Found {len(search_results)} clinical severity guideline sources")
            
            return severity_result
            
        except Exception as e:
            logger.error(f"Error searching severity criteria: {e}")
            return severity_result
    
    def calculate(
        self,
        symptoms: List[str],
        probability: float,
        profile: Dict
    ) -> Dict:
        """
        Legacy method for backward compatibility.
        
        This method maintains the original interface while using enhanced processing.
        New code should use process() method.
        
        Requirements: 1.6 - Preserve functionality
        
        Args:
            symptoms: List of symptoms
            probability: Model prediction probability
            profile: Patient profile
            
        Returns:
            Severity assessment result
        """
        logger.info("Using legacy calculate() method - consider migrating to process()")
        
        # Convert to new format
        input_data = {
            "symptoms": symptoms,
            "probability": probability,
            "profile": profile
        }
        
        # Use enhanced processing
        result = self.process(input_data)
        
        # Extract data for legacy format
        if result.get("success"):
            data = result.get("data", {})
            return {
                "severity_score": data.get("severity_score", 0),
                "severity_level": data.get("severity_level", "UNKNOWN")
            }
        else:
            # Fallback to basic calculation
            score = self._calculate_base_score(symptoms, probability, profile)
            level = self._determine_severity_level(score)
            return {
                "severity_score": score,
                "severity_level": level
            }


# Alias for backward compatibility
SeverityAgent = SeverityScoringAgent
