# Configuration Guide

## Overview

This guide documents all configuration parameters for the autonomous AI agents system, including default values, valid ranges, and tuning recommendations.

## Configuration Sources

Configuration is loaded from multiple sources in order of precedence:

1. **Environment Variables** (highest priority)
2. **Configuration Files** (.env, config.yaml)
3. **Default Values** (lowest priority)

## Environment Variables

### API Keys and Credentials

#### GEMINI_API_KEY
- **Description**: API key for Google Gemini AI
- **Required**: Yes
- **Default**: None
- **Example**: `export GEMINI_API_KEY="your-api-key-here"`
- **Security**: Store in secure vault or environment, never commit to code

#### SEARCH_API_KEY
- **Description**: API key for web search service
- **Required**: Yes
- **Default**: None
- **Example**: `export SEARCH_API_KEY="your-search-api-key"`
- **Security**: Store in secure vault or environment, never commit to code

#### FIREBASE_CREDENTIALS
- **Description**: Path to Firebase service account credentials JSON
- **Required**: Yes (for production)
- **Default**: None
- **Example**: `export FIREBASE_CREDENTIALS="/path/to/firebase-credentials.json"`
- **Security**: Restrict file permissions, never commit credentials

### Agent Configuration

#### AGENT_TIMEOUT
- **Description**: Maximum execution time for individual agents (seconds)
- **Required**: No
- **Default**: 30
- **Valid Range**: 5-300
- **Example**: `export AGENT_TIMEOUT=45`
- **Tuning**: 
  - Increase for complex medical reports
  - Decrease for faster response times
  - Monitor timeout rates to optimize

#### AGENT_MAX_RETRIES
- **Description**: Maximum retry attempts for failed operations
- **Required**: No
- **Default**: 3
- **Valid Range**: 0-10
- **Example**: `export AGENT_MAX_RETRIES=5`
- **Tuning**:
  - Increase for unreliable networks
  - Decrease to fail faster
  - Consider cost implications of retries

#### ORCHESTRATOR_TIMEOUT
- **Description**: Maximum execution time for full orchestration (seconds)
- **Required**: No
- **Default**: 120
- **Valid Range**: 30-600
- **Example**: `export ORCHESTRATOR_TIMEOUT=180`
- **Tuning**:
  - Must be greater than sum of agent timeouts
  - Increase for comprehensive assessments
  - Consider user experience for long waits

### Web Search Configuration

#### SEARCH_RATE_LIMIT
- **Description**: Maximum search requests per minute
- **Required**: No
- **Default**: 10
- **Valid Range**: 1-100
- **Example**: `export SEARCH_RATE_LIMIT=20`
- **Tuning**:
  - Increase for high-traffic scenarios
  - Decrease to control costs
  - Check API provider limits

#### SEARCH_MAX_RESULTS
- **Description**: Maximum search results to retrieve per query
- **Required**: No
- **Default**: 10
- **Valid Range**: 1-50
- **Example**: `export SEARCH_MAX_RESULTS=15`
- **Tuning**:
  - Increase for comprehensive information
  - Decrease to reduce processing time
  - Balance quality vs quantity

#### SEARCH_CACHE_TTL
- **Description**: Search result cache time-to-live (seconds)
- **Required**: No
- **Default**: 3600 (1 hour)
- **Valid Range**: 300-86400
- **Example**: `export SEARCH_CACHE_TTL=7200`
- **Tuning**:
  - Increase for stable information (anatomy, basic concepts)
  - Decrease for rapidly changing information (drug recalls, guidelines)
  - Monitor cache hit rates

#### SEARCH_RELIABLE_SOURCES_ONLY
- **Description**: Only return results from reliable medical sources
- **Required**: No
- **Default**: true
- **Valid Values**: true, false
- **Example**: `export SEARCH_RELIABLE_SOURCES_ONLY=true`
- **Tuning**:
  - Keep true for production (safety)
  - Set false for development/testing only

### Gemini AI Configuration

#### GEMINI_MODEL
- **Description**: Gemini model to use for text generation
- **Required**: No
- **Default**: gemini-1.5-pro
- **Valid Values**: gemini-1.5-pro, gemini-1.5-flash
- **Example**: `export GEMINI_MODEL=gemini-1.5-flash`
- **Tuning**:
  - Use gemini-1.5-pro for best quality
  - Use gemini-1.5-flash for faster/cheaper responses

