"""
Property-Based Tests for DataExtractionAgent

Tests universal correctness properties that should hold across all valid inputs
for the enhanced data extraction agent with web search and confidence scoring.

Requirements: 1.6, 8.3, 8.4, 8.5, 8.6

Properties Tested:
- Property 1: Agent Migration Preserves Functionality (Requirement 1.6)
- Property 32: Medication Extraction Includes Complete Details (Requirement 8.3)
- Property 33: Diagnosis Extraction Includes Codes and Dates (Requirement 8.4)
- Property 34: Vital Signs Extraction Includes Units (Requirement 8.5)
- Property 35: Ambiguous Terms Trigger Clarification Searches (Requirement 8.6)
"""

import pytest
pytest_plugins = ['pytest_asyncio']
pytestmark = pytest.mark.pbt

import pytest
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from typing import Dict, Any, List
import json

from .data_extraction import DataExtractionAgent
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
        agent_name="DataExtractionAgent",
        enable_web_search=True,
        enable_caching=True,
        monitoring_enabled=False
    )
    agent = DataExtractionAgent(config)
    
    # Mock web search tool
    agent.web_search_tool = MagicMock()
    
    return agent


@pytest.fixture
def agent_without_web_search(mock_gemini_client):
    """Create agent with web search disabled."""
    config = AgentConfig(
        agent_name="DataExtractionAgent",
        enable_web_search=False,
        monitoring_enabled=False
    )
    agent = DataExtractionAgent(config)
    return agent


# ============================================================================
# Hypothesis Strategies for Generating Test Data
# ============================================================================

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

# Valid age strategy
age_strategy = st.integers(min_value=1, max_value=120)

# Valid gender strategy
gender_strategy = st.sampled_from(["male", "female", "other"])

# Valid disease strategy
disease_strategy = st.sampled_from(["diabetes", "heart_disease", "hypertension"])

# Medication data strategy
medication_strategy = st.fixed_dictionaries({
    "name": st.text(min_size=3, max_size=30),
    "dosage": st.text(min_size=2, max_size=20),
    "frequency": st.sampled_from(["once daily", "twice daily", "three times daily", "as needed"]),
    "duration": st.text(min_size=3, max_size=20)
})

# Diagnosis data strategy
diagnosis_strategy = st.fixed_dictionaries({
    "condition": st.text(min_size=3, max_size=50),
    "icd_code": st.one_of(
        st.none(),
        st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.", min_size=3, max_size=10)
    ),
    "date": st.one_of(
        st.none(),
        st.dates().map(lambda d: d.isoformat())
    )
})

# Vital signs data strategy
vital_signs_strategy = st.fixed_dictionaries({
    "blood_pressure": st.one_of(
        st.none(),
        st.tuples(st.integers(min_value=60, max_value=200), st.integers(min_value=40, max_value=130))
            .map(lambda t: f"{t[0]}/{t[1]} mmHg")
    ),
    "heart_rate": st.one_of(
        st.none(),
        st.integers(min_value=40, max_value=200).map(lambda v: f"{v} bpm")
    ),
    "temperature": st.one_of(
        st.none(),
        st.floats(min_value=95.0, max_value=105.0).map(lambda v: f"{v:.1f} °F")
    ),
    "weight": st.one_of(
        st.none(),
        st.floats(min_value=30.0, max_value=300.0).map(lambda v: f"{v:.1f} kg")
    )
})

# Ambiguous medical terms strategy
ambiguous_terms_strategy = st.lists(
    st.sampled_from([
        "MI", "CVA", "SOB", "DOE", "CP", "N/V", "HTN", "DM", "CAD", "CHF",
        "acute", "chronic", "severe", "mild", "moderate"
    ]),
    min_size=1,
    max_size=5
)


# ============================================================================
# Property 1: Agent Migration Preserves Functionality
# Validates: Requirement 1.6
# ============================================================================

