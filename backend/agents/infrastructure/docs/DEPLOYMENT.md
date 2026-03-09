# Deployment Guide

## Overview

This guide documents the deployment process for the autonomous AI agents system, including feature flag usage, gradual rollout strategies, and rollback procedures.

## Deployment Strategy

The system uses a **gradual migration strategy** with feature flags to enable safe, incremental deployment of new agent implementations.

### Migration Phases

1. **Phase 1**: Deploy infrastructure (circuit breakers, monitoring, web search)
2. **Phase 2**: Deploy simple agents (ValidationAgent, ReflectionAgent)
3. **Phase 3**: Deploy extraction agents (DataExtractionAgent, EnhancedExtractionAgent)
4. **Phase 4**: Deploy specialized agents (SeverityAgent, TreatmentExplorationAgent, etc.)
5. **Phase 5**: Deploy orchestrator with autonomous coordination
6. **Phase 6**: Remove old implementations

## Pre-Deployment Checklist

### Infrastructure Requirements

- [ ] Python 3.9+ installed
- [ ] Django 4.2+ installed
- [ ] Redis or Firebase for caching
- [ ] PostgreSQL or Firebase for database
- [ ] Sufficient memory (2GB+ per instance)
- [ ] Sufficient CPU (2+ cores per instance)
- [ ] Network access to external APIs

### API Keys and Credentials

- [ ] Gemini API key obtained and tested
- [ ] Search API key obtained and tested
- [ ] Firebase credentials configured
- [ ] All keys stored securely (vault or environment)
- [ ] Key permissions verified

### Configuration

- [ ] Environment variables configured
- [ ] Configuration file created (.env or config.yaml)
- [ ] Configuration validated
- [ ] Logging configured
- [ ] Monitoring configured

### Testing

- [ ] All unit tests passing
- [ ] All property tests passing
- [ ] Integration tests passing
- [ ] Performance tests passing
- [ ] Safety tests passing
- [ ] Load testing completed

### Monitoring

- [ ] Monitoring dashboards created
- [ ] Alerts configured
- [ ] Log aggregation configured
- [ ] Error tracking configured
- [ ] Cost tracking configured

## Feature Flags

Feature flags control which agent implementations are active.

### Available Feature Flags

```bash
# Infrastructure
FEATURE_WEB_SEARCH=true              # Enable web search capabilities
FEATURE_PARALLEL_EXECUTION=true      # Enable parallel agent execution

# Agent Implementations
FEATURE_NEW_ORCHESTRATOR=true        # Use new orchestrator
FEATURE_NEW_DATA_EXTRACTION=true     # Use new data extraction agent
FEATURE_NEW_ENHANCED_EXTRACTION=true # Use new enhanced extraction agent
FEATURE_NEW_SEVERITY=true            # Use new severity agent
FEATURE_NEW_TREATMENT_EXPLORATION=true # Use new treatment exploration agent
FEATURE_NEW_RECOMMENDATION=true      # Use new recommendation agent
FEATURE_NEW_LIFESTYLE=true           # Use new lifestyle agent
FEATURE_NEW_EXPLANATION=true         # Use new explanation agent
FEATURE_NEW_VALIDATION=true          # Use new validation agent
FEATURE_NEW_REFLECTION=true          # Use new reflection agent

# Data Sources
FEATURE_DYNAMIC_TREATMENT=true       # Use dynamic treatment retrieval
```

### Feature Flag Management

```bash
# View current feature flags
python manage.py show_feature_flags

# Enable feature flag
python manage.py enable_feature FEATURE_NEW_DATA_EXTRACTION

# Disable feature flag
python manage.py disable_feature FEATURE_NEW_DATA_EXTRACTION

# Toggle feature flag
python manage.py toggle_feature FEATURE_NEW_DATA_EXTRACTION

# Set feature flag percentage (gradual rollout)
python manage.py set_feature_percentage FEATURE_NEW_DATA_EXTRACTION 25
```

## Deployment Environments

### Development Environment

**Purpose**: Local development and testing

**Configuration**:
```bash
# .env.development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
LOG_FORMAT=text

# Use faster model for development
GEMINI_MODEL=gemini-1.5-flash

# Shorter timeouts
AGENT_TIMEOUT=15
ORCHESTRATOR_TIMEOUT=60

# Disable monitoring overhead
MONITORING_ENABLED=false

# All feature flags enabled
FEATURE_NEW_ORCHESTRATOR=true
FEATURE_NEW_DATA_EXTRACTION=true
# ... all other flags true
```

