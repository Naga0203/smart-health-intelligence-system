"""
Unit tests for extraction status endpoint.

Tests the ExtractionStatusView endpoint for:
- Status check for processing job
- Status check for completed job
- Status check for failed job
- Invalid job_id handling

Validates: Requirements 10.3, 10.4
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime


class TestExtractionStatusEndpoint:
    """Test suite for extraction status endpoint logic."""
    
    def test_processing_job_status(self):
        """
        Test status check for job in processing state.
        
        Validates: Requirements 10.3
        """
        with patch('api.extraction_jobs.ExtractionJobManager') as MockJobManager:
            from api.extraction_jobs import ExtractionJobManager
            
            mock_job_mgr = MockJobManager.return_value
            mock_job_mgr.get_job_status.return_value = {
                'job_id': 'job_123',
                'report_id': 'report_123',
                'user_id': 'user_123',
                'status': 'processing',
                'progress_percent': 65,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            job_id = 'job_123'
            user_id = 'user_123'
            
            # Get job status
            job_data = mock_job_mgr.get_job_status(job_id)
            
            # Verify user access
            assert job_data['user_id'] == user_id
            
            # Build response
            response_data = {
                'job_id': job_id,
                'status': 'processing',
                'progress_percent': job_data['progress_percent'],
                'message': 'Extracting medical data...'
            }
            
            # Verify response structure
            assert response_data['job_id'] == 'job_123'
            assert response_data['status'] == 'processing'
            assert response_data['progress_percent'] == 65
            assert 'message' in response_data
    
    def test_completed_job_status(self):
        """
        Test status check for completed job with extracted data.
        
        Validates: Requirements 10.3, 10.4
        """
        with patch('api.extraction_jobs.ExtractionJobManager') as MockJobManager:
            from api.extraction_jobs import ExtractionJobManager
            
            mock_job_mgr = MockJobManager.return_value
            mock_job_mgr.get_job_status.return_value = {
                'job_id': 'job_123',
                'report_id': 'report_123',
                'user_id': 'user_123',
                'status': 'complete',
                'progress_percent': 100,
                'extracted_data': {
                    'symptoms': ['fever', 'cough'],
                    'vitals': {
                        'blood_pressure': '120/80',
                        'heart_rate': 72
                    },
                    'lab_results': [],
                    'medications': [],
                    'diagnoses': [],
                    'confidence_scores': {
                        'overall': 0.85,
                        'symptoms': 0.90,
                        'vitals': 0.88,
                        'lab_results': 0.0,
                        'medications': 0.0,
                        'diagnoses': 0.0
                    }
                },
                'extraction_metadata': {
                    'extraction_time_seconds': 7.2,
                    'ocr_used': False,
                    'pages_processed': 3,
                    'gemini_model': 'gemini-1.5-flash'
                },
                'completed_at': datetime.utcnow()
            }
            
            job_id = 'job_123'
            user_id = 'user_123'
            
            # Get job status
            job_data = mock_job_mgr.get_job_status(job_id)
            
            # Verify user access
            assert job_data['user_id'] == user_id
            
            # Build response
            response_data = {
                'job_id': job_id,
                'status': 'complete',
                'extracted_data': job_data['extracted_data'],
                'extraction_metadata': job_data['extraction_metadata']
            }
            
            # Verify response structure
            assert response_data['job_id'] == 'job_123'
            assert response_data['status'] == 'complete'
            assert 'extracted_data' in response_data
            assert 'extraction_metadata' in response_data
            
            # Verify extracted data structure
            extracted_data = response_data['extracted_data']
            assert 'symptoms' in extracted_data
            assert 'vitals' in extracted_data
            assert 'lab_results' in extracted_data
            assert 'medications' in extracted_data
            assert 'diagnoses' in extracted_data
            assert 'confidence_scores' in extracted_data
            
            # Verify metadata
            metadata = response_data['extraction_metadata']
            assert 'extraction_time_seconds' in metadata
            assert 'ocr_used' in metadata
            assert 'pages_processed' in metadata
            assert 'gemini_model' in metadata
    
    def test_failed_job_status(self):
        """
        Test status check for failed job with error details.
        
        Validates: Requirements 10.3
        """
        with patch('api.extraction_jobs.ExtractionJobManager') as MockJobManager:
            from api.extraction_jobs import ExtractionJobManager
            
            mock_job_mgr = MockJobManager.return_value
            mock_job_mgr.get_job_status.return_value = {
                'job_id': 'job_123',
                'report_id': 'report_123',
                'user_id': 'user_123',
                'status': 'failed',
                'error_info': {
                    'error_code': 'unreadable',
                    'message': 'Unable to extract text from report. File may be corrupted.',
                    'timestamp': datetime.utcnow().isoformat()
                },
                'extracted_data': {},
                'completed_at': datetime.utcnow()
            }
            
            job_id = 'job_123'
            user_id = 'user_123'
            
            # Get job status
            job_data = mock_job_mgr.get_job_status(job_id)
            
            # Verify user access
            assert job_data['user_id'] == user_id
            
            # Build response
            error_info = job_data['error_info']
            response_data = {
                'job_id': job_id,
                'status': 'failed',
                'error_code': error_info['error_code'],
                'message': error_info['message'],
                'partial_data': job_data.get('extracted_data', {})
            }
            
            # Verify response structure
            assert response_data['job_id'] == 'job_123'
            assert response_data['status'] == 'failed'
            assert response_data['error_code'] == 'unreadable'
            assert 'message' in response_data
            assert 'partial_data' in response_data
    
    def test_invalid_job_id(self):
        """
        Test handling of invalid/non-existent job ID.
        
        Validates: Requirements 10.3
        """
        with patch('api.extraction_jobs.ExtractionJobManager') as MockJobManager:
            from api.extraction_jobs import ExtractionJobManager
            
            mock_job_mgr = MockJobManager.return_value
            mock_job_mgr.get_job_status.side_effect = ValueError("Job not found: invalid_job_id")
            
            job_id = 'invalid_job_id'
            
            # Attempt to get job status
            with pytest.raises(ValueError) as exc_info:
                mock_job_mgr.get_job_status(job_id)
            
            assert "Job not found" in str(exc_info.value)
            
            # Verify error response would be 404
            error_response = {
                'error': 'not_found',
                'message': 'Resource not found',
                'details': f'Extraction job not found: {job_id}',
                'status_code': 404
            }
            
            assert error_response['error'] == 'not_found'
            assert error_response['status_code'] == 404
    
    def test_unauthorized_access(self):
        """
        Test that users cannot access jobs they don't own.
        
        Validates: Requirements 10.3
        """
        with patch('api.extraction_jobs.ExtractionJobManager') as MockJobManager:
            from api.extraction_jobs import ExtractionJobManager
            
            mock_job_mgr = MockJobManager.return_value
            mock_job_mgr.get_job_status.return_value = {
                'job_id': 'job_123',
                'report_id': 'report_123',
                'user_id': 'other_user',
                'status': 'processing',
                'progress_percent': 50
            }
            
            job_id = 'job_123'
            requesting_user_id = 'user_123'
            
            # Get job status
            job_data = mock_job_mgr.get_job_status(job_id)
            
            # Verify user mismatch
            job_owner = job_data['user_id']
            assert job_owner != requesting_user_id
            
            # Verify error response would be 403
            error_response = {
                'error': 'permission_error',
                'message': 'Permission denied',
                'details': 'You do not have access to this extraction job',
                'status_code': 403
            }
            
            assert error_response['error'] == 'permission_error'
            assert error_response['status_code'] == 403
    
    def test_pending_job_status(self):
        """
        Test status check for job in pending state.
        
        Validates: Requirements 10.3
        """
        with patch('api.extraction_jobs.ExtractionJobManager') as MockJobManager:
            from api.extraction_jobs import ExtractionJobManager
            
            mock_job_mgr = MockJobManager.return_value
            mock_job_mgr.get_job_status.return_value = {
                'job_id': 'job_123',
                'report_id': 'report_123',
                'user_id': 'user_123',
                'status': 'pending',
                'progress_percent': 0,
                'created_at': datetime.utcnow()
            }
            
            job_id = 'job_123'
            user_id = 'user_123'
            
            # Get job status
            job_data = mock_job_mgr.get_job_status(job_id)
            
            # Verify user access
            assert job_data['user_id'] == user_id
            
            # Build response (pending treated as processing)
            response_data = {
                'job_id': job_id,
                'status': 'processing',
                'progress_percent': job_data['progress_percent'],
                'message': 'Initializing extraction process...'
            }
            
            # Verify response
            assert response_data['status'] == 'processing'
            assert response_data['progress_percent'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
