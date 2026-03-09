# Troubleshooting Guide

## Overview

This guide provides solutions for common issues, error code meanings, and debugging strategies for the autonomous AI agents system.

## Quick Diagnostics

### Health Check Commands

```bash
# Check system health
python manage.py health_check

# Check API connectivity
python manage.py test_api_keys

# Check agent status
python manage.py agent_status

# View recent errors
python manage.py show_errors --last=24h

# View metrics
python manage.py show_metrics
```

### Log Locations

```bash
# Application logs
logs/app.log

# Agent execution logs
logs/agents/

# Error logs
logs/errors.log

# Monitoring logs
logs/monitoring.log

# Audit logs
logs/audit.log
```

## Common Issues and Solutions

### 1. API Key Issues

#### Error: "GEMINI_API_KEY is required but not set"

**Cause**: Gemini API key not configured

**Solution**:
```bash
# Set environment variable
export GEMINI_API_KEY="your-api-key-here"

# Or add to .env file
echo "GEMINI_API_KEY=your-api-key-here" >> .env

# Restart application
python manage.py runserver
```

**Verification**:
```bash
python manage.py test_api_keys
```

#### Error: "Invalid API key"

**Cause**: API key is incorrect or expired

**Solution**:
1. Verify key in Google Cloud Console
2. Generate new key if needed
3. Update environment variable
4. Restart application

**Verification**:
```bash
# Test with curl
curl -H "Authorization: Bearer $GEMINI_API_KEY" \
  https://generativelanguage.googleapis.com/v1/models
```

#### Error: "API key access denied"

**Cause**: API key lacks required permissions

**Solution**:
1. Check API key permissions in Google Cloud Console
2. Enable Generative Language API
3. Enable Vision API
4. Regenerate key with correct permissions

---

### 2. Timeout Issues

#### Error: "Agent timeout after 30 seconds"

**Cause**: Agent execution exceeded configured timeout

**Solution**:
```bash
# Increase timeout
export AGENT_TIMEOUT=60

# Or for specific agent
export DATA_EXTRACTION_TIMEOUT=45

# Restart application
```

**Investigation**:
```bash
# Check which agents are timing out
python manage.py show_metrics --filter=timeout

# View slow operations
python manage.py show_slow_operations

# Profile agent execution
python manage.py profile_agent DataExtractionAgent
```

**Tuning**:
- Increase timeout for complex medical reports
- Check network latency to external APIs
- Monitor Gemini API response times
- Consider using faster model (gemini-1.5-flash)

#### Error: "Orchestrator timeout after 120 seconds"

**Cause**: Full health assessment exceeded orchestrator timeout

**Solution**:
```bash
# Increase orchestrator timeout
export ORCHESTRATOR_TIMEOUT=180

# Enable parallel execution
export FEATURE_PARALLEL_EXECUTION=true

# Reduce individual agent timeouts
export AGENT_TIMEOUT=30
```

**Investigation**:
```bash
# View orchestration breakdown
python manage.py show_orchestration_metrics

# Identify bottleneck agents
python manage.py profile_orchestration
```

---

### 3. Web Search Issues

#### Error: "Search rate limit exceeded"

**Cause**: Too many search requests in short time

**Solution**:
```bash
# Increase rate limit
export SEARCH_RATE_LIMIT=20

# Increase cache TTL to reduce searches
export SEARCH_CACHE_TTL=7200

# Enable aggressive caching
export CACHE_ENABLED=true
```

**Investigation**:
```bash
# Check search usage
python manage.py show_metrics --filter=search

# View cache hit rate
python manage.py show_cache_stats

# Identify agents making most searches
python manage.py show_search_by_agent
```

#### Error: "No reliable sources found"

**Cause**: Search returned no results from reliable medical sources

**Solution**:
```bash
# Temporarily allow broader sources (development only)
export SEARCH_RELIABLE_SOURCES_ONLY=false

# Or broaden search query
# Check logs for search query used
tail -f logs/agents/web_search.log
```

