"""
Property-Based Tests for ExplanationAgent

Tests universal correctness properties that should hold across all valid inputs
for the enhanced explanation agent with web search and citation capabilities.

Requirements: 1.6, 2.6, 7.7, 15.7

Properties Tested:
- Property 1: Agent Migration Preserves Functionality (Requirement 1.6)
- Property 3: Web Search Results Include Citations (Requirements 2.6, 7.7, 15.7)
"""

import pytest
pytest_plugins = ['pytest_asyncio']
pytestmark = pytest.mark.pbt

import pytest
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from typing import Dict, Any, List
import json

from .explanation import LangChainExplanationAgent
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
        agent_name="ExplanationAgent",
        enable_web_search=True,
        enable_caching=True,
        monitoring_enabled=False
    )
    agent = LangChainExplanationAgent(config)
    
    # Mock web search tool
    agent.web_search_tool = MagicMock()
    
    return agent


@pytest.fixture
def agent_without_web_search(mock_gemini_client):
    """Create agent with web search disabled."""
    config = AgentConfig(
        agent_name="ExplanationAgent",
        enable_web_search=False,
        monitoring_enabled=False
    )
    agent = LangChainExplanationAgent(config)
    return agent


# ============================================================================
# Hypothesis Strategies for Generating Test Data
# ============================================================================

# Valid disease strategy
disease_strategy = st.sampled_from([
    "diabetes", "heart_disease", "hypertension", "asthma", 
    "arthritis", "migraine", "depression", "anxiety"
])

# Valid probability strategy (0.0 to 1.0)
probability_strategy = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)

