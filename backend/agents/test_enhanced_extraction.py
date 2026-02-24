"""
Unit tests for EnhancedExtractionAgent

Tests the enhanced extraction agent's ability to process medical reports
and extract structured data.
"""

import pytest
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock
from .enhanced_extraction import EnhancedExtractionAgent


class TestEnhancedExtractionAgent:
    """Test suite for EnhancedExtractionAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for testing."""
        with patch('agents.enhanced_extraction.ChatGoogleGenerativeAI'):
            agent = EnhancedExtractionAgent()
            return agent
    
    def test_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.agent_name == "EnhancedExtractionAgent"
        assert agent.extraction_prompt_template is not None
        assert agent.medical_term_mappings is not None
        assert 'bp' in agent.medical_term_mappings
        assert agent.medical_term_mappings['bp'] == 'blood_pressure'
    
    def test_empty_extraction_structure(self, agent):
        """Test empty extraction structure has all required fields."""
        empty_structure = agent._get_empty_extraction_structure()
        
        assert 'symptoms' in empty_structure
        assert 'vitals' in empty_structure
        assert 'lab_results' in empty_structure
        assert 'medications' in empty_structure
        assert 'diagnoses' in empty_structure
        assert 'confidence_scores' in empty_structure
        
        # Check vitals structure
        assert 'blood_pressure' in empty_structure['vitals']
        assert 'heart_rate' in empty_structure['vitals']
        assert 'temperature' in empty_structure['vitals']
        assert 'weight' in empty_structure['vitals']
        assert 'height' in empty_structure['vitals']
    
    def test_validate_extracted_data_valid(self, agent):
        """Test validation passes for valid data."""
        valid_data = {
            'symptoms': ['headache', 'fever'],
            'vitals': {
                'blood_pressure': '120/80',
                'heart_rate': 72,
                'temperature': 98.6,
                'weight': 70.0,
                'height': 175.0
            },
            'lab_results': [],
            'medications': [],
            'diagnoses': [],
            'confidence_scores': {
                'overall': 0.8,
                'symptoms': 0.9,
                'vitals': 0.8,
                'lab_results': 0.0,
                'medications': 0.0,
                'diagnoses': 0.0
            }
        }
        
        result = agent._validate_extracted_data(valid_data)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
        assert 'flagged_fields' in result
        assert 'low_confidence_fields' in result
    
    def test_validate_extracted_data_missing_fields(self, agent):
        """Test validation fails for missing required fields."""
        invalid_data = {
            'symptoms': ['headache']
            # Missing other required fields
        }
        
        result = agent._validate_extracted_data(invalid_data)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert any('Missing required field' in error for error in result['errors'])
    
    def test_validate_extracted_data_invalid_types(self, agent):
        """Test validation fails for invalid data types."""
        invalid_data = {
            'symptoms': 'not a list',  # Should be list
            'vitals': {
                'blood_pressure': '120/80',
                'heart_rate': 72,
                'temperature': 98.6,
                'weight': 70.0,
                'height': 175.0
            },
            'lab_results': [],
            'medications': [],
            'diagnoses': [],
            'confidence_scores': {
                'overall': 0.8,
                'symptoms': 0.9,
                'vitals': 0.8,
                'lab_results': 0.0,
                'medications': 0.0,
                'diagnoses': 0.0
            }
        }
        
        result = agent._validate_extracted_data(invalid_data)
        
        assert result['valid'] is False
        assert any('must be a list' in error for error in result['errors'])
    
    def test_validate_extracted_data_invalid_confidence_scores(self, agent):
        """Test validation fails for invalid confidence scores."""
        invalid_data = {
            'symptoms': [],
            'vitals': {
                'blood_pressure': None,
                'heart_rate': None,
                'temperature': None,
                'weight': None,
                'height': None
            },
            'lab_results': [],
            'medications': [],
            'diagnoses': [],
            'confidence_scores': {
                'overall': 1.5,  # Invalid: > 1.0
                'symptoms': -0.1,  # Invalid: < 0.0
                'vitals': 0.8,
                'lab_results': 0.0,
                'medications': 0.0,
                'diagnoses': 0.0
            }
        }
        
        result = agent._validate_extracted_data(invalid_data)
        
        assert result['valid'] is False
        assert any('Invalid confidence score' in error for error in result['errors'])
    
    def test_calculate_confidence_scores_with_existing_scores(self, agent):
        """Test confidence calculation uses existing scores if available."""
        data = {
            'symptoms': ['headache'],
            'vitals': {'blood_pressure': '120/80'},
            'lab_results': [],
            'medications': [],
            'diagnoses': [],
            'confidence_scores': {
                'overall': 0.85,
                'symptoms': 0.9,
                'vitals': 0.8,
                'lab_results': 0.0,
                'medications': 0.0,
                'diagnoses': 0.0
            }
        }
        
        scores = agent._calculate_confidence_scores(data, "sample text")
        
        assert scores['overall'] == 0.85
        assert scores['symptoms'] == 0.9
        assert scores['vitals'] == 0.8
    
    def test_calculate_confidence_scores_without_existing_scores(self, agent):
        """Test confidence calculation generates scores based on data completeness."""
        data = {
            'symptoms': ['headache', 'fever'],
            'vitals': {
                'blood_pressure': '120/80',
                'heart_rate': 72,
                'temperature': None,
                'weight': None,
                'height': None
            },
            'lab_results': [{'test_name': 'Glucose', 'value': 95}],
            'medications': [],
            'diagnoses': []
        }
        
        scores = agent._calculate_confidence_scores(data, "sample text")
        
        assert 'overall' in scores
        assert 'symptoms' in scores
        assert 'vitals' in scores
        assert 'lab_results' in scores
        assert 'medications' in scores
        assert 'diagnoses' in scores
        
        # Symptoms should have confidence since data exists
        assert scores['symptoms'] > 0
        
        # Vitals should have partial confidence (2 out of 5 fields)
        assert 0 < scores['vitals'] < 1
        
        # Lab results should have confidence
        assert scores['lab_results'] > 0
        
        # Medications and diagnoses should have no confidence
        assert scores['medications'] == 0
        assert scores['diagnoses'] == 0
    
    @patch('agents.enhanced_extraction.ChatGoogleGenerativeAI')
    def test_extract_from_report_unsupported_file_type(self, mock_gemini):
        """Test extraction fails gracefully for unsupported file types."""
        agent = EnhancedExtractionAgent()
        
        file_stream = BytesIO(b"test content")
        result = agent.extract_from_report(file_stream, 'application/msword')
        
        assert result['success'] is False
        assert 'error_code' in result
        assert result['extracted_data'] is None
    
    @patch('agents.enhanced_extraction.ChatGoogleGenerativeAI')
    def test_extract_from_report_no_text_extracted(self, mock_gemini):
        """Test extraction handles case when no text is extracted."""
        # Mock Gemini client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = ""  # Empty text
        mock_client.invoke.return_value = mock_response
        
        agent = EnhancedExtractionAgent()
        agent.gemini_vision_client = mock_client
        
        file_stream = BytesIO(b"test content")
        result = agent.extract_from_report(file_stream, 'application/pdf')
        
        assert result['success'] is False
        assert result['error_code'] == 'no_text_extracted'
        assert 'metadata' in result
        assert result['metadata']['ocr_used'] is False
    
    @patch('agents.enhanced_extraction.ChatGoogleGenerativeAI')
    def test_extract_from_report_success_pdf(self, mock_gemini):
        """Test successful extraction from PDF."""
        # Mock Gemini client
        mock_client = MagicMock()
        
        # Mock text extraction response
        text_response = MagicMock()
        text_response.content = "Patient has headache and fever. BP: 120/80, HR: 72"
        
        # Mock structured data extraction response
        structured_response = MagicMock()
        structured_response.content = """{
            "symptoms": ["headache", "fever"],
            "vitals": {
                "blood_pressure": "120/80",
                "heart_rate": 72,
                "temperature": null,
                "weight": null,
                "height": null
            },
            "lab_results": [],
            "medications": [],
            "diagnoses": [],
            "confidence_scores": {
                "overall": 0.8,
                "symptoms": 0.9,
                "vitals": 0.8,
                "lab_results": 0.0,
                "medications": 0.0,
                "diagnoses": 0.0
            }
        }"""
        
        mock_client.invoke.side_effect = [text_response, structured_response]
        
        agent = EnhancedExtractionAgent()
        agent.gemini_vision_client = mock_client
        
        file_stream = BytesIO(b"PDF content")
        result = agent.extract_from_report(file_stream, 'application/pdf')
        
        assert result['success'] is True
        assert result['extracted_data'] is not None
        assert 'symptoms' in result['extracted_data']
        assert 'headache' in result['extracted_data']['symptoms']
        assert result['confidence_scores'] is not None
        assert result['metadata']['ocr_used'] is False
    
    @patch('agents.enhanced_extraction.ChatGoogleGenerativeAI')
    def test_extract_from_report_success_image(self, mock_gemini):
        """Test successful extraction from image with OCR."""
        # Mock Gemini client
        mock_client = MagicMock()
        
        # Mock OCR text extraction response
        text_response = MagicMock()
        text_response.content = "Lab Results: Glucose 95 mg/dL"
        
        # Mock structured data extraction response
        structured_response = MagicMock()
        structured_response.content = """{
            "symptoms": [],
            "vitals": {
                "blood_pressure": null,
                "heart_rate": null,
                "temperature": null,
                "weight": null,
                "height": null
            },
            "lab_results": [
                {
                    "test_name": "Glucose",
                    "value": 95.0,
                    "unit": "mg/dL",
                    "reference_range": "70-100",
                    "date": "2024-01-15"
                }
            ],
            "medications": [],
            "diagnoses": [],
            "confidence_scores": {
                "overall": 0.85,
                "symptoms": 0.0,
                "vitals": 0.0,
                "lab_results": 0.85,
                "medications": 0.0,
                "diagnoses": 0.0
            }
        }"""
        
        mock_client.invoke.side_effect = [text_response, structured_response]
        
        agent = EnhancedExtractionAgent()
        agent.gemini_vision_client = mock_client
        
        file_stream = BytesIO(b"Image content")
        result = agent.extract_from_report(file_stream, 'image/jpeg')
        
        assert result['success'] is True
        assert result['extracted_data'] is not None
        assert 'lab_results' in result['extracted_data']
        assert len(result['extracted_data']['lab_results']) > 0
        assert result['metadata']['ocr_used'] is True

    def test_validate_vital_field_blood_pressure_valid(self, agent):
        """Test blood pressure validation with valid values."""
        error = agent._validate_vital_field('blood_pressure', '120/80')
        assert error is None
        
        error = agent._validate_vital_field('blood_pressure', '140/90')
        assert error is None
    
    def test_validate_vital_field_blood_pressure_invalid(self, agent):
        """Test blood pressure validation with invalid values."""
        # Invalid format
        error = agent._validate_vital_field('blood_pressure', '120')
        assert error is not None
        assert 'format' in error.lower()
        
        # Out of range
        error = agent._validate_vital_field('blood_pressure', '300/200')
        assert error is not None
        assert 'out of range' in error.lower()
        
        # Wrong type
        error = agent._validate_vital_field('blood_pressure', 120)
        assert error is not None
        assert 'must be a string' in error.lower()
    
    def test_validate_vital_field_heart_rate_valid(self, agent):
        """Test heart rate validation with valid values."""
        error = agent._validate_vital_field('heart_rate', 72)
        assert error is None
        
        error = agent._validate_vital_field('heart_rate', 100)
        assert error is None
    
    def test_validate_vital_field_heart_rate_invalid(self, agent):
        """Test heart rate validation with invalid values."""
        # Out of range
        error = agent._validate_vital_field('heart_rate', 300)
        assert error is not None
        assert 'out of range' in error.lower()
        
        # Wrong type
        error = agent._validate_vital_field('heart_rate', '72')
        assert error is not None
        assert 'must be a number' in error.lower()
    
    def test_validate_vital_field_temperature_valid(self, agent):
        """Test temperature validation with valid values."""
        error = agent._validate_vital_field('temperature', 98.6)
        assert error is None
        
        error = agent._validate_vital_field('temperature', 100.5)
        assert error is None
    
    def test_validate_vital_field_temperature_invalid(self, agent):
        """Test temperature validation with invalid values."""
        # Out of range
        error = agent._validate_vital_field('temperature', 120.0)
        assert error is not None
        assert 'out of range' in error.lower()
    
    def test_validate_lab_result_valid(self, agent):
        """Test lab result validation with valid data."""
        valid_lab_result = {
            'test_name': 'Glucose',
            'value': 95.0,
            'unit': 'mg/dL',
            'reference_range': '70-100',
            'date': '2024-01-15'
        }
        
        errors = agent._validate_lab_result(valid_lab_result, 0)
        assert len(errors) == 0
    
    def test_validate_lab_result_missing_fields(self, agent):
        """Test lab result validation with missing fields."""
        invalid_lab_result = {
            'test_name': 'Glucose',
            'value': 95.0
            # Missing unit, reference_range, date
        }
        
        errors = agent._validate_lab_result(invalid_lab_result, 0)
        assert len(errors) > 0
        assert any('missing required field' in error.lower() for error in errors)
    
    def test_validate_lab_result_invalid_types(self, agent):
        """Test lab result validation with invalid types."""
        invalid_lab_result = {
            'test_name': 'Glucose',
            'value': 'not a number',  # Should be number
            'unit': 'mg/dL',
            'reference_range': '70-100',
            'date': '2024-01-15'
        }
        
        errors = agent._validate_lab_result(invalid_lab_result, 0)
        assert len(errors) > 0
        assert any('must be a number' in error.lower() for error in errors)
    
    def test_validate_medication_valid(self, agent):
        """Test medication validation with valid data."""
        valid_medication = {
            'name': 'Metformin',
            'dosage': '500mg',
            'frequency': 'twice daily',
            'start_date': '2024-01-10'
        }
        
        errors = agent._validate_medication(valid_medication, 0)
        assert len(errors) == 0
    
    def test_validate_medication_missing_fields(self, agent):
        """Test medication validation with missing fields."""
        invalid_medication = {
            'name': 'Metformin',
            'dosage': '500mg'
            # Missing frequency, start_date
        }
        
        errors = agent._validate_medication(invalid_medication, 0)
        assert len(errors) > 0
        assert any('missing required field' in error.lower() for error in errors)
    
    def test_validate_diagnosis_valid(self, agent):
        """Test diagnosis validation with valid data."""
        valid_diagnosis = {
            'condition': 'Type 2 Diabetes',
            'icd_code': 'E11.9',
            'date': '2024-01-15',
            'status': 'active'
        }
        
        errors = agent._validate_diagnosis(valid_diagnosis, 0)
        assert len(errors) == 0
    
    def test_validate_diagnosis_invalid_status(self, agent):
        """Test diagnosis validation with invalid status."""
        invalid_diagnosis = {
            'condition': 'Type 2 Diabetes',
            'icd_code': 'E11.9',
            'date': '2024-01-15',
            'status': 'invalid_status'  # Should be 'active', 'resolved', or 'chronic'
        }
        
        errors = agent._validate_diagnosis(invalid_diagnosis, 0)
        assert len(errors) > 0
        assert any('must be' in error.lower() and 'active' in error.lower() for error in errors)
    
    def test_validate_extracted_data_low_confidence_fields(self, agent):
        """Test validation flags low confidence fields."""
        data_with_low_confidence = {
            'symptoms': ['headache'],
            'vitals': {
                'blood_pressure': '120/80',
                'heart_rate': 72,
                'temperature': 98.6,
                'weight': 70.0,
                'height': 175.0
            },
            'lab_results': [],
            'medications': [],
            'diagnoses': [],
            'confidence_scores': {
                'overall': 0.6,
                'symptoms': 0.5,  # Low confidence
                'vitals': 0.8,
                'lab_results': 0.0,
                'medications': 0.0,
                'diagnoses': 0.0
            }
        }
        
        result = agent._validate_extracted_data(data_with_low_confidence)
        
        assert result['valid'] is True
        assert 'low_confidence_fields' in result
        assert 'symptoms' in result['low_confidence_fields']
        assert 'vitals' not in result['low_confidence_fields']  # Above 0.7
    
    def test_validate_extracted_data_flagged_fields(self, agent):
        """Test validation flags fields with errors."""
        data_with_errors = {
            'symptoms': ['headache'],
            'vitals': {
                'blood_pressure': '300/200',  # Out of range
                'heart_rate': 72,
                'temperature': 98.6,
                'weight': 70.0,
                'height': 175.0
            },
            'lab_results': [
                {
                    'test_name': 'Glucose',
                    'value': 'not a number',  # Invalid type
                    'unit': 'mg/dL',
                    'reference_range': '70-100',
                    'date': '2024-01-15'
                }
            ],
            'medications': [],
            'diagnoses': [],
            'confidence_scores': {
                'overall': 0.8,
                'symptoms': 0.9,
                'vitals': 0.8,
                'lab_results': 0.8,
                'medications': 0.0,
                'diagnoses': 0.0
            }
        }
        
        result = agent._validate_extracted_data(data_with_errors)
        
        assert result['valid'] is False
        assert 'flagged_fields' in result
        assert len(result['flagged_fields']) > 0
        assert any('vitals.blood_pressure' in field for field in result['flagged_fields'])
        assert any('lab_results[0]' in field for field in result['flagged_fields'])
    
    def test_calculate_confidence_scores_weighted_average(self, agent):
        """Test confidence scores use weighted average for overall score."""
        data = {
            'symptoms': ['headache', 'fever', 'cough'],
            'vitals': {
                'blood_pressure': '120/80',
                'heart_rate': 72,
                'temperature': 98.6,
                'weight': 70.0,
                'height': 175.0
            },
            'lab_results': [
                {
                    'test_name': 'Glucose',
                    'value': 95.0,
                    'unit': 'mg/dL',
                    'reference_range': '70-100',
                    'date': '2024-01-15'
                }
            ],
            'medications': [
                {
                    'name': 'Metformin',
                    'dosage': '500mg',
                    'frequency': 'twice daily',
                    'start_date': '2024-01-10'
                }
            ],
            'diagnoses': [
                {
                    'condition': 'Type 2 Diabetes',
                    'icd_code': 'E11.9',
                    'date': '2024-01-15',
                    'status': 'active'
                }
            ]
        }
        
        scores = agent._calculate_confidence_scores(data, "sample text")
        
        # All categories should have confidence > 0
        assert scores['symptoms'] > 0
        assert scores['vitals'] > 0
        assert scores['lab_results'] > 0
        assert scores['medications'] > 0
        assert scores['diagnoses'] > 0
        
        # Overall should be weighted average
        assert 0 < scores['overall'] <= 1.0
        
        # All scores should be rounded to 2 decimal places
        for score in scores.values():
            assert len(str(score).split('.')[-1]) <= 2
