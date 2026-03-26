"""
Web Search Tool for medical information retrieval.

Provides web search capabilities with medical source filtering,
rate limiting, and result caching.

Requirements: 2.1, 2.5, 2.7
"""

import os
import time
import logging
import concurrent.futures
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from datetime import datetime, timedelta

import requests

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


class PubMedClient:
    """
    Client for querying the NCBI PubMed E-utilities API.

    Retrieves peer-reviewed abstracts via a two-step esearch → efetch flow.

    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 8.4, 9.1, 9.3
    """

    BASE_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    BASE_EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    MIN_DELAY_S = 0.334  # 3 req/sec NCBI unauthenticated limit

    def __init__(self, config: SearchConfig):
        """
        Initialize PubMedClient.

        Args:
            config: Search configuration
        """
        self.config = config

    def search(self, query: str) -> List[SearchResult]:
        """
        Search PubMed for peer-reviewed abstracts.

        Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 8.4

        Args:
            query: Search query string

        Returns:
            List of SearchResult objects, or [] on error/disabled
        """
        if not self.config.pubmed_enabled:
            return []

        try:
            # Step 1: esearch to get PMIDs
            esearch_params = {
                "db": "pubmed",
                "term": query,
                "retmax": self.config.pubmed_max_results,
                "retmode": "json",
            }
            esearch_resp = requests.get(
                self.BASE_ESEARCH, params=esearch_params, timeout=self.config.timeout
            )
            if esearch_resp.status_code != 200:
                logger.warning(
                    f"PubMed esearch returned HTTP {esearch_resp.status_code} for query: {query}"
                )
                return []

            pmids = esearch_resp.json().get("esearchresult", {}).get("idlist", [])
            if not pmids:
                return []

            # Enforce minimum inter-request delay (NCBI rate limit)
            time.sleep(self.MIN_DELAY_S)

            # Step 2: efetch to retrieve article XML
            results = self._fetch_articles(pmids)

            # Cap at configured maximum
            return results[: self.config.pubmed_max_results]

        except requests.RequestException as exc:
            logger.warning(f"PubMed network error for query '{query}': {exc}")
            return []

    def _fetch_articles(self, pmids: List[str]) -> List[SearchResult]:
        """
        Fetch article details for a list of PMIDs via efetch.

        Requirements: 9.1

        Args:
            pmids: List of PubMed IDs

        Returns:
            List of SearchResult objects parsed from XML
        """
        try:
            efetch_data = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "xml",
                "rettype": "abstract",
            }
            efetch_resp = requests.post(
                self.BASE_EFETCH, data=efetch_data, timeout=self.config.timeout
            )
            if efetch_resp.status_code != 200:
                logger.warning(
                    f"PubMed efetch returned HTTP {efetch_resp.status_code}"
                )
                return []

            root = ET.fromstring(efetch_resp.text)
            results: List[SearchResult] = []
            for article_elem in root.iter("PubmedArticle"):
                result = self._parse_article(article_elem)
                if result is not None:
                    results.append(result)
            return results

        except requests.RequestException as exc:
            logger.warning(f"PubMed efetch network error: {exc}")
            return []
        except ET.ParseError as exc:
            logger.warning(f"PubMed efetch XML parse error: {exc}")
            return []

    def _parse_article(self, article_elem) -> Optional[SearchResult]:
        """
        Parse a single PubmedArticle XML element into a SearchResult.

        Requirements: 1.2, 1.6, 1.7, 9.3

        Args:
            article_elem: xml.etree.ElementTree Element for a PubmedArticle

        Returns:
            SearchResult or None if the element is malformed
        """
        try:
            title_elem = article_elem.find(".//ArticleTitle")
            abstract_elem = article_elem.find(".//AbstractText")
            pmid_elem = article_elem.find(".//PMID")

            if title_elem is None or pmid_elem is None:
                logger.debug("Skipping PubMed article: missing ArticleTitle or PMID")
                return None

            title = title_elem.text or ""
            snippet = abstract_elem.text if abstract_elem is not None else ""
            pmid = pmid_elem.text or ""

            if not pmid:
                logger.debug("Skipping PubMed article: empty PMID")
                return None

            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

            return SearchResult(
                title=title,
                url=url,
                snippet=snippet or "",
                source_domain="pubmed.ncbi.nlm.nih.gov",
                quality_score=1.0,
            )
        except Exception as exc:
            logger.debug(f"Skipping malformed PubMed article element: {exc}")
            return None


