"""
LangChain-based Data Extraction Agent for AI Health Intelligence System

This agent uses Gemini AI to intelligently extract and map user input data
to the trained ML model's expected feature columns.

Validates: Requirements 1.1, 1.4, 2.2
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from agents.base_agent import BaseHealthAgent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

logger = logging.getLogger('health_ai.data_extraction')


class ExtractedFeatures(BaseModel):
    """Pydantic model for extracted features."""
    age: int = Field(description="Patient age in years")
    gender: str = Field(description="Patient gender (male/female/other)")
    bmi: Optional[float] = Field(description="Body Mass Index if available")
    blood_pressure_systolic: Optional[int] = Field(description="Systolic blood pressure")
    blood_pressure_diastolic: Optional[int] = Field(description="Diastolic blood pressure")
    glucose_level: Optional[float] = Field(description="Blood glucose level")
    cholesterol: Optional[float] = Field(description="Cholesterol level")
    heart_rate: Optional[int] = Field(description="Heart rate in bpm")
    symptoms_encoded: List[str] = Field(description="List of encoded symptoms")
    medical_history_flags: Dict[str, bool] = Field(description="Medical history flags")
    lifestyle_factors: Dict[str, Any] = Field(description="Lifestyle factors")


class LangChainDataExtractionAgent(BaseHealthAgent):
    """
    LangChain-based agent for intelligent data extraction and feature mapping.
    
    Uses Gemini AI to:
    - Extract structured data from natural language input
    - Map user input to ML model feature columns
    - Handle missing data intelligently
    - Validate and normalize extracted features
    """
    
    def __init__(self):
        """Initialize the data extraction agent."""
        super().__init__("DataExtractionAgent")
        
        # ML model feature schemas for different diseases
        self.ml_feature_schemas = {
            "diabetes": {
                "required": ["age", "gender", "glucose_level", "bmi"],
                "optional": ["blood_pressure_systolic", "blood_pressure_diastolic", 
                           "cholesterol", "family_history_diabetes", "physical_activity"],
                "symptom_features": ["increased_thirst", "frequent_urination", "fatigue", 
                                   "blurred_vision", "slow_healing", "weight_loss"]
            },
            "heart_disease": {
                "required": ["age", "gender", "blood_pressure_systolic", "cholesterol"],
                "optional": ["bmi", "heart_rate", "smoking", "diabetes", "family_history_heart"],
                "symptom_features": ["chest_pain", "shortness_of_breath", "fatigue", 
                                   "irregular_heartbeat", "dizziness", "nausea"]
            },
            "hypertension": {
                "required": ["age", "gender", "blood_pressure_systolic", "blood_pressure_diastolic"],
                "optional": ["bmi", "sodium_intake", "alcohol_consumption", "stress_level"],
                "symptom_features": ["headaches", "dizziness", "chest_pain", "vision_problems", 
                                   "fatigue", "nosebleeds"]
            }
        }
        
        # Create extraction chain with JSON output parser
        self.extraction_chain = self._create_extraction_chain()
        
        logger.info("LangChain DataExtractionAgent initialized")
    
    def _create_extraction_chain(self):
        """Create LangChain chain for data extraction with structured output."""
        if not self.llm:
            logger.warning("LLM not available for data extraction")
            return None
        
        system_prompt = """You are a medical data extraction specialist. Your task is to extract structured health data from user input and map it to specific medical features.

CRITICAL INSTRUCTIONS:
1. Extract all available numerical health metrics (age, BMI, blood pressure, glucose, cholesterol, heart rate)
2. Identify and encode symptoms mentioned by the user
3. Extract medical history information
4. Infer lifestyle factors when mentioned
5. Handle missing data by marking fields as null
6. Be conservative - only extract data that is clearly stated or strongly implied
7. Convert all measurements to standard units

OUTPUT FORMAT:
Return a JSON object with the following structure:
{{
    "age": <integer>,
    "gender": "<male/female/other>",
    "bmi": <float or null>,
    "blood_pressure_systolic": <integer or null>,
    "blood_pressure_diastolic": <integer or null>,
    "glucose_level": <float or null>,
    "cholesterol": <float or null>,
    "heart_rate": <integer or null>,
    "symptoms_encoded": [<list of symptom strings>],
    "medical_history_flags": {{
        "diabetes": <boolean>,
        "hypertension": <boolean>,
        "heart_disease": <boolean>,
        "family_history": <boolean>
    }},
    "lifestyle_factors": {{
        "smoking": <boolean or null>,
        "alcohol": <boolean or null>,
        "exercise": <string or null>,
        "diet": <string or null>
    }}
}}"""

        human_prompt = """Extract structured health data from the following user input:

