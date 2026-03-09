"""
Tests for secure API key management.

Tests secure key retrieval, validation, and graceful failure handling.

Requirements: 11.8
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from agents.infrastructure.api_key_manager import (
    APIKeyManager,
    APIKeyType,
    APIKeyValidationError,
    get_api_key_manager,
    validate_api_keys_on_startup
)


class TestAPIKeyManager:
    """Test suite for APIKeyManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = APIKeyManager()
    
    def test_get_api_key_success(self):
        """Test successful API key retrieval."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-gemini-key-12345'}):
            key = self.manager.get_api_key(APIKeyType.GEMINI, required=True)
            assert key == 'test-gemini-key-12345'
    
    def test_get_api_key_missing_required(self):
        """Test that missing required key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(APIKeyValidationError) as exc_info:
                self.manager.get_api_key(APIKeyType.GEMINI, required=True)
            
            assert 'not found' in str(exc_info.value).lower()
    
    def test_get_api_key_missing_optional(self):
        """Test that missing optional key returns None."""
        with patch.dict(os.environ, {}, clear=True):
            key = self.manager.get_api_key(APIKeyType.SEARCH, required=False)
            assert key is None
    
    def test_get_api_key_invalid_format(self):
        """Test that invalid key format is rejected."""
        # Key too short
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'short'}):
            with pytest.raises(APIKeyValidationError):
                self.manager.get_api_key(APIKeyType.GEMINI, required=True)
    
    def test_get_api_key_logs_access(self):
        """Test that API key access is logged."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-gemini-key-12345'}):
            initial_log_count = len(self.manager.get_access_log())
            self.manager.get_api_key(APIKeyType.GEMINI, required=True)
            
            # Should have logged the access
            assert len(self.manager.get_access_log()) > initial_log_count
            
            # Check log entry
            log_entries = self.manager.get_access_log()
            assert any('GEMINI_API_KEY' in entry['key_name'] for entry in log_entries)
    
    def test_validate_on_startup_all_valid(self):
        """Test startup validation with all valid keys."""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test-gemini-key-12345',
            'SEARCH_API_KEY': 'test-search-key-12345',
            'OPENAI_API_KEY': 'sk-test-openai-key-12345'
        }):
            results = self.manager.validate_on_startup()
            
            assert results['GEMINI_API_KEY'] is True
            assert results['SEARCH_API_KEY'] is True
            assert results['OPENAI_API_KEY'] is True
    
    def test_validate_on_startup_missing_critical(self):
        """Test startup validation with missing critical key."""
        with patch.dict(os.environ, {}, clear=True):
            results = self.manager.validate_on_startup()
            
            # Gemini is critical, should be False
            assert results['GEMINI_API_KEY'] is False
    
    def test_validate_on_startup_missing_optional(self):
        """Test startup validation with missing optional keys."""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test-gemini-key-12345'
        }, clear=True):
            results = self.manager.validate_on_startup()
            
            # Gemini should be valid
            assert results['GEMINI_API_KEY'] is True
            
            # Optional keys should be False but not cause failure
            assert results.get('SEARCH_API_KEY', False) is False
            assert results.get('OPENAI_API_KEY', False) is False
    
    def test_validate_key_format_gemini(self):
        """Test Gemini key format validation."""
        # Valid key
        assert self.manager._validate_key_format(
            'test-gemini-key-12345',
            APIKeyType.GEMINI
        ) is True
        
        # Too short
        assert self.manager._validate_key_format(
            'short',
            APIKeyType.GEMINI
        ) is False
        
        # Invalid characters
        assert self.manager._validate_key_format(
            'test@invalid#key',
            APIKeyType.GEMINI
        ) is False
    
    def test_validate_key_format_openai(self):
        """Test OpenAI key format validation."""
        # Valid key (starts with sk-)
        assert self.manager._validate_key_format(
            'sk-test-openai-key-12345',
            APIKeyType.OPENAI
        ) is True
        
        # Invalid (doesn't start with sk-)
        assert self.manager._validate_key_format(
            'test-openai-key-12345',
            APIKeyType.OPENAI
        ) is False
    
    def test_access_log_limit(self):
        """Test that access log is limited to prevent memory issues."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-gemini-key-12345'}):
            # Generate many log entries
            for _ in range(1500):
                try:
                    self.manager.get_api_key(APIKeyType.GEMINI, required=True)
                except:
                    pass
            
            # Should be limited to 1000 entries
            assert len(self.manager._access_log) <= 1000
    
    def test_is_key_validated(self):
        """Test checking if a key has been validated."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-gemini-key-12345'}):
            # Before validation
            assert self.manager.is_key_validated(APIKeyType.GEMINI) is False
            
            # Run validation
            self.manager.validate_on_startup()
            
            # After validation
            assert self.manager.is_key_validated(APIKeyType.GEMINI) is True
    
    def test_get_access_log_with_limit(self):
        """Test retrieving access log with limit."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-gemini-key-12345'}):
            # Generate some log entries
            for _ in range(10):
                self.manager.get_api_key(APIKeyType.GEMINI, required=True)
            
            # Get limited log
            log = self.manager.get_access_log(limit=5)
            assert len(log) <= 5


class TestGlobalAPIKeyManager:
    """Test global API key manager instance."""
    
    def test_get_api_key_manager_singleton(self):
        """Test that get_api_key_manager returns singleton instance."""
        manager1 = get_api_key_manager()
        manager2 = get_api_key_manager()
        
        assert manager1 is manager2
    
    def test_validate_api_keys_on_startup_function(self):
        """Test convenience function for startup validation."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-gemini-key-12345'}):
            results = validate_api_keys_on_startup()
            
            assert isinstance(results, dict)
            assert 'GEMINI_API_KEY' in results


class TestAPIKeyIntegration:
    """Integration tests for API key management."""
    
    def test_graceful_failure_for_invalid_keys(self):
        """
        Test graceful failure when keys are invalid.
        
        Requirements: 11.8 - Fail gracefully if keys are invalid
        """
        manager = APIKeyManager()
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'invalid'}):
            # Should raise error for required key with invalid format
            with pytest.raises(APIKeyValidationError):
                manager.get_api_key(APIKeyType.GEMINI, required=True)
    
    def test_secure_key_retrieval_no_exposure(self):
        """
        Test that keys are not exposed in logs.
        
        Requirements: 11.3 - Provide keys securely without exposing
        """
        manager = APIKeyManager()
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'secret-key-12345'}):
            manager.get_api_key(APIKeyType.GEMINI, required=True)
            
            # Check that the actual key is not in the log entries
            log_entries = manager.get_access_log()
            for entry in log_entries:
                # Log should contain key name but not the actual key value
                assert 'GEMINI_API_KEY' in str(entry)
                assert 'secret-key-12345' not in str(entry)
    
    def test_key_validation_on_startup(self):
        """
        Test key validation on startup.
        
        Requirements: 11.8 - Validate API keys on startup
        """
        manager = APIKeyManager()
        
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test-gemini-key-12345'
        }):
            results = manager.validate_on_startup()
            
            # Should validate successfully
            assert results['GEMINI_API_KEY'] is True
            
            # Should mark as validated
            assert manager.is_key_validated(APIKeyType.GEMINI) is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