#### GEMINI_VISION_MODEL
- **Description**: Gemini model to use for vision/OCR
- **Required**: No
- **Default**: gemini-1.5-pro-vision
- **Valid Values**: gemini-1.5-pro-vision
- **Example**: `export GEMINI_VISION_MODEL=gemini-1.5-pro-vision`

#### GEMINI_TEMPERATURE
- **Description**: Temperature for Gemini text generation (0-1)
- **Required**: No
- **Default**: 0.1
- **Valid Range**: 0.0-1.0
- **Example**: `export GEMINI_TEMPERATURE=0.2`
- **Tuning**:
  - Lower (0.0-0.3): More deterministic, factual (recommended for medical)
  - Higher (0.7-1.0): More creative, varied (not recommended)

#### GEMINI_MAX_TOKENS
- **Description**: Maximum tokens per Gemini API call
- **Required**: No
- **Default**: 2048
- **Valid Range**: 256-8192
- **Example**: `export GEMINI_MAX_TOKENS=4096`
- **Tuning**:
  - Increase for longer responses
  - Decrease to control costs
  - Monitor token usage

#### GEMINI_TOP_P
- **Description**: Top-p sampling parameter for Gemini
- **Required**: No
- **Default**: 0.95
- **Valid Range**: 0.0-1.0
- **Example**: `export GEMINI_TOP_P=0.9`
- **Tuning**:
  - Keep high (0.9-1.0) for medical accuracy
  - Lower values increase determinism

#### GEMINI_TOP_K
- **Description**: Top-k sampling parameter for Gemini
- **Required**: No
- **Default**: 40
- **Valid Range**: 1-100
- **Example**: `export GEMINI_TOP_K=50`
- **Tuning**:
  - Higher values increase diversity
  - Lower values increase focus

### Circuit Breaker Configuration

#### CIRCUIT_BREAKER_FAILURE_THRESHOLD
- **Description**: Number of failures before opening circuit
- **Required**: No
- **Default**: 5
- **Valid Range**: 1-20
- **Example**: `export CIRCUIT_BREAKER_FAILURE_THRESHOLD=10`
- **Tuning**:
  - Increase for tolerance of transient failures
  - Decrease to fail fast on persistent issues

#### CIRCUIT_BREAKER_TIMEOUT
- **Description**: Time circuit stays open before half-open (seconds)
- **Required**: No
- **Default**: 60
- **Valid Range**: 10-600
- **Example**: `export CIRCUIT_BREAKER_TIMEOUT=120`
- **Tuning**:
  - Increase for slow-recovering services
  - Decrease to retry sooner

#### CIRCUIT_BREAKER_HALF_OPEN_TIMEOUT
- **Description**: Time in half-open state before closing (seconds)
- **Required**: No
- **Default**: 30
- **Valid Range**: 5-300
- **Example**: `export CIRCUIT_BREAKER_HALF_OPEN_TIMEOUT=45`

### Cache Configuration

#### CACHE_ENABLED
- **Description**: Enable caching for web search and treatment data
- **Required**: No
- **Default**: true
- **Valid Values**: true, false
- **Example**: `export CACHE_ENABLED=true`
- **Tuning**:
  - Keep true for production (performance, cost)
  - Set false for development/testing

#### CACHE_TTL
- **Description**: Default cache time-to-live (seconds)
- **Required**: No
- **Default**: 3600 (1 hour)
- **Valid Range**: 60-86400
- **Example**: `export CACHE_TTL=7200`
- **Tuning**:
  - Increase for stable information
  - Decrease for rapidly changing information

#### CACHE_MAX_SIZE
- **Description**: Maximum cache size (MB)
- **Required**: No
- **Default**: 100
- **Valid Range**: 10-1000
- **Example**: `export CACHE_MAX_SIZE=200`
- **Tuning**:
  - Increase for high-traffic scenarios
  - Decrease to limit memory usage

#### TREATMENT_CACHE_TTL
- **Description**: Cache TTL for treatment information (seconds)
- **Required**: No
- **Default**: 86400 (24 hours)
- **Valid Range**: 3600-604800
- **Example**: `export TREATMENT_CACHE_TTL=172800`
- **Tuning**:
  - Treatment guidelines change slowly
  - 24-48 hours is reasonable

### Context Management Configuration

