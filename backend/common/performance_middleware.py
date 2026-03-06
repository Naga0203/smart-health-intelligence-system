"""
Performance Monitoring Middleware for Django

This middleware captures performance metrics for every request including:
- Request duration (start to end time)
- Database query times
- Cache hit/miss rates
- Response timing headers
- Slow request logging

Requirements: 2.4, 2.5, 10.1
"""

import time
import json
import logging
from typing import Callable, Optional
from django.http import HttpRequest, HttpResponse
from django.db import connection
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('health_ai.performance')


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Django middleware for performance monitoring.
    
    Captures request start/end times, tracks database query times,
    records cache hit/miss rates, adds timing headers to responses,
    and logs slow requests exceeding defined thresholds.
    """
    
    # Response time thresholds in milliseconds (from requirements 2.1, 2.2, 2.3)
    THRESHOLDS = {
        'cached': 200,  # 200ms for cached data
        'ml_inference': 2000,  # 2s for ML inference
        'agent_orchestration': 3000,  # 3s for agent orchestration
        'default': 1000,  # 1s default threshold
    }
    
    def __init__(self, get_response: Callable):
        """Initialize the middleware."""
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request: HttpRequest) -> None:
        """
        Called before the view is executed.
        Captures request start time and initial database query count.
        """
        # Capture request start time
        request._performance_start_time = time.time()
        
        # Capture initial database query count
        request._performance_initial_query_count = len(connection.queries)
        
        # Initialize cache tracking
        request._performance_cache_hits = 0
        request._performance_cache_misses = 0
        
        # Track if this is a cached response
        request._performance_is_cached = False
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        Called after the view is executed.
        Calculates metrics, adds headers, and logs performance data.
        """
        # Calculate request duration
        if not hasattr(request, '_performance_start_time'):
            return response
        
        end_time = time.time()
        duration_seconds = end_time - request._performance_start_time
        duration_ms = duration_seconds * 1000
        
        # Calculate database query time
        db_query_time_ms = self._calculate_db_query_time(request)
        
        # Calculate cache hit rate
        cache_hit_rate = self._calculate_cache_hit_rate(request)
        
        # Add timing headers to response (Requirement 2.4)
        response['X-Request-Duration'] = f"{duration_ms:.2f}ms"
        response['X-Database-Time'] = f"{db_query_time_ms:.2f}ms"
        response['X-Cache-Hit-Rate'] = f"{cache_hit_rate:.2f}"
        
        # Determine request type for threshold selection
        request_type = self._determine_request_type(request)
        threshold = self.THRESHOLDS.get(request_type, self.THRESHOLDS['default'])
        
        # Log slow requests (Requirement 2.5)
        if duration_ms > threshold:
            self._log_slow_request(
                request=request,
                response=response,
                duration_ms=duration_ms,
                db_query_time_ms=db_query_time_ms,
                cache_hit_rate=cache_hit_rate,
                threshold=threshold,
                request_type=request_type
            )
        
        # Log all request metrics (Requirement 10.1)
        self._log_request_metrics(
            request=request,
            response=response,
            duration_ms=duration_ms,
            db_query_time_ms=db_query_time_ms,
            cache_hit_rate=cache_hit_rate
        )
        
        return response
    
    def _calculate_db_query_time(self, request: HttpRequest) -> float:
        """
        Calculate total database query time for this request.
        
        Returns:
            Total query time in milliseconds
        """
        if not hasattr(request, '_performance_initial_query_count'):
            return 0.0
        
        initial_count = request._performance_initial_query_count
        current_queries = connection.queries[initial_count:]
        
        total_time = 0.0
        for query in current_queries:
            # Django stores query time as a string in seconds
            query_time = float(query.get('time', 0))
            total_time += query_time
        
        # Convert to milliseconds
        return total_time * 1000
    
    def _calculate_cache_hit_rate(self, request: HttpRequest) -> float:
        """
        Calculate cache hit rate for this request.
        
        Returns:
            Cache hit rate as a decimal (0.0 to 1.0)
        """
        hits = getattr(request, '_performance_cache_hits', 0)
        misses = getattr(request, '_performance_cache_misses', 0)
        
        total = hits + misses
        if total == 0:
            return 0.0
        
        return hits / total
    
    def _determine_request_type(self, request: HttpRequest) -> str:
        """
        Determine the type of request to select appropriate threshold.
        
        Returns:
            Request type: 'cached', 'ml_inference', 'agent_orchestration', or 'default'
        """
        path = request.path.lower()
        
        # Check if response was cached
        if getattr(request, '_performance_is_cached', False):
            return 'cached'
        
        # Check for ML inference endpoints
        if '/predict' in path or '/prediction' in path:
            return 'ml_inference'
        
        # Check for agent orchestration endpoints
        if '/analyze' in path or '/assessment' in path or '/health-analysis' in path:
            return 'agent_orchestration'
        
        return 'default'
    
    def _log_slow_request(
        self,
        request: HttpRequest,
        response: HttpResponse,
        duration_ms: float,
        db_query_time_ms: float,
        cache_hit_rate: float,
        threshold: float,
        request_type: str
    ) -> None:
        """
        Log warning for slow requests exceeding thresholds (Requirement 2.5).
        """
        log_data = {
            'event': 'slow_request',
            'method': request.method,
            'path': request.path,
            'request_type': request_type,
            'duration_ms': round(duration_ms, 2),
            'threshold_ms': threshold,
            'exceeded_by_ms': round(duration_ms - threshold, 2),
            'db_query_time_ms': round(db_query_time_ms, 2),
            'cache_hit_rate': round(cache_hit_rate, 2),
            'status_code': response.status_code,
            'user': str(request.user) if hasattr(request, 'user') else 'anonymous',
            'query_params': dict(request.GET),
        }
        
        logger.warning(json.dumps(log_data))
    
    def _log_request_metrics(
        self,
        request: HttpRequest,
        response: HttpResponse,
        duration_ms: float,
        db_query_time_ms: float,
        cache_hit_rate: float
    ) -> None:
        """
        Log complete request metrics for every API request (Requirement 10.1).
        
        Uses structured JSON logging format for machine parsing.
        """
        log_data = {
            'event': 'request_metrics',
            'timestamp': time.time(),
            'method': request.method,
            'path': request.path,
            'duration_ms': round(duration_ms, 2),
            'db_query_time_ms': round(db_query_time_ms, 2),
            'cache_hit_rate': round(cache_hit_rate, 2),
            'status_code': response.status_code,
            'response_size_bytes': len(response.content) if hasattr(response, 'content') else 0,
            'user': str(request.user) if hasattr(request, 'user') else 'anonymous',
        }
        
        logger.info(json.dumps(log_data))


# Helper functions for tracking cache operations
def track_cache_hit(request: HttpRequest) -> None:
    """
    Track a cache hit for the current request.
    Call this function when data is successfully retrieved from cache.
    """
    if hasattr(request, '_performance_cache_hits'):
        request._performance_cache_hits += 1
    else:
        request._performance_cache_hits = 1


def track_cache_miss(request: HttpRequest) -> None:
    """
    Track a cache miss for the current request.
    Call this function when data is not found in cache.
    """
    if hasattr(request, '_performance_cache_misses'):
        request._performance_cache_misses += 1
    else:
        request._performance_cache_misses = 1


def mark_cached_response(request: HttpRequest) -> None:
    """
    Mark the current request as having a cached response.
    Call this function when returning a fully cached response.
    """
    request._performance_is_cached = True
