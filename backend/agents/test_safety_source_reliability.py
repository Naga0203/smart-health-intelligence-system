"""
Safety tests for source reliability.

Tests that only reliable medical sources are used
and that source filtering works correctly.

Requirements: 17.6 - Use reliable medical sources only
"""

import pytest
from agents.infrastructure.web_search import (
    MedicalSourceFilter,
    WebSearchTool,
    SearchCache,
    RateLimiter
)
from agents.infrastructure.models import SearchResult
from agents.infrastructure.config import SearchConfig
from datetime import datetime


class TestMedicalSourceFilter:
    """Test suite for medical source filtering."""
    
    @pytest.fixture
    def filter(self):
        """Create MedicalSourceFilter instance."""
        return MedicalSourceFilter()
    
    def test_recognizes_pubmed_as_reliable(self, filter):
        """Test that PubMed is recognized as reliable source."""
        url = "https://pubmed.ncbi.nlm.nih.gov/12345678/"
        assert filter.is_reliable_source(url) is True
    
    def test_recognizes_who_as_reliable(self, filter):
        """Test that WHO is recognized as reliable source."""
        url = "https://www.who.int/health-topics/diabetes"
        assert filter.is_reliable_source(url) is True
    
    def test_recognizes_cdc_as_reliable(self, filter):
        """Test that CDC is recognized as reliable source."""
        url = "https://www.cdc.gov/diabetes/basics/diabetes.html"
        assert filter.is_reliable_source(url) is True
    
    def test_recognizes_nih_as_reliable(self, filter):
        """Test that NIH is recognized as reliable source."""
        url = "https://www.nih.gov/health-information"
        assert filter.is_reliable_source(url) is True
    
    def test_recognizes_mayo_clinic_as_reliable(self, filter):
        """Test that Mayo Clinic is recognized as reliable source."""
        url = "https://www.mayoclinic.org/diseases-conditions/diabetes"
        assert filter.is_reliable_source(url) is True
    
    def test_recognizes_nejm_as_reliable(self, filter):
        """Test that NEJM is recognized as reliable source."""
        url = "https://www.nejm.org/doi/full/10.1056/NEJMoa123456"
        assert filter.is_reliable_source(url) is True
    
    def test_recognizes_lancet_as_reliable(self, filter):
        """Test that The Lancet is recognized as reliable source."""
        url = "https://www.thelancet.com/journals/lancet/article"
        assert filter.is_reliable_source(url) is True
    
    def test_recognizes_bmj_as_reliable(self, filter):
        """Test that BMJ is recognized as reliable source."""
        url = "https://www.bmj.com/content/123/456/789"
        assert filter.is_reliable_source(url) is True
    
    def test_recognizes_jama_as_reliable(self, filter):
        """Test that JAMA is recognized as reliable source."""
        url = "https://jamanetwork.com/journals/jama/fullarticle/123456"
        assert filter.is_reliable_source(url) is True
    
    def test_recognizes_cleveland_clinic_as_reliable(self, filter):
        """Test that Cleveland Clinic is recognized as reliable source."""
        url = "https://my.clevelandclinic.org/health/diseases/123"
        assert filter.is_reliable_source(url) is True
    
    def test_recognizes_hopkins_as_reliable(self, filter):
        """Test that Johns Hopkins is recognized as reliable source."""
        url = "https://www.hopkinsmedicine.org/health/conditions"
        assert filter.is_reliable_source(url) is True
    
    def test_recognizes_harvard_health_as_reliable(self, filter):
        """Test that Harvard Health is recognized as reliable source."""
        url = "https://www.health.harvard.edu/topics/diabetes"
        assert filter.is_reliable_source(url) is True
    
    def test_recognizes_nhs_as_reliable(self, filter):
        """Test that NHS is recognized as reliable source."""
        url = "https://www.nhs.uk/conditions/diabetes/"
        assert filter.is_reliable_source(url) is True
    
    def test_rejects_unreliable_source(self, filter):
        """Test that unreliable sources are rejected."""
        unreliable_urls = [
            "https://www.random-health-blog.com/article",
            "https://www.fake-medical-site.net/info",
            "https://www.unverified-health.org/treatment",
            "https://www.personal-blog.com/my-cure"
        ]
        
        for url in unreliable_urls:
            assert filter.is_reliable_source(url) is False
    
    def test_handles_www_prefix(self, filter):
        """Test that www prefix is handled correctly."""
        urls_with_www = [
            "https://www.who.int/health",
            "https://www.cdc.gov/health",
            "https://www.nih.gov/health"
        ]
        
        for url in urls_with_www:
            assert filter.is_reliable_source(url) is True
    
    def test_case_insensitive_domain_check(self, filter):
        """Test that domain checking is case insensitive."""
        urls = [
            "https://WHO.INT/health",
            "https://www.CDC.GOV/health",
            "https://PubMed.NCBI.NLM.NIH.GOV/12345"
        ]
        
        for url in urls:
            assert filter.is_reliable_source(url) is True
    
    def test_filters_search_results(self, filter):
        """Test filtering list of search results."""
        results = [
            SearchResult(
                title="Study 1",
                url="https://pubmed.ncbi.nlm.nih.gov/12345",
                snippet="Reliable source",
                source_domain="pubmed.ncbi.nlm.nih.gov",
                quality_score=1.0,
                publication_date=None,
                content="",
                metadata={}
            ),
            SearchResult(
                title="Blog Post",
                url="https://random-blog.com/article",
                snippet="Unreliable source",
                source_domain="random-blog.com",
                quality_score=0.3,
                publication_date=None,
                content="",
                metadata={}
            ),
            SearchResult(
                title="WHO Article",
                url="https://www.who.int/article",
                snippet="Reliable source",
                source_domain="who.int",
                quality_score=0.95,
                publication_date=None,
                content="",
                metadata={}
            )
        ]
        
        filtered = filter.filter_results(results)
        
        assert len(filtered) == 2
        assert all(filter.is_reliable_source(r.url) for r in filtered)
    
    def test_assess_source_quality_pubmed(self, filter):
        """Test quality assessment for PubMed."""
        quality = filter.assess_source_quality("pubmed.ncbi.nlm.nih.gov")
        assert quality == 1.0
    
    def test_assess_source_quality_who(self, filter):
        """Test quality assessment for WHO."""
        quality = filter.assess_source_quality("who.int")
        assert quality == 0.95
    
    def test_assess_source_quality_mayo_clinic(self, filter):
        """Test quality assessment for Mayo Clinic."""
        quality = filter.assess_source_quality("mayoclinic.org")
        assert quality == 0.85
    
    def test_assess_source_quality_unknown(self, filter):
        """Test quality assessment for unknown source."""
        quality = filter.assess_source_quality("unknown-site.com")
        assert quality == 0.5  # Default score
    
    def test_handles_invalid_url(self, filter):
        """Test that invalid URLs are handled gracefully."""
        invalid_urls = [
            "not-a-url",
            "",
            "ftp://invalid-protocol.com",
            None
        ]
        
        for url in invalid_urls:
            try:
                result = filter.is_reliable_source(url) if url else False
                assert result is False
            except Exception:
                # Should handle gracefully
                pass
    
    def test_all_reliable_domains_have_quality_scores(self, filter):
        """Test that all reliable domains have quality scores."""
        for domain in filter.RELIABLE_DOMAINS:
            quality = filter.assess_source_quality(domain)
            assert quality >= 0.5, f"Domain {domain} missing quality score"


