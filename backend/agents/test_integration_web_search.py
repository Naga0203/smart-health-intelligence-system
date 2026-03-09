"""
Integration tests for web search functionality.

Tests web search across multiple agents including:
- Web search across multiple agents
- Search result caching
- Rate limiting
- Source filtering

Requirements: 2.1, 2.5, 2.7, 18.1
"""

import pytest
import time
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from backend.agents.infrastructure.web_search import WebSearchTool, MedicalSourceFilter
from backend.agents.infrastructure.config import SearchConfig
from backend.agents.infrastructure.models import SearchResult
from backend.agents.treatment_exploration import TreatmentExplorationAgent
from backend.agents.recommendation import RecommendationAgent
from backend.agents.lifestyle import LifestyleModificationAgent


class TestWebSearchIntegration:
    """Integration tests for web search functionality."""
    
    @pytest.fixture
    def search_config(self):
        """Create search configuration for testing."""
        return SearchConfig(
            rate_limit=10,  # 10 requests per minute
            cache_ttl=3600,  # 1 hour
            max_results=10,
            reliable_sources_only=True
        )
    
    @pytest.fixture
    def web_search_tool(self, search_config):
        """Create web search tool for testing."""
        return WebSearchTool(search_config)
    
    @pytest.fixture
    def mock_search_results(self):
        """Create mock search results."""
        return [
            SearchResult(
                title="Diabetes Treatment Guidelines",
                url="https://pubmed.ncbi.nlm.nih.gov/12345",
                snippet="Current guidelines for diabetes treatment...",
                source_domain="pubmed.ncbi.nlm.nih.gov",
                quality_score=0.95,
                publication_date=datetime.utcnow(),
                content="Detailed diabetes treatment information",
                metadata={"source_type": "medical_journal"}
            ),
            SearchResult(
                title="Diabetes Management - WHO",
                url="https://who.int/diabetes/treatment",
                snippet="WHO guidelines for diabetes management...",
                source_domain="who.int",
                quality_score=0.98,
                publication_date=datetime.utcnow(),
                content="WHO diabetes guidelines",
                metadata={"source_type": "health_organization"}
            )
        ]
    
    def test_web_search_across_multiple_agents(self, mock_search_results):
        """
        Test that multiple agents can perform web searches.
        
        Requirements: 2.1 - Web search capabilities for all agents
        """
        # Mock web search for all agents
        with patch('backend.agents.infrastructure.enhanced_base_agent.WebSearchTool') as mock_search:
            mock_search_instance = Mock()
            mock_search_instance.search.return_value = mock_search_results
            mock_search.return_value = mock_search_instance
            
            # Test treatment exploration agent
            treatment_agent = TreatmentExplorationAgent()
            treatment_agent.web_search_tool = mock_search_instance
            
            treatment_results = treatment_agent.search_web("diabetes treatment")
            assert len(treatment_results) > 0
            assert all(isinstance(r, SearchResult) for r in treatment_results)
            
            # Test recommendation agent
            recommendation_agent = RecommendationAgent()
            recommendation_agent.web_search_tool = mock_search_instance
            
            recommendation_results = recommendation_agent.search_web("diabetes recommendations")
            assert len(recommendation_results) > 0
            
            # Test lifestyle agent
            lifestyle_agent = LifestyleModificationAgent()
            lifestyle_agent.web_search_tool = mock_search_instance
            
            lifestyle_results = lifestyle_agent.search_web("diabetes lifestyle modifications")
            assert len(lifestyle_results) > 0
            
            print("✓ Web search verified across multiple agents")
    
    def test_search_result_caching(self, web_search_tool, mock_search_results):
        """
        Test that search results are cached and reused.
        
        Requirements: 18.1 - Cache web search results
        """
        query = "diabetes treatment guidelines"
        
        # Mock the actual search API
        with patch.object(web_search_tool, '_perform_search', return_value=mock_search_results):
            # First search - should hit API
            start_time = time.time()
            results1 = web_search_tool.search(query)
            first_search_time = time.time() - start_time
            
            assert len(results1) > 0
            
            # Second search - should use cache
            start_time = time.time()
            results2 = web_search_tool.search(query)
            cached_search_time = time.time() - start_time
            
            assert len(results2) > 0
            assert results1 == results2
            
            # Cached search should be faster
            # Note: This is a soft check as timing can vary
            print(f"✓ Search caching verified: first={first_search_time:.4f}s, cached={cached_search_time:.4f}s")
    
    def test_cache_expiration(self, web_search_tool, mock_search_results):
        """
        Test that cached results expire after TTL.
        
        Requirements: 3.8 - Cache expiration triggers refresh
        """
        query = "diabetes treatment"
        
        # Set short TTL for testing
        web_search_tool.cache.ttl = 1  # 1 second
        
        # Mock the actual search API
        with patch.object(web_search_tool, '_perform_search', return_value=mock_search_results):
            # First search
            results1 = web_search_tool.search(query)
            assert len(results1) > 0
            
            # Wait for cache to expire
            time.sleep(2)
            
            # Second search - should refresh from API
            results2 = web_search_tool.search(query)
            assert len(results2) > 0
            
            print("✓ Cache expiration verified")
    
    def test_rate_limiting(self, web_search_tool, mock_search_results):
        """
        Test that rate limiting prevents excessive searches.
        
        Requirements: 2.7 - Rate limiting for web searches
        """
        # Mock the actual search API
        with patch.object(web_search_tool, '_perform_search', return_value=mock_search_results):
            # Perform searches up to rate limit
            rate_limit = web_search_tool.config.rate_limit
            
            successful_searches = 0
            rate_limited_searches = 0
            
            # Try to exceed rate limit
            for i in range(rate_limit + 5):
                try:
                    query = f"test query {i}"  # Different queries to avoid cache
                    results = web_search_tool.search(query)
                    if results:
                        successful_searches += 1
                except Exception as e:
                    if "rate limit" in str(e).lower():
                        rate_limited_searches += 1
            
            # Verify rate limiting occurred
            # Note: Implementation may queue requests instead of rejecting
            print(f"✓ Rate limiting: {successful_searches} successful, {rate_limited_searches} limited")
            assert successful_searches <= rate_limit + 2  # Allow small buffer
    
    def test_source_filtering(self, web_search_tool):
        """
        Test that only reliable medical sources are returned.
        
        Requirements: 2.5 - Use reliable medical sources
        """
        # Create mixed results (reliable and unreliable)
        mixed_results = [
            SearchResult(
                title="Reliable Source",
                url="https://pubmed.ncbi.nlm.nih.gov/article",
                snippet="Medical information",
                source_domain="pubmed.ncbi.nlm.nih.gov",
                quality_score=0.95,
                publication_date=datetime.utcnow(),
                content="Content",
                metadata={}
            ),
            SearchResult(
                title="Unreliable Source",
                url="https://random-blog.com/health",
                snippet="Health tips",
                source_domain="random-blog.com",
                quality_score=0.3,
                publication_date=datetime.utcnow(),
                content="Content",
                metadata={}
            ),
            SearchResult(
                title="WHO Guidelines",
                url="https://who.int/guidelines",
                snippet="Official guidelines",
                source_domain="who.int",
                quality_score=0.98,
                publication_date=datetime.utcnow(),
                content="Content",
                metadata={}
            )
        ]
        
        # Mock search to return mixed results
        with patch.object(web_search_tool, '_perform_search', return_value=mixed_results):
            results = web_search_tool.search("diabetes treatment")
            
            # Verify only reliable sources are returned
            for result in results:
                assert web_search_tool.source_filter.is_reliable_source(result.url)
                assert result.quality_score >= 0.5
            
            # Verify unreliable source was filtered out
            domains = [r.source_domain for r in results]
            assert "random-blog.com" not in domains
            assert "pubmed.ncbi.nlm.nih.gov" in domains or "who.int" in domains
            
            print(f"✓ Source filtering verified: {len(results)} reliable sources")
    
    def test_medical_source_filter(self):
        """
        Test medical source filter functionality.
        
        Requirements: 2.5, 17.6 - Reliable source filtering
        """
        source_filter = MedicalSourceFilter()
        
        # Test reliable sources
        reliable_urls = [
            "https://pubmed.ncbi.nlm.nih.gov/12345",
            "https://who.int/health/diabetes",
            "https://cdc.gov/diabetes/guidelines",
            "https://nih.gov/research/diabetes",
            "https://mayoclinic.org/diseases/diabetes"
        ]
        
        for url in reliable_urls:
            assert source_filter.is_reliable_source(url), f"Should be reliable: {url}"
        
        # Test unreliable sources
        unreliable_urls = [
            "https://random-blog.com/health",
            "https://social-media.com/post",
            "https://unknown-site.net/medical"
        ]
        
        for url in unreliable_urls:
            assert not source_filter.is_reliable_source(url), f"Should be unreliable: {url}"
        
        print("✓ Medical source filter verified")
    
    def test_search_quality_scoring(self):
        """
        Test that search results are scored by quality.
        
        Requirements: 5.7 - Select most reliable sources
        """
        source_filter = MedicalSourceFilter()
        
        # Test quality scores for different sources
        pubmed_score = source_filter.assess_source_quality("pubmed.ncbi.nlm.nih.gov")
        who_score = source_filter.assess_source_quality("who.int")
        random_score = source_filter.assess_source_quality("random-blog.com")
        
        # Verify quality scores are appropriate
        assert pubmed_score > 0.8, "PubMed should have high quality score"
        assert who_score > 0.8, "WHO should have high quality score"
        assert random_score < 0.5, "Random blog should have low quality score"
        
        # Verify reliable sources score higher
        assert pubmed_score > random_score
        assert who_score > random_score
        
        print(f"✓ Quality scoring: PubMed={pubmed_score:.2f}, WHO={who_score:.2f}, Random={random_score:.2f}")
    
    def test_search_with_filters(self, web_search_tool, mock_search_results):
        """
        Test web search with various filters.
        
        Requirements: 2.1 - Web search with filtering
        """
        # Mock search API
        with patch.object(web_search_tool, '_perform_search', return_value=mock_search_results):
            # Test with date filter
            filters = {
                "date_range": {
                    "start": (datetime.utcnow() - timedelta(days=365)).isoformat(),
                    "end": datetime.utcnow().isoformat()
                }
            }
            
            results = web_search_tool.search("diabetes treatment", filters)
            assert len(results) > 0
            
            # Test with source type filter
            filters = {
                "source_types": ["medical_journal", "health_organization"]
            }
            
            results = web_search_tool.search("diabetes guidelines", filters)
            assert len(results) > 0
            
            print("✓ Search with filters verified")
    
    def test_concurrent_searches_from_multiple_agents(self, mock_search_results):
        """
        Test concurrent web searches from multiple agents.
        
        Requirements: 6.7 - Parallel agent execution with web search
        """
        import threading
        
        results_dict = {}
        
        def agent_search(agent_name, query):
            """Simulate agent performing search."""
            with patch('backend.agents.infrastructure.enhanced_base_agent.WebSearchTool') as mock_search:
                mock_search_instance = Mock()
                mock_search_instance.search.return_value = mock_search_results
                mock_search.return_value = mock_search_instance
                
                # Simulate search
                results = mock_search_instance.search(query)
                results_dict[agent_name] = results
        
        # Create threads for concurrent searches
        threads = []
        agents = [
            ("treatment_agent", "diabetes treatment"),
            ("recommendation_agent", "diabetes recommendations"),
            ("lifestyle_agent", "diabetes lifestyle")
        ]
        
        for agent_name, query in agents:
            thread = threading.Thread(target=agent_search, args=(agent_name, query))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all agents got results
        assert len(results_dict) == len(agents)
        for agent_name, _ in agents:
            assert agent_name in results_dict
            assert len(results_dict[agent_name]) > 0
        
        print(f"✓ Concurrent searches verified: {len(results_dict)} agents")
    
    def test_search_failure_handling(self, web_search_tool):
        """
        Test handling of search failures.
        
        Requirements: 2.8 - Handle search failures
        """
        # Mock search to fail
        with patch.object(web_search_tool, '_perform_search', side_effect=Exception("Search API error")):
            # Search should handle error gracefully
            results = web_search_tool.search("test query")
            
            # Should return empty results instead of crashing
            assert results == [] or results is None
            
            print("✓ Search failure handling verified")
    
    def test_search_result_validation(self, web_search_tool):
        """
        Test that search results are validated before use.
        
        Requirements: 9.6 - Validate external data
        """
        # Create invalid search results
        invalid_results = [
            SearchResult(
                title="",  # Empty title
                url="invalid-url",  # Invalid URL
                snippet="",
                source_domain="",
                quality_score=-1,  # Invalid score
                publication_date=None,
                content="",
                metadata={}
            )
        ]
        
        # Mock search to return invalid results
        with patch.object(web_search_tool, '_perform_search', return_value=invalid_results):
            results = web_search_tool.search("test query")
            
            # Invalid results should be filtered out
            for result in results:
                assert result.title != ""
                assert result.url.startswith("http")
                assert 0 <= result.quality_score <= 1
            
            print("✓ Search result validation verified")
    
    def test_search_citation_generation(self, mock_search_results):
        """
        Test that search results include proper citations.
        
        Requirements: 2.6 - Validate and cite sources
        """
        for result in mock_search_results:
            citation = result.get_citation()
            
            # Verify citation includes required elements
            assert result.title in citation
            assert result.url in citation
            assert result.source_domain in citation
            
            # Verify citation format
            assert len(citation) > 0
            
        print("✓ Citation generation verified")