**Deployment**:
```bash
# Load development configuration
export $(cat .env.development | xargs)

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

### Staging Environment

**Purpose**: Pre-production testing and validation

**Configuration**:
```bash
# .env.staging
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json

# Production-like settings
GEMINI_MODEL=gemini-1.5-pro
AGENT_TIMEOUT=30
ORCHESTRATOR_TIMEOUT=120

# Enable monitoring
MONITORING_ENABLED=true
MONITORING_SAMPLE_RATE=100

# Gradual feature rollout
FEATURE_NEW_ORCHESTRATOR=true
FEATURE_NEW_DATA_EXTRACTION=true
# ... enable features being tested
```

**Deployment**:
```bash
# Load staging configuration
export $(cat .env.staging | xargs)

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start with gunicorn
gunicorn backend.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120
```

### Production Environment

**Purpose**: Live production system

**Configuration**:
```bash
# .env.production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_SANITIZE_PII=true

# Production settings
GEMINI_MODEL=gemini-1.5-pro
AGENT_TIMEOUT=45
ORCHESTRATOR_TIMEOUT=180

# Full monitoring
MONITORING_ENABLED=true
MONITORING_SAMPLE_RATE=100

# Alerts
ALERT_ERROR_RATE_THRESHOLD=5
ALERT_RESPONSE_TIME_THRESHOLD=30

# Feature flags (gradual rollout)
FEATURE_NEW_ORCHESTRATOR=true
FEATURE_NEW_DATA_EXTRACTION=true
# ... enable features gradually
```

**Deployment**:
```bash
# Load production configuration
export $(cat .env.production | xargs)

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start with gunicorn
gunicorn backend.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 8 \
  --timeout 180 \
  --max-requests 1000 \
  --max-requests-jitter 100
```

## Gradual Rollout Process

### Step 1: Deploy Infrastructure

**Goal**: Deploy shared infrastructure without changing agent behavior

**Actions**:
1. Deploy new code with all agent feature flags OFF
2. Verify infrastructure components:
   - Circuit breakers
   - Monitoring service
   - Web search tool
   - Context manager
   - Safety guardrails

**Verification**:
```bash
# Test infrastructure
python manage.py test_infrastructure

# Verify no behavior changes
python manage.py compare_outputs --before --after
```

**Rollback**: Revert deployment if infrastructure issues detected

### Step 2: Deploy Simple Agents (10% Traffic)

**Goal**: Validate simple agents with low risk

**Agents**: ValidationAgent, ReflectionAgent

**Actions**:
```bash
# Enable for 10% of traffic
python manage.py set_feature_percentage FEATURE_NEW_VALIDATION 10
python manage.py set_feature_percentage FEATURE_NEW_REFLECTION 10
```

**Monitoring**:
- Error rate: Should remain < 5%
- Response time: Should not increase significantly
- Output quality: Compare old vs new outputs

**Duration**: 24-48 hours

**Decision**:
- ✅ Success: Increase to 50%
- ❌ Issues: Rollback and investigate

### Step 3: Increase Simple Agents (50% Traffic)

**Actions**:
```bash
# Increase to 50% of traffic
python manage.py set_feature_percentage FEATURE_NEW_VALIDATION 50
python manage.py set_feature_percentage FEATURE_NEW_REFLECTION 50
```

**Duration**: 48-72 hours

**Decision**:
- ✅ Success: Increase to 100%
- ❌ Issues: Rollback to 10% or 0%

### Step 4: Full Rollout Simple Agents (100% Traffic)

**Actions**:
```bash
# Enable for all traffic
python manage.py enable_feature FEATURE_NEW_VALIDATION
python manage.py enable_feature FEATURE_NEW_REFLECTION
```

**Duration**: 1 week

**Decision**:
- ✅ Success: Proceed to extraction agents
- ❌ Issues: Rollback

### Step 5: Deploy Extraction Agents (10% → 50% → 100%)

**Agents**: DataExtractionAgent, EnhancedExtractionAgent

**Process**: Same as steps 2-4

**Special Considerations**:
- OCR changes may affect downstream agents
- Monitor extraction confidence scores
- Compare structured data quality

### Step 6: Deploy Specialized Agents (10% → 50% → 100%)

**Agents**: SeverityAgent, TreatmentExplorationAgent, RecommendationAgent, LifestyleAgent, ExplanationAgent

**Process**: Same as steps 2-4

**Special Considerations**:
- Web search introduces latency
- Monitor search API costs
- Verify source reliability
- Check safety guardrails

### Step 7: Deploy Orchestrator (10% → 50% → 100%)

**Agent**: OrchestratorAgent

**Process**: Same as steps 2-4

**Special Considerations**:
- Affects entire pipeline
- Monitor end-to-end response time
- Verify parallel execution
- Check context sharing

### Step 8: Remove Old Implementations

**Goal**: Clean up old code after successful migration

**Actions**:
1. Verify all feature flags at 100% for 2+ weeks
2. Verify no rollbacks needed
3. Remove old agent implementations
4. Remove feature flag code
5. Update documentation

**Verification**:
```bash
# Verify no old code references
python manage.py verify_migration_complete

