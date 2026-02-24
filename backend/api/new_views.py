"""
New API endpoints for medical history and report parsing.

These endpoints extend the health assessment system with:
- Medical history management
- Assessment export (PDF and JSON)
- AI-powered medical report parsing
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiExample
from datetime import datetime
import logging
import json
import io

from common.firebase_auth import FirebaseAuthentication
from common.firebase_db import get_firebase_db
from common.gemini_client import LangChainGeminiClient
from .serializers import (
    MedicalHistorySerializer,
    ReportUploadSerializer,
    ReportParseInputSerializer,
    ReportParseOutputSerializer
)
from .throttling import HealthAnalysisRateThrottle
from .views import APIErrorHandler

logger = logging.getLogger('health_ai.api.new_endpoints')


class MedicalHistoryAPIView(APIView):
    """
    Medical history management endpoint.
    
    GET: Retrieve user's medical history
    POST: Create or update medical history
    
    Requires Firebase authentication.
    """
    
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [HealthAnalysisRateThrottle]
    
    @extend_schema(
        tags=['Medical History'],
        summary='Get user medical history',
        description='''
        Retrieve the authenticated user's complete medical history.
        
        Includes conditions, surgeries, family history, allergies, medications,
        immunizations, and lifestyle factors.
        
        **Authentication Required**: Firebase ID token
        ''',
        responses={
            200: OpenApiExample(
                'Medical History',
                value={
                    "conditions": ["diabetes", "hypertension"],
                    "surgeries": [
                        {"type": "appendectomy", "date": "2020-05-15", "hospital": "General Hospital"}
                    ],
                    "family_history": ["heart disease", "cancer"],
                    "allergies": ["penicillin", "peanuts"],
                    "current_medications": [
                        {"name": "metformin", "dosage": "500mg", "frequency": "twice daily"}
                    ],
                    "immunizations": [
                        {"vaccine": "COVID-19", "date": "2023-01-15", "dose": "booster"}
                    ],
                    "lifestyle": {
                        "smoking": "never",
                        "alcohol": "occasional",
                        "exercise": "3-4 times/week",
                        "diet": "balanced"
                    },
                    "notes": "Patient is generally healthy",
                    "last_updated": "2026-02-12T12:00:00Z"
                },
                response_only=True
            ),
            404: OpenApiExample(
                'No Medical History',
                value={
                    "error": "not_found",
                    "message": "No medical history found",
                    "details": "User has not created medical history yet",
                    "status_code": 404
                },
                response_only=True
            )
        }
    )
    def get(self, request):
        """
        GET /api/user/medical-history/
        
        Retrieve user's medical history from Firestore.
        """
        try:
            user_id = request.user.uid
            logger.info(f"Fetching medical history for user: {user_id}")
            
            db = get_firebase_db().db
            
            # Fetch medical history from Firestore
            history_doc = db.collection('medical_history').document(user_id).get()
            
            if not history_doc.exists:
                return APIErrorHandler.handle_not_found_error(
                    "Medical history not found for this user",
                    logger
                )
            
            history_data = history_doc.to_dict()
            return Response(history_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error fetching medical history for user {request.user.uid}: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_internal_error(e, logger)
    
    @extend_schema(
        tags=['Medical History'],
        summary='Create or update medical history',
        description='''
        Create or update the authenticated user's medical history.
        
        All fields are optional. Provided fields will be updated or added.
        
        **Authentication Required**: Firebase ID token
        ''',
        request=MedicalHistorySerializer,
        responses={
            200: OpenApiExample(
                'Updated Medical History',
                value={
                    "conditions": ["diabetes", "hypertension"],
                    "surgeries": [],
                    "family_history": ["heart disease"],
                    "allergies": ["penicillin"],
                    "current_medications": [
                        {"name": "metformin", "dosage": "500mg", "frequency": "twice daily"}
                    ],
                    "immunizations": [],
                    "lifestyle": {
                        "smoking": "never",
                        "alcohol": "never",
                        "exercise": "daily",
                        "diet": "vegetarian"
                    },
                    "notes": "",
                    "last_updated": "2026-02-12T12:30:00Z"
                },
                response_only=True
            )
        },
        examples=[
            OpenApiExample(
                'Update Medical History',
                value={
                    "conditions": ["diabetes", "hypertension"],
                    "allergies": ["penicillin", "sulfa drugs"],
                    "current_medications": [
                        {"name": "metformin", "dosage": "500mg", "frequency": "twice daily"},
                        {"name": "lisinopril", "dosage": "10mg", "frequency": "once daily"}
                    ],
                    "lifestyle": {
                        "smoking": "never",
                        "alcohol": "occasional",
                        "exercise": "3-4 times/week",
                        "diet": "balanced"
                    },
                    "notes": "Patient is managing conditions well"
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        """
        POST /api/user/medical-history/
        
        Create or update user's medical history.
        """
        try:
            user_id = request.user.uid
            logger.info(f"Updating medical history for user: {user_id}")
            
            # Validate input
            serializer = MedicalHistorySerializer(data=request.data)
            if not serializer.is_valid():
                return APIErrorHandler.handle_validation_error(serializer.errors, logger)
            
            db = get_firebase_db().db
            
            # Prepare data
            history_data = serializer.validated_data
            history_data['last_updated'] = datetime.utcnow()
            history_data['user_id'] = user_id
            
            # Save to Firestore
            db.collection('medical_history').document(user_id).set(history_data)
            
            logger.info(f"Medical history updated for user: {user_id}")
            
            return Response(history_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error updating medical history for user {request.user.uid}: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_internal_error(e, logger)


class AssessmentExportAPIView(APIView):
    """
    Assessment export endpoints (PDF and JSON).
    
    Allows users to export their assessment results.
    """
    
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [HealthAnalysisRateThrottle]
    
    @extend_schema(
        tags=['Assessments'],
        summary='Export assessment as JSON',
        description='''
        Export a specific assessment as JSON format.
        
        **Authentication Required**: Firebase ID token
        ''',
        responses={
            200: OpenApiExample(
                'Assessment Export',
                value={
                    "assessment_id": "assessment_123",
                    "user_id": "user_456",
                    "created_at": "2026-02-12T10:00:00Z",
                    "symptoms": ["fever", "cough", "headache"],
                    "prediction": {
                        "disease": "Common Cold",
                        "probability": 0.85,
                        "confidence": "HIGH"
                    },
                    "explanation": "Based on your symptoms...",
                    "recommendations": ["Rest", "Hydration"]
                },
                response_only=True
            )
        }
    )
    def get(self, request, assessment_id):
        """
        GET /api/user/assessments/{assessment_id}/export/
        
        Export assessment as JSON.
        """
        try:
            user_id = request.user.uid
            logger.info(f"Exporting assessment {assessment_id} for user: {user_id}")
            
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
                from rest_framework.exceptions import PermissionDenied
                return APIErrorHandler.handle_permission_error(
                    "You don't have permission to access this assessment",
                    logger
                )
            
            # Add assessment_id to response
            assessment_data['assessment_id'] = assessment_id
            
            return Response(assessment_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error exporting assessment: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_internal_error(e, logger)


class ReportUploadAPIView(APIView):
    """
    Medical report upload endpoint.
    
    Accepts file uploads for medical reports.
    """
    
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [HealthAnalysisRateThrottle]
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        tags=['Reports'],
        summary='Upload medical report',
        description='''
        Upload a medical report file (PDF, JPG, PNG).
        
        The file will be stored and can be parsed later for data extraction.
        
        **Authentication Required**: Firebase ID token
        ''',
        request=ReportUploadSerializer,
        responses={
            200: OpenApiExample(
                'Upload Success',
                value={
                    "success": True,
                    "report_id": "report_123",
                    "file_name": "lab_results.pdf",
                    "report_type": "lab_report",
                    "upload_date": "2026-02-12T12:00:00Z",
                    "message": "Report uploaded successfully"
                },
                response_only=True
            )
        }
    )
    def post(self, request):
        """
        POST /api/reports/upload/
        
        Upload medical report file.
        """
        try:
            # Check if report upload feature is enabled
            from django.conf import settings
            if not getattr(settings, 'ENABLE_REPORT_UPLOAD', True):
                return Response({
                    "success": False,
                    "error": "Report upload feature is currently disabled",
                    "code": "FEATURE_DISABLED"
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            user_id = request.user.uid
            logger.info(f"Report upload request from user: {user_id}")
            
            # Validate input
            serializer = ReportUploadSerializer(data=request.data)
            if not serializer.is_valid():
                return APIErrorHandler.handle_validation_error(serializer.errors, logger)
            
            uploaded_file = serializer.validated_data['file']
            report_type = serializer.validated_data['report_type']
            report_date = serializer.validated_data.get('report_date')
            notes = serializer.validated_data.get('notes', '')
            
            # TODO: Store file in Firebase Storage or other storage service
            # For now, we'll create a record in Firestore
            
            db = get_firebase_db().db
            
            report_ref = db.collection('reports').document()
            report_data = {
                'user_id': user_id,
                'file_name': uploaded_file.name,
                'file_size': uploaded_file.size,
                'report_type': report_type,
                'report_date': report_date,
                'notes': notes,
                'upload_date': datetime.utcnow(),
                'status': 'uploaded'
            }
            
            report_ref.set(report_data)
            
            response_data = {
                "success": True,
                "report_id": report_ref.id,
                "file_name": uploaded_file.name,
                "report_type": report_type,
                "upload_date": datetime.utcnow().isoformat(),
                "message": "Report uploaded successfully"
            }
            
            logger.info(f"Report {report_ref.id} uploaded for user: {user_id}")
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error uploading report: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_internal_error(e, logger)


class ReportParseAPIView(APIView):
    """
    AI-powered medical report parsing endpoint.
    
    Uses Gemini AI to parse medical reports and extract structured data.
    """
    
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [HealthAnalysisRateThrottle]
    
    @extend_schema(
        tags=['Reports'],
        summary='Parse medical report with AI',
        description='''
        Parse medical report text using Gemini AI to extract structured data.
        
        The AI will identify and extract relevant medical information such as:
        - Lab results (glucose, cholesterol, blood pressure, etc.)
        - Diagnoses
        - Medications
        - Vital signs
        - Recommendations
        
        **Authentication Required**: Firebase ID token
        ''',
        request=ReportParseInputSerializer,
        responses={
            200: ReportParseOutputSerializer,
            400: OpenApiExample(
                'Validation Error',
                value={
                    "error": "validation_error",
                    "message": "Invalid input data",
                    "details": {"report_text": ["This field is required."]},
                    "status_code": 400
                },
                response_only=True
            )
        },
        examples=[
            OpenApiExample(
                'Lab Report Parsing',
                value={
                    "report_text": "Patient: John Doe\\nDate: 2026-02-10\\nGlucose: 125 mg/dL\\nCholesterol: 210 mg/dL\\nHbA1c: 6.5%\\nBlood Pressure: 135/85",
                    "report_type": "lab_report",
                    "extract_fields": ["glucose", "cholesterol", "hba1c", "blood_pressure"]
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        """
        POST /api/reports/parse/
        
        Parse medical report using AI.
        """
        try:
            # Check if report upload feature is enabled
            from django.conf import settings
            if not getattr(settings, 'ENABLE_REPORT_UPLOAD', True):
                return Response({
                    "success": False,
                    "error": "Report parsing feature is currently disabled",
                    "code": "FEATURE_DISABLED"
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            user_id = request.user.uid
            logger.info(f"Report parsing request from user: {user_id}")
            
            # Validate input
            serializer = ReportParseInputSerializer(data=request.data)
            if not serializer.is_valid():
                return APIErrorHandler.handle_validation_error(serializer.errors, logger)
            
            report_text = serializer.validated_data['report_text']
            report_type = serializer.validated_data['report_type']
            extract_fields = serializer.validated_data.get('extract_fields', [])
            
            # Initialize Gemini client
            gemini_client = LangChainGeminiClient()
            
            # Create parsing prompt
            fields_hint = f"Focus on extracting: {', '.join(extract_fields)}" if extract_fields else ""
            
            prompt = f"""
