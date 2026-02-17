"""
Firebase Storage Service for Medical Report Upload

Handles file upload, validation, storage, and retrieval for medical reports.
Integrates with Firebase Storage for secure, scalable file storage.
"""

import firebase_admin
from firebase_admin import storage
from django.conf import settings
from typing import Dict, Any, Optional, BinaryIO
from io import BytesIO
import uuid
import logging
from datetime import timedelta
import mimetypes
import os

logger = logging.getLogger('health_ai.file_storage')


class ValidationResult:
    """Result of file validation."""
    
    def __init__(self, valid: bool, errors: Optional[list] = None):
        self.valid = valid
        self.errors = errors or []
    
    def __bool__(self):
        return self.valid


class FileStorageService:
    """
    Service for managing medical report file storage in Firebase Storage.
    
    Handles:
    - File validation (type, size)
    - Upload to Firebase Storage
    - Signed URL generation
    - File retrieval
    - File deletion
    """
    
    def __init__(self):
        """Initialize Firebase Storage service."""
        self.max_file_size = getattr(settings, 'MAX_FILE_SIZE_MB', 10) * 1024 * 1024  # Convert MB to bytes
        self.allowed_types = [
            'application/pdf',
            'image/jpeg',
            'image/png'
        ]
        self.storage_bucket = self._get_storage_bucket()
    
    def _get_storage_bucket(self):
        """Get Firebase Storage bucket."""
        try:
            bucket = storage.bucket()
            logger.info("Firebase Storage bucket initialized")
            return bucket
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Storage bucket: {e}")
            raise
    
    def validate_file(self, file: Any) -> ValidationResult:
        """
        Validate file type and size.
        
        Args:
            file: Uploaded file object (Django UploadedFile)
            
        Returns:
            ValidationResult with valid flag and error messages
        """
        errors = []
        
        # Check file type
        content_type = file.content_type if hasattr(file, 'content_type') else mimetypes.guess_type(file.name)[0]
        if content_type not in self.allowed_types:
            errors.append(f"Invalid file type: {content_type}. Allowed types: PDF, JPG, PNG")
        
        # Check file size
        file_size = file.size if hasattr(file, 'size') else len(file.read())
        if hasattr(file, 'seek'):
            file.seek(0)  # Reset file pointer after reading
        
        if file_size > self.max_file_size:
            max_mb = self.max_file_size / (1024 * 1024)
            actual_mb = file_size / (1024 * 1024)
            errors.append(f"File size {actual_mb:.2f}MB exceeds maximum {max_mb:.0f}MB")
        
        if file_size == 0:
            errors.append("File is empty")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info(f"File validation passed: {file.name}, size: {file_size} bytes")
        else:
            logger.warning(f"File validation failed: {file.name}, errors: {errors}")
        
        return ValidationResult(valid=is_valid, errors=errors if not is_valid else None)
    
    def upload_file(self, file: Any, user_id: str) -> Dict[str, Any]:
        """
        Upload file to Firebase Storage.
        
        Args:
            file: Uploaded file object
            user_id: User ID for organizing files
            
        Returns:
            Dictionary with report_id, storage_path, file_name, file_size, content_type
            
        Raises:
            ValueError: If file validation fails
            Exception: If upload fails
        """
        # Validate file first
        validation = self.validate_file(file)
        if not validation.valid:
            raise ValueError(f"File validation failed: {', '.join(validation.errors)}")
        
        try:
            # Generate unique report ID
            report_id = str(uuid.uuid4())
            
            # Get file extension
            file_name = file.name if hasattr(file, 'name') else 'report'
            file_extension = os.path.splitext(file_name)[1]
            
            # Create storage path: medical_reports/{user_id}/{report_id}{extension}
            storage_path = f"medical_reports/{user_id}/{report_id}{file_extension}"
            
            # Get blob reference
            blob = self.storage_bucket.blob(storage_path)
            
            # Set content type
            content_type = file.content_type if hasattr(file, 'content_type') else mimetypes.guess_type(file_name)[0]
            blob.content_type = content_type
            
            # Upload file
            if hasattr(file, 'read'):
                file_content = file.read()
                if hasattr(file, 'seek'):
                    file.seek(0)  # Reset for potential reuse
            else:
                file_content = file
            
            blob.upload_from_string(file_content, content_type=content_type)
            
            file_size = len(file_content)
            
            logger.info(f"File uploaded successfully: {storage_path}, size: {file_size} bytes")
            
            return {
                'report_id': report_id,
                'storage_path': storage_path,
                'file_name': file_name,
                'file_size': file_size,
                'content_type': content_type
            }
            
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def get_file_url(self, report_id: str, user_id: str, expiration_minutes: int = 60) -> str:
        """
        Generate signed URL for file download.
        
        Args:
            report_id: Report ID
            user_id: User ID for path construction
            expiration_minutes: URL expiration time in minutes
            
        Returns:
            Signed URL string
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        try:
            # Find the file by searching for blobs with the report_id
            prefix = f"medical_reports/{user_id}/{report_id}"
            blobs = list(self.storage_bucket.list_blobs(prefix=prefix))
            
            if not blobs:
                raise FileNotFoundError(f"Report not found: {report_id}")
            
            blob = blobs[0]
            
            # Generate signed URL
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=expiration_minutes),
                method="GET"
            )
            
            logger.info(f"Generated signed URL for report: {report_id}")
            
            return url
            
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {e}")
            raise Exception(f"Failed to generate download URL: {str(e)}")
    
    def get_file_stream(self, report_id: str, user_id: str) -> BytesIO:
        """
        Retrieve file as stream for processing.
        
        Args:
            report_id: Report ID
            user_id: User ID for path construction
            
        Returns:
            BytesIO stream of file content
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        try:
            # Find the file
            prefix = f"medical_reports/{user_id}/{report_id}"
            blobs = list(self.storage_bucket.list_blobs(prefix=prefix))
            
            if not blobs:
                raise FileNotFoundError(f"Report not found: {report_id}")
            
            blob = blobs[0]
            
            # Download to bytes
            file_bytes = blob.download_as_bytes()
            
            logger.info(f"Retrieved file stream for report: {report_id}")
            
            return BytesIO(file_bytes)
            
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve file stream: {e}")
            raise Exception(f"Failed to retrieve file: {str(e)}")
    
    def delete_file(self, report_id: str, user_id: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            report_id: Report ID
            user_id: User ID for path construction
            
        Returns:
            True if successful
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        try:
            # Find the file
            prefix = f"medical_reports/{user_id}/{report_id}"
            blobs = list(self.storage_bucket.list_blobs(prefix=prefix))
            
            if not blobs:
                raise FileNotFoundError(f"Report not found: {report_id}")
            
            blob = blobs[0]
            blob.delete()
            
            logger.info(f"Deleted file: {report_id}")
            
            return True
            
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            raise Exception(f"Failed to delete file: {str(e)}")
    
    def get_storage_path(self, report_id: str, user_id: str) -> Optional[str]:
        """
        Get storage path for a report.
        
        Args:
            report_id: Report ID
            user_id: User ID
            
        Returns:
            Storage path or None if not found
        """
        try:
            prefix = f"medical_reports/{user_id}/{report_id}"
            blobs = list(self.storage_bucket.list_blobs(prefix=prefix))
            
            if blobs:
                return blobs[0].name
            return None
            
        except Exception as e:
            logger.error(f"Failed to get storage path: {e}")
            return None