class WikipediaClient:
    """
    Client for querying the Wikipedia REST API summary endpoint.

    Returns a single introductory extract as a SearchResult.

    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6
    """

    BASE_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"

    def __init__(self, config: SearchConfig):
        """
        Initialize WikipediaClient.

        Args:
            config: Search configuration
        """
        self.config = config

    def _normalize_title(self, query: str) -> str:
        """
        Normalize a query string to a Wikipedia-compatible title.

        Replaces spaces with underscores and capitalizes the first character.

        Requirements: 2.6

        Args:
            query: Raw query string

        Returns:
            Normalized title string
        """
        normalized = query.replace(" ", "_")
        if normalized:
            normalized = normalized[0].upper() + normalized[1:]
        return normalized

    def search(self, query: str) -> List[SearchResult]:
        """
        Search Wikipedia for a page summary.

        Requirements: 2.1, 2.2, 2.3, 2.4, 2.5

        Args:
            query: Search query string

        Returns:
            List containing at most one SearchResult, or [] on error/disabled
        """
        if not self.config.wikipedia_enabled:
            return []

        title = self._normalize_title(query)
        url = self.BASE_URL.format(title=title)

        try:
            headers = {
                "User-Agent": "HealthAI/1.0 (health assessment system; contact@healthai.example.com)"
            }
            response = requests.get(url, headers=headers, timeout=self.config.timeout)

            if response.status_code == 404:
                return []

            if response.status_code != 200:
                logger.warning(
                    f"Wikipedia API returned HTTP {response.status_code} for query: {query}"
                )
                return []

            data = response.json()

            if data.get("type") == "disambiguation":
                return []

            return [
                SearchResult(
                    title=data.get("title", ""),
                    url=data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    snippet=data.get("extract", ""),
                    source_domain="en.wikipedia.org",
                    quality_score=0.6,
                )
            ]

        except requests.RequestException as exc:
            logger.warning(f"Wikipedia network error for query '{query}': {exc}")
            return []


TAVILY_AUTHORITATIVE_DOMAINS = [
    "who.int",
    "cdc.gov",
    "fda.gov",
    "nih.gov",
    "thelancet.com",
    "nejm.org",
    "pubmed.ncbi.nlm.nih.gov",
    "bmj.com",
    "jamanetwork.com",
]


class TavilyClient:
    """
    Client for querying the Tavily Search API, restricted to authoritative health domains.

    Returns real-time health intelligence as SearchResult objects.

    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7
    """

    ENDPOINT = "https://api.tavily.com/search"

    def __init__(self, config: SearchConfig):
        """
        Initialize TavilyClient.

        Args:
            config: Search configuration
        """
        self.config = config

    def search(self, query: str) -> List[SearchResult]:
        """
        Search Tavily for real-time health results restricted to authoritative domains.

        Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7

        Args:
            query: Search query string

        Returns:
            List of SearchResult objects, or [] on error/disabled/missing key
        """
        if not self.config.tavily_enabled:
            return []

        api_key = os.environ.get("TAVILY_API", "")
        if not api_key:
            logger.warning("TAVILY_API environment variable is not set; skipping Tavily search")
            return []

        payload = {
            "query": query,
            "api_key": api_key,
            "include_domains": TAVILY_AUTHORITATIVE_DOMAINS,
            "max_results": self.config.tavily_max_results,
            "search_depth": self.config.tavily_search_depth,
        }

        try:
            response = requests.post(
                self.ENDPOINT, json=payload, timeout=self.config.timeout
            )
            if response.status_code != 200:
                logger.warning(
                    f"Tavily API returned HTTP {response.status_code} for query: {query}"
                )
                return []

            source_filter = MedicalSourceFilter()
            results: List[SearchResult] = []
            for item in response.json().get("results", []):
                url = item.get("url", "")
                domain = urlparse(url).netloc
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=url,
                        snippet=item.get("content", ""),
                        source_domain=domain,
                        quality_score=source_filter.assess_source_quality(domain),
                    )
                )
            return results

        except requests.RequestException as exc:
            logger.warning(f"Tavily network error for query '{query}': {exc}")
            return []