# Valid confidence strategy
confidence_strategy = st.sampled_from(["LOW", "MEDIUM", "HIGH"])

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
    
    For any valid input (disease, probability, confidence, symptoms),
    the migrated agent should produce a valid explanation response with
    all required fields.
    """
    
    @given(
        disease=disease_strategy,
        probability=probability_strategy,
        confidence=confidence_strategy,
        symptoms=symptoms_strategy
    )
    @settings(
        max_examples=50,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_migrated_agent_produces_valid_explanation(
        self,
        agent_without_web_search,
        disease,
        probability,
        confidence,
        symptoms
    ):
        """
        Test that migrated agent produces valid explanation for any valid input.
        
        This validates that the migration to EnhancedBaseHealthAgent preserves
        the core functionality of generating explanations.
        """
        # Arrange
        input_data = {
            "disease": disease,
            "probability": probability,
            "confidence": confidence,
            "symptoms": symptoms
        }
        
        # Mock the LangChain chain execution
        mock_explanation = f"This is a detailed explanation about {disease}."
        agent_without_web_search.execute_chain = MagicMock(return_value=mock_explanation)
        
        # Act
        result = agent_without_web_search.process(input_data)
        
        # Assert - Verify response structure
        assert result is not None, "Agent should return a response"
        assert isinstance(result, dict), "Response should be a dictionary"
        assert "success" in result, "Response should have success field"
        
        # If successful, verify explanation data structure
        if result["success"]:
            assert "data" in result, "Successful response should have data field"
            data = result["data"]
            
            # Verify required fields in explanation
            assert "summary" in data, "Explanation should have summary"
            assert "probability_percent" in data, "Explanation should have probability_percent"
            assert "confidence" in data, "Explanation should have confidence"
            assert "main_explanation" in data, "Explanation should have main_explanation"
            assert "confidence_reasoning" in data, "Explanation should have confidence_reasoning"
            assert "disclaimer" in data, "Explanation should have medical disclaimer"
            assert "generated_at" in data, "Explanation should have timestamp"
            assert "agent" in data, "Explanation should identify the agent"
            
            # Verify data types
            assert isinstance(data["probability_percent"], (int, float)), "Probability should be numeric"
            assert data["confidence"] in ["LOW", "MEDIUM", "HIGH"], "Confidence should be valid level"
            assert isinstance(data["main_explanation"], str), "Explanation should be string"
            assert len(data["main_explanation"]) > 0, "Explanation should not be empty"
    
    @given(
        disease=disease_strategy,
        probability=probability_strategy,
        confidence=confidence_strategy,
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
        probability,
        confidence,
        symptoms
    ):
        """
        Test that migrated agent handles errors gracefully.
        
        This validates that error handling is preserved after migration.
        """
        # Arrange
        input_data = {
            "disease": disease,
            "probability": probability,
            "confidence": confidence,
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
        
        # Should have fallback explanation
        if "data" in result:
            data = result["data"]
            assert "main_explanation" in data, "Should have fallback explanation"
            assert "disclaimer" in data, "Should still have disclaimer"


# ============================================================================
# Property 3: Web Search Results Include Citations
# Validates: Requirements 2.6, 7.7, 15.7
# ============================================================================

class TestProperty3_WebSearchIncludesCitations:
    """
    Property 3: Web Search Results Include Citations
    
    For any explanation that uses web search results, the response should
    include proper citations with source URLs and metadata.
    """
    
    @given(
        disease=disease_strategy,
        probability=probability_strategy,
        confidence=confidence_strategy,
        symptoms=symptoms_strategy,
        search_results=st.lists(search_result_strategy, min_size=1, max_size=5)
    )
    @settings(
        max_examples=50,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_web_search_results_include_citations(
        self,
        agent_with_web_search,
        disease,
        probability,
        confidence,
        symptoms,
        search_results
    ):
        """
        Test that explanations using web search include proper citations.
        
        This validates that all web search results are properly cited with
        URLs, sources, and access dates.
        """
        # Arrange
        input_data = {
            "disease": disease,
            "probability": probability,
            "confidence": confidence,
            "symptoms": symptoms
        }
        
        # Mock web search to return results
        agent_with_web_search.search_web = MagicMock(return_value=search_results)
        
        # Mock the LangChain chain execution
        mock_explanation = f"Based on medical literature, {disease} is characterized by..."
        agent_with_web_search.execute_chain = MagicMock(return_value=mock_explanation)
        
        # Act
        result = agent_with_web_search.process(input_data)
        
        # Assert
        assert result is not None, "Agent should return a response"
        assert result.get("success"), "Response should be successful"
        
        data = result.get("data", {})
        
        # Verify citations are present
        assert "sources" in data, "Response should include sources field"
        sources = data["sources"]
        
        if len(search_results) > 0:
            assert isinstance(sources, list), "Sources should be a list"
            assert len(sources) > 0, "Sources list should not be empty when web search is used"
            
            # Verify each citation has required fields
            for citation in sources:
                assert "url" in citation, "Citation should have URL"
                assert "source" in citation, "Citation should have source domain"
                assert "accessed" in citation, "Citation should have access date"
                assert isinstance(citation["url"], str), "URL should be string"
                assert len(citation["url"]) > 0, "URL should not be empty"
    
    @given(
        disease=disease_strategy,
        probability=probability_strategy,
        confidence=confidence_strategy,
        symptoms=symptoms_strategy,
        search_results=st.lists(search_result_strategy, min_size=1, max_size=10)
    )
    @settings(
        max_examples=30,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_citations_limited_to_reasonable_number(
        self,
        agent_with_web_search,
        disease,
        probability,
        confidence,
        symptoms,
        search_results
    ):
        """
        Test that citations are limited to a reasonable number (top 5 sources).
        
        This validates that even with many search results, only the most
        relevant sources are cited.
        """
        # Arrange
        input_data = {
            "disease": disease,
            "probability": probability,
            "confidence": confidence,
            "symptoms": symptoms
        }
        
        # Mock web search to return many results
        agent_with_web_search.search_web = MagicMock(return_value=search_results)
        
        # Mock the LangChain chain execution
        mock_explanation = f"Medical research on {disease} shows..."
        agent_with_web_search.execute_chain = MagicMock(return_value=mock_explanation)
        
        # Act
        result = agent_with_web_search.process(input_data)
        
        # Assert
        assert result.get("success"), "Response should be successful"
        
        data = result.get("data", {})
        sources = data.get("sources", [])
        
        # Verify citations are limited to top 5
        assert len(sources) <= 5, "Citations should be limited to top 5 sources"
    
    @given(
        disease=disease_strategy,
        probability=probability_strategy,
        confidence=confidence_strategy,
        symptoms=symptoms_strategy
    )
    @settings(
        max_examples=30,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_no_citations_when_web_search_disabled(
        self,
        agent_without_web_search,
        disease,
        probability,
        confidence,
        symptoms
    ):
        """
        Test that no citations are included when web search is disabled.
        
        This validates that citations are only included when web search
        is actually used.
        """
        # Arrange
        input_data = {
            "disease": disease,
            "probability": probability,
            "confidence": confidence,
            "symptoms": symptoms
        }
        
        # Mock the LangChain chain execution
        mock_explanation = f"Explanation about {disease}."
        agent_without_web_search.execute_chain = MagicMock(return_value=mock_explanation)
        
        # Act
        result = agent_without_web_search.process(input_data)
        
        # Assert
        assert result.get("success"), "Response should be successful"
        
        data = result.get("data", {})
        sources = data.get("sources", [])
        
        # Verify no citations when web search is disabled
        assert len(sources) == 0, "Should have no citations when web search is disabled"


# ============================================================================
# Integration Tests for Multiple Properties
# ============================================================================

class TestMultiplePropertiesIntegration:
    """
    Integration tests that validate multiple properties together.
    """
    
    @given(
        disease=disease_strategy,
        probability=probability_strategy,
        confidence=confidence_strategy,
        symptoms=symptoms_strategy,
        search_results=st.lists(search_result_strategy, min_size=2, max_size=5)
    )
    @settings(
        max_examples=20,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_complete_explanation_workflow_with_citations(
        self,
        agent_with_web_search,
        disease,
        probability,
        confidence,
        symptoms,
        search_results
    ):
        """
        Test complete explanation workflow validating multiple properties.
        
        This test validates:
        - Property 1: Migration preserves functionality
        - Property 3: Web search results include citations
        """
        # Arrange
        input_data = {
            "disease": disease,
            "probability": probability,
            "confidence": confidence,
            "symptoms": symptoms
        }
        
        # Mock web search
        agent_with_web_search.search_web = MagicMock(return_value=search_results)
        
        # Mock LangChain execution
        mock_explanation = (
            f"Based on current medical research, {disease} is a condition that "
            f"affects many people. The symptoms you've described are consistent "
            f"with this condition."
        )
        agent_with_web_search.execute_chain = MagicMock(return_value=mock_explanation)
        
        # Act
        result = agent_with_web_search.process(input_data)
        
        # Assert - Property 1: Valid response structure
        assert result is not None
        assert result.get("success")
        assert "data" in result
        
        data = result["data"]
        
        # Verify all required fields
        assert "summary" in data
        assert "probability_percent" in data
        assert "confidence" in data
        assert "main_explanation" in data
        assert "disclaimer" in data
        
        # Assert - Property 3: Citations included
        assert "sources" in data
        sources = data["sources"]
        assert len(sources) > 0, "Should have citations from web search"
        
        # Verify citation quality
        for citation in sources:
            assert "url" in citation
            assert "source" in citation
            assert citation["source"] in [
                "pubmed.ncbi.nlm.nih.gov", "who.int", "cdc.gov",
                "mayoclinic.org", "nih.gov"
            ], "Citations should be from reliable medical sources"