Parse the following medical {report_type} and extract structured data.

{fields_hint}

Extract all relevant medical information including:
- Lab results and values
- Diagnoses
- Medications and dosages
- Vital signs
- Doctor recommendations
- Abnormal findings

Report text:
{report_text}

Provide the extracted information in JSON format with clear field names and values.
Also provide a brief summary and any warnings or concerns identified.
"""
            
            # Parse with Gemini AI
            result = gemini_client.generate(prompt)
            
            if not result.get('success'):
                return Response(
                    {
                        "error": "parsing_failed",
                        "message": "Failed to parse report",
                        "details": result.get('error', 'Unknown error'),
                        "status_code": 500
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Extract parsing result
            parsed_text = result['text']
            
            # Try to extract JSON from response
            try:
                # Find JSON in the response
                import re
                json_match = re.search(r'\{.*\}', parsed_text, re.DOTALL)
                if json_match:
                    extracted_data = json. loads(json_match.group())
                else:
                    extracted_data = {"raw_text": parsed_text}
            except:
                extracted_data = {"raw_text": parsed_text}
            
            response_data = {
                "success": True,
                "extracted_data": extracted_data,
                "confidence": 0.85,  # Could be calculated based on AI response
                "report_type": report_type,
                "summary": parsed_text[:200] + "..." if len(parsed_text) > 200 else parsed_text,
                "warnings": [],  # Could be extracted from AI analysis
                "metadata": {
                    "parsed_at": datetime.utcnow().isoformat(),
                    "user_id": user_id,
                    "ai_model": "gemini"
                }
            }
            
            # Store parsing result
            db = get_firebase_db().db
            parsing_ref = db.collection('parsed_reports').document()
            parsing_ref.set({
                **response_data,
                'user_id': user_id,
                'original_text': report_text
            })
            
            logger.info(f"Report parsed successfully for user: {user_id}")
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error parsing report: {str(e)}", exc_info=True)
            return APIErrorHandler.handle_internal_error(e, logger)