# Run full test suite
python manage.py test

# Deploy and monitor
```

## A/B Testing

### Enable A/B Testing

```bash
# Enable A/B testing for agent
python manage.py enable_ab_test DataExtractionAgent

# Set traffic split (50/50)
python manage.py set_ab_split DataExtractionAgent 50

# View A/B test results
python manage.py show_ab_results DataExtractionAgent
```

### Metrics to Compare

- **Error Rate**: Old vs new implementation
- **Response Time**: Latency comparison
- **Output Quality**: Confidence scores, completeness
- **Cost**: API usage and costs
- **User Satisfaction**: If available

### A/B Test Duration

- Minimum: 1 week
- Recommended: 2-4 weeks
- Collect at least 1000 samples per variant

### A/B Test Decision

```bash
# View statistical significance
python manage.py ab_test_significance DataExtractionAgent

# If new implementation is better:
python manage.py promote_ab_variant DataExtractionAgent new

# If old implementation is better:
python manage.py promote_ab_variant DataExtractionAgent old
```

## Rollback Procedures

For detailed rollback procedures, see [ROLLBACK_PROCEDURES.md](ROLLBACK_PROCEDURES.md).

### Quick Rollback Reference

#### Single Agent Rollback

```bash
# Using automated script
python scripts/rollback_agent.py treatment_exploration "High error rate in production"

# Or using Python API
from backend.agents.infrastructure.rollback import get_rollback_executor
executor = get_rollback_executor()
result = executor.execute_rollback('treatment_exploration', 'High error rate')
```

#### Emergency Rollback (All Agents)

```bash
# Using automated script
python scripts/emergency_rollback.py "Critical production incident"

# Or using Python API
from backend.agents.infrastructure.rollback import emergency_rollback
result = emergency_rollback("Critical production incident")
```

#### Rollback Decision Matrix

| Metric | Threshold | Action |
|--------|-----------|--------|
| Error Rate | >5% increase | Consider rollback |
| Error Rate | >10% increase | Immediate rollback |
| Response Time | >50% slower | Consider rollback |
| Response Time | >100% slower | Immediate rollback |
| A/B Test Pass Rate | <90% | Investigate |
| A/B Test Pass Rate | <80% | Rollback |
| Production Incidents | Any critical | Immediate rollback |

### Rollback Verification

```bash
# Verify rollback completed
python scripts/generate_migration_report.py

# Check agent version
from backend.agents.infrastructure.feature_flags import get_feature_flags
flags = get_feature_flags()
print(flags.get_agent_version('agent_name'))  # Should be OLD

# Monitor metrics
python manage.py show_error_rate --last=1h
python manage.py show_response_time --last=1h
```

## Deployment Automation

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          python -m pytest tests/
          python -m pytest tests/property/
          
  deploy-staging:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: |
          # Deploy code
          # Run migrations
          # Restart services
          
  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to production
        run: |
          # Deploy code
          # Run migrations
          # Gradual rollout with feature flags
```

### Deployment Scripts

```bash
# deploy.sh
#!/bin/bash

ENVIRONMENT=$1
FEATURE_FLAG=$2
PERCENTAGE=$3

echo "Deploying to $ENVIRONMENT"

# Pull latest code
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Run tests
python manage.py test

# Enable feature flag
if [ -n "$FEATURE_FLAG" ]; then
  if [ -n "$PERCENTAGE" ]; then
    python manage.py set_feature_percentage $FEATURE_FLAG $PERCENTAGE
  else
    python manage.py enable_feature $FEATURE_FLAG
  fi
fi

# Restart application
sudo systemctl restart backend

# Verify deployment
python manage.py health_check

echo "Deployment complete"
```

**Usage**:
```bash
# Deploy to staging
./deploy.sh staging

# Deploy to production with gradual rollout
./deploy.sh production FEATURE_NEW_ORCHESTRATOR 10

# Deploy to production with full rollout
./deploy.sh production FEATURE_NEW_ORCHESTRATOR 100
```

