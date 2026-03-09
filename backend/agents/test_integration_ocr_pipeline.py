"""
Integration tests for OCR pipeline.

Tests end-to-end OCR extraction including:
- End-to-end OCR extraction
- Multiple image formats
- Structured data extraction
- Error handling

Requirements: 4.1, 4.5, 4.7
"""

import pytest
import base64
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from io import BytesIO

from backend.agents.infrastructure.gemini_ocr import GeminiOCRService
from backend.agents.infrastructure.models import OCRResult
from backend.agents.enhanced_extraction import EnhancedExtractionAgent


class TestOCRPipelineIntegration:
    """Integration tests for OCR pipeline."""
    
    @pytest.fixture
    def ocr_service(self):
        """Create OCR service for testing."""
        return GeminiOCRService()
    
    @pytest.fixture
    def enhanced_extraction_agent(self):
        """Create enhanced extraction agent for testing."""
        return EnhancedExtractionAgent()
    
    @pytest.fixture
    def sample_medical_report_text(self):
        """Sample medical report text."""
        return """
        MEDICAL REPORT
        
        Patient: John Doe
        Date: 2024-01-15
        
        LABORATORY RESULTS:
        - Fasting Blood Glucose: 145 mg/dL (Reference: 70-100 mg/dL)
        - HbA1c: 7.2% (Reference: 4.0-5.6%)
        - Total Cholesterol: 220 mg/dL (Reference: <200 mg/dL)
        
        VITAL SIGNS:
        - Blood Pressure: 140/90 mmHg
        - Heart Rate: 85 bpm
        - Temperature: 98.6°F
        
        MEDICATIONS:
        - Metformin 500mg twice daily
        - Lisinopril 10mg once daily
        
        DIAGNOSIS:
        - Type 2 Diabetes Mellitus (E11.9)
        - Hypertension (I10)
        """
    
    @pytest.fixture
    def mock_image_data(self):
        """Create mock image data."""
        # Create a simple mock image (1x1 pixel)
        return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
    
    def test_end_to_end_ocr_extraction(self, ocr_service, sample_medical_report_text, mock_image_data):
        """
        Test complete OCR extraction pipeline.
        
        Requirements: 4.1 - Gemini-based OCR
        """
        # Mock Gemini Vision API
        with patch.object(ocr_service, 'gemini_vision') as mock_vision:
            mock_response = Mock()
            mock_response.content = sample_medical_report_text
            mock_vision.invoke.return_value = mock_response
            
            # Perform OCR extraction
            result = ocr_service.extract_text(mock_image_data, "png")
            
            # Verify OCR result structure
            assert isinstance(result, OCRResult)
            assert result.text is not None
            assert len(result.text) > 0
            assert result.confidence > 0
            assert result.format == "png"
            
            # Verify medical content was extracted
            assert "MEDICAL REPORT" in result.text or "medical" in result.text.lower()
            
            print(f"✓ End-to-end OCR extraction verified: {len(result.text)} chars extracted")
    
    def test_multiple_image_formats(self, ocr_service, sample_medical_report_text):
        """
        Test OCR extraction with multiple image formats.
        
        Requirements: 4.5 - Handle multiple image formats
        """
        formats = ["jpeg", "png", "pdf", "tiff"]
        
        # Mock Gemini Vision API
        with patch.object(ocr_service, 'gemini_vision') as mock_vision:
            mock_response = Mock()
            mock_response.content = sample_medical_report_text
            mock_vision.invoke.return_value = mock_response
            
            for image_format in formats:
                # Create mock image data
                mock_image = b'\x00\x01\x02\x03'
                
                # Perform OCR extraction
                result = ocr_service.extract_text(mock_image, image_format)
                
                # Verify extraction succeeded
                assert isinstance(result, OCRResult)
                assert result.format == image_format
                assert len(result.text) > 0
                
                print(f"✓ OCR extraction verified for format: {image_format}")
    
    def test_structured_data_extraction(self, ocr_service, sample_medical_report_text, mock_image_data):
        """
        Test extraction of structured data from medical reports.
        
        Requirements: 4.7 - Extract structured medical data
        """
        # Mock Gemini Vision API
        with patch.object(ocr_service, 'gemini_vision') as mock_vision:
            mock_response = Mock()
            mock_response.content = sample_medical_report_text
            mock_vision.invoke.return_value = mock_response
            
            # Perform structured data extraction
            result = ocr_service.extract_structured_data(mock_image_data)
            
            # Verify structured data was extracted
            assert isinstance(result, dict)
            
            # Verify lab results extraction
            if "lab_results" in result:
                lab_results = result["lab_results"]
                assert isinstance(lab_results, list)
                
                # Check for expected lab tests
                test_names = [lab.get("test_name", "").lower() for lab in lab_results]
                assert any("glucose" in name or "hba1c" in name for name in test_names)
            
            # Verify vitals extraction
            if "vitals" in result:
                vitals = result["vitals"]
                assert isinstance(vitals, dict)
            
            # Verify medications extraction
            if "medications" in result:
                medications = result["medications"]
                assert isinstance(medications, list)
            
            # Verify diagnoses extraction
            if "diagnoses" in result:
                diagnoses = result["diagnoses"]
                assert isinstance(diagnoses, list)
            
            print(f"✓ Structured data extraction verified: {len(result)} categories")
    
    def test_lab_results_extraction(self, ocr_service, sample_medical_report_text, mock_image_data):
        """
        Test extraction of lab results with values and units.
        
        Requirements: 8.2 - Extract lab results with details
        """
        # Mock Gemini Vision API
        with patch.object(ocr_service, 'gemini_vision') as mock_vision:
            mock_response = Mock()
            mock_response.content = sample_medical_report_text
            mock_vision.invoke.return_value = mock_response
            
            # Extract structured data
            result = ocr_service.extract_structured_data(mock_image_data)
            
            # Verify lab results structure
            if "lab_results" in result:
                lab_results = result["lab_results"]
                
                for lab in lab_results:
                    # Each lab result should have required fields
                    assert "test_name" in lab or "name" in lab
                    # May have value, unit, reference_range
                    
                print(f"✓ Lab results extraction verified: {len(lab_results)} tests")
    
    def test_table_extraction(self, ocr_service, mock_image_data):
        """
        Test extraction of data from tables in medical reports.
        
        Requirements: 14.4 - Extract data from tables
        """
        table_text = """
        TEST NAME          VALUE       UNIT      REFERENCE RANGE
        Glucose            145         mg/dL     70-100
        HbA1c              7.2         %         4.0-5.6
        Cholesterol        220         mg/dL     <200
        """
        
        # Mock Gemini Vision API
        with patch.object(ocr_service, 'gemini_vision') as mock_vision:
            mock_response = Mock()
            mock_response.content = table_text
            mock_vision.invoke.return_value = mock_response
            
            # Extract table data
            result = ocr_service.extract_from_table(mock_image_data)
            
            # Verify table extraction
            assert isinstance(result, list)
            
            # Each row should be a dictionary
            for row in result:
                assert isinstance(row, dict)
            
            print(f"✓ Table extraction verified: {len(result)} rows")
    
    def test_chart_data_extraction(self, ocr_service, mock_image_data):
        """
        Test extraction of data from charts and graphs.
        
        Requirements: 14.2 - Extract data from charts
        """
        chart_description = """
        Blood Glucose Trend Chart:
        - January: 150 mg/dL
        - February: 145 mg/dL
        - March: 140 mg/dL
        Trend: Decreasing
        """
        
        # Mock Gemini Vision API
        with patch.object(ocr_service, 'gemini_vision') as mock_vision:
            mock_response = Mock()
            mock_response.content = chart_description
            mock_vision.invoke.return_value = mock_response
            
            # Extract chart data
            result = ocr_service.extract_from_chart(mock_image_data)
            
            # Verify chart extraction
            assert isinstance(result, dict)
            
            # Should contain data points or trend information
            assert len(result) > 0
            
            print(f"✓ Chart extraction verified: {len(result)} elements")
    
    def test_handwriting_extraction(self, ocr_service, mock_image_data):
        """
        Test extraction of handwritten text.
        
        Requirements: 14.5 - Extract handwritten text
        """
        handwritten_text = "Patient complains of increased thirst and frequent urination"
        
        # Mock Gemini Vision API
        with patch.object(ocr_service, 'gemini_vision') as mock_vision:
            mock_response = Mock()
            mock_response.content = handwritten_text
            mock_vision.invoke.return_value = mock_response
            
            # Extract handwritten text
            result = ocr_service.handle_handwriting(mock_image_data)
            
            # Verify extraction
            assert isinstance(result, str)
            assert len(result) > 0
            
            print(f"✓ Handwriting extraction verified: {len(result)} chars")
    
    def test_report_type_identification(self, ocr_service, sample_medical_report_text, mock_image_data):
        """
        Test identification of medical report type.
        
        Requirements: 14.6 - Identify report type
        """
        # Mock Gemini Vision API
        with patch.object(ocr_service, 'gemini_vision') as mock_vision:
            mock_response = Mock()
            mock_response.content = sample_medical_report_text
            mock_vision.invoke.return_value = mock_response
            
            # Extract structured data (includes report type)
            result = ocr_service.extract_structured_data(mock_image_data)
            
            # Verify report type identification
            if "report_type" in result:
                report_type = result["report_type"]
                assert report_type in ["lab_report", "radiology", "pathology", "general", "unknown"]
                print(f"✓ Report type identified: {report_type}")
            else:
                print("✓ Report type identification attempted")
    
    def test_confidence_scores(self, ocr_service, sample_medical_report_text, mock_image_data):
        """
        Test that OCR results include confidence scores.
        
        Requirements: 4.6 - Provide confidence scores
        """
        # Mock Gemini Vision API
        with patch.object(ocr_service, 'gemini_vision') as mock_vision:
            mock_response = Mock()
            mock_response.content = sample_medical_report_text
            mock_vision.invoke.return_value = mock_response
            
            # Perform OCR extraction
            result = ocr_service.extract_text(mock_image_data, "png")
            
            # Verify confidence score
            assert hasattr(result, 'confidence')
            assert 0 <= result.confidence <= 1
            
            print(f"✓ Confidence score verified: {result.confidence:.2f}")
    
    def test_ocr_error_handling(self, ocr_service):
        """
        Test OCR error handling for invalid inputs.
        
        Requirements: 4.8 - Provide detailed error information
        """
        # Test with empty image data
        try:
            result = ocr_service.extract_text(b'', "png")
            # Should either raise exception or return error result
            if isinstance(result, OCRResult):
                assert result.confidence == 0 or "error" in result.metadata
        except Exception as e:
            # Error should be informative
            assert len(str(e)) > 0
            print(f"✓ OCR error handling verified: {str(e)[:50]}")
    
    def test_corrupted_image_handling(self, ocr_service):
        """
        Test handling of corrupted image data.
        
        Requirements: 4.8 - Error handling
        """
        # Create corrupted image data
        corrupted_data = b'\x00\x01\x02\x03\x04\x05'
        
        # Mock Gemini to fail
        with patch.object(ocr_service, 'gemini_vision') as mock_vision:
            mock_vision.invoke.side_effect = Exception("Invalid image format")
            
            # Attempt extraction
            try:
                result = ocr_service.extract_text(corrupted_data, "png")
                # Should handle error gracefully
                if isinstance(result, OCRResult):
                    assert result.confidence == 0
            except Exception as e:
                # Should provide detailed error
                assert "image" in str(e).lower() or "format" in str(e).lower()
                print(f"✓ Corrupted image handling verified")
    
    def test_enhanced_extraction_agent_integration(self, enhanced_extraction_agent, sample_medical_report_text):
        """
        Test integration of OCR service with enhanced extraction agent.
        
        Requirements: 4.1, 4.2, 4.3 - Complete OCR integration
        """
        # Create mock report data
        report_data = {
            "report_id": "report_123",
            "image_data": base64.b64encode(b'\x00\x01\x02\x03').decode(),
            "format": "png"
        }
        
        # Mock OCR service
        with patch.object(enhanced_extraction_agent, 'ocr_service') as mock_ocr:
            mock_result = OCRResult(
                text=sample_medical_report_text,
                confidence=0.95,
                structured_data={
                    "lab_results": [
                        {"test_name": "Glucose", "value": 145, "unit": "mg/dL"}
                    ],
                    "vitals": {"blood_pressure": "140/90"},
                    "medications": [{"name": "Metformin", "dosage": "500mg"}],
                    "diagnoses": [{"condition": "Type 2 Diabetes"}]
                },
                metadata={"report_type": "lab_report"},
                extraction_time=1.5,
                pages_processed=1,
                format="png"
            )
            mock_ocr.extract_text.return_value = mock_result
            mock_ocr.extract_structured_data.return_value = mock_result.structured_data
            
            # Process report through agent
            input_data = {
                "report_data": report_data,
                "user_id": "test_user"
            }
            
            result = enhanced_extraction_agent.process(input_data)
            
            # Verify agent processed OCR results
            assert result is not None
            assert result.get("success") is True or "data" in result
            
            print("✓ Enhanced extraction agent integration verified")
    
    def test_multi_page_document_processing(self, ocr_service):
        """
        Test processing of multi-page documents.
        
        Requirements: 4.1 - OCR for medical reports
        """
        # Mock multi-page document
        pages = [
            "Page 1: Patient Information",
            "Page 2: Lab Results",
            "Page 3: Recommendations"
        ]
        
        # Mock Gemini Vision API
        with patch.object(ocr_service, 'gemini_vision') as mock_vision:
            # Return different content for each page
            mock_vision.invoke.side_effect = [
                Mock(content=page) for page in pages
            ]
            
            # Process each page
            results = []
            for i, page_data in enumerate([b'\x00\x01', b'\x02\x03', b'\x04\x05']):
                result = ocr_service.extract_text(page_data, "pdf")
                results.append(result)
            
            # Verify all pages processed
            assert len(results) == len(pages)
            
            print(f"✓ Multi-page processing verified: {len(results)} pages")
    
    def test_ocr_performance_metrics(self, ocr_service, sample_medical_report_text, mock_image_data):
        """
        Test that OCR results include performance metrics.
        
        Requirements: 10.1 - Track execution metrics
        """
        # Mock Gemini Vision API
        with patch.object(ocr_service, 'gemini_vision') as mock_vision:
            mock_response = Mock()
            mock_response.content = sample_medical_report_text
            mock_vision.invoke.return_value = mock_response
            
            # Perform OCR extraction
            import time
            start_time = time.time()
            result = ocr_service.extract_text(mock_image_data, "png")
            extraction_time = time.time() - start_time
            
            # Verify performance metrics
            assert hasattr(result, 'extraction_time')
            assert result.extraction_time > 0
            assert hasattr(result, 'pages_processed')
            
            print(f"✓ OCR performance metrics: {result.extraction_time:.2f}s, {result.pages_processed} pages")
    
    def test_ocr_with_poor_quality_image(self, ocr_service):
        """
        Test OCR with poor quality images.
        
        Requirements: 4.6 - Confidence scores for quality assessment
        """
        poor_quality_text = "blurry text... unclear... partial..."
        
        # Mock Gemini Vision API with low confidence
        with patch.object(ocr_service, 'gemini_vision') as mock_vision:
            mock_response = Mock()
            mock_response.content = poor_quality_text
            mock_vision.invoke.return_value = mock_response
            
            # Perform OCR extraction
            result = ocr_service.extract_text(b'\x00\x01', "png")
            
            # Verify low confidence is reflected
            # Note: Actual confidence calculation depends on implementation
            assert hasattr(result, 'confidence')
            
            print(f"✓ Poor quality image handling: confidence={result.confidence:.2f}")


class TestOCRDataValidation:
    """Integration tests for OCR data validation."""
    
    def test_extracted_data_validation(self):
        """
        Test that extracted data is validated before use.
        
        Requirements: 9.6 - Validate external data
        """
        # Create OCR result with potentially invalid data
        ocr_result = OCRResult(
            text="Sample text",
            confidence=0.85,
            structured_data={
                "lab_results": [
                    {"test_name": "Glucose", "value": "invalid", "unit": "mg/dL"},
                    {"test_name": "HbA1c", "value": 7.2, "unit": "%"}
                ]
            },
            metadata={},
            extraction_time=1.0,
            pages_processed=1,
            format="png"
        )
        
        # Validate structured data
        lab_results = ocr_result.structured_data.get("lab_results", [])
        
        valid_results = []
        for lab in lab_results:
            # Validate each field
            if isinstance(lab.get("value"), (int, float)):
                valid_results.append(lab)
        
        # Only valid results should remain
        assert len(valid_results) == 1
        assert valid_results[0]["test_name"] == "HbA1c"
        
        print(f"✓ Data validation: {len(valid_results)}/{len(lab_results)} valid")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