#### CONTEXT_MAX_SIZE
- **Description**: Maximum context size (characters)
- **Required**: No
- **Default**: 10000
- **Valid Range**: 1000-100000
- **Example**: `export CONTEXT_MAX_SIZE=20000`
- **Tuning**:
  - Increase for complex multi-agent workflows
  - Decrease to limit memory usage
  - Monitor context size in logs

#### CONTEXT_SUMMARIZATION_THRESHOLD
- **Description**: Context size that triggers summarization (characters)
- **Required**: No
- **Default**: 8000
- **Valid Range**: 500-90000
- **Example**: `export CONTEXT_SUMMARIZATION_THRESHOLD=15000`
- **Tuning**:
  - Should be 70-80% of CONTEXT_MAX_SIZE
  - Increase to preserve more detail

### Monitoring Configuration

#### MONITORING_ENABLED
- **Description**: Enable monitoring and metrics collection
- **Required**: No
- **Default**: true
- **Valid Values**: true, false
- **Example**: `export MONITORING_ENABLED=true`
- **Tuning**:
  - Keep true for production
  - Set false only for local development

#### MONITORING_SAMPLE_RATE
- **Description**: Percentage of requests to monitor (0-100)
- **Required**: No
- **Default**: 100
- **Valid Range**: 1-100
- **Example**: `export MONITORING_SAMPLE_RATE=50`
- **Tuning**:
  - 100% for low-traffic or critical systems
  - Lower for high-traffic to reduce overhead

#### ALERT_ERROR_RATE_THRESHOLD
- **Description**: Error rate percentage that triggers alert
- **Required**: No
- **Default**: 5
- **Valid Range**: 1-50
- **Example**: `export ALERT_ERROR_RATE_THRESHOLD=10`
- **Tuning**:
  - Lower for critical systems
  - Higher to reduce alert noise

#### ALERT_RESPONSE_TIME_THRESHOLD
- **Description**: Response time (seconds) that triggers alert
- **Required**: No
- **Default**: 30
- **Valid Range**: 5-300
- **Example**: `export ALERT_RESPONSE_TIME_THRESHOLD=45`
- **Tuning**:
  - Lower for real-time requirements
  - Higher for batch processing

### Feature Flags

#### FEATURE_NEW_ORCHESTRATOR
- **Description**: Use new autonomous orchestrator implementation
- **Required**: No
- **Default**: true
- **Valid Values**: true, false
- **Example**: `export FEATURE_NEW_ORCHESTRATOR=true`

#### FEATURE_NEW_DATA_EXTRACTION
- **Description**: Use new data extraction agent implementation
- **Required**: No
- **Default**: true
- **Valid Values**: true, false
- **Example**: `export FEATURE_NEW_DATA_EXTRACTION=true`

#### FEATURE_NEW_TREATMENT_EXPLORATION
- **Description**: Use new treatment exploration with dynamic retrieval
- **Required**: No
- **Default**: true
- **Valid Values**: true, false
- **Example**: `export FEATURE_NEW_TREATMENT_EXPLORATION=true`

#### FEATURE_WEB_SEARCH
- **Description**: Enable web search capabilities
- **Required**: No
- **Default**: true
- **Valid Values**: true, false
- **Example**: `export FEATURE_WEB_SEARCH=true`
- **Tuning**:
  - Set false to disable all web searches (use cached data only)

#### FEATURE_PARALLEL_EXECUTION
- **Description**: Enable parallel agent execution
- **Required**: No
- **Default**: true
- **Valid Values**: true, false
- **Example**: `export FEATURE_PARALLEL_EXECUTION=true`
- **Tuning**:
  - Set false for debugging or resource-constrained environments

### Logging Configuration

#### LOG_LEVEL
- **Description**: Logging level
- **Required**: No
- **Default**: INFO
- **Valid Values**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Example**: `export LOG_LEVEL=DEBUG`
- **Tuning**:
  - DEBUG: Development, troubleshooting
  - INFO: Production default
  - WARNING: Reduce log volume
  - ERROR: Only errors and critical issues

#### LOG_FORMAT
- **Description**: Log message format
- **Required**: No
- **Default**: json
- **Valid Values**: json, text
- **Example**: `export LOG_FORMAT=json`
- **Tuning**:
  - json: Production (structured logging)
  - text: Development (human-readable)

#### LOG_SANITIZE_PII
- **Description**: Remove PII from logs
- **Required**: No
- **Default**: true
- **Valid Values**: true, false
- **Example**: `export LOG_SANITIZE_PII=true`
- **Tuning**:
  - Keep true for production (privacy)
  - Set false only for debugging with consent

