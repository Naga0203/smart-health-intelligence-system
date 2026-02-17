"""
API Views for AI Health Intelligence System

REST API endpoints for health assessment and disease prediction.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    PermissionDenied,
    NotFound,
    NotFound,
    Throttled
)
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from datetime import datetime
import logging
import traceback

from agents.orchestrator import OrchestratorAgent
from prediction.predictor import DiseasePredictor
from common.firebase_auth import FirebaseAuthentication
from .serializers import (
    HealthAssessmentInputSerializer,
    HealthAssessmentOutputSerializer,
    SystemStatusSerializer,
    ModelInfoSerializer,
    TopPredictionsInputSerializer,
    DiseaseInfoSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserStatisticsSerializer,
    AssessmentHistorySerializer,
    AssessmentDetailSerializer
)
from .throttling import (
    HealthAnalysisRateThrottle,
    HealthAnalysisBurstRateThrottle,
    AnonymousHealthAnalysisThrottle,
    IPBasedRateThrottle,
    DailyRateThrottle,
    RateLimitExceededLogger
)

logger = logging.getLogger('health_ai.api')


class APIErrorHandler:
    """
    Centralized error handling for API views.
    
    Provides consistent error responses with appropriate HTTP status codes.
    """
    
    @staticmethod
    def handle_validation_error(error, logger_instance=None):
        """Handle validation errors (400 Bad Request)."""
        if logger_instance:
            logger_instance.warning(f"Validation error: {error}")
        
        return Response(
            {
                "error": "validation_error",
                "message": "Invalid input data",
                "details": str(error) if isinstance(error, str) else error,
                "status_code": 400
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @staticmethod
    def handle_authentication_error(error, logger_instance=None):
        """Handle authentication errors (401 Unauthorized)."""
        if logger_instance:
            logger_instance.warning(f"Authentication error: {error}")
        
        return Response(
            {
                "error": "authentication_error",
                "message": "Authentication failed",
                "details": str(error),
                "status_code": 401
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def handle_permission_error(error, logger_instance=None):
        """Handle permission errors (403 Forbidden)."""
        if logger_instance:
            logger_instance.warning(f"Permission error: {error}")
        
        return Response(
            {
                "error": "permission_error",
                "message": "Permission denied",
                "details": str(error),
                "status_code": 403
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def handle_not_found_error(error, logger_instance=None):
        """Handle not found errors (404 Not Found)."""
        if logger_instance:
            logger_instance.warning(f"Not found error: {error}")
        
        return Response(
            {
                "error": "not_found",
                "message": "Resource not found",
                "details": str(error),
                "status_code": 404
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def handle_rate_limit_error(error, logger_instance=None):
        """Handle rate limiting errors (429 Too Many Requests)."""
        if logger_instance:
            logger_instance.warning(f"Rate limit exceeded: {error}")
        
        wait_time = getattr(error, 'wait', None)
        details = f"Rate limit exceeded. Please try again in {wait_time} seconds." if wait_time else "Rate limit exceeded."
        
        return Response(
            {
                "error": "rate_limit_exceeded",
                "message": "Too many requests",
                "details": details,
                "wait_seconds": wait_time,
                "status_code": 429
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    @staticmethod
    def handle_internal_error(error, logger_instance=None, include_traceback=False):
        """Handle internal server errors (500 Internal Server Error)."""
        if logger_instance:
            logger_instance.error(f"Internal error: {error}", exc_info=True)
        
        response_data = {
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "details": str(error),
            "status_code": 500
        }
        
        if include_traceback:
            response_data["traceback"] = traceback.format_exc()
        
        return Response(
            response_data,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @staticmethod
    def handle_service_unavailable(error, logger_instance=None):
        """Handle service unavailable errors (503 Service Unavailable)."""
        if logger_instance:
            logger_instance.error(f"Service unavailable: {error}")
        
        return Response(
            {
                "error": "service_unavailable",
                "message": "Service temporarily unavailable",
                "details": str(error),
                "status_code": 503
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


class HealthAnalysisAPI(APIView):
    """
    Primary health analysis endpoint with Firebase authentication.
    
    This is the main endpoint for authenticated health assessments.
    Requires Firebase ID token in Authorization header.
    
    Rate Limiting:
    - 10 requests per minute (burst protection)
    - 100 requests per hour (sustained usage)
    - 200 requests per day (daily limit)
    - IP-based limit: 200 requests per hour
    
    Validates: Requirements 7.1, 3.4, 3.5, 6.6, 11.2.3
    """
    
    authentication_classes = [FirebaseAuthentication]
    throttle_classes = [
        HealthAnalysisBurstRateThrottle,  # 10/min burst protection
        HealthAnalysisRateThrottle,       # 100/hour sustained
        DailyRateThrottle,                # 200/day daily limit
        IPBasedRateThrottle,              # 200/hour per IP
    ]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def _format_low_confidence_response(self, result_data):
        """
        Format response for LOW confidence predictions.
        
        LOW confidence responses are heavily limited and encourage
        users to provide more information or consult professionals.
        """
        return {
            "status": "low_confidence",
            "confidence": "LOW",
            "message": "Insufficient information for reliable assessment",
            "suggestion": "Please provide more specific symptoms or consult a healthcare professional",
            "prediction": {
                "disease": result_data.get('prediction', {}).get('disease'),
                "probability_percent": result_data.get('prediction', {}).get('probability_percent'),
                "confidence": "LOW"
            },
            "explanation": {
                "text": result_data.get('explanation', {}).get('text', 
                    "The provided symptoms are too general or insufficient for a reliable assessment."),
                "confidence": "LOW"
            },
            "disclaimer": "This is not a medical diagnosis. Please consult healthcare professionals for medical advice.",
            "metadata": {
                "timestamp": result_data.get('metadata', {}).get('timestamp'),
                "assessment_id": result_data.get('assessment_id')
            }
        }
    
    def _format_medium_confidence_response(self, result_data):
        """
        Format response for MEDIUM confidence predictions.
        
        MEDIUM confidence responses provide cautious guidance with
        treatment information and clear disclaimers.
        """
        return {
            "status": "success",
            "confidence": "MEDIUM",
            "message": "Assessment completed with moderate confidence",
            "user_id": result_data.get('user_id'),
            "assessment_id": result_data.get('assessment_id'),
            "prediction": result_data.get('prediction', {}),
            "extraction": result_data.get('extraction', {}),
            "explanation": result_data.get('explanation', {}),
            "recommendations": result_data.get('recommendations', {}),
            "treatment_info": result_data.get('treatment_info', {}),
            "disclaimer": "This is not a medical diagnosis. Treatment information is educational only. Please consult healthcare professionals before taking any action.",
            "metadata": result_data.get('metadata', {})
        }
    
    def _format_high_confidence_response(self, result_data):
        """
        Format response for HIGH confidence predictions.
        
        HIGH confidence responses provide full information with
        comprehensive treatment details and explanations.
        """
        return {
            "status": "success",
            "confidence": "HIGH",
            "message": "Assessment completed with high confidence",
            "user_id": result_data.get('user_id'),
            "assessment_id": result_data.get('assessment_id'),
            "prediction": result_data.get('prediction', {}),
            "extraction": result_data.get('extraction', {}),
            "explanation": result_data.get('explanation', {}),
            "recommendations": result_data.get('recommendations', {}),
            "treatment_info": result_data.get('treatment_info', {}),
            "risk_factors": result_data.get('risk_factors', []),
            "disclaimer": "This is not a medical diagnosis. Treatment information is educational only. Please consult healthcare professionals for personalized medical advice.",
            "metadata": result_data.get('metadata', {})
        }
    
    def _format_response_by_confidence(self, result_data):
        """
        Format response based on confidence level.
        
        Routes to appropriate formatter based on confidence level.
        """
        confidence = result_data.get('prediction', {}).get('confidence', 'LOW')
        
        if confidence == 'LOW':
            return self._format_low_confidence_response(result_data)
        elif confidence == 'MEDIUM':
            return self._format_medium_confidence_response(result_data)
        elif confidence == 'HIGH':
            return self._format_high_confidence_response(result_data)
        else:
            # Default to low confidence format for unknown confidence levels
            return self._format_low_confidence_response(result_data)
    
    @extend_schema(
        tags=['Health Analysis'],
        summary='Perform authenticated health analysis',
        description='''
        Perform complete health analysis with Firebase authentication.
        
        This is the primary endpoint for authenticated health assessments. It processes user symptoms
        through a multi-agent pipeline including validation, data extraction, ML prediction, 
        AI explanation, and ethical recommendation gating.
        
        **Authentication Required**: Firebase ID token in Authorization header
        
        **Rate Limits**:
        - 10 requests per minute (burst protection)
        - 100 requests per hour (sustained usage)
        - 200 requests per day (daily limit)
        - 200 requests per hour per IP
        
        **Confidence-Based Responses**:
        - LOW confidence: Limited response with suggestion to provide more information
        - MEDIUM confidence: Cautious guidance with treatment information
        - HIGH confidence: Full information with comprehensive details
        ''',
        request=HealthAssessmentInputSerializer,
        responses={
            200: OpenApiExample(
                'High Confidence Response',
                value={
                    "status": "success",
                    "confidence": "HIGH",
                    "message": "Assessment completed with high confidence",
                    "user_id": "firebase_user_uid",
                    "assessment_id": "assessment_doc_id_123",
                    "prediction": {
                        "disease": "Diabetes",
                        "probability": 0.78,
                        "probability_percent": 78.0,
                        "confidence": "HIGH",
                        "model_version": "v1.0"
                    },
                    "extraction": {
                        "confidence": 0.85,
                        "method": "gemini_ai_extraction",
                        "extracted_features": ["glucose", "bmi", "age"]
                    },
                    "explanation": {
                        "text": "Based on the symptoms provided including increased thirst, frequent urination, and fatigue, combined with your age and other factors, there is a high probability of diabetes risk. These symptoms are classic indicators of elevated blood glucose levels.",
                        "generated_by": "gemini",
                        "confidence": "HIGH"
                    },
                    "recommendations": {
                        "items": [
                            "Consult an endocrinologist or primary care physician",
                            "Get blood glucose testing (fasting and HbA1c)",
                            "Monitor symptoms and keep a health diary",
                            "Consider lifestyle modifications"
                        ],
                        "urgency": "medium",
                        "confidence": "HIGH"
                    },
                    "treatment_info": {
                        "allopathy": {
                            "approach": "Blood sugar monitoring and medication management",
                            "focus": "Insulin regulation and glucose control",
                            "disclaimer": "Requires medical supervision"
                        },
                        "ayurveda": {
                            "approach": "Diet regulation and lifestyle balance",
                            "focus": "Holistic body constitution and natural remedies",
                            "disclaimer": "Consult qualified Ayurvedic practitioner"
                        },
                        "lifestyle": {
                            "approach": "Diet, exercise, and stress management",
                            "focus": "Preventive care and healthy habits",
                            "disclaimer": "General wellness information only"
                        }
                    },
                    "risk_factors": [
                        "Age over 45",
                        "Family history of diabetes",
                        "Sedentary lifestyle"
                    ],
                    "disclaimer": "This is not a medical diagnosis. Treatment information is educational only. Please consult healthcare professionals for personalized medical advice.",
                    "metadata": {
                        "processing_time_seconds": 2.5,
                        "timestamp": "2026-02-10T12:00:00Z",
                        "storage_ids": {
                            "assessment": "assessment_doc_id_123",
                            "prediction": "prediction_doc_id_456",
                            "explanation": "explanation_doc_id_789"
                        },
                        "pipeline_version": "v1.0"
                    }
                },
                response_only=True
            ),
            400: OpenApiExample(
                'Validation Error',
                value={
                    "error": "validation_error",
                    "message": "Invalid input data",
                    "details": {
                        "age": ["This field is required."],
                        "symptoms": ["This field is required."]
                    },
                    "status_code": 400
                },
                response_only=True
            ),
            401: OpenApiExample(
                'Authentication Failed',
                value={
                    "error": "authentication_error",
                    "message": "Authentication failed",
                    "details": "Invalid or expired Firebase ID token",
                    "status_code": 401
                },
                response_only=True
            ),
            429: OpenApiExample(
                'Rate Limit Exceeded',
                value={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests",
                    "details": "Rate limit exceeded. Please try again in 60 seconds.",
                    "wait_seconds": 60,
                    "status_code": 429
                },
                response_only=True
            ),
            500: OpenApiExample(
                'Internal Server Error',
                value={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred",
                    "details": "Error processing assessment",
                    "status_code": 500
                },
                response_only=True
            )
        },
        examples=[
            OpenApiExample(
                'Basic Health Assessment',
                value={
                    "symptoms": ["increased thirst", "frequent urination", "fatigue"],
                    "age": 45,
                    "gender": "male",
                    "additional_info": {
                        "weight": 85,
                        "height": 175,
                        "family_history": ["diabetes"]
                    }
                },
                request_only=True
            ),
            OpenApiExample(
                'Minimal Assessment',
                value={
                    "symptoms": ["fever", "cough"],
                    "age": 30,
                    "gender": "female"
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        """
        POST /api/health/analyze
        
        Perform complete health analysis with Firebase authentication.
        
        Headers:
        Authorization: Bearer <firebase_id_token>
        
        Request Body:
        {
            "symptoms": ["fever", "cough", "headache"],
            "age": 35,
            "gender": "male",
            "additional_info": {"weight": 70, "height": 175}
        }
        
        Response (HIGH confidence):
        {
            "user_id": "firebase_uid",
            "assessment_id": "...",
            "prediction": {
                "disease": "Diabetes",
                "probability": 0.78,
                "probability_percent": 78.0,
                "confidence": "HIGH",
                "model_version": "v1.0"
            },
            "extraction": {
                "confidence": 0.85,
                "method": "gemini_ai_extraction"
            },
            "explanation": {
                "text": "Based on the symptoms provided...",
                "generated_by": "gemini",
                "confidence": "HIGH"
            },
            "recommendations": {
                "items": ["Consult healthcare professional", ...],
                "urgency": "medium",
                "confidence": "HIGH"
            },
            "metadata": {
                "processing_time_seconds": 2.5,
                "timestamp": "2026-02-09T...",
                "storage_ids": {...},
                "pipeline_version": "v1.0"
            }
        }
        
        Response (LOW confidence):
        {
            "blocked": true,
            "reason": "low_confidence",
            "message": "Insufficient information for reliable assessment",
            "details": {...}
        }
        
        Error Responses:
        - 400: Invalid input data
        - 401: Authentication failed
        - 429: Rate limit exceeded
        - 500: Internal server error
        - 503: Service unavailable
        """
        try:
            # Extract user_id from authenticated Firebase user
            user_id = request.user.uid
            
            logger.info(f"Health analysis request from user: {user_id}")
            
            # Validate input
            serializer = HealthAssessmentInputSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Invalid input from user {user_id}: {serializer.errors}")
                return APIErrorHandler.handle_validation_error(serializer.errors, logger)
            
            # Initialize orchestrator
            orchestrator = OrchestratorAgent()
            
            # Add user_id to validated data
            input_data = serializer.validated_data
            input_data['user_id'] = user_id
            
            # Process through complete pipeline
            result = orchestrator.process(input_data)
            
            if result.get('success'):
                response_data = result['data']
                
                # Check if response was blocked
                if response_data.get('blocked'):
                    return Response(
                        response_data,
                        status=status.HTTP_200_OK
                    )
                
                # Format response based on confidence level
                formatted_response = self._format_response_by_confidence(response_data)
                
                # Return successful assessment
                return Response(
                    formatted_response,
                    status=status.HTTP_200_OK
                )
            else:
                # Handle orchestrator failure
                error_message = result.get('message', 'Assessment failed')
                logger.error(f"Assessment failed for user {user_id}: {error_message}")
                
                # Check if it's a service availability issue
                if 'unavailable' in error_message.lower() or 'timeout' in error_message.lower():
                    return APIErrorHandler.handle_service_unavailable(error_message, logger)
                
                return Response(
                    {
                        "error": "assessment_failed",
                        "message": error_message,
                        "details": result.get('data', {}),
                        "status_code": 500
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except ValidationError as e:
            return APIErrorHandler.handle_validation_error(e, logger)
        
        except AuthenticationFailed as e:
            return APIErrorHandler.handle_authentication_error(e, logger)
        
        except PermissionDenied as e:
            return APIErrorHandler.handle_permission_error(e, logger)
        
        except Throttled as e:
            # Log rate limit exceeded event
            RateLimitExceededLogger.log_rate_limit_exceeded(
                request, 
                e.__class__.__name__,
                e.wait
            )
            return APIErrorHandler.handle_rate_limit_error(e, logger)
        
        except Exception as e:
            logger.error(f"Unexpected error for user {request.user.uid if hasattr(request.user, 'uid') else 'unknown'}: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_internal_error(e, logger)


class HealthAssessmentView(APIView):
    """
    Main endpoint for health assessment.
    
    Accepts user symptoms and returns disease prediction with explanation.
    
    Rate Limiting:
    - Anonymous users: 5 requests per hour
    - IP-based limit: 200 requests per hour
    """
    
    authentication_classes = []  # Allow unauthenticated access
    permission_classes = []  # Allow any user
    throttle_classes = [
        AnonymousHealthAnalysisThrottle,  # 5/hour for anonymous
        IPBasedRateThrottle,              # 200/hour per IP
    ]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    @extend_schema(
        tags=['Health Analysis'],
        summary='Perform health assessment (unauthenticated)',
        description='''
        Perform health assessment based on symptoms without authentication.
        
        This endpoint allows anonymous users to get health assessments with limited rate limits.
        For better rate limits and history tracking, use the authenticated endpoint.
        
        **No Authentication Required**
        
        **Rate Limits**:
        - Anonymous users: 5 requests per hour
        - IP-based limit: 200 requests per hour
        ''',
        request=HealthAssessmentInputSerializer,
        responses={
            200: OpenApiExample(
                'Assessment Result',
                value={
                    "user_id": "anonymous_or_provided_id",
                    "assessment_id": "assessment_doc_id_123",
                    "prediction": {
                        "disease": "Common Cold",
                        "probability": 0.72,
                        "probability_percent": 72.0,
                        "confidence": "MEDIUM"
                    },
                    "explanation": {
                        "text": "Based on your symptoms...",
                        "generated_by": "gemini",
                        "confidence": "MEDIUM"
                    },
                    "recommendations": {
                        "items": ["Rest and hydration", "Monitor symptoms"],
                        "urgency": "low",
                        "confidence": "MEDIUM"
                    },
                    "metadata": {
                        "processing_time_seconds": 2.1,
                        "timestamp": "2026-02-10T12:00:00Z"
                    }
                },
                response_only=True
            ),
            429: OpenApiExample(
                'Rate Limit Exceeded',
                value={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests",
                    "details": "Rate limit exceeded. Please try again in 3600 seconds.",
                    "wait_seconds": 3600,
                    "status_code": 429
                },
                response_only=True
            )
        },
        examples=[
            OpenApiExample(
                'Anonymous Assessment',
                value={
                    "symptoms": ["fever", "cough", "sore throat"],
                    "age": 28,
                    "gender": "female"
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        """
        POST /api/assess
        
        Perform health assessment based on symptoms.
        
        Request Body:
        {
            "symptoms": ["fever", "cough", "headache"],
            "age": 35,
            "gender": "male",
            "user_id": "optional_user_id",
            "additional_info": {"weight": 70, "height": 175}
        }
        
        Response:
        {
            "user_id": "...",
            "assessment_id": "...",
            "prediction": {
                "disease": "Influenza",
                "probability": 0.85,
                "probability_percent": 85.0,
                "confidence": "HIGH"
            },
            "explanation": {...},
            "recommendations": {...},
            "metadata": {...}
        }
        
        Error Responses:
        - 400: Invalid input data
        - 429: Rate limit exceeded
        - 500: Internal server error
        - 503: Service unavailable
        """
        try:
            # Validate input
            serializer = HealthAssessmentInputSerializer(data=request.data)
            if not serializer.is_valid():
                return APIErrorHandler.handle_validation_error(serializer.errors, logger)
            
            # Initialize orchestrator
            orchestrator = OrchestratorAgent()
            
            # Process assessment
            result = orchestrator.process(serializer.validated_data)
            
            if result.get('success'):
                return Response(result['data'], status=status.HTTP_200_OK)
            else:
                error_message = result.get('message', 'Assessment failed')
                
                # Check if it's a service availability issue
                if 'unavailable' in error_message.lower() or 'timeout' in error_message.lower():
                    return APIErrorHandler.handle_service_unavailable(error_message, logger)
                
                return Response(
                    {
                        "error": "assessment_failed",
                        "message": error_message,
                        "status_code": 500
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except ValidationError as e:
            return APIErrorHandler.handle_validation_error(e, logger)
        
        except Throttled as e:
            return APIErrorHandler.handle_rate_limit_error(e, logger)
        
        except Exception as e:
            logger.error(f"Assessment error: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_internal_error(e, logger)


class TopPredictionsView(APIView):
    """
    Get top N disease predictions.
    
    Returns multiple possible diseases ranked by probability.
    """
    
    authentication_classes = []  # Allow unauthenticated access
    permission_classes = []  # Allow any user
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    @extend_schema(
        tags=['Predictions'],
        summary='Get top N disease predictions',
        description='''
        Get top N disease predictions ranked by probability.
        
        Returns multiple possible diseases based on symptoms, ranked by prediction probability.
        
        **No Authentication Required**
        ''',
        request=TopPredictionsInputSerializer,
        responses={
            200: OpenApiExample(
                'Top Predictions',
                value=[
                    {"disease": "Influenza", "probability": 0.85, "rank": 1},
                    {"disease": "Common Cold", "probability": 0.72, "rank": 2},
                    {"disease": "Bronchitis", "probability": 0.68, "rank": 3},
                    {"disease": "Pneumonia", "probability": 0.55, "rank": 4},
                    {"disease": "Allergic Rhinitis", "probability": 0.48, "rank": 5}
                ],
                response_only=True
            )
        },
        examples=[
            OpenApiExample(
                'Get Top 5 Predictions',
                value={
                    "symptoms": ["fever", "cough", "headache"],
                    "age": 35,
                    "gender": "male",
                    "n": 5
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        """
        POST /api/predict/top
        
        Get top N disease predictions.
        
        Request Body:
        {
            "symptoms": ["fever", "cough"],
            "age": 35,
            "gender": "male",
            "n": 5
        }
        
        Response:
        [
            {"disease": "Influenza", "probability": 0.85, "rank": 1},
            {"disease": "Common Cold", "probability": 0.72, "rank": 2},
            ...
        ]
        
        Error Responses:
        - 400: Invalid input data
        - 429: Rate limit exceeded
        - 500: Internal server error
        """
        try:
            serializer = TopPredictionsInputSerializer(data=request.data)
            if not serializer.is_valid():
                return APIErrorHandler.handle_validation_error(serializer.errors, logger)
            
            # Initialize predictor
            predictor = DiseasePredictor()
            
            # Get top N predictions (simplified for mock)
            n = serializer.validated_data.get('n', 5)
            supported_diseases = predictor.get_supported_diseases()
            
            # Mock top predictions
            top_predictions = []
            for i, disease in enumerate(supported_diseases[:n]):
                top_predictions.append({
                    'disease': disease,
                    'probability': 0.7 - (i * 0.1),
                    'rank': i + 1
                })
            
            return Response(top_predictions, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return APIErrorHandler.handle_validation_error(e, logger)
        
        except Throttled as e:
            return APIErrorHandler.handle_rate_limit_error(e, logger)
        
        except Exception as e:
            logger.error(f"Top predictions error: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_internal_error(e, logger)


class SystemStatusView(APIView):
    """
    Get system status and health check.
    """
    
    authentication_classes = []  # Allow unauthenticated access
    permission_classes = []  # Allow any user
    
    @extend_schema(
        tags=['System'],
        summary='Get system status',
        description='''
        Get system status and component health check.
        
        Returns operational status of all system components including orchestrator,
        predictor, database, and external services.
        
        **No Authentication Required**
        ''',
        responses={
            200: OpenApiExample(
                'System Operational',
                value={
                    "status": "operational",
                    "version": "1.0",
                    "components": {
                        "orchestrator": {"status": "healthy", "version": "1.0"},
                        "predictor": {"status": "healthy", "models_loaded": 3},
                        "database": {"status": "connected", "type": "firebase"},
                        "gemini_ai": {"status": "available"}
                    },
                    "timestamp": "2026-02-10T12:00:00Z"
                },
                response_only=True
            ),
            503: OpenApiExample(
                'Service Unavailable',
                value={
                    "status": "error",
                    "error": "Database connection failed",
                    "timestamp": "2026-02-10T12:00:00Z"
                },
                response_only=True
            )
        }
    )
    def get(self, request):
        """
        GET /api/status
        
        Get system status.
        
        Response:
        {
            "status": "operational",
            "version": "1.0",
            "components": {
                "orchestrator": {...},
                "predictor": {...},
                "database": {...}
            },
            "timestamp": "2026-02-09T..."
        }
        
        Error Responses:
        - 500: Internal server error
        - 503: Service unavailable
        """
        try:
            orchestrator = OrchestratorAgent()
            pipeline_status = orchestrator.get_pipeline_status()
            
            return Response({
                "status": "operational",
                "version": "1.0",
                "components": pipeline_status,
                "timestamp": datetime.utcnow().isoformat()
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Status check error: {str(e)}", exc_info=True)
            return Response({
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class ModelInfoView(APIView):
    """
    Get information about the loaded model.
    """
    
    authentication_classes = []  # Allow unauthenticated access
    permission_classes = []  # Allow any user
    
    @extend_schema(
        tags=['System'],
        summary='Get model information',
        description='''
        Get information about the loaded ML model.
        
        Returns details about the disease prediction model including type, features, and device.
        
        **No Authentication Required**
        ''',
        responses={
            200: OpenApiExample(
                'Model Info',
                value={
                    "model_loaded": True,
                    "model_type": "pytorch",
                    "num_features": 132,
                    "num_diseases": 715,
                    "device": "cuda"
                },
                response_only=True
            ),
            503: OpenApiExample(
                'Model Not Available',
                value={
                    "error": "service_unavailable",
                    "message": "Service temporarily unavailable",
                    "details": "Failed to get model info: Model not loaded",
                    "status_code": 503
                },
                response_only=True
            )
        }
    )
    def get(self, request):
        """
        GET /api/model/info
        
        Get model information.
        
        Response:
        {
            "model_loaded": true,
            "model_type": "pytorch",
            "num_features": 132,
            "num_diseases": 715,
            "device": "cuda"
        }
        
        Error Responses:
        - 500: Internal server error
        - 503: Service unavailable
        """
        try:
            predictor = DiseasePredictor()
            supported_diseases = predictor.get_supported_diseases()
            
            model_info = {
                "model_loaded": True,
                "model_type": "mock",
                "model_version": predictor.model_version,
                "num_diseases": len(supported_diseases),
                "supported_diseases": supported_diseases
            }
            
            return Response(model_info, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Model info error: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_service_unavailable(
                f"Failed to get model info: {str(e)}", 
                logger
            )


class DiseasesListView(APIView):
    """
    Get list of all supported diseases.
    """
    
    authentication_classes = []  # Allow unauthenticated access
    permission_classes = []  # Allow any user
    
    @extend_schema(
        tags=['System'],
        summary='Get supported diseases list',
        description='''
        Get list of all diseases currently supported by the prediction model.
        
        **Currently Supported Diseases:**
        - Diabetes
        - Heart Disease
        - Hypertension
        
        More diseases will be added in future updates.
        
        **No Authentication Required**
        ''',
        responses={
            200: OpenApiExample(
                'Diseases List',
                value={
                    "total": 3,
                    "diseases": [
                        "diabetes",
                        "heart_disease",
                        "hypertension"
                    ]
                },
                response_only=True
            )
        }
    )
    def get(self, request):
        """
        GET /api/diseases
        
        Get list of all supported diseases.
        
        Response:
        {
            "total": 715,
            "diseases": ["Fungal infection", "Allergy", ...]
        }
        
        Error Responses:
        - 500: Internal server error
        - 503: Service unavailable
        """
        try:
            predictor = DiseasePredictor()
            diseases = predictor.get_supported_diseases()
            
            return Response({
                "total": len(diseases),
                "diseases": diseases
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Diseases list error: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_service_unavailable(
                f"Failed to get diseases list: {str(e)}", 
                logger
            )


@api_view(['GET'])
def health_check(request):
    """
    Simple health check endpoint.
    
    GET /api/health
    
    Response:
    {
        "status": "healthy",
        "timestamp": "2026-02-09T..."
    }
    """
    return Response({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }, status=status.HTTP_200_OK)




# ============================================================================
# User Profile and History APIs
# ============================================================================

class UserProfileAPIView(APIView):
    """
    User profile management endpoint.
    
    GET: Retrieve user profile
    PUT: Update user profile
    
    Requires Firebase authentication.
    Validates: Requirements 11.3.1, 11.3.2
    """
    
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [
        HealthAnalysisRateThrottle,  # 100/hour
    ]
    
    @extend_schema(
        tags=['User Profile'],
        summary='Get user profile',
        description='''
        Retrieve the authenticated user's profile from Firebase Firestore.
        
        If the user profile doesn't exist, it will be automatically created with default values
        from the Firebase Authentication data.
        
        **Authentication Required**: Firebase ID token
        ''',
        responses={
            200: OpenApiExample(
                'User Profile',
                value={
                    "uid": "firebase_user_uid_123",
                    "email": "user@example.com",
                    "display_name": "John Doe",
                    "photo_url": "https://example.com/photo.jpg",
                    "email_verified": True,
                    "created_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-02-10T00:00:00Z",
                    "last_login": "2026-02-10T12:00:00Z",
                    "phone_number": "+1234567890",
                    "date_of_birth": "1990-01-01",
                    "gender": "male",
                    "address": {
                        "street": "123 Main St",
                        "city": "New York",
                        "state": "NY",
                        "zip": "10001",
                        "country": "USA"
                    },
                    "emergency_contact": {
                        "name": "Jane Doe",
                        "relationship": "spouse",
                        "phone": "+1234567891"
                    },
                    "medical_history": ["diabetes", "hypertension"],
                    "allergies": ["penicillin"],
                    "current_medications": ["metformin", "lisinopril"]
                },
                response_only=True
            ),
            401: OpenApiExample(
                'Authentication Failed',
                value={
                    "error": "authentication_error",
                    "message": "Authentication failed",
                    "details": "Invalid or expired Firebase ID token",
                    "status_code": 401
                },
                response_only=True
            )
        }
    )
    def get(self, request):
        """
        GET /api/user/profile
        
        Retrieve the authenticated user's profile from Firebase.
        
        Headers:
        Authorization: Bearer <firebase_id_token>
        
        Response:
        {
            "uid": "firebase_uid",
            "email": "user@example.com",
            "display_name": "John Doe",
            "photo_url": "https://...",
            "email_verified": true,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-02-10T00:00:00Z",
            "last_login": "2026-02-10T12:00:00Z",
            "phone_number": "+1234567890",
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "address": {...},
            "emergency_contact": {...},
            "medical_history": [...],
            "allergies": [...],
            "current_medications": [...]
        }
        """
        try:
            from common.firebase_db import get_firebase_db
            
            user_id = request.user.uid
            logger.info(f"Fetching profile for user: {user_id}")
            
            # Get Firebase database
            # Get Firebase database
            db = get_firebase_db().db
            
            # Fetch user profile from Firestore
            user_doc = db.collection('users').document(user_id).get()
            
            if not user_doc.exists:
                # Create profile on first access
                logger.info(f"Creating new profile for user: {user_id}")
                profile_data = {
                    'uid': user_id,
                    'email': request.user.email,
                    'display_name': request.user.display_name or '',
                    'photo_url': getattr(request.user, 'photo_url', ''),
                    'email_verified': request.user.email_verified,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow(),
                    'last_login': datetime.utcnow(),
                    'phone_number': '',
                    'date_of_birth': None,
                    'gender': '',
                    'address': {},
                    'emergency_contact': {},
                    'medical_history': [],
                    'allergies': [],
                    'current_medications': []
                }
                db.collection('users').document(user_id).set(profile_data)
                
                return Response(profile_data, status=status.HTTP_200_OK)
            
            # Return existing profile
            profile_data = user_doc.to_dict()
            
            # Update last_login
            db.collection('users').document(user_id).update({
                'last_login': datetime.utcnow()
            })
            
            return Response(profile_data, status=status.HTTP_200_OK)
        
        except AuthenticationFailed as e:
            return APIErrorHandler.handle_authentication_error(e, logger)
        
        except Throttled as e:
            RateLimitExceededLogger.log_rate_limit_exceeded(request, e.__class__.__name__, e.wait)
            return APIErrorHandler.handle_rate_limit_error(e, logger)
        
        except Exception as e:
            logger.error(f"Error fetching profile for user {request.user.uid}: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_internal_error(e, logger)
    
    @extend_schema(
        tags=['User Profile'],
        summary='Update user profile',
        description='''
        Update the authenticated user's profile in Firebase Firestore.
        
        All fields are optional. Only provided fields will be updated.
        
        **Authentication Required**: Firebase ID token
        ''',
        request=UserProfileUpdateSerializer,
        responses={
            200: OpenApiExample(
                'Updated Profile',
                value={
                    "uid": "firebase_user_uid_123",
                    "email": "user@example.com",
                    "display_name": "John Doe Updated",
                    "phone_number": "+1234567890",
                    "date_of_birth": "1990-01-01",
                    "gender": "male",
                    "updated_at": "2026-02-10T12:30:00Z"
                },
                response_only=True
            ),
            400: OpenApiExample(
                'Validation Error',
                value={
                    "error": "validation_error",
                    "message": "Invalid input data",
                    "details": {
                        "date_of_birth": ["Date has wrong format. Use YYYY-MM-DD."]
                    },
                    "status_code": 400
                },
                response_only=True
            )
        },
        examples=[
            OpenApiExample(
                'Update Basic Info',
                value={
                    "display_name": "John Doe",
                    "phone_number": "+1234567890",
                    "date_of_birth": "1990-01-01",
                    "gender": "male"
                },
                request_only=True
            ),
            OpenApiExample(
                'Update Medical Info',
                value={
                    "medical_history": ["diabetes", "hypertension"],
                    "allergies": ["penicillin", "sulfa drugs"],
                    "current_medications": ["metformin", "lisinopril"]
                },
                request_only=True
            )
        ]
    )
    def put(self, request):
        """
        PUT /api/user/profile
        
        Update the authenticated user's profile.
        
        Headers:
        Authorization: Bearer <firebase_id_token>
        
        Request Body:
        {
            "display_name": "John Doe",
            "phone_number": "+1234567890",
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA"
            },
            "emergency_contact": {
                "name": "Jane Doe",
                "relationship": "spouse",
                "phone": "+1234567891"
            },
            "medical_history": ["diabetes", "hypertension"],
            "allergies": ["penicillin"],
            "current_medications": ["metformin"]
        }
        
        Response:
        {
            "uid": "firebase_uid",
            "email": "user@example.com",
            ...updated fields...
        }
        """
        try:
            from common.firebase_db import get_firebase_db
            
            user_id = request.user.uid
            logger.info(f"Updating profile for user: {user_id}")
            
            # Validate input
            serializer = UserProfileUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return APIErrorHandler.handle_validation_error(serializer.errors, logger)
            
            # Get Firebase database
            # Get Firebase database
            db = get_firebase_db().db
            
            # Prepare update data
            update_data = serializer.validated_data
            update_data['updated_at'] = datetime.utcnow()
            
            # Update profile in Firestore
            db.collection('users').document(user_id).update(update_data)
            
            # Fetch updated profile
            updated_doc = db.collection('users').document(user_id).get()
            profile_data = updated_doc.to_dict()
            
            logger.info(f"Profile updated successfully for user: {user_id}")
            
            return Response(profile_data, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return APIErrorHandler.handle_validation_error(e, logger)
        
        except AuthenticationFailed as e:
            return APIErrorHandler.handle_authentication_error(e, logger)
        
        except Throttled as e:
            RateLimitExceededLogger.log_rate_limit_exceeded(request, e.__class__.__name__, e.wait)
            return APIErrorHandler.handle_rate_limit_error(e, logger)
        
        except Exception as e:
            logger.error(f"Error updating profile for user {request.user.uid}: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_internal_error(e, logger)


class UserStatisticsAPIView(APIView):
    """
    User statistics endpoint.
    
    GET: Retrieve user statistics
    
    Requires Firebase authentication.
    Validates: Requirements 11.3.4
    """
    
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [HealthAnalysisRateThrottle]
    
    @extend_schema(
        tags=['User Profile'],
        summary='Get user statistics',
        description='''
        Retrieve statistics about the user's health assessments.
        
        Provides aggregate data including total assessments, confidence distribution,
        most common diseases, and account information.
        
        **Authentication Required**: Firebase ID token
        ''',
        responses={
            200: OpenApiExample(
                'User Statistics',
                value={
                    "total_assessments": 25,
                    "assessments_by_confidence": {
                        "LOW": 5,
                        "MEDIUM": 10,
                        "HIGH": 10
                    },
                    "most_common_diseases": [
                        {"disease": "Diabetes", "count": 8},
                        {"disease": "Hypertension", "count": 5},
                        {"disease": "Common Cold", "count": 3}
                    ],
                    "last_assessment_date": "2026-02-10T12:00:00Z",
                    "account_age_days": 45
                },
                response_only=True
            )
        }
    )
    def get(self, request):
        """
        GET /api/user/statistics
        
        Retrieve statistics about the user's assessments.
        
        Response:
        {
            "total_assessments": 25,
            "assessments_by_confidence": {
                "LOW": 5,
                "MEDIUM": 10,
                "HIGH": 10
            },
            "most_common_diseases": [
                {"disease": "Diabetes", "count": 8},
                {"disease": "Hypertension", "count": 5}
            ],
            "last_assessment_date": "2026-02-10T12:00:00Z",
            "account_age_days": 45
        }
        """
        try:
            from common.firebase_db import get_firebase_db
            
            user_id = request.user.uid
            logger.info(f"Fetching statistics for user: {user_id}")
            
            db = get_firebase_db().db
            
            # Get user profile for account age
            user_doc = db.collection('users').document(user_id).get()
            if not user_doc.exists:
                return Response({
                    "total_assessments": 0,
                    "assessments_by_confidence": {},
                    "most_common_diseases": [],
                    "last_assessment_date": None,
                    "account_age_days": 0
                }, status=status.HTTP_200_OK)
            
            user_data = user_doc.to_dict()
            created_at = user_data.get('created_at')
            account_age_days = (datetime.utcnow() - created_at).days if created_at else 0
            
            # Query assessments
            assessments_ref = db.collection('assessments').where('user_id', '==', user_id)
            assessments = list(assessments_ref.stream())
            
            # Calculate statistics
            total_assessments = len(assessments)
            confidence_counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0}
            disease_counts = {}
            last_assessment_date = None
            
            for assessment in assessments:
                data = assessment.to_dict()
                
                # Count by confidence
                confidence = data.get('confidence', 'LOW')
                confidence_counts[confidence] = confidence_counts.get(confidence, 0) + 1
                
                # Count by disease
                disease = data.get('disease', 'Unknown')
                disease_counts[disease] = disease_counts.get(disease, 0) + 1
                
                # Track last assessment
                created = data.get('created_at')
                if created and (not last_assessment_date or created > last_assessment_date):
                    last_assessment_date = created
            
            # Get most common diseases
            most_common = sorted(
                [{'disease': d, 'count': c} for d, c in disease_counts.items()],
                key=lambda x: x['count'],
                reverse=True
            )[:5]
            
            statistics = {
                'total_assessments': total_assessments,
                'assessments_by_confidence': confidence_counts,
                'most_common_diseases': most_common,
                'last_assessment_date': last_assessment_date,
                'account_age_days': account_age_days
            }
            
            return Response(statistics, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error fetching statistics for user {request.user.uid}: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_internal_error(e, logger)


class AssessmentHistoryAPIView(APIView):
    """
    Assessment history endpoint.
    
    GET: Retrieve user's assessment history with pagination
    
    Requires Firebase authentication.
    Validates: Requirements 11.4.1, 11.4.2
    """
    
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [HealthAnalysisRateThrottle]
    
    @extend_schema(
        tags=['Assessment History'],
        summary='Get assessment history',
        description='''
        Retrieve paginated assessment history for the authenticated user.
        
        Supports pagination, sorting, and filtering of past health assessments.
        
        **Authentication Required**: Firebase ID token
        
        **Query Parameters**:
        - `page`: Page number (default: 1)
        - `page_size`: Items per page (default: 10, max: 50)
        - `sort`: Sort field - created_at, confidence, disease (default: created_at)
        - `order`: Sort order - asc, desc (default: desc)
        ''',
        parameters=[
            OpenApiParameter('page', OpenApiTypes.INT, description='Page number (default: 1)'),
            OpenApiParameter('page_size', OpenApiTypes.INT, description='Items per page (default: 10, max: 50)'),
            OpenApiParameter('sort', OpenApiTypes.STR, description='Sort by: created_at, confidence, disease (default: created_at)'),
            OpenApiParameter('order', OpenApiTypes.STR, description='Order: asc, desc (default: desc)'),
        ],
        responses={
            200: OpenApiExample(
                'Assessment History',
                value={
                    "total": 25,
                    "page": 1,
                    "page_size": 10,
                    "assessments": [
                        {
                            "id": "assessment_id_1",
                            "created_at": "2026-02-10T12:00:00Z",
                            "disease": "Diabetes",
                            "probability": 0.78,
                            "confidence": "HIGH",
                            "symptoms": ["increased thirst", "frequent urination", "fatigue"],
                            "status": "completed"
                        },
                        {
                            "id": "assessment_id_2",
                            "created_at": "2026-02-09T10:30:00Z",
                            "disease": "Hypertension",
                            "probability": 0.65,
                            "confidence": "MEDIUM",
                            "symptoms": ["headache", "dizziness"],
                            "status": "completed"
                        }
                    ]
                },
                response_only=True
            )
        }
    )
    def get(self, request):
        """
        GET /api/user/assessments
        
        Retrieve paginated assessment history for the authenticated user.
        
        Query Parameters:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 10, max: 50)
        - sort: Sort field (created_at, confidence, disease)
        - order: Sort order (asc, desc)
        
        Response:
        {
            "total": 25,
            "page": 1,
            "page_size": 10,
            "assessments": [
                {
                    "id": "assessment_id",
                    "created_at": "2026-02-10T12:00:00Z",
                    "disease": "Diabetes",
                    "probability": 0.78,
                    "confidence": "HIGH",
                    "symptoms": ["fatigue", "increased_thirst"],
                    "status": "completed"
                },
                ...
            ]
        }
        """
        try:
            from common.firebase_db import get_firebase_db
            
            user_id = request.user.uid
            
            # Parse query parameters
            page = int(request.query_params.get('page', 1))
            page_size = min(int(request.query_params.get('page_size', 10)), 50)
            sort_field = request.query_params.get('sort', 'created_at')
            sort_order = request.query_params.get('order', 'desc')
            
            logger.info(f"Fetching assessment history for user: {user_id}, page: {page}, size: {page_size}")
            
            db = get_firebase_db().db
            
            # Query assessments
            assessments_ref = db.collection('assessments').where('user_id', '==', user_id)
            
            # Get all assessments
            all_assessments = []
            for doc in assessments_ref.stream():
                all_assessments.append(doc)
            
            # Apply sorting in Python to avoid Firestore index requirements
            reverse = (sort_order == 'desc')
            
            def get_sort_key(doc):
                data = doc.to_dict()
                return data.get(sort_field, '') or ''
                
            all_assessments.sort(key=get_sort_key, reverse=reverse)
            
            total = len(all_assessments)
            
            # Apply pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_assessments = all_assessments[start_idx:end_idx]
            
            # Format response
            assessments_data = []
            for assessment in paginated_assessments:
                data = assessment.to_dict()
                assessments_data.append({
                    'id': assessment.id,
                    'created_at': data.get('created_at'),
                    'disease': data.get('disease'),
                    'probability': data.get('probability'),
                    'confidence': data.get('confidence'),
                    'symptoms': data.get('symptoms', []),
                    'status': data.get('status', 'completed')
                })
            
            response_data = {
                'total': total,
                'page': page,
                'page_size': page_size,
                'assessments': assessments_data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except ValueError as e:
            return APIErrorHandler.handle_validation_error(f"Invalid query parameters: {str(e)}", logger)
        
        except Exception as e:
            import traceback
            with open('assessments_500_debug.txt', 'w') as f:
                f.write(f"Error fetching assessments: {str(e)}\n")
                f.write(traceback.format_exc())
            logger.error(f"Error fetching assessment history for user {request.user.uid}: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_internal_error(e, logger)


class AssessmentDetailAPIView(APIView):
    """
    Assessment detail endpoint.
    
    GET: Retrieve detailed information about a specific assessment
    
    Requires Firebase authentication.
    Validates: Requirements 11.4.3
    """
    
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [HealthAnalysisRateThrottle]
    
    @extend_schema(
        tags=['Assessment History'],
        summary='Get assessment details',
        description='''
        Retrieve detailed information about a specific assessment.
        
        Returns complete assessment data including symptoms, prediction, explanation,
        recommendations, and treatment information.
        
        **Authentication Required**: Firebase ID token
        
        **Authorization**: Users can only access their own assessments
        ''',
        responses={
            200: OpenApiExample(
                'Assessment Details',
                value={
                    "id": "assessment_id_123",
                    "user_id": "firebase_user_uid",
                    "created_at": "2026-02-10T12:00:00Z",
                    "symptoms": ["increased thirst", "frequent urination", "fatigue"],
                    "age": 45,
                    "gender": "male",
                    "disease": "Diabetes",
                    "probability": 0.78,
                    "confidence": "HIGH",
                    "extraction_data": {
                        "confidence": 0.85,
                        "method": "gemini_ai_extraction"
                    },
                    "prediction_metadata": {
                        "model_version": "v1.0",
                        "processing_time": 1.2
                    },
                    "explanation": {
                        "text": "Based on the symptoms provided...",
                        "generated_by": "gemini",
                        "confidence": "HIGH"
                    },
                    "recommendations": {
                        "items": ["Consult healthcare professional", "Get blood glucose testing"],
                        "urgency": "medium",
                        "confidence": "HIGH"
                    },
                    "status": "completed"
                },
                response_only=True
            ),
            404: OpenApiExample(
                'Assessment Not Found',
                value={
                    "error": "not_found",
                    "message": "Resource not found",
                    "details": "Assessment assessment_id_123 not found",
                    "status_code": 404
                },
                response_only=True
            ),
            403: OpenApiExample(
                'Permission Denied',
                value={
                    "error": "permission_error",
                    "message": "Permission denied",
                    "details": "You don't have permission to access this assessment",
                    "status_code": 403
                },
                response_only=True
            )
        }
    )
    def get(self, request, assessment_id):
        """
        GET /api/user/assessments/{assessment_id}
        
        Retrieve detailed information about a specific assessment.
        
        Response:
        {
            "id": "assessment_id",
            "user_id": "firebase_uid",
            "created_at": "2026-02-10T12:00:00Z",
            "symptoms": ["fatigue", "increased_thirst"],
            "age": 35,
            "gender": "male",
            "disease": "Diabetes",
            "probability": 0.78,
            "confidence": "HIGH",
            "extraction_data": {...},
            "prediction_metadata": {...},
            "explanation": {...},
            "recommendations": {...},
            "status": "completed"
        }
        """
        try:
            from common.firebase_db import get_firebase_db
            
            user_id = request.user.uid
            logger.info(f"Fetching assessment {assessment_id} for user: {user_id}")
            
            db = get_firebase_db().db
            
            # Fetch assessment
            assessment_doc = db.collection('assessments').document(assessment_id).get()
            
            if not assessment_doc.exists:
                return APIErrorHandler.handle_not_found_error(
                    f"Assessment {assessment_id} not found",
                    logger
                )
            
            assessment_data = assessment_doc.to_dict()
            
            # Verify ownership
            if assessment_data.get('user_id') != user_id:
                return APIErrorHandler.handle_permission_error(
                    "You don't have permission to access this assessment",
                    logger
                )
            
            # Add assessment ID to response
            assessment_data['id'] = assessment_id
            
            return Response(assessment_data, status=status.HTTP_200_OK)
        
        except NotFound as e:
            return APIErrorHandler.handle_not_found_error(e, logger)
        
        except PermissionDenied as e:
            return APIErrorHandler.handle_permission_error(e, logger)
        
        except Exception as e:
            logger.error(f"Error fetching assessment {assessment_id} for user {request.user.uid}: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_internal_error(e, logger)



# ============================================================================
# Medical Report Upload and Extraction APIs
# ============================================================================

class ReportUploadView(APIView):
    """
    Medical report upload endpoint.
    
    POST: Upload medical report file and initiate extraction
    
    Requires Firebase authentication.
    Validates: Requirements 2.4, 10.1, 10.2
    """
    
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [
        HealthAnalysisRateThrottle,  # 100/hour
    ]
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        tags=['Medical Reports'],
        summary='Upload medical report',
        description='''
        Upload a medical report file (PDF, JPG, PNG) and initiate extraction.
        
        The file will be stored securely in Firebase Storage and processed asynchronously
        to extract structured medical data using Google Gemini AI.
        
        **Authentication Required**: Firebase ID token
        
        **Supported Formats**: PDF, JPG, PNG
        **Maximum File Size**: 10MB
        
        **Rate Limits**:
        - 100 requests per hour (authenticated users)
        ''',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Medical report file (PDF, JPG, PNG)'
                    },
                    'assessment_type': {
                        'type': 'string',
                        'enum': ['lab_results', 'diagnosis', 'prescription', 'general'],
                        'description': 'Optional assessment type'
                    }
                },
                'required': ['file']
            }
        },
        responses={
            201: OpenApiExample(
                'Upload Successful',
                value={
                    "success": True,
                    "job_id": "550e8400-e29b-41d4-a716-446655440000",
                    "report_id": "660e8400-e29b-41d4-a716-446655440001",
                    "file_name": "lab_report.pdf",
                    "file_size": 245678,
                    "upload_timestamp": "2026-02-17T12:00:00Z",
                    "status": "processing",
                    "estimated_completion_seconds": 8
                },
                response_only=True
            ),
            400: OpenApiExample(
                'Invalid File',
                value={
                    "success": False,
                    "error_code": "invalid_format",
                    "message": "File validation failed",
                    "details": "Invalid file type: application/msword. Allowed types: PDF, JPG, PNG"
                },
                response_only=True
            ),
            401: OpenApiExample(
                'Authentication Failed',
                value={
                    "error": "authentication_error",
                    "message": "Authentication failed",
                    "details": "Invalid or expired Firebase ID token",
                    "status_code": 401
                },
                response_only=True
            ),
            413: OpenApiExample(
                'File Too Large',
                value={
                    "success": False,
                    "error_code": "file_too_large",
                    "message": "File validation failed",
                    "details": "File size 12.5MB exceeds maximum 10MB"
                },
                response_only=True
            ),
            500: OpenApiExample(
                'Upload Failed',
                value={
                    "success": False,
                    "error_code": "upload_failed",
                    "message": "Failed to upload file",
                    "details": "Storage service unavailable"
                },
                response_only=True
            )
        }
    )
    def post(self, request):
        """
        POST /api/reports/upload/
        
        Upload medical report file and initiate extraction.
        
        Headers:
        Authorization: Bearer <firebase_id_token>
        Content-Type: multipart/form-data
        
        Request Body (multipart/form-data):
        - file: Medical report file (PDF, JPG, PNG)
        - assessment_type: Optional assessment type (lab_results, diagnosis, prescription, general)
        
        Response (201 Created):
        {
            "success": true,
            "job_id": "550e8400-e29b-41d4-a716-446655440000",
            "report_id": "660e8400-e29b-41d4-a716-446655440001",
            "file_name": "lab_report.pdf",
            "file_size": 245678,
            "upload_timestamp": "2026-02-17T12:00:00Z",
            "status": "processing",
            "estimated_completion_seconds": 8
        }
        
        Error Responses:
        - 400: Invalid file format or validation failed
        - 401: Authentication failed
        - 413: File too large
        - 429: Rate limit exceeded
        - 500: Upload or processing failed
        """
        try:
            from api.file_storage import FileStorageService
            from api.extraction_jobs import ExtractionJobManager
            from agents.enhanced_extraction import EnhancedExtractionAgent
            
            # Extract user_id from authenticated Firebase user
            user_id = request.user.uid
            
            logger.info(f"Report upload request from user: {user_id}")
            
            # Validate file is present
            if 'file' not in request.FILES:
                return Response(
                    {
                        "success": False,
                        "error_code": "missing_file",
                        "message": "No file provided",
                        "details": "Request must include a 'file' field"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded_file = request.FILES['file']
            assessment_type = request.data.get('assessment_type', 'general')
            
            # Initialize services
            file_storage = FileStorageService()
            job_manager = ExtractionJobManager()
            
            # Step 1: Validate file
            validation_result = file_storage.validate_file(uploaded_file)
            if not validation_result.valid:
                logger.warning(f"File validation failed for user {user_id}: {validation_result.errors}")
                
                # Determine appropriate status code
                error_message = validation_result.errors[0] if validation_result.errors else "File validation failed"
                if "exceeds maximum" in error_message:
                    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                    error_code = "file_too_large"
                else:
                    status_code = status.HTTP_400_BAD_REQUEST
                    error_code = "invalid_format"
                
                return Response(
                    {
                        "success": False,
                        "error_code": error_code,
                        "message": "File validation failed",
                        "details": ", ".join(validation_result.errors)
                    },
                    status=status_code
                )
            
            # Step 2: Upload file to Firebase Storage
            try:
                upload_result = file_storage.upload_file(uploaded_file, user_id)
                report_id = upload_result['report_id']
                file_name = upload_result['file_name']
                file_size = upload_result['file_size']
                file_type = upload_result['content_type']
                storage_path = upload_result['storage_path']
                
                logger.info(f"File uploaded successfully: {report_id}, size: {file_size} bytes")
                
            except ValueError as e:
                # Validation error from upload_file
                logger.error(f"File upload validation error: {e}")
                return Response(
                    {
                        "success": False,
                        "error_code": "validation_error",
                        "message": str(e),
                        "details": str(e)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                # Storage error
                logger.error(f"File upload failed: {e}")
                return Response(
                    {
                        "success": False,
                        "error_code": "upload_failed",
                        "message": "Failed to upload file",
                        "details": str(e)
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Step 3: Create extraction job
            try:
                job_id = job_manager.create_job(report_id, user_id)
                logger.info(f"Extraction job created: {job_id}")
                
            except Exception as e:
                logger.error(f"Failed to create extraction job: {e}")
                # Clean up uploaded file
                try:
                    file_storage.delete_file(report_id, user_id)
                except:
                    pass
                
                return Response(
                    {
                        "success": False,
                        "error_code": "job_creation_failed",
                        "message": "Failed to create extraction job",
                        "details": str(e)
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Step 4: Store report metadata
            try:
                job_manager.store_report_metadata(
                    report_id=report_id,
                    user_id=user_id,
                    file_name=file_name,
                    file_size=file_size,
                    file_type=file_type,
                    storage_path=storage_path,
                    extraction_job_id=job_id
                )
                logger.info(f"Report metadata stored: {report_id}")
                
            except Exception as e:
                logger.error(f"Failed to store report metadata: {e}")
                # Continue anyway - metadata can be reconstructed
            
            # Step 5: Trigger async extraction (simplified - in production would use Celery)
            # For now, we'll update job status to processing and trigger extraction synchronously
            try:
                job_manager.update_job_status(job_id, 'processing', progress=10)
                
                # Trigger extraction in background (simplified)
                # In production, this would be: extract_medical_data_task.delay(job_id, report_id, user_id, file_type)
                extraction_agent = EnhancedExtractionAgent()
                
                # Get file stream
                file_stream = file_storage.get_file_stream(report_id, user_id)
                
                # Extract data
                extraction_result = extraction_agent.extract_from_report(file_stream, file_type)
                
                if extraction_result['success']:
                    # Mark job complete
                    job_manager.mark_job_complete(
                        job_id,
                        extraction_result['extracted_data'],
                        extraction_result['metadata']
                    )
                    logger.info(f"Extraction completed successfully: {job_id}")
                else:
                    # Mark job failed
                    job_manager.mark_job_failed(
                        job_id,
                        extraction_result.get('error_code', 'extraction_failed'),
                        extraction_result.get('message', 'Extraction failed'),
                        extraction_result.get('extracted_data')
                    )
                    logger.warning(f"Extraction failed: {job_id}")
                
            except Exception as e:
                logger.error(f"Extraction trigger failed: {e}")
                # Mark job as failed
                try:
                    job_manager.mark_job_failed(
                        job_id,
                        'extraction_trigger_failed',
                        f"Failed to trigger extraction: {str(e)}"
                    )
                except:
                    pass
            
            # Step 6: Return response
            upload_timestamp = datetime.utcnow().isoformat() + 'Z'
            
            response_data = {
                "success": True,
                "job_id": job_id,
                "report_id": report_id,
                "file_name": file_name,
                "file_size": file_size,
                "upload_timestamp": upload_timestamp,
                "status": "processing",
                "estimated_completion_seconds": 8
            }
            
            logger.info(f"Report upload successful for user {user_id}: {report_id}")
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        except AuthenticationFailed as e:
            return APIErrorHandler.handle_authentication_error(e, logger)
        
        except PermissionDenied as e:
            return APIErrorHandler.handle_permission_error(e, logger)
        
        except Throttled as e:
            RateLimitExceededLogger.log_rate_limit_exceeded(
                request,
                e.__class__.__name__,
                e.wait
            )
            return APIErrorHandler.handle_rate_limit_error(e, logger)
        
        except Exception as e:
            logger.error(f"Unexpected error in report upload for user {request.user.uid if hasattr(request.user, 'uid') else 'unknown'}: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_internal_error(e, logger)



class ExtractionStatusView(APIView):
    """
    Extraction status endpoint.
    
    GET: Check extraction job status and retrieve results
    
    Requires Firebase authentication.
    Validates: Requirements 10.3, 10.4
    """
    
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [
        HealthAnalysisRateThrottle,  # 100/hour
    ]
    parser_classes = [JSONParser]
    
    @extend_schema(
        tags=['Medical Reports'],
        summary='Get extraction job status',
        description='''
        Check the status of a medical report extraction job and retrieve results when complete.
        
        The extraction process is asynchronous. Poll this endpoint to check progress and
        retrieve extracted medical data when processing is complete.
        
        **Authentication Required**: Firebase ID token
        
        **Status Values**:
        - processing: Extraction in progress
        - complete: Extraction finished successfully
        - failed: Extraction failed with error details
        
        **Rate Limits**:
        - 100 requests per hour (authenticated users)
        ''',
        parameters=[
            OpenApiParameter(
                name='job_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='Extraction job ID (UUID)',
                required=True
            )
        ],
        responses={
            200: OpenApiExample(
                'Processing Status',
                value={
                    "job_id": "550e8400-e29b-41d4-a716-446655440000",
                    "status": "processing",
                    "progress_percent": 65,
                    "message": "Extracting medical data from report..."
                },
                response_only=True
            ),
            200: OpenApiExample(
                'Complete Status',
                value={
                    "job_id": "550e8400-e29b-41d4-a716-446655440000",
                    "status": "complete",
                    "extracted_data": {
                        "symptoms": ["fever", "cough", "fatigue"],
                        "vitals": {
                            "blood_pressure": "120/80",
                            "heart_rate": 72,
                            "temperature": 37.2,
                            "weight": 70.5,
                            "height": 175.0
                        },
                        "lab_results": [
                            {
                                "test_name": "Glucose",
                                "value": 95.0,
                                "unit": "mg/dL",
                                "reference_range": "70-100",
                                "date": "2026-02-15"
                            }
                        ],
                        "medications": [
                            {
                                "name": "Metformin",
                                "dosage": "500mg",
                                "frequency": "twice daily",
                                "start_date": "2026-01-10"
                            }
                        ],
                        "diagnoses": [
                            {
                                "condition": "Type 2 Diabetes",
                                "icd_code": "E11",
                                "date": "2026-01-10",
                                "status": "active"
                            }
                        ],
                        "confidence_scores": {
                            "overall": 0.85,
                            "symptoms": 0.90,
                            "vitals": 0.88,
                            "lab_results": 0.92,
                            "medications": 0.85,
                            "diagnoses": 0.80
                        }
                    },
                    "extraction_metadata": {
                        "extraction_time_seconds": 7.2,
                        "ocr_used": False,
                        "pages_processed": 3,
                        "gemini_model": "gemini-1.5-flash"
                    }
                },
                response_only=True
            ),
            200: OpenApiExample(
                'Failed Status',
                value={
                    "job_id": "550e8400-e29b-41d4-a716-446655440000",
                    "status": "failed",
                    "error_code": "unreadable",
                    "message": "Unable to extract text from report. File may be corrupted or password-protected.",
                    "partial_data": {}
                },
                response_only=True
            ),
            401: OpenApiExample(
                'Authentication Failed',
                value={
                    "error": "authentication_error",
                    "message": "Authentication failed",
                    "details": "Invalid or expired Firebase ID token",
                    "status_code": 401
                },
                response_only=True
            ),
            403: OpenApiExample(
                'Permission Denied',
                value={
                    "error": "permission_error",
                    "message": "Permission denied",
                    "details": "You do not have access to this extraction job",
                    "status_code": 403
                },
                response_only=True
            ),
            404: OpenApiExample(
                'Job Not Found',
                value={
                    "error": "not_found",
                    "message": "Resource not found",
                    "details": "Extraction job not found: 550e8400-e29b-41d4-a716-446655440000",
                    "status_code": 404
                },
                response_only=True
            ),
            500: OpenApiExample(
                'Internal Server Error',
                value={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred",
                    "details": "Failed to retrieve job status",
                    "status_code": 500
                },
                response_only=True
            )
        }
    )
    def get(self, request, job_id):
        """
        GET /api/reports/extract/{job_id}/
        
        Check extraction job status and retrieve results.
        
        Headers:
        Authorization: Bearer <firebase_id_token>
        
        Path Parameters:
        - job_id: Extraction job ID (UUID)
        
        Response (200 OK - Processing):
        {
            "job_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "processing",
            "progress_percent": 65,
            "message": "Extracting medical data from report..."
        }
        
        Response (200 OK - Complete):
        {
            "job_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "complete",
            "extracted_data": {
                "symptoms": [...],
                "vitals": {...},
                "lab_results": [...],
                "medications": [...],
                "diagnoses": [...],
                "confidence_scores": {...}
            },
            "extraction_metadata": {
                "extraction_time_seconds": 7.2,
                "ocr_used": false,
                "pages_processed": 3,
                "gemini_model": "gemini-1.5-flash"
            }
        }
        
        Response (200 OK - Failed):
        {
            "job_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "failed",
            "error_code": "unreadable",
            "message": "Unable to extract text from report",
            "partial_data": {}
        }
        
        Error Responses:
        - 401: Authentication failed
        - 403: Permission denied (not job owner)
        - 404: Job not found
        - 429: Rate limit exceeded
        - 500: Internal server error
        """
        try:
            from api.extraction_jobs import ExtractionJobManager
            
            # Extract user_id from authenticated Firebase user
            user_id = request.user.uid
            
            logger.info(f"Extraction status request from user: {user_id}, job_id: {job_id}")
            
            # Initialize job manager
            job_manager = ExtractionJobManager()
            
            # Step 1: Retrieve job status
            try:
                job_data = job_manager.get_job_status(job_id)
                
            except ValueError as e:
                # Job not found
                logger.warning(f"Job not found: {job_id}")
                return APIErrorHandler.handle_not_found_error(
                    f"Extraction job not found: {job_id}",
                    logger
                )
            except Exception as e:
                logger.error(f"Failed to retrieve job status: {e}")
                return APIErrorHandler.handle_internal_error(e, logger)
            
            # Step 2: Verify user has access to this job
            job_user_id = job_data.get('user_id')
            if job_user_id != user_id:
                logger.warning(f"User {user_id} attempted to access job {job_id} owned by {job_user_id}")
                return APIErrorHandler.handle_permission_error(
                    "You do not have access to this extraction job",
                    logger
                )
            
            # Step 3: Format response based on job status
            job_status = job_data.get('status')
            
            if job_status == 'processing' or job_status == 'pending':
                # Return processing status
                response_data = {
                    "job_id": job_id,
                    "status": "processing",
                    "progress_percent": job_data.get('progress_percent', 0),
                    "message": self._get_status_message(job_data.get('progress_percent', 0))
                }
                
                logger.debug(f"Job {job_id} is processing: {job_data.get('progress_percent', 0)}%")
                
                return Response(response_data, status=status.HTTP_200_OK)
            
            elif job_status == 'complete':
                # Return complete status with extracted data
                extracted_data = job_data.get('extracted_data', {})
                extraction_metadata = job_data.get('extraction_metadata', {})
                
                response_data = {
                    "job_id": job_id,
                    "status": "complete",
                    "extracted_data": extracted_data,
                    "extraction_metadata": extraction_metadata
                }
                
                logger.info(f"Job {job_id} completed successfully")
                
                return Response(response_data, status=status.HTTP_200_OK)
            
            elif job_status == 'failed':
                # Return failed status with error details
                error_info = job_data.get('error_info', {})
                partial_data = job_data.get('extracted_data', {})
                
                response_data = {
                    "job_id": job_id,
                    "status": "failed",
                    "error_code": error_info.get('error_code', 'unknown_error'),
                    "message": error_info.get('message', 'Extraction failed'),
                    "partial_data": partial_data
                }
                
                logger.warning(f"Job {job_id} failed: {error_info.get('error_code')}")
                
                return Response(response_data, status=status.HTTP_200_OK)
            
            else:
                # Unknown status
                logger.error(f"Unknown job status: {job_status} for job {job_id}")
                return Response(
                    {
                        "job_id": job_id,
                        "status": "unknown",
                        "message": f"Unknown job status: {job_status}"
                    },
                    status=status.HTTP_200_OK
                )
        
        except AuthenticationFailed as e:
            return APIErrorHandler.handle_authentication_error(e, logger)
        
        except PermissionDenied as e:
            return APIErrorHandler.handle_permission_error(e, logger)
        
        except Throttled as e:
            RateLimitExceededLogger.log_rate_limit_exceeded(
                request,
                e.__class__.__name__,
                e.wait
            )
            return APIErrorHandler.handle_rate_limit_error(e, logger)
        
        except Exception as e:
            logger.error(f"Unexpected error in extraction status for user {request.user.uid if hasattr(request.user, 'uid') else 'unknown'}: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_internal_error(e, logger)
    
    def _get_status_message(self, progress_percent: int) -> str:
        """
        Get human-readable status message based on progress.
        
        Args:
            progress_percent: Progress percentage (0-100)
            
        Returns:
            Status message string
        """
        if progress_percent < 20:
            return "Initializing extraction process..."
        elif progress_percent < 40:
            return "Reading report content..."
        elif progress_percent < 60:
            return "Extracting medical data..."
        elif progress_percent < 80:
            return "Validating extracted data..."
        elif progress_percent < 100:
            return "Finalizing extraction..."
        else:
            return "Processing complete"



class ReportMetadataView(APIView):
    """
    Report metadata endpoint.
    
    GET: Retrieve report metadata and download URL
    
    Requires Firebase authentication.
    Validates: Requirements 2.4, 10.5
    """
    
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [
        HealthAnalysisRateThrottle,  # 100/hour
    ]
    parser_classes = [JSONParser]
    
    @extend_schema(
        tags=['Medical Reports'],
        summary='Get report metadata',
        description='''
        Retrieve metadata for a medical report and generate a signed download URL.
        
        Returns information about the uploaded report including file details,
        upload timestamp, and a temporary signed URL for downloading the file.
        
        **Authentication Required**: Firebase ID token
        
        **Authorization**: Users can only access their own reports
        
        **Download URL**: Signed URL expires in 1 hour
        
        **Rate Limits**:
        - 100 requests per hour (authenticated users)
        ''',
        parameters=[
            OpenApiParameter(
                name='report_id',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='Report ID (UUID)',
                required=True
            )
        ],
        responses={
            200: OpenApiExample(
                'Report Metadata',
                value={
                    "report_id": "660e8400-e29b-41d4-a716-446655440001",
                    "user_id": "firebase_user_123",
                    "file_name": "lab_report.pdf",
                    "file_size": 245678,
                    "file_type": "application/pdf",
                    "upload_timestamp": "2026-02-17T12:00:00Z",
                    "download_url": "https://storage.googleapis.com/...",
                    "extraction_job_id": "550e8400-e29b-41d4-a716-446655440000",
                    "associated_assessment_id": "770e8400-e29b-41d4-a716-446655440002"
                },
                response_only=True
            ),
            401: OpenApiExample(
                'Authentication Failed',
                value={
                    "error": "authentication_error",
                    "message": "Authentication failed",
                    "details": "Invalid or expired Firebase ID token",
                    "status_code": 401
                },
                response_only=True
            ),
            403: OpenApiExample(
                'Permission Denied',
                value={
                    "error": "permission_error",
                    "message": "Permission denied",
                    "details": "You do not have access to this report",
                    "status_code": 403
                },
                response_only=True
            ),
            404: OpenApiExample(
                'Report Not Found',
                value={
                    "error": "not_found",
                    "message": "Resource not found",
                    "details": "Report not found: 660e8400-e29b-41d4-a716-446655440001",
                    "status_code": 404
                },
                response_only=True
            ),
            500: OpenApiExample(
                'Internal Server Error',
                value={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred",
                    "details": "Failed to retrieve report metadata",
                    "status_code": 500
                },
                response_only=True
            )
        }
    )
    def get(self, request, report_id):
        """
        GET /api/reports/{report_id}/
        
        Retrieve report metadata and download URL.
        
        Headers:
        Authorization: Bearer <firebase_id_token>
        
        Path Parameters:
        - report_id: Report ID (UUID)
        
        Response (200 OK):
        {
            "report_id": "660e8400-e29b-41d4-a716-446655440001",
            "user_id": "firebase_user_123",
            "file_name": "lab_report.pdf",
            "file_size": 245678,
            "file_type": "application/pdf",
            "upload_timestamp": "2026-02-17T12:00:00Z",
            "download_url": "https://storage.googleapis.com/...",
            "extraction_job_id": "550e8400-e29b-41d4-a716-446655440000",
            "associated_assessment_id": "770e8400-e29b-41d4-a716-446655440002"
        }
        
        Error Responses:
        - 401: Authentication failed
        - 403: Permission denied (not report owner)
        - 404: Report not found
        - 429: Rate limit exceeded
        - 500: Internal server error
        """
        try:
            from api.extraction_jobs import ExtractionJobManager
            from api.file_storage import FileStorageService
            
            # Extract user_id from authenticated Firebase user
            user_id = request.user.uid
            
            logger.info(f"Report metadata request from user: {user_id}, report_id: {report_id}")
            
            # Initialize services
            job_manager = ExtractionJobManager()
            file_storage = FileStorageService()
            
            # Step 1: Retrieve report metadata from Firestore
            try:
                report_data = job_manager.get_report_metadata(report_id)
                
            except ValueError as e:
                # Report not found
                logger.warning(f"Report not found: {report_id}")
                return APIErrorHandler.handle_not_found_error(
                    f"Report not found: {report_id}",
                    logger
                )
            except Exception as e:
                logger.error(f"Failed to retrieve report metadata: {e}")
                return APIErrorHandler.handle_internal_error(e, logger)
            
            # Step 2: Verify user has access to this report (authorization check)
            report_user_id = report_data.get('user_id')
            if report_user_id != user_id:
                logger.warning(f"User {user_id} attempted to access report {report_id} owned by {report_user_id}")
                return APIErrorHandler.handle_permission_error(
                    "You do not have access to this report",
                    logger
                )
            
            # Step 3: Generate signed download URL
            try:
                download_url = file_storage.get_file_url(
                    report_id=report_id,
                    user_id=user_id,
                    expiration_minutes=60
                )
                
                logger.info(f"Generated download URL for report: {report_id}")
                
            except FileNotFoundError as e:
                logger.error(f"File not found in storage for report {report_id}: {e}")
                return APIErrorHandler.handle_not_found_error(
                    f"Report file not found in storage: {report_id}",
                    logger
                )
            except Exception as e:
                logger.error(f"Failed to generate download URL: {e}")
                return APIErrorHandler.handle_internal_error(e, logger)
            
            # Step 4: Format response
            response_data = {
                "report_id": report_id,
                "user_id": report_data.get('user_id'),
                "file_name": report_data.get('file_name'),
                "file_size": report_data.get('file_size'),
                "file_type": report_data.get('file_type'),
                "upload_timestamp": report_data.get('upload_timestamp'),
                "download_url": download_url,
                "extraction_job_id": report_data.get('extraction_job_id'),
                "associated_assessment_id": report_data.get('associated_assessment_id')
            }
            
            logger.info(f"Report metadata retrieved successfully for user {user_id}: {report_id}")
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except AuthenticationFailed as e:
            return APIErrorHandler.handle_authentication_error(e, logger)
        
        except PermissionDenied as e:
            return APIErrorHandler.handle_permission_error(e, logger)
        
        except Throttled as e:
            RateLimitExceededLogger.log_rate_limit_exceeded(
                request,
                e.__class__.__name__,
                e.wait
            )
            return APIErrorHandler.handle_rate_limit_error(e, logger)
        
        except Exception as e:
            logger.error(f"Unexpected error in report metadata for user {request.user.uid if hasattr(request.user, 'uid') else 'unknown'}: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_internal_error(e, logger)
