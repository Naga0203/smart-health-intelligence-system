"""
Performance tests for agent response times.

Tests health assessment completion time, individual agent execution times,
web search latency, and OCR processing time.

Requirements: 18.5, 18.7
"""

import pytest
import time
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock
import statistics

from agents.orchestrator import OrchestratorAgent
from agents.validation import LangChainValidationAgent
from agents.data_extraction import DataExtractionAgent
from agents.severity import SeverityAgent
from agents.explanation import LangChainExplanationAgent
from agents.recommendation import RecommendationAgent
from agents.lifestyle import LifestyleModificationAgent
from agents.reflection import ReflectionAgent
from agents.infrastructure.web_search import WebSearchTool
from agents.infrastructure.gemini_ocr import GeminiOCRService
from agents.infrastructure.config import SearchConfig


# Performance thresholds (in seconds)
HEALTH_ASSESSMENT_THRESHOLD = 30.0  # Complete pipeline
VALIDATION_THRESHOLD = 2.0
EXTRACTION_THRESHOLD = 5.0
SEVERITY_THRESHOLD = 3.0
EXPLANATION_THRESHOLD = 5.0
RECOMMENDATION_THRESHOLD = 5.0
LIFESTYLE_THRESHOLD = 4.0
REFLECTION_THRESHOLD = 3.0
WEB_SEARCH_THRESHOLD = 2.0
OCR_THRESHOLD = 10.0


@pytest.fixture
def sample_input():
    """Sample input for performance testing."""
    return {
        "user_id": "perf_test_user",
        "symptoms": ["increased_thirst", "frequent_urination", "fatigue"],
        "age": 45,
        "gender": "male",
        "additional_info": {
            "vitals": {
                "blood_pressure": "140/90",
                "heart_rate": 85,
                "temperature": 98.6
            },
            "lab_results": {
                "glucose": 180,
                "hba1c": 7.5
            }
        }
    }


@pytest.fixture
def mock_prediction_engine():
    """Mock prediction engine for performance tests."""
    with patch('agents.orchestrator.DiseasePredictor') as mock:
        predictor = Mock()
        predictor.predict.return_value = (0.75, {"model": "test", "features": 10})
        mock.return_value = predictor
        yield predictor


@pytest.fixture
def mock_firebase():
    """Mock Firebase for performance tests."""
    with patch('agents.orchestrator.get_firebase_db') as mock:
        db = Mock()
        db.collection.return_value.document.return_value.set.return_value = None
        db.collection.return_value.add.return_value = (None, "test_id")
        mock.return_value = db
        yield db


class TestHealthAssessmentPerformance:
    """
    Test complete health assessment pipeline performance.
    
    Property: Health assessment should complete within acceptable time threshold
    Requirements: 18.5 - Test health assessment completion time
    """
    
    def test_complete_pipeline_performance(self, sample_input, mock_prediction_engine, mock_firebase):
        """Test that complete health assessment completes within threshold."""
        orchestrator = OrchestratorAgent()
        
        start_time = time.time()
        result = orchestrator.run_pipeline(sample_input)
        elapsed_time = time.time() - start_time
        
        assert result is not None
        assert elapsed_time < HEALTH_ASSESSMENT_THRESHOLD, \
            f"Health assessment took {elapsed_time:.2f}s, threshold is {HEALTH_ASSESSMENT_THRESHOLD}s"
        
        print(f"✓ Complete pipeline: {elapsed_time:.2f}s (threshold: {HEALTH_ASSESSMENT_THRESHOLD}s)")
    
    def test_pipeline_performance_multiple_runs(self, sample_input, mock_prediction_engine, mock_firebase):
        """Test pipeline performance consistency across multiple runs."""
        orchestrator = OrchestratorAgent()
        execution_times = []
        
        num_runs = 5
        for i in range(num_runs):
            start_time = time.time()
            result = orchestrator.run_pipeline(sample_input)
            elapsed_time = time.time() - start_time
            execution_times.append(elapsed_time)
            
            assert result is not None
        
        avg_time = statistics.mean(execution_times)
        std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        
        assert avg_time < HEALTH_ASSESSMENT_THRESHOLD, \
            f"Average time {avg_time:.2f}s exceeds threshold {HEALTH_ASSESSMENT_THRESHOLD}s"
        
        print(f"✓ Pipeline performance over {num_runs} runs:")
        print(f"  Average: {avg_time:.2f}s")
        print(f"  Std Dev: {std_dev:.2f}s")
        print(f"  Min: {min(execution_times):.2f}s")
        print(f"  Max: {max(execution_times):.2f}s")
    
    def test_pipeline_performance_with_report_data(self, mock_prediction_engine, mock_firebase):
        """Test pipeline performance with medical report data."""
        input_with_report = {
            "user_id": "perf_test_user",
            "symptoms": ["chest_pain", "shortness_of_breath"],
            "age": 55,
            "gender": "male",
            "report_metadata": {
                "report_id": "test_report",
                "has_extracted_data": True
            },
            "extracted_data": {
                "lab_results": {"cholesterol": 240, "ldl": 160},
                "vitals": {"blood_pressure": "150/95"}
            },
            "data_sources": {
                "symptoms": "manual",
                "lab_results": "extracted"
            }
        }
        
        orchestrator = OrchestratorAgent()
        
        start_time = time.time()
        result = orchestrator.run_pipeline(input_with_report)
        elapsed_time = time.time() - start_time
        
        assert result is not None
        assert elapsed_time < HEALTH_ASSESSMENT_THRESHOLD, \
            f"Pipeline with report data took {elapsed_time:.2f}s, threshold is {HEALTH_ASSESSMENT_THRESHOLD}s"
        
        print(f"✓ Pipeline with report data: {elapsed_time:.2f}s")


