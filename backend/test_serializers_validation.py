"""
Test script to validate the new serializers structure.
This script checks that all required serializers are defined with correct fields.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_serializers_exist():
    """Test that all required serializers exist."""
    try:
        from api.serializers import (
            ReportUploadSerializer,
            ReportUploadResponseSerializer,
            ExtractedMedicalDataSerializer,
            ExtractionJobStatusSerializer,
            ReportMetadataSerializer,
            VitalsSerializer,
            LabResultSerializer,
            MedicationSerializer,
            DiagnosisSerializer,
            ConfidenceScoresSerializer,
            ExtractionMetadataSerializer
        )
        print("✓ All required serializers imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_serializer_fields():
    """Test that serializers have the required fields."""
    from api.serializers import (
        ReportUploadSerializer,
        ExtractedMedicalDataSerializer,
        ExtractionJobStatusSerializer,
        ReportMetadataSerializer
    )
    
    # Test ReportUploadSerializer
    upload_fields = set(ReportUploadSerializer().fields.keys())
    required_upload_fields = {'file', 'user_id', 'assessment_type'}
    if required_upload_fields.issubset(upload_fields):
        print("✓ ReportUploadSerializer has all required fields")
    else:
        missing = required_upload_fields - upload_fields
        print(f"✗ ReportUploadSerializer missing fields: {missing}")
        return False
    
    # Test ExtractedMedicalDataSerializer
    extracted_fields = set(ExtractedMedicalDataSerializer().fields.keys())
    required_extracted_fields = {'symptoms', 'vitals', 'lab_results', 'medications', 'diagnoses', 'confidence_scores'}
    if required_extracted_fields.issubset(extracted_fields):
        print("✓ ExtractedMedicalDataSerializer has all required fields")
    else:
        missing = required_extracted_fields - extracted_fields
        print(f"✗ ExtractedMedicalDataSerializer missing fields: {missing}")
        return False
    
    # Test ExtractionJobStatusSerializer
    status_fields = set(ExtractionJobStatusSerializer().fields.keys())
    required_status_fields = {'job_id', 'status', 'progress_percent', 'message', 'extracted_data', 'extraction_metadata', 'error_code', 'partial_data'}
    if required_status_fields.issubset(status_fields):
        print("✓ ExtractionJobStatusSerializer has all required fields")
    else:
        missing = required_status_fields - status_fields
        print(f"✗ ExtractionJobStatusSerializer missing fields: {missing}")
        return False
    
    # Test ReportMetadataSerializer
    metadata_fields = set(ReportMetadataSerializer().fields.keys())
    required_metadata_fields = {'report_id', 'user_id', 'file_name', 'file_size', 'file_type', 'upload_timestamp', 'download_url', 'extraction_job_id', 'associated_assessment_id'}
    if required_metadata_fields.issubset(metadata_fields):
        print("✓ ReportMetadataSerializer has all required fields")
    else:
        missing = required_metadata_fields - metadata_fields
        print(f"✗ ReportMetadataSerializer missing fields: {missing}")
        return False
    
    return True

def test_nested_serializers():
    """Test that nested serializers are properly configured."""
    from api.serializers import (
        VitalsSerializer,
        LabResultSerializer,
        MedicationSerializer,
        DiagnosisSerializer,
        ConfidenceScoresSerializer
    )
    
    # Test VitalsSerializer
    vitals_fields = set(VitalsSerializer().fields.keys())
    required_vitals = {'blood_pressure', 'heart_rate', 'temperature', 'weight', 'height'}
    if required_vitals.issubset(vitals_fields):
        print("✓ VitalsSerializer has all required fields")
    else:
        missing = required_vitals - vitals_fields
        print(f"✗ VitalsSerializer missing fields: {missing}")
        return False
    
    # Test LabResultSerializer
    lab_fields = set(LabResultSerializer().fields.keys())
    required_lab = {'test_name', 'value', 'unit', 'reference_range', 'date'}
    if required_lab.issubset(lab_fields):
        print("✓ LabResultSerializer has all required fields")
    else:
        missing = required_lab - lab_fields
        print(f"✗ LabResultSerializer missing fields: {missing}")
        return False
    
    # Test MedicationSerializer
    med_fields = set(MedicationSerializer().fields.keys())
    required_med = {'name', 'dosage', 'frequency', 'start_date'}
    if required_med.issubset(med_fields):
        print("✓ MedicationSerializer has all required fields")
    else:
        missing = required_med - med_fields
        print(f"✗ MedicationSerializer missing fields: {missing}")
        return False
    
    # Test DiagnosisSerializer
    diag_fields = set(DiagnosisSerializer().fields.keys())
    required_diag = {'condition', 'icd_code', 'date', 'status'}
    if required_diag.issubset(diag_fields):
        print("✓ DiagnosisSerializer has all required fields")
    else:
        missing = required_diag - diag_fields
        print(f"✗ DiagnosisSerializer missing fields: {missing}")
        return False
    
    # Test ConfidenceScoresSerializer
    conf_fields = set(ConfidenceScoresSerializer().fields.keys())
    required_conf = {'overall', 'symptoms', 'vitals', 'lab_results', 'medications', 'diagnoses'}
    if required_conf.issubset(conf_fields):
        print("✓ ConfidenceScoresSerializer has all required fields")
    else:
        missing = required_conf - conf_fields
        print(f"✗ ConfidenceScoresSerializer missing fields: {missing}")
        return False
    
    return True

if __name__ == '__main__':
    print("Testing serializers structure...\n")
    
    all_passed = True
    
    if not test_serializers_exist():
        all_passed = False
    
    if not test_serializer_fields():
        all_passed = False
    
    if not test_nested_serializers():
        all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("✓ All serializer tests passed!")
        sys.exit(0)
    else:
        print("✗ Some serializer tests failed")
        sys.exit(1)