User Input:
{user_input}

Target Disease: {disease}
Required Features: {required_features}
Optional Features: {optional_features}

Please extract all available data and return it in the specified JSON format."""

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])
        
        # Use JSON output parser for structured extraction
        json_parser = JsonOutputParser()
        
        return prompt_template | self.llm | json_parser
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for data extraction.
        
        Args:
            input_data: Contains user_input, disease, and raw data
            
        Returns:
            Extracted and mapped features ready for ML model
        """
        self.log_agent_action("extract_features", {
            "disease": input_data.get("disease"),
            "has_llm": bool(self.llm)
        })
        
        try:
            # Validate input
            if "user_input" not in input_data or "disease" not in input_data:
                return self.format_agent_response(
                    success=False,
                    message="Missing required fields: user_input or disease"
                )
            
            disease = input_data["disease"]
            user_input = input_data["user_input"]
            
            # Get ML feature schema for the disease
            feature_schema = self.ml_feature_schemas.get(disease)
            if not feature_schema:
                return self.format_agent_response(
                    success=False,
                    message=f"Unknown disease: {disease}"
                )
            
            # Extract features using Gemini AI
            extracted_features = self._extract_features_with_gemini(
                user_input, disease, feature_schema
            )
            
            # Validate and normalize extracted features
            validated_features = self._validate_and_normalize(
                extracted_features, feature_schema
            )
            
            # Map to ML model format
            ml_ready_features = self._map_to_ml_format(
                validated_features, disease
            )
            
            return self.format_agent_response(
                success=True,
                data={
                    "extracted_features": validated_features,
                    "ml_ready_features": ml_ready_features,
                    "feature_schema": feature_schema,
                    "extraction_method": "gemini_ai" if self.llm else "rule_based"
                },
                message="Features extracted and mapped successfully"
            )
            
        except Exception as e:
            logger.error(f"Error in data extraction: {str(e)}")
            return self.get_fallback_response(input_data)
    
    def _extract_features_with_gemini(self, user_input: Dict[str, Any], 
                                     disease: str, feature_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features using Gemini AI with LangChain.
        
        Args:
            user_input: Raw user input data
            disease: Target disease for prediction
            feature_schema: ML model feature schema
            
        Returns:
            Extracted features dictionary
        """
        try:
            if not self.extraction_chain:
                # Fallback to rule-based extraction
                return self._rule_based_extraction(user_input, feature_schema)
            
            # Prepare input for Gemini
            chain_input = {
                "user_input": str(user_input),
                "disease": disease,
                "required_features": ", ".join(feature_schema["required"]),
                "optional_features": ", ".join(feature_schema["optional"])
            }
            
            # Execute extraction chain
            extracted = self.execute_chain(self.extraction_chain, chain_input)
            
            if extracted:
                logger.info("Features extracted successfully using Gemini AI")
                return extracted
            else:
                logger.warning("Gemini extraction failed, using rule-based fallback")
                return self._rule_based_extraction(user_input, feature_schema)
                
        except Exception as e:
            logger.error(f"Gemini extraction error: {str(e)}")
            return self._rule_based_extraction(user_input, feature_schema)
    
    def _rule_based_extraction(self, user_input: Dict[str, Any], 
                              feature_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback rule-based extraction when Gemini is unavailable.
        
        Args:
            user_input: Raw user input
            feature_schema: Feature schema
            
        Returns:
            Extracted features using rules
        """
        logger.info("Using rule-based feature extraction")
        
        extracted = {
            "age": user_input.get("age"),
            "gender": user_input.get("gender"),
            "bmi": user_input.get("bmi"),
            "blood_pressure_systolic": user_input.get("blood_pressure_systolic"),
            "blood_pressure_diastolic": user_input.get("blood_pressure_diastolic"),
            "glucose_level": user_input.get("glucose_level"),
            "cholesterol": user_input.get("cholesterol"),
            "heart_rate": user_input.get("heart_rate"),
            "symptoms_encoded": user_input.get("symptoms", []),
            "medical_history_flags": {
                "diabetes": user_input.get("has_diabetes", False),
                "hypertension": user_input.get("has_hypertension", False),
                "heart_disease": user_input.get("has_heart_disease", False),
                "family_history": user_input.get("family_history", False)
            },
            "lifestyle_factors": {
                "smoking": user_input.get("smoking"),
                "alcohol": user_input.get("alcohol"),
                "exercise": user_input.get("exercise"),
                "diet": user_input.get("diet")
            }
        }
        
        return extracted
    
    def _validate_and_normalize(self, extracted_features: Dict[str, Any], 
                                feature_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize extracted features.
        
        Args:
            extracted_features: Raw extracted features
            feature_schema: Expected feature schema
            
        Returns:
            Validated and normalized features
        """
        validated = {}
        
        # Validate age
        if "age" in extracted_features and extracted_features["age"]:
            age = int(extracted_features["age"])
            validated["age"] = max(1, min(120, age))  # Clamp to valid range
        
        # Validate gender
        if "gender" in extracted_features and extracted_features["gender"]:
            gender = str(extracted_features["gender"]).lower()
            validated["gender"] = gender if gender in ["male", "female", "other"] else "other"
        
        # Validate numerical features
        numerical_features = ["bmi", "blood_pressure_systolic", "blood_pressure_diastolic",
                            "glucose_level", "cholesterol", "heart_rate"]
        
        for feature in numerical_features:
            if feature in extracted_features and extracted_features[feature] is not None:
                try:
                    value = float(extracted_features[feature])
                    # Apply reasonable bounds
                    if feature == "bmi":
                        validated[feature] = max(10, min(60, value))
                    elif "blood_pressure" in feature:
                        validated[feature] = max(40, min(250, value))
                    elif feature == "glucose_level":
                        validated[feature] = max(50, min(500, value))
                    elif feature == "cholesterol":
                        validated[feature] = max(100, min(400, value))
                    elif feature == "heart_rate":
                        validated[feature] = max(40, min(200, value))
                except (ValueError, TypeError):
                    validated[feature] = None
            else:
                validated[feature] = None
        
        # Validate symptoms
        if "symptoms_encoded" in extracted_features:
            symptoms = extracted_features["symptoms_encoded"]
            if isinstance(symptoms, list):
                validated["symptoms_encoded"] = [str(s).lower().strip() for s in symptoms]
            else:
                validated["symptoms_encoded"] = []
        else:
            validated["symptoms_encoded"] = []
        
        # Validate medical history flags
        validated["medical_history_flags"] = extracted_features.get("medical_history_flags", {})
        
        # Validate lifestyle factors
        validated["lifestyle_factors"] = extracted_features.get("lifestyle_factors", {})
        
        return validated
    
    def _map_to_ml_format(self, validated_features: Dict[str, Any], 
                         disease: str) -> Dict[str, Any]:
        """
        Map validated features to ML model input format.
        
        Args:
            validated_features: Validated features
            disease: Target disease
            
        Returns:
            Features in ML model format
        """
        feature_schema = self.ml_feature_schemas[disease]
        ml_features = {}
        
        # Map basic features
        ml_features["age"] = validated_features.get("age", 0)
        ml_features["gender_encoded"] = 1 if validated_features.get("gender") == "male" else 0
        
        # Map numerical features
        for feature in ["bmi", "blood_pressure_systolic", "blood_pressure_diastolic",
                       "glucose_level", "cholesterol", "heart_rate"]:
            ml_features[feature] = validated_features.get(feature, 0) or 0
        
        # Encode symptoms as binary features
        for symptom in feature_schema["symptom_features"]:
            symptom_key = f"symptom_{symptom}"
            ml_features[symptom_key] = 1 if symptom in validated_features.get("symptoms_encoded", []) else 0
        
        # Encode medical history
        history = validated_features.get("medical_history_flags", {})
        ml_features["has_diabetes"] = 1 if history.get("diabetes") else 0
        ml_features["has_hypertension"] = 1 if history.get("hypertension") else 0
        ml_features["has_heart_disease"] = 1 if history.get("heart_disease") else 0
        ml_features["family_history"] = 1 if history.get("family_history") else 0
        
        # Encode lifestyle factors
        lifestyle = validated_features.get("lifestyle_factors", {})
        ml_features["smoking"] = 1 if lifestyle.get("smoking") else 0
        ml_features["alcohol"] = 1 if lifestyle.get("alcohol") else 0
        
        return ml_features
    
    def get_feature_schema(self, disease: str) -> Optional[Dict[str, Any]]:
        """Get the ML feature schema for a specific disease."""
        return self.ml_feature_schemas.get(disease)
    
    def get_extraction_summary(self) -> Dict[str, Any]:
        """Get summary of extraction capabilities."""
        return {
            "agent_type": "LangChainDataExtractionAgent",
            "framework": "LangChain",
            "extraction_method": "gemini_ai" if self.llm else "rule_based",
            "supported_diseases": list(self.ml_feature_schemas.keys()),
            "features": [
                "Intelligent feature extraction using Gemini AI",
                "Natural language to structured data mapping",
                "Missing data handling",
                "Feature validation and normalization",
                "ML model format conversion",
                "Rule-based fallback extraction"
            ],
            "llm_available": bool(self.llm)
        }