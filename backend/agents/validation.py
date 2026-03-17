import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from .infrastructure.enhanced_base_agent import EnhancedBaseHealthAgent
from .infrastructure.config import AgentConfig
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger_validation = logging.getLogger('health_ai.validation')

class LangChainValidationAgent(EnhancedBaseHealthAgent):
    """
    Enhanced autonomous validation agent for health intelligence system.
    
    Provides first-line defense against incomplete or unsafe inputs with:
    - LangChain-based intelligent validation
    - Web search for validation criteria
    - Autonomous decision-making
    - Monitoring and error handling
    - Circuit breaker protection
    
    Requirements: 1.1, 1.2, 1.3, 1.5, 1.6
    """
    
    # Required fields as per Requirements 1.2
    REQUIRED_FIELDS = ["age", "gender", "symptoms"]
    
    # Valid gender options
    VALID_GENDERS = ["male", "female", "other"]
    
    # Age validation bounds
    MIN_AGE = 1
    MAX_AGE = 120
    
    # Symptom validation
    MAX_SYMPTOMS_PER_REQUEST = 20
    MIN_SYMPTOM_LENGTH = 2
    MAX_SYMPTOM_LENGTH = 100
    
    # Unsafe patterns to filter out
    UNSAFE_PATTERNS = [
        r'<script.*?>.*?</script>',  # Script tags
        r'javascript:',              # JavaScript URLs
        r'on\w+\s*=',               # Event handlers
        r'<.*?>',                   # HTML tags
        r'(sql\s+)?(select|insert|update|delete|drop|create|alter|truncate)\s+(table|database|from|into)',  # SQL injection
        r';\s*(drop|delete|update|insert)',  # SQL injection after semicolon
    ]
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the enhanced validation agent.
        
        Args:
            config: Agent configuration (uses defaults if not provided)
        """
        # Initialize with enhanced base agent capabilities
        super().__init__("ValidationAgent", config)
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.UNSAFE_PATTERNS]
        
        # Create LangChain chain for intelligent validation feedback
        self.validation_feedback_chain = self._create_validation_feedback_chain()
        
        # Create chain for autonomous validation decisions
        self.validation_decision_chain = self._create_validation_decision_chain()
        
        logger_validation.info("Enhanced ValidationAgent initialized with autonomous capabilities")
    
    def _create_validation_feedback_chain(self):
        """Create LangChain chain for validation feedback."""
        if not self.llm:
            return None
        
        try:
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are a validation agent for a health assessment system. 
                Your role is to provide clear, helpful feedback about input validation issues.
                Always be supportive and guide users on how to correct their input.
                Keep responses concise and actionable."""),
                ("human", """The user input has validation issues: {validation_issues}
                Please provide a clear, helpful message explaining what needs to be corrected.
                Be specific about what the user should do to fix the issues.""")
            ])
            
            return prompt_template | self.llm | StrOutputParser()
        except Exception as e:
            logger_validation.error(f"Error creating validation feedback chain: {e}")
            return None
    
    def _create_validation_decision_chain(self):
        """Create LangChain chain for autonomous validation decisions."""
        if not self.llm:
            return None
        
        try:
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are an autonomous validation decision agent.
                Analyze validation scenarios and decide the best course of action.
                Consider: severity of issues, user experience, and system safety.
                Respond with one of: ACCEPT, REJECT, REQUEST_CLARIFICATION, SEARCH_CRITERIA"""),
                ("human", """Validation scenario:
                Input: {input_summary}
                Issues found: {issues}
                Context: {context}
                
                What action should be taken?""")
            ])
            
            return prompt_template | self.llm | StrOutputParser()
        except Exception as e:
            logger_validation.error(f"Error creating validation decision chain: {e}")
            return None
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for validation with enhanced capabilities.
        
        Uses autonomous decision-making, web search for criteria, and monitoring.
        
        Requirements:
        - 1.1: LangChain framework integration
        - 1.2: Enhanced BaseHealthAgent inheritance
        - 1.3: LangChain chains for validation
        - 1.5: Autonomous decision-making
        - 1.6: Preserve functionality with enhancements
        
        Args:
            input_data: User input to validate
            
        Returns:
            Validation result with enhanced feedback and monitoring
        """
        self.log_agent_action("validate_input", {"fields_count": len(input_data)})
        
        try:
            # Execute validation with retry logic
            validation_result = self.execute_with_retry(
                lambda: self._perform_validation(input_data)
            )
            
            # Apply autonomous decision-making if validation has issues
            if not validation_result["valid"]:
                validation_result = self._apply_autonomous_decision(input_data, validation_result)
            
            # Apply safety guardrails to any generated feedback
            if "enhanced_feedback" in validation_result:
                validation_result["enhanced_feedback"] = self.apply_safety_guardrails(
                    validation_result["enhanced_feedback"]
                )
            
            return self.format_agent_response(
                success=validation_result["valid"],
                data=validation_result,
                message="Input validation completed with autonomous enhancements"
            )
            
        except Exception as e:
            logger_validation.error(f"Validation processing error: {str(e)}")
            return self.format_agent_response(
                success=False,
                message=f"Validation error: {str(e)}",
                metadata={"error": str(e)}
            )
    
    def _perform_validation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform core validation logic.
        
        Args:
            input_data: Input to validate
            
        Returns:
            Validation result
        """
        # Check required fields
        validation_result = self._validate_required_fields(input_data)
        if not validation_result["valid"]:
            return validation_result
        
        # Validate age
        validation_result = self._validate_age(input_data["age"])
        if not validation_result["valid"]:
            return validation_result
        
        # Validate gender
        validation_result = self._validate_gender(input_data["gender"])
        if not validation_result["valid"]:
            return validation_result
        
        # Validate symptoms
        validation_result = self._validate_symptoms_format(input_data["symptoms"])
        if not validation_result["valid"]:
            return validation_result
        
        # Apply safety filters
        validation_result = self._apply_safety_filters(input_data)
        if not validation_result["valid"]:
            return validation_result
        
        # If all validations pass, return sanitized input
        sanitized_input = self._sanitize_input(input_data)
        
        logger_validation.info("Input validation successful")
        return {
            "valid": True,
            "sanitized_input": sanitized_input,
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": "EnhancedValidationAgent"
        }
    
    def _apply_autonomous_decision(
        self,
        input_data: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply autonomous decision-making for validation failures.
        
        Requirements: 1.5 - Autonomous decision-making
        
        Args:
            input_data: Original input
            validation_result: Current validation result
            
        Returns:
            Enhanced validation result with autonomous decisions
        """
        try:
            # Prepare context for decision
            context = {
                "input_summary": str(input_data),
                "issues": validation_result.get("reason", "Unknown issues"),
                "context": self.context_manager.get_context()
            }
            
            # Make autonomous decision
            if self.validation_decision_chain:
                decision = self.validation_decision_chain.invoke(context)
                validation_result["autonomous_decision"] = decision.strip()
                
                # If decision is to search for criteria, perform web search
                if "SEARCH_CRITERIA" in decision:
                    validation_result = self._search_validation_criteria(validation_result)
            
            # Get enhanced feedback using LangChain
            if self.validation_feedback_chain:
                enhanced_feedback = self._get_enhanced_feedback(validation_result)
                if enhanced_feedback:
                    validation_result["enhanced_feedback"] = enhanced_feedback
            
            return validation_result
            
        except Exception as e:
            logger_validation.error(f"Error in autonomous decision: {e}")
            return validation_result
    
    def _search_validation_criteria(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search web for validation criteria when needed.
        
        Requirements: 1.3 - Web search for validation criteria
        
        Args:
            validation_result: Current validation result
            
        Returns:
            Enhanced validation result with search results
        """
        try:
            # Determine what to search for based on validation issue
            reason = validation_result.get("reason", "")
            
            if "age" in reason.lower():
                query = "medical age validation criteria health assessment"
            elif "symptom" in reason.lower():
                query = "valid medical symptom description criteria"
            else:
                query = "health data validation best practices"
            
            # Perform web search
            search_results = self.search_web(query)
            
            if search_results:
                validation_result["validation_criteria_sources"] = [
                    result.get_citation() for result in search_results[:3]
                ]
                logger_validation.info(f"Found {len(search_results)} validation criteria sources")
            
            return validation_result
            
        except Exception as e:
            logger_validation.error(f"Error searching validation criteria: {e}")
            return validation_result
    
    def validate_symptoms(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main validation method for symptom input (legacy compatibility).
        
        This method is maintained for backward compatibility.
        New code should use process() method.
        
        Args:
            user_input: Dictionary containing user symptoms and metadata
            
        Returns:
            Dictionary with validation results
        """
        logger_validation.info(f"Validating symptoms input: {len(user_input)} fields provided")
        return self._perform_validation(user_input)
    
    def _get_enhanced_feedback(self, validation_result: Dict[str, Any]) -> Optional[str]:
        """
        Get enhanced feedback using LangChain for validation failures.
        
        Args:
            validation_result: Basic validation result
            
        Returns:
            Enhanced feedback message or None
        """
        try:
            if not self.validation_feedback_chain:
                return None
            
            # Prepare validation issues for LangChain
            issues = []
            if "reason" in validation_result:
                issues.append(validation_result["reason"])
            if "missing" in validation_result:
                issues.append(f"Missing fields: {', '.join(validation_result['missing'])}")
            
            if not issues:
                return None
            
            # Get enhanced feedback from LangChain
            enhanced_feedback = self.validation_feedback_chain.invoke(
                {"validation_issues": "; ".join(issues)}
            )
            
            return enhanced_feedback
            
        except Exception as e:
            logger_validation.error(f"Error getting enhanced feedback: {str(e)}")
            return None
    
    def _validate_required_fields(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all required fields are present."""
        missing_fields = [field for field in self.REQUIRED_FIELDS if field not in user_input or user_input[field] is None]
        
        if missing_fields:
            logger_validation.warning(f"Missing required fields: {missing_fields}")
            return {
                "valid": False,
                "reason": "Missing critical fields",
                "missing": missing_fields
            }
        
        return {"valid": True}
    
    def _validate_age(self, age: Any) -> Dict[str, Any]:
        """Validate age field."""
        try:
            age_int = int(age)
            if not (self.MIN_AGE <= age_int <= self.MAX_AGE):
                logger_validation.warning(f"Invalid age range: {age_int}")
                return {
                    "valid": False,
                    "reason": f"Age must be between {self.MIN_AGE} and {self.MAX_AGE} years"
                }
            return {"valid": True}
        except (ValueError, TypeError):
            logger_validation.warning(f"Invalid age format: {age}")
            return {
                "valid": False,
                "reason": "Age must be a valid number"
            }
    
    def _validate_gender(self, gender: Any) -> Dict[str, Any]:
        """Validate gender field."""
        if not isinstance(gender, str):
            return {
                "valid": False,
                "reason": "Gender must be a string"
            }
        
        gender_lower = gender.lower().strip()
        if gender_lower not in self.VALID_GENDERS:
            logger_validation.warning(f"Invalid gender: {gender}")
            return {
                "valid": False,
                "reason": f"Gender must be one of: {', '.join(self.VALID_GENDERS)}"
            }
        
        return {"valid": True}
    
    def _validate_symptoms_format(self, symptoms: Any) -> Dict[str, Any]:
        """Validate symptoms format and content."""
        if not isinstance(symptoms, list):
            return {
                "valid": False,
                "reason": "Symptoms must be provided as a list"
            }
        
        if len(symptoms) == 0:
            return {
                "valid": False,
                "reason": "At least one symptom must be provided"
            }
        
        if len(symptoms) > self.MAX_SYMPTOMS_PER_REQUEST:
            return {
                "valid": False,
                "reason": f"Maximum {self.MAX_SYMPTOMS_PER_REQUEST} symptoms allowed per request"
            }
        
        # Validate each symptom
        for i, symptom in enumerate(symptoms):
            if not isinstance(symptom, str):
                return {
                    "valid": False,
                    "reason": f"Symptom {i+1} must be a string"
                }
            
            symptom_clean = symptom.strip()
            if len(symptom_clean) < self.MIN_SYMPTOM_LENGTH:
                return {
                    "valid": False,
                    "reason": f"Symptom {i+1} is too short (minimum {self.MIN_SYMPTOM_LENGTH} characters)"
                }
            
            if len(symptom_clean) > self.MAX_SYMPTOM_LENGTH:
                return {
                    "valid": False,
                    "reason": f"Symptom {i+1} is too long (maximum {self.MAX_SYMPTOM_LENGTH} characters)"
                }
        
        return {"valid": True}
    
    def _apply_safety_filters(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Apply safety filters to detect potentially malicious input."""
        # Check all string values for unsafe patterns
        for key, value in user_input.items():
            if isinstance(value, str):
                if self._contains_unsafe_content(value):
                    logger_validation.warning(f"Unsafe content detected in field: {key}")
                    return {
                        "valid": False,
                        "reason": "Input contains potentially unsafe content"
                    }
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and self._contains_unsafe_content(item):
                        logger_validation.warning(f"Unsafe content detected in list field: {key}")
                        return {
                            "valid": False,
                            "reason": "Input contains potentially unsafe content"
                        }
        
        return {"valid": True}
    
    def _contains_unsafe_content(self, text: str) -> bool:
        """Check if text contains unsafe patterns."""
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True
        return False
    
    def _sanitize_input(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize and normalize the input."""
        sanitized = {}
        
        # Sanitize age
        sanitized["age"] = int(user_input["age"])
        
        # Sanitize gender
        sanitized["gender"] = user_input["gender"].lower().strip()
        
        # Sanitize symptoms
        sanitized["symptoms"] = [symptom.strip().lower() for symptom in user_input["symptoms"]]
        
        # Include optional fields if present
        if "medical_history" in user_input:
            if isinstance(user_input["medical_history"], list):
                sanitized["medical_history"] = [
                    item.strip().lower() if isinstance(item, str) else item 
                    for item in user_input["medical_history"]
                ]
            else:
                sanitized["medical_history"] = []
        
        return sanitized
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of validation rules and capabilities."""
        base_summary = {
            "agent_type": "EnhancedValidationAgent",
            "framework": "LangChain",
            "required_fields": self.REQUIRED_FIELDS,
            "age_range": {"min": self.MIN_AGE, "max": self.MAX_AGE},
            "valid_genders": self.VALID_GENDERS,
            "symptom_limits": {
                "max_count": self.MAX_SYMPTOMS_PER_REQUEST,
                "min_length": self.MIN_SYMPTOM_LENGTH,
                "max_length": self.MAX_SYMPTOM_LENGTH
            },
            "safety_features": [
                "HTML/Script injection prevention",
                "SQL injection prevention", 
                "Input sanitization",
                "Length validation",
                "LangChain-enhanced feedback",
                "Autonomous decision-making",
                "Web search for validation criteria",
                "Circuit breaker protection",
                "Retry logic with exponential backoff"
            ],
            "llm_available": bool(self.llm),
            "web_search_enabled": bool(self.web_search_tool),
            "monitoring_enabled": bool(self.monitoring)
        }
        
        # Add agent status from enhanced base
        base_summary.update(self.get_agent_status())
        
        return base_summary