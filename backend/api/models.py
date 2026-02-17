"""
Django Models for Medical Report Upload and Extraction

Note: This application primarily uses Firebase Firestore for data storage.
These models are defined for Django admin interface and potential future use,
but the actual data persistence happens in Firestore via the ExtractionJobManager
and FileStorageService.

Firestore Collections:
- extraction_jobs: Job tracking and status
- medical_reports: Report metadata and references
"""

from django.db import models
from django.contrib.auth.models import User
import uuid


class MedicalReport(models.Model):
    """
    Medical report metadata model (for Django admin/reference).
    
    Actual data stored in Firestore via ExtractionJobManager.
    """
    
    report_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the report"
    )
    
    user_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Firebase user ID who uploaded the report"
    )
    
    file_name = models.CharField(
        max_length=255,
        help_text="Original filename"
    )
    
    file_size = models.IntegerField(
        help_text="File size in bytes"
    )
    
    file_type = models.CharField(
        max_length=50,
        help_text="MIME type (application/pdf, image/jpeg, image/png)"
    )
    
    storage_path = models.CharField(
        max_length=500,
        help_text="Firebase Storage path"
    )
    
    upload_timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the report was uploaded"
    )
    
    extraction_job_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="Associated extraction job ID"
    )
    
    associated_assessment_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Assessment ID if report was used in an assessment"
    )
    
    class Meta:
        db_table = 'medical_reports'
        ordering = ['-upload_timestamp']
        indexes = [
            models.Index(fields=['user_id', '-upload_timestamp']),
            models.Index(fields=['extraction_job_id']),
        ]
    
    def __str__(self):
        return f"{self.file_name} ({self.report_id})"


class ExtractionJob(models.Model):
    """
    Extraction job tracking model (for Django admin/reference).
    
    Actual data stored in Firestore via ExtractionJobManager.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
    ]
    
    job_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the extraction job"
    )
    
    report_id = models.UUIDField(
        db_index=True,
        help_text="Report being processed"
    )
    
    user_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Firebase user ID"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text="Current job status"
    )
    
    progress_percent = models.IntegerField(
        default=0,
        help_text="Progress percentage (0-100)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the job was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the job completed or failed"
    )
    
    error_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Error code if job failed"
    )
    
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if job failed"
    )
    
    extraction_time_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Time taken for extraction"
    )
    
    ocr_used = models.BooleanField(
        default=False,
        help_text="Whether OCR was used"
    )
    
    pages_processed = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of pages processed"
    )
    
    gemini_model = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Gemini model used for extraction"
    )
    
    class Meta:
        db_table = 'extraction_jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['report_id']),
        ]
    
    def __str__(self):
        return f"Job {self.job_id} - {self.status}"


class ExtractedMedicalData(models.Model):
    """
    Extracted medical data model (for Django admin/reference).
    
    Stores structured medical data extracted from reports.
    Actual data also stored in Firestore as part of extraction_jobs.
    """
    
    extraction_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    job_id = models.UUIDField(
        db_index=True,
        help_text="Associated extraction job"
    )
    
    report_id = models.UUIDField(
        db_index=True,
        help_text="Source report"
    )
    
    # Extracted data stored as JSON
    symptoms = models.JSONField(
        default=list,
        help_text="List of extracted symptoms"
    )
    
    vitals = models.JSONField(
        default=dict,
        help_text="Extracted vital signs"
    )
    
    lab_results = models.JSONField(
        default=list,
        help_text="List of lab results"
    )
    
    medications = models.JSONField(
        default=list,
        help_text="List of medications"
    )
    
    diagnoses = models.JSONField(
        default=list,
        help_text="List of diagnoses"
    )
    
    confidence_scores = models.JSONField(
        default=dict,
        help_text="Confidence scores for extracted data"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'extracted_medical_data'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['job_id']),
            models.Index(fields=['report_id']),
        ]
    
    def __str__(self):
        return f"Extraction {self.extraction_id} for Job {self.job_id}"
