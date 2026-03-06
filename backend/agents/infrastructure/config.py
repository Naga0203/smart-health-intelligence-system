"""
Configuration data classes for autonomous AI agents.

Provides configuration structures for agent behavior, web search,
circuit breakers, and other infrastructure components.

Requirements: 12.1, 12.2, 12.3, 12.7, 12.8
"""

from dataclasses import dataclass, field
from typing import Optional
import logging

logger = logging.getLogger('health_ai.agents.infrastructure')


@dataclass
class CircuitConfig:
    """
    Configuration for circuit breaker behavior.
    
    Requirements: 12.3
    """
    failure_threshold: int = 5  # Number of failures before opening circuit
    timeout: int = 60  # Seconds to wait before attempting half-open
    half_open_timeout: int = 30  # Seconds in half-open state
    
    def __post_init__(self):
        """Validate configuration values."""
        if self.failure_threshold < 1:
            logger.warning(f"Invalid failure_threshold {self.failure_threshold}, using default 5")
            self.failure_threshold = 5
        
        if self.timeout < 1:
            logger.warning(f"Invalid timeout {self.timeout}, using default 60")
            self.timeout = 60
        
        if self.half_open_timeout < 1:
            logger.warning(f"Invalid half_open_timeout {self.half_open_timeout}, using default 30")
            self.half_open_timeout = 30


@dataclass
class SearchConfig:
    """
    Configuration for web search behavior.
    
    Requirements: 12.2
    """
    rate_limit: int = 10  # Requests per minute
    cache_ttl: int = 3600  # Cache time-to-live in seconds (1 hour)
    max_results: int = 10  # Maximum search results to return
    reliable_sources_only: bool = True  # Filter to reliable medical sources only
    timeout: int = 10  # Search request timeout in seconds
    
    def __post_init__(self):
        """Validate configuration values."""
        if self.rate_limit < 1:
            logger.warning(f"Invalid rate_limit {self.rate_limit}, using default 10")
            self.rate_limit = 10
        
        if self.cache_ttl < 0:
            logger.warning(f"Invalid cache_ttl {self.cache_ttl}, using default 3600")
            self.cache_ttl = 3600
        
        if self.max_results < 1:
            logger.warning(f"Invalid max_results {self.max_results}, using default 10")
            self.max_results = 10
        
        if self.timeout < 1:
            logger.warning(f"Invalid timeout {self.timeout}, using default 10")
            self.timeout = 10


@dataclass
class AgentConfig:
    """
    Configuration for agent behavior.
    
    Requirements: 12.1, 12.7, 12.8
    """
    agent_name: str
    timeout: int = 30  # Agent operation timeout in seconds
    max_retries: int = 3  # Maximum retry attempts for failed operations
    enable_web_search: bool = True  # Enable web search capabilities
    enable_caching: bool = True  # Enable result caching
    cache_ttl: int = 3600  # Cache time-to-live in seconds
    monitoring_enabled: bool = True  # Enable monitoring and metrics tracking
    
    # Nested configurations with defaults
    search_config: SearchConfig = field(default_factory=SearchConfig)
    circuit_config: CircuitConfig = field(default_factory=CircuitConfig)
    
    def __post_init__(self):
        """
        Validate configuration values.
        
        Requirements: 12.7 - Validate all configuration values on load
        """
        if not self.agent_name:
            raise ValueError("agent_name is required")
        
        if self.timeout < 1:
            logger.warning(f"Invalid timeout {self.timeout}, using default 30")
            self.timeout = 30
        
        if self.max_retries < 0:
            logger.warning(f"Invalid max_retries {self.max_retries}, using default 3")
            self.max_retries = 3
        
        if self.cache_ttl < 0:
            logger.warning(f"Invalid cache_ttl {self.cache_ttl}, using default 3600")
            self.cache_ttl = 3600
        
        # Ensure nested configs are initialized
        if not isinstance(self.search_config, SearchConfig):
            self.search_config = SearchConfig()
        
        if not isinstance(self.circuit_config, CircuitConfig):
            self.circuit_config = CircuitConfig()
        
        logger.info(f"AgentConfig initialized for {self.agent_name}")
    
    @classmethod
    def from_env(cls, agent_name: str) -> 'AgentConfig':
        """
        Create configuration from environment variables.
        
        Requirements: 12.1, 12.8 - Configuration through environment variables with defaults
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            AgentConfig instance with values from environment or defaults
        """
        import os
        
        return cls(
            agent_name=agent_name,
            timeout=int(os.getenv(f'{agent_name.upper()}_TIMEOUT', '30')),
            max_retries=int(os.getenv(f'{agent_name.upper()}_MAX_RETRIES', '3')),
            enable_web_search=os.getenv(f'{agent_name.upper()}_ENABLE_WEB_SEARCH', 'true').lower() == 'true',
            enable_caching=os.getenv(f'{agent_name.upper()}_ENABLE_CACHING', 'true').lower() == 'true',
            cache_ttl=int(os.getenv(f'{agent_name.upper()}_CACHE_TTL', '3600')),
            monitoring_enabled=os.getenv(f'{agent_name.upper()}_MONITORING_ENABLED', 'true').lower() == 'true',
            search_config=SearchConfig(
                rate_limit=int(os.getenv('SEARCH_RATE_LIMIT', '10')),
                cache_ttl=int(os.getenv('SEARCH_CACHE_TTL', '3600')),
                max_results=int(os.getenv('SEARCH_MAX_RESULTS', '10')),
                reliable_sources_only=os.getenv('SEARCH_RELIABLE_SOURCES_ONLY', 'true').lower() == 'true',
                timeout=int(os.getenv('SEARCH_TIMEOUT', '10')),
            ),
            circuit_config=CircuitConfig(
                failure_threshold=int(os.getenv('CIRCUIT_FAILURE_THRESHOLD', '5')),
                timeout=int(os.getenv('CIRCUIT_TIMEOUT', '60')),
                half_open_timeout=int(os.getenv('CIRCUIT_HALF_OPEN_TIMEOUT', '30')),
            )
        )
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            'agent_name': self.agent_name,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'enable_web_search': self.enable_web_search,
            'enable_caching': self.enable_caching,
            'cache_ttl': self.cache_ttl,
            'monitoring_enabled': self.monitoring_enabled,
            'search_config': {
                'rate_limit': self.search_config.rate_limit,
                'cache_ttl': self.search_config.cache_ttl,
                'max_results': self.search_config.max_results,
                'reliable_sources_only': self.search_config.reliable_sources_only,
                'timeout': self.search_config.timeout,
            },
            'circuit_config': {
                'failure_threshold': self.circuit_config.failure_threshold,
                'timeout': self.circuit_config.timeout,
                'half_open_timeout': self.circuit_config.half_open_timeout,
            }
        }