**Investigation**:
- Review search query in logs
- Check if medical term is too specific
- Verify reliable source list is up to date
- Test search manually with same query

#### Error: "Search API unavailable"

**Cause**: External search API is down or unreachable

**Solution**:
```bash
# Check circuit breaker status
python manage.py show_circuit_breakers

# Reset circuit breaker if needed
python manage.py reset_circuit_breaker search_api

# Use cached results
export CACHE_ENABLED=true
```

**Investigation**:
```bash
# Test search API connectivity
curl -H "Authorization: Bearer $SEARCH_API_KEY" \
  https://search-api-endpoint.com/health

# Check network connectivity
ping search-api-endpoint.com

# Review circuit breaker logs
grep "circuit_breaker" logs/app.log
```

---

### 4. OCR Issues

#### Error: "Unsupported image format"

**Cause**: Image format not supported by Gemini Vision

**Solution**:
- Convert image to supported format (JPEG, PNG, PDF, TIFF)
- Check image file extension matches actual format
- Verify image is not corrupted

**Supported Formats**:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- PDF (.pdf)
- TIFF (.tif, .tiff)

**Conversion**:
```bash
# Convert to JPEG
convert input.bmp output.jpg

# Convert to PNG
convert input.gif output.png
```

#### Error: "Image too large"

**Cause**: Image exceeds maximum size limit

**Solution**:
```bash
# Resize image
convert input.jpg -resize 2048x2048 output.jpg

# Compress image
convert input.jpg -quality 85 output.jpg

# Check image size
ls -lh image.jpg
```

**Limits**:
- Maximum file size: 20 MB
- Maximum dimensions: 4096x4096 pixels

#### Error: "Low confidence OCR extraction"

**Cause**: Image quality is poor or text is unclear

**Solution**:
- Improve image quality (higher resolution, better lighting)
- Enhance image before OCR:
  ```bash
  # Increase contrast
  convert input.jpg -contrast-stretch 0 output.jpg
  
  # Denoise
  convert input.jpg -despeckle output.jpg
  
  # Sharpen
  convert input.jpg -sharpen 0x1 output.jpg
  ```
- Review low confidence sections manually
- Flag for human review

**Investigation**:
```bash
# View confidence scores
python manage.py show_ocr_confidence --report-id=123

# View low confidence extractions
python manage.py show_low_confidence --threshold=0.7
```

#### Error: "Vision API quota exceeded"

**Cause**: Exceeded Gemini Vision API quota

**Solution**:
```bash
# Check quota usage
python manage.py show_api_usage --api=vision

# Request quota increase in Google Cloud Console
# Implement request throttling
export VISION_RATE_LIMIT=10

# Use caching for repeated images
export CACHE_ENABLED=true
```

---

### 5. Circuit Breaker Issues

#### Error: "Circuit breaker open for gemini_api"

**Cause**: Multiple consecutive failures to Gemini API

**Solution**:
```bash
# Check Gemini API status
curl https://status.cloud.google.com/

# Wait for circuit breaker timeout (default 60s)
# Or reset manually
python manage.py reset_circuit_breaker gemini_api

# Check circuit breaker status
python manage.py show_circuit_breakers
```

**Investigation**:
```bash
# View failure history
python manage.py show_circuit_breaker_history gemini_api

# Check error logs
grep "gemini_api" logs/errors.log

# Verify API key is valid
python manage.py test_api_keys
```

**Prevention**:
```bash
# Increase failure threshold
export CIRCUIT_BREAKER_FAILURE_THRESHOLD=10

# Increase timeout
export CIRCUIT_BREAKER_TIMEOUT=120
```

#### Error: "Circuit breaker open for search_api"

**Cause**: Multiple consecutive failures to search API

**Solution**:
```bash
# Check search API status
# Reset circuit breaker
python manage.py reset_circuit_breaker search_api

# Use cached results
export CACHE_ENABLED=true

# Disable web search temporarily
export FEATURE_WEB_SEARCH=false
```

---

### 6. Context Management Issues

#### Error: "Context size exceeded maximum"

**Cause**: Context grew beyond configured maximum

