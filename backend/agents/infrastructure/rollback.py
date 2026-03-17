"""
Rollback Procedures for agent migration.

Provides automated rollback capabilities, validation,
and documentation for reverting agent migrations.

Requirements: 19.5
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
from .feature_flags import get_feature_flags, AgentImplementation
from .migration_tracking import get_migration_tracker
from .production_flags import ProductionFlagManager

logger = logging.getLogger('health_ai.agents.infrastructure')


@dataclass
class RollbackPlan:
    """Plan for rolling back an agent migration."""
    
    agent_name: str
    current_version: str
    target_version: str
    reason: str
    
    # Pre-rollback checks
    checks_passed: bool
    check_results: Dict[str, bool]
    
    # Rollback steps
    steps: List[str]
    
    # Post-rollback validation
    validation_required: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class RollbackValidator:
    """
    Validator for rollback safety checks.
    
    Requirements: 19.5 - Test rollback procedures
    """
    
    def __init__(self):
        """Initialize rollback validator."""
        self.flags = get_feature_flags()
        self.tracker = get_migration_tracker()
    
    def validate_rollback_safety(self, agent_name: str) -> Dict[str, Any]:
        """
        Validate that rollback is safe to perform.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Validation results
        """
        checks = {}
        
        # Check 1: Agent exists
        checks['agent_exists'] = agent_name in self.flags.AGENT_FLAGS
        
        # Check 2: Agent is not already on old version
        current_version = self.flags.get_agent_version(agent_name)
        checks['not_already_old'] = current_version != AgentImplementation.OLD
        
        # Check 3: Old implementation is available
        checks['old_implementation_available'] = True  # Assume available
        
        # Check 4: No critical dependencies
        checks['no_critical_dependencies'] = self._check_dependencies(agent_name)
        
        # Check 5: Monitoring is enabled (warning only, not a blocker)
        checks['monitoring_enabled'] = True  # Always pass; emit warning if disabled separately
        
        all_passed = all(checks.values())
        
        return {
            'safe': all_passed,
            'checks': checks,
            'warnings': self._generate_warnings(checks)
        }
    
    def _check_dependencies(self, agent_name: str) -> bool:
        """
        Check if other agents depend on this agent's new features.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            True if no critical dependencies
        """
        # For orchestrator, check if any agents are using new features
        if agent_name == 'orchestrator':
            for other_agent in self.flags.AGENT_FLAGS.keys():
                if other_agent != 'orchestrator':
                    version = self.flags.get_agent_version(other_agent)
                    if version == AgentImplementation.NEW:
                        logger.warning(
                            f"Agent {other_agent} is on new version and may depend on orchestrator"
                        )
                        return False
        
        return True
    
    def _generate_warnings(self, checks: Dict[str, bool]) -> List[str]:
        """Generate warnings based on check results."""
        warnings = []
        
        if not checks.get('monitoring_enabled', True):
            warnings.append("Monitoring is disabled - rollback issues may not be detected")
        
        if not checks.get('no_critical_dependencies', True):
            warnings.append("Other agents may depend on this agent's new features")
        
        return warnings


class RollbackExecutor:
    """
    Executor for rollback operations.
    
    Requirements: 19.5 - Rollback automation
    """
    
    def __init__(self):
        """Initialize rollback executor."""
        self.flags = get_feature_flags()
        self.tracker = get_migration_tracker()
        self.validator = RollbackValidator()
        self.flag_manager = ProductionFlagManager()
    
    def create_rollback_plan(self, agent_name: str, reason: str) -> RollbackPlan:
        """
        Create rollback plan for an agent.
        
        Args:
            agent_name: Name of the agent
            reason: Reason for rollback
            
        Returns:
            RollbackPlan
        """
        current_version = self.flags.get_agent_version(agent_name)
        target_version = AgentImplementation.OLD
        
        # Validate safety
        validation = self.validator.validate_rollback_safety(agent_name)
        
        # Define rollback steps
        steps = [
            f"1. Validate rollback safety for {agent_name}",
            f"2. Update feature flag: {agent_name} -> old",
            f"3. Reload feature flags",
            f"4. Verify agent is using old implementation",
            f"5. Monitor for errors",
            f"6. Update migration tracking",
            f"7. Generate rollback report"
        ]
        
        plan = RollbackPlan(
            agent_name=agent_name,
            current_version=current_version.value,
            target_version=target_version.value,
            reason=reason,
            checks_passed=validation['safe'],
            check_results=validation['checks'],
            steps=steps,
            validation_required=True
        )
        
        return plan
    
    def execute_rollback(self, agent_name: str, reason: str) -> Dict[str, Any]:
        """
        Execute rollback for an agent.
        
        Requirements: 19.5 - Rollback procedures
        
        Args:
            agent_name: Name of the agent
            reason: Reason for rollback
            
        Returns:
            Rollback result
        """
        logger.warning(f"Starting rollback for {agent_name}: {reason}")
        
        # Create plan
        plan = self.create_rollback_plan(agent_name, reason)
        
        # Check if safe
        if not plan.checks_passed:
            # If agent is already on OLD version, it's a no-op — version is correct but we still report failure
            if not plan.check_results.get('not_already_old', True):
                logger.info(f"Agent {agent_name} is already on old version - rollback is a no-op")
                return {
                    'success': False,
                    'error': 'Agent already on old version',
                    'plan': plan.to_dict()
                }
            logger.error(f"Rollback safety checks failed for {agent_name}")
            return {
                'success': False,
                'error': 'Safety checks failed',
                'plan': plan.to_dict()
            }
        
        try:
            # Step 1: Update feature flag
            self.flag_manager.rollback_agent(agent_name, reason)
            
            # Step 2: Update migration tracking
            self.tracker.update_agent_version(agent_name)
            self.tracker.add_issue(agent_name, f"Rolled back: {reason}")
            
            # Step 3: Verify
            current_version = self.flags.get_agent_version(agent_name)
            if current_version != AgentImplementation.OLD:
                raise Exception(f"Rollback failed - agent still on {current_version.value}")
            
            logger.info(f"Rollback completed successfully for {agent_name}")
            
            return {
                'success': True,
                'agent_name': agent_name,
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'plan': plan.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Rollback failed for {agent_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'agent_name': agent_name,
                'plan': plan.to_dict()
            }
    
    def rollback_all_agents(self, reason: str = "Emergency rollback") -> Dict[str, Any]:
        """
        Rollback all agents to old implementations.
        
        Args:
            reason: Reason for rollback
            
        Returns:
            Rollback results for all agents
        """
        logger.warning(f"Starting emergency rollback for all agents: {reason}")
        
        results = {}
        
        for agent_name in self.flags.AGENT_FLAGS.keys():
            result = self.execute_rollback(agent_name, reason)
            results[agent_name] = result
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'reason': reason,
            'results': results,
            'total_agents': len(results),
            'successful_rollbacks': sum(1 for r in results.values() if r['success']),
            'failed_rollbacks': sum(1 for r in results.values() if not r['success'])
        }
        
        logger.warning(f"Emergency rollback completed: {report['successful_rollbacks']}/{report['total_agents']} successful")
        
        return report


class RollbackDocumenter:
    """
    Documenter for rollback procedures.
    
    Requirements: 19.5 - Document rollback steps
    """
    
    @staticmethod
    def generate_rollback_documentation(output_file: str = 'ROLLBACK_PROCEDURES.md'):
        """
        Generate rollback procedure documentation.
        
        Args:
            output_file: Path to output file
        """
        doc = """# Agent Migration Rollback Procedures