## Monitoring During Deployment

### Key Metrics to Watch

```bash
# Error rate (should stay < 5%)
python manage.py show_error_rate --live

# Response time (should stay < 30s p95)
python manage.py show_response_time --live

# Agent success rate (should stay > 95%)
python manage.py show_agent_success_rate --live

# API costs (should not spike)
python manage.py show_api_costs --live

# Cache hit rate (should stay > 60%)
python manage.py show_cache_hit_rate --live
```

### Deployment Dashboard

Create a deployment dashboard showing:
- Current feature flag states
- Traffic split percentages
- Error rates (old vs new)
- Response times (old vs new)
- Cost comparison
- Rollback button

### Alerts During Deployment

```bash
# Enable deployment alerts
python manage.py enable_deployment_alerts

# Configure alert thresholds
export DEPLOYMENT_ALERT_ERROR_RATE=3  # Lower threshold during deployment
export DEPLOYMENT_ALERT_RESPONSE_TIME=25

# Disable after deployment complete
python manage.py disable_deployment_alerts
```

## Post-Deployment Verification

### Smoke Tests

```bash
# Run smoke tests
python manage.py smoke_test

# Test critical paths
python manage.py test_critical_paths

# Test each agent
python manage.py test_all_agents
```

### Performance Verification

```bash
# Compare performance before/after
python manage.py compare_performance --before --after

# Generate performance report
python manage.py performance_report --deployment-id=123
```

### Quality Verification

```bash
# Compare output quality
python manage.py compare_output_quality --before --after

# Run quality tests
python manage.py quality_test --sample-size=100
```

### Cost Verification

```bash
# Compare costs before/after
python manage.py compare_costs --before --after

# Project monthly costs
python manage.py project_costs --based-on-last=7d
```

## Disaster Recovery

### Backup Procedures

```bash
# Backup database
python manage.py backup_database

# Backup configuration
python manage.py backup_configuration

# Backup feature flags
python manage.py backup_feature_flags
```

### Recovery Procedures

```bash
# Restore database
python manage.py restore_database --backup-id=123

# Restore configuration
python manage.py restore_configuration --backup-id=123

# Restore feature flags
python manage.py restore_feature_flags --backup-id=123
```

### Failover Procedures

```bash
# Switch to backup region
python manage.py failover --region=us-west-2

# Verify failover
python manage.py verify_failover

# Switch back to primary
python manage.py failback --region=us-east-1
```

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Configuration validated
- [ ] Backup created
- [ ] Rollback plan documented
- [ ] Monitoring dashboard ready
- [ ] Alerts configured
- [ ] Team notified

### During Deployment

- [ ] Deploy to staging first
- [ ] Verify staging deployment
- [ ] Deploy to production with feature flags OFF
- [ ] Verify production deployment
- [ ] Enable feature flags gradually (10% → 50% → 100%)
- [ ] Monitor metrics continuously
- [ ] Compare old vs new implementations
- [ ] Document any issues

### Post-Deployment

- [ ] Verify all smoke tests pass
- [ ] Verify performance metrics
- [ ] Verify quality metrics
- [ ] Verify cost metrics
- [ ] Update documentation
- [ ] Notify team of completion
- [ ] Schedule post-deployment review

## Troubleshooting Deployments

### Deployment Failed

```bash
# Check deployment logs
tail -f logs/deployment.log

# Verify migrations
python manage.py showmigrations

# Verify configuration
python manage.py check

# Rollback if needed
python manage.py rollback_deployment
```

### Feature Flag Not Working

```bash
# Verify feature flag state
python manage.py show_feature_flags

# Check feature flag cache
python manage.py clear_feature_flag_cache

# Test feature flag
python manage.py test_feature_flag FEATURE_NEW_ORCHESTRATOR
```

### Performance Degradation

```bash
# Profile slow requests
python manage.py profile_slow_requests

# Check resource usage
python manage.py show_resource_usage

# Reduce traffic to new implementation
python manage.py set_feature_percentage FEATURE_NAME 10
```

## References

- [Architecture Documentation](ARCHITECTURE.md)
- [Agent Behavior Documentation](AGENT_BEHAVIOR.md)
- [Configuration Guide](CONFIGURATION.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Design Document](../../../.kiro/specs/autonomous-ai-agents-refactor/design.md)
- [Requirements Document](../../../.kiro/specs/autonomous-ai-agents-refactor/requirements.md)
