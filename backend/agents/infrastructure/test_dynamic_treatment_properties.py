"""
Property-based tests for DynamicTreatmentRetrieval.

These tests validate Property 6: Dynamic Retrieval Replaces Static Lookups
Validates: Requirements 3.3, 3.4

Property 6 states: For any treatment or disease information request,
the system should perform a web search or AI query rather than loading
from static data files.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

from agents.infrastructure.dynamic_treatment import DynamicTreatmentRetrieval
from agents.infrastructure.web_search import WebSearchTool, SearchResult
from agents.infrastructure.config import SearchConfig


# Strategy for generating disease names
disease_names = st.sampled_from([
    'diabetes', 'heart_disease', 'hypertension', 'asthma',
    'arthritis', 'cancer', 'alzheimers', 'parkinsons'
])

# Strategy for generating medical system names
medical_systems = st.sampled_from([
    'allopathy', 'ayurveda', 'homeopathy', 'lifestyle', 'traditional'
])

# Strategy for generating medication lists
medication_lists = st.lists(
    st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('L',))),
    min_size=1,
    max_size=5
)


class TestDynamicRetrievalProperty:
    """Property-based tests for dynamic treatment retrieval."""
    
    @given(disease=disease_names, medical_system=medical_systems)
    @settings(max_examples=20, deadline=None)
    def test_property_6_no_static_data_access(self, disease, medical_system):
        """
        Property 6: Dynamic Retrieval Replaces Static Lookups
        
        For any disease and medical system combination, the system should:
        1. NOT access any static data files
        2. Perform web search or AI query
        3. Return dynamically retrieved information
        
        This test verifies that no file I/O operations occur during retrieval.
        """
        # Create mock web search tool
        mock_web_search = Mock(spec=WebSearchTool)
        mock_web_search.search_medical_literature.return_value = [
            SearchResult(
                title=f"Treatment for {disease}",
                url=f"https://pubmed.ncbi.nlm.nih.gov/{disease}",
                snippet=f"Current treatment approaches for {disease}",
                source_domain="pubmed.ncbi.nlm.nih.gov",
                quality_score=0.95,
                publication_date=None,
                content=f"Detailed treatment information for {disease} in {medical_system}",
                metadata={}
            )
        ]
        
        # Create mock LLM
        mock_llm = Mock()
        mock_llm.invoke.return_value = Mock(
            content=f"Treatment information for {disease} using {medical_system}"
        )
        
        # Create DynamicTreatmentRetrieval instance
        retrieval = DynamicTreatmentRetrieval(
            web_search=mock_web_search,
            llm=mock_llm
        )
        
        # Patch file operations to detect any static data access
        with patch('builtins.open', side_effect=AssertionError("Static file access detected!")):
            with patch('pathlib.Path.read_text', side_effect=AssertionError("Static file read detected!")):
                with patch('json.load', side_effect=AssertionError("JSON file load detected!")):
                    # Perform treatment information retrieval
                    result = retrieval.get_treatment_info(disease, medical_system)
                    
                    # Verify web search was called (dynamic retrieval)
                    assert mock_web_search.search_medical_literature.called, \
                        "Web search should be called for dynamic retrieval"
                    
                    # Verify result is not None
                    assert result is not None, \
                        "Dynamic retrieval should return information"
    
    @given(disease=disease_names)
    @settings(max_examples=20, deadline=None)
    def test_property_6_web_search_invoked(self, disease):
        """
        Property 6: Dynamic Retrieval Replaces Static Lookups
        
        For any disease query, verify that web search is invoked
        rather than loading from static sources.
        """
        # Create mock web search tool
        mock_web_search = Mock(spec=WebSearchTool)
        mock_web_search.search_clinical_guidelines.return_value = [
            SearchResult(
                title=f"Clinical guidelines for {disease}",
                url="https://www.who.int/guidelines",
                snippet="Current clinical guidelines",
                source_domain="who.int",
                quality_score=0.98,
                publication_date=None,
                content="Detailed guidelines",
                metadata={}
            )
        ]
        
        mock_llm = Mock()
        mock_llm.invoke.return_value = Mock(content="Clinical guidelines information")
        
        retrieval = DynamicTreatmentRetrieval(
            web_search=mock_web_search,
            llm=mock_llm
        )
        
        # Get clinical guidelines
        result = retrieval.get_clinical_guidelines(disease)
        
        # Verify web search was invoked
        assert mock_web_search.search_clinical_guidelines.called, \
            "Web search should be invoked for clinical guidelines"
        
        # Verify the disease was passed to search
        call_args = mock_web_search.search_clinical_guidelines.call_args
        assert disease in str(call_args), \
            f"Disease '{disease}' should be included in search query"
    
    @given(medications=medication_lists)
    @settings(max_examples=20, deadline=None)
    def test_property_6_drug_interactions_dynamic(self, medications):
        """
        Property 6: Dynamic Retrieval Replaces Static Lookups
        
        For any list of medications, verify that drug interaction
        information is retrieved dynamically, not from static data.
        """
        assume(len(medications) > 0)
        
        # Create mock web search tool
        mock_web_search = Mock(spec=WebSearchTool)
        mock_web_search.search_drug_information.return_value = {
            'interactions': [],
            'warnings': [],
            'sources': ['https://www.drugs.com']
        }
        
        mock_llm = Mock()
        mock_llm.invoke.return_value = Mock(content="No significant interactions found")
        
        retrieval = DynamicTreatmentRetrieval(
            web_search=mock_web_search,
            llm=mock_llm
        )
        
        # Patch file operations to ensure no static data access
        with patch('builtins.open', side_effect=AssertionError("Static file access detected!")):
            # Get drug interactions
            result = retrieval.get_drug_interactions(medications)
            
            # Verify web search was called for each medication
            assert mock_web_search.search_drug_information.called, \
                "Web search should be called for drug interactions"
            
            # Verify result is not None
            assert result is not None, \
                "Dynamic retrieval should return interaction information"
    
    @given(disease=disease_names, medical_system=medical_systems)
    @settings(max_examples=20, deadline=None)
    def test_property_6_synthesis_uses_ai(self, disease, medical_system):
        """
        Property 6: Dynamic Retrieval Replaces Static Lookups
        
        Verify that information synthesis uses AI/LLM rather than
        static templates or hardcoded responses.
        """
        # Create mock search results
        search_results = [
            SearchResult(
                title=f"Source 1 for {disease}",
                url="https://pubmed.ncbi.nlm.nih.gov/1",
                snippet="Information from source 1",
                source_domain="pubmed.ncbi.nlm.nih.gov",
                quality_score=0.9,
                publication_date=None,
                content="Detailed content from source 1",
                metadata={}
            ),
            SearchResult(
                title=f"Source 2 for {disease}",
                url="https://www.who.int/2",
                snippet="Information from source 2",
                source_domain="who.int",
                quality_score=0.95,
                publication_date=None,
                content="Detailed content from source 2",
                metadata={}
            )
        ]
        
        mock_web_search = Mock(spec=WebSearchTool)
        mock_llm = Mock()
        mock_llm.invoke.return_value = Mock(
            content=f"Synthesized treatment information for {disease}"
        )
        
        retrieval = DynamicTreatmentRetrieval(
            web_search=mock_web_search,
            llm=mock_llm
        )
        
        # Synthesize information
        result = retrieval.synthesize_treatment_info(search_results)
        
        # Verify LLM was invoked for synthesis
        assert mock_llm.invoke.called, \
            "LLM should be invoked for information synthesis"
        
        # Verify result contains synthesized content
        assert result is not None, \
            "Synthesis should return information"
        
        # Verify the synthesis is not just concatenation of sources
        # (AI synthesis should transform and integrate information)
        if isinstance(result, dict) and 'synthesized_info' in result:
            assert len(result['synthesized_info']) > 0, \
                "Synthesized information should not be empty"


class TestNoStaticDataInvariants:
    """Test invariants that ensure no static data is used."""
    
    def test_no_static_data_files_in_module(self):
        """Verify no static data files are bundled with the module."""
        import agents.infrastructure.dynamic_treatment as dt_module
        from pathlib import Path
        
        module_dir = Path(dt_module.__file__).parent
        
        # Check for JSON files
        json_files = list(module_dir.glob('*.json'))
        treatment_json = [f for f in json_files if 'treatment' in f.name.lower()]
        
        assert len(treatment_json) == 0, \
            f"Found static treatment JSON files: {treatment_json}"
        
        # Check for CSV files
        csv_files = list(module_dir.glob('*.csv'))
        treatment_csv = [f for f in csv_files if any(
            keyword in f.name.lower() 
            for keyword in ['treatment', 'disease', 'medical']
        )]
        
        assert len(treatment_csv) == 0, \
            f"Found static treatment CSV files: {treatment_csv}"
    
    def test_dynamic_treatment_has_no_hardcoded_data(self):
        """Verify DynamicTreatmentRetrieval class has no hardcoded treatment data."""
        from agents.infrastructure.dynamic_treatment import DynamicTreatmentRetrieval
        import inspect
        
        # Get source code of the class
        source = inspect.getsource(DynamicTreatmentRetrieval)
        
        # Check for suspicious patterns indicating hardcoded data
        suspicious_patterns = [
            '"allopathy": {',
            '"ayurveda": {',
            '"homeopathy": {',
            'common_approaches = [',
            'lifestyle_recommendations = [',
        ]
        
        for pattern in suspicious_patterns:
            assert pattern not in source, \
                f"Found hardcoded treatment data pattern: {pattern}"
    
    @given(disease=disease_names)
    @settings(max_examples=10, deadline=None)
    def test_retrieval_always_calls_external_service(self, disease):
        """
        Verify that every retrieval operation calls an external service
        (web search or LLM), never returns cached static data.
        """
        call_count = {'web_search': 0, 'llm': 0}
        
        def track_web_search(*args, **kwargs):
            call_count['web_search'] += 1
            return [SearchResult(
                title="Test", url="https://test.com", snippet="Test",
                source_domain="test.com", quality_score=0.9,
                publication_date=None, content="Test content", metadata={}
            )]
        
        def track_llm(*args, **kwargs):
            call_count['llm'] += 1
            return Mock(content="Test response")
        
        mock_web_search = Mock(spec=WebSearchTool)
        mock_web_search.search_medical_literature.side_effect = track_web_search
        
        mock_llm = Mock()
        mock_llm.invoke.side_effect = track_llm
        
        retrieval = DynamicTreatmentRetrieval(
            web_search=mock_web_search,
            llm=mock_llm
        )
        
        # Perform retrieval
        retrieval.get_treatment_info(disease, 'allopathy')
        
        # Verify at least one external service was called
        total_calls = call_count['web_search'] + call_count['llm']
        assert total_calls > 0, \
            "At least one external service (web search or LLM) must be called"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