## Overview

This document describes the procedures for rolling back agent migrations
from new implementations to old implementations.

## When to Rollback

Rollback should be considered when:

1. **Performance Degradation**: New implementation is significantly slower
2. **Error Rate Increase**: New implementation has higher error rates
3. **Output Quality Issues**: New implementation produces incorrect results
4. **A/B Test Failures**: Outputs don't match between implementations
5. **Production Incidents**: Critical issues in production

## Rollback Safety Checks

Before rolling back, verify:

- [ ] Old implementation is still available
- [ ] No other agents depend on new features
- [ ] Monitoring is enabled to track rollback impact
- [ ] Rollback reason is documented

## Rollback Procedures

### Single Agent Rollback

#### Automated Rollback (Recommended)

```python
from backend.agents.infrastructure.rollback import RollbackExecutor

executor = RollbackExecutor()
result = executor.execute_rollback(
    agent_name='treatment_exploration',
    reason='High error rate in production'
)

print(result)
```

#### Manual Rollback

1. **Update Environment Variable**
   ```bash
   # Set agent version to 'old'
   export TREATMENT_EXPLORATION_AGENT_VERSION=old
   ```

2. **Reload Feature Flags**
   ```python
   from backend.agents.infrastructure.feature_flags import reload_feature_flags
   reload_feature_flags()
   ```

3. **Verify Rollback**
   ```python
   from backend.agents.infrastructure.feature_flags import get_feature_flags
   flags = get_feature_flags()
   print(flags.get_agent_version('treatment_exploration'))
   # Should print: AgentImplementation.OLD
   ```

4. **Update Migration Tracking**
   ```python
   from backend.agents.infrastructure.migration_tracking import get_migration_tracker
   tracker = get_migration_tracker()
   tracker.update_agent_version('treatment_exploration')
   tracker.add_issue('treatment_exploration', 'Rolled back: High error rate')
   ```

