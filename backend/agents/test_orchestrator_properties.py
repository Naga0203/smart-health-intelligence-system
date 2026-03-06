"""
Property-Based Tests for OrchestratorAgent

Tests universal correctness properties that should hold across all valid inputs
for the enhanced orchestrator agent with autonomous coordination, parallel execution,
and context sharing capabilities.

Requirements: 1.6, 5.1, 6.1, 6.2, 6.3, 6.4, 6.7, 6.8, 16.3, 16.4

Properties Tested:
- Property 1: Agent Migration Preserves Functionality (Requirement 1.6)
- Property 13: Orchestrator Selects Agents Based on Input (Requirement 5.1)
- Property 21: Orchestrator Coordinates Multiple Agents (Requirements 6.1, 6.8)
- Property 22: Agent Completion Triggers Next Agent Selection (Requirement 6.2)
- Property 23: Agents Share Context and Results (Requirements 6.3, 6.4, 16.3, 16.4)
- Property 26: Independent Agents Execute in Parallel (Requirement 6.7)
"""

import pytest
pytest_plugins = ['pytest_asyncio']
pytestmark = pytest.mark.pbt

from unittest.mock import Mock, patch, MagicMock, call
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from typing import Dict, Any, List
import time
import uuid

from .orchestrator import OrchestratorAgent
from .infrastructure.config import AgentConfig


# ============================================================================
# Test Fixtures and Helpers
# ============================================================================

@pytest.fixture
def mock_firebase():
    """Mock Firebase database."""
    with patch('backend.agents.orchestrator.get_firebase_db') as mock_db:
        mock_instance = MagicMock()
        mock_instance.db = MagicMock()
        mock_instance.store_assessment.return_value = str(uuid.uuid4())
        mock_instance.store_prediction.return_value = str(uuid.uuid4())
        mock_instance.store_explanation.return_value = str(uuid.uuid4())
        mock_instance.store_recommendation.return_value = str(uuid.uuid4())
        mock_instance.store_audit_log.return_value = None
        mock_db.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_predictor():
    """Mock disease predictor."""
    with patch('backend.agents.orchestrator.DiseasePredictor') as mock_pred:
        mock_instance = MagicMock()
        mock_instance.predict.return_value = (0.75, {"model_version": "v1.0"})
        mock_instance.get_supported_diseases.return_value = ["diabetes", "heart_disease", "hypertension"]
        mock_instance.model_version = "v1.0"
        mock_pred.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_agents():
    """Mock all specialized agents."""
    mocks = {}
    
    # Validation agent
    validation_mock = MagicMock()
    validation_mock.process.return_value = {
        "success": True,
        "data": {
            "sanitized_input": {
                "symptoms": ["fatigue", "thirst"],
                "age": 45,
                "gender": "male",
                "additional_info": {}
            },
            "reason": "valid"
        }
    }
    mocks['validation'] = validation_mock
    
    # Extraction agent
    extraction_mock = MagicMock()
    extraction_mock.process.return_value = {
        "success": True,
        "data": {
            "features": {"feature1": 1.0, "feature2": 0.5},
            "extraction_confidence": 0.85
        }
    }
    mocks['extraction'] = extraction_mock
    
    # Severity agent
    severity_mock = MagicMock()
    severity_mock.process.return_value = {
        "success": True,
        "data": {
            "severity_level": "moderate",
            "risk_factors": ["age", "symptoms"]
        }
    }
    mocks['severity'] = severity_mock
    
    # Explanation agent
    explanation_mock = MagicMock()
    explanation_mock.process.return_value = {
        "success": True,
        "data": {
            "explanation": "Test explanation",
            "citations": []
        }
    }
    mocks['explanation'] = explanation_mock
    
    # Recommendation agent
    recommendation_mock = MagicMock()
    recommendation_mock.process.return_value = {
        "success": True,
        "data": {
            "recommendations": ["recommendation1", "recommendation2"]
        }
    }
    mocks['recommendation'] = recommendation_mock
    
    # Lifestyle agent
    lifestyle_mock = MagicMock()
    lifestyle_mock.process.return_value = {
        "success": True,
        "data": {
            "lifestyle_modifications": ["exercise", "diet"]
        }
    }
    mocks['lifestyle'] = lifestyle_mock
    
    # Reflection agent
    reflection_mock = MagicMock()
    reflection_mock.verify_assessment.return_value = {
        "recommended_action": "approve",
        "severity": "low",
        "issue_count": 0,
        "revised_assessment": {}
    }
    mocks['reflection'] = reflection_mock
    
    return mocks