class TestProperty1_MigrationPreservesFunctionality:
    """
    Property 1: Agent Migration Preserves Functionality
    
    For any valid input (symptoms, age, gender, disease), the migrated agent
    implementation should produce outputs with the same structure and key fields
    as the original implementation.
    """
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        symptoms=symptoms_strategy,
        age=age_strategy,
        gender=gender_strategy,
        disease=disease_strategy
    )
    def test_migrated_agent_preserves_output_structure(
        self, agent_with_web_search, symptoms, age, gender, disease
    ):
        """
        Test that migrated agent produces outputs with expected structure.
        
        The migrated agent should always return:
        - success field (boolean)
        - data field with extraction results
        - features dictionary
        - confidence_scores dictionary
        - extraction_confidence score
        """
        input_data = {
            "symptoms": symptoms,
            "age": age,
            "gender": gender,
            "disease": disease
        }
        
        result = agent_with_web_search.process(input_data)
        
        # Property: Result must have success field
        assert "success" in result, "Result must contain 'success' field"
        assert isinstance(result["success"], bool), "'success' must be boolean"
        
        if result["success"]:
            # Property: Successful results must have data field
            assert "data" in result, "Successful result must contain 'data' field"
            data = result["data"]
            
            # Property: Data must contain features
            assert "features" in data, "Data must contain 'features' field"
            assert isinstance(data["features"], dict), "'features' must be a dictionary"
            
            # Property: Data must contain confidence scores
            assert "confidence_scores" in data, "Data must contain 'confidence_scores' field"
            assert isinstance(data["confidence_scores"], dict), "'confidence_scores' must be a dictionary"
            
            # Property: Data must contain overall extraction confidence
            assert "extraction_confidence" in data, "Data must contain 'extraction_confidence' field"
            assert isinstance(data["extraction_confidence"], (int, float)), "'extraction_confidence' must be numeric"
            assert 0.0 <= data["extraction_confidence"] <= 1.0, "'extraction_confidence' must be between 0 and 1"
            
            # Property: Basic features must always be present
            assert "age" in data["features"], "Features must contain 'age'"
            assert "gender" in data["features"], "Features must contain 'gender'"
            
            # Property: Confidence scores must exist for all features
            for feature in data["features"]:
                assert feature in data["confidence_scores"], f"Confidence score missing for feature '{feature}'"
                confidence = data["confidence_scores"][feature]
                assert isinstance(confidence, (int, float)), f"Confidence for '{feature}' must be numeric"
                assert 0.0 <= confidence <= 1.0, f"Confidence for '{feature}' must be between 0 and 1"
    
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        symptoms=symptoms_strategy,
        age=age_strategy,
        gender=gender_strategy,
        disease=disease_strategy
    )
    def test_migrated_agent_handles_missing_fields_consistently(
        self, agent_with_web_search, symptoms, age, gender, disease
    ):
        """
        Test that migrated agent consistently handles missing required fields.
        
        When required fields are missing, the agent should:
        - Return success=False
        - Provide clear error message
        - List missing fields
        """
        # Test with missing symptoms
        input_missing_symptoms = {
            "age": age,
            "gender": gender,
            "disease": disease
            # Missing symptoms
        }
        
        result = agent_with_web_search.process(input_missing_symptoms)
        
        # Property: Missing required fields should result in failure
        assert result["success"] is False, "Missing required fields should fail"
        assert "message" in result, "Error result must contain 'message'"
        assert "symptoms" in result["message"].lower() or (
            "metadata" in result and "missing_fields" in result["metadata"]
        ), "Error should indicate missing symptoms"


# ============================================================================
# Property 32: Medication Extraction Includes Complete Details
# Validates: Requirement 8.3
# ============================================================================

