"""
Feature Flags for gradual agent migration rollout.

Enables switching between old and new agent implementations,
web search enablement, and dynamic treatment retrieval.

Requirements: 19.1, 19.2
"""

import logging
import os
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger('health_ai.agents.infrastructure')


class AgentImplementation(Enum):
    """Agent implementation versions."""
    OLD = "old"
    NEW = "new"
    BOTH = "both"  # Run both for A/B testing


class FeatureFlags:
    """
    Feature flag system for agent migration.
    
    Requirements:
    - 19.1: Support running old and new implementations side-by-side
    - 19.2: Feature flags to enable/disable new implementations
    """
    
    # Agent-specific flags
    AGENT_FLAGS = {
        'orchestrator': 'ORCHESTRATOR_AGENT_VERSION',
        'data_extraction': 'DATA_EXTRACTION_AGENT_VERSION',
        'enhanced_extraction': 'ENHANCED_EXTRACTION_AGENT_VERSION',
        'explanation': 'EXPLANATION_AGENT_VERSION',
        'lifestyle': 'LIFESTYLE_AGENT_VERSION',
        'recommendation': 'RECOMMENDATION_AGENT_VERSION',
        'reflection': 'REFLECTION_AGENT_VERSION',
        'severity': 'SEVERITY_AGENT_VERSION',
        'treatment_exploration': 'TREATMENT_EXPLORATION_AGENT_VERSION',
        'validation': 'VALIDATION_AGENT_VERSION'
    }
    
    # Feature flags
    WEB_SEARCH_ENABLED = 'WEB_SEARCH_ENABLED'
    DYNAMIC_TREATMENT_ENABLED = 'DYNAMIC_TREATMENT_ENABLED'
    GEMINI_OCR_ENABLED = 'GEMINI_OCR_ENABLED'
    MONITORING_ENABLED = 'MONITORING_ENABLED'
    SAFETY_GUARDRAILS_ENABLED = 'SAFETY_GUARDRAILS_ENABLED'
    
    def __init__(self):
        """Initialize feature flags from environment."""
        self._flags: Dict[str, Any] = {}
        self._load_from_environment()
        
        logger.info("FeatureFlags initialized")
    
    def _load_from_environment(self):
        """Load feature flags from environment variables."""
        # Load agent version flags
        for agent_name, env_var in self.AGENT_FLAGS.items():
            value = os.getenv(env_var, 'old').lower()
            try:
                self._flags[agent_name] = AgentImplementation(value)
            except ValueError:
                logger.warning(f"Invalid agent version for {agent_name}: {value}, using 'old'")
                self._flags[agent_name] = AgentImplementation.OLD
        
        # Load feature flags
        self._flags['web_search_enabled'] = os.getenv(self.WEB_SEARCH_ENABLED, 'false').lower() == 'true'
        self._flags['dynamic_treatment_enabled'] = os.getenv(self.DYNAMIC_TREATMENT_ENABLED, 'false').lower() == 'true'
        self._flags['gemini_ocr_enabled'] = os.getenv(self.GEMINI_OCR_ENABLED, 'false').lower() == 'true'
        self._flags['monitoring_enabled'] = os.getenv(self.MONITORING_ENABLED, 'true').lower() == 'true'
        self._flags['safety_guardrails_enabled'] = os.getenv(self.SAFETY_GUARDRAILS_ENABLED, 'true').lower() == 'true'
        
        logger.info(f"Feature flags loaded: {self._flags}")
    
    def get_agent_version(self, agent_name: str) -> AgentImplementation:
        """
        Get agent implementation version.
        
        Requirements: 19.1, 19.2 - Feature flags for agent versions
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            AgentImplementation enum value
        """
        return self._flags.get(agent_name, AgentImplementation.OLD)
    
    def use_new_agent(self, agent_name: str) -> bool:
        """
        Check if new agent implementation should be used.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            True if new implementation should be used
        """
        version = self.get_agent_version(agent_name)
        return version in [AgentImplementation.NEW, AgentImplementation.BOTH]
    
    def use_old_agent(self, agent_name: str) -> bool:
        """
        Check if old agent implementation should be used.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            True if old implementation should be used
        """
        version = self.get_agent_version(agent_name)
        return version in [AgentImplementation.OLD, AgentImplementation.BOTH]
    
    def is_ab_testing(self, agent_name: str) -> bool:
        """
        Check if agent is in A/B testing mode (both versions).
        
        Requirements: 19.3 - A/B testing support
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            True if both versions should run
        """
        return self.get_agent_version(agent_name) == AgentImplementation.BOTH
    
    def is_web_search_enabled(self) -> bool:
        """Check if web search is enabled."""
        return self._flags.get('web_search_enabled', False)
    
    def is_dynamic_treatment_enabled(self) -> bool:
        """Check if dynamic treatment retrieval is enabled."""
        return self._flags.get('dynamic_treatment_enabled', False)
    
    def is_gemini_ocr_enabled(self) -> bool:
        """Check if Gemini OCR is enabled."""
        return self._flags.get('gemini_ocr_enabled', False)
    
    def is_monitoring_enabled(self) -> bool:
        """Check if monitoring is enabled."""
        return self._flags.get('monitoring_enabled', True)
    
    def is_safety_guardrails_enabled(self) -> bool:
        """Check if safety guardrails are enabled."""
        return self._flags.get('safety_guardrails_enabled', True)
    
    def set_agent_version(self, agent_name: str, version: AgentImplementation):
        """
        Set agent version (for testing/admin purposes).
        
        Args:
            agent_name: Name of the agent
            version: AgentImplementation version
        """
        self._flags[agent_name] = version
        logger.info(f"Agent {agent_name} version set to {version.value}")
    
    def enable_feature(self, feature_name: str):
        """
        Enable a feature flag.
        
        Args:
            feature_name: Name of the feature
        """
        self._flags[feature_name] = True
        logger.info(f"Feature {feature_name} enabled")
    
    def disable_feature(self, feature_name: str):
        """
        Disable a feature flag.
        
        Args:
            feature_name: Name of the feature
        """
        self._flags[feature_name] = False
        logger.info(f"Feature {feature_name} disabled")
    
    def get_all_flags(self) -> Dict[str, Any]:
        """
        Get all feature flags.
        
        Returns:
            Dictionary of all flags
        """
        return {
            'agents': {
                name: self._flags.get(name, AgentImplementation.OLD).value
                for name in self.AGENT_FLAGS.keys()
            },
            'features': {
                'web_search_enabled': self.is_web_search_enabled(),
                'dynamic_treatment_enabled': self.is_dynamic_treatment_enabled(),
                'gemini_ocr_enabled': self.is_gemini_ocr_enabled(),
                'monitoring_enabled': self.is_monitoring_enabled(),
                'safety_guardrails_enabled': self.is_safety_guardrails_enabled()
            }
        }
    
    def get_migration_status(self) -> Dict[str, Any]:
        """
        Get migration status for all agents.
        
        Requirements: 19.6 - Track migration status
        
        Returns:
            Migration status dictionary
        """
        status = {
            'total_agents': len(self.AGENT_FLAGS),
            'migrated': 0,
            'in_progress': 0,
            'not_started': 0,
            'agents': {}
        }
        
        for agent_name in self.AGENT_FLAGS.keys():
            version = self.get_agent_version(agent_name)
            
            if version == AgentImplementation.NEW:
                status['migrated'] += 1
                agent_status = 'migrated'
            elif version == AgentImplementation.BOTH:
                status['in_progress'] += 1
                agent_status = 'testing'
            else:
                status['not_started'] += 1
                agent_status = 'not_started'
            
            status['agents'][agent_name] = agent_status
        
        return status
    
    def rollback_agent(self, agent_name: str):
        """
        Rollback agent to old implementation.
        
        Requirements: 19.5 - Support rollback
        
        Args:
            agent_name: Name of the agent
        """
        self.set_agent_version(agent_name, AgentImplementation.OLD)
        logger.warning(f"Agent {agent_name} rolled back to old implementation")
    
    def migrate_agent(self, agent_name: str, enable_ab_testing: bool = False):
        """
        Migrate agent to new implementation.
        
        Args:
            agent_name: Name of the agent
            enable_ab_testing: Whether to enable A/B testing first
        """
        if enable_ab_testing:
            self.set_agent_version(agent_name, AgentImplementation.BOTH)
            logger.info(f"Agent {agent_name} migrated with A/B testing enabled")
        else:
            self.set_agent_version(agent_name, AgentImplementation.NEW)
            logger.info(f"Agent {agent_name} migrated to new implementation")


# Global feature flags instance
_feature_flags: Optional[FeatureFlags] = None


def get_feature_flags() -> FeatureFlags:
    """
    Get global feature flags instance.
    
    Returns:
        FeatureFlags instance
    """
    global _feature_flags
    
    if _feature_flags is None:
        _feature_flags = FeatureFlags()
    
    return _feature_flags


def reload_feature_flags():
    """Reload feature flags from environment."""
    global _feature_flags
    _feature_flags = FeatureFlags()
    logger.info("Feature flags reloaded")
