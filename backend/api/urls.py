"""
API URL Configuration

Defines all REST API endpoints.
"""

from django.urls import path
from .views import (
    HealthAnalysisAPI,
    HealthAssessmentView,
    TopPredictionsView,
    SystemStatusView,
    ModelInfoView,
    DiseasesListView,
    health_check,
    UserProfileAPIView,
    UserStatisticsAPIView,
    AssessmentHistoryAPIView,
    AssessmentDetailAPIView,
    ReportUploadView,
    ExtractionStatusView,
    ReportMetadataView,
    PredictView
)
from .new_views import (
    MedicalHistoryAPIView,
    AssessmentExportAPIView,
    ReportUploadAPIView,
    ReportUploadAPIView,
    ReportParseAPIView
)
from prediction.views import SymptomPredictionView

app_name = 'api'

urlpatterns = [
    # Primary health analysis endpoint with Firebase auth
    path('health/analyze/', HealthAnalysisAPI.as_view(), name='health-analysis'),
    
    # Main health assessment endpoint
    path('assess/', HealthAssessmentView.as_view(), name='health-assessment'),
    
    # Top N predictions
    path('predict/top/', TopPredictionsView.as_view(), name='top-predictions'),
    
    # System status and health
    path('status/', SystemStatusView.as_view(), name='system-status'),
    path('health/', health_check, name='health-check'),
    
    # Model information
    path('model/info/', ModelInfoView.as_view(), name='model-info'),
    
    # Diseases list
    path('diseases/', DiseasesListView.as_view(), name='diseases-list'),
    
    # User profile endpoints
    path('user/profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('user/statistics/', UserStatisticsAPIView.as_view(), name='user-statistics'),
    
    # Assessment history endpoints
    path('user/assessments/', AssessmentHistoryAPIView.as_view(), name='assessment-history'),
    # Assessment detail
    path('user/assessments/<str:assessment_id>/', AssessmentDetailAPIView.as_view(), name='assessment-detail'),
    
    # Medical History endpoints
    path('user/medical-history/', MedicalHistoryAPIView.as_view(), name='medical-history'),
    
    # Assessment Export endpoints
    path('user/assessments/<str:assessment_id>/export/', AssessmentExportAPIView.as_view(), name='assessment-export'),
    
    # Report Upload and Parsing endpoints
    path('reports/upload/', ReportUploadView.as_view(), name='report-upload'),
    path('reports/extract/<str:job_id>/', ExtractionStatusView.as_view(), name='extraction-status'),
    path('reports/<str:report_id>/', ReportMetadataView.as_view(), name='report-metadata'),
    path('reports/parse/', ReportParseAPIView.as_view(), name='report-parse'),

    # Symptom Prediction
    path('predict/symptoms/', SymptomPredictionView.as_view(), name='predict-symptoms'),
    
    # Full prediction (Orchestrator)
    path('predict/', PredictView.as_view(), name='predict'),
]