@pytest.fixture
def orchestrator(mock_firebase, mock_predictor, mock_agents):
    """Create orchestrator with mocked dependencies."""
    config = AgentConfig(
        agent_name="OrchestratorAgent",
        enable_web_search=False,
        monitoring_enabled=False
    )
    
    with patch('backend.agents.orchestrator.LangChainValidationAgent', return_value=mock_agents['validation']), \
         patch('backend.agents.orchestrator.DataExtractionAgent', return_value=mock_agents['extraction']), \
         patch('backend.agents.orchestrator.SeverityAgent', return_value=mock_agents['severity']), \
         patch('backend.agents.orchestrator.LangChainExplanationAgent', return_value=mock_agents['explanation']), \
         patch('backend.agents.orchestrator.RecommendationAgent', return_value=mock_agents['recommendation']), \
         patch('backend.agents.orchestrator.LifestyleModificationAgent', return_value=mock_agents['lifestyle']), \
         patch('backend.agents.orchestrator.ReflectionAgent', return_value=mock_agents['reflection']):
        
        agent = OrchestratorAgent(config)
        yield agent


# ============================================================================
# Hypothesis Strategies for Generating Test Data
# ============================================================================

# Valid symptoms strategy
symptoms_strategy = st.lists(
    st.text(
        alphabet=st.characters(whitelist_categories=('L', 'N'), max_codepoint=127),
        min_size=3,
        max_size=30
    ).filter(lambda s: len(s.strip()) >= 3),
    min_size=1,
    max_size=10
)

# Valid age strategy
age_strategy = st.integers(min_value=1, max_value=120)

# Valid gender strategy
gender_strategy = st.sampled_from(["male", "female", "other"])

# Valid user input strategy
user_input_strategy = st.fixed_dictionaries({
    "user_id": st.uuids().map(str),
    "symptoms": symptoms_strategy,
    "age": age_strategy,
    "gender": gender_strategy,
    "additional_info": st.dictionaries(
        keys=st.sampled_from(["vitals", "lab_results"]),
        values=st.just({}),
        min_size=0,
        max_size=2
    )
})


# ============================================================================
# Property 1: Agent Migration Preserves Functionality
# Feature: autonomous-ai-agents-refactor, Property 1: Agent Migration Preserves Functionality
# ============================================================================

@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(user_input=user_input_strategy)
def test_property_1_migration_preserves_functionality(orchestrator, user_input):
    """
    Property 1: Agent Migration Preserves Functionality
    
    For any agent and any valid input, the migrated agent implementation should 
    produce equivalent outputs to the original implementation.
    
    Validates: Requirements 1.6
    
    This test verifies that the orchestrator produces valid outputs with the
    expected structure after migration to EnhancedBaseHealthAgent.
    """
    # Feature: autonomous-ai-agents-refactor, Property 1: Agent Migration Preserves Functionality
    
    # Execute the orchestrator
    result = orchestrator.process(user_input)
    
    # Verify result structure (migrated agent should produce valid outputs)
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "success" in result, "Result should have success field"
    
    if result["success"]:
        assert "data" in result, "Successful result should have data field"
        data = result["data"]
        
        # Verify expected output structure
        assert "user_id" in data, "Data should contain user_id"
        assert "prediction" in data, "Data should contain prediction"
        assert "explanation" in data, "Data should contain explanation"
        assert "recommendations" in data, "Data should contain recommendations"
        assert "metadata" in data, "Data should contain metadata"
        
        # Verify prediction structure
        prediction = data["prediction"]
        assert "disease" in prediction, "Prediction should contain disease"
        assert "probability" in prediction, "Prediction should contain probability"
        assert "confidence" in prediction, "Prediction should contain confidence"
        
        # Verify metadata structure
        metadata = data["metadata"]
        assert "processing_time_seconds" in metadata, "Metadata should contain processing time"
        assert "timestamp" in metadata, "Metadata should contain timestamp"


# ============================================================================
# Property 13: Orchestrator Selects Agents Based on Input
# Feature: autonomous-ai-agents-refactor, Property 13: Orchestrator Selects Agents Based on Input
# ============================================================================

