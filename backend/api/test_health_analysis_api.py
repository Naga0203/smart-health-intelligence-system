"""
Django tests for HealthAnalysisAPI endpoint

Run with: python manage.py test api.test_health_analysis_api
"""

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import Mock, patch, MagicMock
from api.views import HealthAnalysisAPI
from common.firebase_auth import FirebaseAuthentication, FirebaseUser


class HealthAnalysisAPIStructureTest(TestCase):
    """Test the structure and configuration of HealthAnalysisAPI."""
    
    def test_authentication_class_configured(self):
        """Test that Firebase authentication is configured."""
        self.assertIn(FirebaseAuthentication, HealthAnalysisAPI.authentication_classes)
    
    def test_post_method_exists(self):
        """Test that POST method is implemented."""
        self.assertTrue(hasattr(HealthAnalysisAPI, 'post'))
        self.assertTrue(callable(getattr(HealthAnalysisAPI, 'post')))


class HealthAnalysisAPIIntegrationTest(APITestCase):
    """Integration tests for HealthAnalysisAPI endpoint."""
    
    def setUp(self):
        """Set up test client and mock Firebase user."""
        self.client = APIClient()
        self.url = '/api/health/analyze/'
        
        # Create mock Firebase user
        self.mock_user = FirebaseUser(
            uid='test_user_123',
            email='test@example.com',
            display_name='Test User',
            email_verified=True
        )
    
    def test_endpoint_requires_authentication(self):
        """Test that endpoint requires authentication."""
        # Request without authentication should fail
        response = self.client.post(self.url, {}, format='json')
        
        # Should return 401 or 403 (depending on DRF configuration)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    @patch('api.views.OrchestratorAgent')
    @patch.object(FirebaseAuthentication, 'authenticate')
    def test_valid_request_with_authentication(self, mock_auth, mock_orchestrator):
        """Test valid request with Firebase authentication."""
        # Mock authentication
        mock_auth.return_value = (self.mock_user, {'uid': 'test_user_123'})
        
        # Mock orchestrator response
        mock_orchestrator_instance = Mock()
        mock_orchestrator_instance.process.return_value = {
            'success': True,
            'data': {
                'user_id': 'test_user_123',
                'assessment_id': 'assessment_123',
                'prediction': {
                    'disease': 'Diabetes',
                    'probability': 0.78,
                    'probability_percent': 78.0,
                    'confidence': 'HIGH'
                },
                'extraction': {
                    'confidence': 0.85,
                    'method': 'gemini_ai_extraction'
                },
                'explanation': {
                    'text': 'Test explanation',
                    'generated_by': 'gemini',
                    'confidence': 'HIGH'
                },
                'recommendations': {
                    'items': ['Consult healthcare professional'],
                    'urgency': 'medium',
                    'confidence': 'HIGH'
                },
                'metadata': {
                    'processing_time_seconds': 2.5,
                    'timestamp': '2026-02-09T12:00:00',
                    'storage_ids': {},
                    'pipeline_version': 'v1.0'
                }
            }
        }
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Force authentication
        self.client.force_authenticate(user=self.mock_user)
        
        # Make request
        data = {
            'symptoms': ['fever', 'cough', 'headache'],
            'age': 35,
            'gender': 'male'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_id', response.data)
        self.assertIn('prediction', response.data)
        self.assertIn('explanation', response.data)
    
    @patch.object(FirebaseAuthentication, 'authenticate')
    def test_invalid_input_validation(self, mock_auth):
        """Test that invalid input is rejected."""
        # Mock authentication
        mock_auth.return_value = (self.mock_user, {'uid': 'test_user_123'})
        
        # Force authentication
        self.client.force_authenticate(user=self.mock_user)
        
        # Request with missing required fields
        data = {
            'symptoms': ['fever'],
            # Missing age and gender
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Should return 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('api.views.OrchestratorAgent')
    @patch.object(FirebaseAuthentication, 'authenticate')
    def test_blocked_response_for_low_confidence(self, mock_auth, mock_orchestrator):
        """Test that low confidence results in blocked response."""
        # Mock authentication
        mock_auth.return_value = (self.mock_user, {'uid': 'test_user_123'})
        
        # Mock orchestrator response with blocked result
        mock_orchestrator_instance = Mock()
        mock_orchestrator_instance.process.return_value = {
            'success': True,
            'data': {
                'blocked': True,
                'reason': 'low_confidence',
                'message': 'Insufficient information for reliable assessment',
                'details': {}
            }
        }
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Force authentication
        self.client.force_authenticate(user=self.mock_user)
        
        # Make request
        data = {
            'symptoms': ['fever'],
            'age': 35,
            'gender': 'male'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Verify blocked response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('blocked'))
        self.assertIn('reason', response.data)
    
    @patch('api.views.OrchestratorAgent')
    @patch.object(FirebaseAuthentication, 'authenticate')
    def test_user_id_extraction(self, mock_auth, mock_orchestrator):
        """Test that user_id is correctly extracted from Firebase user."""
        # Mock authentication
        mock_auth.return_value = (self.mock_user, {'uid': 'test_user_123'})
        
        # Mock orchestrator
        mock_orchestrator_instance = Mock()
        mock_orchestrator_instance.process.return_value = {
            'success': True,
            'data': {'user_id': 'test_user_123'}
        }
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Force authentication
        self.client.force_authenticate(user=self.mock_user)
        
        # Make request
        data = {
            'symptoms': ['fever', 'cough'],
            'age': 35,
            'gender': 'male'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Verify user_id was passed to orchestrator
        call_args = mock_orchestrator_instance.process.call_args
        self.assertIsNotNone(call_args)
        input_data = call_args[0][0]
        self.assertEqual(input_data['user_id'], 'test_user_123')
    
    @patch('api.views.OrchestratorAgent')
    @patch.object(FirebaseAuthentication, 'authenticate')
    def test_error_handling(self, mock_auth, mock_orchestrator):
        """Test error handling for orchestrator failures."""
        # Mock authentication
        mock_auth.return_value = (self.mock_user, {'uid': 'test_user_123'})
        
        # Mock orchestrator to raise exception
        mock_orchestrator_instance = Mock()
        mock_orchestrator_instance.process.side_effect = Exception('Test error')
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Force authentication
        self.client.force_authenticate(user=self.mock_user)
        
        # Make request
        data = {
            'symptoms': ['fever', 'cough'],
            'age': 35,
            'gender': 'male'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Should return 500 Internal Server Error
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)


class HealthAnalysisAPISerializerTest(TestCase):
    """Test input serializer validation."""
    
    def test_valid_input(self):
        """Test that valid input is accepted."""
        from api.serializers import HealthAssessmentInputSerializer
        
        data = {
            'symptoms': ['fever', 'cough'],
            'age': 35,
            'gender': 'male'
        }
        
        serializer = HealthAssessmentInputSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_missing_required_fields(self):
        """Test that missing required fields are rejected."""
        from api.serializers import HealthAssessmentInputSerializer
        
        data = {
            'symptoms': ['fever'],
            # Missing age and gender
        }
        
        serializer = HealthAssessmentInputSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('age', serializer.errors)
        self.assertIn('gender', serializer.errors)
    
    def test_invalid_age(self):
        """Test that invalid age is rejected."""
        from api.serializers import HealthAssessmentInputSerializer
        
        data = {
            'symptoms': ['fever'],
            'age': 150,  # Invalid age
            'gender': 'male'
        }
        
        serializer = HealthAssessmentInputSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('age', serializer.errors)
    
    def test_invalid_gender(self):
        """Test that invalid gender is rejected."""
        from api.serializers import HealthAssessmentInputSerializer
        
        data = {
            'symptoms': ['fever'],
            'age': 35,
            'gender': 'invalid'  # Invalid gender
        }
        
        serializer = HealthAssessmentInputSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('gender', serializer.errors)
    
    def test_optional_fields(self):
        """Test that optional fields work correctly."""
        from api.serializers import HealthAssessmentInputSerializer
        
        data = {
            'symptoms': ['fever', 'cough'],
            'age': 35,
            'gender': 'male',
            'user_id': 'test_user',
            'additional_info': {'weight': 70, 'height': 175}
        }
        
        serializer = HealthAssessmentInputSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user_id'], 'test_user')
        self.assertEqual(serializer.validated_data['additional_info']['weight'], 70)
