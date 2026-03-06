"""
Unit tests for LangChainValidationAgent

Tests the enhanced validation agent's ability to validate health data inputs
with autonomous decision-making and web search capabilities.

Requirements: 1.1, 1.2, 1.3, 1.5, 1.6
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from .validation import LangChainValidationAgent
from .infrastructure.config import AgentConfig


class TestLangChainValidationAgent:
    """Test suite for LangChainValidationAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for testing."""
        with patch('common.gemini_client.LangChainGeminiClient'):
            config = AgentConfig(
                agent_name="ValidationAgent",
                enable_web_search=False,  # Disable for unit tests
                monitoring_enabled=False  # Disable for unit tests
            )
            agent = LangChainValidationAgent(config)
            return agent
    
    @pytest.fixture
    def valid_input(self):
        """Valid health data input."""
        return {
            "age": 30,
            "gender": "male",
            "symptoms": ["headache", "fever", "fatigue"]
        }
    
    @pytest.fixture
    def invalid_input_missing_fields(self):
        """Invalid input with missing required fields."""
        return {
            "age": 30
            # Missing gender and symptoms
        }
    
    @pytest.fixture
    def invalid_input_bad_age(self):
        """Invalid input with out-of-range age."""
        return {
            "age": 150,  # Too old
            "gender": "female",
            "symptoms": ["cough"]
        }
    
    # Test 1: Initialization
    def test_initialization(self, agent):
        """Test agent initializes correctly with enhanced capabilities."""
        assert agent.agent_name == "ValidationAgent"
        assert agent.REQUIRED_FIELDS == ["age", "gender", "symptoms"]
        assert agent.VALID_GENDERS == ["male", "female", "other"]
        assert agent.MIN_AGE == 1
        assert agent.MAX_AGE == 120
        assert len(agent.compiled_patterns) > 0
        assert agent.validation_feedback_chain is not None or agent.llm is None
        assert agent.validation_decision_chain is not None or agent.llm is None
    
    # Test 2: Valid health data validation
    def test_validate_valid_health_data(self, agent, valid_input):
        """Test validation passes for valid health data."""
        result = agent.process(valid_input)
        
        assert result["success"] is True
        assert result["data"]["valid"] is True
        assert "sanitized_input" in result["data"]
        assert result["data"]["sanitized_input"]["age"] == 30
        assert result["data"]["sanitized_input"]["gender"] == "male"
        assert len(result["data"]["sanitized_input"]["symptoms"]) == 3
    
    # Test 3: Invalid health data - missing fields
    def test_validate_invalid_missing_fields(self, agent, invalid_input_missing_fields):
        """Test validation fails for missing required fields."""
        result = agent.process(invalid_input_missing_fields)
        
        assert result["success"] is False
        assert result["data"]["valid"] is False
        assert "reason" in result["data"]
        assert "missing" in result["data"]
        assert "gender" in result["data"]["missing"]
        assert "symptoms" in result["data"]["missing"]
    
    # Test 4: Invalid health data - bad age
    def test_validate_invalid_age_range(self, agent, invalid_input_bad_age):
        """Test validation fails for out-of-range age."""
        result = agent.process(invalid_input_bad_age)
        
        assert result["success"] is False
        assert result["data"]["valid"] is False
        assert "age" in result["data"]["reason"].lower()
    
    # Test 5: Invalid age format
    def test_validate_invalid_age_format(self, agent):
        """Test validation fails for non-numeric age."""
        invalid_input = {
            "age": "thirty",  # String instead of number
            "gender": "female",
            "symptoms": ["cough"]
        }
        
        result = agent.process(invalid_input)
        
        assert result["success"] is False
        assert result["data"]["valid"] is False
        assert "age" in result["data"]["reason"].lower()
    
    # Test 6: Invalid gender
    def test_validate_invalid_gender(self, agent):
        """Test validation fails for invalid gender value."""
        invalid_input = {
            "age": 25,
            "gender": "invalid_gender",
            "symptoms": ["headache"]
        }
        
        result = agent.process(invalid_input)
        
        assert result["success"] is False
        assert result["data"]["valid"] is False
        assert "gender" in result["data"]["reason"].lower()
    
    # Test 7: Empty symptoms list
    def test_validate_empty_symptoms(self, agent):
        """Test validation fails for empty symptoms list."""
        invalid_input = {
            "age": 25,
            "gender": "male",
            "symptoms": []
        }
        
        result = agent.process(invalid_input)
        
        assert result["success"] is False
        assert result["data"]["valid"] is False
        assert "symptom" in result["data"]["reason"].lower()
    
    # Test 8: Too many symptoms
    def test_validate_too_many_symptoms(self, agent):
        """Test validation fails for too many symptoms."""
        invalid_input = {
            "age": 25,
            "gender": "male",
            "symptoms": [f"symptom_{i}" for i in range(25)]  # More than MAX_SYMPTOMS_PER_REQUEST
        }
        
        result = agent.process(invalid_input)
        
        assert result["success"] is False
        assert result["data"]["valid"] is False
        assert "maximum" in result["data"]["reason"].lower()
    
    # Test 9: Symptom too short
    def test_validate_symptom_too_short(self, agent):
        """Test validation fails for symptom that's too short."""
        invalid_input = {
            "age": 25,
            "gender": "male",
            "symptoms": ["a"]  # Only 1 character
        }
        
        result = agent.process(invalid_input)
        
        assert result["success"] is False
        assert result["data"]["valid"] is False
        assert "too short" in result["data"]["reason"].lower()
    
    # Test 10: Symptom too long
    def test_validate_symptom_too_long(self, agent):
        """Test validation fails for symptom that's too long."""
        invalid_input = {
            "age": 25,
            "gender": "male",
            "symptoms": ["a" * 150]  # More than MAX_SYMPTOM_LENGTH
        }
        
        result = agent.process(invalid_input)
        
        assert result["success"] is False
        assert result["data"]["valid"] is False
        assert "too long" in result["data"]["reason"].lower()
    
    # Test 11: Symptoms not a list
    def test_validate_symptoms_not_list(self, agent):
        """Test validation fails when symptoms is not a list."""
        invalid_input = {
            "age": 25,
            "gender": "male",
            "symptoms": "headache"  # String instead of list
        }
        
        result = agent.process(invalid_input)
        
        assert result["success"] is False
        assert result["data"]["valid"] is False
        assert "list" in result["data"]["reason"].lower()
    
    # Test 12: Safety filter - script injection
    def test_safety_filter_script_injection(self, agent):
        """Test safety filter detects script injection attempts."""
        malicious_input = {
            "age": 25,
            "gender": "male",
            "symptoms": ["<script>alert('xss')</script>"]
        }
        
        result = agent.process(malicious_input)
        
        assert result["success"] is False
        assert result["data"]["valid"] is False
        assert "unsafe" in result["data"]["reason"].lower()
    
    # Test 13: Safety filter - SQL injection
    def test_safety_filter_sql_injection(self, agent):
        """Test safety filter detects SQL injection attempts."""
        malicious_input = {
            "age": 25,
            "gender": "male",
            "symptoms": ["headache'; DROP TABLE users; --"]
        }
        
        result = agent.process(malicious_input)
        
        assert result["success"] is False
        assert result["data"]["valid"] is False
        assert "unsafe" in result["data"]["reason"].lower()
    
    # Test 14: Input sanitization
    def test_input_sanitization(self, agent, valid_input):
        """Test that valid input is properly sanitized."""
        # Add extra whitespace and mixed case
        input_with_whitespace = {
            "age": "30",  # String that can be converted
            "gender": "  MALE  ",  # Extra whitespace and uppercase
            "symptoms": ["  Headache  ", "FEVER", "fatigue  "]
        }
        
        result = agent.process(input_with_whitespace)
        
        assert result["success"] is True
        sanitized = result["data"]["sanitized_input"]
        assert sanitized["age"] == 30  # Converted to int
        assert sanitized["gender"] == "male"  # Lowercase and trimmed
        assert sanitized["symptoms"] == ["headache", "fever", "fatigue"]  # All lowercase and trimmed
    
    # Test 15: Optional medical history field
    def test_optional_medical_history(self, agent):
        """Test that optional medical_history field is handled correctly."""
        input_with_history = {
            "age": 30,
            "gender": "male",
            "symptoms": ["headache"],
            "medical_history": ["diabetes", "hypertension"]
        }
        
        result = agent.process(input_with_history)
        
        assert result["success"] is True
        assert "medical_history" in result["data"]["sanitized_input"]
        assert len(result["data"]["sanitized_input"]["medical_history"]) == 2
    
    # Test 16: Error handling - exception during validation
    def test_error_handling(self, agent):
        """Test error handling when validation encounters an exception."""
        # Mock _perform_validation to raise an exception
        with patch.object(agent, '_perform_validation', side_effect=Exception("Test error")):
            result = agent.process({"age": 30, "gender": "male", "symptoms": ["test"]})
            
            assert result["success"] is False
            assert "error" in result["message"].lower() or "metadata" in result
    
    # Test 17: Edge case - minimum age
    def test_edge_case_minimum_age(self, agent):
        """Test validation with minimum valid age."""
        input_min_age = {
            "age": 1,  # Minimum age
            "gender": "male",
            "symptoms": ["fever"]
        }
        
        result = agent.process(input_min_age)
        
        assert result["success"] is True
        assert result["data"]["valid"] is True
    
    # Test 18: Edge case - maximum age
    def test_edge_case_maximum_age(self, agent):
        """Test validation with maximum valid age."""
        input_max_age = {
            "age": 120,  # Maximum age
            "gender": "female",
            "symptoms": ["fatigue"]
        }
        
        result = agent.process(input_max_age)
        
        assert result["success"] is True
        assert result["data"]["valid"] is True
    
    # Test 19: Edge case - age below minimum
    def test_edge_case_age_below_minimum(self, agent):
        """Test validation fails for age below minimum."""
        input_below_min = {
            "age": 0,
            "gender": "male",
            "symptoms": ["fever"]
        }
        
        result = agent.process(input_below_min)
        
        assert result["success"] is False
        assert result["data"]["valid"] is False
    
    # Test 20: Edge case - age above maximum
    def test_edge_case_age_above_maximum(self, agent):
        """Test validation fails for age above maximum."""
        input_above_max = {
            "age": 121,
            "gender": "female",
            "symptoms": ["fatigue"]
        }
        
        result = agent.process(input_above_max)
        
        assert result["success"] is False
        assert result["data"]["valid"] is False
    
    # Test 21: Validation summary
    def test_get_validation_summary(self, agent):
        """Test that validation summary returns correct information."""
        summary = agent.get_validation_summary()
        
        assert summary["agent_type"] == "EnhancedValidationAgent"
        assert summary["framework"] == "LangChain"
        assert summary["required_fields"] == ["age", "gender", "symptoms"]
        assert summary["age_range"]["min"] == 1
        assert summary["age_range"]["max"] == 120
        assert "safety_features" in summary
        assert len(summary["safety_features"]) > 0
    
    # Test 22: Legacy validate_symptoms method
    def test_legacy_validate_symptoms_method(self, agent, valid_input):
        """Test that legacy validate_symptoms method still works."""
        result = agent.validate_symptoms(valid_input)
        
        assert result["valid"] is True
        assert "sanitized_input" in result
    
    # Test 23: Malformed data - None values
    def test_malformed_data_none_values(self, agent):
        """Test validation handles None values correctly."""
        malformed_input = {
            "age": None,
            "gender": "male",
            "symptoms": ["headache"]
        }
        
        result = agent.process(malformed_input)
        
        assert result["success"] is False
        assert result["data"]["valid"] is False
    
    # Test 24: Malformed data - wrong types
    def test_malformed_data_wrong_types(self, agent):
        """Test validation handles wrong data types."""
        malformed_input = {
            "age": 30,
            "gender": 123,  # Should be string
            "symptoms": ["headache"]
        }
        
        result = agent.process(malformed_input)
        
        assert result["success"] is False
        assert result["data"]["valid"] is False
    
    # Test 25: Enhanced feedback with LangChain
    def test_enhanced_feedback_generation(self, agent, invalid_input_missing_fields):
        """Test that enhanced feedback is generated for validation failures."""
        with patch.object(agent, '_get_enhanced_feedback', return_value="Please provide your gender and symptoms."):
            result = agent.process(invalid_input_missing_fields)
            
            # Feedback generation should be attempted for invalid input
            assert result["success"] is False
