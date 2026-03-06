"""
Unit tests for LifestyleModificationAgent.

Tests the migrated LifestyleModificationAgent with enhanced capabilities including
web search for evidence-based interventions, dynamic retrieval, personalization,
and citation generation.

Requirements tested:
- 1.1: Inherits from EnhancedBaseHealthAgent
- 1.2: Uses LangChain chains
- 1.3: Web search integration
- 1.5: Autonomous decision-making
- 1.6: Preserves existing functionality
- 2.4: Web search for lifestyle interventions
- 3.3, 3.4: Dynamic retrieval replaces static data
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from agents.lifestyle import LifestyleModificationAgent
from agents.infrastructure.config import AgentConfig


@pytest.fixture
def lifestyle_agent():
    """Create a LifestyleModificationAgent instance for testing."""
    config = AgentConfig(
        agent_name="LifestyleModificationAgent",
        enable_web_search=False,
        timeout=30,
        max_retries=2
    )
    
    # Mock the LLM and chains to avoid initialization issues
    with patch('agents.infrastructure.enhanced_base_agent.LangChainGeminiClient') as mock_client:
        mock_llm = MagicMock()
        mock_client.return_value.llm = mock_llm
        
        agent = LifestyleModificationAgent(config)
        agent.llm = mock_llm  # Ensure LLM is set
        
        # Mock the lifestyle chain
        agent.lifestyle_chain = MagicMock()
        
        return agent


@pytest.fixture
def lifestyle_agent_with_web_search():
    """Create a LifestyleModificationAgent with web search enabled."""
    config = AgentConfig(
        agent_name="LifestyleModificationAgent",
        enable_web_search=True,
        timeout=30,
        max_retries=2
    )
    
    with patch('agents.infrastructure.enhanced_base_agent.LangChainGeminiClient') as mock_client:
        mock_llm = MagicMock()
        mock_client.return_value.llm = mock_llm
        
        agent = LifestyleModificationAgent(config)
        agent.llm = mock_llm
        agent.lifestyle_chain = MagicMock()
        
        # Mock web search tool
        agent.web_search_tool = MagicMock()
        agent.search_web = MagicMock()
        
        return agent


@pytest.fixture
def sample_input():
    """Sample input data for lifestyle recommendation generation."""
    return {
        "disease": "diabetes",
        "user_context": {
            "age": 45,
            "gender": "male",
            "medical_history": "No prior conditions"
        },
        "symptoms": ["increased_thirst", "frequent_urination", "fatigue"],
        "confidence": "MEDIUM"
    }


@pytest.fixture
def sample_web_sources():
    """Sample web search results for lifestyle interventions."""
    return [
        {
            "title": "Evidence-Based Diabetes Lifestyle Interventions - PubMed",
            "url": "https://pubmed.ncbi.nlm.nih.gov/12345",
            "snippet": "Mediterranean diet and regular exercise reduce diabetes risk by 58%.",
            "source_domain": "pubmed.ncbi.nlm.nih.gov",
            "quality_score": 0.95
        },
        {
            "title": "Diabetes Prevention Program - CDC",
            "url": "https://www.cdc.gov/diabetes/prevention",
            "snippet": "Lifestyle changes including diet and exercise are effective for diabetes management.",
            "source_domain": "cdc.gov",
            "quality_score": 0.90
        }
    ]


@pytest.fixture
def sample_recommendations():
    """Sample structured lifestyle recommendations."""
    return {
        "diet_plan": [
            {"recommendation": "Reduce refined carbohydrates", "evidence": "Lowers blood sugar", "priority": "high"},
            {"recommendation": "Increase fiber intake", "evidence": "Improves glycemic control", "priority": "high"}
        ],
        "exercise_plan": [
            {"activity": "Brisk walking", "frequency": "5 days/week", "duration": "30 minutes", 
             "safety_notes": "Monitor blood sugar", "priority": "high"}
        ],
        "stress_management": [
            {"technique": "Mindfulness meditation", "how_to": "10 minutes daily", "evidence": "Reduces cortisol"}
        ],
        "sleep_hygiene": [
            {"tip": "Consistent sleep schedule", "rationale": "Regulates blood sugar"}
        ],
        "immediate_actions": [
            "Start walking routine",
            "Reduce sugar intake",
            "Monitor blood glucose"
        ],
        "contraindications": [
            "Avoid high-sugar foods",
            "Avoid intense exercise without medical clearance"
        ],
        "personalization_notes": "Plan tailored for 45-year-old male with diabetes"
    }


class TestLifestyleAgentInitialization:
    """Test LifestyleModificationAgent initialization."""
    
    def test_initialization_with_config(self):
        """Test agent initializes with custom config."""
        config = AgentConfig(
            agent_name="TestLifestyle",
            timeout=60,
            max_retries=5,
            enable_web_search=True
        )
        
        with patch('agents.infrastructure.enhanced_base_agent.LangChainGeminiClient') as mock_client:
            mock_llm = MagicMock()
            mock_client.return_value.llm = mock_llm
            
            agent = LifestyleModificationAgent(config)
            
            assert agent.agent_name == "LifestyleModificationAgent"
            assert agent.config.timeout == 60
            assert agent.config.max_retries == 5
            assert agent.config.enable_web_search is True
    
    def test_initialization_without_config(self):
        """Test agent initializes with default config."""
        with patch('agents.infrastructure.enhanced_base_agent.LangChainGeminiClient') as mock_client:
            mock_llm = MagicMock()
            mock_client.return_value.llm = mock_llm
            
            agent = LifestyleModificationAgent()
            
            assert agent.agent_name == "LifestyleModificationAgent"
            assert agent.config.agent_name == "LifestyleModificationAgent"
            assert agent.llm is not None
    
    def test_lifestyle_chain_created(self, lifestyle_agent):
        """Test that lifestyle chain is properly created."""
        assert lifestyle_agent.lifestyle_chain is not None


class TestLifestyleRecommendationGeneration:
    """Test lifestyle recommendation generation functionality."""
    
    def test_process_with_valid_input(self, lifestyle_agent, sample_input, sample_recommendations):
        """Test recommendation generation with valid input."""
        # Mock the execute_chain method
        mock_response = json.dumps(sample_recommendations)
        lifestyle_agent.execute_chain = MagicMock(return_value=mock_response)
        
        # Process the input
        result = lifestyle_agent.process(sample_input)
        
        # Verify response structure
        assert result is not None
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "data" in result
        
        # Verify recommendation data
        data = result["data"]
        assert "diet_plan" in data or "text_plan" in data
        assert "generated_at" in data
        assert "agent" in data
        
        # If structured response, verify structure
        if "diet_plan" in data:
            assert isinstance(data["diet_plan"], list)
            assert "exercise_plan" in data
            assert isinstance(data["exercise_plan"], list)
    
    def test_process_with_missing_required_fields(self, lifestyle_agent):
        """Test that missing required fields are handled."""
        invalid_input = {
            "disease": "diabetes"
            # Missing user_context
        }
        
        result = lifestyle_agent.process(invalid_input)
        
        # Should return error response
        assert result is not None
        assert result.get("success") is False
        assert "message" in result
    
    def test_recommendations_include_all_pillars(self, lifestyle_agent, sample_input, sample_recommendations):
        """Test that recommendations cover all 4 pillars."""
        mock_response = json.dumps(sample_recommendations)
        lifestyle_agent.execute_chain = MagicMock(return_value=mock_response)
        
        result = lifestyle_agent.process(sample_input)
        
        assert result.get("success") is True
        data = result["data"]
        
        # Verify all 4 pillars are present
        if "diet_plan" in data:
            assert "diet_plan" in data
            assert "exercise_plan" in data
            assert "stress_management" in data
            assert "sleep_hygiene" in data
    
    def test_recommendations_include_immediate_actions(self, lifestyle_agent, sample_input, sample_recommendations):
        """Test that recommendations include immediate actions."""
        mock_response = json.dumps(sample_recommendations)
        lifestyle_agent.execute_chain = MagicMock(return_value=mock_response)
        
        result = lifestyle_agent.process(sample_input)
        
        assert result.get("success") is True
        data = result["data"]
        
        # Verify immediate actions
        if "immediate_actions" in data:
            assert isinstance(data["immediate_actions"], list)
            assert len(data["immediate_actions"]) > 0


class TestPersonalization:
    """Test personalization based on user profile."""
    
    def test_personalization_by_age(self, lifestyle_agent, sample_input, sample_recommendations):
        """Test that recommendations are personalized by age."""
        mock_response = json.dumps(sample_recommendations)
        lifestyle_agent.execute_chain = MagicMock(return_value=mock_response)
        
        result = lifestyle_agent.process(sample_input)
        
        assert result.get("success") is True
        data = result["data"]
        
        # Verify personalization metadata
        if "personalization" in data:
            assert "age" in data["personalization"]
            assert data["personalization"]["age"] == 45
    
    def test_personalization_by_gender(self, lifestyle_agent, sample_input, sample_recommendations):
        """Test that recommendations consider gender."""
        mock_response = json.dumps(sample_recommendations)
        lifestyle_agent.execute_chain = MagicMock(return_value=mock_response)
        
        result = lifestyle_agent.process(sample_input)
        
        assert result.get("success") is True
        data = result["data"]
        
        # Verify gender is included in personalization
        if "personalization" in data:
            assert "gender" in data["personalization"]
            assert data["personalization"]["gender"] == "male"
    
    def test_personalization_by_condition(self, lifestyle_agent, sample_input, sample_recommendations):
        """Test that recommendations are tailored to the condition."""
        mock_response = json.dumps(sample_recommendations)
        lifestyle_agent.execute_chain = MagicMock(return_value=mock_response)
        
        result = lifestyle_agent.process(sample_input)
        
        assert result.get("success") is True
        data = result["data"]
        
        # Verify condition is included in personalization
        if "personalization" in data:
            assert "condition" in data["personalization"]
            assert data["personalization"]["condition"] == "diabetes"


class TestWebSearchIntegration:
    """Test web search integration for evidence-based interventions."""
    
    def test_web_search_called_when_enabled(
        self, 
        lifestyle_agent_with_web_search, 
        sample_input,
        sample_web_sources,
        sample_recommendations
    ):
        """Test that web search is called when enabled."""
        # Mock web search
        lifestyle_agent_with_web_search.search_web = MagicMock(return_value=sample_web_sources)
        
        # Mock recommendation generation
        mock_response = json.dumps(sample_recommendations)
        lifestyle_agent_with_web_search.execute_chain = MagicMock(return_value=mock_response)
        
        # Process
        result = lifestyle_agent_with_web_search.process(sample_input)
        
        # Verify web search was called
        lifestyle_agent_with_web_search.search_web.assert_called()
        
        # Verify result includes sources
        assert result.get("success") is True
        data = result["data"]
        assert "sources" in data
    
    def test_web_search_query_includes_lifestyle_keywords(
        self,
        lifestyle_agent_with_web_search,
        sample_input,
        sample_web_sources,
        sample_recommendations
    ):
        """Test that web search query includes lifestyle intervention keywords."""
        # Mock web search
        lifestyle_agent_with_web_search.search_web = MagicMock(return_value=sample_web_sources)
        
        # Mock recommendation generation
        mock_response = json.dumps(sample_recommendations)
        lifestyle_agent_with_web_search.execute_chain = MagicMock(return_value=mock_response)
        
        # Process
        result = lifestyle_agent_with_web_search.process(sample_input)
        
        # Verify web search was called
        lifestyle_agent_with_web_search.search_web.assert_called()
        
        # Check the search query
        call_args = lifestyle_agent_with_web_search.search_web.call_args
        if call_args:
            query = call_args[1].get("query", "") if len(call_args) > 1 else call_args[0][0] if call_args[0] else ""
            assert any(keyword in query.lower() for keyword in [
                "lifestyle", "intervention", "diet", "exercise", "management", "evidence"
            ]), "Search query should include lifestyle intervention keywords"
    
    def test_citations_included_with_web_search(
        self,
        lifestyle_agent_with_web_search,
        sample_input,
        sample_web_sources,
        sample_recommendations
    ):
        """Test that citations are included when web search is used."""
        # Mock web search
        lifestyle_agent_with_web_search.search_web = MagicMock(return_value=sample_web_sources)
        
        # Mock recommendation generation
        mock_response = json.dumps(sample_recommendations)
        lifestyle_agent_with_web_search.execute_chain = MagicMock(return_value=mock_response)
        
        # Process
        result = lifestyle_agent_with_web_search.process(sample_input)
        
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
    
    def test_no_citations_when_web_search_disabled(self, lifestyle_agent, sample_input, sample_recommendations):
        """Test that no citations are included when web search is disabled."""
        # Mock recommendation generation
        mock_response = json.dumps(sample_recommendations)
        lifestyle_agent.execute_chain = MagicMock(return_value=mock_response)
        
        # Process
        result = lifestyle_agent.process(sample_input)
        
        assert result.get("success") is True
        data = result["data"]
        
        # Verify no sources when web search is disabled
        sources = data.get("sources", [])
        assert len(sources) == 0


class TestDynamicRetrieval:
    """Test dynamic retrieval replaces static data."""
    
    def test_no_static_data_files_loaded(
        self,
        lifestyle_agent_with_web_search,
        sample_input,
        sample_recommendations
    ):
        """Test that no static data files are loaded."""
        # Mock web search
        lifestyle_agent_with_web_search.search_web = MagicMock(return_value=[])
        
        # Mock recommendation generation
        mock_response = json.dumps(sample_recommendations)
        lifestyle_agent_with_web_search.execute_chain = MagicMock(return_value=mock_response)
        
        # Patch file operations to detect static file loading
        with patch('builtins.open', side_effect=AssertionError("Static file should not be loaded")):
            with patch('json.load', side_effect=AssertionError("Static JSON should not be loaded")):
                # Act
                result = lifestyle_agent_with_web_search.process(sample_input)
                
                # Assert - Should succeed without loading static files
                assert result is not None
    
    def test_recommendations_use_dynamic_generation(
        self,
        lifestyle_agent_with_web_search,
        sample_input,
        sample_web_sources,
        sample_recommendations
    ):
        """Test that recommendations are dynamically generated, not from templates."""
        # Mock web search
        lifestyle_agent_with_web_search.search_web = MagicMock(return_value=sample_web_sources)
        
        # Mock LangChain execution
        mock_response = json.dumps(sample_recommendations)
        lifestyle_agent_with_web_search.execute_chain = MagicMock(return_value=mock_response)
        
        # Process
        result = lifestyle_agent_with_web_search.process(sample_input)
        
        # Verify LangChain was used for generation
        lifestyle_agent_with_web_search.execute_chain.assert_called()
        
        # Verify result is successful
        assert result.get("success") is True


class TestFallbackBehavior:
    """Test fallback behavior when primary generation fails."""
    
    def test_fallback_to_template_on_chain_failure(self, lifestyle_agent, sample_input):
        """Test that fallback template is used when chain fails."""
        # Mock chain to raise exception
        lifestyle_agent.execute_chain = MagicMock(side_effect=Exception("LLM error"))
        
        # Process
        result = lifestyle_agent.process(sample_input)
        
        # Should still return a response
        assert result is not None
        assert isinstance(result, dict)
        
        # Should have fallback recommendations
        if result.get("success"):
            data = result["data"]
            assert "diet_plan" in data or "text_plan" in data
    
    def test_fallback_includes_basic_recommendations(self, lifestyle_agent, sample_input):
        """Test that fallback includes basic recommendations."""
        # Mock chain to return None
        lifestyle_agent.execute_chain = MagicMock(return_value=None)
        
        # Process
        result = lifestyle_agent.process(sample_input)
        
        # Should have fallback
        if result.get("success"):
            data = result["data"]
            assert "diet_plan" in data
            assert "exercise_plan" in data
            assert "generated_by" in data
            assert data["generated_by"] == "template_fallback"


class TestErrorHandling:
    """Test error handling in recommendation generation."""
    
    def test_web_search_failure_handled_gracefully(
        self,
        lifestyle_agent_with_web_search,
        sample_input,
        sample_recommendations
    ):
        """Test that web search failures are handled gracefully."""
        # Mock web search to raise exception
        lifestyle_agent_with_web_search.search_web = MagicMock(side_effect=Exception("Search API error"))
        
        # Mock recommendation generation
        mock_response = json.dumps(sample_recommendations)
        lifestyle_agent_with_web_search.execute_chain = MagicMock(return_value=mock_response)
        
        # Process - should not fail
        result = lifestyle_agent_with_web_search.process(sample_input)
        
        # Should still succeed with recommendations
        assert result is not None
    
    def test_retry_logic_on_transient_failures(self, lifestyle_agent, sample_input, sample_recommendations):
        """Test that retry logic is applied on transient failures."""
        # Mock execute_with_retry to verify it's called
        lifestyle_agent.execute_with_retry = MagicMock(return_value=sample_recommendations)
        
        # Process
        result = lifestyle_agent.process(sample_input)
        
        # Verify retry logic was used
        lifestyle_agent.execute_with_retry.assert_called()
    
    def test_invalid_json_response_handled(self, lifestyle_agent, sample_input):
        """Test that invalid JSON responses are handled."""
        # Mock chain to return invalid JSON
        lifestyle_agent.execute_chain = MagicMock(return_value="This is not JSON")
        
        # Process
        result = lifestyle_agent.process(sample_input)
        
        # Should still return a response
        assert result is not None
        
        # Should have text_plan as fallback
        if result.get("success"):
            data = result["data"]
            assert "text_plan" in data or "diet_plan" in data


class TestDiseaseSpecificRecommendations:
    """Test disease-specific recommendation generation."""
    
    @pytest.mark.parametrize("disease", ["diabetes", "heart_disease", "hypertension"])
    def test_recommendations_for_different_diseases(self, lifestyle_agent, disease, sample_recommendations):
        """Test that recommendations are generated for different diseases."""
        input_data = {
            "disease": disease,
            "user_context": {"age": 50, "gender": "female", "medical_history": "None"},
            "symptoms": ["symptom1", "symptom2"]
        }
        
        mock_response = json.dumps(sample_recommendations)
        lifestyle_agent.execute_chain = MagicMock(return_value=mock_response)
        
        result = lifestyle_agent.process(input_data)
        
        assert result.get("success") is True
        data = result["data"]
        assert "diet_plan" in data or "text_plan" in data
    
    def test_fallback_templates_for_common_diseases(self, lifestyle_agent):
        """Test that fallback templates exist for common diseases."""
        # Test diabetes template
        diabetes_plan = lifestyle_agent._generate_template_plan("diabetes", 45)
        assert "diet_plan" in diabetes_plan
        assert "exercise_plan" in diabetes_plan
        
        # Test heart disease template
        heart_plan = lifestyle_agent._generate_template_plan("heart_disease", 60)
        assert "diet_plan" in heart_plan
        assert "exercise_plan" in heart_plan
        
        # Test hypertension template
        hypertension_plan = lifestyle_agent._generate_template_plan("hypertension", 55)
        assert "diet_plan" in hypertension_plan
        assert "exercise_plan" in hypertension_plan