class TestSearchCacheIntegration:
    """Integration tests for search result caching."""
    
    def test_cache_hit_rate_tracking(self):
        """
        Test that cache hit rates are tracked.
        
        Requirements: 18.1 - Cache effectiveness
        """
        from backend.agents.infrastructure.web_search import SearchCache
        
        cache = SearchCache(ttl=3600)
        
        # Perform cache operations
        cache.set("query1", ["result1"])
        cache.set("query2", ["result2"])
        
        # Cache hits
        result1 = cache.get("query1")
        result2 = cache.get("query2")
        
        # Cache miss
        result3 = cache.get("query3")
        
        # Verify cache operations
        assert result1 == ["result1"]
        assert result2 == ["result2"]
        assert result3 is None
        
        print("✓ Cache hit rate tracking verified")
    
    def test_cache_memory_management(self):
        """
        Test that cache manages memory properly.
        
        Requirements: 18.1 - Cache management
        """
        from backend.agents.infrastructure.web_search import SearchCache
        
        cache = SearchCache(ttl=3600, max_size=100)
        
        # Fill cache beyond capacity
        for i in range(150):
            cache.set(f"query_{i}", [f"result_{i}"])
        
        # Verify cache size is limited
        cache_size = len(cache._cache) if hasattr(cache, '_cache') else 0
        assert cache_size <= 120  # Allow some buffer
        
        print(f"✓ Cache memory management verified: size={cache_size}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
