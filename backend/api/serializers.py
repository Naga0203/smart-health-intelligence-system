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


class MedicalHistorySerializer(serializers.Serializer):
    """Serializer for medical history data."""
    
    conditions = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False,
        help_text="List of chronic or past medical conditions"
    )
    surgeries = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="List of past surgeries with date and details"
    )
    family_history = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False,
        help_text="Family medical history"
    )
    allergies = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False,
        help_text="Known allergies"
    )
    current_medications = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="Currently taking medications"
    )
    immunizations = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="Vaccination history"
    )
    lifestyle = serializers.DictField(
        required=False,
        help_text="Lifestyle factors (smoking, alcohol, exercise, diet)"
    )
    notes = serializers.CharField(
        max_length=2000,
        required=False,
        allow_blank=True,
        help_text="Additional notes or comments"
    )
    last_updated = serializers.DateTimeField(read_only=True)


class ReportUploadSerializer(serializers.Serializer):
    """Serializer for medical report upload request."""
    
    file = serializers.FileField(
        help_text="Medical report file (PDF, JPG, PNG)"
    )
    user_id = serializers.CharField(
        max_length=100,
        help_text="User ID for report ownership"
    )
    assessment_type = serializers.ChoiceField(
        choices=['lab_results', 'diagnosis', 'prescription', 'general'],
        required=False,
        help_text="Optional assessment type"
    )


class ReportUploadResponseSerializer(serializers.Serializer):
    """Serializer for medical report upload response."""
    
    success = serializers.BooleanField()
    job_id = serializers.CharField(
        help_text="UUID for tracking extraction"
    )
    report_id = serializers.CharField(
        help_text="UUID for report reference"
    )
    file_name = serializers.CharField()
    file_size = serializers.IntegerField()
    upload_timestamp = serializers.DateTimeField(
        help_text="ISO 8601 timestamp"
    )
    status = serializers.CharField(
        help_text="Processing status"
    )
    estimated_completion_seconds = serializers.IntegerField(
        help_text="Estimated time to complete extraction"
    )


class VitalsSerializer(serializers.Serializer):
    """Serializer for vital signs data."""
    
    blood_pressure = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Blood pressure (e.g., '120/80')"
    )
    heart_rate = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Heart rate in bpm"
    )
    temperature = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Temperature in Celsius or Fahrenheit"
    )
    weight = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Weight in kg"
    )
    height = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Height in cm"
    )


class LabResultSerializer(serializers.Serializer):
    """Serializer for lab result data."""
    
    test_name = serializers.CharField()
    value = serializers.FloatField()
    unit = serializers.CharField()
    reference_range = serializers.CharField()
    date = serializers.CharField(
        help_text="Date in YYYY-MM-DD format"
    )


class MedicationSerializer(serializers.Serializer):
    """Serializer for medication data."""
    
    name = serializers.CharField()
    dosage = serializers.CharField()
    frequency = serializers.CharField()
    start_date = serializers.CharField(
        help_text="Date in YYYY-MM-DD format"
    )


class DiagnosisSerializer(serializers.Serializer):
    """Serializer for diagnosis data."""
    
    condition = serializers.CharField()
    icd_code = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="ICD code if available"
    )
    date = serializers.CharField(
        help_text="Date in YYYY-MM-DD format"
    )
    status = serializers.ChoiceField(
        choices=['active', 'resolved', 'chronic'],
        help_text="Diagnosis status"
    )


class ConfidenceScoresSerializer(serializers.Serializer):
    """Serializer for confidence scores."""
    
    overall = serializers.FloatField(
        min_value=0.0,
        max_value=1.0,
        help_text="Overall confidence score (0.0-1.0)"
    )
    symptoms = serializers.FloatField(
        min_value=0.0,
        max_value=1.0
    )
    vitals = serializers.FloatField(
        min_value=0.0,
        max_value=1.0
    )
    lab_results = serializers.FloatField(
        min_value=0.0,
        max_value=1.0
    )
    medications = serializers.FloatField(
        min_value=0.0,
        max_value=1.0
    )
    diagnoses = serializers.FloatField(
        min_value=0.0,
        max_value=1.0
    )


class ExtractedMedicalDataSerializer(serializers.Serializer):
    """Serializer for extracted medical data from reports."""
    
    symptoms = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of extracted symptoms"
    )
    vitals = VitalsSerializer(
        help_text="Extracted vital signs"
    )
    lab_results = serializers.ListField(
        child=LabResultSerializer(),
        help_text="List of lab results"
    )
    medications = serializers.ListField(
        child=MedicationSerializer(),
        help_text="List of medications"
    )
    diagnoses = serializers.ListField(
        child=DiagnosisSerializer(),
        help_text="List of diagnoses"
    )
    confidence_scores = ConfidenceScoresSerializer(
        help_text="Confidence scores for each data category"
    )


class ExtractionMetadataSerializer(serializers.Serializer):
    """Serializer for extraction metadata."""
    
    extraction_time_seconds = serializers.FloatField()
    ocr_used = serializers.BooleanField()
    pages_processed = serializers.IntegerField()
    gemini_model = serializers.CharField()


class ExtractionJobStatusSerializer(serializers.Serializer):
    """Serializer for extraction job status response."""
    
    job_id = serializers.CharField()
    status = serializers.ChoiceField(
        choices=['processing', 'complete', 'failed'],
        help_text="Current job status"
    )
    progress_percent = serializers.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        help_text="Progress percentage (0-100) for processing status"
    )
    message = serializers.CharField(
        required=False,
        help_text="Status message"
    )
    extracted_data = ExtractedMedicalDataSerializer(
        required=False,
        help_text="Extracted data (only present when status is complete)"
    )
    extraction_metadata = ExtractionMetadataSerializer(
        required=False,
        help_text="Extraction metadata (only present when status is complete)"
    )
    error_code = serializers.CharField(
        required=False,
        help_text="Error code (only present when status is failed)"
    )
    partial_data = serializers.DictField(
        required=False,
        help_text="Partial data extracted before failure"
    )


class ReportMetadataSerializer(serializers.Serializer):
    """Serializer for report metadata response."""
    
    report_id = serializers.CharField()
    user_id = serializers.CharField()
    file_name = serializers.CharField()
    file_size = serializers.IntegerField()
    file_type = serializers.CharField()
    upload_timestamp = serializers.DateTimeField()
    download_url = serializers.URLField(
        help_text="Signed URL for file download (expires in 1 hour)"
    )
    extraction_job_id = serializers.CharField()
    associated_assessment_id = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Assessment ID if report was used in an assessment"
    )


class ReportParseInputSerializer(serializers.Serializer):
    """Serializer for report parsing input."""
    
    report_text = serializers.CharField(
        help_text="Text content of the medical report to parse"
    )
    report_type = serializers.ChoiceField(
        choices=['lab_report', 'imaging', 'prescription', 'discharge_summary',  'other'],
        help_text="Type of medical report"
    )
    extract_fields = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Specific fields to extract (e.g., ['glucose', 'cholesterol', 'blood_pressure'])"
    )


class ReportParseOutputSerializer(serializers.Serializer):
    """Serializer for parsed report output."""
    
    success = serializers.BooleanField()
    extracted_data = serializers.DictField()
    confidence = serializers.FloatField()
    report_type = serializers.CharField()
    summary = serializers.CharField()
    warnings = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    metadata = serializers.DictField()