**Solution**:
```bash
# Increase context size
export CONTEXT_MAX_SIZE=20000

# Lower summarization threshold
export CONTEXT_SUMMARIZATION_THRESHOLD=15000

# Clear context more frequently
```

**Investigation**:
```bash
# View context size
python manage.py show_context_size --session-id=abc123

# View context growth over time
python manage.py show_context_growth --session-id=abc123
```

#### Error: "Context summarization failed"

**Cause**: Failed to summarize context when approaching size limit

**Solution**:
```bash
# Check Gemini API availability
python manage.py test_api_keys

# Increase context size to avoid summarization
export CONTEXT_MAX_SIZE=50000

# Clear context and restart
python manage.py clear_context --session-id=abc123
```

---

### 7. Agent Coordination Issues

#### Error: "Agent dependency cycle detected"

**Cause**: Circular dependency between agents

**Solution**:
- Review agent dependencies in orchestrator
- Remove circular dependencies
- Ensure agents can execute independently

**Investigation**:
```bash
# View agent dependency graph
python manage.py show_agent_dependencies

# Validate orchestration logic
python manage.py validate_orchestration
```

#### Error: "Parallel execution failed"

**Cause**: Error during parallel agent execution

**Solution**:
```bash
# Disable parallel execution temporarily
export FEATURE_PARALLEL_EXECUTION=false

# Check resource limits
ulimit -a

# Increase worker pool size
export AGENT_WORKER_POOL_SIZE=10
```

**Investigation**:
```bash
# View parallel execution metrics
python manage.py show_parallel_metrics

# Check for resource contention
python manage.py show_resource_usage
```

---

### 8. Cache Issues

#### Error: "Cache connection failed"

**Cause**: Cannot connect to cache backend (Redis/Firebase)

**Solution**:
```bash
# Check cache backend status
redis-cli ping  # For Redis
# Or check Firebase connection

# Use in-memory cache temporarily
export CACHE_BACKEND=memory

# Restart cache backend
sudo systemctl restart redis
```

#### Error: "Cache full"

**Cause**: Cache reached maximum size

**Solution**:
```bash
# Increase cache size
export CACHE_MAX_SIZE=500

# Clear old cache entries
python manage.py clear_cache --older-than=7d

# Reduce cache TTL
export CACHE_TTL=1800
```

**Investigation**:
```bash
# View cache usage
python manage.py show_cache_stats

# View cache hit rate
python manage.py show_cache_hit_rate

# View largest cache entries
python manage.py show_cache_top_entries
```

---

### 9. Safety Guardrail Issues

#### Error: "Safety violation detected"

**Cause**: Response contained prohibited content (diagnosis, dosage)

**Solution**:
- Review safety guardrail logs
- Check if false positive
- Adjust safety rules if needed (carefully!)

**Investigation**:
```bash
# View safety violations
python manage.py show_safety_violations

# View specific violation
python manage.py show_safety_violation --id=123

# Test safety guardrails
python manage.py test_safety_guardrails
```

#### Error: "Emergency indicator not detected"

**Cause**: System failed to detect emergency medical situation

**Solution**:
- Review emergency keyword list
- Add missing keywords
- Improve detection logic
- Report as critical bug

**Investigation**:
```bash
# View emergency detection logs
grep "emergency" logs/agents/severity.log

# Test emergency detection
python manage.py test_emergency_detection
```

---

### 10. Performance Issues

#### Error: "Slow response times"

**Cause**: System responding slower than expected

**Solution**:
```bash
# Use faster model
export GEMINI_MODEL=gemini-1.5-flash

# Enable parallel execution
export FEATURE_PARALLEL_EXECUTION=true

# Increase cache hit rate
export CACHE_TTL=7200

# Reduce search results
export SEARCH_MAX_RESULTS=5
```

**Investigation**:
```bash
# Profile slow requests
python manage.py profile_slow_requests

# View bottleneck agents
python manage.py show_bottlenecks

# View API latency
python manage.py show_api_latency

# View cache hit rate
python manage.py show_cache_hit_rate
```

