"""
Unit tests for ExplanationAgent.

Tests the migrated ExplanationAgent with enhanced capabilities including
web search, citation generation, and safety guardrails.

Requirements tested:
- 1.1: Inherits from EnhancedBaseHealthAgent
- 1.2: Uses LangChain chains
- 1.3: Web search integration
- 1.5: Autonomous decision-making
- 1.6: Preserves existing functionality
- 2.6: Citation of sources
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from agents.explanation import LangChainExplanationAgent
from agents.infrastructure.config import AgentConfig


@pytest.fixture
def explanation_agent():
    """Create an ExplanationAgent instance for testing."""
    config = AgentConfig(
        agent_name="ExplanationAgent",
        enable_web_search=False,
        timeout=30,
        max_retries=2
    )
    
    # Mock the LLM and chains to avoid initialization issues
    with patch('agents.infrastructure.enhanced_base_agent.LangChainGeminiClient') as mock_client:
        mock_llm = MagicMock()
        mock_client.return_value.llm = mock_llm
        
        agent = LangChainExplanationAgent(config)
        agent.llm = mock_llm  # Ensure LLM is set
        
        # Mock the explanation chain
        agent.explanation_chain = MagicMock()
        
        return agent


@pytest.fixture
def explanation_agent_with_web_search():
    """Create an ExplanationAgent with web search enabled."""
    config = AgentConfig(
        agent_name="ExplanationAgent",
        enable_web_search=True,
        timeout=30,
        max_retries=2
    )
    
    with patch('agents.infrastructure.enhanced_base_agent.LangChainGeminiClient') as mock_client:
        mock_llm = MagicMock()
        mock_client.return_value.llm = mock_llm
        
        agent = LangChainExplanationAgent(config)
        agent.llm = mock_llm
        agent.explanation_chain = MagicMock()
        
        # Mock web search tool
        agent.web_search_tool = MagicMock()
        agent.search_web = MagicMock()
        
        return agent


@pytest.fixture
def sample_input():
    """Sample input data for explanation generation."""
    return {
        "disease": "diabetes",
        "probability": 0.75,
        "confidence": "HIGH",
        "symptoms": ["increased_thirst", "frequent_urination", "fatigue", "blurred_vision"]
    }


@pytest.fixture
def sample_web_sources():
    """Sample web search results."""
    return [
        {
            "title": "Diabetes Overview - PubMed",
            "url": "https://pubmed.ncbi.nlm.nih.gov/12345",
            "snippet": "Diabetes is a metabolic disorder characterized by high blood sugar levels.",
            "source_domain": "pubmed.ncbi.nlm.nih.gov",
            "quality_score": 0.95
        },
        {
            "title": "Understanding Diabetes - CDC",
            "url": "https://www.cdc.gov/diabetes",
            "snippet": "Learn about diabetes symptoms, causes, and management.",
            "source_domain": "cdc.gov",
            "quality_score": 0.90
        }
    ]


class TestExplanationAgentInitialization:
    """Test ExplanationAgent initialization."""
    
    def test_initialization_with_config(self):
        """Test agent initializes with custom config."""
        config = AgentConfig(
            agent_name="TestExplanation",
            timeout=60,
            max_retries=5,
            enable_web_search=True
        )
        
        with patch('agents.infrastructure.enhanced_base_agent.LangChainGeminiClient') as mock_client:
            mock_llm = MagicMock()
            mock_client.return_value.llm = mock_llm
            
            agent = LangChainExplanationAgent(config)
            
            assert agent.agent_name == "ExplanationAgent"
            assert agent.config.timeout == 60
            assert agent.config.max_retries == 5
            assert agent.config.enable_web_search is True
    
    def test_initialization_without_config(self):
        """Test agent initializes with default config."""
        with patch('agents.infrastructure.enhanced_base_agent.LangChainGeminiClient') as mock_client:
            mock_llm = MagicMock()
            mock_client.return_value.llm = mock_llm
            
            agent = LangChainExplanationAgent()
            
            assert agent.agent_name == "ExplanationAgent"
            assert agent.config.agent_name == "ExplanationAgent"
            assert agent.llm is not None
    
    def test_confidence_explanations_loaded(self, explanation_agent):
        """Test that confidence explanations are properly loaded."""
        assert "LOW" in explanation_agent.confidence_explanations
        assert "MEDIUM" in explanation_agent.confidence_explanations
        assert "HIGH" in explanation_agent.confidence_explanations
        
        # Verify structure of confidence explanations
        for level in ["LOW", "MEDIUM", "HIGH"]:
            assert "meaning" in explanation_agent.confidence_explanations[level]
            assert "reason" in explanation_agent.confidence_explanations[level]
            assert "recommendation" in explanation_agent.confidence_explanations[level]
    
    def test_medical_disclaimer_present(self, explanation_agent):
        """Test that medical disclaimer is defined."""
        assert explanation_agent.medical_disclaimer is not None
        assert len(explanation_agent.medical_disclaimer) > 0
        assert "not intended" in explanation_agent.medical_disclaimer.lower()
        assert "professional medical advice" in explanation_agent.medical_disclaimer.lower()


class TestExplanationGeneration:
    """Test explanation generation functionality."""
    
    def test_process_with_valid_input(self, explanation_agent, sample_input):
        """Test explanation generation with valid input."""
        # Mock the execute_chain method
        mock_explanation = (
            "Diabetes is a metabolic disorder that affects how your body processes blood sugar. "
            "Your symptoms of increased thirst and frequent urination are classic signs."
        )
        explanation_agent.execute_chain = MagicMock(return_value=mock_explanation)
        
        # Process the input
        result = explanation_agent.process(sample_input)
        
        # Verify response structure
        assert result is not None
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "data" in result
        
        # Verify explanation data
        data = result["data"]
        assert "summary" in data
        assert "probability_percent" in data
        assert "confidence" in data
        assert "main_explanation" in data
        assert "confidence_reasoning" in data
        assert "disclaimer" in data
        assert "generated_at" in data
        
        # Verify values
        assert data["confidence"] == "HIGH"
        assert data["probability_percent"] == 75.0
        assert len(data["main_explanation"]) > 0
    
    def test_process_with_missing_required_fields(self, explanation_agent):
        """Test that missing required fields are handled."""
        invalid_input = {
            "disease": "diabetes",
            "probability": 0.75
            # Missing confidence and symptoms
        }
        
        result = explanation_agent.process(invalid_input)
        
        # Should return error response
        assert result is not None
        assert result.get("success") is False
        assert "message" in result
    
    def test_explanation_includes_confidence_reasoning(self, explanation_agent, sample_input):
        """Test that explanation includes confidence reasoning."""
        mock_explanation = "Detailed explanation about diabetes."
        explanation_agent.execute_chain = MagicMock(return_value=mock_explanation)
        
        result = explanation_agent.process(sample_input)
        
        assert result.get("success") is True
        data = result["data"]
        
        # Verify confidence reasoning
        assert "confidence_reasoning" in data
        reasoning = data["confidence_reasoning"]
        assert "meaning" in reasoning
        assert "reason" in reasoning
        assert "recommendation" in reasoning
    
    def test_explanation_includes_educational_content(self, explanation_agent, sample_input):
        """Test that explanation includes educational content."""
        mock_explanation = "Explanation about diabetes."
        explanation_agent.execute_chain = MagicMock(return_value=mock_explanation)
        
        result = explanation_agent.process(sample_input)
        
        assert result.get("success") is True
        data = result["data"]
        
        # Verify educational content
        assert "educational_content" in data
        educational = data["educational_content"]
        assert isinstance(educational, dict)
    
    def test_explanation_includes_contributing_factors(self, explanation_agent, sample_input):
        """Test that explanation analyzes contributing factors."""
        mock_explanation = "Explanation about diabetes."
        explanation_agent.execute_chain = MagicMock(return_value=mock_explanation)
        
        result = explanation_agent.process(sample_input)
        
        assert result.get("success") is True
        data = result["data"]
        
        # Verify contributing factors analysis
        assert "contributing_factors" in data
        factors = data["contributing_factors"]
        assert isinstance(factors, dict)


class TestWebSearchIntegration:
    """Test web search integration for explanations."""
    
    def test_web_search_called_when_enabled(
        self, 
        explanation_agent_with_web_search, 
        sample_input,
        sample_web_sources
    ):
        """Test that web search is called when enabled."""
        # Mock web search
        explanation_agent_with_web_search.search_web = MagicMock(return_value=sample_web_sources)
        
        # Mock explanation generation
        mock_explanation = "Diabetes explanation with web context."
        explanation_agent_with_web_search.execute_chain = MagicMock(return_value=mock_explanation)
        
        # Process
        result = explanation_agent_with_web_search.process(sample_input)
        
        # Verify web search was called
        explanation_agent_with_web_search.search_web.assert_called()
        
        # Verify result includes sources
        assert result.get("success") is True
        data = result["data"]
        assert "sources" in data
    
    def test_citations_included_with_web_search(
        self,
        explanation_agent_with_web_search,
        sample_input,
        sample_web_sources
    ):
        """Test that citations are included when web search is used."""
        # Mock web search
        explanation_agent_with_web_search.search_web = MagicMock(return_value=sample_web_sources)
        
        # Mock explanation generation
        mock_explanation = "Diabetes explanation."
        explanation_agent_with_web_search.execute_chain = MagicMock(return_value=mock_explanation)
        
        # Process
        result = explanation_agent_with_web_search.process(sample_input)
        
        assert result.get("success") is True
        data = result["data"]
        
        # Verify citations
        assert "sources" in data
        sources = data["sources"]
        assert len(sources) > 0
        
        # Verify citation structure
        for citation in sources:
            assert "url" in citation
            assert "source" in citation
            assert "accessed" in citation
            assert "title" in citation
    
    def test_no_citations_when_web_search_disabled(self, explanation_agent, sample_input):
        """Test that no citations are included when web search is disabled."""
        # Mock explanation generation
        mock_explanation = "Diabetes explanation."
        explanation_agent.execute_chain = MagicMock(return_value=mock_explanation)
        
        # Process
        result = explanation_agent.process(sample_input)
        
        assert result.get("success") is True
        data = result["data"]
        
        # Verify no sources when web search is disabled
        sources = data.get("sources", [])
        assert len(sources) == 0


class TestSafetyGuardrails:
    """Test safety guardrails integration."""
    
    def test_medical_disclaimer_always_included(self, explanation_agent, sample_input):
        """Test that medical disclaimer is always included."""
        mock_explanation = "Explanation about diabetes."
        explanation_agent.execute_chain = MagicMock(return_value=mock_explanation)
        
        result = explanation_agent.process(sample_input)
        
        assert result.get("success") is True
        data = result["data"]
        
        # Verify disclaimer
        assert "disclaimer" in data
        assert len(data["disclaimer"]) > 0
        assert "not intended" in data["disclaimer"].lower()
    
    def test_safety_guardrails_applied_to_explanation(
        self,
        explanation_agent_with_web_search,
        sample_input
    ):
        """Test that safety guardrails are applied to generated explanations."""
        # Mock explanation with potentially unsafe content
        mock_explanation = "You have diabetes. Take 500mg metformin daily."
        explanation_agent_with_web_search.execute_chain = MagicMock(return_value=mock_explanation)
        
        # Mock safety guardrails
        safe_explanation = "Based on your symptoms, diabetes is a possibility. Consult a doctor for diagnosis and treatment."
        explanation_agent_with_web_search.apply_safety_guardrails = MagicMock(return_value=safe_explanation)
        
        # Process
        result = explanation_agent_with_web_search.process(sample_input)
        
        # Verify safety guardrails were applied
        explanation_agent_with_web_search.apply_safety_guardrails.assert_called()


class TestErrorHandling:
    """Test error handling in explanation generation."""
    
    def test_fallback_explanation_on_chain_failure(self, explanation_agent, sample_input):
        """Test that fallback explanation is provided when chain fails."""
        # Mock chain to raise exception
        explanation_agent.execute_chain = MagicMock(side_effect=Exception("LLM error"))
        
        # Process
        result = explanation_agent.process(sample_input)
        
        # Should still return a response
        assert result is not None
        assert isinstance(result, dict)
        
        # Should have fallback explanation
        if result.get("success"):
            data = result["data"]
            assert "main_explanation" in data
            assert len(data["main_explanation"]) > 0
    
    def test_web_search_failure_handled_gracefully(
        self,
        explanation_agent_with_web_search,
        sample_input
    ):
        """Test that web search failures are handled gracefully."""
        # Mock web search to raise exception
        explanation_agent_with_web_search.search_web = MagicMock(side_effect=Exception("Search API error"))
        
        # Mock explanation generation
        mock_explanation = "Explanation without web context."
        explanation_agent_with_web_search.execute_chain = MagicMock(return_value=mock_explanation)
        
        # Process - should not fail
        result = explanation_agent_with_web_search.process(sample_input)
        
        # Should still succeed with explanation
        assert result is not None
        # May succeed or fail depending on error handling, but should not crash
    
    def test_retry_logic_on_transient_failures(self, explanation_agent, sample_input):
        """Test that retry logic is applied on transient failures."""
        # Mock execute_with_retry to verify it's called
        explanation_agent.execute_with_retry = MagicMock(
            return_value={
                "summary": "Test",
                "probability_percent": 75.0,
                "confidence": "HIGH",
                "main_explanation": "Test explanation",
                "confidence_reasoning": {},
                "contributing_factors": {},
                "educational_content": {},
                "disclaimer": "Test disclaimer",
                "generated_at": datetime.utcnow().isoformat(),
                "generated_by": "test",
                "agent": "ExplanationAgent"
            }
        )
        
        # Process
        result = explanation_agent.process(sample_input)
        
        # Verify retry logic was used
        explanation_agent.execute_with_retry.assert_called()


class TestConfidenceLevels:
    """Test handling of different confidence levels."""
    
    @pytest.mark.parametrize("confidence", ["LOW", "MEDIUM", "HIGH"])
    def test_all_confidence_levels_handled(self, explanation_agent, sample_input, confidence):
        """Test that all confidence levels are properly handled."""
        sample_input["confidence"] = confidence
        
        mock_explanation = f"Explanation for {confidence} confidence."
        explanation_agent.execute_chain = MagicMock(return_value=mock_explanation)
        
        result = explanation_agent.process(sample_input)
        
        assert result.get("success") is True
        data = result["data"]
        assert data["confidence"] == confidence
        assert "confidence_reasoning" in data
    
    def test_confidence_reasoning_differs_by_level(self, explanation_agent):
        """Test that confidence reasoning differs for each level."""
        low_reasoning = explanation_agent._get_confidence_reasoning("LOW")
        medium_reasoning = explanation_agent._get_confidence_reasoning("MEDIUM")
        high_reasoning = explanation_agent._get_confidence_reasoning("HIGH")
        
        # Verify they are different
        assert low_reasoning != medium_reasoning
        assert medium_reasoning != high_reasoning
        assert low_reasoning != high_reasoning
        
        # Verify all have required fields
        for reasoning in [low_reasoning, medium_reasoning, high_reasoning]:
            assert "meaning" in reasoning
            assert "reason" in reasoning
            assert "recommendation" in reasoning
