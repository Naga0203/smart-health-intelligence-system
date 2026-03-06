"""
Unit tests for ReflectionAgent.

Tests the migrated ReflectionAgent with enhanced capabilities including
self-evaluation, quality assessment, and LangChain integration.

Requirements tested:
- 1.1: Inherits from EnhancedBaseHealthAgent
- 1.2: Uses LangChain chains
- 1.6: Preserves existing functionality
- 5.5: Self-evaluation capabilities
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from agents.reflection import ReflectionAgent
from agents.infrastructure.config import AgentConfig


@pytest.fixture
def reflection_agent():
    """Create a ReflectionAgent instance for testing."""
    config = AgentConfig(
        agent_name="ReflectionAgent",
        enable_web_search=False,
        timeout=30,
        max_retries=2
    )
    
    # Mock the LLM and chains to avoid initialization issues
    with patch('agents.infrastructure.enhanced_base_agent.LangChainGeminiClient') as mock_client:
        mock_llm = MagicMock()
        mock_client.return_value.llm = mock_llm
        
        # Patch the chain creation methods to avoid LLMChain validation errors
        with patch.object(ReflectionAgent, '_create_critique_chain', return_value=MagicMock()):
            with patch.object(ReflectionAgent, '_create_quality_assessment_chain', return_value=MagicMock()):
                agent = ReflectionAgent(config)
                agent.llm = mock_llm  # Ensure LLM is set
                
                return agent


@pytest.fixture
def sample_assessment():
    """Sample assessment for testing."""
    return {
        "prediction": {
            "disease": "Type 2 Diabetes",
            "confidence": "HIGH",
            "probability": 0.85
        },
        "explanation": {
            "summary": "Based on elevated blood glucose levels and symptoms",
            "disclaimer": "This is not a medical diagnosis. Consult a healthcare professional."
        },
        "recommendations": {
            "lifestyle": ["Monitor blood sugar", "Healthy diet", "Regular exercise"],
            "medical": ["Consult endocrinologist"]
        }
    }


@pytest.fixture
def assessment_without_disclaimer():
    """Assessment missing medical disclaimer."""
    return {
        "prediction": {
            "disease": "Hypertension",
            "confidence": "MEDIUM",
            "probability": 0.65
        },
        "explanation": {
            "summary": "Elevated blood pressure readings"
        },
        "recommendations": {
            "lifestyle": ["Reduce sodium intake"]
        }
    }


@pytest.fixture
def inconsistent_assessment():
    """Assessment with inconsistent confidence and probability."""
    return {
        "prediction": {
            "disease": "Influenza",
            "confidence": "LOW",
            "probability": 0.92  # High probability but low confidence
        },
        "explanation": {
            "summary": "Flu-like symptoms present",
            "disclaimer": "Consult a doctor."
        },
        "recommendations": {
            "medical": ["Get tested for flu"]
        }
    }


class TestReflectionAgentInitialization:
    """Test ReflectionAgent initialization."""
    
    def test_initialization_with_config(self):
        """Test agent initializes with custom config."""
        config = AgentConfig(
            agent_name="TestReflection",
            timeout=60,
            max_retries=5,
            enable_web_search=False  # Explicitly set to False
        )
        
        with patch('agents.infrastructure.enhanced_base_agent.LangChainGeminiClient') as mock_client:
            mock_llm = MagicMock()
            mock_client.return_value.llm = mock_llm
            
            with patch.object(ReflectionAgent, '_create_critique_chain', return_value=MagicMock()):
                with patch.object(ReflectionAgent, '_create_quality_assessment_chain', return_value=MagicMock()):
                    agent = ReflectionAgent(config)
                    
                    assert agent.agent_name == "ReflectionAgent"  # Name is overridden
                    assert agent.config.timeout == 60
                    assert agent.config.max_retries == 5
                    # Config is overridden in __init__, so check the actual value
                    assert agent.config.enable_web_search is False
    
    def test_initialization_without_config(self):
        """Test agent initializes with default config."""
        with patch('agents.infrastructure.enhanced_base_agent.LangChainGeminiClient') as mock_client:
            mock_llm = MagicMock()
            mock_client.return_value.llm = mock_llm
            
            with patch.object(ReflectionAgent, '_create_critique_chain', return_value=MagicMock()):
                with patch.object(ReflectionAgent, '_create_quality_assessment_chain', return_value=MagicMock()):
                    agent = ReflectionAgent()
                    
                    assert agent.agent_name == "ReflectionAgent"
                    assert agent.config.agent_name == "ReflectionAgent"
                    assert agent.config.enable_web_search is False
                    assert agent.llm is not None
    
    def test_chains_created(self, reflection_agent):
        """Test that LangChain chains are created."""
        assert reflection_agent.critique_chain is not None
        assert reflection_agent.quality_assessment_chain is not None


class TestReflectionAgentProcess:
    """Test ReflectionAgent process method."""
    
    def test_process_valid_assessment(self, reflection_agent, sample_assessment):
        """Test processing a valid assessment."""
        with patch.object(reflection_agent, '_generate_critique') as mock_critique:
            mock_critique.return_value = {
                "is_safe": True,
                "consistency_score": 9,
                "issues": [],
                "suggested_improvements": [],
                "severity": "low"
            }
            
            with patch.object(reflection_agent, '_evaluate_critique_quality') as mock_quality:
                mock_quality.return_value = {
                    "quality_score": 8,
                    "confidence": 0.85,
                    "strengths": ["Thorough review"],
                    "weaknesses": []
                }
                
                result = reflection_agent.process({"assessment": sample_assessment})
                
                assert result["success"] is True
                assert result["data"]["reviewed"] is True
                assert "critique" in result["data"]
                assert "quality_assessment" in result["data"]
                assert result["data"]["critique"]["is_safe"] is True
    
    def test_process_insufficient_data(self, reflection_agent):
        """Test processing with insufficient data falls back to heuristic."""
        result = reflection_agent.process({"assessment": {}})
        
        # Falls back to heuristic check, which returns success=True
        assert result["success"] is True
        assert result["data"]["method"] == "heuristic"
    
    def test_process_missing_disease(self, reflection_agent):
        """Test processing assessment without disease falls back to heuristic."""
        assessment = {
            "prediction": {},
            "explanation": {"summary": "Some text"}
        }
        
        result = reflection_agent.process({"assessment": assessment})
        
        # Falls back to heuristic check
        assert result["success"] is True
        assert result["data"]["method"] == "heuristic"
    
    def test_process_with_retry_on_failure(self, reflection_agent, sample_assessment):
        """Test that process retries on failure."""
        call_count = 0
        
        def mock_critique(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return {
                "is_safe": True,
                "issues": [],
                "severity": "low"
            }
        
        with patch.object(reflection_agent, '_generate_critique', side_effect=mock_critique):
            with patch.object(reflection_agent, '_evaluate_critique_quality') as mock_quality:
                mock_quality.return_value = {"quality_score": 7, "confidence": 0.7}
                
                result = reflection_agent.process({"assessment": sample_assessment})
                
                assert call_count == 2  # Should retry once
                assert result["success"] is True
    
    def test_process_fallback_to_heuristic(self, reflection_agent, sample_assessment):
        """Test fallback to heuristic check when LLM fails."""
        with patch.object(reflection_agent, '_generate_critique', return_value=None):
            result = reflection_agent.process({"assessment": sample_assessment})
            
            assert result["success"] is True
            assert result["data"]["method"] == "heuristic"
            assert "quality_assessment" in result["data"]


class TestReflectionAgentVerifyAssessment:
    """Test verify_assessment method (public API)."""
    
    def test_verify_safe_assessment(self, reflection_agent, sample_assessment):
        """Test verifying a safe assessment."""
        with patch.object(reflection_agent, 'process') as mock_process:
            mock_process.return_value = {
                "success": True,
                "data": {
                    "reviewed": True,
                    "critique": {
                        "is_safe": True,
                        "issues": [],
                        "severity": "low"
                    },
                    "quality_assessment": {
                        "quality_score": 8,
                        "confidence": 0.8
                    }
                }
            }
            
            result = reflection_agent.verify_assessment(sample_assessment)
            
            assert result["severity"] == "low"
            assert result["issue_count"] == 0
            assert result["recommended_action"] == "proceed"
            assert result["quality_score"] == 8
            assert result["confidence"] == 0.8
    
    def test_verify_unsafe_assessment(self, reflection_agent, sample_assessment):
        """Test verifying an unsafe assessment."""
        with patch.object(reflection_agent, 'process') as mock_process:
            mock_process.return_value = {
                "success": True,
                "data": {
                    "reviewed": True,
                    "critique": {
                        "is_safe": False,
                        "issues": ["Missing emergency warning"],
                        "severity": "critical"
                    },
                    "quality_assessment": {
                        "quality_score": 9,
                        "confidence": 0.9
                    }
                }
            }
            
            result = reflection_agent.verify_assessment(sample_assessment)
            
            assert result["severity"] == "critical"
            assert result["issue_count"] == 1
            assert result["recommended_action"] == "revise"
    
    def test_verify_assessment_with_multiple_issues(self, reflection_agent, sample_assessment):
        """Test verifying assessment with multiple issues."""
        with patch.object(reflection_agent, 'process') as mock_process:
            mock_process.return_value = {
                "success": True,
                "data": {
                    "reviewed": True,
                    "critique": {
                        "is_safe": True,
                        "issues": ["Issue 1", "Issue 2", "Issue 3"],
                        "severity": "low"
                    },
                    "quality_assessment": {
                        "quality_score": 6,
                        "confidence": 0.7
                    }
                }
            }
            
            result = reflection_agent.verify_assessment(sample_assessment)
            
            assert result["severity"] == "medium"  # Upgraded due to issue count
            assert result["issue_count"] == 3
    
    def test_verify_assessment_process_failure(self, reflection_agent, sample_assessment):
        """Test verify when process fails."""
        with patch.object(reflection_agent, 'process') as mock_process:
            mock_process.return_value = {
                "success": False,
                "message": "Processing failed"
            }
            
            result = reflection_agent.verify_assessment(sample_assessment)
            
            assert result["severity"] == "low"
            assert result["issue_count"] == 0
            assert "error" in result


class TestReflectionAgentHeuristicCheck:
    """Test heuristic check functionality."""
    
    def test_heuristic_detects_missing_disclaimer(self, reflection_agent, assessment_without_disclaimer):
        """Test heuristic check detects missing disclaimer."""
        result = reflection_agent._perform_heuristic_check(assessment_without_disclaimer)
        
        assert result["success"] is True
        assert result["data"]["method"] == "heuristic"
        assert "Missing medical disclaimer" in result["data"]["critique"]["issues"]
    
    def test_heuristic_detects_inconsistent_confidence(self, reflection_agent, inconsistent_assessment):
        """Test heuristic check detects inconsistent confidence."""
        result = reflection_agent._perform_heuristic_check(inconsistent_assessment)
        
        assert result["success"] is True
        issues = result["data"]["critique"]["issues"]
        assert any("Inconsistent" in issue for issue in issues)
    
    def test_heuristic_passes_valid_assessment(self, reflection_agent, sample_assessment):
        """Test heuristic check passes valid assessment."""
        result = reflection_agent._perform_heuristic_check(sample_assessment)
        
        assert result["success"] is True
        assert len(result["data"]["critique"]["issues"]) == 0
        assert result["data"]["critique"]["consistency_score"] == 7
    
    def test_heuristic_includes_quality_assessment(self, reflection_agent, sample_assessment):
        """Test heuristic check includes self-evaluation."""
        result = reflection_agent._perform_heuristic_check(sample_assessment)
        
        assert "quality_assessment" in result["data"]
        quality = result["data"]["quality_assessment"]
        assert "quality_score" in quality
        assert "confidence" in quality
        assert quality["quality_score"] == 3  # Lower for heuristic


class TestReflectionAgentSafetyGuardrails:
    """Test safety guardrails integration."""
    
    def test_safety_guardrails_applied_to_improvements(self, reflection_agent, sample_assessment):
        """Test safety guardrails are applied to suggested improvements."""
        with patch.object(reflection_agent, '_generate_critique') as mock_critique:
            mock_critique.return_value = {
                "is_safe": True,
                "issues": [],
                "suggested_improvements": [
                    "Add more detail about treatment",
                    "Include dosage information"
                ],
                "severity": "low"
            }
            
            with patch.object(reflection_agent, '_evaluate_critique_quality') as mock_quality:
                mock_quality.return_value = {"quality_score": 7, "confidence": 0.7}
                
                with patch.object(reflection_agent, 'apply_safety_guardrails') as mock_safety:
                    mock_safety.side_effect = lambda x: f"SAFE: {x}"
                    
                    result = reflection_agent.process({"assessment": sample_assessment})
                    
                    improvements = result["data"]["critique"]["suggested_improvements"]
                    assert all(imp.startswith("SAFE:") for imp in improvements)
                    assert mock_safety.call_count == 2


class TestReflectionAgentMonitoring:
    """Test monitoring and logging."""
    
    def test_execution_tracked(self, reflection_agent, sample_assessment):
        """Test that execution is tracked in monitoring."""
        with patch.object(reflection_agent, '_generate_critique') as mock_critique:
            mock_critique.return_value = {
                "is_safe": True,
                "issues": [],
                "severity": "low"
            }
            
            with patch.object(reflection_agent, '_evaluate_critique_quality') as mock_quality:
                mock_quality.return_value = {"quality_score": 8, "confidence": 0.8}
                
                with patch.object(reflection_agent, 'log_agent_action') as mock_log:
                    result = reflection_agent.process({"assessment": sample_assessment})
                    
                    # Should log at least critique_assessment
                    assert mock_log.call_count >= 1
                    # Check that critique_assessment was logged
                    assert any('critique_assessment' in str(call) for call in mock_log.call_args_list)
    
    def test_response_format_standardized(self, reflection_agent, sample_assessment):
        """Test that response follows standardized format."""
        with patch.object(reflection_agent, '_generate_critique') as mock_critique:
            mock_critique.return_value = {
                "is_safe": True,
                "issues": [],
                "severity": "low"
            }
            
            with patch.object(reflection_agent, '_evaluate_critique_quality') as mock_quality:
                mock_quality.return_value = {"quality_score": 8, "confidence": 0.8}
                
                result = reflection_agent.process({"assessment": sample_assessment})
                
                # Check standardized response format
                assert "success" in result
                assert "agent" in result
                assert "timestamp" in result
                assert "version" in result
                assert result["agent"] == "ReflectionAgent"
                assert result["version"] == "enhanced"


class TestReflectionAgentEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_assessment(self, reflection_agent):
        """Test handling empty assessment falls back to heuristic."""
        result = reflection_agent.process({"assessment": {}})
        
        # Falls back to heuristic check
        assert result["success"] is True
        assert result["data"]["method"] == "heuristic"
    
    def test_malformed_assessment(self, reflection_agent):
        """Test handling malformed assessment."""
        result = reflection_agent.process({"assessment": "not a dict"})
        
        # Should handle gracefully
        assert "success" in result
    
    def test_none_assessment(self, reflection_agent):
        """Test handling None assessment."""
        result = reflection_agent.process({"assessment": None})
        
        assert result["success"] is False
    
    def test_exception_during_critique(self, reflection_agent, sample_assessment):
        """Test handling exception during critique generation."""
        with patch.object(reflection_agent, '_generate_critique', side_effect=Exception("Test error")):
            # Should exhaust retries and return error
            result = reflection_agent.process({"assessment": sample_assessment})
            
            assert result["success"] is False
            assert "error" in result["metadata"]
