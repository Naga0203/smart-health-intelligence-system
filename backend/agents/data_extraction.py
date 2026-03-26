import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .infrastructure.enhanced_base_agent import EnhancedBaseHealthAgent
from .infrastructure.config import AgentConfig
from .infrastructure.models import SearchResult

logger_data = logging.getLogger('health_ai.data_extraction')

class DataExtractionAgent(EnhancedBaseHealthAgent):
    """
    Enhanced agent responsible for extracting structured data from user input.
    
    Uses LangChain and Gemini for intelligent feature extraction and mapping
    to disease prediction models. Now includes web search for medical terminology
    clarification, confidence scoring, and autonomous decision-making.
    
    Requirements: 1.1, 1.2, 1.3, 1.5, 8.1, 8.6, 8.7, 1.6
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the enhanced data extraction agent.
        
        Args:
            config: Agent configuration (uses defaults if not provided)
        """
        if config is None:
            config = AgentConfig(
                agent_name="DataExtractionAgent",
                enable_web_search=True,
                enable_caching=True,
                timeout=30,
                max_retries=3
            )
        
        super().__init__("DataExtractionAgent", config)
        
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
        
        # Create LangChain chain for extraction with structured output
        self._create_extraction_chain()
        
        logger_data.info("Enhanced DataExtractionAgent initialized with web search and confidence scoring")
    
    def _create_extraction_chain(self):
        """Create LangChain chain for structured data extraction."""
        if not self.llm:
            logger_data.warning("LLM not available, extraction chain not created")
            self.extraction_chain = None
            return
        
        try:
            system_prompt = """You are an expert medical data extractor with access to medical terminology databases.
            
Your task is to extract structured feature values from patient symptoms and descriptions for disease prediction models.

IMPORTANT INSTRUCTIONS:
1. Map the input text to the required features for the specified disease model
2. For ambiguous medical terms, note them for clarification via web search
3. Provide confidence scores (0.0-1.0) for each extracted feature
4. Identify missing features that are critical for accurate prediction
5. Return ONLY valid JSON with no additional text

Required JSON structure:
{{
    "mapped_features": {{"feature_name": value, ...}},
    "confidence_scores": {{"feature_name": confidence, ...}},
    "overall_confidence": 0.0-1.0,
    "missing_features": ["feature1", "feature2"],
    "ambiguous_terms": ["term1", "term2"],
    "clarifications_needed": ["clarification1", "clarification2"]
}}"""
            
            human_prompt = """Extract features for {disease} prediction from:

Symptoms: {symptoms}
Age: {age}
Gender: {gender}
Additional Info: {additional_info}

Required features to map: {required_features}

Return JSON only."""
            
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", human_prompt)
            ])
            
            self.extraction_chain = prompt_template | self.llm | StrOutputParser()
            logger_data.info("Extraction chain created successfully")
            
        except Exception as e:
            logger_data.error(f"Failed to create extraction chain: {e}")
            self.extraction_chain = None
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and map data for prediction models with enhanced capabilities.
        
        Requirements:
        - 8.1: Structured data extraction from unstructured text
        - 8.6: Web search for ambiguous medical terminology
        - 8.7: Confidence scores for extractions
        
        Args:
            input_data: Input dictionary containing:
                - symptoms (List[str])
                - age (int)
                - gender (str)
                - disease (str)
                - additional_info (Dict, optional)
                
        Returns:
            Dictionary with extracted features, confidence scores, and metadata
        """
        required_fields = ["symptoms", "age", "gender", "disease"]
        
        # Validate input
        missing_fields = [field for field in required_fields if field not in input_data]
        if missing_fields:
            return self.format_agent_response(
                success=False,
                message=f"Missing required fields: {', '.join(missing_fields)}",
                metadata={"missing_fields": missing_fields}
            )
        
        self.log_agent_action("extract_data", {"disease": input_data["disease"]})
        
        try:
            # Execute extraction with retry logic
            extraction_result = self.execute_with_retry(
                lambda: self.extract_and_map(
                    symptoms=input_data["symptoms"],
                    age=input_data["age"],
                    gender=input_data["gender"],
                    disease=input_data["disease"],
                    additional_info=input_data.get("additional_info", {})
                )
            )
            
            return self.format_agent_response(
                success=True,
                data=extraction_result,
                message="Data extracted successfully with confidence scoring"
            )
            
        except Exception as e:
            logger_data.error(f"Extraction error: {str(e)}")
            return self.format_agent_response(
                success=False,
                message=f"Extraction failed: {str(e)}",
                metadata={"error": str(e)}
            )
    
    def extract_and_map(self, symptoms: List[str], age: int, gender: str, 
                        disease: str, additional_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extract features and map them to model requirements with enhanced capabilities.
        
        Requirements:
        - 8.1: Structured data extraction
        - 8.6: Clarify ambiguous terms via web search
        - 8.7: Provide confidence scores
        
        Args:
            symptoms: List of user symptoms
            age: User age
            gender: User gender
            disease: Target disease for prediction
            additional_info: Additional health information
            
        Returns:
            Dictionary with mapped features, confidence scores, and metadata
        """
        logger_data.info(f"Extracting data for {disease} prediction with enhanced capabilities")
        
        try:
            # Get required features for the disease
            required_features = self.model_features.get(disease, [])
            
            # Try LangChain extraction with Gemini
            if self.extraction_chain:
                langchain_result = self._extract_with_langchain(
                    symptoms, age, gender, disease, required_features, additional_info
                )
                
                if langchain_result:
                    # Check for ambiguous terms that need clarification
                    ambiguous_terms = langchain_result.get("ambiguous_terms", [])
                    if ambiguous_terms and self.web_search_tool:
                        clarifications = self._clarify_medical_terms(ambiguous_terms)
                        langchain_result["term_clarifications"] = clarifications
                        
                        # Re-extract with clarified terms if significant clarifications found
                        if clarifications:
                            logger_data.info(f"Re-extracting with {len(clarifications)} clarified terms")
                            # Add clarifications to additional_info for re-extraction
                            enhanced_info = additional_info.copy() if additional_info else {}
                            enhanced_info["clarified_terms"] = clarifications
                            
                            # Re-run extraction with clarified information
                            refined_result = self._extract_with_langchain(
                                symptoms, age, gender, disease, required_features, enhanced_info
                            )
                            if refined_result:
                                refined_result["term_clarifications"] = clarifications
                                refined_result["extraction_refined"] = True
                                return refined_result
                    
                    return langchain_result
            
            # Fallback to rule-based extraction
            logger_data.warning("LangChain extraction unavailable, using rule-based fallback")
            return self._extract_with_rules(
                symptoms, age, gender, disease, required_features, additional_info
            )
            
        except Exception as e:
            logger_data.error(f"Error in extract_and_map: {str(e)}")
            return self._get_fallback_extraction(symptoms, age, gender, disease)
    
    def _clarify_medical_terms(self, terms: List[str]) -> Dict[str, str]:
        """
        Clarify ambiguous medical terms using web search.
        
        Requirements: 8.6 - Ambiguous terms trigger clarification searches
        
        Args:
            terms: List of ambiguous medical terms
            
        Returns:
            Dictionary mapping terms to their clarifications
        """
        clarifications = {}
        
        for term in terms:
            try:
                # Search for medical term definition
                query = f"medical definition {term}"
                search_results = self.search_web(query, filters={"max_results": 3})
                
                if search_results:
                    # Extract clarification from top result
                    top_result = search_results[0]
                    clarification = f"{top_result.snippet} (Source: {top_result.source_domain})"
                    clarifications[term] = clarification
                    logger_data.info(f"Clarified term '{term}' via web search")
                else:
                    logger_data.warning(f"No clarification found for term '{term}'")
                    
            except Exception as e:
                logger_data.error(f"Failed to clarify term '{term}': {e}")
        
        return clarifications
    
    def _extract_with_langchain(self, symptoms: List[str], age: int, gender: str,
                                disease: str, required_features: List[str],
                                additional_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract data using LangChain and Gemini AI with confidence scoring.
        
        Requirements:
        - 8.1: Structured data extraction with Gemini
        - 8.7: Confidence scores for each extracted element
        """
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
            
            # Execute chain with circuit breaker
            if not self.extraction_chain:
                logger.warning("extraction_chain is None (LLM unavailable), using fallback")
                return None
            result = self.execute_with_circuit_breaker(
                lambda: self.extraction_chain.invoke(chain_input)
            )
            
            if result:
                # Parse JSON response from Gemini
                try:
                    parsed_result = json.loads(result)
                    
                    # Add basic features
                    if "mapped_features" not in parsed_result:
                        parsed_result["mapped_features"] = {}
                    
                    parsed_result["mapped_features"]["age"] = age
                    parsed_result["mapped_features"]["gender"] = 1 if gender.lower() == "male" else 0
                    
                    # Ensure confidence scores exist
                    if "confidence_scores" not in parsed_result:
                        parsed_result["confidence_scores"] = {}
                    
                    # Add confidence for basic features
                    parsed_result["confidence_scores"]["age"] = 1.0
                    parsed_result["confidence_scores"]["gender"] = 1.0
                    
                    # Calculate overall confidence if not provided
                    if "overall_confidence" not in parsed_result:
                        confidence_values = list(parsed_result["confidence_scores"].values())
                        parsed_result["overall_confidence"] = (
                            sum(confidence_values) / len(confidence_values) if confidence_values else 0.7
                        )
                    
                    return {
                        "features": parsed_result["mapped_features"],
                        "confidence_scores": parsed_result["confidence_scores"],
                        "extraction_confidence": parsed_result["overall_confidence"],
                        "missing_features": parsed_result.get("missing_features", []),
                        "ambiguous_terms": parsed_result.get("ambiguous_terms", []),
                        "clarifications_needed": parsed_result.get("clarifications_needed", []),
                        "extraction_method": "langchain_gemini_enhanced",
                        "disease": disease
                    }
                    
                except json.JSONDecodeError as e:
                    logger_data.warning(f"Failed to parse LangChain JSON response: {e}")
                    # Try to extract partial information
                    return None
            
            return None
            
        except Exception as e:
            logger_data.error(f"LangChain extraction failed: {str(e)}")
            return None
    
    def _extract_with_rules(self, symptoms: List[str], age: int, gender: str,
                           disease: str, required_features: List[str],
                           additional_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data using rule-based mapping with confidence scores.
        
        Requirements: 8.7 - Provide confidence scores even for rule-based extraction
        """
        logger_data.info("Using rule-based extraction with confidence scoring")
        
        features = {}
        confidence_scores = {}
        
        # Add basic features with high confidence
        features["age"] = age
        features["gender"] = 1 if gender.lower() == "male" else 0
        confidence_scores["age"] = 1.0
        confidence_scores["gender"] = 1.0
        
        # Map symptoms to features
        for symptom in symptoms:
            symptom_lower = symptom.lower().strip().replace(" ", "_")
            
            # Direct mapping
            if symptom_lower in self.symptom_mappings:
                feature_name = self.symptom_mappings[symptom_lower]
                if feature_name in required_features:
                    features[feature_name] = 1  # Binary feature
                    confidence_scores[feature_name] = 0.8  # High confidence for direct mapping
            
            # Check if symptom matches any required feature
            for feature in required_features:
                if symptom_lower in feature or feature in symptom_lower:
                    if feature not in features:
                        features[feature] = 1
                        confidence_scores[feature] = 0.6  # Medium confidence for fuzzy matching
        
        # Add additional info if provided
        if additional_info:
            for key, value in additional_info.items():
                if key in required_features:
                    features[key] = value
                    confidence_scores[key] = 0.9  # High confidence for explicit values
        
        # Fill missing features with defaults
        missing_features = []
        for feature in required_features:
            if feature not in features and feature not in ["age", "gender"]:
                features[feature] = 0  # Default to 0 for binary features
                confidence_scores[feature] = 0.3  # Low confidence for defaults
                missing_features.append(feature)
        
        # Calculate overall confidence
        confidence_values = list(confidence_scores.values())
        overall_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.5
        
        return {
            "features": features,
            "confidence_scores": confidence_scores,
            "extraction_confidence": overall_confidence,
            "missing_features": missing_features,
            "clarifications_needed": [],
            "extraction_method": "rule_based_enhanced",
            "disease": disease
        }
    
    def _get_fallback_extraction(self, symptoms: List[str], age: int, 
                                gender: str, disease: str) -> Dict[str, Any]:
        """
        Get minimal fallback extraction with confidence scores.
        
        Requirements: 8.7 - Include confidence scores in fallback
        """
        return {
            "features": {
                "age": age,
                "gender": 1 if gender.lower() == "male" else 0,
                "symptoms_count": len(symptoms)
            },
            "confidence_scores": {
                "age": 1.0,
                "gender": 1.0,
                "symptoms_count": 0.5
            },
            "extraction_confidence": 0.3,
            "missing_features": ["most_features"],
            "clarifications_needed": ["Please provide more detailed health information"],
            "extraction_method": "fallback_minimal",
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
            "version": "enhanced",
            "framework": "LangChain",
            "supported_diseases": self.get_supported_diseases(),
            "extraction_methods": [
                "langchain_gemini_enhanced",
                "rule_based_enhanced",
                "fallback_minimal"
            ],
            "features": [
                "Natural language symptom parsing",
                "Intelligent feature mapping",
                "Confidence scoring for all extractions",
                "Web search for ambiguous medical terms",
                "Missing data handling",
                "Clarification suggestions",
                "Retry logic with exponential backoff",
                "Circuit breaker for resilience"
            ],
            "capabilities": {
                "llm_available": bool(self.llm),
                "web_search_enabled": bool(self.web_search_tool),
                "monitoring_enabled": bool(self.monitoring),
                "circuit_breaker_enabled": True
            }
        }