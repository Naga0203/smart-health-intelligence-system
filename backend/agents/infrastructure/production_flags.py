"""
Production feature flag configuration and management.

This module provides production-ready feature flag configuration,
flag switching procedures, and deployment utilities.

Requirements: 19.1, 19.2
"""

import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
from .feature_flags import FeatureFlags, AgentImplementation, get_feature_flags

logger = logging.getLogger('health_ai.agents.infrastructure')


class ProductionFlagManager:
    """
    Manager for production feature flag configuration.
    
    Requirements:
    - 19.1: Support running old and new implementations side-by-side
    - 19.2: Feature flags to enable/disable new implementations
    """
    
    # Production-safe default configuration
    # All agents start with OLD implementation for safety
    PRODUCTION_DEFAULTS = {
        'orchestrator': AgentImplementation.OLD,
        'data_extraction': AgentImplementation.OLD,
        'enhanced_extraction': AgentImplementation.OLD,
        'explanation': AgentImplementation.OLD,
        'lifestyle': AgentImplementation.OLD,
        'recommendation': AgentImplementation.OLD,
        'reflection': AgentImplementation.OLD,
        'severity': AgentImplementation.OLD,
        'treatment_exploration': AgentImplementation.OLD,
        'validation': AgentImplementation.OLD
    }
    
    def __init__(self):
        """Initialize production flag manager."""
        self.flags = get_feature_flags()
        self.change_log: list = []
        
    def get_production_config(self) -> Dict[str, str]:
        """
        Get production-safe feature flag configuration.
        
        Returns environment variable configuration that can be
        used in production deployment.
        
        Returns:
            Dictionary of environment variables
        """
        config = {}
        
        # Agent version flags
        for agent_name, default_version in self.PRODUCTION_DEFAULTS.items():
            env_var = FeatureFlags.AGENT_FLAGS[agent_name]
            current_version = self.flags.get_agent_version(agent_name)
            config[env_var] = current_version.value
            
        # Feature flags - conservative defaults for production
        config['WEB_SEARCH_ENABLED'] = 'false'
        config['DYNAMIC_TREATMENT_ENABLED'] = 'false'
        config['GEMINI_OCR_ENABLED'] = 'false'
        config['MONITORING_ENABLED'] = 'true'
        config['SAFETY_GUARDRAILS_ENABLED'] = 'true'
        
        return config
    
    def generate_env_file(self, output_path: str = '.env.production'):
        """
        Generate .env file for production deployment.
        
        Args:
            output_path: Path to output .env file
        """
        config = self.get_production_config()
        
        with open(output_path, 'w') as f:
            f.write("# Production Feature Flags Configuration\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write("# DO NOT EDIT MANUALLY - Use ProductionFlagManager\n\n")
            
            f.write("# Agent Version Flags\n")
            for agent_name in self.PRODUCTION_DEFAULTS.keys():
                env_var = FeatureFlags.AGENT_FLAGS[agent_name]
                value = config[env_var]
                f.write(f"{env_var}={value}\n")
            
            f.write("\n# Feature Flags\n")
            f.write(f"WEB_SEARCH_ENABLED={config['WEB_SEARCH_ENABLED']}\n")
            f.write(f"DYNAMIC_TREATMENT_ENABLED={config['DYNAMIC_TREATMENT_ENABLED']}\n")
            f.write(f"GEMINI_OCR_ENABLED={config['GEMINI_OCR_ENABLED']}\n")
            f.write(f"MONITORING_ENABLED={config['MONITORING_ENABLED']}\n")
            f.write(f"SAFETY_GUARDRAILS_ENABLED={config['SAFETY_GUARDRAILS_ENABLED']}\n")
        
        logger.info(f"Production configuration written to {output_path}")
    
    def switch_agent_to_ab_testing(self, agent_name: str, reason: str = ""):
        """
        Switch agent to A/B testing mode (both implementations).
        
        Args:
            agent_name: Name of the agent
            reason: Reason for the switch
        """
        self.flags.set_agent_version(agent_name, AgentImplementation.BOTH)
        
        change = {
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'action': 'enable_ab_testing',
            'from': 'old',
            'to': 'both',
            'reason': reason
        }
        self.change_log.append(change)
        
        logger.info(f"Agent {agent_name} switched to A/B testing: {reason}")
    
    def switch_agent_to_new(self, agent_name: str, reason: str = ""):
        """
        Switch agent to new implementation only.
        
        Args:
            agent_name: Name of the agent
            reason: Reason for the switch
        """
        current = self.flags.get_agent_version(agent_name)
        self.flags.set_agent_version(agent_name, AgentImplementation.NEW)
        
        change = {
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'action': 'migrate_to_new',
            'from': current.value,
            'to': 'new',
            'reason': reason
        }
        self.change_log.append(change)
        
        logger.info(f"Agent {agent_name} switched to new implementation: {reason}")
    
    def rollback_agent(self, agent_name: str, reason: str = ""):
        """
        Rollback agent to old implementation.
        
        Requirements: 19.5 - Support rollback
        
        Args:
            agent_name: Name of the agent
            reason: Reason for rollback
        """
        current = self.flags.get_agent_version(agent_name)
        self.flags.rollback_agent(agent_name)
        
        change = {
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'action': 'rollback',
            'from': current.value,
            'to': 'old',
            'reason': reason
        }
        self.change_log.append(change)
        
        logger.warning(f"Agent {agent_name} rolled back: {reason}")
    
    def get_change_log(self) -> list:
        """
        Get log of all flag changes.
        
        Returns:
            List of change records
        """
        return self.change_log
    
    def validate_production_safety(self) -> Dict[str, Any]:
        """
        Validate that production configuration is safe.
        
        Checks:
        - Safety guardrails are enabled
        - Monitoring is enabled
        - No agents in invalid states
        
        Returns:
            Validation result with warnings
        """
        warnings = []
        errors = []
        
        # Check safety guardrails
        if not self.flags.is_safety_guardrails_enabled():
            errors.append("Safety guardrails are DISABLED - this is unsafe for production")
        
        # Check monitoring
        if not self.flags.is_monitoring_enabled():
            warnings.append("Monitoring is disabled - observability will be limited")
        
        # Check agent states
        for agent_name in self.PRODUCTION_DEFAULTS.keys():
            version = self.flags.get_agent_version(agent_name)
            if version == AgentImplementation.BOTH:
                warnings.append(f"Agent {agent_name} is in A/B testing mode - ensure comparison logging is active")
        
        return {
            'safe': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'timestamp': datetime.now().isoformat()
        }


def create_production_config():
    """Create production feature flag configuration file."""
    manager = ProductionFlagManager()
    manager.generate_env_file('.env.production')
    
    # Validate safety
    validation = manager.validate_production_safety()
    
    if not validation['safe']:
        logger.error("Production configuration is UNSAFE:")
        for error in validation['errors']:
            logger.error(f"  - {error}")
    
    if validation['warnings']:
        logger.warning("Production configuration warnings:")
        for warning in validation['warnings']:
            logger.warning(f"  - {warning}")
    
    return validation


if __name__ == '__main__':
    # Generate production configuration
    create_production_config()