#### Error: "High memory usage"

**Cause**: System consuming excessive memory

**Solution**:
```bash
# Reduce context size
export CONTEXT_MAX_SIZE=5000

# Reduce cache size
export CACHE_MAX_SIZE=50

# Reduce worker pool size
export AGENT_WORKER_POOL_SIZE=2

# Enable lazy loading
export AGENT_LAZY_LOADING=true
```

**Investigation**:
```bash
# View memory usage
python manage.py show_memory_usage

# Profile memory usage
python manage.py profile_memory

# View largest objects
python manage.py show_memory_top_objects
```

---

## Error Codes

### Agent Errors (1000-1999)

| Code | Error | Meaning | Solution |
|------|-------|---------|----------|
| 1001 | AGENT_TIMEOUT | Agent exceeded timeout | Increase timeout or optimize agent |
| 1002 | AGENT_FAILED | Agent execution failed | Check logs, retry operation |
| 1003 | AGENT_NOT_FOUND | Agent not registered | Check agent name, verify registration |
| 1004 | AGENT_DISABLED | Agent disabled by feature flag | Enable feature flag |
| 1005 | AGENT_DEPENDENCY_FAILED | Agent dependency failed | Check dependent agent status |

### API Errors (2000-2999)

| Code | Error | Meaning | Solution |
|------|-------|---------|----------|
| 2001 | GEMINI_API_ERROR | Gemini API call failed | Check API key, retry |
| 2002 | GEMINI_QUOTA_EXCEEDED | Gemini API quota exceeded | Wait or request quota increase |
| 2003 | GEMINI_INVALID_REQUEST | Invalid request to Gemini | Check request format |
| 2004 | SEARCH_API_ERROR | Search API call failed | Check API key, retry |
| 2005 | SEARCH_RATE_LIMIT | Search rate limit exceeded | Wait or increase limit |
| 2006 | FIREBASE_ERROR | Firebase operation failed | Check credentials, connection |

### Data Errors (3000-3999)

| Code | Error | Meaning | Solution |
|------|-------|---------|----------|
| 3001 | INVALID_INPUT | Invalid input data | Validate input format |
| 3002 | MISSING_REQUIRED_FIELD | Required field missing | Provide required field |
| 3003 | INVALID_IMAGE_FORMAT | Unsupported image format | Convert to supported format |
| 3004 | IMAGE_TOO_LARGE | Image exceeds size limit | Resize or compress image |
| 3005 | CORRUPTED_IMAGE | Image file corrupted | Provide valid image |
| 3006 | EXTRACTION_FAILED | Data extraction failed | Check input quality, retry |

### System Errors (4000-4999)

| Code | Error | Meaning | Solution |
|------|-------|---------|----------|
| 4001 | CIRCUIT_BREAKER_OPEN | Circuit breaker open | Wait for timeout or reset |
| 4002 | CACHE_ERROR | Cache operation failed | Check cache backend |
| 4003 | CONTEXT_SIZE_EXCEEDED | Context too large | Increase limit or clear context |
| 4004 | CONFIGURATION_ERROR | Invalid configuration | Fix configuration, restart |
| 4005 | RESOURCE_EXHAUSTED | System resources exhausted | Scale up or optimize |

### Safety Errors (5000-5999)

| Code | Error | Meaning | Solution |
|------|-------|---------|----------|
| 5001 | SAFETY_VIOLATION | Safety guardrail triggered | Review content, adjust if needed |
| 5002 | UNRELIABLE_SOURCE | Source not reliable | Use reliable sources only |
| 5003 | EMERGENCY_DETECTED | Emergency situation detected | Escalate to human review |
| 5004 | DIAGNOSIS_PREVENTED | Diagnosis content filtered | Rephrase without diagnosis |
| 5005 | DOSAGE_PREVENTED | Dosage content filtered | Remove specific dosages |

---

## Debugging Strategies

### 1. Enable Debug Logging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Restart application
python manage.py runserver

