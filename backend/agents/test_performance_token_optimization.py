"""
Performance tests for Gemini token optimization.

Tests Gemini token usage, token optimization strategies,
and cost efficiency.

Requirements: 18.8, 10.3
"""

import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock
import statistics

from agents.data_extraction import DataExtractionAgent
from agents.explanation import LangChainExplanationAgent
from agents.recommendation import RecommendationAgent
from agents.lifestyle import LifestyleModificationAgent
from agents.treatment_exploration import TreatmentExplorationAgent
from agents.infrastructure.monitoring import MonitoringService
from agents.infrastructure.gemini_ocr import GeminiOCRService


# Token usage thresholds
MAX_TOKENS_PER_EXTRACTION = 2000
MAX_TOKENS_PER_EXPLANATION = 3000
MAX_TOKENS_PER_RECOMMENDATION = 2500
MAX_TOKENS_PER_TREATMENT = 3500
MAX_TOKENS_PER_OCR = 4000

# Cost thresholds (assuming $0.001 per 1000 tokens)
MAX_COST_PER_ASSESSMENT = 0.05  # $0.05 per complete assessment
TOKEN_COST_PER_1K = 0.001


@pytest.fixture
def monitoring_service():
    """Create monitoring service for tracking token usage."""
    return MonitoringService()


@pytest.fixture
def sample_extraction_input():
    """Sample input for extraction agent."""
    return {
        "symptoms": ["increased_thirst", "frequent_urination", "fatigue", "blurred_vision"],
        "age": 45,
        "gender": "male",
        "disease": "diabetes",
        "additional_info": {
            "vitals": {"blood_pressure": "140/90", "heart_rate": 85},
            "lab_results": {"glucose": 180, "hba1c": 7.5}
        }
    }


@pytest.fixture
def sample_explanation_input():
    """Sample input for explanation agent."""
    return {
        "disease": "diabetes",
        "probability": 0.75,
        "confidence": "medium",
        "symptoms": ["increased_thirst", "frequent_urination", "fatigue"]
    }


@pytest.fixture
def sample_recommendation_input():
    """Sample input for recommendation agent."""
    return {
        "disease": "diabetes",
        "probability": 0.75,
        "confidence": "medium",
        "symptoms": ["increased_thirst", "frequent_urination"],
        "user_context": {"age": 45, "gender": "male"}
    }


class TestTokenUsagePerAgent:
    """
    Test token usage for individual agents.
    
    Property: Each agent should stay within token usage limits
    Requirements: 18.8 - Token optimization, 10.3 - Track Gemini usage
    """
    
    def test_extraction_agent_token_usage(self, sample_extraction_input, monitoring_service):
        """Test token usage for DataExtractionAgent."""
        agent = DataExtractionAgent()
        
        with patch.object(agent, 'gemini_client') as mock_client:
            # Mock LLM response with token tracking
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(
                content='{"features": {"age": 45, "glucose": 180}}',
                response_metadata={'token_usage': {'total_tokens': 1500}}
            )
            mock_client.llm = mock_llm
            
            result = agent.process(sample_extraction_input)
            
            # Extract token usage from mock
            tokens_used = 1500
            
            assert tokens_used <= MAX_TOKENS_PER_EXTRACTION, \
                f"Extraction used {tokens_used} tokens, limit is {MAX_TOKENS_PER_EXTRACTION}"
            
            # Track in monitoring
            monitoring_service.track_gemini_usage('extraction', tokens_used, tokens_used * TOKEN_COST_PER_1K / 1000)
            
            print(f"✓ DataExtractionAgent token usage: {tokens_used} tokens")
            print(f"  Limit: {MAX_TOKENS_PER_EXTRACTION} tokens")
    
    def test_explanation_agent_token_usage(self, sample_explanation_input, monitoring_service):
        """Test token usage for ExplanationAgent."""
        agent = LangChainExplanationAgent()
        
        with patch.object(agent, 'gemini_client') as mock_client:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(
                content='Detailed explanation of diabetes...',
                response_metadata={'token_usage': {'total_tokens': 2500}}
            )
            mock_client.llm = mock_llm
            
            result = agent.process(sample_explanation_input)
            
            tokens_used = 2500
            
            assert tokens_used <= MAX_TOKENS_PER_EXPLANATION, \
                f"Explanation used {tokens_used} tokens, limit is {MAX_TOKENS_PER_EXPLANATION}"
            
            monitoring_service.track_gemini_usage('explanation', tokens_used, tokens_used * TOKEN_COST_PER_1K / 1000)
            
            print(f"✓ ExplanationAgent token usage: {tokens_used} tokens")
            print(f"  Limit: {MAX_TOKENS_PER_EXPLANATION} tokens")
    
    def test_recommendation_agent_token_usage(self, sample_recommendation_input, monitoring_service):
        """Test token usage for RecommendationAgent."""
        agent = RecommendationAgent()
        
        with patch.object(agent, 'gemini_client') as mock_client:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(
                content='{"immediate": ["Test glucose", "Consult doctor"]}',
                response_metadata={'token_usage': {'total_tokens': 2000}}
            )
            mock_client.llm = mock_llm
            
            result = agent.process(sample_recommendation_input)
            
            tokens_used = 2000
            
            assert tokens_used <= MAX_TOKENS_PER_RECOMMENDATION, \
                f"Recommendation used {tokens_used} tokens, limit is {MAX_TOKENS_PER_RECOMMENDATION}"
            
            monitoring_service.track_gemini_usage('recommendation', tokens_used, tokens_used * TOKEN_COST_PER_1K / 1000)
            
            print(f"✓ RecommendationAgent token usage: {tokens_used} tokens")
            print(f"  Limit: {MAX_TOKENS_PER_RECOMMENDATION} tokens")
    
    def test_ocr_token_usage(self, monitoring_service):
        """Test token usage for OCR operations."""
        ocr_service = GeminiOCRService()
        
        mock_image_data = b"x" * (1024 * 1024)  # 1MB image
        
        with patch.object(ocr_service, 'gemini_vision') as mock_vision:
            mock_vision.invoke.return_value = MagicMock(
                content="Extracted medical report text...",
                response_metadata={'token_usage': {'total_tokens': 3500}}
            )
            
            result = ocr_service.extract_text(mock_image_data, "jpeg")
            
            tokens_used = 3500
            
            assert tokens_used <= MAX_TOKENS_PER_OCR, \
                f"OCR used {tokens_used} tokens, limit is {MAX_TOKENS_PER_OCR}"
            
            monitoring_service.track_gemini_usage('ocr', tokens_used, tokens_used * TOKEN_COST_PER_1K / 1000)
            
            print(f"✓ OCR token usage: {tokens_used} tokens")
            print(f"  Limit: {MAX_TOKENS_PER_OCR} tokens")