## Configuration File Format

### .env File Example

```bash
# API Keys
GEMINI_API_KEY=your-gemini-api-key
SEARCH_API_KEY=your-search-api-key
FIREBASE_CREDENTIALS=/path/to/firebase-creds.json

# Agent Configuration
AGENT_TIMEOUT=45
AGENT_MAX_RETRIES=3
ORCHESTRATOR_TIMEOUT=180

# Gemini Configuration
GEMINI_MODEL=gemini-1.5-pro
GEMINI_TEMPERATURE=0.1
GEMINI_MAX_TOKENS=2048

# Web Search Configuration
SEARCH_RATE_LIMIT=20
SEARCH_MAX_RESULTS=10
SEARCH_CACHE_TTL=3600
SEARCH_RELIABLE_SOURCES_ONLY=true

# Circuit Breaker Configuration
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60

# Cache Configuration
CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_MAX_SIZE=100
TREATMENT_CACHE_TTL=86400

# Context Configuration
CONTEXT_MAX_SIZE=10000
CONTEXT_SUMMARIZATION_THRESHOLD=8000

# Monitoring Configuration
MONITORING_ENABLED=true
MONITORING_SAMPLE_RATE=100
ALERT_ERROR_RATE_THRESHOLD=5
ALERT_RESPONSE_TIME_THRESHOLD=30

# Feature Flags
FEATURE_NEW_ORCHESTRATOR=true
FEATURE_NEW_DATA_EXTRACTION=true
FEATURE_NEW_TREATMENT_EXPLORATION=true
FEATURE_WEB_SEARCH=true
FEATURE_PARALLEL_EXECUTION=true

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_SANITIZE_PII=true
```

### config.yaml Example

```yaml
api_keys:
  gemini: ${GEMINI_API_KEY}
  search: ${SEARCH_API_KEY}
  firebase_credentials: ${FIREBASE_CREDENTIALS}

agents:
  timeout: 45
  max_retries: 3
  orchestrator_timeout: 180

gemini:
  model: gemini-1.5-pro
  vision_model: gemini-1.5-pro-vision
  temperature: 0.1
  max_tokens: 2048
  top_p: 0.95
  top_k: 40

web_search:
  rate_limit: 20
  max_results: 10
  cache_ttl: 3600
  reliable_sources_only: true

circuit_breaker:
  failure_threshold: 5
  timeout: 60
  half_open_timeout: 30

cache:
  enabled: true
  ttl: 3600
  max_size_mb: 100
  treatment_ttl: 86400

context:
  max_size: 10000
  summarization_threshold: 8000

monitoring:
  enabled: true
  sample_rate: 100
  alerts:
    error_rate_threshold: 5
    response_time_threshold: 30

feature_flags:
  new_orchestrator: true
  new_data_extraction: true
  new_treatment_exploration: true
  web_search: true
  parallel_execution: true

logging:
  level: INFO
  format: json
  sanitize_pii: true
```

## Configuration Profiles

### Development Profile

```bash
# Faster timeouts for quick iteration
AGENT_TIMEOUT=15
ORCHESTRATOR_TIMEOUT=60

# More verbose logging
LOG_LEVEL=DEBUG
LOG_FORMAT=text

# Disable monitoring overhead
MONITORING_ENABLED=false

# Smaller cache
CACHE_MAX_SIZE=50

# Use faster model
GEMINI_MODEL=gemini-1.5-flash
```

### Staging Profile

```bash
# Production-like timeouts
AGENT_TIMEOUT=30
ORCHESTRATOR_TIMEOUT=120

# Production logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Enable monitoring
MONITORING_ENABLED=true
MONITORING_SAMPLE_RATE=100

# Full cache
CACHE_MAX_SIZE=100

# Production model
GEMINI_MODEL=gemini-1.5-pro
```

### Production Profile

```bash
# Generous timeouts for reliability
AGENT_TIMEOUT=45
ORCHESTRATOR_TIMEOUT=180

# Production logging with PII sanitization
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_SANITIZE_PII=true

# Full monitoring
MONITORING_ENABLED=true
MONITORING_SAMPLE_RATE=100

# Large cache for performance
CACHE_MAX_SIZE=200

# Best model for quality
GEMINI_MODEL=gemini-1.5-pro

# Strict safety
SEARCH_RELIABLE_SOURCES_ONLY=true
```

