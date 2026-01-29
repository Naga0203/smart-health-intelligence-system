"""
Validation Agent for AI Health Intelligence System

This agent provides the first line of defense against incomplete or unsafe inputs.
It validates user symptoms and metadata before they reach the ML prediction layer.

Validates: Requirements 1.2, 1.3, 1.5
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger('health_ai.validation')


class ValidationAgent:
    """
    First-line defense against incomplete or unsafe inputs.
    Validates user symptoms and metadata according to system requirements.
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
        r'sql\s+(select|insert|update|delete|drop|create)',  # SQL injection
    ]
    
    def __init__(self):
        """Initialize the validation agent."""
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.UNSAFE_PATTERNS]
        logger.info("ValidationAgent initialized")
    
    def validate_symptoms(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main validation method for symptom input.
        
        Args:
            user_input: Dictionary containing user symptoms and metadata
            
        Returns:
            Dictionary with validation results:
            {
                "valid": bool,
                "reason": str (if invalid),
                "missing": List[str] (if fields missing),
                "sanitized_input": Dict (if valid)
            }
        """
        logger.info(f"Validating symptoms input: {len(user_input)} fields provided")
        
        try:
            # Check required fields
            validation_result = self._validate_required_fields(user_input)
            if not validation_result["valid"]:
                return validation_result
            
            # Validate age
            validation_result = self._validate_age(user_input["age"])
            if not validation_result["valid"]:
                return validation_result
            
            # Validate gender
            validation_result = self._validate_gender(user_input["gender"])
            if not validation_result["valid"]:
                return validation_result
            
            # Validate symptoms
            validation_result = self._validate_symptoms_format(user_input["symptoms"])
            if not validation_result["valid"]:
                return validation_result
            
            # Apply safety filters
            validation_result = self._apply_safety_filters(user_input)
            if not validation_result["valid"]:
                return validation_result
            
            # If all validations pass, return sanitized input
            sanitized_input = self._sanitize_input(user_input)
            
            logger.info("Input validation successful")
            return {
                "valid": True,
                "sanitized_input": sanitized_input,
                "validation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return {
                "valid": False,
                "reason": "Internal validation error",
                "error": str(e)
            }
    
    def _validate_required_fields(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all required fields are present."""
        missing_fields = [field for field in self.REQUIRED_FIELDS if field not in user_input or user_input[field] is None]
        
        if missing_fields:
            logger.warning(f"Missing required fields: {missing_fields}")
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
                logger.warning(f"Invalid age range: {age_int}")
                return {
                    "valid": False,
                    "reason": f"Age must be between {self.MIN_AGE} and {self.MAX_AGE} years"
                }
            return {"valid": True}
        except (ValueError, TypeError):
            logger.warning(f"Invalid age format: {age}")
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
            logger.warning(f"Invalid gender: {gender}")
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
                    logger.warning(f"Unsafe content detected in field: {key}")
                    return {
                        "valid": False,
                        "reason": "Input contains potentially unsafe content"
                    }
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and self._contains_unsafe_content(item):
                        logger.warning(f"Unsafe content detected in list field: {key}")
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
        """Get a summary of validation rules for documentation."""
        return {
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
                "Length validation"
            ]
        }