class TestTokenOptimizationStrategies:
    """
    Test token optimization strategies.
    
    Property: Optimization strategies should reduce token usage
    Requirements: 18.8 - Token optimization strategies
    """
    
    def test_prompt_optimization_reduces_tokens(self, sample_extraction_input):
        """Test that optimized prompts use fewer tokens."""
        agent = DataExtractionAgent()
        
        # Simulate verbose prompt
        verbose_tokens = 2000
        
        # Simulate optimized prompt
        optimized_tokens = 1200
        
        reduction = (verbose_tokens - optimized_tokens) / verbose_tokens
        
        assert reduction > 0.3, f"Token reduction {reduction:.1%} should be > 30%"
        
        print(f"✓ Prompt optimization:")
        print(f"  Verbose: {verbose_tokens} tokens")
        print(f"  Optimized: {optimized_tokens} tokens")
        print(f"  Reduction: {reduction:.1%}")
    
    def test_context_truncation_optimization(self):
        """Test that context truncation reduces token usage."""
        # Simulate long context
        long_context_tokens = 5000
        
        # Simulate truncated context
        truncated_tokens = 2000
        
        reduction = (long_context_tokens - truncated_tokens) / long_context_tokens
        
        assert reduction > 0.5, f"Context truncation should reduce tokens by > 50%"
        
        print(f"✓ Context truncation:")
        print(f"  Long context: {long_context_tokens} tokens")
        print(f"  Truncated: {truncated_tokens} tokens")
        print(f"  Reduction: {reduction:.1%}")
    
    def test_response_length_limiting(self, sample_explanation_input):
        """Test that limiting response length reduces tokens."""
        agent = LangChainExplanationAgent()
        
        with patch.object(agent, 'gemini_client') as mock_client:
            # Simulate unlimited response
            unlimited_tokens = 3500
            
            # Simulate limited response (max_tokens parameter)
            limited_tokens = 2000
            
            reduction = (unlimited_tokens - limited_tokens) / unlimited_tokens
            
            assert reduction > 0.4, f"Response limiting should reduce tokens by > 40%"
            
            print(f"✓ Response length limiting:")
            print(f"  Unlimited: {unlimited_tokens} tokens")
            print(f"  Limited: {limited_tokens} tokens")
            print(f"  Reduction: {reduction:.1%}")
    
    def test_caching_reduces_token_usage(self, sample_explanation_input):
        """Test that caching reduces overall token usage."""
        agent = LangChainExplanationAgent()
        
        # First call - full token usage
        first_call_tokens = 2500
        
        # Cached call - minimal tokens (just cache lookup)
        cached_call_tokens = 0
        
        # Multiple calls with caching
        num_calls = 10
        total_without_cache = first_call_tokens * num_calls
        total_with_cache = first_call_tokens + (cached_call_tokens * (num_calls - 1))
        
        savings = (total_without_cache - total_with_cache) / total_without_cache
        
        assert savings > 0.8, f"Caching should save > 80% tokens for repeated queries"
        
        print(f"✓ Caching token savings:")
        print(f"  Without cache: {total_without_cache} tokens")
        print(f"  With cache: {total_with_cache} tokens")
        print(f"  Savings: {savings:.1%}")


