"""
Common utilities package for Health Intelligence System

This package contains shared utilities, database connections,
and external service integrations.
"""

from .gemini_client import GeminiClient

__all__ = [
    'GeminiClient'
]