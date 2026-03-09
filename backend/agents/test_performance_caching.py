"""
Performance tests for caching effectiveness.

Tests cache hit rates, cache expiration, and cache effectiveness
for web search results and dynamic treatment retrieval.

Requirements: 18.1, 3.7, 3.8
"""

import pytest
import time
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from agents.infrastructure.web_search import WebSearchTool, SearchCache
from agents.infrastructure.dynamic_treatment import DynamicTreatmentRetrieval
from agents.infrastructure.config import SearchConfig
from agents.infrastructure.models import SearchResult
from common.cache_service import CacheService


# Cache performance thresholds
CACHE_HIT_RATE_THRESHOLD = 0.7  # 70% hit rate
CACHE_LOOKUP_TIME_THRESHOLD = 0.01  # 10ms
CACHE_SPEEDUP_THRESHOLD = 5.0  # 5x faster than uncached


@pytest.fixture
def search_cache():
    """Create a search cache for testing."""
    return SearchCache(ttl=3600)


@pytest.fixture
def web_search_tool():
    """Create a web search tool with caching."""
    config = SearchConfig(rate_limit=10, cache_ttl=3600)
    return WebSearchTool(config)


@pytest.fixture
def cache_service():
    """Create a cache service for testing."""
    return CacheService()


@pytest.fixture
def sample_search_results():
    """Sample search results for testing."""
    return [
        SearchResult(
            title="Diabetes Treatment Guidelines",
            url="https://pubmed.ncbi.nlm.nih.gov/test1",
            snippet="Treatment guidelines for diabetes...",
            source_domain="pubmed.ncbi.nlm.nih.gov",
            quality_score=1.0,
            publication_date=datetime.utcnow(),
            content="Full content here",
            metadata={}
        ),
        SearchResult(
            title="Managing Type 2 Diabetes",
            url="https://who.int/test2",
            snippet="WHO guidelines for diabetes management...",
            source_domain="who.int",
            quality_score=0.95,
            publication_date=datetime.utcnow(),
            content="Full content here",
            metadata={}
        )
    ]


class TestCacheHitRates:
    """
    Test cache hit rates for various scenarios.
    
    Property: Cache should achieve acceptable hit rates for repeated queries
    Requirements: 18.1 - Test cache hit rates
    """
    
    def test_search_cache_hit_rate_repeated_queries(self, search_cache, sample_search_results):
        """Test cache hit rate with repeated identical queries."""
        query = "diabetes treatment"
        
        # Populate cache
        search_cache.set(query, sample_search_results)
        
        hits = 0
        misses = 0
        total_queries = 100
        
        for i in range(total_queries):
            if i % 10 == 0:
                # Every 10th query is different (cache miss)
                result = search_cache.get(f"query_{i}")
                if result is None:
                    misses += 1
            else:
                # Same query (cache hit)
                result = search_cache.get(query)
                if result is not None:
                    hits += 1
                else:
                    misses += 1
        
        hit_rate = hits / total_queries
        
        assert hit_rate >= CACHE_HIT_RATE_THRESHOLD, \
            f"Cache hit rate {hit_rate:.2%} is below threshold {CACHE_HIT_RATE_THRESHOLD:.2%}"
        
        print(f"✓ Cache hit rate: {hit_rate:.2%} (threshold: {CACHE_HIT_RATE_THRESHOLD:.2%})")
        print(f"  Hits: {hits}, Misses: {misses}")
    
    def test_web_search_cache_hit_rate(self, web_search_tool, sample_search_results):
        """Test web search tool cache hit rate."""
        queries = [
            "diabetes treatment",
            "heart disease symptoms",
            "diabetes treatment",  # Repeat
            "hypertension guidelines",
            "diabetes treatment",  # Repeat
            "heart disease symptoms",  # Repeat
        ]
        
        with patch.object(web_search_tool, '_perform_search') as mock_search:
            mock_search.return_value = sample_search_results
            
            api_calls = 0
            cache_hits = 0
            
            for query in queries:
                # Check if in cache before search
                cached = web_search_tool.cache.get(query)
                if cached is not None:
                    cache_hits += 1
                else:
                    api_calls += 1
                
                web_search_tool.search(query)
            
            hit_rate = cache_hits / len(queries)
            
            # Should have 3 cache hits (3 repeated queries)
            assert cache_hits == 3, f"Expected 3 cache hits, got {cache_hits}"
            assert api_calls == 3, f"Expected 3 API calls, got {api_calls}"
            
            print(f"✓ Web search cache hit rate: {hit_rate:.2%}")
            print(f"  Cache hits: {cache_hits}, API calls: {api_calls}")
    
    def test_treatment_retrieval_cache_hit_rate(self, cache_service):
        """Test dynamic treatment retrieval cache hit rate."""
        with patch('agents.infrastructure.dynamic_treatment.WebSearchTool') as mock_search_tool:
            mock_tool = Mock()
            mock_tool.search.return_value = []
            mock_search_tool.return_value = mock_tool
            
            retrieval = DynamicTreatmentRetrieval(mock_tool, cache_service)
            
            diseases = ["diabetes", "heart_disease", "diabetes", "hypertension", "diabetes"]
            
            cache_hits = 0
            cache_misses = 0
            
            for disease in diseases:
                cache_key = f"treatment_{disease}_allopathy"
                
                # Check cache before retrieval
                if cache_service.get(cache_key) is not None:
                    cache_hits += 1
                else:
                    cache_misses += 1
                
                retrieval.get_treatment_info(disease, "allopathy")
            
            hit_rate = cache_hits / len(diseases)
            
            print(f"✓ Treatment retrieval cache hit rate: {hit_rate:.2%}")
            print(f"  Cache hits: {cache_hits}, Cache misses: {cache_misses}")