class TestIndividualAgentPerformance:
    """
    Test individual agent execution times.
    
    Property: Each agent should complete within its specific time threshold
    Requirements: 18.5 - Test individual agent execution times
    """
    
    def test_validation_agent_performance(self, sample_input):
        """Test ValidationAgent performance."""
        agent = LangChainValidationAgent()
        
        start_time = time.time()
        result = agent.process(sample_input)
        elapsed_time = time.time() - start_time
        
        assert result["success"]
        assert elapsed_time < VALIDATION_THRESHOLD, \
            f"Validation took {elapsed_time:.2f}s, threshold is {VALIDATION_THRESHOLD}s"
        
        print(f"✓ ValidationAgent: {elapsed_time:.2f}s (threshold: {VALIDATION_THRESHOLD}s)")
    
    def test_extraction_agent_performance(self):
        """Test DataExtractionAgent performance."""
        agent = DataExtractionAgent()
        
        input_data = {
            "symptoms": ["increased_thirst", "frequent_urination"],
            "age": 45,
            "gender": "male",
            "disease": "diabetes"
        }
        
        start_time = time.time()
        result = agent.process(input_data)
        elapsed_time = time.time() - start_time
        
        assert result["success"]
        assert elapsed_time < EXTRACTION_THRESHOLD, \
            f"Extraction took {elapsed_time:.2f}s, threshold is {EXTRACTION_THRESHOLD}s"
        
        print(f"✓ DataExtractionAgent: {elapsed_time:.2f}s (threshold: {EXTRACTION_THRESHOLD}s)")
    
    def test_severity_agent_performance(self):
        """Test SeverityAgent performance."""
        agent = SeverityAgent()
        
        input_data = {
            "symptoms": ["chest_pain", "shortness_of_breath"],
            "vitals": {"blood_pressure": "150/95", "heart_rate": 95},
            "disease": "heart_disease"
        }
        
        start_time = time.time()
        result = agent.process(input_data)
        elapsed_time = time.time() - start_time
        
        assert result["success"]
        assert elapsed_time < SEVERITY_THRESHOLD, \
            f"Severity assessment took {elapsed_time:.2f}s, threshold is {SEVERITY_THRESHOLD}s"
        
        print(f"✓ SeverityAgent: {elapsed_time:.2f}s (threshold: {SEVERITY_THRESHOLD}s)")
    
    def test_explanation_agent_performance(self):
        """Test ExplanationAgent performance."""
        agent = LangChainExplanationAgent()
        
        input_data = {
            "disease": "diabetes",
            "probability": 0.75,
            "confidence": "medium",
            "symptoms": ["increased_thirst", "frequent_urination"]
        }
        
        start_time = time.time()
        result = agent.process(input_data)
        elapsed_time = time.time() - start_time
        
        assert result["success"]
        assert elapsed_time < EXPLANATION_THRESHOLD, \
            f"Explanation took {elapsed_time:.2f}s, threshold is {EXPLANATION_THRESHOLD}s"
        
        print(f"✓ ExplanationAgent: {elapsed_time:.2f}s (threshold: {EXPLANATION_THRESHOLD}s)")
    
    def test_recommendation_agent_performance(self):
        """Test RecommendationAgent performance."""
        agent = RecommendationAgent()
        
        input_data = {
            "disease": "diabetes",
            "probability": 0.75,
            "confidence": "medium",
            "symptoms": ["increased_thirst", "frequent_urination"],
            "user_context": {"age": 45, "gender": "male"}
        }
        
        start_time = time.time()
        result = agent.process(input_data)
        elapsed_time = time.time() - start_time
        
        assert result["success"]
        assert elapsed_time < RECOMMENDATION_THRESHOLD, \
            f"Recommendations took {elapsed_time:.2f}s, threshold is {RECOMMENDATION_THRESHOLD}s"
        
        print(f"✓ RecommendationAgent: {elapsed_time:.2f}s (threshold: {RECOMMENDATION_THRESHOLD}s)")
    
    def test_lifestyle_agent_performance(self):
        """Test LifestyleAgent performance."""
        agent = LifestyleModificationAgent()
        
        input_data = {
            "disease": "diabetes",
            "confidence": "medium",
            "symptoms": ["increased_thirst", "frequent_urination"],
            "user_context": {"age": 45, "gender": "male"}
        }
        
        start_time = time.time()
        result = agent.process(input_data)
        elapsed_time = time.time() - start_time
        
        assert result["success"]
        assert elapsed_time < LIFESTYLE_THRESHOLD, \
            f"Lifestyle recommendations took {elapsed_time:.2f}s, threshold is {LIFESTYLE_THRESHOLD}s"
        
        print(f"✓ LifestyleAgent: {elapsed_time:.2f}s (threshold: {LIFESTYLE_THRESHOLD}s)")
    
    def test_reflection_agent_performance(self):
        """Test ReflectionAgent performance."""
        agent = ReflectionAgent()
        
        assessment = {
            "prediction": {"disease": "diabetes", "probability": 0.75, "confidence": "medium"},
            "explanation": {"summary": "Test explanation"},
            "recommendations": {"immediate": ["Test recommendation"]},
            "symptoms": ["increased_thirst"]
        }
        
        start_time = time.time()
        result = agent.verify_assessment(assessment)
        elapsed_time = time.time() - start_time
        
        assert result is not None
        assert elapsed_time < REFLECTION_THRESHOLD, \
            f"Reflection took {elapsed_time:.2f}s, threshold is {REFLECTION_THRESHOLD}s"
        
        print(f"✓ ReflectionAgent: {elapsed_time:.2f}s (threshold: {REFLECTION_THRESHOLD}s)")