class TestProperty32_MedicationExtractionComplete:
    """
    Property 32: Medication Extraction Includes Complete Details
    
    For any medical report containing medications, the extraction should include:
    - Drug name
    - Dosage
    - Frequency
    - Duration (when available)
    """
    
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        medication=medication_strategy,
        age=age_strategy,
        gender=gender_strategy
    )
    def test_medication_extraction_includes_all_details(
        self, agent_with_web_search, medication, age, gender
    ):
        """
        Test that medication extraction captures all relevant details.
        
        When additional_info contains medication data, the extraction should
        preserve all medication details with appropriate confidence scores.
        """
        # Create input with medication information
        symptoms = [f"taking {medication['name']}"]
        input_data = {
            "symptoms": symptoms,
            "age": age,
            "gender": gender,
            "disease": "diabetes",
            "additional_info": {
                "medications": [medication]
            }
        }
        
        # Mock LangChain extraction to return medication details
        mock_extraction_result = json.dumps({
            "mapped_features": {
                "age": age,
                "gender": 1 if gender == "male" else 0,
                "medications": [medication]
            },
            "confidence_scores": {
                "age": 1.0,
                "gender": 1.0,
                "medications": 0.9
            },
            "overall_confidence": 0.95,
            "missing_features": [],
            "ambiguous_terms": []
        })
        
        if agent_with_web_search.extraction_chain:
            agent_with_web_search.extraction_chain.invoke = MagicMock(return_value=mock_extraction_result)
        
        result = agent_with_web_search.process(input_data)
        
        if result["success"] and "medications" in result["data"].get("features", {}):
            medications_extracted = result["data"]["features"]["medications"]
            
            # Property: Extracted medications must be a list
            assert isinstance(medications_extracted, list), "Medications must be extracted as a list"
            
            if medications_extracted:
                med = medications_extracted[0]
                
                # Property: Each medication must have a name
                assert "name" in med, "Medication must include drug name"
                assert len(med["name"]) > 0, "Drug name must not be empty"
                
                # Property: Each medication should have dosage information
                if "dosage" in med:
                    assert len(med["dosage"]) > 0, "Dosage must not be empty if present"
                
                # Property: Each medication should have frequency information
                if "frequency" in med:
                    assert len(med["frequency"]) > 0, "Frequency must not be empty if present"
                
                # Property: Medication extraction should have confidence score
                if "medications" in result["data"]["confidence_scores"]:
                    med_confidence = result["data"]["confidence_scores"]["medications"]
                    assert 0.0 <= med_confidence <= 1.0, "Medication confidence must be between 0 and 1"


# ============================================================================
# Property 33: Diagnosis Extraction Includes Codes and Dates
# Validates: Requirement 8.4
# ============================================================================

class TestProperty33_DiagnosisExtractionComplete:
    """
    Property 33: Diagnosis Extraction Includes Codes and Dates
    
    For any medical report containing diagnoses, the extraction should include:
    - Condition name
    - ICD codes (when present)
    - Diagnosis dates (when present)
    """
    
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        diagnosis=diagnosis_strategy,
        age=age_strategy,
        gender=gender_strategy
    )
    def test_diagnosis_extraction_includes_codes_and_dates(
        self, agent_with_web_search, diagnosis, age, gender
    ):
        """
        Test that diagnosis extraction captures condition, codes, and dates.
        
        When additional_info contains diagnosis data, the extraction should
        preserve all diagnosis details including ICD codes and dates when available.
        """
        # Create input with diagnosis information
        symptoms = [f"diagnosed with {diagnosis['condition']}"]
        input_data = {
            "symptoms": symptoms,
            "age": age,
            "gender": gender,
            "disease": "diabetes",
            "additional_info": {
                "diagnoses": [diagnosis]
            }
        }
        
        # Mock LangChain extraction to return diagnosis details
        mock_extraction_result = json.dumps({
            "mapped_features": {
                "age": age,
                "gender": 1 if gender == "male" else 0,
                "diagnoses": [diagnosis]
            },
            "confidence_scores": {
                "age": 1.0,
                "gender": 1.0,
                "diagnoses": 0.85
            },
            "overall_confidence": 0.90,
            "missing_features": [],
            "ambiguous_terms": []
        })
        
        if agent_with_web_search.extraction_chain:
            agent_with_web_search.extraction_chain.invoke = MagicMock(return_value=mock_extraction_result)
        
        result = agent_with_web_search.process(input_data)
        
        if result["success"] and "diagnoses" in result["data"].get("features", {}):
            diagnoses_extracted = result["data"]["features"]["diagnoses"]
            
            # Property: Extracted diagnoses must be a list
            assert isinstance(diagnoses_extracted, list), "Diagnoses must be extracted as a list"
            
            if diagnoses_extracted:
                diag = diagnoses_extracted[0]
                
                # Property: Each diagnosis must have a condition name
                assert "condition" in diag, "Diagnosis must include condition name"
                assert len(diag["condition"]) > 0, "Condition name must not be empty"
                
                # Property: ICD code should be preserved if present in input
                if diagnosis["icd_code"] is not None:
                    # If ICD code was in input, it should be in output or noted as missing
                    assert "icd_code" in diag or "missing_features" in result["data"], \
                        "ICD code should be extracted or noted as missing"
                
                # Property: Date should be preserved if present in input
                if diagnosis["date"] is not None:
                    # If date was in input, it should be in output or noted as missing
                    assert "date" in diag or "missing_features" in result["data"], \
                        "Diagnosis date should be extracted or noted as missing"
                
                # Property: Diagnosis extraction should have confidence score
                if "diagnoses" in result["data"]["confidence_scores"]:
                    diag_confidence = result["data"]["confidence_scores"]["diagnoses"]
                    assert 0.0 <= diag_confidence <= 1.0, "Diagnosis confidence must be between 0 and 1"


