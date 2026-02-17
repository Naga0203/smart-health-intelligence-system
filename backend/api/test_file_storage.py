"""
Unit tests for FileStorageService

Tests file validation, upload, retrieval, and signed URL generation.
Requirements: 1.2, 1.3, 2.1
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from io import BytesIO
import uuid
from datetime import timedelta

from api.file_storage import FileStorageService, ValidationResult


class MockUploadedFile:
    """Mock Django UploadedFile for testing."""
    
    def __init__(self, name: str, content: bytes, content_type: str):
        self.name = name
        self.content = content
        self.content_type = content_type
        self.size = len(content)
        self._position = 0
    
    def read(self):
        """Read file content."""
        return self.content
    
    def seek(self, position):
        """Seek to position in file."""
        self._position = position


@pytest.fixture
def file_storage_service():
    """Create FileStorageService instance with mocked Firebase."""
    with patch('api.file_storage.storage.bucket') as mock_bucket, \
         patch('api.file_storage.settings') as mock_settings:
        
        # Mock Django settings
        mock_settings.MAX_FILE_SIZE_MB = 10
        
        mock_bucket_instance = MagicMock()
        mock_bucket.return_value = mock_bucket_instance
        
        service = FileStorageService()
        service.storage_bucket = mock_bucket_instance
        
        yield service


@pytest.fixture
def valid_pdf_file():
    """Create a valid PDF file mock."""
    content = b'%PDF-1.4\n%\xE2\xE3\xCF\xD3\n' + b'x' * 1000  # Valid PDF header + content
    return MockUploadedFile('test_report.pdf', content, 'application/pdf')


@pytest.fixture
def valid_jpg_file():
    """Create a valid JPG file mock."""
    # JPEG file signature
    content = b'\xFF\xD8\xFF\xE0' + b'x' * 1000
    return MockUploadedFile('test_scan.jpg', content, 'image/jpeg')


@pytest.fixture
def valid_png_file():
    """Create a valid PNG file mock."""
    # PNG file signature
    content = b'\x89PNG\r\n\x1a\n' + b'x' * 1000
    return MockUploadedFile('test_scan.png', content, 'image/png')


@pytest.fixture
def invalid_format_file():
    """Create an invalid format file mock."""
    content = b'x' * 1000
    return MockUploadedFile('test_doc.docx', content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')


@pytest.fixture
def oversized_file():
    """Create an oversized file mock (>10MB)."""
    content = b'x' * (11 * 1024 * 1024)  # 11MB
    return MockUploadedFile('large_report.pdf', content, 'application/pdf')


@pytest.fixture
def empty_file():
    """Create an empty file mock."""
    return MockUploadedFile('empty.pdf', b'', 'application/pdf')


class TestFileValidation:
    """Test file validation functionality."""
    
    def test_validate_valid_pdf(self, file_storage_service, valid_pdf_file):
        """Test validation accepts valid PDF files."""
        result = file_storage_service.validate_file(valid_pdf_file)
        
        assert result.valid is True
        assert result.errors == []
        assert bool(result) is True
    
    def test_validate_valid_jpg(self, file_storage_service, valid_jpg_file):
        """Test validation accepts valid JPG files."""
        result = file_storage_service.validate_file(valid_jpg_file)
        
        assert result.valid is True
        assert result.errors == []
    
    def test_validate_valid_png(self, file_storage_service, valid_png_file):
        """Test validation accepts valid PNG files."""
        result = file_storage_service.validate_file(valid_png_file)
        
        assert result.valid is True
        assert result.errors == []
    
    def test_validate_invalid_format(self, file_storage_service, invalid_format_file):
        """Test validation rejects invalid file formats."""
        result = file_storage_service.validate_file(invalid_format_file)
        
        assert result.valid is False
        assert len(result.errors) > 0
        assert any('Invalid file type' in error for error in result.errors)
        assert bool(result) is False
    
    def test_validate_oversized_file(self, file_storage_service, oversized_file):
        """Test validation rejects files exceeding size limit."""
        result = file_storage_service.validate_file(oversized_file)
        
        assert result.valid is False
        assert len(result.errors) > 0
        assert any('exceeds maximum' in error for error in result.errors)
    
    def test_validate_empty_file(self, file_storage_service, empty_file):
        """Test validation rejects empty files."""
        result = file_storage_service.validate_file(empty_file)
        
        assert result.valid is False
        assert len(result.errors) > 0
        assert any('empty' in error.lower() for error in result.errors)
    
    def test_validate_file_at_size_limit(self, file_storage_service):
        """Test validation accepts file exactly at 10MB limit."""
        content = b'x' * (10 * 1024 * 1024)  # Exactly 10MB
        file = MockUploadedFile('limit_test.pdf', content, 'application/pdf')
        
        result = file_storage_service.validate_file(file)
        
        assert result.valid is True
        assert result.errors == []


class TestFileUpload:
    """Test file upload functionality."""
    
    def test_upload_valid_pdf(self, file_storage_service, valid_pdf_file):
        """Test successful upload of valid PDF file."""
        user_id = 'test_user_123'
        
        # Mock the blob
        mock_blob = MagicMock()
        file_storage_service.storage_bucket.blob.return_value = mock_blob
        
        result = file_storage_service.upload_file(valid_pdf_file, user_id)
        
        # Verify result structure
        assert 'report_id' in result
        assert 'storage_path' in result
        assert 'file_name' in result
        assert 'file_size' in result
        assert 'content_type' in result
        
        # Verify values
        assert result['file_name'] == 'test_report.pdf'
        assert result['file_size'] == valid_pdf_file.size
        assert result['content_type'] == 'application/pdf'
        assert user_id in result['storage_path']
        assert result['report_id'] in result['storage_path']
        
        # Verify Firebase calls
        file_storage_service.storage_bucket.blob.assert_called_once()
        mock_blob.upload_from_string.assert_called_once()
    
    def test_upload_valid_jpg(self, file_storage_service, valid_jpg_file):
        """Test successful upload of valid JPG file."""
        user_id = 'test_user_456'
        
        mock_blob = MagicMock()
        file_storage_service.storage_bucket.blob.return_value = mock_blob
        
        result = file_storage_service.upload_file(valid_jpg_file, user_id)
        
        assert result['file_name'] == 'test_scan.jpg'
        assert result['content_type'] == 'image/jpeg'
        assert '.jpg' in result['storage_path']
    
    def test_upload_valid_png(self, file_storage_service, valid_png_file):
        """Test successful upload of valid PNG file."""
        user_id = 'test_user_789'
        
        mock_blob = MagicMock()
        file_storage_service.storage_bucket.blob.return_value = mock_blob
        
        result = file_storage_service.upload_file(valid_png_file, user_id)
        
        assert result['file_name'] == 'test_scan.png'
        assert result['content_type'] == 'image/png'
        assert '.png' in result['storage_path']
    
    def test_upload_invalid_format_raises_error(self, file_storage_service, invalid_format_file):
        """Test upload rejects invalid file format."""
        user_id = 'test_user_123'
        
        with pytest.raises(ValueError) as exc_info:
            file_storage_service.upload_file(invalid_format_file, user_id)
        
        assert 'File validation failed' in str(exc_info.value)
        assert 'Invalid file type' in str(exc_info.value)
    
    def test_upload_oversized_file_raises_error(self, file_storage_service, oversized_file):
        """Test upload rejects oversized file."""
        user_id = 'test_user_123'
        
        with pytest.raises(ValueError) as exc_info:
            file_storage_service.upload_file(oversized_file, user_id)
        
        assert 'File validation failed' in str(exc_info.value)
        assert 'exceeds maximum' in str(exc_info.value)
    
    def test_upload_generates_unique_report_ids(self, file_storage_service, valid_pdf_file):
        """Test that multiple uploads generate unique report IDs."""
        user_id = 'test_user_123'
        
        mock_blob = MagicMock()
        file_storage_service.storage_bucket.blob.return_value = mock_blob
        
        result1 = file_storage_service.upload_file(valid_pdf_file, user_id)
        result2 = file_storage_service.upload_file(valid_pdf_file, user_id)
        
        assert result1['report_id'] != result2['report_id']
    
    def test_upload_storage_path_format(self, file_storage_service, valid_pdf_file):
        """Test storage path follows correct format."""
        user_id = 'test_user_123'
        
        mock_blob = MagicMock()
        file_storage_service.storage_bucket.blob.return_value = mock_blob
        
        result = file_storage_service.upload_file(valid_pdf_file, user_id)
        
        # Path should be: medical_reports/{user_id}/{report_id}.pdf
        assert result['storage_path'].startswith('medical_reports/')
        assert f'/{user_id}/' in result['storage_path']
        assert result['storage_path'].endswith('.pdf')
    
    def test_upload_firebase_error_raises_exception(self, file_storage_service, valid_pdf_file):
        """Test upload handles Firebase errors gracefully."""
        user_id = 'test_user_123'
        
        mock_blob = MagicMock()
        mock_blob.upload_from_string.side_effect = Exception('Firebase connection error')
        file_storage_service.storage_bucket.blob.return_value = mock_blob
        
        with pytest.raises(Exception) as exc_info:
            file_storage_service.upload_file(valid_pdf_file, user_id)
        
        assert 'Failed to upload file' in str(exc_info.value)


class TestSignedURLGeneration:
    """Test signed URL generation functionality."""
    
    def test_get_file_url_success(self, file_storage_service):
        """Test successful signed URL generation."""
        report_id = str(uuid.uuid4())
        user_id = 'test_user_123'
        
        # Mock blob with signed URL
        mock_blob = MagicMock()
        mock_blob.generate_signed_url.return_value = 'https://storage.googleapis.com/signed-url'
        
        file_storage_service.storage_bucket.list_blobs.return_value = [mock_blob]
        
        url = file_storage_service.get_file_url(report_id, user_id)
        
        assert url == 'https://storage.googleapis.com/signed-url'
        mock_blob.generate_signed_url.assert_called_once()
    
    def test_get_file_url_with_custom_expiration(self, file_storage_service):
        """Test signed URL generation with custom expiration time."""
        report_id = str(uuid.uuid4())
        user_id = 'test_user_123'
        expiration_minutes = 120
        
        mock_blob = MagicMock()
        mock_blob.generate_signed_url.return_value = 'https://storage.googleapis.com/signed-url'
        
        file_storage_service.storage_bucket.list_blobs.return_value = [mock_blob]
        
        url = file_storage_service.get_file_url(report_id, user_id, expiration_minutes)
        
        # Verify expiration parameter was passed
        call_args = mock_blob.generate_signed_url.call_args
        assert call_args[1]['expiration'] == timedelta(minutes=expiration_minutes)
    
    def test_get_file_url_file_not_found(self, file_storage_service):
        """Test signed URL generation raises error for non-existent file."""
        report_id = str(uuid.uuid4())
        user_id = 'test_user_123'
        
        file_storage_service.storage_bucket.list_blobs.return_value = []
        
        with pytest.raises(FileNotFoundError) as exc_info:
            file_storage_service.get_file_url(report_id, user_id)
        
        assert 'Report not found' in str(exc_info.value)
    
    def test_get_file_url_default_expiration(self, file_storage_service):
        """Test signed URL uses default 60-minute expiration."""
        report_id = str(uuid.uuid4())
        user_id = 'test_user_123'
        
        mock_blob = MagicMock()
        mock_blob.generate_signed_url.return_value = 'https://storage.googleapis.com/signed-url'
        
        file_storage_service.storage_bucket.list_blobs.return_value = [mock_blob]
        
        file_storage_service.get_file_url(report_id, user_id)
        
        call_args = mock_blob.generate_signed_url.call_args
        assert call_args[1]['expiration'] == timedelta(minutes=60)


class TestFileRetrieval:
    """Test file retrieval functionality."""
    
    def test_get_file_stream_success(self, file_storage_service):
        """Test successful file stream retrieval."""
        report_id = str(uuid.uuid4())
        user_id = 'test_user_123'
        file_content = b'PDF content here'
        
        mock_blob = MagicMock()
        mock_blob.download_as_bytes.return_value = file_content
        
        file_storage_service.storage_bucket.list_blobs.return_value = [mock_blob]
        
        stream = file_storage_service.get_file_stream(report_id, user_id)
        
        assert isinstance(stream, BytesIO)
        assert stream.read() == file_content
    
    def test_get_file_stream_file_not_found(self, file_storage_service):
        """Test file stream retrieval raises error for non-existent file."""
        report_id = str(uuid.uuid4())
        user_id = 'test_user_123'
        
        file_storage_service.storage_bucket.list_blobs.return_value = []
        
        with pytest.raises(FileNotFoundError) as exc_info:
            file_storage_service.get_file_stream(report_id, user_id)
        
        assert 'Report not found' in str(exc_info.value)


class TestFileDeletion:
    """Test file deletion functionality."""
    
    def test_delete_file_success(self, file_storage_service):
        """Test successful file deletion."""
        report_id = str(uuid.uuid4())
        user_id = 'test_user_123'
        
        mock_blob = MagicMock()
        file_storage_service.storage_bucket.list_blobs.return_value = [mock_blob]
        
        result = file_storage_service.delete_file(report_id, user_id)
        
        assert result is True
        mock_blob.delete.assert_called_once()
    
    def test_delete_file_not_found(self, file_storage_service):
        """Test file deletion raises error for non-existent file."""
        report_id = str(uuid.uuid4())
        user_id = 'test_user_123'
        
        file_storage_service.storage_bucket.list_blobs.return_value = []
        
        with pytest.raises(FileNotFoundError) as exc_info:
            file_storage_service.delete_file(report_id, user_id)
        
        assert 'Report not found' in str(exc_info.value)


class TestValidationResult:
    """Test ValidationResult class."""
    
    def test_validation_result_valid(self):
        """Test ValidationResult with valid state."""
        result = ValidationResult(valid=True)
        
        assert result.valid is True
        assert result.errors == []
        assert bool(result) is True
    
    def test_validation_result_invalid(self):
        """Test ValidationResult with invalid state."""
        errors = ['Error 1', 'Error 2']
        result = ValidationResult(valid=False, errors=errors)
        
        assert result.valid is False
        assert result.errors == errors
        assert bool(result) is False
