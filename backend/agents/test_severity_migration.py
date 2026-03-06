"""
Test for SeverityAgent migration to enhanced base agent.

Validates that the migrated agent:
- Maintains backward compatibility with legacy calculate() method
- Provides enhanced functionality through process() method
- Integrates with LangChain and infrastructure components
"""

import pytest
from typing import Dict, List
from .severity import SeverityScoringAgent
from .infrastructure.config import AgentConfig


class TestSeverityAgentMigration:
    """Test suite for SeverityAgent migration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = SeverityScoringAgent()
        
        self.test_symptoms = [
            "fever",
            "cough",
            "fatigue"
        ]
        
        self.test_profile = {
            "age": 45,
            "temperature": 38.5,
            "past_health_conditions": ["diabetes", "hypertension"]
        }
        
        self.test_probability = 0.8
    
    def test_agent_initialization(self):
        """Test that agent initializes with enhanced capabilities."""
        assert self.agent.agent_name == "SeverityAgent"
        assert self.agent.llm is not None
        assert self.agent.decision_engine is not None
        assert self.agent.circuit_breaker is not None
        assert self.agent.context_manager is not None
        assert self.agent.safety_guardrails is not None
    
    def test_legacy_calculate_method(self):
        """Test backward compatibility with legacy calculate() method."""
        result = self.agent.calculate(
            symptoms=self.test_symptoms,
            probability=self.test_probability,
            profile=self.test_profile
        )
        
        # Verify legacy interface
        assert "severity_score" in result
        assert "severity_level" in result
        assert isinstance(result["severity_score"], int)
        assert result["severity_level"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]
    
    def test_legacy_scoring_logic(self):
        """Test that original scoring logic is preserved."""
        # Test with minimal input
        result = self.agent.calculate(
            symptoms=["headache"],
            probability=0.3,
            profile={"age": 30, "past_health_conditions": []}
        )
        
        # Score should be: 1 (symptom count) = 1
        assert result["severity_score"] == 1
        assert result["severity_level"] == "LOW"
    
    def test_critical_symptom_detection(self):
        """Test that critical symptoms increase severity score."""
        critical_symptoms = ["chest pain", "shortness of breath"]
        
        result = self.agent.calculate(
            symptoms=critical_symptoms,
            probability=0.5,
            profile={"age": 60, "past_health_conditions": []}
        )
        
        # Score should be: 2 (symptoms) + 4 (chest pain) + 4 (shortness of breath) = 10
        assert result["severity_score"] >= 10
        assert result["severity_level"] in ["HIGH", "CRITICAL"]
    
    def test_temperature_scoring(self):
        """Test temperature-based severity scoring."""
        # High fever (>= 40)
        result_high = self.agent.calculate(
            symptoms=["fever"],
            probability=0.5,
            profile={"age": 30, "temperature": 40.5, "past_health_conditions": []}
        )
        
        # Moderate fever (>= 39)
        result_moderate = self.agent.calculate(
            symptoms=["fever"],
            probability=0.5,
            profile={"age": 30, "temperature": 39.2, "past_health_conditions": []}
        )
        
        # High fever should score higher
        assert result_high["severity_score"] > result_moderate["severity_score"]
    
    def test_enhanced_process_method(self):
        """Test enhanced process() method with new capabilities."""
        input_data = {
            "symptoms": self.test_symptoms,
            "probability": self.test_probability,
            "profile": self.test_profile
        }
        
        result = self.agent.process(input_data)
        
        # Verify enhanced response format
        assert result["success"] is True
        assert "data" in result
        assert "agent" in result
        assert "timestamp" in result
        
        # Verify data contains severity assessment
        data = result["data"]
        assert "severity_score" in data
        assert "severity_level" in data
        assert "assessment_timestamp" in data
        assert data["agent"] == "EnhancedSeverityAgent"
    
    def test_critical_symptoms_detection_enhanced(self):
        """Test enhanced critical symptom detection."""
        input_data = {
            "symptoms": ["severe chest pain", "difficulty breathing"],
            "probability": 0.9,
            "profile": {"age": 65, "past_health_conditions": ["heart disease"]}
        }
        
        result = self.agent.process(input_data)
        
        assert result["success"] is True
        data = result["data"]
        
        # Should detect critical symptoms
        assert "critical_symptoms_detected" in data
        assert len(data["critical_symptoms_detected"]) > 0
        assert data["severity_level"] in ["HIGH", "CRITICAL"]
    
    def test_emergency_indicator_detection(self):
        """Test emergency indicator detection and escalation."""
        input_data = {
            "symptoms": ["severe chest pain", "loss of consciousness"],
            "probability": 0.95,
            "profile": {"age": 70, "temperature": 40, "past_health_conditions": ["diabetes"]}
        }
        
        result = self.agent.process(input_data)
        
        assert result["success"] is True
        data = result["data"]
        
        # Should detect emergency
        assert "emergency_indicators" in data
        assert "requires_immediate_attention" in data
        assert data["requires_immediate_attention"] is True
    
    def test_agent_status(self):
        """Test agent status reporting."""
        status = self.agent.get_agent_status()
        
        assert status["agent_name"] == "SeverityAgent"
        assert "llm_available" in status
        assert "web_search_enabled" in status
        assert "monitoring_enabled" in status
        assert "circuit_breaker_state" in status
        assert status["framework"] == "LangChain"
        assert status["version"] == "enhanced"
    
    def test_severity_thresholds(self):
        """Test severity level thresholds."""
        # Test CRITICAL threshold (>= 12)
        result_critical = self.agent.calculate(
            symptoms=["chest pain", "shortness of breath", "severe headache"],
            probability=0.9,
            profile={"age": 70, "temperature": 40, "past_health_conditions": ["heart disease", "diabetes"]}
        )
        assert result_critical["severity_level"] == "CRITICAL"
        
        # Test LOW threshold (< 4)
        result_low = self.agent.calculate(
            symptoms=["mild headache"],
            probability=0.2,
            profile={"age": 25, "past_health_conditions": []}
        )
        assert result_low["severity_level"] == "LOW"
    
    def test_error_handling(self):
        """Test error handling with invalid input."""
        # Test with missing required fields
        result = self.agent.process({})
        
        # Should handle gracefully
        assert "success" in result
        # May succeed with defaults or fail gracefully
    
    def test_monitoring_integration(self):
        """Test that monitoring is integrated."""
        input_data = {
            "symptoms": self.test_symptoms,
            "probability": self.test_probability,
            "profile": self.test_profile
        }
        
        # Process should track execution
        result = self.agent.process(input_data)
        
        # Verify monitoring is available
        assert self.agent.monitoring is not None or self.agent.config.monitoring_enabled is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