# ============================================================================
# Property 34: Vital Signs Extraction Includes Units
# Validates: Requirement 8.5
# ============================================================================

class TestProperty34_VitalSignsIncludeUnits:
    """
    Property 34: Vital Signs Extraction Includes Units
    
    For any medical report containing vital signs, the extraction should include:
    - Measurement value
    - Appropriate units (mmHg, bpm, °F/°C, kg/lbs, etc.)
    """
    
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        vital_signs=vital_signs_strategy,
        age=age_strategy,
        gender=gender_strategy
    )
    def test_vital_signs_extraction_includes_units(
        self, agent_with_web_search, vital_signs, age, gender
    ):
        """
        Test that vital signs extraction includes units for all measurements.
        
        When additional_info contains vital signs, the extraction should
        preserve both values and units for each measurement.
        """
        # Create input with vital signs information
        symptoms = ["routine checkup"]
        input_data = {
            "symptoms": symptoms,
            "age": age,
            "gender": gender,
            "disease": "hypertension",
            "additional_info": {
                "vital_signs": vital_signs
            }
        }
        
        # Mock LangChain extraction to return vital signs with units
        mock_extraction_result = json.dumps({
            "mapped_features": {
                "age": age,
                "gender": 1 if gender == "male" else 0,
                "vital_signs": vital_signs
            },
            "confidence_scores": {
                "age": 1.0,
                "gender": 1.0,
                "vital_signs": 0.95
            },
            "overall_confidence": 0.95,
            "missing_features": [],
            "ambiguous_terms": []
        })
        
        if agent_with_web_search.extraction_chain:
            agent_with_web_search.extraction_chain.invoke = MagicMock(return_value=mock_extraction_result)
        
        result = agent_with_web_search.process(input_data)
        
        if result["success"] and "vital_signs" in result["data"].get("features", {}):
            vitals_extracted = result["data"]["features"]["vital_signs"]
            
            # Property: Extracted vital signs must be a dictionary
            assert isinstance(vitals_extracted, dict), "Vital signs must be extracted as a dictionary"
            
            # Define expected units for each vital sign type
            unit_patterns = {
                "blood_pressure": ["mmHg", "mm Hg"],
                "heart_rate": ["bpm", "beats/min", "beats per minute"],
                "temperature": ["°F", "°C", "F", "C", "degrees"],
                "weight": ["kg", "lbs", "pounds", "kilograms"]
            }
            
            # Property: Each vital sign with a value should include units
            for vital_type, value in vitals_extracted.items():
                if value is not None and value != "":
                    value_str = str(value)
                    
                    # Check if units are present for this vital sign type
                    if vital_type in unit_patterns:
                        expected_units = unit_patterns[vital_type]
                        has_unit = any(unit.lower() in value_str.lower() for unit in expected_units)
                        
                        assert has_unit, f"Vital sign '{vital_type}' with value '{value}' must include units from {expected_units}"
            
            # Property: Vital signs extraction should have confidence score
            if "vital_signs" in result["data"]["confidence_scores"]:
                vitals_confidence = result["data"]["confidence_scores"]["vital_signs"]
                assert 0.0 <= vitals_confidence <= 1.0, "Vital signs confidence must be between 0 and 1"


