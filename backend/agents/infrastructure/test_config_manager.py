"""
Tests for configuration management system.

Tests configuration loading, validation, default values, and hot reload.

Requirements: 12.7, 12.8
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from agents.infrastructure.config_manager import (
    ConfigurationManager,
    ConfigurationError,
    get_config_manager,
    load_agent_config,
    reload_agent_config
)
from agents.infrastructure.config import AgentConfig, SearchConfig, CircuitConfig


class TestConfigurationManager:
    """Test suite for ConfigurationManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ConfigurationManager()
    
    def test_load_config_from_env(self):
        """
        Test configuration loading from environment variables.
        
        Requirements: 12.1 - Configuration through environment variables
        """
        with patch.dict(os.environ, {
            'TEST_AGENT_TIMEOUT': '60',
            'TEST_AGENT_MAX_RETRIES': '5',
            'TEST_AGENT_ENABLE_WEB_SEARCH': 'true',
            'SEARCH_RATE_LIMIT': '20'
        }):
            config = self.manager.load_config('test_agent')
            
            assert config.agent_name == 'test_agent'
            assert config.timeout == 60
            assert config.max_retries == 5
            assert config.enable_web_search is True
            assert config.search_config.rate_limit == 20
    
    def test_load_config_with_defaults(self):
        """
        Test that default values are used when env vars not set.
        
        Requirements: 12.8 - Provide default values for all parameters
        """
        with patch.dict(os.environ, {}, clear=True):
            config = self.manager.load_config('test_agent')
            
            # Should use default values
            assert config.timeout == 30  # default
            assert config.max_retries == 3  # default
            assert config.enable_web_search is True  # default
            assert config.cache_ttl == 3600  # default
    
    def test_load_config_caching(self):
        """Test that configurations are cached."""
        with patch.dict(os.environ, {'TEST_AGENT_TIMEOUT': '60'}):
            config1 = self.manager.load_config('test_agent')
            config2 = self.manager.load_config('test_agent')
            
            # Should return same cached instance
            assert config1 is config2
    
    def test_load_config_force_reload(self):
        """Test force reload bypasses cache."""
        with patch.dict(os.environ, {'TEST_AGENT_TIMEOUT': '60'}):
            config1 = self.manager.load_config('test_agent')
        
        # Change environment
        with patch.dict(os.environ, {'TEST_AGENT_TIMEOUT': '90'}):
            config2 = self.manager.load_config('test_agent', force_reload=True)
            
            # Should have new timeout value
            assert config2.timeout == 90
            assert config1 is not config2
    
    def test_validate_config_valid(self):
        """
        Test validation of valid configuration.
        
        Requirements: 12.7 - Validate all configuration values
        """
        config = AgentConfig(
            agent_name='test_agent',
            timeout=30,
            max_retries=3,
            cache_ttl=3600
        )
        
        assert self.manager.validate_config(config) is True
    
    def test_validate_config_invalid_timeout(self):
        """
        Test validation rejects invalid timeout.
        
        Requirements: 12.7 - Validate all configuration values
        """
        # Create config with invalid timeout directly (bypass __post_init__)
        config = AgentConfig.__new__(AgentConfig)
        config.agent_name = 'test_agent'
        config.timeout = 0  # Invalid
        config.max_retries = 3
        config.cache_ttl = 3600
        config.search_config = SearchConfig()
        config.circuit_config = CircuitConfig()
        
        assert self.manager.validate_config(config) is False
    
    def test_validate_config_invalid_retries(self):
        """
        Test validation rejects invalid max_retries.
        
        Requirements: 12.7 - Validate all configuration values
        """
        # Create config with invalid retries directly (bypass __post_init__)
        config = AgentConfig.__new__(AgentConfig)
        config.agent_name = 'test_agent'
        config.timeout = 30
        config.max_retries = -1  # Invalid
        config.cache_ttl = 3600
        config.search_config = SearchConfig()
        config.circuit_config = CircuitConfig()
        
        assert self.manager.validate_config(config) is False
    
    def test_validate_config_missing_agent_name(self):
        """Test validation rejects missing agent_name."""
        # Create config with empty agent_name directly (bypass __post_init__)
        config = AgentConfig.__new__(AgentConfig)
        config.agent_name = ''  # Invalid
        config.timeout = 30
        config.max_retries = 3
        config.cache_ttl = 3600
        config.search_config = SearchConfig()
        config.circuit_config = CircuitConfig()
        
        assert self.manager.validate_config(config) is False
    
    def test_reload_config(self):
        """
        Test configuration hot reload.
        
        Requirements: 12.6 - Apply changes without requiring restart
        """
        # Load initial config
        with patch.dict(os.environ, {'TEST_AGENT_TIMEOUT': '60'}):
            config1 = self.manager.load_config('test_agent')
            assert config1.timeout == 60
        
        # Change environment and reload
        with patch.dict(os.environ, {'TEST_AGENT_TIMEOUT': '90'}):
            config2 = self.manager.reload_config('test_agent')
            
            # Should have new value
            assert config2.timeout == 90
            
            # Should update cache
            cached_config = self.manager.get_config('test_agent')
            assert cached_config.timeout == 90
    
    def test_reload_all_configs(self):
        """
        Test reloading all configurations.
        
        Requirements: 12.6 - Hot reload support
        """
        # Load multiple configs
        with patch.dict(os.environ, {
            'AGENT1_TIMEOUT': '60',
            'AGENT2_TIMEOUT': '70'
        }):
            self.manager.load_config('agent1')
            self.manager.load_config('agent2')
        
        # Change environment and reload all
        with patch.dict(os.environ, {
            'AGENT1_TIMEOUT': '90',
            'AGENT2_TIMEOUT': '100'
        }):
            reloaded = self.manager.reload_all_configs()
            
            assert len(reloaded) == 2
            assert reloaded['agent1'].timeout == 90
            assert reloaded['agent2'].timeout == 100
    
    def test_reload_callback(self):
        """
        Test reload callbacks are triggered.
        
        Requirements: 12.6 - Hot reload support
        """
        callback_called = []
        
        def callback(config):
            callback_called.append(config)
        
        # Register callback
        self.manager.register_reload_callback('test_agent', callback)
        
        # Load and reload config
        with patch.dict(os.environ, {'TEST_AGENT_TIMEOUT': '60'}):
            self.manager.load_config('test_agent')
        
        with patch.dict(os.environ, {'TEST_AGENT_TIMEOUT': '90'}):
            self.manager.reload_config('test_agent')
        
        # Callback should have been called
        assert len(callback_called) == 1
        assert callback_called[0].timeout == 90
    
    def test_get_config(self):
        """Test retrieving cached configuration."""
        with patch.dict(os.environ, {'TEST_AGENT_TIMEOUT': '60'}):
            self.manager.load_config('test_agent')
            
            config = self.manager.get_config('test_agent')
            assert config is not None
            assert config.agent_name == 'test_agent'
    
    def test_get_config_not_loaded(self):
        """Test retrieving non-existent configuration."""
        config = self.manager.get_config('nonexistent')
        assert config is None
    
    def test_get_all_configs(self):
        """Test retrieving all configurations."""
        with patch.dict(os.environ, {}):
            self.manager.load_config('agent1')
            self.manager.load_config('agent2')
            
            all_configs = self.manager.get_all_configs()
            assert len(all_configs) == 2
            assert 'agent1' in all_configs
            assert 'agent2' in all_configs
    
    def test_clear_cache(self):
        """Test clearing configuration cache."""
        with patch.dict(os.environ, {}):
            self.manager.load_config('test_agent')
            assert self.manager.get_config('test_agent') is not None
            
            self.manager.clear_cache()
            assert self.manager.get_config('test_agent') is None
    
    def test_export_config(self):
        """Test exporting configuration as dictionary."""
        with patch.dict(os.environ, {'TEST_AGENT_TIMEOUT': '60'}):
            self.manager.load_config('test_agent')
            
            exported = self.manager.export_config('test_agent')
            assert exported is not None
            assert exported['agent_name'] == 'test_agent'
            assert exported['timeout'] == 60
            assert 'search_config' in exported
            assert 'circuit_config' in exported
    
    def test_get_config_summary(self):
        """Test getting configuration summary."""
        with patch.dict(os.environ, {}):
            self.manager.load_config('agent1')
            self.manager.load_config('agent2')
            
            summary = self.manager.get_config_summary()
            assert summary['total_configs'] == 2
            assert 'agent1' in summary['agent_names']
            assert 'agent2' in summary['agent_names']
    
    def test_get_last_reload_time(self):
        """Test tracking last reload time."""
        # Initially None
        assert self.manager.get_last_reload_time() is None
        
        # After reload, should have timestamp
        with patch.dict(os.environ, {'TEST_AGENT_TIMEOUT': '60'}):
            self.manager.load_config('test_agent')
            self.manager.reload_config('test_agent')
            
            last_reload = self.manager.get_last_reload_time()
            assert last_reload is not None


