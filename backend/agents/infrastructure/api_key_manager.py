"""
Secure API key management for autonomous AI agents.

Provides secure retrieval, validation, and logging of API keys
for Gemini AI and web search services.

Requirements: 11.1, 11.2, 11.3, 11.5, 11.8
"""

import os
import logging
from typing import Optional, Dict
from datetime import datetime
from enum import Enum

logger = logging.getLogger('health_ai.agents.infrastructure')


class APIKeyType(Enum):
    """Types of API keys managed by the system."""
    GEMINI = "GEMINI_API_KEY"
    SEARCH = "SEARCH_API_KEY"
    OPENAI = "OPENAI_API_KEY"


class APIKeyValidationError(Exception):
    """Raised when API key validation fails."""
    pass


class APIKeyManager:
    """
    Secure API key management system.
    
    Manages API keys for external services with secure retrieval,
    validation, and access logging.
    
    Requirements: 11.1, 11.2, 11.3, 11.5, 11.8
    """
    
    def __init__(self):
        """Initialize API key manager."""
        self._access_log: list = []
        self._validated_keys: Dict[str, bool] = {}
        logger.info("APIKeyManager initialized")
    
    def get_api_key(self, key_type: APIKeyType, required: bool = True) -> Optional[str]:
        """
        Securely retrieve an API key from environment variables.
        
        Requirements:
        - 11.1: Store API keys in environment variables
        - 11.3: Provide keys securely without exposing in logs
        - 11.5: Log all API key access attempts
        
        Args:
            key_type: Type of API key to retrieve
            required: Whether the key is required (raises error if missing)
            
        Returns:
            API key string or None if not required and not found
            
        Raises:
            APIKeyValidationError: If required key is missing or invalid
        """
        key_name = key_type.value
        
        # Log access attempt (without exposing the key)
        self._log_access(key_name, "retrieve")
        
        # Retrieve from environment variable
        api_key = os.getenv(key_name)
        
        if not api_key:
            if required:
                error_msg = f"Required API key {key_name} not found in environment variables"
                logger.error(error_msg)
                self._log_access(key_name, "retrieve_failed", success=False)
                raise APIKeyValidationError(error_msg)
            else:
                logger.warning(f"Optional API key {key_name} not found")
                self._log_access(key_name, "retrieve_missing", success=True)
                return None
        
        # Validate the key format
        if not self._validate_key_format(api_key, key_type):
            error_msg = f"API key {key_name} has invalid format"
            logger.error(error_msg)
            self._log_access(key_name, "retrieve_invalid", success=False)
            if required:
                raise APIKeyValidationError(error_msg)
            return None
        
        self._log_access(key_name, "retrieve_success", success=True)
        logger.info(f"Successfully retrieved API key: {key_name}")
        
        return api_key
    
    def validate_on_startup(self) -> Dict[str, bool]:
        """
        Validate all required API keys on system startup.
        
        Requirements:
        - 11.8: Validate API keys on startup and fail gracefully if invalid
        
        Returns:
            Dictionary mapping key names to validation status
        """
        logger.info("Validating API keys on startup...")
        validation_results = {}
        
        # Validate required keys
        required_keys = [APIKeyType.GEMINI]
        
        for key_type in required_keys:
            key_name = key_type.value
            try:
                api_key = self.get_api_key(key_type, required=True)
                validation_results[key_name] = True
                self._validated_keys[key_name] = True
                logger.info(f"✓ {key_name} validated successfully")
            except APIKeyValidationError as e:
                validation_results[key_name] = False
                self._validated_keys[key_name] = False
                logger.error(f"✗ {key_name} validation failed: {e}")
        
        # Validate optional keys
        optional_keys = [APIKeyType.SEARCH, APIKeyType.OPENAI]
        
        for key_type in optional_keys:
            key_name = key_type.value
            try:
                api_key = self.get_api_key(key_type, required=False)
                if api_key:
                    validation_results[key_name] = True
                    self._validated_keys[key_name] = True
                    logger.info(f"✓ {key_name} validated successfully")
                else:
                    validation_results[key_name] = False
                    self._validated_keys[key_name] = False
                    logger.warning(f"○ {key_name} not configured (optional)")
            except Exception as e:
                validation_results[key_name] = False
                self._validated_keys[key_name] = False
                logger.warning(f"○ {key_name} validation failed: {e} (optional)")
        
        # Log summary
        total_keys = len(validation_results)
        valid_keys = sum(1 for v in validation_results.values() if v)
        logger.info(f"API key validation complete: {valid_keys}/{total_keys} keys valid")
        
        # Check if critical keys are missing
        if not validation_results.get(APIKeyType.GEMINI.value, False):
            logger.critical("CRITICAL: Gemini API key is missing or invalid. System may not function properly.")
        
        return validation_results
    
    def _validate_key_format(self, api_key: str, key_type: APIKeyType) -> bool:
        """
        Validate API key format.
        
        Requirements: 11.8 - Validate API keys
        
        Args:
            api_key: The API key to validate
            key_type: Type of API key
            
        Returns:
            True if key format is valid, False otherwise
        """
        if not api_key or not isinstance(api_key, str):
            return False
        
        # Basic validation: key should not be empty and should have minimum length
        if len(api_key.strip()) < 10:
            return False
        
        # Key-specific validation
        if key_type == APIKeyType.GEMINI:
            # Gemini keys typically start with specific patterns
            # Basic check: should be alphanumeric with possible dashes/underscores
            if not all(c.isalnum() or c in '-_' for c in api_key):
                return False
        
        elif key_type == APIKeyType.OPENAI:
            # OpenAI keys start with 'sk-'
            if not api_key.startswith('sk-'):
                return False
        
        return True
    
    def _log_access(self, key_name: str, operation: str, success: bool = True):
        """
        Log API key access attempts.
        
        Requirements: 11.5 - Log all API key access attempts
        
        Args:
            key_name: Name of the API key
            operation: Operation performed (retrieve, validate, etc.)
            success: Whether the operation was successful
        """
        from datetime import datetime, timezone
        
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'key_name': key_name,
            'operation': operation,
            'success': success
        }
        
        self._access_log.append(log_entry)
        
        # Keep only last 1000 entries to prevent memory issues
        if len(self._access_log) > 1000:
            self._access_log = self._access_log[-1000:]
    
    def get_access_log(self, limit: int = 100) -> list:
        """
        Get recent API key access log entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of recent log entries
        """
        return self._access_log[-limit:]
    
    def is_key_validated(self, key_type: APIKeyType) -> bool:
        """
        Check if a key has been validated.
        
        Args:
            key_type: Type of API key
            
        Returns:
            True if key has been validated, False otherwise
        """
        return self._validated_keys.get(key_type.value, False)


# Global instance for application-wide use
_api_key_manager = None


def get_api_key_manager() -> APIKeyManager:
    """
    Get the global API key manager instance.
    
    Returns:
        Global APIKeyManager instance
    """
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager


def validate_api_keys_on_startup() -> Dict[str, bool]:
    """
    Convenience function to validate API keys on startup.
    
    Requirements: 11.8 - Validate API keys on startup
    
    Returns:
        Dictionary mapping key names to validation status
    """
    manager = get_api_key_manager()
    return manager.validate_on_startup()
