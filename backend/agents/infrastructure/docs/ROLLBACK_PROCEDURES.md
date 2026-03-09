# Agent Migration Rollback Procedures

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
