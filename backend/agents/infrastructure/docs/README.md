# Autonomous AI Agents Documentation

## Overview

This directory contains comprehensive documentation for the autonomous AI agents health intelligence system. The system uses LangChain framework and Gemini AI to provide intelligent health assessments through coordinated autonomous agents.

## Documentation Structure

### 📐 [ARCHITECTURE.md](ARCHITECTURE.md)
**System and agent architecture documentation**

Learn about:
- High-level system architecture
- Agent architecture and layering
- Component interactions and data flow
- Design patterns used throughout the system
- Scalability and performance considerations
- Security architecture
- Deployment architecture

**Start here if you want to understand how the system works.**

### 🤖 [AGENT_BEHAVIOR.md](AGENT_BEHAVIOR.md)
**Detailed agent behavior and capabilities**

Learn about:
- Each agent's purpose and capabilities
- Decision-making logic for autonomous behavior
- Web search strategies and triggers
- Error handling approaches
- Input/output formats
- Performance characteristics
- Cost estimates

**Start here if you want to understand what each agent does and how it makes decisions.**

### ⚙️ [CONFIGURATION.md](CONFIGURATION.md)
**Configuration parameters and tuning guide**

Learn about:
- All environment variables and their meanings
- Default values and valid ranges
- Configuration file formats
- Configuration profiles (development, staging, production)
- Tuning recommendations for different scenarios
- Hot reload support
- Security best practices

**Start here if you need to configure or tune the system.**

### 🔧 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
**Common issues, error codes, and debugging**

Learn about:
- Common issues and their solutions
- Error code meanings and resolutions
- Debugging strategies and tools
- Performance troubleshooting
- Log analysis techniques
- Monitoring and alerts
- Getting help

**Start here if you're experiencing issues or errors.**

### 🚀 [DEPLOYMENT.md](DEPLOYMENT.md)
**Deployment process and rollout strategies**

Learn about:
- Deployment strategy and phases
- Feature flag usage
- Gradual rollout process (10% → 50% → 100%)
- A/B testing procedures
- Rollback procedures
- Deployment automation
- Post-deployment verification

**Start here if you're deploying the system or managing feature rollouts.**

## Quick Start

### For Developers

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
2. Read [AGENT_BEHAVIOR.md](AGENT_BEHAVIOR.md) to understand agent capabilities
3. Read [CONFIGURATION.md](CONFIGURATION.md) to set up your environment
4. Refer to [TROUBLESHOOTING.md](TROUBLESHOOTING.md) when issues arise

### For Operators

1. Read [DEPLOYMENT.md](DEPLOYMENT.md) for deployment procedures
2. Read [CONFIGURATION.md](CONFIGURATION.md) for configuration management
3. Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for operational issues
4. Refer to [ARCHITECTURE.md](ARCHITECTURE.md) for system understanding

### For System Administrators

1. Read [CONFIGURATION.md](CONFIGURATION.md) for system configuration
2. Read [DEPLOYMENT.md](DEPLOYMENT.md) for deployment management
3. Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for issue resolution
4. Read [ARCHITECTURE.md](ARCHITECTURE.md) for security and scalability

## Common Tasks

### Setting Up Development Environment

1. Install dependencies: `pip install -r requirements.txt`
2. Configure API keys (see [CONFIGURATION.md](CONFIGURATION.md))
3. Set up development configuration
4. Run migrations: `python manage.py migrate`
5. Start server: `python manage.py runserver`

### Deploying a New Agent

1. Review deployment strategy in [DEPLOYMENT.md](DEPLOYMENT.md)
2. Enable feature flag at 10%
3. Monitor metrics for 24-48 hours
4. Increase to 50% if successful
5. Monitor for 48-72 hours
6. Increase to 100% if successful

### Troubleshooting an Issue

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
2. Review error logs: `tail -f logs/errors.log`
3. Check system health: `python manage.py health_check`
4. View metrics: `python manage.py show_metrics`
5. Generate diagnostic report: `python manage.py diagnostic_report`

### Tuning Performance

1. Review current configuration in [CONFIGURATION.md](CONFIGURATION.md)
2. Identify bottleneck: `python manage.py show_bottlenecks`
3. Apply tuning recommendations from [CONFIGURATION.md](CONFIGURATION.md)
4. Monitor impact: `python manage.py show_metrics`
5. Iterate as needed

