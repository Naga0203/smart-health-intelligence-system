"""
Custom throttling classes for API rate limiting.

Implements rate limiting to prevent abuse of the health analysis API.
Validates: Requirements 11.2.3
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, SimpleRateThrottle
from django.core.cache import cache
from django.conf import settings
import time


class HealthAnalysisRateThrottle(UserRateThrottle):
    """
    Rate throttle specifically for health analysis endpoint.
    
    Limits authenticated users to prevent abuse of the computationally
    expensive health analysis pipeline.
    
    Default: 10 requests per minute, 100 requests per hour
    """
    scope = 'health_analysis'
    
    def get_cache_key(self, request, view):
        """
        Generate cache key based on user ID.
        
        For authenticated users, use their Firebase UID.
        For anonymous users, use IP address.
        """
        if request.user and hasattr(request.user, 'uid'):
            ident = request.user.uid
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class HealthAnalysisBurstRateThrottle(SimpleRateThrottle):
    """
    Burst rate throttle for health analysis endpoint.
    
    Prevents rapid-fire requests in short time windows.
    Allows 5 requests per minute to prevent abuse while allowing
    legitimate use cases.
    """
    scope = 'health_analysis_burst'
    
    def get_cache_key(self, request, view):
        """Generate cache key for burst rate limiting."""
        if request.user and hasattr(request.user, 'uid'):
            ident = request.user.uid
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class AnonymousHealthAnalysisThrottle(AnonRateThrottle):
    """
    Stricter rate limiting for anonymous/unauthenticated requests.
    
    Anonymous users get lower rate limits to prevent abuse.
    Default: 5 requests per hour
    """
    scope = 'anon_health_analysis'
    
    def get_cache_key(self, request, view):
        """Generate cache key based on IP address for anonymous users."""
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class IPBasedRateThrottle(SimpleRateThrottle):
    """
    IP-based rate throttle as additional protection layer.
    
    Limits requests per IP address regardless of authentication status.
    Helps prevent distributed abuse attempts.
    """
    scope = 'ip_based'
    
    def get_cache_key(self, request, view):
        """Generate cache key based on IP address."""
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class DailyRateThrottle(SimpleRateThrottle):
    """
    Daily rate limit for health analysis.
    
    Prevents excessive usage over longer time periods.
    Default: 50 requests per day per user
    """
    scope = 'daily_health_analysis'
    
    def get_cache_key(self, request, view):
        """Generate cache key for daily rate limiting."""
        if request.user and hasattr(request.user, 'uid'):
            ident = request.user.uid
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class AdaptiveRateThrottle(SimpleRateThrottle):
    """
    Adaptive rate throttle that adjusts based on system load.
    
    Can be extended to implement dynamic rate limiting based on:
    - Current system load
    - User tier/subscription level
    - Historical usage patterns
    """
    scope = 'adaptive'
    
    def __init__(self):
        super().__init__()
        self.base_rate = '100/hour'
    
    def get_rate(self):
        """
        Get current rate limit.
        
        Can be extended to adjust rate based on system conditions.
        """
        # Future enhancement: adjust rate based on system load
        return self.base_rate
    
    def get_cache_key(self, request, view):
        """Generate cache key for adaptive rate limiting."""
        if request.user and hasattr(request.user, 'uid'):
            ident = request.user.uid
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class RateLimitExceededLogger:
    """
    Utility class to log rate limit violations.
    
    Helps identify potential abuse patterns and adjust rate limits.
    """
    
    @staticmethod
    def log_rate_limit_exceeded(request, throttle_class, wait_time):
        """
        Log rate limit exceeded event.
        
        Args:
            request: Django request object
            throttle_class: Name of throttle class that triggered
            wait_time: Seconds until rate limit resets
        """
        import logging
        logger = logging.getLogger('health_ai.api')
        
        user_id = getattr(request.user, 'uid', 'anonymous') if hasattr(request, 'user') else 'anonymous'
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')
        
        logger.warning(
            f"Rate limit exceeded - User: {user_id}, IP: {ip_address}, "
            f"Throttle: {throttle_class}, Wait: {wait_time}s"
        )
        
        # Store in cache for monitoring
        cache_key = f"rate_limit_violations:{user_id}:{ip_address}"
        violations = cache.get(cache_key, 0)
        cache.set(cache_key, violations + 1, timeout=86400)  # 24 hours
