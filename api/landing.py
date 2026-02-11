"""
Landing page view for the Health AI Backend API
"""
from django.shortcuts import render


def landing_page(request):
    """
    Render the landing page with links to all available endpoints
    """
    context = {
        'title': 'Health AI Backend API',
        'description': 'AI-powered health analysis and assessment platform',
        'endpoints': {
            'Documentation': [
                {'name': 'Swagger UI', 'url': '/api/docs/', 'description': 'Interactive API documentation'},
                {'name': 'ReDoc', 'url': '/api/redoc/', 'description': 'Alternative API documentation'},
                {'name': 'OpenAPI Schema', 'url': '/api/schema/', 'description': 'Raw OpenAPI schema'},
            ],
            'Health Analysis': [
                {'name': 'Health Analysis', 'url': '/api/health/analyze/', 'description': 'Analyze health data with Firebase auth'},
                {'name': 'Health Assessment', 'url': '/api/assess/', 'description': 'Get health assessment'},
                {'name': 'Top Predictions', 'url': '/api/predict/top/', 'description': 'Get top N disease predictions'},
            ],
            'System': [
                {'name': 'System Status', 'url': '/api/status/', 'description': 'Check system status'},
                {'name': 'Health Check', 'url': '/api/health/', 'description': 'API health check'},
                {'name': 'Model Info', 'url': '/api/model/info/', 'description': 'Get model information'},
                {'name': 'Diseases List', 'url': '/api/diseases/', 'description': 'List all supported diseases'},
            ],
            'User Management': [
                {'name': 'User Profile', 'url': '/api/user/profile/', 'description': 'Get or update user profile'},
                {'name': 'User Statistics', 'url': '/api/user/statistics/', 'description': 'Get user statistics'},
                {'name': 'Assessment History', 'url': '/api/user/assessments/', 'description': 'Get user assessment history'},
            ],
            'Admin': [
                {'name': 'Admin Panel', 'url': '/admin/', 'description': 'Django admin interface'},
            ],
        }
    }
    return render(request, 'landing.html', context)
