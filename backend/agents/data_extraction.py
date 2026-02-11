"""
LangChain-based Data Extraction Agent for AI Health Intelligence System

This agent uses Gemini AI to extract and map user input data to match
the trained ML model's expected features/columns.

Validates: Requirements 1.1, 1.4
"""

from typing import Dict, Any, List, Optional
import logging
import json
from agents.base_agent import BaseHealthAgent

logger = logging.getLogger('health_ai.data_extraction')


class DataExtractionAgent(BaseHealthAgent):
    """
    LangChain-based agent for extracting and mapping user input to ML model features.
    
    Uses Gemini AI to:
    - Parse natural language symptom descriptions
    - Map symptoms to standardized medical terms
    - Extract relevant features for ML model
    - Handle missing or ambiguous data
    """
    
    def __init__(self):
        """Initialize the data extraction agent."""
        super().__init__("DataExtractionAgent")
        
        # Define expected ML model features for different diseases
        self.model_features = {
            "diabetes": [
                "age", "gender", "polyuria", "polydipsia", "sudden_weight_loss",
                "weakness", "polyphagia", "genital_thrush", "visual_blurring",
                "itching", "irritability", "delayed_healing", "partial_paresis",
                "muscle_stiffness", "alopecia", "obesity"
            ],
            "heart_disease": [
                "age", "gender", "chest_pain_type", "resting_blood_pressure",
                "cholesterol", "fasting_blood_sugar", "resting_ecg",
                "max_heart_rate", "exercise_angina", "oldpeak", "slope",
                "ca", "thal"
            ],
            "hypertension": [
                "age", "gender", "systolic_bp", "diastolic_bp", "bmi",
                "smoking", "alcohol", "physical_activity", "stress_level",
                "family_history", "salt_intake", "sleep_hours"
            ]
        }
        
        # Symptom to feature mapping
        self.symptom_mappings = {
            "increased_thirst": "polydipsia",
            "excessive_thirst": "polydipsia",
            "frequent_urination": "polyuria",
            "excessive_urination": "polyuria",
            "weight_loss": "sudden_weight_loss",
            "losing_weight": "sudden_weight_loss",
            "fatigue": "weakness",
            "tired": "weakness",
            "excessive_hunger": "polyphagia",
            "always_hungry": "polyphagia",
            "blurred_vision": "visual_blurring",
            "vision_problems": "visual_blurring",
            "chest_pain": "chest_pain_type",
            "chest_discomfort": "chest_pain_type",
            "shortness_of_breath": "exercise_angina",
            "breathing_difficulty": "exercise_angina",
            "headache": "systolic_bp",  # Indicator for hypertension
            "dizziness": "systolic_bp"
        }
        
        # Create LangChain chain for intelligent data extraction
        self.extraction_chain = self.create_agent_chain(
            system_prompt="""You are a medical data extraction agent. Your role is to:
1. Parse user-provided symptoms and health information
2. Map symptoms to standardized medical terms
3. Extract relevant features for disease prediction models
4. Handle ambiguous or incomplete information

IMPORTANT:
- Be precise in symptom mapping
- Ask for clarification when needed
- Use medical terminology correctly
- Return structured data in JSON format""",
            
            human_prompt="""Extract and map the following health information to standardized medical features:

User Input:
- Symptoms: {symptoms}
- Age: {age}
- Gender: {gender}
- Additional Info: {additional_info}

Target Disease: {disease}
Required Features: {required_features}

Please extract and map the data to match the required features. Return a JSON object with:
1. "mapped_features": Dictionary of feature names and values
2. "confidence": Your confidence in the extraction (0-1)
3. "missing_features": List of features that couldn't be extracted
4. "clarifications_needed": List of questions to ask user for better accuracy"""
        )
        
        logger.info("DataExtractionAgent initialized with LangChain")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for data extraction.
        
        Args:
            input_data: Raw user input containing symptoms, age, gender, etc.
            
        Returns:
            Extracted and mapped data ready for ML model
        """
        required_fields = ["symptoms", "age", "gender"]
        validation = self.validate_input(input_data, required_fields)
        
        if not validation["valid"]:
            return self.format_agent_response(
                success=False,
                message=validation["message"],
                data=validation
            )
        
        self.log_agent_action("extract_data", {
            "symptoms_count": len(input_data.get("symptoms", [])),
            "disease": input_data.get("disease", "unknown")
        })
        
        try:
            # Extract and map data
            extracted_data = self.extract_and_map(
                symptoms=input_data["symptoms"],
                age=input_data["age"],
                gender=input_data["gender"],
                disease=input_data.get("disease", "diabetes"),
                additional_info=input_data.get("additional_info", {})
            )
            
            return self.format_agent_response(
                success=True,
                data=extracted_data,
                message="Data extraction completed successfully"
            )
            
        except Exception as e:
            logger.error(f"Error in data extraction: {str(e)}")
            return self.get_fallback_response(input_data)
    
    def extract_and_map(self, symptoms: List[str], age: int, gender: str,
                       disease: str, additional_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extract and map user data to ML model features using Gemini AI.
        
        Args:
            symptoms: List of user symptoms
            age: User age
            gender: User gender
            disease: Target disease for prediction
            additional_info: Additional health information
            
        Returns:
            Dictionary with mapped features and metadata
        """
        logger.info(f"Extracting data for {disease} prediction")
        
        try:
            # Get required features for the disease
            required_features = self.model_features.get(disease, [])
            
            # Try LangChain extraction first
            if self.extraction_chain:
                langchain_result = self._extract_with_langchain(
                    symptoms, age, gender, disease, required_features, additional_info
                )
                if langchain_result:
                    return langchain_result
            
            # Fallback to rule-based extraction
            return self._extract_with_rules(
                symptoms, age, gender, disease, required_features, additional_info
            )
            
        except Exception as e:
            logger.error(f"Error in extract_and_map: {str(e)}")
            return self._get_fallback_extraction(symptoms, age, gender, disease)
    
    def _extract_with_langchain(self, symptoms: List[str], age: int, gender: str,
                                disease: str, required_features: List[str],
                                additional_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract data using LangChain and Gemini AI."""
        try:
            if not self.extraction_chain:
                return None
            
            # Prepare input for LangChain
            chain_input = {
                "symptoms": ", ".join(symptoms),
                "age": age,
                "gender": gender,
                "disease": disease,
                "required_features": ", ".join(required_features),
                "additional_info": json.dumps(additional_info or {})
            }
            
            # Execute chain
            result = self.execute_chain(self.extraction_chain, chain_input)
            
            if result:
                # Parse JSON response from Gemini
                try:
                    parsed_result = json.loads(result)
                    
                    # Add basic features
                    parsed_result["mapped_features"]["age"] = age
                    parsed_result["mapped_features"]["gender"] = 1 if gender.lower() == "male" else 0
                    
                    return {
                        "features": parsed_result["mapped_features"],
                        "extraction_confidence": parsed_result.get("confidence", 0.7),
                        "missing_features": parsed_result.get("missing_features", []),
                        "clarifications_needed": parsed_result.get("clarifications_needed", []),
                        "extraction_method": "langchain_gemini",
                        "disease": disease
                    }
                except json.JSONDecodeError:
                    logger.warning("Failed to parse LangChain JSON response, using fallback")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"LangChain extraction failed: {str(e)}")
            return None
    
    def _extract_with_rules(self, symptoms: List[str], age: int, gender: str,
                           disease: str, required_features: List[str],
                           additional_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data using rule-based mapping."""
        logger.info("Using rule-based extraction")
        
        features = {}
        
        # Add basic features
        features["age"] = age
        features["gender"] = 1 if gender.lower() == "male" else 0
        
        # Map symptoms to features
        for symptom in symptoms:
            symptom_lower = symptom.lower().strip().replace(" ", "_")
            
            # Direct mapping
            if symptom_lower in self.symptom_mappings:
                feature_name = self.symptom_mappings[symptom_lower]
                if feature_name in required_features:
                    features[feature_name] = 1  # Binary feature
            
            # Check if symptom matches any required feature
            for feature in required_features:
                if symptom_lower in feature or feature in symptom_lower:
                    features[feature] = 1
        
        # Add additional info if provided
        if additional_info:
            for key, value in additional_info.items():
                if key in required_features:
                    features[key] = value
        
        # Fill missing features with defaults
        missing_features = []
        for feature in required_features:
            if feature not in features and feature not in ["age", "gender"]:
                features[feature] = 0  # Default to 0 for binary features
                missing_features.append(feature)
        
        return {
            "features": features,
            "extraction_confidence": 0.6,  # Lower confidence for rule-based
            "missing_features": missing_features,
            "clarifications_needed": [],
            "extraction_method": "rule_based",
            "disease": disease
        }
    
    def _get_fallback_extraction(self, symptoms: List[str], age: int, 
                                gender: str, disease: str) -> Dict[str, Any]:
        """Get minimal fallback extraction."""
        return {
            "features": {
                "age": age,
                "gender": 1 if gender.lower() == "male" else 0,
                "symptoms_count": len(symptoms)
            },
            "extraction_confidence": 0.3,
            "missing_features": ["most_features"],
            "clarifications_needed": ["Please provide more detailed health information"],
            "extraction_method": "fallback",
            "disease": disease
        }
    
    def get_supported_diseases(self) -> List[str]:
        """Get list of diseases with feature mappings."""
        return list(self.model_features.keys())
    
    def get_required_features(self, disease: str) -> List[str]:
        """Get required features for a specific disease."""
        return self.model_features.get(disease, [])
    
    def get_extraction_summary(self) -> Dict[str, Any]:
        """Get summary of extraction capabilities."""
        return {
            "agent_type": "DataExtractionAgent",
            "framework": "LangChain",
            "supported_diseases": self.get_supported_diseases(),
            "extraction_methods": ["langchain_gemini", "rule_based", "fallback"],
            "features": [
                "Natural language symptom parsing",
                "Intelligent feature mapping",
                "Missing data handling",
                "Clarification suggestions"
            ],
            "llm_available": bool(self.llm)
        }