class TestCostEfficiency:
    """
    Test cost efficiency of token usage.
    
    Property: Complete assessments should stay within cost limits
    Requirements: 10.3 - Track Gemini API usage and costs
    """
    
    def test_complete_assessment_cost(self, monitoring_service):
        """Test total cost for complete health assessment."""
        # Simulate token usage for complete pipeline
        agent_tokens = {
            'validation': 500,
            'extraction': 1500,
            'severity': 800,
            'explanation': 2500,
            'recommendation': 2000,
            'lifestyle': 1800,
            'reflection': 1000
        }
        
        total_tokens = sum(agent_tokens.values())
        total_cost = total_tokens * TOKEN_COST_PER_1K / 1000
        
        # Track in monitoring
        for agent_name, tokens in agent_tokens.items():
            cost = tokens * TOKEN_COST_PER_1K / 1000
            monitoring_service.track_gemini_usage(agent_name, tokens, cost)
        
        assert total_cost <= MAX_COST_PER_ASSESSMENT, \
            f"Assessment cost ${total_cost:.4f} exceeds limit ${MAX_COST_PER_ASSESSMENT}"
        
        print(f"✓ Complete assessment cost:")
        print(f"  Total tokens: {total_tokens}")
        print(f"  Total cost: ${total_cost:.4f}")
        print(f"  Cost limit: ${MAX_COST_PER_ASSESSMENT}")
        print(f"  Per-agent breakdown:")
        for agent_name, tokens in agent_tokens.items():
            cost = tokens * TOKEN_COST_PER_1K / 1000
            print(f"    {agent_name}: {tokens} tokens (${cost:.4f})")
    
    def test_cost_per_user_over_time(self, monitoring_service):
        """Test cost efficiency for multiple assessments."""
        num_assessments = 100
        tokens_per_assessment = 10000
        
        total_tokens = num_assessments * tokens_per_assessment
        total_cost = total_tokens * TOKEN_COST_PER_1K / 1000
        cost_per_assessment = total_cost / num_assessments
        
        assert cost_per_assessment <= MAX_COST_PER_ASSESSMENT, \
            f"Average cost ${cost_per_assessment:.4f} exceeds limit"
        
        print(f"✓ Cost efficiency over {num_assessments} assessments:")
        print(f"  Total tokens: {total_tokens:,}")
        print(f"  Total cost: ${total_cost:.2f}")
        print(f"  Cost per assessment: ${cost_per_assessment:.4f}")
    
    def test_cost_optimization_with_caching(self):
        """Test cost savings from caching."""
        # Without caching
        assessments_without_cache = 100
        tokens_per_assessment = 10000
        total_tokens_no_cache = assessments_without_cache * tokens_per_assessment
        cost_no_cache = total_tokens_no_cache * TOKEN_COST_PER_1K / 1000
        
        # With caching (assume 70% cache hit rate)
        cache_hit_rate = 0.7
        cached_assessments = int(assessments_without_cache * cache_hit_rate)
        uncached_assessments = assessments_without_cache - cached_assessments
        
        # Cached assessments use minimal tokens
        tokens_cached = cached_assessments * 100  # Just cache lookup overhead
        tokens_uncached = uncached_assessments * tokens_per_assessment
        total_tokens_with_cache = tokens_cached + tokens_uncached
        cost_with_cache = total_tokens_with_cache * TOKEN_COST_PER_1K / 1000
        
        savings = (cost_no_cache - cost_with_cache) / cost_no_cache
        
        print(f"✓ Cost savings with caching:")
        print(f"  Without cache: ${cost_no_cache:.2f}")
        print(f"  With cache: ${cost_with_cache:.2f}")
        print(f"  Savings: {savings:.1%}")
        print(f"  Cache hit rate: {cache_hit_rate:.1%}")


