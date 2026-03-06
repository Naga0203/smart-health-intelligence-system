"""
Cache Service for AI Health Intelligence System

Provides centralized caching using Redis for:
- Treatment data (rarely changes, perfect for caching)
- User profiles (frequent reads)
- System status and metadata
- Common Gemini AI responses

Uses Django's cache framework with Redis backend.

Error Handling (Requirements 3.3, 3.4):
- Graceful degradation on Redis failure
- Cache reconnection logic (30-second intervals)
- Serialization error handling
"""

import logging
import json
import hashlib
import time
import asyncio
from typing import Any, Optional, Dict, Callable
from functools import wraps
from .errors import CacheError

logger = logging.getLogger('health_ai.cache')

# Try to import Django cache, fallback to no-op if not available
try:
    from django.core.cache import cache
    CACHE_AVAILABLE = True
except ImportError:
    logger.warning("Django cache not available, caching will be disabled")
    CACHE_AVAILABLE = False
    cache = None


class CacheService:
    """
    Centralized caching service with graceful fallback.
    
    Features:
    - Automatic fallback if Redis is unavailable (Requirement 3.3)
    - Configurable TTLs for different data types
    - Cache key versioning
    - Pattern-based invalidation
    - Reconnection logic (Requirement 3.4)
    - Serialization error handling (Requirement 3.4)
    """
    
    # Cache TTLs (in seconds)
    TREATMENT_DATA_TTL = 86400      # 24 hours - rarely changes
    USER_PROFILE_TTL = 3600         # 1 hour - changes occasionally
    SYSTEM_STATUS_TTL = 300         # 5 minutes - changes frequently
    ML_MODEL_INFO_TTL = 3600        # 1 hour - rarely changes
    GEMINI_RESPONSE_TTL = 7200      # 2 hours - for common queries
    ASSESSMENT_TTL = 1800           # 30 minutes
    
    # Cache key prefix for versioning
    VERSION = "v1"
    
    # Reconnection configuration (Requirement 3.4)
    RECONNECT_INTERVAL = 30  # seconds
    _last_reconnect_attempt = 0
    _cache_unavailable = False
    _reconnect_task = None
    
    @staticmethod
    def _is_available() -> bool:
        """
        Check if cache is available.
        
        Requirement 3.3: Graceful degradation on Redis failure
        """
        if not CACHE_AVAILABLE or cache is None:
            return False
        
        # If we know cache is unavailable, check if it's time to retry
        if CacheService._cache_unavailable:
            current_time = time.time()
            if current_time - CacheService._last_reconnect_attempt >= CacheService.RECONNECT_INTERVAL:
                # Try to reconnect
                if CacheService._try_reconnect():
                    CacheService._cache_unavailable = False
                    logger.info("Cache reconnected successfully")
                    return True
                else:
                    CacheService._last_reconnect_attempt = current_time
                    return False
            return False
        
        return True
    
    @staticmethod
    def _try_reconnect() -> bool:
        """
        Attempt to reconnect to cache.
        
        Requirement 3.4: Cache reconnection logic (30-second intervals)
        
        Returns:
            True if reconnection successful, False otherwise
        """
        try:
            # Try a simple operation to test connection
            test_key = CacheService._make_key("_health_check")
            cache.set(test_key, "ok", timeout=10)
            result = cache.get(test_key)
            cache.delete(test_key)
            return result == "ok"
        except Exception as e:
            logger.debug(f"Cache reconnection failed: {e}")
            return False
    
    @staticmethod
    def _mark_unavailable():
        """Mark cache as unavailable and schedule reconnection attempts."""
        if not CacheService._cache_unavailable:
            CacheService._cache_unavailable = True
            CacheService._last_reconnect_attempt = time.time()
            logger.warning("Cache marked as unavailable - will retry every 30s")
    
    @staticmethod
    def _make_key(*parts: str) -> str:
        """
        Create cache key from parts.
        
        Args:
            *parts: Key components
            
        Returns:
            Versioned cache key
        """
        key_parts = [CacheService.VERSION] + list(parts)
        return ":".join(str(part) for part in key_parts)
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Get value from cache with graceful degradation.
        
        Requirement 3.3: Graceful degradation on Redis failure
        
        Args:
            key: Cache key
            default: Default value if not found or cache unavailable
            
        Returns:
            Cached value or default
        """
        if not CacheService._is_available():
            logger.debug(f"Cache unavailable, returning default for: {key}")
            return default
        
        try:
            value = cache.get(key, default)
            if value is not None and value != default:
                logger.debug(f"Cache HIT: {key}")
            else:
                logger.debug(f"Cache MISS: {key}")
            return value
        except Exception as e:
            logger.warning(f"Cache get error for key '{key}': {str(e)}")
            CacheService._mark_unavailable()
            return default
    
    @staticmethod
    def set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache with serialization error handling.
        
        Requirement 3.4: Handle serialization errors
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None = default TTL)
            
        Returns:
            True if successful, False otherwise
        """
        if not CacheService._is_available():
            logger.debug(f"Cache unavailable, skipping set for: {key}")
            return False
        
        try:
            cache.set(key, value, ttl)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except (TypeError, ValueError) as e:
            # Serialization error
            logger.warning(f"Cache serialization error for key '{key}': {str(e)}")
            logger.debug(f"Problematic value type: {type(value)}")
            return False
        except Exception as e:
            logger.warning(f"Cache set error for key '{key}': {str(e)}")
            CacheService._mark_unavailable()
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """
        Delete value from cache with graceful degradation.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        if not CacheService._is_available():
            logger.debug(f"Cache unavailable, skipping delete for: {key}")
            return False
        
        try:
            cache.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key '{key}': {str(e)}")
            CacheService._mark_unavailable()
            return False
    
    @staticmethod
    def delete_pattern(pattern: str) -> bool:
        """
        Delete all keys matching pattern with graceful degradation.
        
        Args:
            pattern: Key pattern (e.g., "treatment:*")
            
        Returns:
            True if successful, False otherwise
        """
        if not CacheService._is_available():
            logger.debug(f"Cache unavailable, skipping delete_pattern for: {pattern}")
            return False
        
        try:
            # Django-redis specific method
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(pattern)
                logger.info(f"Cache DELETE PATTERN: {pattern}")
                return True
            else:
                logger.warning("delete_pattern not supported by cache backend")
                return False
        except Exception as e:
            logger.warning(f"Cache delete_pattern error for '{pattern}': {str(e)}")
            CacheService._mark_unavailable()
            return False
    
    # Domain-specific caching methods
    
    @staticmethod
    def get_treatment_data(disease: str, system: str) -> Optional[Dict]:
        """
        Get cached treatment data.
        
        Args:
            disease: Disease name
            system: Medical system (allopathy, homeopathy, etc.)
            
        Returns:
            Cached treatment data or None
        """
        key = CacheService._make_key("treatment", disease, system)
        return CacheService.get(key)
    
    @staticmethod
    def set_treatment_data(disease: str, system: str, data: Dict) -> bool:
        """
        Cache treatment data.
        
        Args:
            disease: Disease name
            system: Medical system
            data: Treatment data to cache
            
        Returns:
            True if successful
        """
        key = CacheService._make_key("treatment", disease, system)
        return CacheService.set(key, data, CacheService.TREATMENT_DATA_TTL)
    
    @staticmethod
    def invalidate_treatment_data(disease: Optional[str] = None) -> bool:
        """
        Invalidate treatment data cache.
        
        Args:
            disease: Specific disease to invalidate, or None for all
            
        Returns:
            True if successful
        """
        if disease:
            # Invalidate all systems for this disease
            pattern = CacheService._make_key("treatment", disease, "*")
        else:
            # Invalidate all treatment data
            pattern = CacheService._make_key("treatment", "*")
        
        return CacheService.delete_pattern(pattern)
    
    @staticmethod
    def get_user_profile(user_id: str) -> Optional[Dict]:
        """Get cached user profile."""
        key = CacheService._make_key("user_profile", user_id)
        return CacheService.get(key)
    
    @staticmethod
    def set_user_profile(user_id: str, profile: Dict) -> bool:
        """Cache user profile."""
        key = CacheService._make_key("user_profile", user_id)
        return CacheService.set(key, profile, CacheService.USER_PROFILE_TTL)
    
    @staticmethod
    def invalidate_user_profile(user_id: str) -> bool:
        """Invalidate user profile cache."""
        key = CacheService._make_key("user_profile", user_id)
        return CacheService.delete(key)
    
    @staticmethod
    def get_system_status() -> Optional[Dict]:
        """Get cached system status."""
        key = CacheService._make_key("system_status")
        return CacheService.get(key)
    
    @staticmethod
    def set_system_status(status: Dict) -> bool:
        """Cache system status."""
        key = CacheService._make_key("system_status")
        return CacheService.set(key, status, CacheService.SYSTEM_STATUS_TTL)
    
    @staticmethod
    def get_ml_model_info(disease: str) -> Optional[Dict]:
        """Get cached ML model info."""
        key = CacheService._make_key("ml_model", disease)
        return CacheService.get(key)
    
    @staticmethod
    def set_ml_model_info(disease: str, info: Dict) -> bool:
        """Cache ML model info."""
        key = CacheService._make_key("ml_model", disease)
        return CacheService.set(key, info, CacheService.ML_MODEL_INFO_TTL)
    
    @staticmethod
    def get_gemini_response(prompt_hash: str) -> Optional[Dict]:
        """
        Get cached Gemini AI response.
        
        Args:
            prompt_hash: Hash of the prompt
            
        Returns:
            Cached response or None
        """
        key = CacheService._make_key("gemini", prompt_hash)
        return CacheService.get(key)
    
    @staticmethod
    def set_gemini_response(prompt_hash: str, response: Dict) -> bool:
        """Cache Gemini AI response."""
        key = CacheService._make_key("gemini", prompt_hash)
        return CacheService.set(key, response, CacheService.GEMINI_RESPONSE_TTL)
    
    @staticmethod
    def hash_prompt(prompt: str) -> str:
        """
        Create hash of prompt for caching.
        
        Args:
            prompt: Prompt text
            
        Returns:
            SHA256 hash of prompt
        """
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]


def cached(ttl: Optional[int] = None, key_func: Optional[Callable] = None):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Cache TTL in seconds
        key_func: Function to generate cache key from args
        
    Example:
        @cached(ttl=3600)
        def expensive_operation(param1, param2):
            # ... complex computation
            return result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: use function name and str representation of args
                key_parts = [func.__name__] + [str(arg) for arg in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
                cache_key = CacheService._make_key(*key_parts)
            
            # Try to get from cache
            cached_result = CacheService.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            CacheService.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Statistics tracking
class CacheStats:
    """Track cache hit/miss statistics."""
    
    hits = 0
    misses = 0
    errors = 0
    
    @classmethod
    def record_hit(cls):
        cls.hits += 1
    
    @classmethod
    def record_miss(cls):
        cls.misses += 1
    
    @classmethod
    def record_error(cls):
        cls.errors += 1
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get cache statistics."""
        total = cls.hits + cls.misses
        hit_rate = (cls.hits / total * 100) if total > 0 else 0
        
        return {
            "hits": cls.hits,
            "misses": cls.misses,
            "errors": cls.errors,
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 2)
        }
    
    @classmethod
    def reset(cls):
        """Reset statistics."""
        cls.hits = 0
        cls.misses = 0
        cls.errors = 0
