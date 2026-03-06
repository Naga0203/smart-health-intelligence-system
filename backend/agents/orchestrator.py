import logging
import uuid
import asyncio
from typing import Dict, Any, List, Optional, Callable, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError
import time

from .infrastructure.enhanced_base_agent import EnhancedBaseHealthAgent
from .infrastructure.config import AgentConfig
from .validation import LangChainValidationAgent
from .data_extraction import DataExtractionAgent
from .lifestyle import LifestyleModificationAgent
from .reflection import ReflectionAgent
from .severity import SeverityAgent
from .explanation import LangChainExplanationAgent
from .recommendation import RecommendationAgent

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

class OrchestratorAgent(EnhancedBaseHealthAgent):
    """
    Enhanced autonomous orchestrator agent coordinating the health assessment pipeline.
    
    Key Enhancements:
    - Autonomous agent selection based on input characteristics
    - Parallel execution of independent agents
    - Context sharing between agents
    - Timeout management with graceful degradation
    - Failure recovery with alternative strategies
    - Comprehensive monitoring and error handling
    
    Pipeline Flow:
    1. Validate input (ValidationAgent)
    2. Autonomous agent selection based on input
    3. Parallel execution of independent agents (extraction, severity)
    4. Sequential execution of dependent agents (prediction, explanation, recommendations)
    5. Cross-verification (ReflectionAgent)
    6. Store in Firebase
    7. Return complete assessment
    
    Requirements: 1.1, 1.2, 1.3, 1.5, 5.1, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 1.6
    """
    
    # Confidence thresholds
    CONFIDENCE_THRESHOLDS = {
        "LOW": 0.55,
        "MEDIUM": 0.75
    }
    
    # Agent timeout configuration
    AGENT_TIMEOUT = 30  # seconds (increased for autonomous operations)
    PARALLEL_TIMEOUT = 45  # seconds for parallel execution
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the enhanced orchestrator agent.
        
        Requirements: 1.1, 1.2, 1.3 - LangChain integration with enhanced capabilities
        """
        super().__init__("OrchestratorAgent", config)
        
        # Initialize all agents with shared context manager
        self.validation_agent = LangChainValidationAgent()
        self.extraction_agent = DataExtractionAgent()
        self.severity_agent = SeverityAgent()
        self.prediction_engine = DiseasePredictor()
        self.explanation_agent = LangChainExplanationAgent()
        self.recommendation_agent = RecommendationAgent()
        self.lifestyle_agent = LifestyleModificationAgent()
        self.reflection_agent = ReflectionAgent()
        
        # Agent registry for autonomous selection
        self.agent_registry = {
            'validation': self.validation_agent,
            'extraction': self.extraction_agent,
            'severity': self.severity_agent,
            'explanation': self.explanation_agent,
            'recommendation': self.recommendation_agent,
            'lifestyle': self.lifestyle_agent,
            'reflection': self.reflection_agent
        }
        
        # Initialize Firebase database
        self.db = get_firebase_db()
        
        # Thread pool for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger_orchestrator.info("Enhanced OrchestratorAgent initialized with autonomous capabilities")
    
    
    def _select_agents_for_input(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Autonomously select which agents to invoke based on input characteristics.
        
        Requirements: 5.1 - Autonomous agent selection based on input
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            List of agent names to invoke
        """
        selected_agents = ['validation']  # Always start with validation
        
        # Analyze input characteristics
        has_report = bool(input_data.get('report_metadata') or input_data.get('extracted_data'))
        has_symptoms = bool(input_data.get('symptoms'))
        has_vitals = bool(input_data.get('additional_info', {}).get('vitals'))
        has_lab_results = bool(input_data.get('additional_info', {}).get('lab_results'))
        
        # Use decision engine for autonomous selection
        context = {
            'has_report': has_report,
            'has_symptoms': has_symptoms,
            'has_vitals': has_vitals,
            'has_lab_results': has_lab_results,
            'input_keys': list(input_data.keys())
        }
        
        # Always need extraction for feature mapping
        selected_agents.append('extraction')
        
        # Add severity assessment if symptoms present
        if has_symptoms or has_vitals:
            selected_agents.append('severity')
        
        # Always need explanation and recommendations
        selected_agents.extend(['explanation', 'recommendation', 'lifestyle'])
        
        # Always end with reflection for quality check
        selected_agents.append('reflection')
        
        self.log_agent_action("agent_selection", {
            "selected_agents": selected_agents,
            "input_characteristics": context
        })
        
        logger_orchestrator.info(f"Selected {len(selected_agents)} agents for execution: {selected_agents}")
        
        return selected_agents
    
    def _execute_agents_parallel(
        self,
        agents_and_inputs: List[Tuple[str, Any, Dict[str, Any]]],
        timeout: Optional[float] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Execute multiple independent agents in parallel.
        
        Requirements: 6.7 - Parallel execution of independent agents
        
        Args:
            agents_and_inputs: List of (agent_name, agent_instance, input_data) tuples
            timeout: Timeout for parallel execution
            
        Returns:
            Dictionary mapping agent names to results
        """
        timeout = timeout or self.PARALLEL_TIMEOUT
        results = {}
        
        self.log_agent_action("parallel_execution_start", {
            "agent_count": len(agents_and_inputs),
            "timeout": timeout
        })
        
        # Submit all agents to thread pool
        future_to_agent = {}
        for agent_name, agent, input_data in agents_and_inputs:
            future = self.executor.submit(self._execute_single_agent, agent_name, agent, input_data)
            future_to_agent[future] = agent_name
        
        # Collect results with timeout
        start_time = time.time()
        for future in as_completed(future_to_agent, timeout=timeout):
            agent_name = future_to_agent[future]
            try:
                result = future.result()
                results[agent_name] = result
                
                # Share result in context for other agents
                self.context_manager.share_context(agent_name, result)
                
                logger_orchestrator.info(f"Parallel agent {agent_name} completed successfully")
                
            except Exception as e:
                logger_orchestrator.error(f"Parallel agent {agent_name} failed: {e}")
                results[agent_name] = self.format_agent_response(
                    success=False,
                    message=f"Agent {agent_name} failed",
                    data={'error': str(e)}
                )
        
        elapsed = time.time() - start_time
        self.log_agent_action("parallel_execution_complete", {
            "elapsed_seconds": elapsed,
            "successful_agents": sum(1 for r in results.values() if r.get('success', False))
        })
        
        return results
    
    def _execute_single_agent(
        self,
        agent_name: str,
        agent: Any,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single agent with timeout and error handling.
        
        Requirements: 6.5 - Timeout management, 9.1 - Error handling
        
        Args:
            agent_name: Name of the agent
            agent: Agent instance
            input_data: Input data for the agent
            
        Returns:
            Agent result
        """
        try:
            # Execute with timeout using base class method
            result = self.execute_with_timeout(
                lambda: agent.process(input_data),
                timeout=self.AGENT_TIMEOUT
            )
            
            return result
            
        except TimeoutError:
            logger_orchestrator.error(f"{agent_name} timeout after {self.AGENT_TIMEOUT}s")
            return self.format_agent_response(
                success=False,
                message=f"{agent_name} timed out",
                data={"error": "timeout", "timeout_seconds": self.AGENT_TIMEOUT}
            )
            
        except Exception as e:
            logger_orchestrator.error(f"{agent_name} crashed: {str(e)}", exc_info=True)
            return self.format_agent_response(
                success=False,
                message=f"{agent_name} encountered an error",
                data={"error": str(e), "agent": agent_name}
            )
    
    def _handle_agent_failure(
        self,
        agent_name: str,
        error: Exception,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle agent failure with recovery strategies.
        
        Requirements: 6.6 - Failure recovery logic
        
        Args:
            agent_name: Name of failed agent
            error: Exception that occurred
            input_data: Original input data
            
        Returns:
            Recovery result or error response
        """
        self.log_agent_action("agent_failure", {
            "agent": agent_name,
            "error": str(error)
        })
        
        # Use decision engine to determine recovery strategy
        situation = {
            'agent_name': agent_name,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'is_timeout': isinstance(error, TimeoutError),
            'is_critical': agent_name in ['validation', 'extraction']
        }
        
        should_retry = not isinstance(error, TimeoutError)  # Don't retry timeouts
        
        if should_retry:
            logger_orchestrator.info(f"Attempting retry for {agent_name}")
            try:
                # Retry with exponential backoff
                agent = self.agent_registry.get(agent_name)
                if agent:
                    result = self.execute_with_retry(
                        lambda: agent.process(input_data),
                        max_retries=2
                    )
                    logger_orchestrator.info(f"Retry successful for {agent_name}")
                    return result
            except Exception as retry_error:
                logger_orchestrator.error(f"Retry failed for {agent_name}: {retry_error}")
        
        # Check if agent is critical
        if situation['is_critical']:
            logger_orchestrator.critical(f"Critical agent {agent_name} failed, cannot continue")
            return self.format_agent_response(
                success=False,
                message=f"Critical agent {agent_name} failed",
                data={'error': str(error), 'recovery': 'failed'}
            )
        
        # For non-critical agents, return degraded response
        logger_orchestrator.warning(f"Non-critical agent {agent_name} failed, continuing with degraded output")
        return self.format_agent_response(
            success=False,
            message=f"Agent {agent_name} unavailable",
            data={'error': str(error), 'recovery': 'degraded'}
        )
    
    async def _execute_agent_with_timeout(self, agent, input_data: Dict[str, Any], 
                                          agent_name: str, timeout: float = None) -> Dict[str, Any]:
        """
        Execute agent with timeout and exception handling.
        
        Requirements:
        - 4.3: Timeout cancellation (5 seconds)
        - 4.5: Handle agent crashes with exception catching
        
        Args:
            agent: Agent instance to execute
            input_data: Input data for the agent
            agent_name: Name of the agent for logging
            timeout: Timeout in seconds (default: AGENT_TIMEOUT)
            
        Returns:
            Agent result or error response
        """
        timeout = timeout or self.AGENT_TIMEOUT
        
        try:
            # Run agent with timeout
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                asyncio.wait_for(
                    self._async_agent_process(agent, input_data),
                    timeout=timeout
                )
            )
            loop.close()
            
            return result
            
        except asyncio.TimeoutError:
            logger_orchestrator.error(f"{agent_name} timeout after {timeout}s")
            return self.format_agent_response(
                success=False,
                message=f"{agent_name} timed out",
                data={"error": "timeout", "timeout_seconds": timeout}
            )
            
        except Exception as e:
            logger_orchestrator.error(f"{agent_name} crashed: {str(e)}", exc_info=True)
            return self.format_agent_response(
                success=False,
                message=f"{agent_name} encountered an error",
                data={"error": str(e), "agent": agent_name}
            )
    
    async def _async_agent_process(self, agent, input_data):
        """Async wrapper for agent processing."""
        return await asyncio.get_event_loop().run_in_executor(
            None, agent.process, input_data
        )
    
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
        Execute the complete health assessment pipeline with autonomous coordination.
        
        Requirements:
        - 5.1: Autonomous agent selection
        - 6.1: Coordinate multiple agents
        - 6.2: Determine next agent autonomously
        - 6.3, 6.4: Share context between agents
        - 6.7: Parallel execution of independent agents
        - 6.8: Aggregate results
        
        Args:
            user_input: User input data (may include report_metadata and extracted_data)
            
        Returns:
            Complete assessment result
        """
        pipeline_start = datetime.utcnow()
        user_id = user_input.get("user_id", str(uuid.uuid4()))
        
        # Set session ID for context tracking
        session_id = f"session_{user_id}_{int(time.time())}"
        self.context_manager.set_session_id(session_id)
        
        logger_orchestrator.info(f"Starting autonomous pipeline for user: {user_id}, session: {session_id}")
        
        # Step 1: Validate Input
        self.log_agent_action("step_1_validation")
        validation_result = self._execute_single_agent('validation', self.validation_agent, user_input)
        
        if not validation_result["success"]:
            return self._blocked_response(
                "validation_failed",
                validation_result["data"]["reason"],
                validation_result["data"]
            )
        
        sanitized_input = validation_result["data"]["sanitized_input"]
        self.context_manager.add_to_context('sanitized_input', sanitized_input)
        
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
            self.context_manager.add_to_context('merged_input', sanitized_input)
        
        # Step 2: Autonomous Agent Selection
        self.log_agent_action("step_2_autonomous_agent_selection")
        selected_agents = self._select_agents_for_input(sanitized_input)
        
        # Step 3: Parallel Execution of Independent Agents (extraction + severity)
        self.log_agent_action("step_3_parallel_execution")
        
        disease = self._select_disease(sanitized_input["symptoms"])
        self.context_manager.add_to_context('selected_disease', disease)
        
        extraction_input = {
            "symptoms": sanitized_input["symptoms"],
            "age": sanitized_input["age"],
            "gender": sanitized_input["gender"],
            "disease": disease,
            "additional_info": user_input.get("additional_info", {})
        }
        
        severity_input = {
            "symptoms": sanitized_input["symptoms"],
            "vitals": sanitized_input.get("additional_info", {}).get("vitals", {}),
            "disease": disease
        }
        
        # Execute extraction and severity in parallel
        parallel_agents = [
            ('extraction', self.extraction_agent, extraction_input),
            ('severity', self.severity_agent, severity_input)
        ]
        
        parallel_results = self._execute_agents_parallel(parallel_agents)
        
        extraction_result = parallel_results.get('extraction', {})
        severity_result = parallel_results.get('severity', {})
        
        # Handle extraction failure with recovery
        if not extraction_result.get("success"):
            extraction_result = self._handle_agent_failure(
                'extraction',
                Exception(extraction_result.get('data', {}).get('error', 'Unknown error')),
                extraction_input
            )
            
            if not extraction_result.get("success"):
                return self._blocked_response(
                    "extraction_failed",
                    "Failed to extract features from input",
                    extraction_result
                )
        
        extracted_features = extraction_result["data"]["features"]
        extraction_confidence = extraction_result["data"]["extraction_confidence"]
        
        # Store severity assessment in context
        if severity_result.get("success"):
            self.context_manager.add_to_context('severity_assessment', severity_result["data"])
        
        # Step 4: ML Prediction
        self.log_agent_action("step_3_prediction", {"disease": disease})
        
        try:
            probability, prediction_metadata = self.execute_with_retry(
                lambda: self.prediction_engine.predict(disease, extracted_features),
                max_retries=2
            )
        except Exception as e:
            logger_orchestrator.error(f"Prediction failed: {e}")
            return self._blocked_response(
                "prediction_failed",
                f"Prediction engine error: {str(e)}",
                {"error": str(e)}
            )
        
        # Step 5: Evaluate Confidence
        confidence = self._evaluate_confidence(probability)
        
        self.log_agent_action("step_4_confidence_evaluation", {
            "probability": probability,
            "confidence": confidence
        })
        
        # Add prediction to context for downstream agents
        self.context_manager.add_to_context('prediction', {
            'disease': disease,
            'probability': probability,
            'confidence': confidence
        })
        
        # Step 6: Sequential Execution of Dependent Agents
        self.log_agent_action("step_5_sequential_execution")
        
        # Generate Explanation
        explanation_input = {
            "disease": disease,
            "probability": probability,
            "confidence": confidence,
            "symptoms": sanitized_input["symptoms"],
            "severity": severity_result.get("data", {}) if severity_result.get("success") else {}
        }
        
        explanation_result = self._execute_single_agent('explanation', self.explanation_agent, explanation_input)
        explanation_data = explanation_result["data"] if explanation_result["success"] else {}
        
        # Generate Recommendations
        recommendations = self._execute_single_agent(
            'recommendation',
            self.recommendation_agent,
            {
                "disease": disease,
                "probability": probability,
                "confidence": confidence,
                "symptoms": sanitized_input["symptoms"],
                "user_context": {"age": sanitized_input["age"], "gender": sanitized_input["gender"]},
                "severity": severity_result.get("data", {}) if severity_result.get("success") else {}
            }
        )
        
        recommendations_data = recommendations.get("data", {}) if recommendations.get("success") else {}
        
        # Generate Lifestyle Modifications
        lifestyle_input = {
            "disease": disease,
            "confidence": confidence,
            "symptoms": sanitized_input["symptoms"],
            "user_context": {"age": sanitized_input["age"], "gender": sanitized_input["gender"]}
        }
        
        lifestyle_result = self._execute_single_agent('lifestyle', self.lifestyle_agent, lifestyle_input)
        lifestyle_recommendations = lifestyle_result["data"] if lifestyle_result["success"] else {}
        
        # Step 7: Cross-Verification with Reflection Agent
        self.log_agent_action("step_6_cross_verification")
        
        # Build complete assessment for verification
        complete_assessment = {
            "prediction": {
                "disease": disease,
                "probability": probability,
                "confidence": confidence
            },
            "explanation": explanation_data,
            "recommendations": recommendations_data,
            "lifestyle_recommendations": lifestyle_recommendations,
            "symptoms": sanitized_input["symptoms"],
            "severity": severity_result.get("data", {}) if severity_result.get("success") else {}
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
                recommendations_data = revised["recommendations"]
        
        # Log critical issues for escalation
        if verification_result["severity"] == "critical":
            logger_orchestrator.critical(f"Critical safety issue detected and corrected: {verification_result['issue_count']} issues")
        
        # Step 8: Store in Firebase
        self.log_agent_action("step_7_database_storage")
        
        storage_ids = self._store_assessment(
            user_id=user_id,
            sanitized_input=sanitized_input,
            disease=disease,
            probability=probability,
            confidence=confidence,
            extraction_data=extraction_result["data"],
            prediction_metadata=prediction_metadata,
            explanation_data=explanation_data,
            recommendations=recommendations_data,
            lifestyle_recommendations=lifestyle_recommendations,
            report_metadata=report_metadata,
            severity_data=severity_result.get("data", {}) if severity_result.get("success") else {}
        )
        
        # Step 9: Build Complete Response
        pipeline_end = datetime.utcnow()
        processing_time = (pipeline_end - pipeline_start).total_seconds()
        
        complete_response = self._build_response(
            user_id=user_id,
            disease=disease,
            probability=probability,
            confidence=confidence,
            extraction_confidence=extraction_confidence,
            explanation=explanation_data,
            recommendations=recommendations_data,
            lifestyle_recommendations=lifestyle_recommendations,
            storage_ids=storage_ids,
            processing_time=processing_time,
            prediction_metadata=prediction_metadata,
            severity_data=severity_result.get("data", {}) if severity_result.get("success") else {}
        )
        
        # Clear context at end of session
        self.context_manager.clear_context()
        
        logger_orchestrator.info(f"Autonomous pipeline completed for user: {user_id} in {processing_time:.2f}s")
        
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
                          report_metadata: Dict[str, Any] = None,
                          severity_data: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Store complete assessment in Firebase Firestore.
        
        Args:
            report_metadata: Optional metadata about uploaded medical report
            severity_data: Optional severity assessment data
        
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
                'lifestyle_recommendations': lifestyle_recommendations or {},
                'severity_assessment': severity_data or {}
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
                    report_ref = self.db.db.collection('medical_reports').document(report_metadata['report_id'])
                    # Check if report exists before updating
                    report_doc = report_ref.get()
                    if report_doc.exists:
                        report_ref.update({
                            'associated_assessment_id': assessment_id
                        })
                        logger_orchestrator.info(f"Successfully linked report {report_metadata['report_id']} to assessment {assessment_id}")
                    else:
                        logger_orchestrator.warning(f"Report {report_metadata['report_id']} not found in Firestore, skipping link")
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
                        prediction_metadata: Dict[str, Any],
                        severity_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Build the complete response for the frontend.
        
        Requirements: 6.8 - Aggregate results from multiple agents
        """
        return {
            "user_id": user_id,
            "assessment_id": storage_ids.get("assessment_id"),
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
            "severity": severity_data or {},
            "explanation": explanation,
            "recommendations": recommendations,
            "lifestyle_recommendations": lifestyle_recommendations,
            "metadata": {
                "processing_time_seconds": round(processing_time, 2),
                "timestamp": datetime.utcnow().isoformat(),
                "storage_ids": storage_ids,
                "pipeline_version": "v2.0_autonomous",
                "agents_executed": list(self.context_manager.get_shared_context().keys()) if self.context_manager.get_shared_context() else []
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
        """
        Get status of all pipeline components.
        
        Returns:
            Complete pipeline status including all agents and infrastructure
        """
        return {
            "orchestrator": self.get_agent_status(),
            "agents": {
                "validation": self.validation_agent.get_agent_status(),
                "extraction": self.extraction_agent.get_agent_status(),
                "severity": self.severity_agent.get_agent_status(),
                "explanation": self.explanation_agent.get_agent_status(),
                "recommendation": self.recommendation_agent.get_agent_status(),
                "lifestyle": self.lifestyle_agent.get_agent_status(),
                "reflection": self.reflection_agent.get_agent_status()
            },
            "prediction_engine": {
                "supported_diseases": self.prediction_engine.get_supported_diseases(),
                "model_version": self.prediction_engine.model_version
            },
            "infrastructure": {
                "context_manager": self.context_manager.get_status(),
                "decision_engine": self.decision_engine.get_statistics(),
                "circuit_breaker": self.circuit_breaker.get_state()
            },
            "database": {
                "connected": self.db.db is not None
            }
        }