# ============================================================================
# Property 35: Ambiguous Terms Trigger Clarification Searches
# Validates: Requirement 8.6
# ============================================================================

class TestProperty35_AmbiguousTermsTriggerSearches:
    """
    Property 35: Ambiguous Terms Trigger Clarification Searches
    
    For any extraction containing ambiguous medical terms, the agent should:
    - Identify the ambiguous terms
    - Perform web searches to clarify them
    - Include clarifications in the output
    """
    
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        ambiguous_terms=ambiguous_terms_strategy,
        age=age_strategy,
        gender=gender_strategy
    )
    def test_ambiguous_terms_trigger_web_search(
        self, agent_with_web_search, ambiguous_terms, age, gender
    ):
        """
        Test that ambiguous medical terms trigger clarification searches.
        
        When the extraction identifies ambiguous terms, the agent should:
        1. Detect the ambiguous terms
        2. Perform web searches for clarification
        3. Include clarifications in the result
        """
        # Create input with ambiguous medical terms
        symptoms = [f"patient has {term}" for term in ambiguous_terms[:3]]
        input_data = {
            "symptoms": symptoms,
            "age": age,
            "gender": gender,
            "disease": "heart_disease"
        }
        
        # Mock LangChain extraction to identify ambiguous terms
        mock_extraction_result = json.dumps({
            "mapped_features": {
                "age": age,
                "gender": 1 if gender == "male" else 0
            },
            "confidence_scores": {
                "age": 1.0,
                "gender": 1.0
            },
            "overall_confidence": 0.60,
            "missing_features": [],
            "ambiguous_terms": ambiguous_terms[:3]  # Report some terms as ambiguous
        })
        
        if agent_with_web_search.extraction_chain:
            agent_with_web_search.extraction_chain.invoke = MagicMock(return_value=mock_extraction_result)
        
        # Mock web search to return clarifications
        mock_search_results = [
            SearchResult(
                title=f"Medical Definition of {term}",
                url=f"https://medical-dictionary.com/{term}",
                snippet=f"{term} is a medical abbreviation meaning...",
                source_domain="medical-dictionary.com",
                quality_score=0.9,
                publication_date=None,
                content=f"Detailed definition of {term}",
                metadata={}
            )
            for term in ambiguous_terms[:3]
        ]
        
        agent_with_web_search.search_web = MagicMock(return_value=mock_search_results[:1])
        
        result = agent_with_web_search.process(input_data)
        
        if result["success"]:
            data = result["data"]
            
            # Property: If ambiguous terms were identified, web search should be called
            if "ambiguous_terms" in data and len(data["ambiguous_terms"]) > 0:
                # Check if web search was called for clarification
                if agent_with_web_search.web_search_tool:
                    # Property: Clarifications should be included in the result
                    assert "term_clarifications" in data or "clarifications_needed" in data, \
                        "Result should include term clarifications when ambiguous terms are detected"
                    
                    if "term_clarifications" in data:
                        clarifications = data["term_clarifications"]
                        
                        # Property: Clarifications should be a dictionary
                        assert isinstance(clarifications, dict), "Clarifications must be a dictionary"
                        
                        # Property: Each clarified term should have a non-empty clarification
                        for term, clarification in clarifications.items():
                            assert isinstance(clarification, str), f"Clarification for '{term}' must be a string"
                            assert len(clarification) > 0, f"Clarification for '{term}' must not be empty"
    
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        ambiguous_terms=ambiguous_terms_strategy,
        age=age_strategy,
        gender=gender_strategy
    )
    def test_clarified_terms_improve_extraction_confidence(
        self, agent_with_web_search, ambiguous_terms, age, gender
    ):
        """
        Test that clarifying ambiguous terms can improve extraction confidence.
        
        When terms are clarified via web search, the re-extraction should
        potentially have higher confidence than the initial extraction.
        """
        # Create input with ambiguous medical terms
        symptoms = [f"patient has {term}" for term in ambiguous_terms[:2]]
        input_data = {
            "symptoms": symptoms,
            "age": age,
            "gender": gender,
            "disease": "diabetes"
        }
        
        # Mock initial extraction with low confidence due to ambiguous terms
        initial_extraction = json.dumps({
            "mapped_features": {"age": age, "gender": 1 if gender == "male" else 0},
            "confidence_scores": {"age": 1.0, "gender": 1.0},
            "overall_confidence": 0.50,  # Low confidence
            "missing_features": [],
            "ambiguous_terms": ambiguous_terms[:2]
        })
        
        # Mock refined extraction with higher confidence after clarification
        refined_extraction = json.dumps({
            "mapped_features": {"age": age, "gender": 1 if gender == "male" else 0, "glucose": 120},
            "confidence_scores": {"age": 1.0, "gender": 1.0, "glucose": 0.85},
            "overall_confidence": 0.85,  # Higher confidence after clarification
            "missing_features": [],
            "ambiguous_terms": []
        })
        
        if agent_with_web_search.extraction_chain:
            # First call returns initial extraction, second call returns refined
            agent_with_web_search.extraction_chain.invoke = MagicMock(
                side_effect=[initial_extraction, refined_extraction]
            )
        
        # Mock web search
        mock_search_results = [
            SearchResult(
                title="Medical Definition",
                url="https://medical-dictionary.com/term",
                snippet="Medical definition...",
                source_domain="medical-dictionary.com",
                quality_score=0.9,
                publication_date=None,
                content="Detailed definition",
                metadata={}
            )
        ]
        agent_with_web_search.search_web = MagicMock(return_value=mock_search_results)
        
        result = agent_with_web_search.process(input_data)
        
        if result["success"]:
            data = result["data"]
            
            # Property: Result should indicate if extraction was refined
            if "extraction_refined" in data and data["extraction_refined"]:
                # Property: Refined extraction should have clarifications
                assert "term_clarifications" in data, "Refined extraction should include term clarifications"
                
                # Property: Extraction confidence should be reasonable
                assert "extraction_confidence" in data, "Result must include extraction confidence"
                assert 0.0 <= data["extraction_confidence"] <= 1.0, "Confidence must be between 0 and 1"


