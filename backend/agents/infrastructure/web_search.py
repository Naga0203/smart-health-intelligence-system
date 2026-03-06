"""
Web Search Tool for medical information retrieval.

Provides web search capabilities with medical source filtering,
rate limiting, and result caching.

Requirements: 2.1, 2.5, 2.7
"""

import time
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from datetime import datetime, timedelta
from .models import SearchResult
from .config import SearchConfig

logger = logging.getLogger('health_ai.agents.infrastructure')


class MedicalSourceFilter:
    """
    Filter and validate medical information sources.
    
    Requirements: 2.5 - Use reliable medical sources
    """
    
    # Reliable medical domains
    RELIABLE_DOMAINS = [
        'pubmed.ncbi.nlm.nih.gov',
        'ncbi.nlm.nih.gov',
        'who.int',
        'cdc.gov',
        'nih.gov',
        'mayoclinic.org',
        'nejm.org',
        'thelancet.com',
        'bmj.com',
        'jamanetwork.com',
        'medlineplus.gov',
        'healthline.com',
        'webmd.com',
        'clevelandclinic.org',
        'hopkinsmedicine.org',
        'health.harvard.edu',
        'nhs.uk',
        'cancer.gov',
        'heart.org',
        'diabetes.org',
        'arthritis.org'
    ]
    
    # Domain quality scores (0.0 to 1.0)
    DOMAIN_QUALITY_SCORES = {
        'pubmed.ncbi.nlm.nih.gov': 1.0,
        'ncbi.nlm.nih.gov': 1.0,
        'who.int': 0.95,
        'cdc.gov': 0.95,
        'nih.gov': 0.95,
        'nejm.org': 0.9,
        'thelancet.com': 0.9,
        'bmj.com': 0.9,
        'jamanetwork.com': 0.9,
        'mayoclinic.org': 0.85,
        'clevelandclinic.org': 0.85,
        'hopkinsmedicine.org': 0.85,
        'health.harvard.edu': 0.85,
        'nhs.uk': 0.85,
        'medlineplus.gov': 0.8,
        'cancer.gov': 0.8,
        'heart.org': 0.8,
        'diabetes.org': 0.8,
        'healthline.com': 0.7,
        'webmd.com': 0.7
    }
    
    def is_reliable_source(self, url: str) -> bool:
        """
        Check if source is from reliable medical domain.
        
        Requirements: 2.5 - Filter to reliable medical sources
        
        Args:
            url: URL to check
            
        Returns:
            True if source is reliable
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain in self.RELIABLE_DOMAINS
        except Exception as e:
            logger.error(f"Error parsing URL {url}: {e}")
            return False
    
    def filter_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Filter search results to only reliable sources.
        
        Requirements: 2.5 - Use reliable medical sources only
        
        Args:
            results: List of search results
            
        Returns:
            Filtered list of reliable results
        """
        filtered = [r for r in results if self.is_reliable_source(r.url)]
        
        logger.info(f"Filtered {len(results)} results to {len(filtered)} reliable sources")
        
        return filtered
    
    def assess_source_quality(self, source: str) -> float:
        """
        Assess quality score of information source.
        
        Args:
            source: Source domain
            
        Returns:
            Quality score (0.0 to 1.0)
        """
        source_lower = source.lower()
        
        # Remove www. prefix
        if source_lower.startswith('www.'):
            source_lower = source_lower[4:]
        
        return self.DOMAIN_QUALITY_SCORES.get(source_lower, 0.5)


class RateLimiter:
    """Rate limiter for web search requests."""
    
    def __init__(self, requests_per_minute: int):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self.request_timestamps: List[float] = []
    
    def can_make_request(self) -> bool:
        """
        Check if request can be made within rate limit.
        
        Requirements: 2.7 - Implement rate limiting
        
        Returns:
            True if request is allowed
        """
        current_time = time.time()
        
        # Remove timestamps older than 1 minute
        self.request_timestamps = [
            ts for ts in self.request_timestamps
            if current_time - ts < 60
        ]
        
        return len(self.request_timestamps) < self.requests_per_minute
    
    def record_request(self):
        """Record a request timestamp."""
        self.request_timestamps.append(time.time())
    
    def wait_time(self) -> float:
        """
        Get time to wait before next request.
        
        Returns:
            Seconds to wait
        """
        if self.can_make_request():
            return 0.0
        
        # Calculate time until oldest request expires
        current_time = time.time()
        oldest_timestamp = min(self.request_timestamps)
        return max(0, 60 - (current_time - oldest_timestamp))


class SearchCache:
    """Cache for search results."""
    
    def __init__(self, ttl: int = 3600):
        """
        Initialize search cache.
        
        Args:
            ttl: Time-to-live in seconds
        """
        self.ttl = ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, query: str) -> Optional[List[SearchResult]]:
        """
        Get cached results for query.
        
        Args:
            query: Search query
            
        Returns:
            Cached results or None if not found/expired
        """
        query_key = query.lower().strip()
        
        if query_key not in self.cache:
            return None
        
        cached = self.cache[query_key]
        
        # Check if expired
        if datetime.utcnow() > cached['expires_at']:
            del self.cache[query_key]
            return None
        
        logger.debug(f"Cache hit for query: {query}")
        return cached['results']
    
    def set(self, query: str, results: List[SearchResult]):
        """
        Cache results for query.
        
        Args:
            query: Search query
            results: Search results to cache
        """
        query_key = query.lower().strip()
        
        self.cache[query_key] = {
            'results': results,
            'cached_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(seconds=self.ttl)
        }
        
        logger.debug(f"Cached {len(results)} results for query: {query}")
    
    def clear(self):
        """Clear all cached results."""
        self.cache.clear()
        logger.info("Search cache cleared")


