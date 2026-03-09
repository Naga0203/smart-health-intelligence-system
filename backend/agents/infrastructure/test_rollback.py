"""
Tests for rollback procedures.

Requirements: 19.5 - Test rollback procedures
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from .rollback import (
    RollbackValidator,
    RollbackExecutor,
    RollbackPlan,
    get_rollback_executor,
    emergency_rollback
)
from .feature_flags import AgentImplementation


class TestRollbackValidator:
    """Test rollback safety validation."""
    
    def test_validate_rollback_safety_all_checks_pass(self):
        """Test validation when all checks pass."""
        validator = RollbackValidator()
        
        result = validator.validate_rollback_safety('data_extraction')
        
        assert 'safe' in result
        assert 'checks' in result
        assert 'warnings' in result
        assert result['checks']['agent_exists']
    
    def test_validate_rollback_safety_agent_not_exists(self):
        """Test validation when agent doesn't exist."""
        validator = RollbackValidator()
        
        result = validator.validate_rollback_safety('nonexistent_agent')
        
        assert not result['safe']
        assert not result['checks']['agent_exists']
    
    def test_validate_rollback_safety_already_old(self):
        """Test validation when agent is already on old version."""
        validator = RollbackValidator()
        validator.flags.set_agent_version('data_extraction', AgentImplementation.OLD)
        
        result = validator.validate_rollback_safety('data_extraction')
        
        assert not result['checks']['not_already_old']
    
    def test_check_dependencies_orchestrator(self):
        """Test dependency checking for orchestrator."""
        validator = RollbackValidator()
        
        # Set another agent to new version
        validator.flags.set_agent_version('data_extraction', AgentImplementation.NEW)
        
        # Orchestrator rollback should fail dependency check
        result = validator._check_dependencies('orchestrator')
        
        assert not result


class TestRollbackExecutor:
    """Test rollback execution."""
    
    def test_create_rollback_plan(self):
        """Test rollback plan creation."""
        executor = RollbackExecutor()
        
        plan = executor.create_rollback_plan('data_extraction', 'Test rollback')
        
        assert isinstance(plan, RollbackPlan)
        assert plan.agent_name == 'data_extraction'
        assert plan.reason == 'Test rollback'
        assert plan.target_version == AgentImplementation.OLD.value
        assert len(plan.steps) > 0
    
    def test_create_rollback_plan_safety_checks(self):
        """Test that rollback plan includes safety checks."""
        executor = RollbackExecutor()
        
        plan = executor.create_rollback_plan('data_extraction', 'Test rollback')
        
        assert 'checks_passed' in plan.__dict__
        assert 'check_results' in plan.__dict__
    
    @patch('backend.agents.infrastructure.rollback.get_migration_tracker')
    def test_execute_rollback_success(self, mock_tracker):
        """Test successful rollback execution."""
        executor = RollbackExecutor()
        
        # Set agent to new version first
        executor.flags.set_agent_version('data_extraction', AgentImplementation.NEW)
        
        # Mock tracker
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        
        result = executor.execute_rollback('data_extraction', 'Test rollback')
        
        assert result['success']
        assert result['agent_name'] == 'data_extraction'
        assert result['reason'] == 'Test rollback'
        
        # Verify agent was rolled back
        assert executor.flags.get_agent_version('data_extraction') == AgentImplementation.OLD
    
    def test_execute_rollback_safety_checks_fail(self):
        """Test rollback when safety checks fail."""
        executor = RollbackExecutor()
        
        # Set agent to old version (already rolled back)
        executor.flags.set_agent_version('data_extraction', AgentImplementation.OLD)
        
        result = executor.execute_rollback('data_extraction', 'Test rollback')
        
        assert not result['success']
        assert 'error' in result
    
    @patch('backend.agents.infrastructure.rollback.get_migration_tracker')
    def test_rollback_all_agents(self, mock_tracker):
        """Test rolling back all agents."""
        executor = RollbackExecutor()
        
        # Set some agents to new version
        executor.flags.set_agent_version('data_extraction', AgentImplementation.NEW)
        executor.flags.set_agent_version('explanation', AgentImplementation.NEW)
        
        # Mock tracker
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        
        result = executor.rollback_all_agents('Emergency rollback')
        
        assert 'results' in result
        assert 'total_agents' in result
        assert 'successful_rollbacks' in result
        assert result['total_agents'] == len(executor.flags.AGENT_FLAGS)