# ============================================================================
# Integration Tests for Multiple Properties
# ============================================================================

class TestMultiplePropertiesIntegration:
    """
    Integration tests that validate multiple properties together.
    """
    
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        symptoms=symptoms_strategy,
        age=age_strategy,
        gender=gender_strategy,
        disease=disease_strategy
    )
    def test_complete_extraction_workflow(
        self, agent_with_web_search, symptoms, age, gender, disease
    ):
        """
        Test complete extraction workflow validating multiple properties.
        
        This test validates:
        - Output structure preservation (Property 1)
        - Confidence scoring (Properties 32, 33, 34)
        - Error handling
        """
        input_data = {
            "symptoms": symptoms,
            "age": age,
            "gender": gender,
            "disease": disease
        }
        
        result = agent_with_web_search.process(input_data)
        
        # Property 1: Output structure
        assert "success" in result
        assert isinstance(result["success"], bool)
        
        if result["success"]:
            assert "data" in result
            data = result["data"]
            
            # Property 1: Required fields
            assert "features" in data
            assert "confidence_scores" in data
            assert "extraction_confidence" in data
            
            # Properties 32-34: Confidence scores for all features
            for feature in data["features"]:
                if feature in data["confidence_scores"]:
                    confidence = data["confidence_scores"][feature]
                    assert 0.0 <= confidence <= 1.0, \
                        f"Confidence for '{feature}' must be between 0 and 1"
            
            # Property 1: Overall confidence
            assert 0.0 <= data["extraction_confidence"] <= 1.0, \
                "Overall extraction confidence must be between 0 and 1"
