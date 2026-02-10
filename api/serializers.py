"""
API Serializers for AI Health Intelligence System

Defines data serialization for REST API endpoints.
"""

from rest_framework import serializers


class HealthAssessmentInputSerializer(serializers.Serializer):
    """Serializer for health assessment input."""
    
    symptoms = serializers.ListField(
        child=serializers.CharField(max_length=200),
        help_text="List of symptoms (e.g., ['fever', 'cough', 'headache'])"
    )
    age = serializers.IntegerField(
        min_value=1,
        max_value=120,
        help_text="Patient age in years"
    )
    gender = serializers.ChoiceField(
        choices=['male', 'female', 'other'],
        help_text="Patient gender"
    )
    user_id = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Optional user ID for tracking"
    )
    additional_info = serializers.DictField(
        required=False,
        help_text="Optional additional health information (e.g., {'weight': 70, 'height': 175})"
    )


class PredictionSerializer(serializers.Serializer):
    """Serializer for disease prediction."""
    
    disease = serializers.CharField()
    probability = serializers.FloatField()
    probability_percent = serializers.FloatField()
    confidence = serializers.CharField()
    model_version = serializers.CharField(required=False)


class ExplanationSerializer(serializers.Serializer):
    """Serializer for explanation data."""
    
    text = serializers.CharField()
    generated_by = serializers.CharField()
    confidence = serializers.CharField()


class RecommendationSerializer(serializers.Serializer):
    """Serializer for recommendations."""
    
    items = serializers.ListField(child=serializers.CharField())
    urgency = serializers.CharField()
    confidence = serializers.CharField()


class HealthAssessmentOutputSerializer(serializers.Serializer):
    """Serializer for complete health assessment output."""
    
    user_id = serializers.CharField()
    assessment_id = serializers.CharField()
    prediction = PredictionSerializer()
    extraction = serializers.DictField()
    explanation = ExplanationSerializer()
    recommendations = RecommendationSerializer()
    metadata = serializers.DictField()


class SystemStatusSerializer(serializers.Serializer):
    """Serializer for system status."""
    
    status = serializers.CharField()
    version = serializers.CharField()
    components = serializers.DictField()
    timestamp = serializers.DateTimeField()


class ModelInfoSerializer(serializers.Serializer):
    """Serializer for model information."""
    
    model_loaded = serializers.BooleanField()
    model_type = serializers.CharField()
    num_features = serializers.IntegerField()
    num_diseases = serializers.IntegerField()
    device = serializers.CharField(required=False)


class TopPredictionsInputSerializer(serializers.Serializer):
    """Serializer for top-N predictions input."""
    
    symptoms = serializers.ListField(
        child=serializers.CharField(max_length=200)
    )
    age = serializers.IntegerField(min_value=1, max_value=120)
    gender = serializers.ChoiceField(choices=['male', 'female', 'other'])
    n = serializers.IntegerField(
        min_value=1,
        max_value=20,
        default=5,
        help_text="Number of top predictions to return"
    )


class DiseaseInfoSerializer(serializers.Serializer):
    """Serializer for disease information."""
    
    disease = serializers.CharField()
    probability = serializers.FloatField()
    rank = serializers.IntegerField()


class UserProfileSerializer(serializers.Serializer):
    """Serializer for user profile data."""
    
    uid = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    display_name = serializers.CharField(max_length=200, required=False)
    photo_url = serializers.URLField(required=False, allow_blank=True)
    email_verified = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    
    # Additional profile fields
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(
        choices=['male', 'female', 'other', 'prefer_not_to_say'],
        required=False,
        allow_blank=True
    )
    address = serializers.DictField(required=False)
    emergency_contact = serializers.DictField(required=False)
    medical_history = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    allergies = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    current_medications = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class UserProfileUpdateSerializer(serializers.Serializer):
    """Serializer for updating user profile."""
    
    display_name = serializers.CharField(max_length=200, required=False)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(
        choices=['male', 'female', 'other', 'prefer_not_to_say'],
        required=False
    )
    address = serializers.DictField(required=False)
    emergency_contact = serializers.DictField(required=False)
    medical_history = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    allergies = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    current_medications = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class UserStatisticsSerializer(serializers.Serializer):
    """Serializer for user statistics."""
    
    total_assessments = serializers.IntegerField()
    assessments_by_confidence = serializers.DictField()
    most_common_diseases = serializers.ListField()
    last_assessment_date = serializers.DateTimeField(allow_null=True)
    account_age_days = serializers.IntegerField()


class AssessmentHistoryItemSerializer(serializers.Serializer):
    """Serializer for assessment history item."""
    
    id = serializers.CharField()
    created_at = serializers.DateTimeField()
    disease = serializers.CharField()
    probability = serializers.FloatField()
    confidence = serializers.CharField()
    symptoms = serializers.ListField(child=serializers.CharField())
    status = serializers.CharField()


class AssessmentHistorySerializer(serializers.Serializer):
    """Serializer for paginated assessment history."""
    
    total = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    assessments = AssessmentHistoryItemSerializer(many=True)


class AssessmentDetailSerializer(serializers.Serializer):
    """Serializer for detailed assessment information."""
    
    id = serializers.CharField()
    user_id = serializers.CharField()
    created_at = serializers.DateTimeField()
    symptoms = serializers.ListField(child=serializers.CharField())
    age = serializers.IntegerField()
    gender = serializers.CharField()
    disease = serializers.CharField()
    probability = serializers.FloatField()
    confidence = serializers.CharField()
    extraction_data = serializers.DictField()
    prediction_metadata = serializers.DictField()
    explanation = serializers.DictField()
    recommendations = serializers.DictField()
    status = serializers.CharField()
