"""
Startup validation and initialization for autonomous AI agents.

Validates API keys and configuration on system startup.

Requirements: 11.8
"""

import logging
from typing import Dict, Tuple

logger = logging.getLogger('health_ai.agents.infrastructure')


def validate_system_startup() -> Tuple[bool, Dict[str, bool]]:
    """
    Validate system configuration and API keys on startup.
    
    Requirements: 11.8 - Validate API keys on startup and fail gracefully
    
    Returns:
        Tuple of (success, validation_results)
        - success: True if all critical validations passed
        - validation_results: Dictionary of validation results
    """
    logger.info("=" * 60)
    logger.info("Starting system validation...")
    logger.info("=" * 60)
    
    validation_results = {}
    critical_failures = []
    
    # Validate API keys
    try:
        from agents.infrastructure.api_key_manager import validate_api_keys_on_startup, APIKeyType
        
        logger.info("Validating API keys...")
        api_key_results = validate_api_keys_on_startup()
        validation_results['api_keys'] = api_key_results
        
        # Check for critical API key failures
        if not api_key_results.get(APIKeyType.GEMINI.value, False):
            critical_failures.append("Gemini API key is missing or invalid")
        
    except Exception as e:
        logger.error(f"API key validation failed: {e}")
        validation_results['api_keys'] = {}
        critical_failures.append(f"API key validation error: {e}")
    
    # Validate configuration
    try:
        from agents.infrastructure.config import AgentConfig
        
        logger.info("Validating configuration system...")
        # Test configuration loading
        test_config = AgentConfig.from_env("test_agent")
        validation_results['configuration'] = True
        logger.info("✓ Configuration system validated")
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        validation_results['configuration'] = False
        critical_failures.append(f"Configuration validation error: {e}")
    
    # Log summary
    logger.info("=" * 60)
    if critical_failures:
        logger.error("CRITICAL FAILURES DETECTED:")
        for failure in critical_failures:
            logger.error(f"  ✗ {failure}")
        logger.error("=" * 60)
        logger.error("System startup validation FAILED")
        logger.error("The system may not function properly with missing critical components")
        logger.error("=" * 60)
        return False, validation_results
    else:
        logger.info("✓ All critical validations passed")
        logger.info("=" * 60)
        logger.info("System startup validation SUCCESSFUL")
        logger.info("=" * 60)
        return True, validation_results


def log_startup_info():
    """Log system startup information."""
    import sys
    import os
    
    logger.info("=" * 60)
    logger.info("Health AI Backend - Autonomous Agents System")
    logger.info("=" * 60)
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Environment: {os.getenv('DJANGO_ENV', 'development')}")
    logger.info("=" * 60)