## Tuning Recommendations

### For High Traffic

```bash
# Increase cache to reduce API calls
CACHE_MAX_SIZE=500
SEARCH_CACHE_TTL=7200
TREATMENT_CACHE_TTL=172800

# Increase rate limits
SEARCH_RATE_LIMIT=50

# Use faster model
GEMINI_MODEL=gemini-1.5-flash

# Reduce monitoring overhead
MONITORING_SAMPLE_RATE=10
```

### For High Accuracy

```bash
# Use best model
GEMINI_MODEL=gemini-1.5-pro

# Lower temperature for determinism
GEMINI_TEMPERATURE=0.0

# More search results
SEARCH_MAX_RESULTS=20

# Strict source filtering
SEARCH_RELIABLE_SOURCES_ONLY=true

# Full monitoring
MONITORING_SAMPLE_RATE=100
```

### For Cost Optimization

```bash
# Use cheaper model
GEMINI_MODEL=gemini-1.5-flash

# Reduce token usage
GEMINI_MAX_TOKENS=1024

# Aggressive caching
CACHE_TTL=7200
TREATMENT_CACHE_TTL=604800

# Fewer search results
SEARCH_MAX_RESULTS=5

# Lower rate limit
SEARCH_RATE_LIMIT=5
```

### For Low Latency

```bash
# Shorter timeouts
AGENT_TIMEOUT=15
ORCHESTRATOR_TIMEOUT=60

# Use faster model
GEMINI_MODEL=gemini-1.5-flash

# Fewer search results
SEARCH_MAX_RESULTS=5

# Aggressive caching
CACHE_ENABLED=true
CACHE_TTL=7200

# Enable parallel execution
FEATURE_PARALLEL_EXECUTION=true
```

## Configuration Validation

The system validates all configuration on startup:

```python
# Example validation errors
ConfigurationError: AGENT_TIMEOUT must be between 5 and 300 seconds
ConfigurationError: GEMINI_API_KEY is required but not set
ConfigurationError: CIRCUIT_BREAKER_FAILURE_THRESHOLD must be positive
ConfigurationError: CONTEXT_SUMMARIZATION_THRESHOLD must be less than CONTEXT_MAX_SIZE
```

## Hot Reload Support

Some configuration parameters support hot reload (no restart required):

**Hot Reload Supported**:
- LOG_LEVEL
- MONITORING_SAMPLE_RATE
- CACHE_TTL
- SEARCH_RATE_LIMIT
- Feature flags

**Restart Required**:
- API keys
- AGENT_TIMEOUT
- GEMINI_MODEL
- CIRCUIT_BREAKER_FAILURE_THRESHOLD

To trigger hot reload:
```bash
# Send SIGHUP signal
kill -HUP <pid>

# Or use management command
python manage.py reload_config
```

## Monitoring Configuration Impact

Track how configuration changes affect system behavior:

```python
# Example metrics to monitor after config changes
- Response time (should decrease with faster model)
- Error rate (should decrease with more retries)
- Cache hit rate (should increase with longer TTL)
- Cost per request (should decrease with caching)
- Quality scores (should increase with better model)
```

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** or secure vaults for secrets
3. **Rotate API keys** regularly
4. **Restrict file permissions** on credential files (chmod 600)
5. **Enable PII sanitization** in production logs
6. **Use HTTPS** for all external API calls
7. **Validate all configuration** on startup
8. **Audit configuration changes** in production

## Troubleshooting Configuration Issues

### API Key Issues
```bash
# Test API key validity
python manage.py test_api_keys

# Check key permissions
ls -la /path/to/firebase-credentials.json
```

### Timeout Issues
```bash
# Check current timeouts
python manage.py show_config | grep TIMEOUT

# Monitor timeout rates
python manage.py show_metrics --filter=timeout
```

### Cache Issues
```bash
# Check cache hit rate
python manage.py show_metrics --filter=cache

# Clear cache
python manage.py clear_cache
```

### Performance Issues
```bash
# Profile configuration impact
python manage.py profile_config

# Compare configurations
python manage.py compare_config config1.yaml config2.yaml
```

## References

- [Architecture Documentation](ARCHITECTURE.md)
- [Agent Behavior Documentation](AGENT_BEHAVIOR.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Deployment Guide](DEPLOYMENT.md)
