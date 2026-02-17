"""
Extraction Job Manager for Medical Report Processing

Manages asynchronous extraction jobs and status tracking in Firestore.
Handles job creation, status updates, and result storage.
"""

from common.firebase_db import get_firebase_db
from firebase_admin import firestore
from typing import Dict, Any, Optional
import uuid
import logging
from datetime import datetime

logger = logging.getLogger('health_ai.extraction_jobs')


class ExtractionJobManager:
    """
    Manager for extraction job lifecycle and status tracking.
    
    Handles:
    - Job creation
    - Status updates
    - Progress tracking
    - Result storage
    - Error handling
    """
    
    def __init__(self):
        """Initialize job manager with Firestore connection."""
        self.db = get_firebase_db().db
        self.jobs_collection = 'extraction_jobs'
        self.reports_collection = 'medical_reports'
    
    def create_job(self, report_id: str, user_id: str) -> str:
        """
        Create extraction job in Firestore.
        
        Args:
            report_id: Report ID to process
            user_id: User ID who owns the report
            
        Returns:
            job_id: UUID for tracking
        """
        try:
            job_id = str(uuid.uuid4())
            
            job_data = {
                'job_id': job_id,
                'report_id': report_id,
                'user_id': user_id,
                'status': 'pending',
                'progress_percent': 0,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'completed_at': None,
                'extracted_data': None,
                'error_info': None,
                'extraction_metadata': {}
            }
            
            # Store job in Firestore
            job_ref = self.db.collection(self.jobs_collection).document(job_id)
            job_ref.set(job_data)
            
            logger.info(f"Created extraction job: {job_id} for report: {report_id}")
            
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to create extraction job: {e}")
            raise Exception(f"Failed to create extraction job: {str(e)}")
    
    def update_job_status(self, job_id: str, status: str, 
                         progress: Optional[int] = None, 
                         data: Optional[dict] = None) -> None:
        """
        Update job status and progress.
        
        Args:
            job_id: Job ID to update
            status: New status ('pending', 'processing', 'complete', 'failed')
            progress: Progress percentage (0-100)
            data: Additional data to update
        """
        try:
            job_ref = self.db.collection(self.jobs_collection).document(job_id)
            
            update_data = {
                'status': status,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            if progress is not None:
                update_data['progress_percent'] = progress
            
            if data:
                update_data.update(data)
            
            job_ref.update(update_data)
            
            logger.info(f"Updated job {job_id}: status={status}, progress={progress}")
            
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
            raise Exception(f"Failed to update job status: {str(e)}")
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Retrieve current job status.
        
        Args:
            job_id: Job ID to query
            
        Returns:
            Dictionary with job status and data
            
        Raises:
            ValueError: If job not found
        """
        try:
            job_ref = self.db.collection(self.jobs_collection).document(job_id)
            job_doc = job_ref.get()
            
            if not job_doc.exists:
                raise ValueError(f"Job not found: {job_id}")
            
            job_data = job_doc.to_dict()
            
            logger.debug(f"Retrieved job status: {job_id}, status: {job_data.get('status')}")
            
            return job_data
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            raise Exception(f"Failed to get job status: {str(e)}")
    
    def mark_job_complete(self, job_id: str, extracted_data: dict, 
                         extraction_metadata: Optional[dict] = None) -> None:
        """
        Mark job as complete with results.
        
        Args:
            job_id: Job ID to complete
            extracted_data: Extracted medical data
            extraction_metadata: Metadata about extraction process
        """
        try:
            job_ref = self.db.collection(self.jobs_collection).document(job_id)
            
            update_data = {
                'status': 'complete',
                'progress_percent': 100,
                'completed_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'extracted_data': extracted_data,
                'extraction_metadata': extraction_metadata or {}
            }
            
            job_ref.update(update_data)
            
            logger.info(f"Marked job complete: {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to mark job complete: {e}")
            raise Exception(f"Failed to mark job complete: {str(e)}")
    
    def mark_job_failed(self, job_id: str, error_code: str, 
                       message: str, partial_data: Optional[dict] = None) -> None:
        """
        Mark job as failed with error details.
        
        Args:
            job_id: Job ID to fail
            error_code: Machine-readable error code
            message: Human-readable error message
            partial_data: Any data extracted before failure
        """
        try:
            job_ref = self.db.collection(self.jobs_collection).document(job_id)
            
            error_info = {
                'error_code': error_code,
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            update_data = {
                'status': 'failed',
                'updated_at': firestore.SERVER_TIMESTAMP,
                'completed_at': firestore.SERVER_TIMESTAMP,
                'error_info': error_info
            }
            
            if partial_data:
                update_data['extracted_data'] = partial_data
            
            job_ref.update(update_data)
            
            logger.warning(f"Marked job failed: {job_id}, error: {error_code}")
            
        except Exception as e:
            logger.error(f"Failed to mark job as failed: {e}")
            raise Exception(f"Failed to mark job as failed: {str(e)}")
    
    def store_report_metadata(self, report_id: str, user_id: str, 
                             file_name: str, file_size: int, 
                             file_type: str, storage_path: str,
                             extraction_job_id: str) -> str:
        """
        Store report metadata in Firestore.
        
        Args:
            report_id: Unique report identifier
            user_id: User who uploaded the report
            file_name: Original file name
            file_size: File size in bytes
            file_type: MIME type
            storage_path: Firebase Storage path
            extraction_job_id: Associated extraction job ID
            
        Returns:
            Report document ID
        """
        try:
            report_data = {
                'report_id': report_id,
                'user_id': user_id,
                'file_name': file_name,
                'file_size': file_size,
                'file_type': file_type,
                'storage_path': storage_path,
                'upload_timestamp': firestore.SERVER_TIMESTAMP,
                'extraction_job_id': extraction_job_id,
                'associated_assessment_id': None
            }
            
            # Store report metadata
            report_ref = self.db.collection(self.reports_collection).document(report_id)
            report_ref.set(report_data)
            
            logger.info(f"Stored report metadata: {report_id}")
            
            return report_id
            
        except Exception as e:
            logger.error(f"Failed to store report metadata: {e}")
            raise Exception(f"Failed to store report metadata: {str(e)}")
    
    def get_report_metadata(self, report_id: str) -> Dict[str, Any]:
        """
        Get report metadata from Firestore.
        
        Args:
            report_id: Report ID to query
            
        Returns:
            Dictionary with report metadata
            
        Raises:
            ValueError: If report not found
        """
        try:
            report_ref = self.db.collection(self.reports_collection).document(report_id)
            report_doc = report_ref.get()
            
            if not report_doc.exists:
                raise ValueError(f"Report not found: {report_id}")
            
            report_data = report_doc.to_dict()
            
            logger.debug(f"Retrieved report metadata: {report_id}")
            
            return report_data
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to get report metadata: {e}")
            raise Exception(f"Failed to get report metadata: {str(e)}")
    
    def update_report_assessment_link(self, report_id: str, assessment_id: str) -> None:
        """
        Link report to an assessment.
        
        Args:
            report_id: Report ID
            assessment_id: Assessment ID to link
        """
        try:
            report_ref = self.db.collection(self.reports_collection).document(report_id)
            report_ref.update({
                'associated_assessment_id': assessment_id,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            logger.info(f"Linked report {report_id} to assessment {assessment_id}")
            
        except Exception as e:
            logger.error(f"Failed to link report to assessment: {e}")
            raise Exception(f"Failed to link report to assessment: {str(e)}")
    
    def get_user_reports(self, user_id: str, limit: int = 10) -> list:
        """
        Get user's uploaded reports.
        
        Args:
            user_id: User ID
            limit: Maximum number of reports to return
            
        Returns:
            List of report metadata dictionaries
        """
        try:
            reports_ref = self.db.collection(self.reports_collection)
            query = (reports_ref
                    .where('user_id', '==', user_id)
                    .order_by('upload_timestamp', direction=firestore.Query.DESCENDING)
                    .limit(limit))
            
            docs = query.stream()
            
            reports = []
            for doc in docs:
                data = doc.to_dict()
                reports.append(data)
            
            logger.info(f"Retrieved {len(reports)} reports for user: {user_id}")
            
            return reports
            
        except Exception as e:
            logger.error(f"Failed to get user reports: {e}")
            return []
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete extraction job.
        
        Args:
            job_id: Job ID to delete
            
        Returns:
            True if successful
        """
        try:
            job_ref = self.db.collection(self.jobs_collection).document(job_id)
            job_ref.delete()
            
            logger.info(f"Deleted extraction job: {job_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete job: {e}")
            return False
    
    def delete_report_metadata(self, report_id: str) -> bool:
        """
        Delete report metadata.
        
        Args:
            report_id: Report ID to delete
            
        Returns:
            True if successful
        """
        try:
            report_ref = self.db.collection(self.reports_collection).document(report_id)
            report_ref.delete()
            
            logger.info(f"Deleted report metadata: {report_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete report metadata: {e}")
            return False
