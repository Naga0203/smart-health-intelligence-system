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
    health_check
)

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
]