class WebSearchTool:
    """
    Tool for searching medical information on the web.
    
    Requirements:
    - 2.1: Provide web search capabilities to all agents
    - 2.5: Use reliable medical sources
    - 2.7: Implement rate limiting
    """
    
    def __init__(self, config: Optional[SearchConfig] = None):
        """
        Initialize web search tool.
        
        Args:
            config: Search configuration
        """
        self.config = config or SearchConfig()
        self.rate_limiter = RateLimiter(self.config.rate_limit)
        self.source_filter = MedicalSourceFilter()
        self.cache = SearchCache(ttl=self.config.cache_ttl)
        
        logger.info(
            f"WebSearchTool initialized: rate_limit={self.config.rate_limit}/min, "
            f"cache_ttl={self.config.cache_ttl}s"
        )
    
    def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """
        Search for medical information.
        
        Requirements: 2.1 - Web search capabilities for agents
        
        Args:
            query: Search query
            filters: Optional filters (date range, source types, etc.)
            
        Returns:
            List of search results from reliable medical sources
        """
        # Check cache first
        cached_results = self.cache.get(query)
        if cached_results is not None:
            logger.info(f"Returning cached results for: {query}")
            return cached_results
        
        # Check rate limit
        if not self.rate_limiter.can_make_request():
            wait_time = self.rate_limiter.wait_time()
            logger.warning(f"Rate limit exceeded, need to wait {wait_time:.1f}s")
            raise RateLimitExceeded(f"Rate limit exceeded. Wait {wait_time:.1f}s")
        
        # Perform search (placeholder - would integrate with actual search API)
        results = self._perform_search(query, filters)
        
        # Filter to reliable sources if configured
        if self.config.reliable_sources_only:
            results = self.source_filter.filter_results(results)
        
        # Limit results
        results = results[:self.config.max_results]
        
        # Cache results
        self.cache.set(query, results)
        
        # Record request
        self.rate_limiter.record_request()
        
        logger.info(f"Search completed: {query} ({len(results)} results)")
        
        return results
    
    def _perform_search(self, query: str, filters: Optional[Dict[str, Any]]) -> List[SearchResult]:
        """
        Perform actual search (placeholder for real implementation).
        
        In production, this would integrate with a search API like:
        - Google Custom Search API
        - Bing Search API
        - PubMed API
        
        Args:
            query: Search query
            filters: Optional filters
            
        Returns:
            List of search results
        """
        # Placeholder implementation
        # In production, this would call actual search APIs
        logger.warning("Using placeholder search implementation - integrate real search API")
        
        # Return empty results for now
        # Real implementation would call search API and parse results
        return []
    
    def search_medical_literature(self, query: str) -> List[SearchResult]:
        """
        Search PubMed and medical journals.
        
        Requirements: 2.1 - Search medical literature
        
        Args:
            query: Search query
            
        Returns:
            List of medical literature results
        """
        # Add medical literature specific filters
        filters = {
            'sources': ['pubmed', 'medical_journals'],
            'content_type': 'research'
        }
        
        logger.info(f"Searching medical literature: {query}")
        return self.search(query, filters)
    
    def search_clinical_guidelines(self, condition: str) -> List[SearchResult]:
        """
        Search for clinical practice guidelines.
        
        Requirements: 2.3 - Search for clinical guidelines
        
        Args:
            condition: Medical condition
            
        Returns:
            List of clinical guideline results
        """
        query = f"{condition} clinical practice guidelines"
        filters = {
            'sources': ['who', 'cdc', 'nih', 'medical_societies'],
            'content_type': 'guidelines'
        }
        
        logger.info(f"Searching clinical guidelines for: {condition}")
        return self.search(query, filters)
    
    def search_drug_information(self, drug_name: str) -> Dict[str, Any]:
        """
        Search for drug information and interactions.
        
        Requirements: 7.5 - Search for drug interactions
        
        Args:
            drug_name: Drug name
            
        Returns:
            Drug information dictionary
        """
        # Search for drug information
        info_query = f"{drug_name} drug information"
        info_results = self.search(info_query)
        
        # Search for interactions
        interaction_query = f"{drug_name} drug interactions"
        interaction_results = self.search(interaction_query)
        
        logger.info(f"Searched drug information for: {drug_name}")
        
        return {
            'drug_name': drug_name,
            'information': info_results,
            'interactions': interaction_results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cached_queries': len(self.cache.cache),
            'cache_ttl': self.cache.ttl
        }
    
    def clear_cache(self):
        """Clear search cache."""
        self.cache.clear()


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass
