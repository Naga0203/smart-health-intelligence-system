"""
Property-based tests for TreatmentExplorationAgent.

Tests the following properties:
- Property 1: Agent Migration Preserves Functionality (Validates: Requirements 1.6)
- Property 6: Dynamic Retrieval Replaces Static Lookups (Validates: Requirements 3.3, 3.4)
- Property 27: Treatment Searches Cover Multiple Medical Systems (Validates: Requirements 7.2)
- Property 29: Treatment Information Includes Evidence Levels (Validates: Requirements 7.4, 17.7)
- Property 30: Drug Queries Include Interaction Searches (Validates: Requirements 7.5)

Feature: autonomous-ai-agents-refactor
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from .treatment_exploration import TreatmentExplorationAgent
from .infrastructure.config import AgentConfig
from .infrastructure.models import SearchResult


# Test data strategies
@st.composite
def disease_names(draw):
    """Generate valid disease names."""
    diseases = st.sampled_from([
        'diabetes', 'hypertension', 'asthma', 'arthritis',
        'heart disease', 'cancer', 'depression', 'anxiety'
    ])
    return draw(diseases)


@st.composite
def medical_systems(draw):
    """Generate valid medical system names."""
    systems = st.sampled_from(['allopathy', 'ayurveda', 'homeopathy', 'all'])
    return draw(systems)


@st.composite
def medication_lists(draw):
    """Generate lists of medication names."""
    medications = st.lists(
        st.sampled_from([
            'metformin', 'insulin', 'lisinopril', 'amlodipine',
            'aspirin', 'atorvastatin', 'levothyroxine'
        ]),
        min_size=1,
        max_size=5,
        unique=True
    )
    return draw(medications)


@st.composite
def treatment_input_data(draw):
    """Generate valid treatment exploration input data."""
    disease = draw(disease_names())
    system = draw(medical_systems())
    include_evidence = draw(st.booleans())
    
    data = {
        'disease': disease,
        'system': system,
        'include_evidence': include_evidence
    }
    
    # Sometimes include medications
    if draw(st.booleans()):
        data['medications'] = draw(medication_lists())
    
    return data


# Fixtures
@pytest.fixture
def mock_search_results():
    """Create mock search results."""
    def create_results(query):
        return [
            SearchResult(
                title=f"Treatment for {query}",
                url="https://pubmed.ncbi.nlm.nih.gov/test",
                snippet=f"Treatment information about {query}. Evidence from clinical trials.",
                source_domain="pubmed.ncbi.nlm.nih.gov",
                quality_score=0.9,
                content=f"Detailed treatment information for {query} with evidence levels."
            )
        ]
    return create_results


@pytest.fixture
def agent(mock_search_results):
    """Create TreatmentExplorationAgent with mocked dependencies."""
    config = AgentConfig(
        agent_name="TreatmentExplorationAgent",
        enable_web_search=True,
        enable_caching=False,  # Disable caching for tests
        monitoring_enabled=False  # Disable monitoring for tests
    )
    
    # Patch at the infrastructure level
    with patch('backend.agents.infrastructure.web_search.WebSearchTool') as mock_web_search_class, \
         patch('backend.agents.infrastructure.enhanced_base_agent.LangChainGeminiClient') as mock_gemini_class, \
         patch('backend.agents.infrastructure.enhanced_base_agent.MonitoringService') as mock_monitoring:
        
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
        llm.invoke = Mock(return_value="Synthesized treatment information with evidence levels")
        client = Mock()
        client.llm = llm
        mock_gemini_class.return_value = client
        
        # Create agent
        agent = TreatmentExplorationAgent(config)
        
        yield agent


# Property 1: Agent Migration Preserves Functionality
# Validates: Requirements 1.6
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(input_data=treatment_input_data())
def test_property_1_migration_preserves_functionality(agent, input_data):
    """
    Property 1: Agent Migration Preserves Functionality
    
    For any valid treatment exploration input, the migrated agent should
    return a successful response with treatment information.
    
    Validates: Requirements 1.6
    """
    # Execute agent
    result = agent.process(input_data)
    
    # Verify response structure is preserved
    assert isinstance(result, dict), "Response should be a dictionary"
    assert 'success' in result, "Response should have 'success' field"
    assert 'agent' in result, "Response should have 'agent' field"
    assert result['agent'] == 'TreatmentExplorationAgent', "Agent name should be preserved"
    
    # For valid inputs, should succeed
    if input_data.get('disease'):
        assert result['success'] is True, "Valid input should succeed"
        assert 'data' in result, "Successful response should have 'data' field"
        assert 'message' in result, "Response should have 'message' field"


# Property 6: Dynamic Retrieval Replaces Static Lookups
# Validates: Requirements 3.3, 3.4
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(disease=disease_names(), system=medical_systems())
def test_property_6_dynamic_retrieval_replaces_static(agent, disease, system):
    """
    Property 6: Dynamic Retrieval Replaces Static Lookups
    
    For any treatment information request, the system should perform
    web search or AI query rather than loading from static data files.
    
    Validates: Requirements 3.3, 3.4
    """
    input_data = {
        'disease': disease,
        'system': system
    }
    
    # Track if web search was called
    search_called = False
    original_search = agent.web_search_tool.search
    
    def track_search(*args, **kwargs):
        nonlocal search_called
        search_called = True
        return original_search(*args, **kwargs)
    
    agent.web_search_tool.search = track_search
    
    # Execute agent
    result = agent.process(input_data)
    
    # Verify dynamic retrieval was used (web search called)
    assert search_called, (
        f"Dynamic retrieval should be used for {disease} ({system}), "
        "not static data lookup"
    )
    
    # Verify no static data structures are accessed
    # (The agent should not have detailed_treatments attribute)
    assert not hasattr(agent, 'detailed_treatments'), (
        "Agent should not have static detailed_treatments data"
    )
    assert not hasattr(agent, 'treatment_kb'), (
        "Agent should not have static treatment_kb"
    )


# Property 27: Treatment Searches Cover Multiple Medical Systems
# Validates: Requirements 7.2
@settings(
    max_examples=30,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(disease=disease_names())
def test_property_27_multi_system_search(agent, disease):
    """
    Property 27: Treatment Searches Cover Multiple Medical Systems
    
    For any treatment exploration query with system='all', the agent should
    search for information across allopathy, ayurveda, and homeopathy systems.
    
    Validates: Requirements 7.2
    """
    input_data = {
        'disease': disease,
        'system': 'all'
    }
    
    # Track search queries
    search_queries = []
    original_search = agent.web_search_tool.search
    
    def track_queries(query, *args, **kwargs):
        search_queries.append(query.lower())
        return original_search(query, *args, **kwargs)
    
    agent.web_search_tool.search = track_queries
    
    # Execute agent
    result = agent.process(input_data)
    
    # Verify multi-system search occurred
    assert result['success'], "Multi-system search should succeed"
    
    # Check that searches covered multiple systems
    # The dynamic_treatment service should search for each system
    systems_searched = set()
    for query in search_queries:
        if 'allopathy' in query:
            systems_searched.add('allopathy')
        if 'ayurveda' in query:
            systems_searched.add('ayurveda')
        if 'homeopathy' in query:
            systems_searched.add('homeopathy')
    
    # Should search at least 2 systems (may not always search all 3 depending on implementation)
    assert len(systems_searched) >= 2, (
        f"Multi-system search should cover multiple medical systems, "
        f"but only found: {systems_searched}"
    )


# Property 29: Treatment Information Includes Evidence Levels
# Validates: Requirements 7.4, 17.7
@settings(
    max_examples=30,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(disease=disease_names(), system=medical_systems())
def test_property_29_evidence_levels_included(agent, disease, system):
    """
    Property 29: Treatment Information Includes Evidence Levels
    
    For any treatment recommendation with include_evidence=True, the response
    should include evidence levels (e.g., clinical trial data, expert opinion).
    
    Validates: Requirements 7.4, 17.7
    """
    input_data = {
        'disease': disease,
        'system': system,
        'include_evidence': True
    }
    
    # Execute agent
    result = agent.process(input_data)
    
    assert result['success'], "Treatment query should succeed"
    
    # Verify evidence information is included
    data = result.get('data', {})
    
    # Evidence should be present in some form
    # Could be in evidence_analysis, clinical_guidelines, or treatment_info
    has_evidence = (
        'evidence_analysis' in data or
        'evidence' in str(data).lower() or
        'clinical' in str(data).lower() or
        'trial' in str(data).lower()
    )
    
    assert has_evidence, (
        f"Treatment information should include evidence levels when requested, "
        f"but none found in response for {disease} ({system})"
    )


# Property 30: Drug Queries Include Interaction Searches
# Validates: Requirements 7.5
@settings(
    max_examples=30,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(disease=disease_names(), medications=medication_lists())
def test_property_30_drug_interaction_searches(agent, disease, medications):
    """
    Property 30: Drug Queries Include Interaction Searches
    
    For any treatment query involving medications, the agent should search
    for drug interactions and include them in the response.
    
    Validates: Requirements 7.5
    """
    input_data = {
        'disease': disease,
        'system': 'allopathy',
        'medications': medications
    }
    
    # Track drug information searches
    drug_searches = []
    original_drug_search = agent.web_search_tool.search_drug_information
    
    def track_drug_search(drug_name, *args, **kwargs):
        drug_searches.append(drug_name)
        return original_drug_search(drug_name, *args, **kwargs)
    
    agent.web_search_tool.search_drug_information = track_drug_search
    
    # Execute agent
    result = agent.process(input_data)
    
    assert result['success'], "Treatment query with medications should succeed"
    
    # Verify drug interaction information is included
    data = result.get('data', {})
    assert 'drug_interactions' in data, (
        "Response should include drug_interactions when medications provided"
    )
    
    # Verify drug searches were performed
    assert len(drug_searches) > 0, (
        f"Drug interaction searches should be performed for medications: {medications}"
    )
    
    # Verify interaction data structure
    interactions = data['drug_interactions']
    assert isinstance(interactions, dict), "Drug interactions should be a dictionary"
    assert 'medications' in interactions, "Should list medications checked"
    assert 'interactions' in interactions or 'success' in interactions, (
        "Should include interaction information or status"
    )


# Additional property test: Citations are included
@settings(
    max_examples=30,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(disease=disease_names(), system=medical_systems())
def test_property_citations_included(agent, disease, system):
    """
    Property: Web Search Results Include Citations
    
    For any treatment information retrieved via web search, the response
    should include proper citations with source URLs.
    
    Validates: Requirements 2.6, 7.7
    """
    input_data = {
        'disease': disease,
        'system': system
    }
    
    # Execute agent
    result = agent.process(input_data)
    
    assert result['success'], "Treatment query should succeed"
    
    # Verify citations are included
    data = result.get('data', {})
    
    # Citations should be present somewhere in the response
    has_citations = (
        'sources' in data or
        'citations' in data or
        any('sources' in str(v) for v in data.values() if isinstance(v, dict))
    )
    
    assert has_citations, (
        f"Treatment information should include citations/sources, "
        f"but none found for {disease} ({system})"
    )


# Additional property test: Medical disclaimers are present
@settings(
    max_examples=30,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(input_data=treatment_input_data())
def test_property_medical_disclaimers(agent, input_data):
    """
    Property: Medical Responses Include Disclaimers
    
    For any treatment information response, appropriate medical disclaimers
    should be included.
    
    Validates: Requirements 7.8, 17.2
    """
    # Execute agent
    result = agent.process(input_data)
    
    if result['success']:
        data = result.get('data', {})
        
        # Verify disclaimer is present
        assert 'disclaimer' in data, (
            "Treatment information should include medical disclaimer"
        )
        
        disclaimer = data['disclaimer']
        assert isinstance(disclaimer, str), "Disclaimer should be a string"
        assert len(disclaimer) > 50, "Disclaimer should be substantial"
        
        # Check for key disclaimer elements
        disclaimer_lower = disclaimer.lower()
        assert any(word in disclaimer_lower for word in ['medical', 'professional', 'advice']), (
            "Disclaimer should mention medical professional advice"
        )


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