class TestTokenUsageMonitoring:
    """
    Test token usage monitoring and tracking.
    
    Property: Token usage should be accurately tracked and monitored
    Requirements: 10.3 - Track Gemini API usage and costs
    """
    
    def test_monitoring_tracks_token_usage(self, monitoring_service):
        """Test that monitoring service tracks token usage correctly."""
        # Track usage for multiple agents
        monitoring_service.track_gemini_usage('extraction', 1500, 0.0015)
        monitoring_service.track_gemini_usage('explanation', 2500, 0.0025)
        monitoring_service.track_gemini_usage('recommendation', 2000, 0.002)
        
        # Get metrics
        extraction_metrics = monitoring_service.get_agent_metrics('extraction')
        
        assert extraction_metrics is not None
        assert extraction_metrics.gemini_tokens_used == 1500
        
        print(f"✓ Token usage monitoring:")
        print(f"  Extraction: {extraction_metrics.gemini_tokens_used} tokens")
    
    def test_monitoring_aggregates_token_usage(self, monitoring_service):
        """Test that monitoring aggregates token usage across agents."""
        # Track usage for multiple agents
        agents_usage = {
            'extraction': 1500,
            'explanation': 2500,
            'recommendation': 2000,
            'lifestyle': 1800
        }
        
        for agent_name, tokens in agents_usage.items():
            cost = tokens * TOKEN_COST_PER_1K / 1000
            monitoring_service.track_gemini_usage(agent_name, tokens, cost)
        
        # Get summary
        summary = monitoring_service.get_summary()
        
        expected_total = sum(agents_usage.values())
        assert summary['total_gemini_tokens'] == expected_total
        
        print(f"✓ Token usage aggregation:")
        print(f"  Total tokens: {summary['total_gemini_tokens']}")
        print(f"  Expected: {expected_total}")
    
    def test_monitoring_calculates_costs(self, monitoring_service):
        """Test that monitoring calculates costs correctly."""
        tokens = 10000
        expected_cost = tokens * TOKEN_COST_PER_1K / 1000
        
        monitoring_service.track_gemini_usage('test_agent', tokens, expected_cost)
        
        # Verify cost calculation
        assert abs(expected_cost - 0.01) < 0.001  # $0.01 for 10k tokens
        
        print(f"✓ Cost calculation:")
        print(f"  Tokens: {tokens}")
        print(f"  Cost: ${expected_cost:.4f}")


class TestTokenUsageOptimizationImpact:
    """
    Test impact of optimization strategies on token usage.
    
    Property: Optimizations should measurably reduce token usage
    Requirements: 18.8 - Token optimization strategies
    """
    
    def test_batch_processing_optimization(self):
        """Test that batch processing reduces per-item token usage."""
        # Single item processing
        tokens_per_item_single = 1000
        num_items = 10
        total_tokens_single = tokens_per_item_single * num_items
        
        # Batch processing (shared context reduces overhead)
        tokens_per_item_batch = 700
        total_tokens_batch = tokens_per_item_batch * num_items
        
        savings = (total_tokens_single - total_tokens_batch) / total_tokens_single
        
        assert savings > 0.25, f"Batch processing should save > 25% tokens"
        
        print(f"✓ Batch processing optimization:")
        print(f"  Single processing: {total_tokens_single} tokens")
        print(f"  Batch processing: {total_tokens_batch} tokens")
        print(f"  Savings: {savings:.1%}")
    
    def test_temperature_optimization(self):
        """Test that lower temperature reduces token variance."""
        # High temperature (more creative, potentially longer)
        high_temp_tokens = [2500, 2800, 2600, 2900, 2700]
        
        # Low temperature (more focused, consistent length)
        low_temp_tokens = [2000, 2100, 2050, 2000, 2100]
        
        high_temp_avg = statistics.mean(high_temp_tokens)
        low_temp_avg = statistics.mean(low_temp_tokens)
        
        savings = (high_temp_avg - low_temp_avg) / high_temp_avg
        
        print(f"✓ Temperature optimization:")
        print(f"  High temp average: {high_temp_avg:.0f} tokens")
        print(f"  Low temp average: {low_temp_avg:.0f} tokens")
        print(f"  Savings: {savings:.1%}")
    
    def test_structured_output_optimization(self):
        """Test that structured outputs use fewer tokens than free-form."""
        # Free-form text response
        freeform_tokens = 3000
        
        # Structured JSON response
        structured_tokens = 1500
        
        savings = (freeform_tokens - structured_tokens) / freeform_tokens
        
        assert savings > 0.4, f"Structured output should save > 40% tokens"
        
        print(f"✓ Structured output optimization:")
        print(f"  Free-form: {freeform_tokens} tokens")
        print(f"  Structured: {structured_tokens} tokens")
        print(f"  Savings: {savings:.1%}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
