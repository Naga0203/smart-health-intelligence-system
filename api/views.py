"""
API Views for AI Health Intelligence System

REST API endpoints for health assessment and disease prediction.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from datetime import datetime
import logging

from agents.orchestrator import OrchestratorAgent
from prediction.multi_disease_predictor import MultiDiseasePredictor
from .serializers import (
    HealthAssessmentInputSerializer,
    HealthAssessmentOutputSerializer,
    SystemStatusSerializer,
    ModelInfoSerializer,
    TopPredictionsInputSerializer,
    DiseaseInfoSerializer
)

logger = logging.getLogger('health_ai.api')


class HealthAssessmentView(APIView):
    """
    Main endpoint for health assessment.
    
    Accepts user symptoms and returns disease prediction with explanation.
    """
    
    @extend_schema(
        request=HealthAssessmentInputSerializer,
        responses={200: HealthAssessmentOutputSerializer},
        description="Perform complete health assessment based on symptoms"
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
        """
        # Validate input
        serializer = HealthAssessmentInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid input", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Initialize orchestrator
            orchestrator = OrchestratorAgent()
            
            # Process assessment
            result = orchestrator.process(serializer.validated_data)
            
            if result.get('success'):
                return Response(result['data'], status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": result.get('message', 'Assessment failed')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Assessment error: {str(e)}")
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TopPredictionsView(APIView):
    """
    Get top N disease predictions.
    
    Returns multiple possible diseases ranked by probability.
    """
    
    @extend_schema(
        request=TopPredictionsInputSerializer,
        responses={200: DiseaseInfoSerializer(many=True)},
        description="Get top N disease predictions"
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
        """
        serializer = TopPredictionsInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid input", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Initialize predictor
            predictor = MultiDiseasePredictor()
            
            # Prepare features (simplified - in production use data extraction agent)
            features = {f: 0 for f in predictor.get_feature_names()}
            
            # Get top N predictions
            n = serializer.validated_data.get('n', 5)
            top_predictions = predictor.predict_top_n(features, n=n)
            
            return Response(top_predictions, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Top predictions error: {str(e)}")
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SystemStatusView(APIView):
    """
    Get system status and health check.
    """
    
    @extend_schema(
        responses={200: SystemStatusSerializer},
        description="Get system status and component health"
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
            logger.error(f"Status check error: {str(e)}")
            return Response({
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ModelInfoView(APIView):
    """
    Get information about the loaded model.
    """
    
    @extend_schema(
        responses={200: ModelInfoSerializer},
        description="Get model information"
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
        """
        try:
            predictor = MultiDiseasePredictor()
            model_info = predictor.get_model_info()
            
            return Response(model_info, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Model info error: {str(e)}")
            return Response(
                {"error": "Failed to get model info", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DiseasesListView(APIView):
    """
    Get list of all supported diseases.
    """
    
    @extend_schema(
        responses={200: OpenApiTypes.OBJECT},
        description="Get list of all supported diseases"
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
        """
        try:
            predictor = MultiDiseasePredictor()
            diseases = predictor.get_supported_diseases()
            
            return Response({
                "total": len(diseases),
                "diseases": diseases
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Diseases list error: {str(e)}")
            return Response(
                {"error": "Failed to get diseases list", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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