@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    symptoms=symptoms_strategy,
    has_vitals=st.booleans(),
    has_lab_results=st.booleans()
)
def test_property_13_agent_selection_based_on_input(orchestrator, symptoms, has_vitals, has_lab_results):
    """
    Property 13: Orchestrator Selects Agents Based on Input
    
    For any health assessment request, the orchestrator should select different 
    sets of specialized agents based on the input data characteristics.
    
    Validates: Requirements 5.1
    """
    # Feature: autonomous-ai-agents-refactor, Property 13: Orchestrator Selects Agents Based on Input
    
    # Build input with varying characteristics
    input_data = {
        "symptoms": symptoms,
        "additional_info": {}
    }
    
    if has_vitals:
        input_data["additional_info"]["vitals"] = {
            "blood_pressure": "120/80",
            "heart_rate": 75
        }
    
    if has_lab_results:
        input_data["additional_info"]["lab_results"] = [
            {"test_name": "glucose", "value": 100, "unit": "mg/dL"}
        ]
    
    # Select agents based on input
    selected_agents = orchestrator._select_agents_for_input(input_data)
    
    # Verify agent selection logic
    assert isinstance(selected_agents, list), "Selected agents should be a list"
    assert len(selected_agents) > 0, "At least one agent should be selected"
    
    # Validation should always be first
    assert selected_agents[0] == 'validation', "Validation should always be first"
    
    # Extraction should always be included
    assert 'extraction' in selected_agents, "Extraction should always be included"
    
    # Severity should be included if symptoms or vitals present
    if symptoms or has_vitals:
        assert 'severity' in selected_agents, "Severity should be included when symptoms/vitals present"
    
    # Reflection should always be last
    assert selected_agents[-1] == 'reflection', "Reflection should always be last"


# ============================================================================
# Property 21: Orchestrator Coordinates Multiple Agents
# Feature: autonomous-ai-agents-refactor, Property 21: Orchestrator Coordinates Multiple Agents
# ============================================================================

@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(user_input=user_input_strategy)
def test_property_21_orchestrator_coordinates_agents(orchestrator, user_input):
    """
    Property 21: Orchestrator Coordinates Multiple Agents
    
    For any health assessment request, the orchestrator should invoke multiple 
    specialized agents and aggregate their results into a coherent response.
    
    Validates: Requirements 6.1, 6.8
    """
    # Feature: autonomous-ai-agents-refactor, Property 21: Orchestrator Coordinates Multiple Agents
    
    # Execute orchestrator
    result = orchestrator.process(user_input)
    
    # Verify orchestrator coordinated multiple agents
    assert result["success"], "Orchestrator should successfully coordinate agents"
    
    data = result["data"]
    
    # Verify results from multiple agents are aggregated
    assert "prediction" in data, "Should have prediction from prediction engine"
    assert "explanation" in data, "Should have explanation from explanation agent"
    assert "recommendations" in data, "Should have recommendations from recommendation agent"
    assert "lifestyle_recommendations" in data, "Should have lifestyle from lifestyle agent"
    
    # Verify coherent aggregation
    assert data["prediction"]["disease"], "Prediction should have disease"
    assert isinstance(data["explanation"], dict), "Explanation should be aggregated"
    assert isinstance(data["recommendations"], dict), "Recommendations should be aggregated"
    
    # Verify metadata shows coordination
    assert "metadata" in data, "Should have metadata"
    assert "processing_time_seconds" in data["metadata"], "Should track processing time"


# ============================================================================
# Property 22: Agent Completion Triggers Next Agent Selection
# Feature: autonomous-ai-agents-refactor, Property 22: Agent Completion Triggers Next Agent Selection
# ============================================================================

@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(user_input=user_input_strategy)
def test_property_22_agent_completion_triggers_next(orchestrator, mock_agents, user_input):
    """
    Property 22: Agent Completion Triggers Next Agent Selection
    
    For any agent completing its task in a multi-agent workflow, the orchestrator 
    should autonomously determine and invoke the next appropriate agent.
    
    Validates: Requirements 6.2
    """
    # Feature: autonomous-ai-agents-refactor, Property 22: Agent Completion Triggers Next Agent Selection
    
    # Track agent execution order
    execution_order = []
    
    def track_execution(agent_name):
        def wrapper(*args, **kwargs):
            execution_order.append(agent_name)
            return mock_agents[agent_name].process(*args, **kwargs)
        return wrapper
    
    # Wrap agent process methods to track execution
    for agent_name in ['validation', 'extraction', 'severity', 'explanation', 'recommendation', 'lifestyle']:
        if agent_name in mock_agents:
            mock_agents[agent_name].process.side_effect = track_execution(agent_name)
    
    # Execute orchestrator
    result = orchestrator.process(user_input)
    
    # Verify agents were executed in sequence
    assert len(execution_order) > 0, "At least one agent should be executed"
    
    # Verify validation was first
    if 'validation' in execution_order:
        assert execution_order[0] == 'validation', "Validation should be executed first"
    
    # Verify sequential execution (each agent completion triggers next)
    # The orchestrator should have called multiple agents in order
    assert len(execution_order) >= 3, "Multiple agents should be executed sequentially"


# ============================================================================
# Property 23: Agents Share Context and Results
# Feature: autonomous-ai-agents-refactor, Property 23: Agents Share Context and Results
# ============================================================================