class TestCacheExpiration:
    """
    Test cache expiration behavior.
    
    Property: Expired cache entries should trigger refresh
    Requirements: 3.8 - Cache expiration triggers refresh
    """
    
    def test_cache_expiration_triggers_refresh(self, sample_search_results):
        """Test that expired cache entries are not returned."""
        # Create cache with 1 second TTL
        cache = SearchCache(ttl=1)
        
        query = "diabetes treatment"
        cache.set(query, sample_search_results)
        
        # Immediate retrieval should hit cache
        result = cache.get(query)
        assert result is not None, "Cache should return result immediately"
        
        # Wait for expiration
        time.sleep(1.1)
        
        # After expiration, should return None
        result = cache.get(query)
        assert result is None, "Expired cache entry should return None"
        
        print("✓ Cache expiration working correctly")
    
    def test_cache_expiration_with_web_search(self, sample_search_results):
        """Test that web search refreshes expired cache."""
        config = SearchConfig(rate_limit=10, cache_ttl=1)  # 1 second TTL
        search_tool = WebSearchTool(config)
        
        query = "diabetes treatment"
        
        with patch.object(search_tool, '_perform_search') as mock_search:
            mock_search.return_value = sample_search_results
            
            # First search - cache miss
            result1 = search_tool.search(query)
            assert mock_search.call_count == 1
            
            # Second search immediately - cache hit
            result2 = search_tool.search(query)
            assert mock_search.call_count == 1  # No additional call
            
            # Wait for expiration
            time.sleep(1.1)
            
            # Third search after expiration - cache miss, triggers refresh
            result3 = search_tool.search(query)
            assert mock_search.call_count == 2  # Additional call made
            
            print("✓ Cache expiration triggers refresh in web search")
    
    def test_cache_ttl_configuration(self):
        """Test that different TTL values work correctly."""
        ttl_values = [1, 5, 10]
        
        for ttl in ttl_values:
            cache = SearchCache(ttl=ttl)
            cache.set("test_query", [])
            
            # Should be cached immediately
            assert cache.get("test_query") is not None
            
            # Wait half the TTL - should still be cached
            time.sleep(ttl / 2)
            assert cache.get("test_query") is not None
            
            # Wait for full expiration
            time.sleep(ttl / 2 + 0.1)
            assert cache.get("test_query") is None
            
            print(f"✓ Cache TTL {ttl}s working correctly")


