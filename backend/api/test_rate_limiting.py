"""
Tests for API rate limiting functionality.

Validates: Requirements 11.2.3
"""

import os
import django

# Configure Django settings before importing Django modules
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_ai_backend.settings')
django.setup()

import pytest
from django.test import TestCase, override_settings
from django.core.cache import cache
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from unittest.mock import Mock, patch
import time

from api.throttling import (
    HealthAnalysisRateThrottle,
    HealthAnalysisBurstRateThrottle,
    AnonymousHealthAnalysisThrottle,
    IPBasedRateThrottle,
    DailyRateThrottle,
    RateLimitExceededLogger
)
from api.views import HealthAnalysisAPI


class RateLimitingTestCase(TestCase):
    """Test rate limiting functionality."""
    
    def setUp(self):
        """Set up test client and clear cache."""
        self.client = APIClient()
        self.factory = APIRequestFactory()
        cache.clear()
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_THROTTLE_RATES': {
                'health_analysis_burst': '3/min',
            }
        }
    )
    def test_burst_rate_limiting(self):
        """Test burst rate limiting prevents rapid requests."""
        # Create mock authenticated user
        mock_user = Mock()
        mock_user.uid = 'test_user_123'
        mock_user.is_authenticated = True
        
        # Create throttle instance
        throttle = HealthAnalysisBurstRateThrottle()
        
        # Create mock request
        request = self.factory.post('/api/health/analyze')
        request.user = mock_user
        
        # Create mock view
        view = Mock()
        
        # First 3 requests should be allowed
        for i in range(3):
            allowed = throttle.allow_request(request, view)
            self.assertTrue(allowed, f"Request {i+1} should be allowed")
        
        # 4th request should be throttled
        allowed = throttle.allow_request(request, view)
        self.assertFalse(allowed, "4th request should be throttled")
    
    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_THROTTLE_RATES': {
                'anon_health_analysis': '2/min',
            }
        }
    )
    def test_anonymous_rate_limiting(self):
        """Test anonymous users have stricter rate limits."""
        # Create throttle instance
        throttle = AnonymousHealthAnalysisThrottle()
        
        # Create mock anonymous request
        request = self.factory.post('/api/health/analyze')
        request.user = Mock(is_authenticated=False)
        request.META = {'REMOTE_ADDR': '192.168.1.1'}
        
        # Create mock view
        view = Mock()
        
        # First 2 requests should be allowed
        for i in range(2):
            allowed = throttle.allow_request(request, view)
            self.assertTrue(allowed, f"Request {i+1} should be allowed")
        
        # 3rd request should be throttled
        allowed = throttle.allow_request(request, view)
        self.assertFalse(allowed, "3rd request should be throttled")
    
    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_THROTTLE_RATES': {
                'ip_based': '5/min',
            }
        }
    )
    def test_ip_based_rate_limiting(self):
        """Test IP-based rate limiting works regardless of authentication."""
        # Create throttle instance
        throttle = IPBasedRateThrottle()
        
        # Create mock request with specific IP
        request = self.factory.post('/api/health/analyze')
        request.user = Mock(uid='test_user', is_authenticated=True)
        request.META = {'REMOTE_ADDR': '10.0.0.1'}
        
        # Create mock view
        view = Mock()
        
        # First 5 requests should be allowed
        for i in range(5):
            allowed = throttle.allow_request(request, view)
            self.assertTrue(allowed, f"Request {i+1} should be allowed")
        
        # 6th request should be throttled
        allowed = throttle.allow_request(request, view)
        self.assertFalse(allowed, "6th request should be throttled")
    
    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_THROTTLE_RATES': {
                'daily_health_analysis': '10/day',
            }
        }
    )
    def test_daily_rate_limiting(self):
        """Test daily rate limiting."""
        # Create throttle instance
        throttle = DailyRateThrottle()
        
        # Create mock authenticated user
        mock_user = Mock()
        mock_user.uid = 'daily_test_user'
        mock_user.is_authenticated = True
        
        # Create mock request
        request = self.factory.post('/api/health/analyze')
        request.user = mock_user
        
        # Create mock view
        view = Mock()
        
        # First 10 requests should be allowed
        for i in range(10):
            allowed = throttle.allow_request(request, view)
            self.assertTrue(allowed, f"Request {i+1} should be allowed")
        
        # 11th request should be throttled
        allowed = throttle.allow_request(request, view)
        self.assertFalse(allowed, "11th request should be throttled")
    
    def test_different_users_have_separate_limits(self):
        """Test that different users have independent rate limits."""
        throttle = HealthAnalysisBurstRateThrottle()
        view = Mock()
        
        # User 1
        user1 = Mock(uid='user_1', is_authenticated=True)
        request1 = self.factory.post('/api/health/analyze')
        request1.user = user1
        
        # User 2
        user2 = Mock(uid='user_2', is_authenticated=True)
        request2 = self.factory.post('/api/health/analyze')
        request2.user = user2
        
        # Both users should be able to make requests independently
        self.assertTrue(throttle.allow_request(request1, view))
        self.assertTrue(throttle.allow_request(request2, view))
    
    def test_rate_limit_logger(self):
        """Test rate limit exceeded logging."""
        # Create mock request
        request = self.factory.post('/api/health/analyze')
        request.user = Mock(uid='test_user', is_authenticated=True)
        request.META = {'REMOTE_ADDR': '192.168.1.100'}
        
        # Log rate limit exceeded
        with patch('api.throttling.logging.getLogger') as mock_logger:
            logger_instance = Mock()
            mock_logger.return_value = logger_instance
            
            RateLimitExceededLogger.log_rate_limit_exceeded(
                request,
                'HealthAnalysisBurstRateThrottle',
                60
            )
            
            # Verify logger was called
            logger_instance.warning.assert_called_once()
            call_args = logger_instance.warning.call_args[0][0]
            self.assertIn('test_user', call_args)
            self.assertIn('192.168.1.100', call_args)
            self.assertIn('60s', call_args)
    
    def test_rate_limit_response_format(self):
        """Test that rate limit exceeded returns proper error format."""
        from rest_framework.exceptions import Throttled
        from api.views import APIErrorHandler
        
        # Create throttled exception
        error = Throttled(wait=120)
        
        # Get error response
        response = APIErrorHandler.handle_rate_limit_error(error)
        
        # Verify response structure
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response.data['error'], 'rate_limit_exceeded')
        self.assertEqual(response.data['status_code'], 429)
        self.assertIn('wait_seconds', response.data)
        self.assertEqual(response.data['wait_seconds'], 120)


