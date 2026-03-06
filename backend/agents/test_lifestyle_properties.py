"""
Property-Based Tests for LifestyleModificationAgent

Tests universal correctness properties that should hold across all valid inputs
for the enhanced lifestyle agent with web search and dynamic retrieval capabilities.

Requirements: 1.6, 3.3, 3.4

Properties Tested:
- Property 1: Agent Migration Preserves Functionality (Requirement 1.6)
- Property 6: Dynamic Retrieval Replaces Static Lookups (Requirements 3.3, 3.4)
"""

import pytest
pytest_plugins = ['pytest_asyncio']
pytestmark = pytest.mark.pbt

import pytest
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from typing import Dict, Any, List
import json

from .lifestyle import LifestyleModificationAgent
from .infrastructure.config import AgentConfig
from .infrastructure.models import SearchResult


# ============================================================================
# Test Fixtures and Helpers
# ============================================================================

@pytest.fixture
def mock_gemini_client():
    """Mock LangChain Gemini client."""
    with patch('common.gemini_client.LangChainGeminiClient') as mock_client:
        mock_llm = MagicMock()
        mock_client.return_value.llm = mock_llm
        yield mock_client


@pytest.fixture
def agent_with_web_search(mock_gemini_client):
    """Create agent with web search enabled."""
    config = AgentConfig(
        agent_name="LifestyleModificationAgent",
        enable_web_search=True,
        enable_caching=True,
        monitoring_enabled=False
    )
    agent = LifestyleModificationAgent(config)
    
    # Mock web search tool
    agent.web_search_tool = MagicMock()
    
    return agent


@pytest.fixture
def agent_without_web_search(mock_gemini_client):
    """Create agent with web search disabled."""
    config = AgentConfig(
        agent_name="LifestyleModificationAgent",
        enable_web_search=False,
        monitoring_enabled=False
    )
    agent = LifestyleModificationAgent(config)
    return agent


# ============================================================================
# Hypothesis Strategies for Generating Test Data
# ============================================================================

# Valid disease strategy
disease_strategy = st.sampled_from([
    "diabetes", "heart_disease", "hypertension", "asthma", 
    "arthritis", "obesity", "depression", "anxiety"
])

# Valid age strategy
age_strategy = st.integers(min_value=18, max_value=90)

# Valid gender strategy
gender_strategy = st.sampled_from(["male", "female", "other", "unknown"])

# Valid confidence/risk level strategy
risk_level_strategy = st.sampled_from(["LOW", "MEDIUM", "HIGH"])

# Valid symptoms strategy
symptoms_strategy = st.lists(
    st.text(
        alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'), max_codepoint=127),
        min_size=3,
        max_size=50
    ).filter(lambda s: len(s.strip()) >= 3),
    min_size=1,
    max_size=10
)

# User context strategy
user_context_strategy = st.fixed_dictionaries({
    "age": age_strategy,
    "gender": gender_strategy,
    "medical_history": st.text(min_size=0, max_size=200)
})

# Search result strategy for mocking web search
search_result_strategy = st.fixed_dictionaries({
    "title": st.text(min_size=10, max_size=100),
    "url": st.text(min_size=10, max_size=100).map(lambda t: f"https://pubmed.ncbi.nlm.nih.gov/{t}"),
    "snippet": st.text(min_size=20, max_size=200),
    "source_domain": st.sampled_from([
        "pubmed.ncbi.nlm.nih.gov", "who.int", "cdc.gov", 
        "mayoclinic.org", "nih.gov"
    ]),
    "quality_score": st.floats(min_value=0.7, max_value=1.0)
})


# ============================================================================
# Property 1: Agent Migration Preserves Functionality
# Validates: Requirement 1.6
# ============================================================================