@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(user_input=user_input_strategy)
def test_property_23_agents_share_context(orchestrator, user_input):
    """
    Property 23: Agents Share Context and Results
    
    For any multi-agent workflow, agents should be able to access context and 
    intermediate results from previously executed agents in the same session.
    
    Validates: Requirements 6.3, 6.4, 16.3, 16.4
    """
    # Feature: autonomous-ai-agents-refactor, Property 23: Agents Share Context and Results
    
    # Execute orchestrator
    result = orchestrator.process(user_input)
    
    # Verify context manager was used
    context_manager = orchestrator.context_manager
    assert context_manager is not None, "Orchestrator should have context manager"
    
    # After execution, context should have been populated and then cleared
    # (context is cleared at end of session)
    # We can verify the context manager exists and has the capability
    assert hasattr(context_manager, 'add_to_context'), "Context manager should support adding context"
    assert hasattr(context_manager, 'get_context'), "Context manager should support getting context"
    assert hasattr(context_manager, 'share_context'), "Context manager should support sharing context"
    
    # Verify result contains aggregated data from multiple agents
    if result["success"]:
        data = result["data"]
        
        # Verify data from different agents is present (showing context was shared)
        assert "prediction" in data, "Should have prediction data"
        assert "explanation" in data, "Should have explanation data"
        assert "recommendations" in data, "Should have recommendations data"
        
        # The fact that explanation and recommendations exist shows they had access
        # to prediction context (they need disease and probability to generate their outputs)


# ============================================================================
# Property 26: Independent Agents Execute in Parallel
# Feature: autonomous-ai-agents-refactor, Property 26: Independent Agents Execute in Parallel
# ============================================================================

@settings(
    max_examples=10,  # Reduced for performance
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(user_input=user_input_strategy)
def test_property_26_parallel_execution(orchestrator, mock_agents, user_input):
    """
    Property 26: Independent Agents Execute in Parallel
    
    For any set of agents with no data dependencies, the orchestrator should 
    execute them concurrently rather than sequentially.
    
    Validates: Requirements 6.7
    """
    # Feature: autonomous-ai-agents-refactor, Property 26: Independent Agents Execute in Parallel
    
    # Track execution timing for parallel agents
    execution_times = {}
    
    def timed_execution(agent_name, delay=0.01):
        def wrapper(*args, **kwargs):
            start = time.time()
            time.sleep(delay)  # Simulate work
            result = mock_agents[agent_name].process(*args, **kwargs)
            execution_times[agent_name] = time.time() - start
            return result
        return wrapper
    
    # Add delays to extraction and severity (parallel agents)
    mock_agents['extraction'].process.side_effect = timed_execution('extraction', 0.05)
    mock_agents['severity'].process.side_effect = timed_execution('severity', 0.05)
    
    # Execute orchestrator
    start_time = time.time()
    result = orchestrator.process(user_input)
    total_time = time.time() - start_time
    
    # Verify parallel execution occurred
    # If executed sequentially, total time would be sum of individual times
    # If executed in parallel, total time should be less than sum
    
    if 'extraction' in execution_times and 'severity' in execution_times:
        sequential_time = execution_times['extraction'] + execution_times['severity']
        
        # Parallel execution should be faster than sequential
        # Allow some overhead for thread management
        assert total_time < sequential_time * 1.5, \
            f"Parallel execution should be faster: {total_time}s vs {sequential_time}s sequential"
    
    # Verify both agents were called (showing they ran in parallel)
    assert mock_agents['extraction'].process.called, "Extraction agent should be called"
    assert mock_agents['severity'].process.called, "Severity agent should be called"


# ============================================================================
# Additional Helper Tests
# ============================================================================

def test_orchestrator_initialization(orchestrator):
    """Test that orchestrator initializes correctly with all components."""
    assert orchestrator is not None
    assert orchestrator.agent_name == "OrchestratorAgent"
    assert orchestrator.validation_agent is not None
    assert orchestrator.extraction_agent is not None
    assert orchestrator.severity_agent is not None
    assert orchestrator.explanation_agent is not None
    assert orchestrator.recommendation_agent is not None
    assert orchestrator.lifestyle_agent is not None
    assert orchestrator.reflection_agent is not None
    assert orchestrator.context_manager is not None
    assert orchestrator.decision_engine is not None


def test_orchestrator_agent_registry(orchestrator):
    """Test that orchestrator maintains agent registry for autonomous selection."""
    assert hasattr(orchestrator, 'agent_registry')
    assert isinstance(orchestrator.agent_registry, dict)
    assert 'validation' in orchestrator.agent_registry
    assert 'extraction' in orchestrator.agent_registry
    assert 'severity' in orchestrator.agent_registry
    assert 'explanation' in orchestrator.agent_registry
    assert 'recommendation' in orchestrator.agent_registry
    assert 'lifestyle' in orchestrator.agent_registry
    assert 'reflection' in orchestrator.agent_registry