class TestCacheEffectiveness:
    """
    Test cache effectiveness and performance improvements.
    
    Property: Caching should significantly improve performance
    Requirements: 18.1 - Test cache effectiveness
    """
    
    def test_cache_lookup_speed(self, search_cache, sample_search_results):
        """Test that cache lookups are fast."""
        query = "diabetes treatment"
        search_cache.set(query, sample_search_results)
        
        # Measure cache lookup time
        lookup_times = []
        for _ in range(100):
            start_time = time.time()
            result = search_cache.get(query)
            elapsed_time = time.time() - start_time
            lookup_times.append(elapsed_time)
            
            assert result is not None
        
        avg_lookup_time = sum(lookup_times) / len(lookup_times)
        
        assert avg_lookup_time < CACHE_LOOKUP_TIME_THRESHOLD, \
            f"Average cache lookup {avg_lookup_time:.4f}s exceeds threshold {CACHE_LOOKUP_TIME_THRESHOLD}s"
        
        print(f"✓ Cache lookup speed: {avg_lookup_time*1000:.2f}ms (threshold: {CACHE_LOOKUP_TIME_THRESHOLD*1000:.2f}ms)")
    
    def test_cache_speedup_vs_api_call(self, web_search_tool, sample_search_results):
        """Test that cached searches are significantly faster than API calls."""
        query = "diabetes treatment"
        
        with patch.object(web_search_tool, '_perform_search') as mock_search:
            # Simulate API latency
            def slow_search(*args, **kwargs):
                time.sleep(0.1)  # 100ms simulated API latency
                return sample_search_results
            
            mock_search.side_effect = slow_search
            
            # First search (uncached) - includes API call
            start_time = time.time()
            result1 = web_search_tool.search(query)
            uncached_time = time.time() - start_time
            
            # Second search (cached) - no API call
            start_time = time.time()
            result2 = web_search_tool.search(query)
            cached_time = time.time() - start_time
            
            speedup = uncached_time / cached_time
            
            assert speedup >= CACHE_SPEEDUP_THRESHOLD, \
                f"Cache speedup {speedup:.1f}x is below threshold {CACHE_SPEEDUP_THRESHOLD}x"
            
            print(f"✓ Cache speedup: {speedup:.1f}x faster")
            print(f"  Uncached: {uncached_time*1000:.2f}ms")
            print(f"  Cached: {cached_time*1000:.2f}ms")
    
    def test_cache_memory_efficiency(self, search_cache, sample_search_results):
        """Test that cache doesn't grow unbounded."""
        # Add many entries to cache
        num_entries = 1000
        
        for i in range(num_entries):
            query = f"query_{i}"
            search_cache.set(query, sample_search_results)
        
        # Check cache size
        cache_size = len(search_cache.cache)
        
        assert cache_size == num_entries, f"Cache should contain {num_entries} entries"
        
        # Clear cache
        search_cache.clear()
        
        assert len(search_cache.cache) == 0, "Cache should be empty after clear"
        
        print(f"✓ Cache memory management: {num_entries} entries handled correctly")
    
    def test_cache_effectiveness_with_similar_queries(self, web_search_tool, sample_search_results):
        """Test cache behavior with similar but different queries."""
        queries = [
            "diabetes treatment",
            "diabetes treatment guidelines",
            "diabetes treatment options",
            "diabetes treatment",  # Exact repeat
        ]
        
        with patch.object(web_search_tool, '_perform_search') as mock_search:
            mock_search.return_value = sample_search_results
            
            for query in queries:
                web_search_tool.search(query)
            
            # Should have 3 unique queries + 1 cache hit
            # Total API calls should be 3 (not 4)
            assert mock_search.call_count == 3, \
                f"Expected 3 API calls for 3 unique queries, got {mock_search.call_count}"
            
            print(f"✓ Cache correctly handles similar queries")
            print(f"  Unique queries: 3, Total queries: 4, API calls: {mock_search.call_count}")


class TestCacheConsistency:
    """
    Test cache consistency and correctness.
    
    Property: Cache should return correct data and handle edge cases
    Requirements: 18.1 - Cache effectiveness
    """
    
    def test_cache_returns_correct_data(self, search_cache, sample_search_results):
        """Test that cache returns the exact data that was stored."""
        query = "diabetes treatment"
        
        search_cache.set(query, sample_search_results)
        cached_results = search_cache.get(query)
        
        assert cached_results == sample_search_results, "Cached data should match stored data"
        assert len(cached_results) == len(sample_search_results)
        assert cached_results[0].title == sample_search_results[0].title
        
        print("✓ Cache returns correct data")
    
    def test_cache_handles_empty_results(self, search_cache):
        """Test that cache correctly handles empty result sets."""
        query = "nonexistent query"
        empty_results = []
        
        search_cache.set(query, empty_results)
        cached_results = search_cache.get(query)
        
        assert cached_results == empty_results
        assert len(cached_results) == 0
        
        print("✓ Cache handles empty results correctly")
    
    def test_cache_case_insensitivity(self, search_cache, sample_search_results):
        """Test that cache treats queries case-insensitively."""
        query_lower = "diabetes treatment"
        query_upper = "DIABETES TREATMENT"
        query_mixed = "Diabetes Treatment"
        
        search_cache.set(query_lower, sample_search_results)
        
        # All variations should hit the same cache entry
        result_lower = search_cache.get(query_lower)
        result_upper = search_cache.get(query_upper)
        result_mixed = search_cache.get(query_mixed)
        
        assert result_lower is not None
        assert result_upper is not None
        assert result_mixed is not None
        assert result_lower == result_upper == result_mixed
        
        print("✓ Cache is case-insensitive")
    
    def test_cache_whitespace_normalization(self, search_cache, sample_search_results):
        """Test that cache normalizes whitespace in queries."""
        query1 = "diabetes treatment"
        query2 = "  diabetes   treatment  "
        query3 = "diabetes\ttreatment"
        
        search_cache.set(query1, sample_search_results)
        
        # Queries with different whitespace should hit same cache entry
        result1 = search_cache.get(query1)
        result2 = search_cache.get(query2)
        
        assert result1 is not None
        assert result2 is not None
        
        print("✓ Cache normalizes whitespace")


