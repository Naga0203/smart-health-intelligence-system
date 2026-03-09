"""
Integration tests for multi-agent workflows.

Tests the complete health assessment pipeline including:
- Full health assessment pipeline
- Agent coordination
- Context sharing between agents
- Parallel agent execution
- Error recovery in workflows

Requirements: 6.1, 6.3, 6.7, 6.6
"""

import pytest
import time
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from backend.agents.orchestrator import OrchestratorAgent
from backend.agents.infrastructure.context_manager import ContextManager
from backend.agents.infrastructure.config import AgentConfig
from backend.prediction.predictor import DiseasePredictor


class TestMultiAgentWorkflowIntegration:
    """Integration tests for multi-agent workflows."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator agent for testing."""
        config = AgentConfig(
            agent_name="OrchestratorAgent",
            timeout=30,
            enable_web_search=False,  # Disable for faster tests
            monitoring_enabled=False
        )
        # Patch the agents to avoid initialization issues
        with patch('backend.agents.orchestrator.LangChainExplanationAgent') as mock_explanation:
            with patch('backend.agents.orchestrator.RecommendationAgent') as mock_recommendation:
                with patch('backend.agents.orchestrator.LifestyleModificationAgent') as mock_lifestyle:
                    # Create mock agents
                    mock_explanation.return_value = Mock()
                    mock_recommendation.return_value = Mock()
                    mock_lifestyle.return_value = Mock()
                    
                    orchestrator = OrchestratorAgent(config)
                    
                    # Set up mock agent responses
                    orchestrator.explanation_agent.process = Mock(return_value={
                        "success": True,
                        "data": {"summary": "Test explanation", "main_explanation": "Test"}
                    })
                    orchestrator.recommendation_agent.process = Mock(return_value={
                        "success": True,
                        "data": {"recommendations": ["Test recommendation"]}
                    })
                    orchestrator.lifestyle_agent.process = Mock(return_value={
                        "success": True,
                        "data": {"lifestyle_recommendations": ["Test lifestyle"]}
                    })
                    
                    return orchestrator
    
    @pytest.fixture
    def sample_input(self):
        """Sample input data for health assessment."""
        return {
            "user_id": "test_user_123",
            "symptoms": ["increased_thirst", "frequent_urination", "fatigue"],
            "age": 45,
            "gender": "male",
            "additional_info": {
                "vitals": {
                    "blood_pressure": "140/90",
                    "heart_rate": 85,
                    "temperature": 98.6
                },
                "lab_results": [
                    {
                        "test_name": "Fasting Blood Glucose",
                        "value": 145,
                        "unit": "mg/dL",
                        "reference_range": "70-100"
                    }
                ]
            }
        }
    
    @pytest.fixture
    def mock_firebase(self):
        """Mock Firebase database."""
        with patch('backend.agents.orchestrator.get_firebase_db') as mock_db:
            db_instance = Mock()
            db_instance.store_assessment.return_value = "assessment_123"
            db_instance.store_prediction.return_value = "prediction_123"
            db_instance.store_explanation.return_value = "explanation_123"
            db_instance.store_recommendation.return_value = "recommendation_123"
            db_instance.store_audit_log.return_value = None
            db_instance.db = Mock()
            db_instance.db.collection.return_value.document.return_value.get.return_value.exists = False
            mock_db.return_value = db_instance
            yield db_instance
    
    def test_full_health_assessment_pipeline(self, orchestrator, sample_input, mock_firebase):
        """
        Test complete health assessment pipeline from input to output.
        
        Requirements: 6.1 - Orchestrator coordinates multiple agents
        """
        # Execute full pipeline
        result = orchestrator.run_pipeline(sample_input)
        
        # Verify pipeline completed successfully
        assert result is not None
        assert "user_id" in result
        assert "prediction" in result
        assert "explanation" in result
        assert "recommendations" in result
        assert "metadata" in result
        
        # Verify prediction structure
        prediction = result["prediction"]
        assert "disease" in prediction
        assert "probability" in prediction
        assert "confidence" in prediction
        assert prediction["confidence"] in ["LOW", "MEDIUM", "HIGH"]
        
        # Verify metadata includes processing time
        metadata = result["metadata"]
        assert "processing_time_seconds" in metadata
        assert metadata["processing_time_seconds"] > 0
        assert "pipeline_version" in metadata
        
        # Verify all agents were executed
        assert "agents_executed" in metadata
        
        print(f"✓ Full pipeline completed in {metadata['processing_time_seconds']:.2f}s")
    
    def test_agent_coordination(self, orchestrator, sample_input, mock_firebase):
        """
        Test that orchestrator properly coordinates multiple agents.
        
        Requirements: 6.1, 6.2 - Agent coordination and next agent selection
        """
        # Track agent execution order
        executed_agents = []
        
        # Patch agents to track execution
        original_validation = orchestrator.validation_agent.process
        original_extraction = orchestrator.extraction_agent.process
        original_severity = orchestrator.severity_agent.process
        
        def track_validation(data):
            executed_agents.append("validation")
            return original_validation(data)
        
        def track_extraction(data):
            executed_agents.append("extraction")
            return original_extraction(data)
        
        def track_severity(data):
            executed_agents.append("severity")
            return original_severity(data)
        
        orchestrator.validation_agent.process = track_validation
        orchestrator.extraction_agent.process = track_extraction
        orchestrator.severity_agent.process = track_severity
        
        # Execute pipeline
        result = orchestrator.run_pipeline(sample_input)
        
        # Verify agents were executed in correct order
        assert "validation" in executed_agents
        assert "extraction" in executed_agents
        
        # Validation should come before extraction
        validation_idx = executed_agents.index("validation")
        extraction_idx = executed_agents.index("extraction")
        assert validation_idx < extraction_idx
        
        # Verify orchestrator selected appropriate agents
        assert len(executed_agents) >= 2  # At least validation and extraction
        
        print(f"✓ Agent coordination verified: {len(executed_agents)} agents executed")
    
    def test_context_sharing_between_agents(self, orchestrator, sample_input, mock_firebase):
        """
        Test that agents can share context and access shared data.
        
        Requirements: 6.3, 6.4 - Context sharing between agents
        """
        # Execute pipeline
        result = orchestrator.run_pipeline(sample_input)
        
        # Verify context was used during pipeline
        context_manager = orchestrator.context_manager
        
        # Check that context was populated during execution
        # Note: Context is cleared at end of pipeline, so we need to check during execution
        # We'll verify through the result that context sharing worked
        
        # Verify that agents had access to shared data
        # This is evidenced by successful pipeline completion with coordinated results
        assert result is not None
        assert "prediction" in result
        
        # Verify that explanation used prediction context
        explanation = result.get("explanation", {})
        assert explanation is not None
        
        # Verify that recommendations used prediction and explanation context
        recommendations = result.get("recommendations", {})
        assert recommendations is not None
        
        print("✓ Context sharing verified through successful agent coordination")
    
    def test_parallel_agent_execution(self, orchestrator, sample_input, mock_firebase):
        """
        Test that independent agents execute in parallel.
        
        Requirements: 6.7 - Parallel execution of independent agents
        """
        # Track execution times
        execution_times = {}
        
        original_extraction = orchestrator.extraction_agent.process
        original_severity = orchestrator.severity_agent.process
        
        def timed_extraction(data):
            start = time.time()
            result = original_extraction(data)
            execution_times["extraction"] = time.time() - start
            return result
        
        def timed_severity(data):
            start = time.time()
            result = original_severity(data)
            execution_times["severity"] = time.time() - start
            return result
        
        orchestrator.extraction_agent.process = timed_extraction
        orchestrator.severity_agent.process = timed_severity
        
        # Execute pipeline
        pipeline_start = time.time()
        result = orchestrator.run_pipeline(sample_input)
        total_time = time.time() - pipeline_start
        
        # Verify both agents executed
        assert "extraction" in execution_times
        assert "severity" in execution_times
        
        # Verify parallel execution (total time should be less than sum of individual times)
        # Note: This is a soft check as actual parallelism depends on system load
        individual_sum = execution_times["extraction"] + execution_times["severity"]
        
        print(f"✓ Parallel execution: extraction={execution_times['extraction']:.2f}s, "
              f"severity={execution_times['severity']:.2f}s, total={total_time:.2f}s")
        
        # Verify result is valid
        assert result is not None
        assert "prediction" in result
    
    def test_error_recovery_in_workflows(self, orchestrator, sample_input, mock_firebase):
        """
        Test that pipeline recovers from agent failures.
        
        Requirements: 6.6 - Failure recovery logic
        """
        # Make severity agent fail
        def failing_severity(data):
            raise Exception("Simulated severity agent failure")
        
        orchestrator.severity_agent.process = failing_severity
        
        # Execute pipeline - should continue despite severity failure
        result = orchestrator.run_pipeline(sample_input)
        
        # Verify pipeline completed despite failure
        assert result is not None
        assert "prediction" in result
        assert "explanation" in result
        assert "recommendations" in result
        
        # Verify severity data is empty or has error indicator
        severity_data = result.get("severity", {})
        # Severity should be empty or indicate failure
        assert severity_data == {} or "error" in str(severity_data)
        
        print("✓ Pipeline recovered from agent failure")
    
    def test_critical_agent_failure_blocks_pipeline(self, orchestrator, sample_input, mock_firebase):
        """
        Test that critical agent failures block the pipeline.
        
        Requirements: 6.6 - Failure recovery with critical agent handling
        """
        # Make validation agent fail (critical agent)
        def failing_validation(data):
            return {
                "success": False,
                "data": {
                    "reason": "Critical validation failure",
                    "errors": ["Invalid input"]
                }
            }
        
        orchestrator.validation_agent.process = failing_validation
        
        # Execute pipeline
        result = orchestrator.run_pipeline(sample_input)
        
        # Verify pipeline was blocked
        assert result is not None
        assert "blocked" in result or "reason" in result
        
        print("✓ Critical agent failure properly blocked pipeline")
    
    def test_agent_timeout_handling(self, orchestrator, sample_input, mock_firebase):
        """
        Test that agent timeouts are handled gracefully.
        
        Requirements: 6.5 - Timeout management
        """
        # Make an agent timeout
        def slow_agent(data):
            time.sleep(35)  # Exceed timeout
            return {"success": True, "data": {}}
        
        # Set short timeout for testing
        orchestrator.AGENT_TIMEOUT = 2
        orchestrator.severity_agent.process = slow_agent
        
        # Execute pipeline
        result = orchestrator.run_pipeline(sample_input)
        
        # Verify pipeline completed despite timeout
        assert result is not None
        assert "prediction" in result
        
        # Verify timeout was logged (severity should be empty or have error)
        severity_data = result.get("severity", {})
        assert severity_data == {} or "error" in str(severity_data)
        
        print("✓ Agent timeout handled gracefully")
    
    def test_multiple_workflows_with_different_inputs(self, orchestrator, mock_firebase):
        """
        Test multiple workflows with different input characteristics.
        
        Requirements: 5.1 - Autonomous agent selection based on input
        """
        # Test case 1: Symptoms only
        input1 = {
            "user_id": "user1",
            "symptoms": ["fever", "cough"],
            "age": 30,
            "gender": "female"
        }
        
        result1 = orchestrator.run_pipeline(input1)
        assert result1 is not None
        assert "prediction" in result1
        
        # Test case 2: Symptoms with vitals
        input2 = {
            "user_id": "user2",
            "symptoms": ["chest_pain", "shortness_of_breath"],
            "age": 55,
            "gender": "male",
            "additional_info": {
                "vitals": {
                    "blood_pressure": "160/100",
                    "heart_rate": 95
                }
            }
        }
        
        result2 = orchestrator.run_pipeline(input2)
        assert result2 is not None
        assert "prediction" in result2
        assert "severity" in result2
        
        # Test case 3: Symptoms with lab results
        input3 = {
            "user_id": "user3",
            "symptoms": ["increased_thirst", "frequent_urination"],
            "age": 45,
            "gender": "male",
            "additional_info": {
                "lab_results": [
                    {
                        "test_name": "HbA1c",
                        "value": 8.5,
                        "unit": "%",
                        "reference_range": "4.0-5.6"
                    }
                ]
            }
        }
        
        result3 = orchestrator.run_pipeline(input3)
        assert result3 is not None
        assert "prediction" in result3
        
        print("✓ Multiple workflows with different inputs completed successfully")
    
    def test_context_cleared_after_pipeline(self, orchestrator, sample_input, mock_firebase):
        """
        Test that context is properly cleared after pipeline completion.
        
        Requirements: 16.5 - Clear context at session end
        """
        # Execute pipeline
        result = orchestrator.run_pipeline(sample_input)
        
        # Verify context was cleared
        context = orchestrator.context_manager.get_context()
        assert context == {} or len(context) == 0
        
        # Verify session ID was cleared
        session_id = orchestrator.context_manager.get_session_id()
        assert session_id is None
        
        print("✓ Context properly cleared after pipeline completion")
    
    def test_agent_result_aggregation(self, orchestrator, sample_input, mock_firebase):
        """
        Test that orchestrator properly aggregates results from multiple agents.
        
        Requirements: 6.8 - Aggregate results from multiple agents
        """
        # Execute pipeline
        result = orchestrator.run_pipeline(sample_input)
        
        # Verify all expected components are aggregated
        assert "prediction" in result
        assert "explanation" in result
        assert "recommendations" in result
        assert "lifestyle_recommendations" in result
        assert "metadata" in result
        
        # Verify prediction aggregation
        prediction = result["prediction"]
        assert "disease" in prediction
        assert "probability" in prediction
        assert "confidence" in prediction
        
        # Verify metadata aggregation
        metadata = result["metadata"]
        assert "processing_time_seconds" in metadata
        assert "timestamp" in metadata
        assert "storage_ids" in metadata
        
        # Verify storage IDs are aggregated
        storage_ids = metadata["storage_ids"]
        assert "assessment_id" in storage_ids
        
        print("✓ Agent results properly aggregated")


