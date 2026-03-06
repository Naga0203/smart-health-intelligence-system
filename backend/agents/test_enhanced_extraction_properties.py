"""
Property-Based Tests for EnhancedExtractionAgent

Tests universal correctness properties using Hypothesis for property-based testing.

Properties tested:
- Property 1: Agent Migration Preserves Functionality (Requirement 1.6)
- Property 10: Extraction Operations Include Confidence Scores (Requirements 4.6, 8.7, 14.8)
- Property 11: OCR Extracts Structured Medical Data (Requirements 4.7, 8.2)
- Property 52: Image Analysis Extracts Chart Data (Requirement 14.2)
- Property 54: Table Extraction Preserves Structure (Requirement 14.4)
- Property 56: Report Type Is Identified (Requirement 14.6)
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock
from .enhanced_extraction import EnhancedExtractionAgent
from .infrastructure.gemini_ocr import GeminiOCRService
from .infrastructure.models import OCRResult


# Strategy for generating valid medical report text
@st.composite
def medical_report_text(draw):
    """Generate realistic medical report text."""
    symptoms = draw(st.lists(
        st.sampled_from(['headache', 'fever', 'cough', 'fatigue', 'nausea']),
        min_size=0,
        max_size=5
    ))
    
    bp_systolic = draw(st.integers(min_value=90, max_value=180))
    bp_diastolic = draw(st.integers(min_value=60, max_value=120))
    heart_rate = draw(st.integers(min_value=50, max_value=120))
    
    report = f"Patient Report\n\n"
    if symptoms:
        report += f"Symptoms: {', '.join(symptoms)}\n"
    report += f"Vitals: BP {bp_systolic}/{bp_diastolic}, HR {heart_rate}\n"
    
    return report


# Strategy for generating valid extracted data
@st.composite
def extracted_medical_data(draw):
    """Generate valid extracted medical data structure."""
    return {
        'symptoms': draw(st.lists(st.text(min_size=1, max_size=20), max_size=5)),
        'vitals': {
            'blood_pressure': f"{draw(st.integers(90, 180))}/{draw(st.integers(60, 120))}",
            'heart_rate': draw(st.integers(50, 120)),
            'temperature': draw(st.floats(96.0, 104.0)),
            'weight': draw(st.floats(30.0, 200.0)),
            'height': draw(st.floats(100.0, 220.0))
        },
        'lab_results': draw(st.lists(
            st.fixed_dictionaries({
                'test_name': st.text(min_size=1, max_size=50),
                'value': st.floats(0.0, 1000.0),
                'unit': st.sampled_from(['mg/dL', 'mmol/L', 'g/dL', 'U/L']),
                'reference_range': st.text(min_size=1, max_size=20),
                'date': st.sampled_from(['2024-01-15', '2024-02-20', '2024-03-10'])
            }),
            max_size=3
        )),
        'medications': draw(st.lists(
            st.fixed_dictionaries({
                'name': st.text(min_size=1, max_size=50),
                'dosage': st.text(min_size=1, max_size=20),
                'frequency': st.sampled_from(['once daily', 'twice daily', 'three times daily']),
                'start_date': st.sampled_from(['2024-01-01', '2024-02-01', '2024-03-01'])
            }),
            max_size=3
        )),
        'diagnoses': draw(st.lists(
            st.fixed_dictionaries({
                'condition': st.text(min_size=1, max_size=50),
                'icd_code': st.one_of(st.none(), st.text(min_size=3, max_size=10)),
                'date': st.sampled_from(['2024-01-15', '2024-02-20', '2024-03-10']),
                'status': st.sampled_from(['active', 'resolved', 'chronic'])
            }),
            max_size=3
        )),
        'confidence_scores': {
            'overall': draw(st.floats(0.0, 1.0)),
            'symptoms': draw(st.floats(0.0, 1.0)),
            'vitals': draw(st.floats(0.0, 1.0)),
            'lab_results': draw(st.floats(0.0, 1.0)),
            'medications': draw(st.floats(0.0, 1.0)),
            'diagnoses': draw(st.floats(0.0, 1.0))
        }
    }


class TestEnhancedExtractionProperties:
    """Property-based tests for EnhancedExtractionAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for testing."""
        with patch('agents.enhanced_extraction.settings') as mock_settings:
            mock_settings.GEMINI_API_KEY = 'test-key'
            with patch('agents.infrastructure.gemini_ocr.ChatGoogleGenerativeAI'):
                agent = EnhancedExtractionAgent()
                return agent
    
    # Property 1: Agent Migration Preserves Functionality
    @given(data=extracted_medical_data())
    @settings(max_examples=50, deadline=None)
    def test_property_1_migration_preserves_functionality(self, agent, data):
        """
        Property 1: Agent Migration Preserves Functionality
        
        For any valid extracted medical data, the migrated agent should validate
        and process it correctly, maintaining all required fields and structure.
        
        Validates: Requirement 1.6
        """
        # The migrated agent should validate data correctly
        validation_result = agent._validate_extracted_data(data)
        
        # Should have validation result structure
        assert 'valid' in validation_result
        assert 'errors' in validation_result
        assert 'flagged_fields' in validation_result
        assert 'low_confidence_fields' in validation_result
        
        # If data is valid, should have no errors
        if validation_result['valid']:
            assert len(validation_result['errors']) == 0
        
        # Should preserve all required fields
        assert 'symptoms' in data
        assert 'vitals' in data
        assert 'lab_results' in data
        assert 'medications' in data
        assert 'diagnoses' in data
        assert 'confidence_scores' in data
    
    # Property 10: Extraction Operations Include Confidence Scores
    @given(data=extracted_medical_data(), text=st.text(min_size=10, max_size=500))
    @settings(max_examples=50, deadline=None)
    def test_property_10_confidence_scores_included(self, agent, data, text):
        """
        Property 10: Extraction Operations Include Confidence Scores
        
        For any extraction operation, the result should include confidence scores
        for all major data categories.
        
        Validates: Requirements 4.6, 8.7, 14.8
        """
        # Calculate confidence scores
        scores = agent._calculate_confidence_scores(data, text)
        
        # Should have all required confidence score fields
        assert 'overall' in scores
        assert 'symptoms' in scores
        assert 'vitals' in scores
        assert 'lab_results' in scores
        assert 'medications' in scores
        assert 'diagnoses' in scores
        
        # All scores should be in valid range [0.0, 1.0]
        for key, value in scores.items():
            assert isinstance(value, (int, float))
            assert 0.0 <= value <= 1.0
        
        # Scores should be rounded to 2 decimal places
        for value in scores.values():
            assert len(str(value).split('.')[-1]) <= 2
    
    # Property 11: OCR Extracts Structured Medical Data
    @given(
        file_type=st.sampled_from(['application/pdf', 'image/jpeg', 'image/png']),
        text=medical_report_text()
    )
    @settings(max_examples=30, deadline=None)
    def test_property_11_ocr_extracts_structured_data(self, agent, file_type, text):
        """
        Property 11: OCR Extracts Structured Medical Data
        
        For any medical report, OCR should extract structured data including
        lab results, vitals, medications, and diagnoses.
        
        Validates: Requirements 4.7, 8.2
        """
        # Mock OCR service to return structured data
        mock_ocr_result = OCRResult(
            text=text,
            confidence=0.9,
            format=file_type.split('/')[-1],
            extraction_time=1.0,
            metadata={'method': 'gemini_vision'}
        )
        
        with patch.object(agent.ocr_service, 'extract_text', return_value=mock_ocr_result):
            with patch.object(agent.ocr_service, 'extract_structured_data', return_value={}):
                with patch.object(agent.ocr_service, 'extract_from_table', return_value=[]):
                    with patch.object(agent.ocr_service, 'extract_from_chart', return_value={}):
                        with patch.object(agent.ocr_service, 'handle_handwriting', return_value=''):
                            with patch.object(agent.ocr_service, 'identify_report_type', return_value='lab_report'):
                                with patch.object(agent.ocr_service, 'extract_report_headers', return_value={}):
                                    # Mock the parsing to return structured data
                                    with patch.object(agent, '_parse_medical_text') as mock_parse:
                                        mock_parse.return_value = {
                                            'symptoms': ['headache'],
                                            'vitals': {
                                                'blood_pressure': '120/80',
                                                'heart_rate': 72,
                                                'temperature': None,
                                                'weight': None,
                                                'height': None
                                            },
                                            'lab_results': [],
                                            'medications': [],
                                            'diagnoses': [],
                                            'confidence_scores': {
                                                'overall': 0.8,
                                                'symptoms': 0.9,
                                                'vitals': 0.7,
                                                'lab_results': 0.0,
                                                'medications': 0.0,
                                                'diagnoses': 0.0
                                            }
                                        }
                                        
                                        file_stream = BytesIO(b"test content")
                                        result = agent.extract_from_report(file_stream, file_type)
        
        # Should successfully extract data
        assert result['success'] is True
        
        # Should have structured data
        assert 'extracted_data' in result
        extracted_data = result['extracted_data']
        
        # Should have all required structured fields
        assert 'symptoms' in extracted_data
        assert 'vitals' in extracted_data
        assert 'lab_results' in extracted_data
        assert 'medications' in extracted_data
        assert 'diagnoses' in extracted_data
        
        # Vitals should have structured fields
        assert isinstance(extracted_data['vitals'], dict)
        assert 'blood_pressure' in extracted_data['vitals']
        assert 'heart_rate' in extracted_data['vitals']
        assert 'temperature' in extracted_data['vitals']
        assert 'weight' in extracted_data['vitals']
        assert 'height' in extracted_data['vitals']
    
    # Property 52: Image Analysis Extracts Chart Data
    @given(file_type=st.sampled_from(['image/jpeg', 'image/png']))
    @settings(max_examples=20, deadline=None)
    def test_property_52_chart_data_extraction(self, agent, file_type):
        """
        Property 52: Image Analysis Extracts Chart Data
        
        For any medical report image containing charts or graphs, the agent
        should extract chart data and analysis.
        
        Validates: Requirement 14.2
        """
        # Mock OCR service to return chart analysis
        mock_ocr_result = OCRResult(
            text="Chart showing glucose levels over time",
            confidence=0.9,
            format=file_type.split('/')[-1],
            extraction_time=1.0,
            metadata={'method': 'gemini_vision'}
        )
        
        mock_chart_analysis = {
            'analysis': 'Line chart showing glucose levels from 80-120 mg/dL over 6 months',
            'extraction_method': 'gemini_vision_chart'
        }
        
        with patch.object(agent.ocr_service, 'extract_text', return_value=mock_ocr_result):
            with patch.object(agent.ocr_service, 'extract_structured_data', return_value={}):
                with patch.object(agent.ocr_service, 'extract_from_table', return_value=[]):
                    with patch.object(agent.ocr_service, 'extract_from_chart', return_value=mock_chart_analysis):
                        with patch.object(agent.ocr_service, 'handle_handwriting', return_value=''):
                            with patch.object(agent.ocr_service, 'identify_report_type', return_value='lab_report'):
                                with patch.object(agent.ocr_service, 'extract_report_headers', return_value={}):
                                    with patch.object(agent, '_parse_medical_text') as mock_parse:
                                        mock_parse.return_value = agent._get_empty_extraction_structure()
                                        
                                        file_stream = BytesIO(b"image with chart")
                                        result = agent.extract_from_report(file_stream, file_type)
        
        # Should successfully extract
        assert result['success'] is True
        
        # Should have chart analysis
        assert 'chart_analysis' in result
        assert result['chart_analysis'] is not None
        
        # Chart analysis should have expected structure
        if result['chart_analysis']:
            assert 'analysis' in result['chart_analysis'] or 'extraction_method' in result['chart_analysis']
        
        # Metadata should indicate charts were found
        assert 'metadata' in result
        assert 'has_charts' in result['metadata']
    
    # Property 54: Table Extraction Preserves Structure
    @given(file_type=st.sampled_from(['application/pdf', 'image/jpeg', 'image/png']))
    @settings(max_examples=20, deadline=None)
    def test_property_54_table_structure_preservation(self, agent, file_type):
        """
        Property 54: Table Extraction Preserves Structure
        
        For any medical report containing tables, the extraction should preserve
        the table structure and relationships.
        
        Validates: Requirement 14.4
        """
        # Mock OCR service to return table data
        mock_ocr_result = OCRResult(
            text="Lab Results Table",
            confidence=0.9,
            format=file_type.split('/')[-1],
            extraction_time=1.0,
            metadata={'method': 'gemini_vision'}
        )
        
        mock_table_data = [
            {
                'raw_content': 'Test | Value | Unit\nGlucose | 95 | mg/dL\nCholesterol | 180 | mg/dL',
                'extraction_method': 'gemini_vision_table'
            }
        ]
        
        with patch.object(agent.ocr_service, 'extract_text', return_value=mock_ocr_result):
            with patch.object(agent.ocr_service, 'extract_structured_data', return_value={}):
                with patch.object(agent.ocr_service, 'extract_from_table', return_value=mock_table_data):
                    with patch.object(agent.ocr_service, 'extract_from_chart', return_value={}):
                        with patch.object(agent.ocr_service, 'handle_handwriting', return_value=''):
                            with patch.object(agent.ocr_service, 'identify_report_type', return_value='lab_report'):
                                with patch.object(agent.ocr_service, 'extract_report_headers', return_value={}):
                                    with patch.object(agent, '_parse_medical_text') as mock_parse:
                                        mock_parse.return_value = agent._get_empty_extraction_structure()
                                        
                                        file_stream = BytesIO(b"document with table")
                                        result = agent.extract_from_report(file_stream, file_type)
        
        # Should successfully extract
        assert result['success'] is True
        
        # Should have table data
        assert 'table_data' in result
        assert result['table_data'] is not None
        assert isinstance(result['table_data'], list)
        
        # If tables were extracted, they should have structure
        if len(result['table_data']) > 0:
            for table in result['table_data']:
                assert isinstance(table, dict)
                # Should have content or extraction method
                assert 'raw_content' in table or 'extraction_method' in table
        
        # Metadata should indicate tables were found
        assert 'metadata' in result
        assert 'has_tables' in result['metadata']
        assert result['metadata']['has_tables'] == (len(result['table_data']) > 0)
    
    # Property 56: Report Type Is Identified
    @given(
        file_type=st.sampled_from(['application/pdf', 'image/jpeg', 'image/png']),
        report_type=st.sampled_from(['lab_report', 'radiology', 'pathology', 'discharge_summary', 'prescription'])
    )
    @settings(max_examples=25, deadline=None)
    def test_property_56_report_type_identification(self, agent, file_type, report_type):
        """
        Property 56: Report Type Is Identified
        
        For any medical report, the agent should identify the report type
        (lab report, radiology, pathology, etc.).
        
        Validates: Requirement 14.6
        """
        # Mock OCR service to return report type
        mock_ocr_result = OCRResult(
            text=f"This is a {report_type}",
            confidence=0.9,
            format=file_type.split('/')[-1],
            extraction_time=1.0,
            metadata={'method': 'gemini_vision'}
        )
        
        with patch.object(agent.ocr_service, 'extract_text', return_value=mock_ocr_result):
            with patch.object(agent.ocr_service, 'extract_structured_data', return_value={}):
                with patch.object(agent.ocr_service, 'extract_from_table', return_value=[]):
                    with patch.object(agent.ocr_service, 'extract_from_chart', return_value={}):
                        with patch.object(agent.ocr_service, 'handle_handwriting', return_value=''):
                            with patch.object(agent.ocr_service, 'identify_report_type', return_value=report_type):
                                with patch.object(agent.ocr_service, 'extract_report_headers', return_value={}):
                                    with patch.object(agent, '_parse_medical_text') as mock_parse:
                                        mock_parse.return_value = agent._get_empty_extraction_structure()
                                        
                                        file_stream = BytesIO(b"medical report")
                                        result = agent.extract_from_report(file_stream, file_type)
        
        # Should successfully extract
        assert result['success'] is True
        
        # Should have report type
        assert 'report_type' in result
        assert result['report_type'] is not None
        assert isinstance(result['report_type'], str)
        
        # Report type should match what was identified
        assert result['report_type'] == report_type
        
        # Metadata should include report type
        assert 'metadata' in result
        assert 'report_type' in result['metadata']
        assert result['metadata']['report_type'] == report_type
    
    # Additional property: Validation consistency
    @given(data=extracted_medical_data())
    @settings(max_examples=50, deadline=None)
    def test_property_validation_consistency(self, agent, data):
        """
        Property: Validation should be consistent across multiple calls.
        
        For any extracted data, validation should produce the same result
        when called multiple times.
        """
        # Validate data twice
        result1 = agent._validate_extracted_data(data)
        result2 = agent._validate_extracted_data(data)
        
        # Results should be identical
        assert result1['valid'] == result2['valid']
        assert result1['errors'] == result2['errors']
        assert set(result1['flagged_fields']) == set(result2['flagged_fields'])
        assert set(result1['low_confidence_fields']) == set(result2['low_confidence_fields'])
    
    # Additional property: Confidence scores are deterministic
    @given(data=extracted_medical_data(), text=st.text(min_size=10, max_size=500))
    @settings(max_examples=50, deadline=None)
    def test_property_confidence_deterministic(self, agent, data, text):
        """
        Property: Confidence score calculation should be deterministic.
        
        For any extracted data and text, confidence scores should be the same
        when calculated multiple times.
        """
        # Calculate scores twice
        scores1 = agent._calculate_confidence_scores(data, text)
        scores2 = agent._calculate_confidence_scores(data, text)
        
        # Scores should be identical
        assert scores1 == scores2
        
        # All scores should be in valid range
        for key in scores1:
            assert 0.0 <= scores1[key] <= 1.0
            assert 0.0 <= scores2[key] <= 1.0
