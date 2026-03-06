"""
Unit tests for Performance Monitoring Middleware

Tests the middleware's ability to:
- Capture request start/end times
- Track database query times
- Record cache hit/miss rates
- Add timing headers to responses
- Log slow requests exceeding thresholds
"""

import json
import time
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import RequestFactory
from django.http import HttpResponse
from django.contrib.auth.models import AnonymousUser
from django.db import connection
from .performance_middleware import (
    PerformanceMonitoringMiddleware,
    track_cache_hit,
    track_cache_miss,
    mark_cached_response
)


class TestPerformanceMonitoringMiddleware:
    """Test suite for PerformanceMonitoringMiddleware"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures"""
        self.factory = RequestFactory()
        self.get_response = Mock(return_value=HttpResponse("OK"))
        self.middleware = PerformanceMonitoringMiddleware(self.get_response)
    
    def test_process_request_initializes_tracking(self):
        """Test that process_request initializes performance tracking attributes"""
        request = self.factory.get('/api/test')
        
        self.middleware.process_request(request)
        
        # Verify tracking attributes are initialized
        assert hasattr(request, '_performance_start_time')
        assert hasattr(request, '_performance_initial_query_count')
        assert hasattr(request, '_performance_cache_hits')
        assert hasattr(request, '_performance_cache_misses')
        assert hasattr(request, '_performance_is_cached')
        
        # Verify initial values
        assert request._performance_cache_hits == 0
        assert request._performance_cache_misses == 0
        assert request._performance_is_cached == False
    
    def test_process_response_adds_timing_headers(self):
        """Test that process_response adds required timing headers (Requirement 2.4)"""
        request = self.factory.get('/api/test')
        request.user = AnonymousUser()
        
        # Initialize request tracking
        self.middleware.process_request(request)
        
        # Simulate some processing time
        time.sleep(0.01)
        
        response = HttpResponse("OK")
        response = self.middleware.process_response(request, response)
        
        # Verify timing headers are present
        assert 'X-Request-Duration' in response
        assert 'X-Database-Time' in response
        assert 'X-Cache-Hit-Rate' in response
        
        # Verify header format
        assert response['X-Request-Duration'].endswith('ms')
        assert response['X-Database-Time'].endswith('ms')
    
    def test_calculate_db_query_time(self):
        """Test database query time calculation"""
        request = self.factory.get('/api/test')
        
        # Mock connection.queries
        with patch.object(connection, 'queries', [
            {'time': '0.001', 'sql': 'SELECT 1'},
            {'time': '0.002', 'sql': 'SELECT 2'},
        ]):
            request._performance_initial_query_count = 0
            
            db_time = self.middleware._calculate_db_query_time(request)
            
            # Should be 3ms (1ms + 2ms)
            assert abs(db_time - 3.0) < 10**(-1)
    
    def test_calculate_cache_hit_rate_with_hits_and_misses(self):
        """Test cache hit rate calculation with both hits and misses"""
        request = self.factory.get('/api/test')
        request._performance_cache_hits = 7
        request._performance_cache_misses = 3
        
        hit_rate = self.middleware._calculate_cache_hit_rate(request)
        
        # 7 hits out of 10 total = 0.7
        assert abs(hit_rate - 0.7) < 10**(-2)
    
    def test_calculate_cache_hit_rate_with_no_cache_operations(self):
        """Test cache hit rate calculation with no cache operations"""
        request = self.factory.get('/api/test')
        request._performance_cache_hits = 0
        request._performance_cache_misses = 0
        
        hit_rate = self.middleware._calculate_cache_hit_rate(request)
        
        # No operations = 0.0 hit rate
        assert hit_rate == 0.0
    
    def test_calculate_cache_hit_rate_with_all_hits(self):
        """Test cache hit rate calculation with all hits"""
        request = self.factory.get('/api/test')
        request._performance_cache_hits = 10
        request._performance_cache_misses = 0
        
        hit_rate = self.middleware._calculate_cache_hit_rate(request)
        
        # All hits = 1.0 hit rate
        assert hit_rate == 1.0
    
    def test_determine_request_type_cached(self):
        """Test request type determination for cached responses"""
        request = self.factory.get('/api/test')
        request._performance_is_cached = True
        
        request_type = self.middleware._determine_request_type(request)
        
        assert request_type == 'cached'
    
    def test_determine_request_type_ml_inference(self):
        """Test request type determination for ML inference endpoints"""
        request = self.factory.get('/api/predict/disease')
        request._performance_is_cached = False
        
        request_type = self.middleware._determine_request_type(request)
        
        assert request_type == 'ml_inference'
    
    def test_determine_request_type_agent_orchestration(self):
        """Test request type determination for agent orchestration endpoints"""
        request = self.factory.get('/api/health-analysis')
        request._performance_is_cached = False
        
        request_type = self.middleware._determine_request_type(request)
        
        assert request_type == 'agent_orchestration'
    
    def test_determine_request_type_default(self):
        """Test request type determination for default endpoints"""
        request = self.factory.get('/api/user/profile')
        request._performance_is_cached = False
        
        request_type = self.middleware._determine_request_type(request)
        
        assert request_type == 'default'
    
    @patch('backend.common.performance_middleware.logger')
    def test_log_slow_request_for_cached_threshold(self, mock_logger):
        """Test slow request logging when exceeding cached threshold (Requirement 2.5)"""
        request = self.factory.get('/api/test')
        request.user = AnonymousUser()
        request._performance_is_cached = True
        
        response = HttpResponse("OK")
        
        # Simulate slow request (250ms, exceeds 200ms cached threshold)
        self.middleware._log_slow_request(
            request=request,
            response=response,
            duration_ms=250.0,
            db_query_time_ms=50.0,
            cache_hit_rate=0.8,
            threshold=200.0,
            request_type='cached'
        )
        
        # Verify warning was logged
        mock_logger.warning.assert_called_once()
        
        # Verify log data structure
        log_call = mock_logger.warning.call_args[0][0]
        log_data = json.loads(log_call)
        
        assert log_data['event'] == 'slow_request'
        assert log_data['duration_ms'] == 250.0
        assert log_data['threshold_ms'] == 200.0
        assert log_data['exceeded_by_ms'] == 50.0
        assert log_data['request_type'] == 'cached'
    
    @patch('backend.common.performance_middleware.logger')
    def test_log_request_metrics(self, mock_logger):
        """Test request metrics logging for all requests (Requirement 10.1)"""
        request = self.factory.get('/api/test')
        request.user = AnonymousUser()
        
        response = HttpResponse("OK")
        
        self.middleware._log_request_metrics(
            request=request,
            response=response,
            duration_ms=150.0,
            db_query_time_ms=30.0,
            cache_hit_rate=0.75
        )
        
        # Verify info log was created
        mock_logger.info.assert_called_once()
        
        # Verify log data structure (JSON format for machine parsing)
        log_call = mock_logger.info.call_args[0][0]
        log_data = json.loads(log_call)
        
        assert log_data['event'] == 'request_metrics'
        assert log_data['duration_ms'] == 150.0
        assert log_data['db_query_time_ms'] == 30.0
        assert log_data['cache_hit_rate'] == 0.75
        assert 'timestamp' in log_data
    
    def test_track_cache_hit_helper(self):
        """Test track_cache_hit helper function"""
        request = self.factory.get('/api/test')
        
        # First hit
        track_cache_hit(request)
        assert request._performance_cache_hits == 1
        
        # Second hit
        track_cache_hit(request)
        assert request._performance_cache_hits == 2
    
    def test_track_cache_miss_helper(self):
        """Test track_cache_miss helper function"""
        request = self.factory.get('/api/test')
        
        # First miss
        track_cache_miss(request)
        assert request._performance_cache_misses == 1
        
        # Second miss
        track_cache_miss(request)
        assert request._performance_cache_misses == 2
    
    def test_mark_cached_response_helper(self):
        """Test mark_cached_response helper function"""
        request = self.factory.get('/api/test')
        
        mark_cached_response(request)
        
        assert request._performance_is_cached
    
    @patch('backend.common.performance_middleware.logger')
    def test_slow_ml_inference_request_logging(self, mock_logger):
        """Test logging for slow ML inference requests (>2s threshold)"""
        request = self.factory.get('/api/predict/disease')
        request.user = AnonymousUser()
        request._performance_is_cached = False
        
        # Initialize tracking
        self.middleware.process_request(request)
        
        # Mock slow response (2500ms, exceeds 2000ms ML threshold)
        with patch('time.time', side_effect=[0, 2.5]):
            response = HttpResponse("OK")
            self.middleware.process_response(request, response)
        
        # Verify slow request was logged
        warning_calls = [call for call in mock_logger.warning.call_args_list]
        assert len(warning_calls > 0)
    
    @patch('backend.common.performance_middleware.logger')
    def test_slow_agent_orchestration_request_logging(self, mock_logger):
        """Test logging for slow agent orchestration requests (>3s threshold)"""
        request = self.factory.get('/api/health-analysis')
        request.user = AnonymousUser()
        request._performance_is_cached = False
        
        # Initialize tracking
        self.middleware.process_request(request)
        
        # Mock slow response (3500ms, exceeds 3000ms agent threshold)
        with patch('time.time', side_effect=[0, 3.5]):
            response = HttpResponse("OK")
            self.middleware.process_response(request, response)
        
        # Verify slow request was logged
        warning_calls = [call for call in mock_logger.warning.call_args_list]
        assert len(warning_calls > 0)
    
    def test_process_response_without_process_request(self):
        """Test that process_response handles missing tracking attributes gracefully"""
        request = self.factory.get('/api/test')
        response = HttpResponse("OK")
        
        # Call process_response without calling process_request first
        result = self.middleware.process_response(request, response)
        
        # Should return response without errors
        assert result == response
    
    def test_cache_hit_rate_in_response_header(self):
        """Test that cache hit rate is correctly reflected in response header"""
        request = self.factory.get('/api/test')
        request.user = AnonymousUser()
        
        # Initialize tracking
        self.middleware.process_request(request)
        
        # Simulate cache operations
        track_cache_hit(request)
        track_cache_hit(request)
        track_cache_hit(request)
        track_cache_miss(request)
        
        response = HttpResponse("OK")
        response = self.middleware.process_response(request, response)
        
        # Verify cache hit rate header (3 hits out of 4 = 0.75)
        cache_hit_rate = float(response['X-Cache-Hit-Rate'])
        assert abs(cache_hit_rate - 0.75) < 10**(-2)
    
    def test_thresholds_configuration(self):
        """Test that thresholds are correctly configured"""
        assert self.middleware.THRESHOLDS['cached'] == 200
        assert self.middleware.THRESHOLDS['ml_inference'] == 2000
        assert self.middleware.THRESHOLDS['agent_orchestration'] == 3000
        assert self.middleware.THRESHOLDS['default'] == 1000
    
    @patch('backend.common.performance_middleware.logger')
    def test_json_logging_format(self, mock_logger):
        """Test that logs use JSON format for machine parsing (Requirement 10.4)"""
        request = self.factory.get('/api/test')
        request.user = AnonymousUser()
        
        response = HttpResponse("OK")
        
        self.middleware._log_request_metrics(
            request=request,
            response=response,
            duration_ms=100.0,
            db_query_time_ms=20.0,
            cache_hit_rate=0.5
        )
        
        # Verify log is valid JSON
        log_call = mock_logger.info.call_args[0][0]
        log_data = json.loads(log_call)  # Should not raise exception
        
        # Verify required fields
        assert 'event' in log_data
        assert 'timestamp' in log_data
        assert 'duration_ms' in log_data
        assert 'db_query_time_ms' in log_data
        assert 'cache_hit_rate' in log_data