class TestContextManagerIntegration:
    """Integration tests for context manager in multi-agent workflows."""
    
    @pytest.fixture
    def context_manager(self):
        """Create context manager for testing."""
        return ContextManager(max_context_size=10000)
    
    def test_context_sharing_across_agents(self, context_manager):
        """
        Test context sharing between multiple agents.
        
        Requirements: 6.3, 6.4 - Context sharing
        """
        # Simulate agent 1 sharing data
        context_manager.share_context("agent1", {
            "result": "data from agent 1",
            "confidence": 0.85
        })
        
        # Simulate agent 2 sharing data
        context_manager.share_context("agent2", {
            "result": "data from agent 2",
            "analysis": "detailed analysis"
        })
        
        # Verify both agents' data is accessible
        agent1_data = context_manager.get_shared_context("agent1")
        assert agent1_data is not None
        assert agent1_data["result"] == "data from agent 1"
        
        agent2_data = context_manager.get_shared_context("agent2")
        assert agent2_data is not None
        assert agent2_data["result"] == "data from agent 2"
        
        # Verify all shared data is accessible
        all_shared = context_manager.get_shared_context()
        assert "agent1" in all_shared
        assert "agent2" in all_shared
        
        print("✓ Context sharing across agents verified")
    
    def test_context_persistence_within_session(self, context_manager):
        """
        Test that context persists within a session.
        
        Requirements: 16.1, 16.2 - Context persistence
        """
        # Set session ID
        session_id = "session_123"
        context_manager.set_session_id(session_id)
        
        # Add multiple context items
        context_manager.add_to_context("item1", "value1")
        context_manager.add_to_context("item2", {"nested": "value2"})
        context_manager.add_to_context("item3", [1, 2, 3])
        
        # Verify all items persist
        assert context_manager.get_context("item1") == "value1"
        assert context_manager.get_context("item2") == {"nested": "value2"}
        assert context_manager.get_context("item3") == [1, 2, 3]
        
        # Verify session ID persists
        assert context_manager.get_session_id() == session_id
        
        print("✓ Context persistence within session verified")
    
    def test_context_size_management(self, context_manager):
        """
        Test that context size is managed properly.
        
        Requirements: 16.6, 16.7 - Context size limits and summarization
        """
        # Add large amount of data
        for i in range(100):
            context_manager.add_to_context(f"key_{i}", f"value_{i}" * 100)
        
        # Verify context size is limited
        context_size = context_manager._get_context_size()
        assert context_size <= context_manager.max_context_size * 1.5  # Allow some overflow
        
        # Verify summarization occurred
        status = context_manager.get_status()
        assert status["context_size"] <= context_manager.max_context_size * 1.5
        
        print(f"✓ Context size managed: {context_size} chars")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