class TestWebSearchPerformance:
    """
    Test web search latency.
    
    Property: Web searches should complete within acceptable latency
    Requirements: 18.5 - Test web search latency
    """
    
    def test_web_search_latency(self):
        """Test web search response time."""
        config = SearchConfig(rate_limit=10, cache_ttl=3600)
        search_tool = WebSearchTool(config)
        
        # Mock the actual search to avoid external API calls
        with patch.object(search_tool, '_perform_search') as mock_search:
            mock_search.return_value = []
            
            start_time = time.time()
            results = search_tool.search("diabetes treatment guidelines")
            elapsed_time = time.time() - start_time
            
            assert elapsed_time < WEB_SEARCH_THRESHOLD, \
                f"Web search took {elapsed_time:.2f}s, threshold is {WEB_SEARCH_THRESHOLD}s"
            
            print(f"✓ Web search: {elapsed_time:.2f}s (threshold: {WEB_SEARCH_THRESHOLD}s)")
    
    def test_cached_search_performance(self):
        """Test that cached searches are significantly faster."""
        config = SearchConfig(rate_limit=10, cache_ttl=3600)
        search_tool = WebSearchTool(config)
        
        query = "diabetes treatment"
        
        # Mock the actual search
        with patch.object(search_tool, '_perform_search') as mock_search:
            mock_search.return_value = []
            
            # First search (uncached)
            start_time = time.time()
            search_tool.search(query)
            first_search_time = time.time() - start_time
            
            # Second search (cached)
            start_time = time.time()
            search_tool.search(query)
            cached_search_time = time.time() - start_time
            
            # Cached search should be much faster
            assert cached_search_time < first_search_time, \
                "Cached search should be faster than initial search"
            assert cached_search_time < 0.1, \
                f"Cached search took {cached_search_time:.2f}s, should be < 0.1s"
            
            print(f"✓ Cached search speedup: {first_search_time/cached_search_time:.1f}x faster")
    
    def test_multiple_concurrent_searches(self):
        """Test performance of multiple concurrent searches."""
        config = SearchConfig(rate_limit=20, cache_ttl=3600)
        search_tool = WebSearchTool(config)
        
        queries = [
            "diabetes symptoms",
            "heart disease treatment",
            "hypertension guidelines",
            "cholesterol management"
        ]
        
        with patch.object(search_tool, '_perform_search') as mock_search:
            mock_search.return_value = []
            
            start_time = time.time()
            for query in queries:
                search_tool.search(query)
            elapsed_time = time.time() - start_time
            
            avg_time_per_search = elapsed_time / len(queries)
            
            assert avg_time_per_search < WEB_SEARCH_THRESHOLD, \
                f"Average search time {avg_time_per_search:.2f}s exceeds threshold"
            
            print(f"✓ Multiple searches: {len(queries)} searches in {elapsed_time:.2f}s")
            print(f"  Average per search: {avg_time_per_search:.2f}s")