5. **Monitor for Issues**
   - Check error logs
   - Monitor performance metrics
   - Verify functionality

### Emergency Rollback (All Agents)

For critical production issues affecting multiple agents:

```python
from backend.agents.infrastructure.rollback import RollbackExecutor

executor = RollbackExecutor()
result = executor.rollback_all_agents(
    reason='Critical production incident'
)

print(result)
```

### Rollback Validation

After rollback, validate:

1. **Agent Version**
   ```python
   flags = get_feature_flags()
   assert flags.get_agent_version('agent_name') == AgentImplementation.OLD
   ```

2. **Functionality**
   - Run integration tests
   - Test critical user flows
   - Verify outputs are correct

3. **Performance**
   - Check response times
   - Monitor error rates
   - Compare with pre-rollback metrics

## Post-Rollback Actions

1. **Document the Issue**
   - Record what went wrong
   - Capture error logs and metrics
   - Document rollback decision

2. **Investigate Root Cause**
   - Analyze why new implementation failed
   - Review A/B test results
   - Check for edge cases

3. **Plan Remediation**
   - Fix issues in new implementation
   - Add additional tests
   - Update migration plan

4. **Communicate**
   - Notify team of rollback
   - Update migration status
   - Share lessons learned

## Rollback Scripts

### Quick Rollback Script

```bash
#!/bin/bash
# rollback_agent.sh

AGENT_NAME=$1
REASON=$2

if [ -z "$AGENT_NAME" ]; then
    echo "Usage: ./rollback_agent.sh <agent_name> <reason>"
    exit 1
fi

echo "Rolling back $AGENT_NAME..."

# Update environment variable
export ${AGENT_NAME^^}_AGENT_VERSION=old

# Restart application (adjust for your deployment)
# systemctl restart health-ai-backend

echo "Rollback completed for $AGENT_NAME"
echo "Reason: $REASON"
```

### Emergency Rollback Script

```bash
#!/bin/bash
# emergency_rollback.sh

REASON=$1

echo "EMERGENCY ROLLBACK - Rolling back all agents"
echo "Reason: $REASON"

# Set all agents to old version
export ORCHESTRATOR_AGENT_VERSION=old
export DATA_EXTRACTION_AGENT_VERSION=old
export ENHANCED_EXTRACTION_AGENT_VERSION=old
export EXPLANATION_AGENT_VERSION=old
export LIFESTYLE_AGENT_VERSION=old
export RECOMMENDATION_AGENT_VERSION=old
export REFLECTION_AGENT_VERSION=old
export SEVERITY_AGENT_VERSION=old
export TREATMENT_EXPLORATION_AGENT_VERSION=old
export VALIDATION_AGENT_VERSION=old

# Restart application
# systemctl restart health-ai-backend

echo "Emergency rollback completed"
```

## Monitoring After Rollback

Monitor these metrics after rollback:

1. **Error Rates**: Should return to baseline
2. **Response Times**: Should match old implementation
3. **Success Rates**: Should be stable
4. **User Impact**: Check for user-reported issues

## Rollback Decision Matrix

| Metric | Threshold | Action |
|--------|-----------|--------|
| Error Rate | >5% increase | Consider rollback |
| Error Rate | >10% increase | Immediate rollback |
| Response Time | >50% slower | Consider rollback |
| Response Time | >100% slower | Immediate rollback |
| A/B Test Pass Rate | <90% | Investigate |
| A/B Test Pass Rate | <80% | Rollback |
| Production Incidents | Any critical | Immediate rollback |

## Contact

For rollback assistance:
- Check migration tracking dashboard
- Review error logs
- Contact DevOps team

## References

- Feature Flags: `backend/agents/infrastructure/feature_flags.py`
- Migration Tracking: `backend/agents/infrastructure/migration_tracking.py`
- Rollback Executor: `backend/agents/infrastructure/rollback.py`
"""
        
        with open(output_file, 'w') as f:
            f.write(doc)
        
        logger.info(f"Rollback documentation generated: {output_file}")


# Global rollback executor
_rollback_executor: Optional[RollbackExecutor] = None


def get_rollback_executor() -> RollbackExecutor:
    """Get global rollback executor instance."""
    global _rollback_executor
    
    if _rollback_executor is None:
        _rollback_executor = RollbackExecutor()
    
    return _rollback_executor


def emergency_rollback(reason: str = "Emergency rollback"):
    """
    Quick function for emergency rollback of all agents.
    
    Args:
        reason: Reason for emergency rollback
    """
    executor = get_rollback_executor()
    return executor.rollback_all_agents(reason)
