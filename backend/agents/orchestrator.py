import logging
import uuid
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseHealthAgent
from .validation import LangChainValidationAgent
from .data_extraction import DataExtractionAgent
from .explanation import LangChainExplanationAgent
from .recommendation import RecommendationAgent
from .lifestyle import LifestyleModificationAgent
from .reflection import ReflectionAgent

try:
    from backend.prediction.predictor import DiseasePredictor
    from backend.common.firebase_db import get_firebase_db
except ImportError:
    try:
        from prediction.predictor import DiseasePredictor
        from common.firebase_db import get_firebase_db
    except ImportError:
        pass

logger_orchestrator = logging.getLogger('health_ai.orchestrator')

class OrchestratorAgent(BaseHealthAgent):
    """
    Main orchestrator agent coordinating the entire health assessment pipeline.
    
    Pipeline Flow:
    1. Validate input (ValidationAgent)
    2. Extract and map data (DataExtractionAgent + Gemini)
    3. Predict disease (ML Model)
    4. Evaluate confidence
    5. Generate explanation (ExplanationAgent + Gemini)
    6. Generate recommendations (RecommendationAgent)
    7. Store in MongoDB
    8. Return complete assessment
    """
    
    # Confidence thresholds
    CONFIDENCE_THRESHOLDS = {
        "LOW": 0.55,
        "MEDIUM": 0.75
    }
    
    def __init__(self):
        """Initialize the orchestrator agent."""
        super().__init__("OrchestratorAgent")
        
        # Initialize all agents
        self.validation_agent = LangChainValidationAgent()
        self.extraction_agent = DataExtractionAgent()
        self.prediction_engine = DiseasePredictor()
        self.explanation_agent = LangChainExplanationAgent()
        self.recommendation_agent = RecommendationAgent()
        self.lifestyle_agent = LifestyleModificationAgent()
        self.reflection_agent = ReflectionAgent()
        
        # Initialize Firebase database
        self.db = get_firebase_db()
        
        logger_orchestrator.info("OrchestratorAgent initialized with complete pipeline including reflection agent")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method - orchestrates the entire pipeline.
        
        Args:
            input_data: Raw user input
            
        Returns:
            Complete assessment result
        """
        self.log_agent_action("start_pipeline", {"user_id": input_data.get("user_id", "anonymous")})
        
        try:
            # Run the complete pipeline
            result = self.run_pipeline(input_data)
            
            return self.format_agent_response(
                success=True,
                data=result,
                message="Health assessment completed successfully"
            )
            
        except Exception as e:
            logger_orchestrator.error(f"Pipeline error: {str(e)}")
            return self.format_agent_response(
                success=False,
                message=f"Pipeline error: {str(e)}",
                data={"error": str(e)}
            )
    
    def run_pipeline(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete health assessment pipeline.
        
        Args:
            user_input: User input data (may include report_metadata and extracted_data)
            
        Returns:
            Complete assessment result
        """
        pipeline_start = datetime.utcnow()
        user_id = user_input.get("user_id", str(uuid.uuid4()))
        
        logger_orchestrator.info(f"Starting pipeline for user: {user_id}")
        
        # Step 1: Validate Input
        self.log_agent_action("step_1_validation")
        validation_result = self.validation_agent.process(user_input)
        
        if not validation_result["success"]:
            return self._blocked_response(
                "validation_failed",
                validation_result["data"]["reason"],
                validation_result["data"]
            )
        
        sanitized_input = validation_result["data"]["sanitized_input"]
        
        # Step 1.5: Merge extracted and manual data if report data is present
        report_metadata = user_input.get("report_metadata")
        extracted_data = user_input.get("extracted_data")
        data_sources = user_input.get("data_sources", {})
        
        if extracted_data and report_metadata and report_metadata.get("has_extracted_data"):
            self.log_agent_action("step_1.5_data_merging")
            logger_orchestrator.info(f"Merging extracted data from report: {report_metadata.get('report_id')}")
            
            sanitized_input = self._merge_data_sources(
                manual_data=sanitized_input,
                extracted_data=extracted_data,
                data_sources=data_sources
            )
        
        # Step 2: Extract and Map Data using Gemini AI
        self.log_agent_action("step_2_data_extraction")
        
        disease = self._select_disease(sanitized_input["symptoms"])
        
        extraction_input = {
            "symptoms": sanitized_input["symptoms"],
            "age": sanitized_input["age"],
            "gender": sanitized_input["gender"],
            "disease": disease,
            "additional_info": user_input.get("additional_info", {})
        }
        
        extraction_result = self.extraction_agent.process(extraction_input)
        
        if not extraction_result["success"]:
            return self._blocked_response(
                "extraction_failed",
                "Failed to extract features from input",
                extraction_result
            )
        
        extracted_features = extraction_result["data"]["features"]
        extraction_confidence = extraction_result["data"]["extraction_confidence"]
        
        # Step 3: ML Prediction
        self.log_agent_action("step_3_prediction", {"disease": disease})
        
        probability, prediction_metadata = self.prediction_engine.predict(disease, extracted_features)
        
        # Step 4: Evaluate Confidence
        confidence = self._evaluate_confidence(probability)
        
        self.log_agent_action("step_4_confidence_evaluation", {
            "probability": probability,
            "confidence": confidence
        })
        
        # Step 5: Generate Explanation using Gemini
        self.log_agent_action("step_5_explanation_generation")
        
        explanation_input = {
            "disease": disease,
            "probability": probability,
            "confidence": confidence,
            "symptoms": sanitized_input["symptoms"]
        }
        
        explanation_result = self.explanation_agent.process(explanation_input)
        explanation_data = explanation_result["data"] if explanation_result["success"] else {}
        
        # Step 6: Generate Recommendations
        self.log_agent_action("step_6_recommendation_generation")
        
        recommendations = self.recommendation_agent.get_recommendations(
            disease=disease,
            probability=probability,
            confidence=confidence,
            symptoms=sanitized_input["symptoms"],
            user_context={"age": sanitized_input["age"], "gender": sanitized_input["gender"]}
        )
        
        # Step 7: Generate Lifestyle Modifications
        self.log_agent_action("step_7_lifestyle_modifications")
        
        lifestyle_input = {
            "disease": disease,
            "confidence": confidence,
            "symptoms": sanitized_input["symptoms"],
            "user_context": {"age": sanitized_input["age"], "gender": sanitized_input["gender"]}
        }
        
        lifestyle_result = self.lifestyle_agent.process(lifestyle_input)
        lifestyle_recommendations = lifestyle_result["data"] if lifestyle_result["success"] else {}
        
        # Step 8: Cross-Verification (Hidden Quality Check)
        self.log_agent_action("step_8_cross_verification")
        
        # Build complete assessment for verification
        complete_assessment = {
            "prediction": {
                "disease": disease,
                "probability": probability,
                "confidence": confidence
            },
            "explanation": explanation_data,
            "recommendations": recommendations,
            "lifestyle_recommendations": lifestyle_recommendations,
            "symptoms": sanitized_input["symptoms"]
        }
        
        # Run reflection agent verification
        verification_result = self.reflection_agent.verify_assessment(complete_assessment)
        
        # Use revised assessment if corrections were made
        if verification_result["recommended_action"] in ["revise", "escalate"]:
            revised = verification_result["revised_assessment"]
            
            # Extract revised components
            if "_verification_info" in revised:
                logger_orchestrator.warning(f"Assessment auto-corrected: {revised['_verification_info']['corrections_applied']}")
            
            # Update components with corrections
            if "prediction" in revised:
                confidence = revised["prediction"].get("confidence", confidence)
            if "recommendations" in revised:
                recommendations = revised["recommendations"]
        
        # Log critical issues for escalation
        if verification_result["severity"] == "critical":
            logger_orchestrator.critical(f"Critical safety issue detected and corrected: {verification_result['issue_count']} issues")
        
        # Step 9: Store in MongoDB
        self.log_agent_action("step_9_database_storage")
        
        storage_ids = self._store_assessment(
            user_id=user_id,
            sanitized_input=sanitized_input,
            disease=disease,
            probability=probability,
            confidence=confidence,
            extraction_data=extraction_result["data"],
            prediction_metadata=prediction_metadata,
            explanation_data=explanation_data,
            recommendations=recommendations,
            lifestyle_recommendations=lifestyle_recommendations,
            report_metadata=report_metadata
        )
        
        # Step 10: Build Complete Response
        pipeline_end = datetime.utcnow()
        processing_time = (pipeline_end - pipeline_start).total_seconds()
        
        complete_response = self._build_response(
            user_id=user_id,
            disease=disease,
            probability=probability,
            confidence=confidence,
            extraction_confidence=extraction_confidence,
            explanation=explanation_data,
            recommendations=recommendations,
            lifestyle_recommendations=lifestyle_recommendations,
            storage_ids=storage_ids,
            processing_time=processing_time,
            prediction_metadata=prediction_metadata
        )
        
        logger_orchestrator.info(f"Pipeline completed for user: {user_id} in {processing_time:.2f}s")
        
        return complete_response
    
    def _select_disease(self, symptoms: list) -> str:
        """
        Select the most likely disease based on symptoms.
        
        Args:
            symptoms: List of symptoms
            
        Returns:
            Disease name
        """
        # Simple keyword-based disease selection
        # In production, this could use a more sophisticated classifier
        
        symptom_text = " ".join(symptoms).lower()
        
        diabetes_keywords = ["thirst", "urination", "weight_loss", "fatigue", "hunger"]
        heart_keywords = ["chest_pain", "shortness_of_breath", "heart", "angina"]
        hypertension_keywords = ["headache", "dizziness", "blood_pressure", "hypertension"]
        
        diabetes_score = sum(1 for kw in diabetes_keywords if kw in symptom_text)
        heart_score = sum(1 for kw in heart_keywords if kw in symptom_text)
        hypertension_score = sum(1 for kw in hypertension_keywords if kw in symptom_text)
        
        scores = {
            "diabetes": diabetes_score,
            "heart_disease": heart_score,
            "hypertension": hypertension_score
        }
        
        selected_disease = max(scores, key=scores.get)
        
        # Default to diabetes if no clear match
        if scores[selected_disease] == 0:
            selected_disease = "diabetes"
        
        logger_orchestrator.info(f"Selected disease: {selected_disease} (scores: {scores})")
        return selected_disease
    
    def _merge_data_sources(self, manual_data: Dict[str, Any], 
                           extracted_data: Dict[str, Any],
                           data_sources: Dict[str, str]) -> Dict[str, Any]:
        """
        Merge extracted data from medical reports with manually entered data.
        User-entered data always takes precedence over extracted data.
        
        Args:
            manual_data: Sanitized manual input from user
            extracted_data: Data extracted from medical report
            data_sources: Map indicating source of each field ('manual', 'extracted', 'merged')
            
        Returns:
            Merged data dictionary with user data taking precedence
        """
        merged = manual_data.copy()
        
        # Merge symptoms - combine both sources if not manually overridden
        if extracted_data.get("symptoms") and data_sources.get("symptoms") != "manual":
            manual_symptoms = set(manual_data.get("symptoms", []))
            extracted_symptoms = set(extracted_data.get("symptoms", []))
            
            # If user provided symptoms, prioritize those but add unique extracted ones
            if manual_symptoms:
                merged["symptoms"] = list(manual_symptoms | extracted_symptoms)
                logger_orchestrator.info(f"Merged symptoms: {len(manual_symptoms)} manual + {len(extracted_symptoms - manual_symptoms)} extracted")
            else:
                merged["symptoms"] = list(extracted_symptoms)
                logger_orchestrator.info(f"Using extracted symptoms: {len(extracted_symptoms)}")
        
        # Merge vitals - user data takes precedence for each field
        if extracted_data.get("vitals"):
            merged_vitals = manual_data.get("additional_info", {}).get("vitals", {}).copy()
            extracted_vitals = extracted_data.get("vitals", {})
            
            for vital_key, vital_value in extracted_vitals.items():
                # Only use extracted value if manual value is not provided
                if vital_key not in merged_vitals or not merged_vitals[vital_key]:
                    if data_sources.get(f"vitals.{vital_key}") != "manual":
                        merged_vitals[vital_key] = vital_value
            
            if "additional_info" not in merged:
                merged["additional_info"] = {}
            merged["additional_info"]["vitals"] = merged_vitals
        
        # Merge lab results - append extracted to manual unless manually overridden
        if extracted_data.get("lab_results") and data_sources.get("lab_results") != "manual":
            manual_labs = manual_data.get("additional_info", {}).get("lab_results", [])
            extracted_labs = extracted_data.get("lab_results", [])
            
            if "additional_info" not in merged:
                merged["additional_info"] = {}
            
            # Combine lab results, avoiding duplicates based on test name
            all_labs = list(manual_labs)
            manual_test_names = {lab.get("test_name") for lab in manual_labs}
            
            for lab in extracted_labs:
                if lab.get("test_name") not in manual_test_names:
                    all_labs.append(lab)
            
            merged["additional_info"]["lab_results"] = all_labs
        
        # Merge medications - append extracted to manual unless manually overridden
        if extracted_data.get("medications") and data_sources.get("medications") != "manual":
            manual_meds = manual_data.get("additional_info", {}).get("medications", [])
            extracted_meds = extracted_data.get("medications", [])
            
            if "additional_info" not in merged:
                merged["additional_info"] = {}
            
            # Combine medications, avoiding duplicates based on name
            all_meds = list(manual_meds)
            manual_med_names = {med.get("name") for med in manual_meds}
            
            for med in extracted_meds:
                if med.get("name") not in manual_med_names:
                    all_meds.append(med)
            
            merged["additional_info"]["medications"] = all_meds
        
        # Merge diagnoses - append extracted to manual unless manually overridden
        if extracted_data.get("diagnoses") and data_sources.get("diagnoses") != "manual":
            manual_diagnoses = manual_data.get("additional_info", {}).get("diagnoses", [])
            extracted_diagnoses = extracted_data.get("diagnoses", [])
            
            if "additional_info" not in merged:
                merged["additional_info"] = {}
            
            # Combine diagnoses, avoiding duplicates based on condition
            all_diagnoses = list(manual_diagnoses)
            manual_conditions = {diag.get("condition") for diag in manual_diagnoses}
            
            for diag in extracted_diagnoses:
                if diag.get("condition") not in manual_conditions:
                    all_diagnoses.append(diag)
            
            merged["additional_info"]["diagnoses"] = all_diagnoses
        
        # Store confidence scores from extraction
        if extracted_data.get("confidence_scores"):
            if "additional_info" not in merged:
                merged["additional_info"] = {}
            merged["additional_info"]["extraction_confidence_scores"] = extracted_data["confidence_scores"]
        
        logger_orchestrator.info("Data merge completed - user data prioritized")
        return merged
    
    def _evaluate_confidence(self, probability: float) -> str:
        """
        Evaluate confidence level based on probability.
        
        Args:
            probability: Prediction probability
            
        Returns:
            Confidence level (LOW, MEDIUM, HIGH)
        """
        if probability < self.CONFIDENCE_THRESHOLDS["LOW"]:
            return "LOW"
        elif probability < self.CONFIDENCE_THRESHOLDS["MEDIUM"]:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _store_assessment(self, user_id: str, sanitized_input: Dict[str, Any],
                          disease: str, probability: float, confidence: str,
                          extraction_data: Dict[str, Any], prediction_metadata: Dict[str, Any],
                          explanation_data: Dict[str, Any], recommendations: Dict[str, Any],
                          lifestyle_recommendations: Dict[str, Any] = None,
                          report_metadata: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Store complete assessment in Firebase Firestore.
        
        Args:
            report_metadata: Optional metadata about uploaded medical report
        
        Returns:
            Dictionary of storage IDs
        """
        try:
            # Store complete assessment in one document
            assessment_data = {
                'symptoms': sanitized_input["symptoms"],
                'age': sanitized_input["age"],
                'gender': sanitized_input["gender"],
                'disease': disease,
                'probability': probability,
                'confidence': confidence,
                'extraction_data': extraction_data,
                'prediction_metadata': prediction_metadata,
                'explanation': explanation_data,
                'recommendations': recommendations,
                'lifestyle_recommendations': lifestyle_recommendations or {}
            }
            
            # Include report metadata if present
            if report_metadata:
                assessment_data['report_metadata'] = {
                    'report_id': report_metadata.get('report_id'),
                    'extraction_job_id': report_metadata.get('extraction_job_id'),
                    'has_extracted_data': report_metadata.get('has_extracted_data', False)
                }
                logger_orchestrator.info(f"Assessment linked to report: {report_metadata.get('report_id')}")
            
            assessment_id = self.db.store_assessment(user_id, assessment_data)
            
            # Update report metadata with assessment ID if report was uploaded
            if report_metadata and report_metadata.get('report_id'):
                try:
                    self.db.db.collection('medical_reports').document(report_metadata['report_id']).update({
                        'associated_assessment_id': assessment_id
                    })
                except Exception as e:
                    logger_orchestrator.warning(f"Could not link report to assessment: {str(e)}")
            
            # Store prediction separately for querying
            prediction_id = self.db.store_prediction(
                user_id=user_id,
                assessment_id=assessment_id,
                prediction_data={
                    'disease': disease,
                    'probability': probability,
                    'confidence': confidence,
                    'model_version': prediction_metadata.get("model_version", "unknown")
                }
            )
            
            # Store explanation
            explanation_id = self.db.store_explanation(
                assessment_id=assessment_id,
                explanation_data=explanation_data
            )
            
            # Store recommendation
            recommendation_id = self.db.store_recommendation(
                assessment_id=assessment_id,
                recommendation_data=recommendations
            )
            
            # Store audit log
            audit_payload = {
                "disease": disease,
                "confidence": confidence,
                "probability": probability
            }
            
            # Include report info in audit log if present
            if report_metadata:
                audit_payload["report_id"] = report_metadata.get('report_id')
                audit_payload["has_extracted_data"] = report_metadata.get('has_extracted_data', False)
            
            self.db.store_audit_log(
                event_type="health_assessment_completed",
                user_id=user_id,
                payload=audit_payload
            )
            
            return {
                "assessment_id": assessment_id,
                "prediction_id": prediction_id,
                "explanation_id": explanation_id,
                "recommendation_id": recommendation_id
            }
            
        except Exception as e:
            logger_orchestrator.error(f"Error storing assessment: {str(e)}")
            return {}
    
    def _build_response(self, user_id: str, disease: str, probability: float,
                        confidence: str, extraction_confidence: float,
                        explanation: Dict[str, Any], recommendations: Dict[str, Any],
                        lifestyle_recommendations: Dict[str, Any],
                        storage_ids: Dict[str, str], processing_time: float,
                        prediction_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Build the complete response for the frontend."""
        return {
            "user_id": user_id,
            "assessment_id": storage_ids.get("prediction_id"),
            "prediction": {
                "disease": disease.replace("_", " ").title(),
                "probability": round(probability, 4),
                "probability_percent": round(probability * 100, 2),
                "confidence": confidence,
                "model_version": prediction_metadata.get("model_version")
            },
            "extraction": {
                "confidence": extraction_confidence,
                "method": "gemini_ai_extraction"
            },
            "explanation": explanation,
            "recommendations": recommendations,
            "lifestyle_recommendations": lifestyle_recommendations,
            "metadata": {
                "processing_time_seconds": round(processing_time, 2),
                "timestamp": datetime.utcnow().isoformat(),
                "storage_ids": storage_ids,
                "pipeline_version": "v1.2"
            }
        }
    
    def _blocked_response(self, reason: str, message: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Build a blocked response when pipeline cannot proceed."""
        return {
            "blocked": True,
            "reason": reason,
            "message": message,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get status of all pipeline components."""
        return {
            "orchestrator": self.get_agent_status(),
            "validation_agent": self.validation_agent.get_agent_status(),
            "extraction_agent": self.extraction_agent.get_agent_status(),
            "explanation_agent": self.explanation_agent.get_agent_status(),
            "prediction_engine": {
                "supported_diseases": self.prediction_engine.get_supported_diseases(),
                "model_version": self.prediction_engine.model_version
            },
            "database": {
                "connected": self.db.db is not None
            }
        }