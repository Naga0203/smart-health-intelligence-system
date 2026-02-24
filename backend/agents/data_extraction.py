import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_agent import BaseHealthAgent

logger_data = logging.getLogger('health_ai.data_extraction')

class DataExtractionAgent(BaseHealthAgent):
    """
    Agent responsible for extracting structured data from user input.
    
    Uses LangChain and Gemini for intelligent feature extraction and mapping
    to disease prediction models.
    """
    
    def __init__(self):
        """Initialize the data extraction agent."""
        super().__init__("DataExtractionAgent")
        
        # Feature mapping for prediction models
        self.model_features = {
            "diabetes": [
                "pregnancies", "glucose", "blood_pressure", "skin_thickness", 
                "insulin", "bmi", "diabetes_pedigree_function", "age"
            ],
            "heart_disease": [
                "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", 
                "thalach", "exang", "oldpeak", "slope", "ca", "thal"
            ],
            "hypertension": [
                "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", 
                "thalach", "exang", "oldpeak", "slope", "ca", "thal" 
            ]
        }
        
        # Mapping from natural language symptoms to features
        self.symptom_mappings = {
            # Diabetes mappings
            "high_blood_sugar": "glucose",
            "frequent_urination": "glucose",
            "thirsty": "glucose",
            "overweight": "bmi",
            "obese": "bmi",
            "family_history": "diabetes_pedigree_function",
            
            # Heart disease mappings
            "chest_pain": "cp",
            "high_blood_pressure": "trestbps",
            "high_cholesterol": "chol",
            "fast_heart_rate": "thalach",
            "exercise_pain": "exang"
        }
        
        # Create LangChain chain for extraction
        self.extraction_chain = self.create_agent_chain(
            system_prompt="""You are an expert medical data extractor. 
            Your task is to extract structured feature values from patient symptoms and descriptions.
            Map the input text to the required features for the specified disease model.
            Return the result as a JSON object with 'mapped_features' and 'confidence' fields.""",
            
            human_prompt="""Extract features for {disease} prediction from:
            Symptoms: {symptoms}
            Age: {age}
            Gender: {gender}
            Additional Info: {additional_info}
            
            Required features to map: {required_features}
            
            Return JSON only."""
        )
        
        logger_data.info("DataExtractionAgent initialized")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and map data for prediction models.
        
        Args:
            input_data: Input dictionary containing:
                - symptoms (List[str])
                - age (int)
                - gender (str)
                - disease (str)
                - additional_info (Dict, optional)
                
        Returns:
            Dictionary with extracted features and metadata
        """
        required_fields = ["symptoms", "age", "gender", "disease"]
        validation = self.validate_input(input_data, required_fields)
        
        if not validation["valid"]:
            return self.format_agent_response(
                success=False,
                message=validation["message"],
                data=validation
            )
            
        self.log_agent_action("extract_data", {"disease": input_data["disease"]})
        
        try:
            extraction_result = self.extract_and_map(
                symptoms=input_data["symptoms"],
                age=input_data["age"],
                gender=input_data["gender"],
                disease=input_data["disease"],
                additional_info=input_data.get("additional_info", {})
            )
            
            return self.format_agent_response(
                success=True,
                data=extraction_result,
                message="Data extracted successfully"
            )
            
        except Exception as e:
            logger_data.error(f"Extraction error: {str(e)}")
            return self.get_fallback_response(input_data)
    
    def extract_and_map(self, symptoms: List[str], age: int, gender: str, 
                        disease: str, additional_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extract features and map them to the model requirements.
        
        Args:
            symptoms: List of user symptoms
            age: User age
            gender: User gender
            disease: Target disease for prediction
            additional_info: Additional health information
            
        Returns:
            Dictionary with mapped features and metadata
        """
        logger_data.info(f"Extracting data for {disease} prediction")
        
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
            logger_data.error(f"Error in extract_and_map: {str(e)}")
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
                    logger_data.warning("Failed to parse LangChain JSON response, using fallback")
                    return None
            
            return None
            
        except Exception as e:
            logger_data.error(f"LangChain extraction failed: {str(e)}")
            return None
    
    def _extract_with_rules(self, symptoms: List[str], age: int, gender: str,
                           disease: str, required_features: List[str],
                           additional_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data using rule-based mapping."""
        logger_data.info("Using rule-based extraction")
        
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