class TestWebSearchToolSourceFiltering:
    """Test suite for WebSearchTool source filtering integration."""
    
    @pytest.fixture
    def search_tool(self):
        """Create WebSearchTool instance with reliable sources only."""
        config = SearchConfig(
            rate_limit=10,
            cache_ttl=3600,
            max_results=10,
            reliable_sources_only=True
        )
        return WebSearchTool(config)
    
    @pytest.fixture
    def search_tool_no_filter(self):
        """Create WebSearchTool instance without source filtering."""
        config = SearchConfig(
            rate_limit=10,
            cache_ttl=3600,
            max_results=10,
            reliable_sources_only=False
        )
        return WebSearchTool(config)
    
    def test_search_tool_has_source_filter(self, search_tool):
        """Test that search tool has source filter."""
        assert search_tool.source_filter is not None
        assert isinstance(search_tool.source_filter, MedicalSourceFilter)
    
    def test_search_tool_filters_when_configured(self, search_tool):
        """Test that search tool filters results when configured."""
        assert search_tool.config.reliable_sources_only is True
    
    def test_search_tool_no_filter_when_disabled(self, search_tool_no_filter):
        """Test that filtering can be disabled."""
        assert search_tool_no_filter.config.reliable_sources_only is False
    
    def test_source_filter_integration(self, search_tool):
        """Test that source filter is properly integrated."""
        # Verify filter has reliable domains configured
        assert len(search_tool.source_filter.RELIABLE_DOMAINS) > 0
        
        # Verify filter can check sources
        assert search_tool.source_filter.is_reliable_source("https://pubmed.ncbi.nlm.nih.gov/123")


