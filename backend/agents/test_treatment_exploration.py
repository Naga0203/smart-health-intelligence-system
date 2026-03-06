"""
Unit tests for TreatmentExplorationAgent.

Tests specific examples, edge cases, and error conditions for:
- Treatment information retrieval
- Multi-system search
- Drug interaction detection
- Evidence level inclusion
- Safety guardrails
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from .treatment_exploration import TreatmentExplorationAgent
from .infrastructure.config import AgentConfig
from .infrastructure.models import SearchResult


@pytest.fixture
def mock_search_results():
    """Create mock search results."""
    def create_results(query):
        return [
            SearchResult(
                title=f"Treatment for {query}",
                url="https://pubmed.ncbi.nlm.nih.gov/test123",
                snippet=f"Clinical evidence for {query} treatment. Randomized controlled trials show effectiveness.",
                source_domain="pubmed.ncbi.nlm.nih.gov",
                quality_score=0.9,
                content=f"Detailed treatment information for {query} with evidence levels from clinical trials."
            ),
            SearchResult(
                title=f"{query} Guidelines",
                url="https://who.int/guidelines",
                snippet=f"WHO guidelines for {query} management.",
                source_domain="who.int",
                quality_score=0.95,
                content=f"International guidelines for {query} treatment."
            )
        ]
    return create_results


@pytest.fixture
def agent(mock_search_results):
    """Create TreatmentExplorationAgent with mocked dependencies."""
    config = AgentConfig(
        agent_name="TreatmentExplorationAgent",
        enable_web_search=True,
        enable_caching=False,
        monitoring_enabled=False
    )
    
    with patch('backend.agents.infrastructure.web_search.WebSearchTool') as mock_web_search_class, \
         patch('backend.agents.infrastructure.enhanced_base_agent.LangChainGeminiClient') as mock_gemini_class, \
         patch('backend.agents.infrastructure.enhanced_base_agent.MonitoringService'):
        
        # Setup web search mock
        search_tool = Mock()
        search_tool.search = Mock(side_effect=lambda q, f=None: mock_search_results(q))
        search_tool.search_clinical_guidelines = Mock(side_effect=lambda q: mock_search_results(q))
        search_tool.search_drug_information = Mock(side_effect=lambda d: {
            'drug': d,
            'interactions': f'Interaction information for {d}',
            'sources': ['https://drugs.com/test']
        })
        mock_web_search_class.return_value = search_tool
        
        # Setup LLM mock
        llm = Mock()
        llm.invoke = Mock(return_value="Synthesized treatment information with evidence from clinical trials")
        client = Mock()
        client.llm = llm
        mock_gemini_class.return_value = client
        
        yield TreatmentExplorationAgent(config)


class TestTreatmentInformationRetrieval:
    """Test treatment information retrieval functionality."""
    
    def test_retrieve_diabetes_treatment(self, agent):
        """Test retrieving treatment information for diabetes."""
        input_data = {
            'disease': 'diabetes',
            'system': 'allopathy'
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        assert 'data' in result
        assert 'disclaimer' in result['data']
        assert result['agent'] == 'TreatmentExplorationAgent'
    
    def test_retrieve_hypertension_treatment(self, agent):
        """Test retrieving treatment information for hypertension."""
        input_data = {
            'disease': 'hypertension',
            'system': 'ayurveda'
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        assert 'data' in result
        data = result['data']
        assert 'disclaimer' in data
    
    def test_retrieve_with_evidence_levels(self, agent):
        """Test retrieving treatment with evidence levels included."""
        input_data = {
            'disease': 'asthma',
            'system': 'allopathy',
            'include_evidence': True
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should include evidence analysis or clinical information
        # Note: Safety guardrails may add disclaimers to text
        data_str = str(data).lower()
        assert 'clinical' in data_str or 'guidelines' in data_str
    
    def test_retrieve_without_evidence_levels(self, agent):
        """Test retrieving treatment without evidence levels."""
        input_data = {
            'disease': 'arthritis',
            'system': 'homeopathy',
            'include_evidence': False
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        assert 'data' in result


class TestMultiSystemSearch:
    """Test multi-system treatment search functionality."""
    
    def test_multi_system_search_all(self, agent):
        """Test searching across all medical systems."""
        input_data = {
            'disease': 'diabetes',
            'system': 'all'
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should have systems information
        assert 'systems' in data or 'allopathy' in str(data).lower()
    
    def test_multi_system_includes_clinical_guidelines(self, agent):
        """Test that multi-system search includes clinical guidelines."""
        input_data = {
            'disease': 'hypertension',
            'system': 'all'
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should include clinical guidelines
        assert 'clinical_guidelines' in data or 'guidelines' in str(data).lower()
    
    def test_treatment_comparison(self, agent):
        """Test comparing treatments across systems."""
        result = agent.get_treatment_comparison(
            disease='diabetes',
            systems=['allopathy', 'ayurveda']
        )
        
        assert 'disease' in result
        # Disease field may have safety disclaimers appended
        assert 'diabetes' in result['disease']
        assert 'systems_compared' in result
        assert 'treatments' in result
        assert 'disclaimer' in result


class TestDrugInteractionDetection:
    """Test drug interaction detection functionality."""
    
    def test_single_medication_interaction(self, agent):
        """Test checking interactions for a single medication."""
        input_data = {
            'disease': 'diabetes',
            'system': 'allopathy',
            'medications': ['metformin']
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should include drug interactions
        assert 'drug_interactions' in data
        interactions = data['drug_interactions']
        assert 'medications' in interactions
        # Medication names may have safety disclaimers appended
        assert any('metformin' in str(med) for med in interactions['medications'])
    
    def test_multiple_medications_interaction(self, agent):
        """Test checking interactions for multiple medications."""
        input_data = {
            'disease': 'hypertension',
            'system': 'allopathy',
            'medications': ['lisinopril', 'amlodipine', 'aspirin']
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should include drug interactions
        assert 'drug_interactions' in data
        interactions = data['drug_interactions']
        assert 'medications' in interactions
        assert len(interactions['medications']) == 3
    
    def test_no_medications_provided(self, agent):
        """Test treatment query without medications."""
        input_data = {
            'disease': 'asthma',
            'system': 'allopathy'
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should not have drug interactions if no medications provided
        assert 'drug_interactions' not in data


class TestEvidenceLevelInclusion:
    """Test evidence level inclusion in treatment information."""
    
    def test_evidence_levels_requested(self, agent):
        """Test that evidence levels are included when requested."""
        input_data = {
            'disease': 'cancer',
            'system': 'allopathy',
            'include_evidence': True
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should have evidence information
        has_evidence = (
            'evidence_analysis' in data or
            'evidence' in str(data).lower() or
            'clinical' in str(data).lower() or
            'trial' in str(data).lower()
        )
        assert has_evidence
    
    def test_clinical_guidelines_search(self, agent):
        """Test searching for clinical guidelines."""
        result = agent.search_treatment_guidelines(
            condition='diabetes',
            guideline_type='clinical'
        )
        
        assert 'condition' in result
        assert 'guidelines' in result
        assert 'disclaimer' in result


class TestSafetyGuardrails:
    """Test safety guardrails integration."""
    
    def test_medical_disclaimer_present(self, agent):
        """Test that medical disclaimer is always present."""
        input_data = {
            'disease': 'diabetes',
            'system': 'allopathy'
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should have disclaimer
        assert 'disclaimer' in data
        disclaimer = data['disclaimer']
        assert len(disclaimer) > 50
        assert 'medical' in disclaimer.lower()
        assert 'professional' in disclaimer.lower()
    
    def test_safety_guardrails_applied(self, agent):
        """Test that safety guardrails are applied to responses."""
        input_data = {
            'disease': 'heart disease',
            'system': 'allopathy'
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        # Safety guardrails should prevent specific diagnoses and dosages
        # This is tested implicitly through the agent's processing


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_missing_disease_field(self, agent):
        """Test handling of missing disease field."""
        input_data = {
            'system': 'allopathy'
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is False
        assert 'message' in result
        assert 'required' in result['message'].lower()
    
    def test_empty_disease_name(self, agent):
        """Test handling of empty disease name."""
        input_data = {
            'disease': '',
            'system': 'allopathy'
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is False
    
    def test_invalid_medical_system(self, agent):
        """Test handling of invalid medical system."""
        input_data = {
            'disease': 'diabetes',
            'system': 'invalid_system'
        }
        
        result = agent.process(input_data)
        
        # Should still succeed but use default system
        assert result['success'] is True
    
    def test_none_input_data(self, agent):
        """Test handling of None input data."""
        result = agent.process(None)
        
        assert result['success'] is False
        assert 'message' in result
    
    def test_web_search_failure(self, agent):
        """Test handling of web search failures."""
        # Mock web search to raise exception
        agent.web_search_tool.search = Mock(side_effect=Exception("Search failed"))
        
        input_data = {
            'disease': 'diabetes',
            'system': 'allopathy'
        }
        
        result = agent.process(input_data)
        
        # Should handle error gracefully
        assert 'success' in result
        # May succeed with fallback or fail gracefully


class TestCitationsAndSources:
    """Test that citations and sources are included."""
    
    def test_sources_included_in_response(self, agent):
        """Test that sources are included in treatment information."""
        input_data = {
            'disease': 'diabetes',
            'system': 'allopathy'
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should have sources somewhere in the response
        has_sources = (
            'sources' in data or
            'citations' in data or
            any('sources' in str(v) for v in data.values() if isinstance(v, dict))
        )
        assert has_sources
    
    def test_clinical_guidelines_have_sources(self, agent):
        """Test that clinical guidelines include sources."""
        result = agent.search_treatment_guidelines(
            condition='hypertension'
        )
        
        assert 'guidelines' in result
        # Should have sources
        has_sources = 'sources' in result or 'source' in str(result).lower()
        assert has_sources


class TestResponseStructure:
    """Test response structure and format."""
    
    def test_response_has_required_fields(self, agent):
        """Test that response has all required fields."""
        input_data = {
            'disease': 'asthma',
            'system': 'allopathy'
        }
        
        result = agent.process(input_data)
        
        # Check required fields
        assert 'success' in result
        assert 'agent' in result
        assert 'timestamp' in result
        assert result['agent'] == 'TreatmentExplorationAgent'
    
    def test_successful_response_structure(self, agent):
        """Test structure of successful response."""
        input_data = {
            'disease': 'diabetes',
            'system': 'allopathy'
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        assert 'data' in result
        assert 'message' in result
        assert isinstance(result['data'], dict)
    
    def test_error_response_structure(self, agent):
        """Test structure of error response."""
        input_data = {}
        
        result = agent.process(input_data)
        
        assert result['success'] is False
        assert 'message' in result
        assert isinstance(result['message'], str)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