class ResultMerger:
    """
    Combines, deduplicates, sorts, and caps result lists from multiple search clients.

    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
    """

    @staticmethod
    def merge(result_lists: List[List[SearchResult]], max_results: int) -> List[SearchResult]:
        """
        Merge multiple SearchResult lists into a single deduplicated, sorted list.

        Algorithm:
        1. Flatten all input lists.
        2. Build dict[url, SearchResult] keeping the entry with the higher quality_score
           when the same URL appears more than once.
        3. Sort by quality_score descending.
        4. Return the first max_results entries.
        5. Returns [] when all inputs are empty — never raises.

        Requirements: 4.1, 4.2, 4.3, 4.4, 4.5

        Args:
            result_lists: List of SearchResult lists from any combination of clients.
            max_results: Maximum number of results to return.

        Returns:
            Merged, deduplicated, sorted list capped at max_results.
        """
        best: Dict[str, SearchResult] = {}
        for result_list in result_lists:
            for result in result_list:
                existing = best.get(result.url)
                if existing is None or result.quality_score > existing.quality_score:
                    best[result.url] = result

        sorted_results = sorted(best.values(), key=lambda r: r.quality_score, reverse=True)
        return sorted_results[:max_results]


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
        Perform actual web search using a configurable search API.

        Supported backends (checked in order):
        1. SerpAPI  — set ``SERPAPI_KEY`` in the environment.
        2. Google Custom Search — set both ``GOOGLE_SEARCH_API_KEY`` and
           ``GOOGLE_SEARCH_ENGINE_ID`` in the environment.

        If no API key is configured the method logs a warning and returns an
        empty list (graceful degradation — preserves existing behaviour).

        Args:
            query: Search query string.
            filters: Optional filters (currently unused by the HTTP backends).

        Returns:
            List of SearchResult objects, or ``[]`` when no key is available
            or a network/API error occurs.
        """
        serpapi_key = os.environ.get("SERPAPI_KEY", "").strip()
        google_key = os.environ.get("GOOGLE_SEARCH_API_KEY", "").strip()
        google_cx = os.environ.get("GOOGLE_SEARCH_ENGINE_ID", "").strip()

        if serpapi_key:
            return self._search_via_serpapi(query, serpapi_key)

        if google_key and google_cx:
            return self._search_via_google(query, google_key, google_cx)

        return self._search_via_stack(query)

    # ------------------------------------------------------------------
    # Private search-backend helpers
    # ------------------------------------------------------------------

    def _search_via_serpapi(self, query: str, api_key: str) -> List[SearchResult]:
        """Call SerpAPI and convert results to SearchResult objects."""
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": api_key,
            "num": self.config.max_results,
            "engine": "google",
        }
        try:
            response = requests.get(url, params=params, timeout=self.config.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            logger.warning(f"SerpAPI request failed: {exc}")
            return []
        except ValueError as exc:
            logger.warning(f"SerpAPI response JSON parse error: {exc}")
            return []

        results: List[SearchResult] = []
        for item in data.get("organic_results", []):
            try:
                result_url = item.get("link", "")
                domain = urlparse(result_url).netloc.lstrip("www.")
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=result_url,
                    snippet=item.get("snippet", ""),
                    source_domain=domain,
                    quality_score=self.source_filter.assess_source_quality(domain),
                ))
            except (ValueError, KeyError) as exc:
                logger.debug(f"Skipping malformed SerpAPI result: {exc}")
                continue

        logger.info(f"SerpAPI returned {len(results)} results for: {query}")
        return results

    def _search_via_google(self, query: str, api_key: str, cx: str) -> List[SearchResult]:
        """Call Google Custom Search JSON API and convert results."""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "key": api_key,
            "cx": cx,
            "num": min(self.config.max_results, 10),  # API max is 10
        }
        try:
            response = requests.get(url, params=params, timeout=self.config.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            logger.warning(f"Google Custom Search request failed: {exc}")
            return []
        except ValueError as exc:
            logger.warning(f"Google Custom Search response JSON parse error: {exc}")
            return []

        results: List[SearchResult] = []
        for item in data.get("items", []):
            try:
                result_url = item.get("link", "")
                domain = urlparse(result_url).netloc.lstrip("www.")
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=result_url,
                    snippet=item.get("snippet", ""),
                    source_domain=domain,
                    quality_score=self.source_filter.assess_source_quality(domain),
                ))
            except (ValueError, KeyError) as exc:
                logger.debug(f"Skipping malformed Google CSE result: {exc}")
                continue

        logger.info(f"Google Custom Search returned {len(results)} results for: {query}")
        return results

    def _search_via_stack(self, query: str) -> List[SearchResult]:
        """
        Run PubMed, Wikipedia, and Tavily in parallel and merge results.

        Requirements: 5.4, 5.5

        Args:
            query: Search query string.

        Returns:
            Merged list of SearchResult objects capped at max_results.
        """
        pubmed_client = PubMedClient(self.config)
        wikipedia_client = WikipediaClient(self.config)
        tavily_client = TavilyClient(self.config)

        clients = [
            ("PubMedClient", pubmed_client.search),
            ("WikipediaClient", wikipedia_client.search),
            ("TavilyClient", tavily_client.search),
        ]

        result_lists: List[List[SearchResult]] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(fn, query): name
                for name, fn in clients
            }
            for future in concurrent.futures.as_completed(futures):
                client_name = futures[future]
                try:
                    result_lists.append(future.result())
                except Exception as exc:
                    logger.warning(f"Search_Stack client {client_name} raised an exception: {exc}")
                    result_lists.append([])

        merged = ResultMerger.merge(result_lists, self.config.max_results)

        if not merged:
            attempted = [name for name, _ in clients]
            logger.warning(
                f"All Search_Stack clients returned empty results. "
                f"Attempted: {', '.join(attempted)}"
            )

        return merged

    def search_medical_literature(self, query: str) -> List[SearchResult]:
        """
        Search medical literature using PubMed (primary) and Wikipedia (secondary).

        Requirements: 5.1, 7.5, 8.1, 8.2, 8.3

        Args:
            query: Search query

        Returns:
            List of medical literature results
        """
        # Check cache first (Requirement 8.1)
        cached = self.cache.get(query)
        if cached is not None:
            logger.info(f"Cache hit for search_medical_literature: {query}")
            return cached

        # Check rate limit (Requirement 8.3)
        if not self.rate_limiter.can_make_request():
            wait_time = self.rate_limiter.wait_time()
            logger.warning(f"Rate limit exceeded for search_medical_literature, wait {wait_time:.1f}s")
            raise RateLimitExceeded(f"Rate limit exceeded. Wait {wait_time:.1f}s")

        logger.info(f"Searching medical literature: {query}")

        # PubMed primary, Wikipedia secondary — sequential (Requirement 5.1)
        pubmed_results = PubMedClient(self.config).search(query)
        wikipedia_results = WikipediaClient(self.config).search(query)

        results = ResultMerger.merge([pubmed_results, wikipedia_results], self.config.max_results)

        # Write to cache and record rate-limiter request (Requirements 8.2, 8.3)
        self.cache.set(query, results)
        self.rate_limiter.record_request()

        logger.info(f"search_medical_literature completed: {query} ({len(results)} results)")
        return results

    def search_clinical_guidelines(self, condition: str) -> List[SearchResult]:
        """
        Search clinical guidelines using Tavily (primary) and PubMed (secondary).

        Requirements: 5.2, 7.5, 8.1, 8.2, 8.3

        Args:
            condition: Medical condition

        Returns:
            List of clinical guideline results
        """
        query = f"{condition} clinical practice guidelines"

        # Check cache first (Requirement 8.1)
        cached = self.cache.get(query)
        if cached is not None:
            logger.info(f"Cache hit for search_clinical_guidelines: {condition}")
            return cached

        # Check rate limit (Requirement 8.3)
        if not self.rate_limiter.can_make_request():
            wait_time = self.rate_limiter.wait_time()
            logger.warning(f"Rate limit exceeded for search_clinical_guidelines, wait {wait_time:.1f}s")
            raise RateLimitExceeded(f"Rate limit exceeded. Wait {wait_time:.1f}s")

        logger.info(f"Searching clinical guidelines for: {condition}")

        # Tavily primary, PubMed secondary — sequential (Requirement 5.2)
        tavily_results = TavilyClient(self.config).search(query)
        pubmed_results = PubMedClient(self.config).search(query)

        results = ResultMerger.merge([tavily_results, pubmed_results], self.config.max_results)

        # Write to cache and record rate-limiter request (Requirements 8.2, 8.3)
        self.cache.set(query, results)
        self.rate_limiter.record_request()

        logger.info(f"search_clinical_guidelines completed: {condition} ({len(results)} results)")
        return results

    def search_drug_information(self, drug_name: str) -> Dict[str, Any]:
        """
        Search drug information using PubMed and Wikipedia for both info and
        interactions queries.

        Requirements: 5.3, 7.5, 8.1, 8.2, 8.3

        Args:
            drug_name: Drug name

        Returns:
            Drug information dictionary
        """
        info_query = f"{drug_name} drug information"
        interaction_query = f"{drug_name} drug interactions"

        # --- Info query ---
        # Check cache first (Requirement 8.1)
        info_results = self.cache.get(info_query)
        if info_results is None:
            if not self.rate_limiter.can_make_request():
                wait_time = self.rate_limiter.wait_time()
                logger.warning(f"Rate limit exceeded for drug info query, wait {wait_time:.1f}s")
                raise RateLimitExceeded(f"Rate limit exceeded. Wait {wait_time:.1f}s")

            pubmed_info = PubMedClient(self.config).search(info_query)
            wiki_info = WikipediaClient(self.config).search(info_query)
            info_results = ResultMerger.merge([pubmed_info, wiki_info], self.config.max_results)

            self.cache.set(info_query, info_results)
            self.rate_limiter.record_request()

        # --- Interactions query ---
        # Check cache first (Requirement 8.1)
        interaction_results = self.cache.get(interaction_query)
        if interaction_results is None:
            if not self.rate_limiter.can_make_request():
                wait_time = self.rate_limiter.wait_time()
                logger.warning(f"Rate limit exceeded for drug interactions query, wait {wait_time:.1f}s")
                raise RateLimitExceeded(f"Rate limit exceeded. Wait {wait_time:.1f}s")

            pubmed_interactions = PubMedClient(self.config).search(interaction_query)
            wiki_interactions = WikipediaClient(self.config).search(interaction_query)
            interaction_results = ResultMerger.merge(
                [pubmed_interactions, wiki_interactions], self.config.max_results
            )

            self.cache.set(interaction_query, interaction_results)
            self.rate_limiter.record_request()

        logger.info(f"search_drug_information completed for: {drug_name}")

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
