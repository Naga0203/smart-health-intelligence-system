"""
Custom Exception Classes for AI Health Intelligence System

Provides structured exception hierarchy for better error handling,
logging, and user-friendly error messages.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger('health_ai.errors')


class HealthAIException(Exception):
    """
    Base exception for all Health AI system errors.
    
    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code
        details: Additional error context
        user_message: User-friendly message (for API responses)
    """
    
    def __init__(
        self, 
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.user_message = user_message or message
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.error_code,
            "message": self.user_message,
            "details": self.details
        }


class ValidationError(HealthAIException):
    """
    Input validation errors.
    
    Used when user input fails validation checks.
    """
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if field:
            error_details['field'] = field
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=error_details,
            user_message="Invalid input provided. Please check your data and try again."
        )


class AuthenticationError(HealthAIException):
    """
    Firebase authentication errors.
    
    Used when Firebase token validation fails.
    """
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details,
            user_message="Authentication failed. Please log in again."
        )


class AuthorizationError(HealthAIException):
    """
    Authorization/permission errors.
    
    Used when user lacks permission for requested action.
    """
    
    def __init__(self, message: str, resource: Optional[str] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if resource:
            error_details['resource'] = resource
        
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=error_details,
            user_message="You don't have permission to access this resource."
        )


class PredictionError(HealthAIException):
    """
    ML prediction errors.
    
    Used when ML model prediction fails.
    """
    
    def __init__(self, message: str, disease: Optional[str] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if disease:
            error_details['disease'] = disease
        
        super().__init__(
            message=message,
            error_code="PREDICTION_ERROR",
            details=error_details,
            user_message="Unable to complete health assessment. Please try again."
        )


class GeminiAPIError(HealthAIException):
    """
    Google Gemini AI API errors.
    
    Used when Gemini AI service fails.
    """
    
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if operation:
            error_details['operation'] = operation
        
        super().__init__(
            message=message,
            error_code="GEMINI_API_ERROR",
            details=error_details,
            user_message="AI service temporarily unavailable. Please try again in a moment."
        )


class DatabaseError(HealthAIException):
    """
    Database operation errors (MongoDB/Firestore).
    
    Used when database operations fail.
    """
    
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if operation:
            error_details['operation'] = operation
        
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=error_details,
            user_message="Database error occurred. Please try again."
        )


class CacheError(HealthAIException):
    """
    Cache operation errors (Redis).
    
    Used when cache operations fail. Non-critical - system should continue.
    """
    
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if operation:
            error_details['operation'] = operation
        
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            details=error_details,
            user_message="Temporary performance issue. Your request is processing."
        )


class ExternalServiceError(HealthAIException):
    """
    External service errors.
    
    Used when external services (not Gemini) fail.
    """
    
    def __init__(self, message: str, service: Optional[str] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if service:
            error_details['service'] = service
        
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=error_details,
            user_message="External service temporarily unavailable. Please try again later."
        )


class RateLimitError(HealthAIException):
    """
    Rate limiting errors.
    
    Used when user exceeds rate limits.
    """
    
    def __init__(self, message: str, retry_after: Optional[int] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if retry_after:
            error_details['retry_after_seconds'] = retry_after
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details=error_details,
            user_message=f"Too many requests. Please try again in {retry_after or 'a few'} seconds."
        )


class DataNotFoundError(HealthAIException):
    """
    Resource not found errors.
    
    Used when requested resource doesn't exist.
    """
    
    def __init__(self, message: str, resource_type: Optional[str] = None, resource_id: Optional[str] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if resource_type:
            error_details['resource_type'] = resource_type
        if resource_id:
            error_details['resource_id'] = resource_id
        
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            details=error_details,
            user_message="The requested resource was not found."
        )


class ConfigurationError(HealthAIException):
    """
    Configuration errors.
    
    Used when system configuration is invalid or missing.
    """
    
    def __init__(self, message: str, config_key: Optional[str] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if config_key:
            error_details['config_key'] = config_key
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=error_details,
            user_message="System configuration error. Please contact support."
        )


# Convenience function for logging errors with context
def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """
    Log error with full context information.
    
    Args:
        error: Exception to log
        context: Additional context (user_id, request_id, etc.)
    """
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error)
    }
    
    # Add custom error details if available
    if isinstance(error, HealthAIException):
        error_info.update({
            "error_code": error.error_code,
            "error_details": error.details
        })
    
    # Add context
    if context:
        error_info["context"] = context
    
    logger.error(f"Error occurred: {error_info}", exc_info=True)