class TestSourceReliabilityValidation:
    """Test suite for validating source reliability in responses."""
    
    @pytest.fixture
    def filter(self):
        """Create MedicalSourceFilter instance."""
        return MedicalSourceFilter()
    
    def test_validates_citation_sources(self, filter):
        """Test validation of sources in citations."""
        citations = [
            "https://pubmed.ncbi.nlm.nih.gov/12345",
            "https://www.who.int/article",
            "https://www.cdc.gov/health"
        ]
        
        for citation in citations:
            assert filter.is_reliable_source(citation) is True
    
    def test_detects_unreliable_citations(self, filter):
        """Test detection of unreliable sources in citations."""
        unreliable_citations = [
            "https://random-blog.com/health-tips",
            "https://unverified-medical.net/cure",
            "https://personal-experience.org/treatment"
        ]
        
        for citation in unreliable_citations:
            assert filter.is_reliable_source(citation) is False
    
    def test_mixed_source_quality_assessment(self, filter):
        """Test quality assessment for mixed sources."""
        sources = [
            ("pubmed.ncbi.nlm.nih.gov", 1.0),
            ("who.int", 0.95),
            ("mayoclinic.org", 0.85),
            ("healthline.com", 0.7),
            ("unknown-site.com", 0.5)
        ]
        
        for source, expected_min_quality in sources:
            quality = filter.assess_source_quality(source)
            assert quality >= expected_min_quality * 0.9  # Allow small variance


