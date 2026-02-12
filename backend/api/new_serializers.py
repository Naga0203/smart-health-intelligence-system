# Medical History Serializers
from rest_framework import serializers


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
    """Serializer for medical report upload."""
    
    file = serializers.FileField(
        help_text="Medical report file (PDF, JPG, PNG)"
    )
    report_type = serializers.ChoiceField(
        choices=['lab_report', 'imaging', 'prescription', 'discharge_summary', 'other'],
        help_text="Type of medical report"
    )
    report_date = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="Date of the report"
    )
    notes = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Additional notes about the report"
    )


class ReportParseInputSerializer(serializers.Serializer):
    """Serializer for report parsing input."""
    
    report_text = serializers.CharField(
        help_text="Text content of the medical report to parse"
    )
    report_type = serializers.ChoiceField(
        choices=['lab_report', 'imaging', 'prescription', 'discharge_summary', 'other'],
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
