"""
Configuration management system for autonomous AI agents.

Provides configuration loading, validation, hot reload, and default values.

Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8
"""

import os
import logging
from typing import Dict, Any, Optional, Callable
from threading import Lock
from datetime import datetime, timezone

from .config import AgentConfig, SearchConfig, CircuitConfig

logger = logging.getLogger('health_ai.agents.infrastructure')


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass


class ConfigurationManager:
    """
    Configuration management system with hot reload support.
    
    Manages configuration loading, validation, and hot reload for
    autonomous AI agents.
    
    Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8
    """
    
    def __init__(self):
        """Initialize configuration manager."""
        self._configs: Dict[str, AgentConfig] = {}
        self._config_lock = Lock()
        self._reload_callbacks: Dict[str, list] = {}
        self._last_reload: Optional[datetime] = None
        logger.info("ConfigurationManager initialized")
    
    def load_config(self, agent_name: str, force_reload: bool = False) -> AgentConfig:
        """
        Load configuration for an agent.
        
        Requirements:
        - 12.1: Configuration through environment variables
        - 12.7: Validate all configuration values on load
        - 12.8: Provide default values for all parameters
        
        Args:
            agent_name: Name of the agent
            force_reload: Force reload from environment even if cached
            
        Returns:
            AgentConfig instance
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        with self._config_lock:
            # Return cached config if available and not forcing reload
            if not force_reload and agent_name in self._configs:
                logger.debug(f"Using cached configuration for {agent_name}")
                return self._configs[agent_name]
            
            try:
                # Load from environment with validation
                config = AgentConfig.from_env(agent_name)
                
                # Cache the configuration
                self._configs[agent_name] = config
                
                logger.info(f"Configuration loaded for {agent_name}")
                return config
                
            except Exception as e:
                error_msg = f"Failed to load configuration for {agent_name}: {e}"
                logger.error(error_msg)
                raise ConfigurationError(error_msg) from e
    
    def reload_config(self, agent_name: str) -> AgentConfig:
        """
        Reload configuration for an agent from environment.
        
        Requirements: 12.6 - Apply changes without requiring restart
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Updated AgentConfig instance
        """
        logger.info(f"Reloading configuration for {agent_name}")
        
        # Force reload from environment
        config = self.load_config(agent_name, force_reload=True)
        
        # Update last reload time
        self._last_reload = datetime.now(timezone.utc)
        
        # Trigger callbacks
        self._trigger_reload_callbacks(agent_name, config)
        
        logger.info(f"Configuration reloaded for {agent_name}")
        return config
    
    def reload_all_configs(self) -> Dict[str, AgentConfig]:
        """
        Reload all cached configurations.
        
        Requirements: 12.6 - Apply changes without requiring restart
        
        Returns:
            Dictionary of agent names to updated configs
        """
        logger.info("Reloading all configurations")
        
        with self._config_lock:
            agent_names = list(self._configs.keys())
        
        reloaded_configs = {}
        for agent_name in agent_names:
            try:
                config = self.reload_config(agent_name)
                reloaded_configs[agent_name] = config
            except Exception as e:
                logger.error(f"Failed to reload config for {agent_name}: {e}")
        
        logger.info(f"Reloaded {len(reloaded_configs)} configurations")
        return reloaded_configs
    
    def register_reload_callback(self, agent_name: str, callback: Callable[[AgentConfig], None]):
        """
        Register a callback to be called when configuration is reloaded.
        
        Requirements: 12.6 - Hot reload support
        
        Args:
            agent_name: Name of the agent
            callback: Function to call with new config
        """
        if agent_name not in self._reload_callbacks:
            self._reload_callbacks[agent_name] = []
        
        self._reload_callbacks[agent_name].append(callback)
        logger.debug(f"Registered reload callback for {agent_name}")
    
    def _trigger_reload_callbacks(self, agent_name: str, config: AgentConfig):
        """
        Trigger reload callbacks for an agent.
        
        Args:
            agent_name: Name of the agent
            config: New configuration
        """
        callbacks = self._reload_callbacks.get(agent_name, [])
        
        for callback in callbacks:
            try:
                callback(config)
                logger.debug(f"Triggered reload callback for {agent_name}")
            except Exception as e:
                logger.error(f"Reload callback failed for {agent_name}: {e}")
    
    def get_config(self, agent_name: str) -> Optional[AgentConfig]:
        """
        Get cached configuration for an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            AgentConfig if cached, None otherwise
        """
        with self._config_lock:
            return self._configs.get(agent_name)
    
    def validate_config(self, config: AgentConfig) -> bool:
        """
        Validate a configuration object.
        
        Requirements: 12.7 - Validate all configuration values
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required fields
            if not config.agent_name:
                logger.error("Configuration missing agent_name")
                return False
            
            # Check numeric ranges
            if config.timeout < 1:
                logger.error(f"Invalid timeout: {config.timeout}")
                return False
            
            if config.max_retries < 0:
                logger.error(f"Invalid max_retries: {config.max_retries}")
                return False
            
            if config.cache_ttl < 0:
                logger.error(f"Invalid cache_ttl: {config.cache_ttl}")
                return False
            
            # Validate nested configs
            if not isinstance(config.search_config, SearchConfig):
                logger.error("Invalid search_config")
                return False
            
            if not isinstance(config.circuit_config, CircuitConfig):
                logger.error("Invalid circuit_config")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return False
    
    def get_all_configs(self) -> Dict[str, AgentConfig]:
        """
        Get all cached configurations.
        
        Returns:
            Dictionary of agent names to configs
        """
        with self._config_lock:
            return self._configs.copy()
    
    def clear_cache(self):
        """Clear all cached configurations."""
        with self._config_lock:
            self._configs.clear()
            logger.info("Configuration cache cleared")
    
    def get_last_reload_time(self) -> Optional[datetime]:
        """
        Get the timestamp of the last configuration reload.
        
        Returns:
            Datetime of last reload, or None if never reloaded
        """
        return self._last_reload
    
    def export_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Export configuration as dictionary.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Configuration dictionary or None if not found
        """
        config = self.get_config(agent_name)
        if config:
            return config.to_dict()
        return None
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get summary of all configurations.
        
        Returns:
            Summary dictionary with config counts and status
        """
        with self._config_lock:
            return {
                'total_configs': len(self._configs),
                'agent_names': list(self._configs.keys()),
                'last_reload': self._last_reload.isoformat() if self._last_reload else None,
                'callback_count': sum(len(cbs) for cbs in self._reload_callbacks.values())
            }


# Global instance for application-wide use
_config_manager = None


def get_config_manager() -> ConfigurationManager:
    """
    Get the global configuration manager instance.
    
    Returns:
        Global ConfigurationManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def load_agent_config(agent_name: str) -> AgentConfig:
    """
    Convenience function to load agent configuration.
    
    Requirements: 12.1, 12.7, 12.8
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        AgentConfig instance
    """
    manager = get_config_manager()
    return manager.load_config(agent_name)


def reload_agent_config(agent_name: str) -> AgentConfig:
    """
    Convenience function to reload agent configuration.
    
    Requirements: 12.6
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Updated AgentConfig instance
    """
    manager = get_config_manager()
    return manager.reload_config(agent_name)