# Tail logs
tail -f logs/app.log
```

### 2. Trace Agent Execution

```bash
# Enable agent tracing
export AGENT_TRACE=true

# View agent execution trace
python manage.py show_trace --request-id=abc123

# View agent decision log
python manage.py show_decisions --agent=OrchestratorAgent
```

### 3. Profile Performance

```bash
# Profile specific request
python manage.py profile_request --request-id=abc123

# Profile agent
python manage.py profile_agent DataExtractionAgent

# Profile orchestration
python manage.py profile_orchestration

# Generate performance report
python manage.py performance_report --last=24h
```

### 4. Test Individual Components

```bash
# Test web search
python manage.py test_web_search "diabetes treatment"

# Test OCR
python manage.py test_ocr /path/to/image.jpg

# Test agent
python manage.py test_agent DataExtractionAgent --input=test_data.json

# Test safety guardrails
python manage.py test_safety_guardrails --text="sample text"
```

### 5. Inspect State

```bash
# View circuit breaker state
python manage.py show_circuit_breakers

# View cache state
python manage.py show_cache_stats

# View context state
python manage.py show_context --session-id=abc123

# View agent state
python manage.py show_agent_state
```

### 6. Compare Implementations

```bash
# Compare old vs new agent
python manage.py compare_agents DataExtractionAgent --input=test_data.json

# View A/B test results
python manage.py show_ab_test_results --agent=TreatmentExplorationAgent
```

---

## Monitoring and Alerts

### Key Metrics to Monitor

1. **Error Rate**: Should be < 5%
2. **Response Time**: Should be < 30s (p95)
3. **Cache Hit Rate**: Should be > 60%
4. **API Cost**: Track daily spend
5. **Circuit Breaker Status**: Should be closed
6. **Agent Success Rate**: Should be > 95%

### Alert Thresholds

```bash
# Configure alert thresholds
export ALERT_ERROR_RATE_THRESHOLD=5
export ALERT_RESPONSE_TIME_THRESHOLD=30
export ALERT_CACHE_HIT_RATE_THRESHOLD=60
export ALERT_COST_SPIKE_THRESHOLD=50  # % above baseline
```

### View Alerts

```bash
# View active alerts
python manage.py show_alerts

# View alert history
python manage.py show_alert_history --last=7d

# Test alerting
python manage.py test_alerts
```

---

## Getting Help

### Log Analysis

```bash
# Search logs for errors
grep "ERROR" logs/app.log

# Search logs for specific agent
grep "DataExtractionAgent" logs/agents/*.log

# Search logs for request ID
grep "request_id=abc123" logs/app.log

# View recent errors
tail -100 logs/errors.log
```

### Collect Diagnostic Information

```bash
# Generate diagnostic report
python manage.py diagnostic_report > diagnostic.txt

# Include:
# - System configuration
# - Recent errors
# - Performance metrics
# - Circuit breaker status
# - Cache statistics
# - Agent status
```

### Contact Support

When contacting support, provide:
1. Diagnostic report
2. Request ID of failing request
3. Relevant log excerpts
4. Configuration (sanitized, no API keys)
5. Steps to reproduce
6. Expected vs actual behavior

---

## Preventive Maintenance

### Regular Tasks

```bash
# Daily
- Review error logs
- Check alert dashboard
- Monitor API costs
- Verify cache hit rates

# Weekly
- Review performance metrics
- Analyze slow requests
- Check circuit breaker history
- Review safety violations

# Monthly
- Rotate API keys
- Update dependencies
- Review and optimize configuration
- Analyze cost trends
- Review agent performance
```

### Health Checks

```bash
# Automated health checks
python manage.py health_check

# Should check:
# - API connectivity
# - Database connectivity
# - Cache connectivity
# - Agent registration
# - Configuration validity
# - Circuit breaker status
```

---

## References

- [Architecture Documentation](ARCHITECTURE.md)
- [Agent Behavior Documentation](AGENT_BEHAVIOR.md)
- [Configuration Guide](CONFIGURATION.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Design Document](../../../.kiro/specs/autonomous-ai-agents-refactor/design.md)
