from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .ml.multihot_inference import predict_disease
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class SymptomPredictionView(APIView):
    """
    API View for symptom-based disease prediction using the multihot model.
    """
    
    def post(self, request):
        """
        Predict disease based on a list of symptoms.
        
        Payload:
        {
            "symptoms": ["fever", "cough", "headache", ...]
        }
        """
        try:
            symptoms = request.data.get('symptoms', [])
            
            # Support both list and string input
            if not symptoms:
                 return Response(
                    {"error": "Invalid input. 'symptoms' must be provided."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not isinstance(symptoms, (list, str)):
                return Response(
                    {"error": "Invalid input. 'symptoms' must be a list or a string."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Prepare input text
            if isinstance(symptoms, list):
                symptoms_text = " ".join(symptoms)
            else:
                symptoms_text = symptoms
            
            # Predict using the separate inference module
            prediction_result = predict_disease(symptoms_text)
            
            return Response(prediction_result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Symptom prediction error: {e}", exc_info=True)
            return Response(
                {"error": "An error occurred during prediction."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