class TestGlobalConfigurationManager:
    """Test global configuration manager instance."""
    
    def test_get_config_manager_singleton(self):
        """Test that get_config_manager returns singleton instance."""
        manager1 = get_config_manager()
        manager2 = get_config_manager()
        
        assert manager1 is manager2
    
    def test_load_agent_config_function(self):
        """Test convenience function for loading config."""
        with patch.dict(os.environ, {'TEST_AGENT_TIMEOUT': '60'}):
            config = load_agent_config('test_agent')
            
            assert config.agent_name == 'test_agent'
            assert config.timeout == 60
    
    def test_reload_agent_config_function(self):
        """Test convenience function for reloading config."""
        with patch.dict(os.environ, {'TEST_AGENT_TIMEOUT': '60'}):
            load_agent_config('test_agent')
        
        with patch.dict(os.environ, {'TEST_AGENT_TIMEOUT': '90'}):
            config = reload_agent_config('test_agent')
            
            assert config.timeout == 90


class TestConfigurationIntegration:
    """Integration tests for configuration management."""
    
    def test_configuration_validation_on_load(self):
        """
        Test that configuration is validated on load.
        
        Requirements: 12.7 - Validate all configuration values on load
        """
        manager = ConfigurationManager()
        
        # Valid configuration should load successfully
        with patch.dict(os.environ, {
            'TEST_AGENT_TIMEOUT': '60',
            'TEST_AGENT_MAX_RETRIES': '3'
        }):
            config = manager.load_config('test_agent')
            assert manager.validate_config(config) is True
    
    def test_default_values_used(self):
        """
        Test that default values are provided.
        
        Requirements: 12.8 - Provide default values for all parameters
        """
        manager = ConfigurationManager()
        
        with patch.dict(os.environ, {}, clear=True):
            config = manager.load_config('test_agent')
            
            # All parameters should have default values
            assert config.timeout > 0
            assert config.max_retries >= 0
            assert config.cache_ttl >= 0
            assert config.search_config is not None
            assert config.circuit_config is not None
    
    def test_hot_reload_without_restart(self):
        """
        Test that configuration changes apply without restart.
        
        Requirements: 12.6 - Apply changes without requiring restart
        """
        manager = ConfigurationManager()
        
        # Load initial config
        with patch.dict(os.environ, {
            'TEST_AGENT_TIMEOUT': '60',
            'SEARCH_RATE_LIMIT': '10'
        }):
            config1 = manager.load_config('test_agent')
            assert config1.timeout == 60
            assert config1.search_config.rate_limit == 10
        
        # Change environment and hot reload
        with patch.dict(os.environ, {
            'TEST_AGENT_TIMEOUT': '90',
            'SEARCH_RATE_LIMIT': '20'
        }):
            config2 = manager.reload_config('test_agent')
            
            # New values should be applied
            assert config2.timeout == 90
            assert config2.search_config.rate_limit == 20
            
            # Cached config should be updated
            cached = manager.get_config('test_agent')
            assert cached.timeout == 90


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