class TestProperty1_MigrationPreservesFunctionality:
    """
    Property 1: Agent Migration Preserves Functionality
    
    For any valid input (disease, user_context, symptoms),
    the migrated agent should produce a valid lifestyle recommendation
    response with all required fields.
    """
    
    @given(
        disease=disease_strategy,
        user_context=user_context_strategy,
        symptoms=symptoms_strategy,
        risk_level=risk_level_strategy
    )
    @settings(
        max_examples=50,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_migrated_agent_produces_valid_recommendations(
        self,
        agent_without_web_search,
        disease,
        user_context,
        symptoms,
        risk_level
    ):
        """
        Test that migrated agent produces valid lifestyle recommendations for any valid input.
        
        This validates that the migration to EnhancedBaseHealthAgent preserves
        the core functionality of generating lifestyle recommendations.
        """
        # Arrange
        input_data = {
            "disease": disease,
            "user_context": user_context,
            "symptoms": symptoms,
            "confidence": risk_level
        }
        
        # Mock the LangChain chain execution with structured response
        mock_recommendations = json.dumps({
            "diet_plan": [
                {"recommendation": "Eat more vegetables", "priority": "high"}
            ],
            "exercise_plan": [
                {"activity": "Walking", "frequency": "daily", "duration": "30 minutes", "priority": "high"}
            ],
            "stress_management": [
                {"technique": "Deep breathing", "how_to": "5 minutes daily"}
            ],
            "sleep_hygiene": [
                {"tip": "Consistent sleep schedule", "rationale": "Improves health"}
            ],
            "immediate_actions": [
                "Start walking routine"
            ]
        })
        agent_without_web_search.execute_chain = MagicMock(return_value=mock_recommendations)
        
        # Act
        result = agent_without_web_search.process(input_data)
        
        # Assert - Verify response structure
        assert result is not None, "Agent should return a response"
        assert isinstance(result, dict), "Response should be a dictionary"
        assert "success" in result, "Response should have success field"
        
        # If successful, verify recommendation data structure
        if result["success"]:
            assert "data" in result, "Successful response should have data field"
            data = result["data"]
            
            # Verify required fields in recommendations
            assert "diet_plan" in data or "text_plan" in data, "Should have diet_plan or text_plan"
            assert "generated_at" in data, "Should have timestamp"
            assert "agent" in data, "Should identify the agent"
            
            # If structured response, verify structure
            if "diet_plan" in data:
                assert isinstance(data["diet_plan"], list), "diet_plan should be a list"
                assert "exercise_plan" in data, "Should have exercise_plan"
                assert isinstance(data["exercise_plan"], list), "exercise_plan should be a list"
    
    @given(
        disease=disease_strategy,
        user_context=user_context_strategy,
        symptoms=symptoms_strategy
    )
    @settings(
        max_examples=30,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_migrated_agent_handles_errors_gracefully(
        self,
        agent_without_web_search,
        disease,
        user_context,
        symptoms
    ):
        """
        Test that migrated agent handles errors gracefully.
        
        This validates that error handling is preserved after migration.
        """
        # Arrange
        input_data = {
            "disease": disease,
            "user_context": user_context,
            "symptoms": symptoms
        }
        
        # Mock the LangChain chain to raise an exception
        agent_without_web_search.execute_chain = MagicMock(side_effect=Exception("LLM error"))
        
        # Act
        result = agent_without_web_search.process(input_data)
        
        # Assert - Should still return a valid response (fallback)
        assert result is not None, "Agent should return response even on error"
        assert isinstance(result, dict), "Response should be a dictionary"
        assert "success" in result, "Response should have success field"
        
        # Should have fallback recommendations
        if result.get("success") and "data" in result:
            data = result["data"]
            assert "diet_plan" in data or "text_plan" in data, "Should have fallback recommendations"
    
    @given(
        disease=disease_strategy,
        user_context=user_context_strategy,
        symptoms=symptoms_strategy
    )
    @settings(
        max_examples=30,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_recommendations_personalized_by_age(
        self,
        agent_without_web_search,
        disease,
        user_context,
        symptoms
    ):
        """
        Test that recommendations consider user age for personalization.
        
        This validates that the agent uses user context for personalization.
        """
        # Arrange
        input_data = {
            "disease": disease,
            "user_context": user_context,
            "symptoms": symptoms
        }
        
        # Mock the LangChain chain execution
        mock_recommendations = json.dumps({
            "diet_plan": [{"recommendation": "Age-appropriate diet", "priority": "high"}],
            "exercise_plan": [{"activity": "Age-appropriate exercise", "frequency": "daily", "duration": "30 min", "priority": "high"}],
            "stress_management": [{"technique": "Meditation", "how_to": "10 minutes"}],
            "sleep_hygiene": [{"tip": "Sleep 7-9 hours", "rationale": "Health"}],
            "immediate_actions": ["Start today"],
            "personalization_notes": f"Tailored for {user_context['age']} year old"
        })
        agent_without_web_search.execute_chain = MagicMock(return_value=mock_recommendations)
        
        # Act
        result = agent_without_web_search.process(input_data)
        
        # Assert
        assert result.get("success"), "Response should be successful"
        data = result.get("data", {})
        
        # Verify personalization metadata is included
        if "personalization" in data:
            assert "age" in data["personalization"], "Should include age in personalization"
            assert data["personalization"]["age"] == user_context["age"], "Should use correct age"


# ============================================================================
# Property 6: Dynamic Retrieval Replaces Static Lookups
# Validates: Requirements 3.3, 3.4
# ============================================================================

class TestProperty6_DynamicRetrievalReplacesStatic:
    """
    Property 6: Dynamic Retrieval Replaces Static Lookups
    
    For any lifestyle recommendation request, the system should perform
    web search or AI query rather than loading from static data files.
    """
    
    @given(
        disease=disease_strategy,
        user_context=user_context_strategy,
        symptoms=symptoms_strategy,
        search_results=st.lists(search_result_strategy, min_size=1, max_size=5)
    )
    @settings(
        max_examples=50,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_web_search_performed_for_lifestyle_interventions(
        self,
        agent_with_web_search,
        disease,
        user_context,
        symptoms,
        search_results
    ):
        """
        Test that web search is performed to retrieve evidence-based interventions.
        
        This validates that the agent uses dynamic retrieval instead of
        static data lookups.
        """
        # Arrange
        input_data = {
            "disease": disease,
            "user_context": user_context,
            "symptoms": symptoms
        }
        
        # Mock web search to return results
        agent_with_web_search.search_web = MagicMock(return_value=search_results)
        
        # Mock the LangChain chain execution
        mock_recommendations = json.dumps({
            "diet_plan": [{"recommendation": "Evidence-based diet", "evidence": "From research", "priority": "high"}],
            "exercise_plan": [{"activity": "Evidence-based exercise", "frequency": "daily", "duration": "30 min", "priority": "high"}],
            "stress_management": [{"technique": "Meditation", "how_to": "10 minutes", "evidence": "Research-backed"}],
            "sleep_hygiene": [{"tip": "Sleep hygiene", "rationale": "Science"}],
            "immediate_actions": ["Start today"]
        })
        agent_with_web_search.execute_chain = MagicMock(return_value=mock_recommendations)
        
        # Act
        result = agent_with_web_search.process(input_data)
        
        # Assert - Verify web search was called
        agent_with_web_search.search_web.assert_called()
        
        # Verify the search query includes lifestyle/intervention keywords
        call_args = agent_with_web_search.search_web.call_args
        if call_args:
            query = call_args[1].get("query", "") if len(call_args) > 1 else call_args[0][0] if call_args[0] else ""
            assert any(keyword in query.lower() for keyword in [
                "lifestyle", "intervention", "diet", "exercise", "management"
            ]), "Search query should include lifestyle intervention keywords"
    
    @given(
        disease=disease_strategy,
        user_context=user_context_strategy,
        symptoms=symptoms_strategy,
        search_results=st.lists(search_result_strategy, min_size=1, max_size=5)
    )
    @settings(
        max_examples=30,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_recommendations_include_evidence_from_web_sources(
        self,
        agent_with_web_search,
        disease,
        user_context,
        symptoms,
        search_results
    ):
        """
        Test that recommendations include evidence basis from web sources.
        
        This validates that dynamic retrieval provides evidence-based
        recommendations rather than static templates.
        """
        # Arrange
        input_data = {
            "disease": disease,
            "user_context": user_context,
            "symptoms": symptoms
        }
        
        # Mock web search to return results with evidence
        agent_with_web_search.search_web = MagicMock(return_value=search_results)
        
        # Mock LangChain to return evidence-based recommendations
        mock_recommendations = json.dumps({
            "diet_plan": [
                {"recommendation": "Mediterranean diet", "evidence": "Reduces cardiovascular risk", "priority": "high"}
            ],
            "exercise_plan": [
                {"activity": "Aerobic exercise", "frequency": "5x/week", "duration": "30 min", 
                 "evidence": "Improves outcomes", "priority": "high"}
            ],
            "stress_management": [
                {"technique": "Mindfulness", "how_to": "Daily practice", "evidence": "Clinical trials"}
            ],
            "sleep_hygiene": [
                {"tip": "Consistent schedule", "rationale": "Circadian rhythm"}
            ],
            "immediate_actions": ["Start walking"]
        })
        agent_with_web_search.execute_chain = MagicMock(return_value=mock_recommendations)
        
        # Act
        result = agent_with_web_search.process(input_data)
        
        # Assert
        assert result.get("success"), "Response should be successful"
        data = result.get("data", {})
        
        # Verify recommendations include evidence or citations
        has_evidence = False
        if "diet_plan" in data and isinstance(data["diet_plan"], list):
            for item in data["diet_plan"]:
                if isinstance(item, dict) and "evidence" in item:
                    has_evidence = True
                    break
        
        # Or check for sources/citations
        has_citations = "sources" in data and len(data.get("sources", [])) > 0
        
        assert has_evidence or has_citations, "Recommendations should include evidence or citations from web sources"
    
    @given(
        disease=disease_strategy,
        user_context=user_context_strategy,
        symptoms=symptoms_strategy
    )
    @settings(
        max_examples=30,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_no_static_data_files_loaded(
        self,
        agent_with_web_search,
        disease,
        user_context,
        symptoms
    ):
        """
        Test that no static data files are loaded for recommendations.
        
        This validates that the agent does not rely on hardcoded
        lifestyle data files.
        """
        # Arrange
        input_data = {
            "disease": disease,
            "user_context": user_context,
            "symptoms": symptoms
        }
        
        # Mock web search
        agent_with_web_search.search_web = MagicMock(return_value=[])
        
        # Mock LangChain execution
        mock_recommendations = json.dumps({
            "diet_plan": [{"recommendation": "Dynamic diet", "priority": "high"}],
            "exercise_plan": [{"activity": "Dynamic exercise", "frequency": "daily", "duration": "30 min", "priority": "high"}],
            "stress_management": [{"technique": "Technique", "how_to": "Instructions"}],
            "sleep_hygiene": [{"tip": "Tip", "rationale": "Reason"}],
            "immediate_actions": ["Action"]
        })
        agent_with_web_search.execute_chain = MagicMock(return_value=mock_recommendations)
        
        # Patch file operations to detect static file loading
        with patch('builtins.open', side_effect=AssertionError("Static file should not be loaded")):
            with patch('json.load', side_effect=AssertionError("Static JSON should not be loaded")):
                # Act
                result = agent_with_web_search.process(input_data)
                
                # Assert - Should succeed without loading static files
                assert result is not None, "Should work without static files"
                # If it reaches here, no static files were loaded


# ============================================================================
# Integration Tests for Multiple Properties
# ============================================================================

class TestMultiplePropertiesIntegration:
    """
    Integration tests that validate multiple properties together.
    """
    
    @given(
        disease=disease_strategy,
        user_context=user_context_strategy,
        symptoms=symptoms_strategy,
        search_results=st.lists(search_result_strategy, min_size=2, max_size=5)
    )
    @settings(
        max_examples=20,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_complete_lifestyle_workflow_with_dynamic_retrieval(
        self,
        agent_with_web_search,
        disease,
        user_context,
        symptoms,
        search_results
    ):
        """
        Test complete lifestyle recommendation workflow validating multiple properties.
        
        This test validates:
        - Property 1: Migration preserves functionality
        - Property 6: Dynamic retrieval replaces static lookups
        """
        # Arrange
        input_data = {
            "disease": disease,
            "user_context": user_context,
            "symptoms": symptoms
        }
        
        # Mock web search
        agent_with_web_search.search_web = MagicMock(return_value=search_results)
        
        # Mock LangChain execution
        mock_recommendations = json.dumps({
            "diet_plan": [
                {"recommendation": "Evidence-based nutrition", "evidence": "Clinical studies", "priority": "high"}
            ],
            "exercise_plan": [
                {"activity": "Personalized exercise", "frequency": "daily", "duration": "30 min", 
                 "safety_notes": "Consult doctor", "priority": "high"}
            ],
            "stress_management": [
                {"technique": "Proven technique", "how_to": "Instructions", "evidence": "Research"}
            ],
            "sleep_hygiene": [
                {"tip": "Sleep tip", "rationale": "Science-based"}
            ],
            "immediate_actions": ["Start today", "Track progress", "Consult professional"],
            "contraindications": ["Avoid X", "Avoid Y"],
            "personalization_notes": f"Tailored for {user_context['age']} year old with {disease}"
        })
        agent_with_web_search.execute_chain = MagicMock(return_value=mock_recommendations)
        
        # Act
        result = agent_with_web_search.process(input_data)
        
        # Assert - Property 1: Valid response structure
        assert result is not None
        assert result.get("success")
        assert "data" in result
        
        data = result["data"]
        
        # Verify all required fields
        assert "diet_plan" in data or "text_plan" in data
        assert "generated_at" in data
        assert "agent" in data
        
        # Assert - Property 6: Dynamic retrieval was used
        agent_with_web_search.search_web.assert_called()
        
        # Verify evidence-based content
        if "diet_plan" in data and isinstance(data["diet_plan"], list):
            # Should have structured recommendations
            assert len(data["diet_plan"]) > 0
            
        # Verify personalization
        if "personalization" in data:
            assert "age" in data["personalization"]
            assert "condition" in data["personalization"]