class TestRollbackIntegration:
    """Integration tests for rollback procedures."""
    
    @patch('backend.agents.infrastructure.rollback.get_migration_tracker')
    def test_full_rollback_workflow(self, mock_tracker):
        """Test complete rollback workflow."""
        # Mock tracker
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        
        # 1. Start with agent on new version
        executor = get_rollback_executor()
        executor.flags.set_agent_version('data_extraction', AgentImplementation.NEW)
        
        # 2. Create rollback plan
        plan = executor.create_rollback_plan('data_extraction', 'Test workflow')
        assert plan.checks_passed
        
        # 3. Execute rollback
        result = executor.execute_rollback('data_extraction', 'Test workflow')
        assert result['success']
        
        # 4. Verify rollback
        assert executor.flags.get_agent_version('data_extraction') == AgentImplementation.OLD
    
    @patch('backend.agents.infrastructure.rollback.get_migration_tracker')
    def test_emergency_rollback_function(self, mock_tracker):
        """Test emergency rollback convenience function."""
        # Mock tracker
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        
        result = emergency_rollback('Test emergency')
        
        assert 'results' in result
        assert 'reason' in result
        assert result['reason'] == 'Test emergency'


class TestRollbackValidation:
    """Test rollback validation procedures."""
    
    def test_rollback_plan_to_dict(self):
        """Test rollback plan serialization."""
        plan = RollbackPlan(
            agent_name='test_agent',
            current_version='new',
            target_version='old',
            reason='Test',
            checks_passed=True,
            check_results={'test': True},
            steps=['Step 1', 'Step 2'],
            validation_required=True
        )
        
        plan_dict = plan.to_dict()
        
        assert plan_dict['agent_name'] == 'test_agent'
        assert plan_dict['current_version'] == 'new'
        assert plan_dict['target_version'] == 'old'
        assert plan_dict['checks_passed']
        assert len(plan_dict['steps']) == 2


class TestRollbackScenarios:
    """Test specific rollback scenarios."""
    
    @patch('backend.agents.infrastructure.rollback.get_migration_tracker')
    def test_rollback_from_ab_testing(self, mock_tracker):
        """Test rollback from A/B testing mode."""
        executor = RollbackExecutor()
        
        # Mock tracker
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        
        # Set agent to A/B testing
        executor.flags.set_agent_version('data_extraction', AgentImplementation.BOTH)
        
        # Rollback
        result = executor.execute_rollback('data_extraction', 'A/B test failed')
        
        assert result['success']
        assert executor.flags.get_agent_version('data_extraction') == AgentImplementation.OLD
    
    @patch('backend.agents.infrastructure.rollback.get_migration_tracker')
    def test_rollback_with_monitoring_disabled(self, mock_tracker):
        """Test rollback when monitoring is disabled."""
        executor = RollbackExecutor()
        
        # Mock tracker
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        
        # Disable monitoring
        executor.flags.disable_feature('monitoring_enabled')
        
        # Set agent to new version
        executor.flags.set_agent_version('data_extraction', AgentImplementation.NEW)
        
        # Create plan (should have warning)
        plan = executor.create_rollback_plan('data_extraction', 'Test')
        
        # Should still be able to rollback
        assert plan.checks_passed
        
        # Execute rollback
        result = executor.execute_rollback('data_extraction', 'Test')
        assert result['success']


# Property-based tests
class TestRollbackProperties:
    """Property-based tests for rollback procedures."""
    
    @patch('backend.agents.infrastructure.rollback.get_migration_tracker')
    def test_property_rollback_always_sets_old_version(self, mock_tracker):
        """
        Property: Rollback always sets agent to OLD version.
        
        For any agent and any starting version, rollback should result in OLD version.
        """
        executor = RollbackExecutor()
        
        # Mock tracker
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        
        for agent_name in executor.flags.AGENT_FLAGS.keys():
            # Try from NEW version
            executor.flags.set_agent_version(agent_name, AgentImplementation.NEW)
            result = executor.execute_rollback(agent_name, 'Property test')
            
            if result['success']:
                assert executor.flags.get_agent_version(agent_name) == AgentImplementation.OLD
            
            # Try from BOTH version
            executor.flags.set_agent_version(agent_name, AgentImplementation.BOTH)
            result = executor.execute_rollback(agent_name, 'Property test')
            
            if result['success']:
                assert executor.flags.get_agent_version(agent_name) == AgentImplementation.OLD
    
    @patch('backend.agents.infrastructure.rollback.get_migration_tracker')
    def test_property_rollback_is_idempotent(self, mock_tracker):
        """
        Property: Rollback is idempotent.
        
        Rolling back multiple times should have the same effect as rolling back once.
        """
        executor = RollbackExecutor()
        
        # Mock tracker
        mock_tracker_instance = Mock()
        mock_tracker.return_value = mock_tracker_instance
        
        agent_name = 'data_extraction'
        
        # Set to new version
        executor.flags.set_agent_version(agent_name, AgentImplementation.NEW)
        
        # First rollback
        result1 = executor.execute_rollback(agent_name, 'Test 1')
        version1 = executor.flags.get_agent_version(agent_name)
        
        # Second rollback (should fail safety checks but not change version)
        result2 = executor.execute_rollback(agent_name, 'Test 2')
        version2 = executor.flags.get_agent_version(agent_name)
        
        # Version should be the same
        assert version1 == version2 == AgentImplementation.OLD


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