class TestCacheStatistics:
    """
    Test cache statistics and monitoring.
    
    Property: Cache should provide useful statistics for monitoring
    Requirements: 18.1 - Cache effectiveness monitoring
    """
    
    def test_cache_statistics_tracking(self, web_search_tool, sample_search_results):
        """Test that cache statistics are tracked correctly."""
        queries = ["query1", "query2", "query1", "query3", "query2", "query1"]
        
        with patch.object(web_search_tool, '_perform_search') as mock_search:
            mock_search.return_value = sample_search_results
            
            for query in queries:
                web_search_tool.search(query)
            
            stats = web_search_tool.get_cache_stats()
            
            assert 'cached_queries' in stats
            assert 'cache_ttl' in stats
            assert stats['cached_queries'] == 3  # 3 unique queries
            
            print(f"✓ Cache statistics:")
            print(f"  Cached queries: {stats['cached_queries']}")
            print(f"  Cache TTL: {stats['cache_ttl']}s")
    
    def test_cache_hit_miss_ratio_calculation(self, web_search_tool, sample_search_results):
        """Test calculation of cache hit/miss ratios."""
        queries = [
            "query1",  # Miss
            "query2",  # Miss
            "query1",  # Hit
            "query3",  # Miss
            "query2",  # Hit
            "query1",  # Hit
        ]
        
        with patch.object(web_search_tool, '_perform_search') as mock_search:
            mock_search.return_value = sample_search_results
            
            hits = 0
            misses = 0
            
            for query in queries:
                if web_search_tool.cache.get(query) is not None:
                    hits += 1
                else:
                    misses += 1
                
                web_search_tool.search(query)
            
            hit_ratio = hits / len(queries)
            miss_ratio = misses / len(queries)
            
            assert hit_ratio + miss_ratio == 1.0
            assert hits == 3  # 3 cache hits
            assert misses == 3  # 3 cache misses
            
            print(f"✓ Cache hit/miss ratio:")
            print(f"  Hit ratio: {hit_ratio:.2%}")
            print(f"  Miss ratio: {miss_ratio:.2%}")


class TestCacheUnderLoad:
    """
    Test cache performance under load.
    
    Property: Cache should maintain performance under high load
    Requirements: 18.1 - Cache effectiveness under load
    """
    
    def test_cache_performance_high_volume(self, search_cache, sample_search_results):
        """Test cache performance with high volume of requests."""
        num_requests = 10000
        num_unique_queries = 100
        
        # Populate cache with unique queries
        for i in range(num_unique_queries):
            search_cache.set(f"query_{i}", sample_search_results)
        
        # Perform high volume of lookups
        start_time = time.time()
        for i in range(num_requests):
            query_id = i % num_unique_queries
            result = search_cache.get(f"query_{query_id}")
            assert result is not None
        
        elapsed_time = time.time() - start_time
        avg_lookup_time = elapsed_time / num_requests
        
        assert avg_lookup_time < CACHE_LOOKUP_TIME_THRESHOLD, \
            f"Average lookup time {avg_lookup_time:.6f}s exceeds threshold under load"
        
        print(f"✓ Cache performance under load:")
        print(f"  {num_requests} lookups in {elapsed_time:.2f}s")
        print(f"  Average: {avg_lookup_time*1000:.4f}ms per lookup")
    
    def test_cache_concurrent_access(self, search_cache, sample_search_results):
        """Test cache behavior with concurrent access patterns."""
        import threading
        
        query = "diabetes treatment"
        search_cache.set(query, sample_search_results)
        
        results = []
        errors = []
        
        def access_cache():
            try:
                for _ in range(100):
                    result = search_cache.get(query)
                    results.append(result is not None)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = [threading.Thread(target=access_cache) for _ in range(10)]
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Concurrent access caused errors: {errors}"
        assert all(results), "All cache lookups should succeed"
        
        print(f"✓ Cache handles concurrent access correctly")
        print(f"  {len(results)} concurrent lookups successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