## System Components

### Agents

- **OrchestratorAgent**: Coordinates all other agents
- **DataExtractionAgent**: Extracts structured data from text
- **EnhancedExtractionAgent**: OCR and image analysis
- **SeverityAgent**: Assesses condition severity
- **TreatmentExplorationAgent**: Searches for treatment information
- **RecommendationAgent**: Generates personalized recommendations
- **LifestyleAgent**: Provides lifestyle intervention advice
- **ExplanationAgent**: Explains medical terms and concepts
- **ValidationAgent**: Validates data quality
- **ReflectionAgent**: Self-evaluates output quality

### Infrastructure

- **WebSearchTool**: Medical web search with source filtering
- **GeminiOCRService**: Vision-based OCR extraction
- **DecisionEngine**: Autonomous decision-making
- **CircuitBreaker**: Prevents cascading failures
- **ContextManager**: Manages agent memory and context
- **MonitoringService**: Tracks metrics and performance
- **SafetyGuardrails**: Ensures medical safety compliance
- **DynamicTreatmentRetrieval**: Dynamic treatment information

## Key Concepts

### Autonomous Agents

Agents make independent decisions about:
- When to search the web for information
- How to handle incomplete or conflicting data
- When to escalate to human review
- Which information sources to trust
- How to recover from errors

### Web Search

All agents can search the web for current information:
- Only reliable medical sources used
- Results cached to reduce costs
- Rate limiting prevents excessive calls
- All sources cited in responses

### Dynamic Data Retrieval

No static medical data:
- Treatment information retrieved dynamically
- Clinical guidelines searched in real-time
- Drug interactions checked on demand
- Information always current

### Safety Guardrails

Medical safety is paramount:
- No specific diagnoses provided
- No medication dosages recommended
- All responses include disclaimers
- Emergency situations detected and escalated
- Only reliable sources used

### Gradual Rollout

New implementations deployed gradually:
- Feature flags control rollout
- Start with 10% of traffic
- Increase to 50%, then 100%
- A/B testing compares implementations
- Easy rollback if issues detected

## Monitoring and Observability

### Key Metrics

- **Error Rate**: Should be < 5%
- **Response Time**: Should be < 30s (p95)
- **Cache Hit Rate**: Should be > 60%
- **Agent Success Rate**: Should be > 95%
- **API Costs**: Track daily spend

### Dashboards

- Agent execution metrics
- Web search usage
- Gemini API usage
- Error rates and types
- Performance trends

### Alerts

- Error rate > 5%: Warning
- Error rate > 10%: Critical
- Response time > 30s: Warning
- Response time > 60s: Critical
- Circuit breaker open: Critical

## Support and Resources

### Internal Resources

- [Design Document](../../../.kiro/specs/autonomous-ai-agents-refactor/design.md)
- [Requirements Document](../../../.kiro/specs/autonomous-ai-agents-refactor/requirements.md)
- [Implementation Tasks](../../../.kiro/specs/autonomous-ai-agents-refactor/tasks.md)

### Management Commands

```bash
# Health and status
python manage.py health_check
python manage.py agent_status
python manage.py show_metrics

# Configuration
python manage.py show_config
python manage.py test_api_keys
python manage.py show_feature_flags

# Troubleshooting
python manage.py show_errors
python manage.py diagnostic_report
python manage.py profile_request

# Deployment
python manage.py enable_feature FEATURE_NAME
python manage.py set_feature_percentage FEATURE_NAME 50
python manage.py show_ab_results AGENT_NAME
```

### Getting Help

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review logs: `tail -f logs/app.log`
3. Generate diagnostic report: `python manage.py diagnostic_report`
4. Contact support with diagnostic information

## Contributing

When updating documentation:

1. Keep documentation in sync with code
2. Update all affected documents
3. Include examples and code snippets
4. Test all commands and procedures
5. Update this README if adding new documents

## Version History

- **v1.0** (2024): Initial documentation for autonomous agents refactor
  - Architecture documentation
  - Agent behavior documentation
  - Configuration guide
  - Troubleshooting guide
  - Deployment guide

## License

Internal documentation for health AI backend system.