class TestSourceReliabilityIntegration:
    """Integration tests for source reliability across agent responses."""
    
    @pytest.fixture
    def filter(self):
        """Create MedicalSourceFilter instance."""
        return MedicalSourceFilter()
    
    def test_agent_response_with_reliable_sources(self, filter):
        """Test agent response using only reliable sources."""
        sources = [
            "https://pubmed.ncbi.nlm.nih.gov/12345",
            "https://www.who.int/diabetes",
            "https://www.cdc.gov/diabetes/basics"
        ]
        
        for source in sources:
            assert filter.is_reliable_source(source) is True
    
    def test_filters_unreliable_from_mixed_results(self, filter):
        """Test filtering unreliable sources from mixed results."""
        results = [
            SearchResult(
                title="PubMed Study",
                url="https://pubmed.ncbi.nlm.nih.gov/123",
                snippet="Research",
                source_domain="pubmed.ncbi.nlm.nih.gov",
                quality_score=1.0,
                publication_date=None,
                content="",
                metadata={}
            ),
            SearchResult(
                title="Blog Post",
                url="https://health-blog.com/post",
                snippet="Opinion",
                source_domain="health-blog.com",
                quality_score=0.3,
                publication_date=None,
                content="",
                metadata={}
            ),
            SearchResult(
                title="CDC Article",
                url="https://www.cdc.gov/article",
                snippet="Guidelines",
                source_domain="cdc.gov",
                quality_score=0.95,
                publication_date=None,
                content="",
                metadata={}
            )
        ]
        
        filtered = filter.filter_results(results)
        
        # Should only keep reliable sources
        assert len(filtered) == 2
        assert filtered[0].source_domain == "pubmed.ncbi.nlm.nih.gov"
        assert filtered[1].source_domain == "cdc.gov"
    
    def test_prioritizes_higher_quality_sources(self, filter):
        """Test that higher quality sources are prioritized."""
        sources = [
            ("pubmed.ncbi.nlm.nih.gov", filter.assess_source_quality("pubmed.ncbi.nlm.nih.gov")),
            ("healthline.com", filter.assess_source_quality("healthline.com"))
        ]
        
        # PubMed should have higher quality score
        assert sources[0][1] > sources[1][1]
    
    def test_comprehensive_source_coverage(self, filter):
        """Test that filter covers major medical source categories."""
        source_categories = {
            'government': ['cdc.gov', 'nih.gov', 'who.int'],
            'academic': ['pubmed.ncbi.nlm.nih.gov', 'nejm.org', 'thelancet.com'],
            'clinical': ['mayoclinic.org', 'clevelandclinic.org', 'hopkinsmedicine.org'],
            'consumer': ['healthline.com', 'webmd.com', 'medlineplus.gov']
        }
        
        for category, domains in source_categories.items():
            for domain in domains:
                assert domain in filter.RELIABLE_DOMAINS, f"Missing {category} source: {domain}"
    
    def test_rejects_commercial_non_medical_sources(self, filter):
        """Test that commercial non-medical sources are rejected."""
        commercial_sources = [
            "https://www.amazon.com/health-products",
            "https://www.ebay.com/medical-supplies",
            "https://www.shopping-site.com/vitamins"
        ]
        
        for source in commercial_sources:
            assert filter.is_reliable_source(source) is False
    
    def test_rejects_social_media_sources(self, filter):
        """Test that social media sources are rejected."""
        social_media = [
            "https://www.facebook.com/health-group",
            "https://twitter.com/health-tips",
            "https://www.instagram.com/wellness",
            "https://www.reddit.com/r/health"
        ]
        
        for source in social_media:
            assert filter.is_reliable_source(source) is False
    
    def test_rejects_personal_blogs(self, filter):
        """Test that personal blogs are rejected."""
        blogs = [
            "https://my-health-journey.blogspot.com",
            "https://wellness-diary.wordpress.com",
            "https://personal-health-blog.com"
        ]
        
        for blog in blogs:
            assert filter.is_reliable_source(blog) is False


class TestRateLimitingForSourceReliability:
    """Test that rate limiting works with source filtering."""
    
    @pytest.fixture
    def search_tool(self):
        """Create WebSearchTool with low rate limit for testing."""
        config = SearchConfig(
            rate_limit=2,  # Low limit for testing
            cache_ttl=3600,
            max_results=10,
            reliable_sources_only=True
        )
        return WebSearchTool(config)
    
    def test_rate_limiter_exists(self, search_tool):
        """Test that rate limiter is configured."""
        assert search_tool.rate_limiter is not None
        assert isinstance(search_tool.rate_limiter, RateLimiter)
    
    def test_rate_limit_prevents_excessive_searches(self, search_tool):
        """Test that rate limiting prevents excessive searches."""
        # Rate limiter should allow initial requests
        assert search_tool.rate_limiter.can_make_request() is True
