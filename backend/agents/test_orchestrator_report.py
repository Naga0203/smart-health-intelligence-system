"""
Unit tests for OrchestratorAgent report data enhancements.

Tests cover:
- Pipeline with extracted data
- Data merging logic
- User data precedence
- Storage with report metadata
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from .orchestrator import OrchestratorAgent


@pytest.fixture
def mock_db():
    """Mock Firebase database."""
    db = Mock()
    db.store_assessment = Mock(return_value="assessment_123")
    db.store_prediction = Mock(return_value="prediction_123")
    db.store_explanation = Mock(return_value="explanation_123")
    db.store_recommendation = Mock(return_value="recommendation_123")
    db.store_audit_log = Mock()
    db.db = Mock()
    db.db.collection = Mock(return_value=Mock(document=Mock(return_value=Mock(update=Mock()))))
    return db


@pytest.fixture
def mock_agents():
    """Mock all agent dependencies."""
    with patch('agents.orchestrator.LangChainValidationAgent') as mock_validation, \
         patch('agents.orchestrator.DataExtractionAgent') as mock_extraction, \
         patch('agents.orchestrator.DiseasePredictor') as mock_predictor, \
         patch('agents.orchestrator.LangChainExplanationAgent') as mock_explanation, \
         patch('agents.orchestrator.RecommendationAgent') as mock_recommendation, \
         patch('agents.orchestrator.LifestyleModificationAgent') as mock_lifestyle, \
         patch('agents.orchestrator.ReflectionAgent') as mock_reflection:
        
        # Setup validation agent
        mock_validation_instance = Mock()
        mock_validation_instance.process = Mock(return_value={
            "success": True,
            "data": {
                "sanitized_input": {
                    "symptoms": ["fever", "cough"],
                    "age": 30,
                    "gender": "male"
                }
            }
        })
        mock_validation.return_value = mock_validation_instance
        
        # Setup extraction agent
        mock_extraction_instance = Mock()
        mock_extraction_instance.process = Mock(return_value={
            "success": True,
            "data": {
                "features": {"feature1": 1.0},
                "extraction_confidence": 0.85
            }
        })
        mock_extraction.return_value = mock_extraction_instance
        
        # Setup predictor
        mock_predictor_instance = Mock()
        mock_predictor_instance.predict = Mock(return_value=(0.75, {"model_version": "v1.0"}))
        mock_predictor.return_value = mock_predictor_instance
        
        # Setup explanation agent
        mock_explanation_instance = Mock()
        mock_explanation_instance.process = Mock(return_value={
            "success": True,
            "data": {"explanation": "Test explanation"}
        })
        mock_explanation.return_value = mock_explanation_instance
        
        # Setup recommendation agent
        mock_recommendation_instance = Mock()
        mock_recommendation_instance.get_recommendations = Mock(return_value={
            "recommendations": ["Test recommendation"]
        })
        mock_recommendation.return_value = mock_recommendation_instance
        
        # Setup lifestyle agent
        mock_lifestyle_instance = Mock()
        mock_lifestyle_instance.process = Mock(return_value={
            "success": True,
            "data": {"lifestyle": "Test lifestyle"}
        })
        mock_lifestyle.return_value = mock_lifestyle_instance
        
        # Setup reflection agent
        mock_reflection_instance = Mock()
        mock_reflection_instance.verify_assessment = Mock(return_value={
            "recommended_action": "approve",
            "severity": "low",
            "issue_count": 0
        })
        mock_reflection.return_value = mock_reflection_instance
        
        yield {
            "validation": mock_validation_instance,
            "extraction": mock_extraction_instance,
            "predictor": mock_predictor_instance,
            "explanation": mock_explanation_instance,
            "recommendation": mock_recommendation_instance,
            "lifestyle": mock_lifestyle_instance,
            "reflection": mock_reflection_instance
        }


@pytest.fixture
def orchestrator(mock_db, mock_agents):
    """Create orchestrator instance with mocked dependencies."""
    with patch('agents.orchestrator.get_firebase_db', return_value=mock_db):
        agent = OrchestratorAgent()
        return agent


class TestDataMerging:
    """Test the _merge_data_sources method."""
    
    def test_merge_symptoms_extracted_only(self, orchestrator):
        """Test merging when only extracted symptoms are present."""
        manual_data = {
            "symptoms": [],
            "age": 30,
            "gender": "male"
        }
        extracted_data = {
            "symptoms": ["headache", "fever", "fatigue"]
        }
        data_sources = {}
        
        result = orchestrator._merge_data_sources(manual_data, extracted_data, data_sources)
        
        assert set(result["symptoms"]) == {"headache", "fever", "fatigue"}
    
    def test_merge_symptoms_manual_priority(self, orchestrator):
        """Test that manual symptoms are preserved and extracted ones are added."""
        manual_data = {
            "symptoms": ["cough", "fever"],
            "age": 30,
            "gender": "male"
        }
        extracted_data = {
            "symptoms": ["fever", "headache", "fatigue"]
        }
        data_sources = {}
        
        result = orchestrator._merge_data_sources(manual_data, extracted_data, data_sources)
        
        # Should have all unique symptoms from both sources
        assert set(result["symptoms"]) == {"cough", "fever", "headache", "fatigue"}
    
    def test_merge_vitals_extracted_fills_gaps(self, orchestrator):
        """Test that extracted vitals fill in missing manual values."""
        manual_data = {
            "symptoms": ["fever"],
            "age": 30,
            "gender": "male",
            "additional_info": {
                "vitals": {
                    "heart_rate": 80
                }
            }
        }
        extracted_data = {
            "vitals": {
                "heart_rate": 75,
                "blood_pressure": "120/80",
                "temperature": 98.6
            }
        }
        data_sources = {}
        
        result = orchestrator._merge_data_sources(manual_data, extracted_data, data_sources)
        
        # Manual heart_rate should be preserved
        assert result["additional_info"]["vitals"]["heart_rate"] == 80
        # Extracted values should fill gaps
        assert result["additional_info"]["vitals"]["blood_pressure"] == "120/80"
        assert result["additional_info"]["vitals"]["temperature"] == 98.6
    
    def test_merge_lab_results_no_duplicates(self, orchestrator):
        """Test that lab results are merged without duplicates."""
        manual_data = {
            "symptoms": ["fever"],
            "age": 30,
            "gender": "male",
            "additional_info": {
                "lab_results": [
                    {"test_name": "glucose", "value": 100, "unit": "mg/dL"}
                ]
            }
        }
        extracted_data = {
            "lab_results": [
                {"test_name": "glucose", "value": 105, "unit": "mg/dL"},
                {"test_name": "cholesterol", "value": 180, "unit": "mg/dL"}
            ]
        }
        data_sources = {}
        
        result = orchestrator._merge_data_sources(manual_data, extracted_data, data_sources)
        
        # Should have 2 unique tests (manual glucose + extracted cholesterol)
        assert len(result["additional_info"]["lab_results"]) == 2
        test_names = {lab["test_name"] for lab in result["additional_info"]["lab_results"]}
        assert test_names == {"glucose", "cholesterol"}
        # Manual glucose value should be preserved
        glucose_result = next(lab for lab in result["additional_info"]["lab_results"] if lab["test_name"] == "glucose")
        assert glucose_result["value"] == 100
    
    def test_merge_medications_no_duplicates(self, orchestrator):
        """Test that medications are merged without duplicates."""
        manual_data = {
            "symptoms": ["fever"],
            "age": 30,
            "gender": "male",
            "additional_info": {
                "medications": [
                    {"name": "aspirin", "dosage": "100mg"}
                ]
            }
        }
        extracted_data = {
            "medications": [
                {"name": "aspirin", "dosage": "81mg"},
                {"name": "metformin", "dosage": "500mg"}
            ]
        }
        data_sources = {}
        
        result = orchestrator._merge_data_sources(manual_data, extracted_data, data_sources)
        
        # Should have 2 unique medications
        assert len(result["additional_info"]["medications"]) == 2
        med_names = {med["name"] for med in result["additional_info"]["medications"]}
        assert med_names == {"aspirin", "metformin"}
    
    def test_merge_diagnoses_no_duplicates(self, orchestrator):
        """Test that diagnoses are merged without duplicates."""
        manual_data = {
            "symptoms": ["fever"],
            "age": 30,
            "gender": "male",
            "additional_info": {
                "diagnoses": [
                    {"condition": "diabetes", "status": "active"}
                ]
            }
        }
        extracted_data = {
            "diagnoses": [
                {"condition": "diabetes", "status": "chronic"},
                {"condition": "hypertension", "status": "active"}
            ]
        }
        data_sources = {}
        
        result = orchestrator._merge_data_sources(manual_data, extracted_data, data_sources)
        
        # Should have 2 unique diagnoses
        assert len(result["additional_info"]["diagnoses"]) == 2
        conditions = {diag["condition"] for diag in result["additional_info"]["diagnoses"]}
        assert conditions == {"diabetes", "hypertension"}
    
    def test_merge_confidence_scores_included(self, orchestrator):
        """Test that extraction confidence scores are included in merged data."""
        manual_data = {
            "symptoms": ["fever"],
            "age": 30,
            "gender": "male"
        }
        extracted_data = {
            "symptoms": ["fever"],
            "confidence_scores": {
                "overall": 0.85,
                "symptoms": 0.90,
                "vitals": 0.80
            }
        }
        data_sources = {}
        
        result = orchestrator._merge_data_sources(manual_data, extracted_data, data_sources)
        
        assert "extraction_confidence_scores" in result["additional_info"]
        assert result["additional_info"]["extraction_confidence_scores"]["overall"] == 0.85


class TestPipelineWithReportData:
    """Test the run_pipeline method with report data."""
    
    def test_pipeline_with_report_metadata(self, orchestrator, mock_db):
        """Test pipeline execution with report metadata."""
        user_input = {
            "user_id": "user_123",
            "symptoms": ["fever", "cough"],
            "age": 30,
            "gender": "male",
            "report_metadata": {
                "report_id": "report_456",
                "extraction_job_id": "job_789",
                "has_extracted_data": True
            },
            "extracted_data": {
                "symptoms": ["headache"],
                "vitals": {"temperature": 99.5}
            },
            "data_sources": {}
        }
        
        result = orchestrator.run_pipeline(user_input)
        
        # Verify pipeline completed successfully
        assert "user_id" in result
        assert "prediction" in result
        assert result["user_id"] == "user_123"
        
        # Verify store_assessment was called with report_metadata
        assert mock_db.store_assessment.called
        call_args = mock_db.store_assessment.call_args
        assessment_data = call_args[0][1]
        assert "report_metadata" in assessment_data
        assert assessment_data["report_metadata"]["report_id"] == "report_456"
    
    def test_pipeline_without_report_metadata(self, orchestrator, mock_db):
        """Test pipeline execution without report metadata (backward compatibility)."""
        user_input = {
            "user_id": "user_123",
            "symptoms": ["fever", "cough"],
            "age": 30,
            "gender": "male"
        }
        
        result = orchestrator.run_pipeline(user_input)
        
        # Verify pipeline completed successfully
        assert "user_id" in result
        assert "prediction" in result
        
        # Verify store_assessment was called without report_metadata
        assert mock_db.store_assessment.called
        call_args = mock_db.store_assessment.call_args
        assessment_data = call_args[0][1]
        assert "report_metadata" not in assessment_data


class TestStorageWithReportMetadata:
    """Test the _store_assessment method with report metadata."""
    
    def test_store_assessment_with_report_metadata(self, orchestrator, mock_db):
        """Test storing assessment with report metadata."""
        report_metadata = {
            "report_id": "report_456",
            "extraction_job_id": "job_789",
            "has_extracted_data": True
        }
        
        result = orchestrator._store_assessment(
            user_id="user_123",
            sanitized_input={"symptoms": ["fever"], "age": 30, "gender": "male"},
            disease="diabetes",
            probability=0.75,
            confidence="MEDIUM",
            extraction_data={"features": {}},
            prediction_metadata={"model_version": "v1.0"},
            explanation_data={"explanation": "test"},
            recommendations={"recommendations": []},
            lifestyle_recommendations={},
            report_metadata=report_metadata
        )
        
        # Verify assessment was stored
        assert result["assessment_id"] == "assessment_123"
        
        # Verify report_metadata was included in assessment_data
        call_args = mock_db.store_assessment.call_args
        assessment_data = call_args[0][1]
        assert "report_metadata" in assessment_data
        assert assessment_data["report_metadata"]["report_id"] == "report_456"
        assert assessment_data["report_metadata"]["has_extracted_data"] is True
        
        # Verify audit log includes report info
        audit_call_args = mock_db.store_audit_log.call_args
        audit_payload = audit_call_args[1]["payload"]
        assert "report_id" in audit_payload
        assert audit_payload["report_id"] == "report_456"
    
    def test_store_assessment_without_report_metadata(self, orchestrator, mock_db):
        """Test storing assessment without report metadata (backward compatibility)."""
        result = orchestrator._store_assessment(
            user_id="user_123",
            sanitized_input={"symptoms": ["fever"], "age": 30, "gender": "male"},
            disease="diabetes",
            probability=0.75,
            confidence="MEDIUM",
            extraction_data={"features": {}},
            prediction_metadata={"model_version": "v1.0"},
            explanation_data={"explanation": "test"},
            recommendations={"recommendations": []},
            lifestyle_recommendations={},
            report_metadata=None
        )
        
        # Verify assessment was stored
        assert result["assessment_id"] == "assessment_123"
        
        # Verify report_metadata was not included
        call_args = mock_db.store_assessment.call_args
        assessment_data = call_args[0][1]
        assert "report_metadata" not in assessment_data
        
        # Verify audit log does not include report info
        audit_call_args = mock_db.store_audit_log.call_args
        audit_payload = audit_call_args[1]["payload"]
        assert "report_id" not in audit_payload
    
    def test_store_assessment_links_report_to_assessment(self, orchestrator, mock_db):
        """Test that report is linked to assessment in Firestore."""
        report_metadata = {
            "report_id": "report_456",
            "extraction_job_id": "job_789",
            "has_extracted_data": True
        }
        
        orchestrator._store_assessment(
            user_id="user_123",
            sanitized_input={"symptoms": ["fever"], "age": 30, "gender": "male"},
            disease="diabetes",
            probability=0.75,
            confidence="MEDIUM",
            extraction_data={"features": {}},
            prediction_metadata={"model_version": "v1.0"},
            explanation_data={"explanation": "test"},
            recommendations={"recommendations": []},
            lifestyle_recommendations={},
            report_metadata=report_metadata
        )
        
        # Verify report document was updated with assessment_id
        mock_db.db.collection.assert_called_with('medical_reports')
        mock_collection = mock_db.db.collection.return_value
        mock_collection.document.assert_called_with('report_456')
        mock_doc = mock_collection.document.return_value
        mock_doc.update.assert_called_with({'associated_assessment_id': 'assessment_123'})


class TestUserDataPrecedence:
    """Test that user data takes precedence over extracted data."""
    
    def test_user_symptoms_take_precedence(self, orchestrator):
        """Test that manually entered symptoms are prioritized."""
        manual_data = {
            "symptoms": ["cough", "fever"],
            "age": 30,
            "gender": "male"
        }
        extracted_data = {
            "symptoms": ["headache", "fatigue"]
        }
        data_sources = {"symptoms": "manual"}
        
        result = orchestrator._merge_data_sources(manual_data, extracted_data, data_sources)
        
        # When marked as manual, should only have manual symptoms
        assert result["symptoms"] == ["cough", "fever"]
    
    def test_user_vitals_take_precedence(self, orchestrator):
        """Test that manually entered vitals override extracted values."""
        manual_data = {
            "symptoms": ["fever"],
            "age": 30,
            "gender": "male",
            "additional_info": {
                "vitals": {
                    "temperature": 100.5,
                    "heart_rate": 85
                }
            }
        }
        extracted_data = {
            "vitals": {
                "temperature": 98.6,
                "heart_rate": 72,
                "blood_pressure": "120/80"
            }
        }
        data_sources = {}
        
        result = orchestrator._merge_data_sources(manual_data, extracted_data, data_sources)
        
        # Manual values should be preserved
        assert result["additional_info"]["vitals"]["temperature"] == 100.5
        assert result["additional_info"]["vitals"]["heart_rate"] == 85
        # Extracted value should fill gap
        assert result["additional_info"]["vitals"]["blood_pressure"] == "120/80"
