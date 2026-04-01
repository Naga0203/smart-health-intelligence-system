"""
Local File Storage Service for Medical Report Upload

Handles file upload, validation, storage, and retrieval for medical reports.
Uses local filesystem storage instead of Firebase Storage to avoid
Cloud Storage bucket dependency (works on Firebase free Spark plan).

Report metadata is stored in Firestore; actual files are stored locally.
"""

from django.conf import settings
from typing import Dict, Any, Optional
from io import BytesIO
import uuid
import logging
import mimetypes
import os
import shutil

logger = logging.getLogger('health_ai.file_storage')

# Base directory for storing uploaded medical reports
MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'media', 'medical_reports')


class ValidationResult:
    """Result of file validation."""
    
    def __init__(self, valid: bool, errors: Optional[list] = None):
        self.valid = valid
        self.errors = errors or []
    
    def __bool__(self):
        return self.valid


class FileStorageService:
    """
    Service for managing medical report file storage on local filesystem.
    
    Handles:
    - File validation (type, size)
    - Upload to local filesystem
    - File retrieval as stream
    - File deletion
    
    Files are stored at: media/medical_reports/{user_id}/{report_id}{extension}
    """
    
    def __init__(self):
        """Initialize local file storage service."""
        self.max_file_size = getattr(settings, 'MAX_FILE_SIZE_MB', 10) * 1024 * 1024  # Convert MB to bytes
        self.allowed_types = [
            'application/pdf',
            'image/jpeg',
            'image/png'
        ]
        self.storage_root = MEDIA_ROOT
        # Ensure base directory exists
        os.makedirs(self.storage_root, exist_ok=True)
        logger.info(f"Local file storage initialized at: {self.storage_root}")
    
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
        Save file to local filesystem.
        
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
            
            # Create storage path: media/medical_reports/{user_id}/{report_id}{extension}
            user_dir = os.path.join(self.storage_root, user_id)
            os.makedirs(user_dir, exist_ok=True)
            
            stored_filename = f"{report_id}{file_extension}"
            full_path = os.path.join(user_dir, stored_filename)
            
            # Relative path for storing in metadata
            storage_path = f"medical_reports/{user_id}/{stored_filename}"
            
            # Get content type
            content_type = file.content_type if hasattr(file, 'content_type') else mimetypes.guess_type(file_name)[0]
            
            # Read file content
            if hasattr(file, 'read'):
                file_content = file.read()
                if hasattr(file, 'seek'):
                    file.seek(0)  # Reset for potential reuse
            else:
                file_content = file
            
            # Write to local filesystem
            with open(full_path, 'wb') as f:
                f.write(file_content)
            
            file_size = len(file_content)
            
            logger.info(f"File saved locally: {storage_path}, size: {file_size} bytes")
            
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
        Get local file path (no signed URLs needed for local storage).
        
        Args:
            report_id: Report ID
            user_id: User ID for path construction
            expiration_minutes: Unused (kept for API compatibility)
            
        Returns:
            Local file path string
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        try:
            file_path = self._find_file(report_id, user_id)
            if not file_path:
                raise FileNotFoundError(f"Report not found: {report_id}")
            
            logger.info(f"File path for report: {report_id}")
            return file_path
            
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get file path: {e}")
            raise Exception(f"Failed to get file path: {str(e)}")
    
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
            file_path = self._find_file(report_id, user_id)
            if not file_path:
                raise FileNotFoundError(f"Report not found: {report_id}")
            
            # Read file into BytesIO
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            
            logger.info(f"Retrieved file stream for report: {report_id}")
            return BytesIO(file_bytes)
            
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve file stream: {e}")
            raise Exception(f"Failed to retrieve file: {str(e)}")
    
    def delete_file(self, report_id: str, user_id: str) -> bool:
        """
        Delete file from local storage.
        
        Args:
            report_id: Report ID
            user_id: User ID for path construction
            
        Returns:
            True if successful
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        try:
            file_path = self._find_file(report_id, user_id)
            if not file_path:
                raise FileNotFoundError(f"Report not found: {report_id}")
            
            os.remove(file_path)
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
            file_path = self._find_file(report_id, user_id)
            if file_path:
                # Return relative path
                return os.path.relpath(file_path, settings.BASE_DIR)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get storage path: {e}")
            return None
    
    def _find_file(self, report_id: str, user_id: str) -> Optional[str]:
        """
        Find a file on disk by report_id and user_id.
        
        Searches for files matching the report_id in the user's directory.
        
        Args:
            report_id: Report UUID
            user_id: User ID
            
        Returns:
            Full file path if found, None otherwise
        """
        user_dir = os.path.join(self.storage_root, user_id)
        
        if not os.path.isdir(user_dir):
            return None
        
        # Search for files starting with the report_id
        for filename in os.listdir(user_dir):
            if filename.startswith(report_id):
                return os.path.join(user_dir, filename)
        
        return None