class RateLimitIntegrationTestCase(TestCase):
    """Integration tests for rate limiting with actual API views."""
    
    def setUp(self):
        """Set up test client and clear cache."""
        self.client = APIClient()
        cache.clear()
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    @patch('api.views.OrchestratorAgent')
    @patch('common.firebase_auth.FirebaseAuthentication.authenticate')
    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_THROTTLE_RATES': {
                'health_analysis_burst': '2/min',
            }
        }
    )
    def test_health_analysis_api_rate_limiting(self, mock_auth, mock_orchestrator):
        """Test rate limiting on actual health analysis endpoint."""
        # Mock authentication
        mock_user = Mock()
        mock_user.uid = 'integration_test_user'
        mock_user.is_authenticated = True
        mock_auth.return_value = (mock_user, {})
        
        # Mock orchestrator response
        mock_orchestrator_instance = Mock()
        mock_orchestrator_instance.process.return_value = {
            'success': True,
            'data': {
                'prediction': {
                    'disease': 'Diabetes',
                    'probability': 0.8,
                    'probability_percent': 80.0,
                    'confidence': 'HIGH'
                },
                'metadata': {'timestamp': '2026-02-10T00:00:00'}
            }
        }
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Test data
        test_data = {
            'symptoms': ['fatigue', 'increased_thirst'],
            'age': 35,
            'gender': 'male'
        }
        
        # First 2 requests should succeed
        for i in range(2):
            response = self.client.post(
                '/api/health/analyze',
                test_data,
                format='json',
                HTTP_AUTHORIZATION='Bearer fake_token'
            )
            self.assertEqual(
                response.status_code, 
                status.HTTP_200_OK,
                f"Request {i+1} should succeed"
            )
        
        # 3rd request should be rate limited
        response = self.client.post(
            '/api/health/analyze',
            test_data,
            format='json',
            HTTP_AUTHORIZATION='Bearer fake_token'
        )
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response.data['error'], 'rate_limit_exceeded')