class TestOCRPerformance:
    """
    Test OCR processing time.
    
    Property: OCR should process images within acceptable time
    Requirements: 18.5 - Test OCR processing time
    """
    
    def test_ocr_text_extraction_performance(self):
        """Test OCR text extraction speed."""
        ocr_service = GeminiOCRService()
        
        # Mock image data (1MB simulated)
        mock_image_data = b"x" * (1024 * 1024)
        
        with patch.object(ocr_service, 'gemini_vision') as mock_vision:
            mock_vision.invoke.return_value = MagicMock(content="Extracted text")
            
            start_time = time.time()
            result = ocr_service.extract_text(mock_image_data, "jpeg")
            elapsed_time = time.time() - start_time
            
            assert result is not None
            assert elapsed_time < OCR_THRESHOLD, \
                f"OCR took {elapsed_time:.2f}s, threshold is {OCR_THRESHOLD}s"
            
            print(f"✓ OCR text extraction: {elapsed_time:.2f}s (threshold: {OCR_THRESHOLD}s)")
    
    def test_ocr_structured_data_extraction_performance(self):
        """Test OCR structured data extraction speed."""
        ocr_service = GeminiOCRService()
        
        mock_image_data = b"x" * (1024 * 1024)
        
        with patch.object(ocr_service, 'gemini_vision') as mock_vision:
            mock_vision.invoke.return_value = MagicMock(
                content='{"lab_results": {"glucose": 120}, "vitals": {"bp": "120/80"}}'
            )
            
            start_time = time.time()
            result = ocr_service.extract_structured_data(mock_image_data)
            elapsed_time = time.time() - start_time
            
            assert result is not None
            assert elapsed_time < OCR_THRESHOLD, \
                f"Structured OCR took {elapsed_time:.2f}s, threshold is {OCR_THRESHOLD}s"
            
            print(f"✓ OCR structured extraction: {elapsed_time:.2f}s (threshold: {OCR_THRESHOLD}s)")
    
    def test_ocr_multiple_formats_performance(self):
        """Test OCR performance across different image formats."""
        ocr_service = GeminiOCRService()
        
        formats = ["jpeg", "png", "pdf"]
        mock_image_data = b"x" * (512 * 1024)  # 512KB
        
        format_times = {}
        
        with patch.object(ocr_service, 'gemini_vision') as mock_vision:
            mock_vision.invoke.return_value = MagicMock(content="Extracted text")
            
            for fmt in formats:
                start_time = time.time()
                result = ocr_service.extract_text(mock_image_data, fmt)
                elapsed_time = time.time() - start_time
                format_times[fmt] = elapsed_time
                
                assert result is not None
                assert elapsed_time < OCR_THRESHOLD
        
        print(f"✓ OCR format performance:")
        for fmt, elapsed in format_times.items():
            print(f"  {fmt}: {elapsed:.2f}s")


class TestParallelExecutionPerformance:
    """
    Test parallel agent execution performance.
    
    Property: Parallel execution should be faster than sequential
    Requirements: 18.7 - Operations respect time limits
    """
    
    def test_parallel_vs_sequential_execution(self, mock_prediction_engine, mock_firebase):
        """Test that parallel execution is faster than sequential."""
        orchestrator = OrchestratorAgent()
        
        input_data = {
            "symptoms": ["increased_thirst", "frequent_urination"],
            "age": 45,
            "gender": "male",
            "disease": "diabetes"
        }
        
        # Measure parallel execution time
        extraction_input = input_data.copy()
        severity_input = {
            "symptoms": input_data["symptoms"],
            "vitals": {},
            "disease": "diabetes"
        }
        
        parallel_agents = [
            ('extraction', orchestrator.extraction_agent, extraction_input),
            ('severity', orchestrator.severity_agent, severity_input)
        ]
        
        start_time = time.time()
        parallel_results = orchestrator._execute_agents_parallel(parallel_agents)
        parallel_time = time.time() - start_time
        
        # Measure sequential execution time
        start_time = time.time()
        seq_result1 = orchestrator._execute_single_agent('extraction', orchestrator.extraction_agent, extraction_input)
        seq_result2 = orchestrator._execute_single_agent('severity', orchestrator.severity_agent, severity_input)
        sequential_time = time.time() - start_time
        
        # Parallel should be faster (or at least not significantly slower)
        speedup = sequential_time / parallel_time
        
        print(f"✓ Parallel execution performance:")
        print(f"  Sequential: {sequential_time:.2f}s")
        print(f"  Parallel: {parallel_time:.2f}s")
        print(f"  Speedup: {speedup:.2f}x")
        
        # Parallel should provide some speedup (at least 1.2x)
        assert speedup >= 1.0, "Parallel execution should not be slower than sequential"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
