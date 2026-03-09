# System Architecture Documentation

## Overview

The autonomous AI agents system is a health intelligence backend powered by LangChain framework and Gemini AI. The system processes medical reports, extracts structured data, and provides personalized health assessments through a coordinated network of specialized autonomous agents.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Layer                                │
│                    (Django REST Framework)                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                   Orchestrator Agent                             │
│  - Autonomous agent selection                                    │
│  - Multi-agent coordination                                      │
│  - Parallel execution management                                 │
│  - Result aggregation                                            │
└─────┬────────────────────────────────────────────────────┬──────┘
      │                                                     │
      ├─────────────────┬───────────────────┬──────────────┤
      │                 │                   │              │
┌─────▼─────┐  ┌───────▼────────┐  ┌──────▼──────┐  ┌───▼────┐
│   Data    │  │   Enhanced     │  │  Severity   │  │  ...   │
│Extraction │  │  Extraction    │  │   Agent     │  │ Agents │
│  Agent    │  │    Agent       │  │             │  │        │
└─────┬─────┘  └───────┬────────┘  └──────┬──────┘  └───┬────┘
      │                │                   │              │
      └────────────────┴───────────────────┴──────────────┘
                         │
      ┌──────────────────┴──────────────────────────────────┐
      │                                                      │
┌─────▼──────────┐  ┌──────────────┐  ┌──────────────────┐
│  Web Search    │  │   Context    │  │    Monitoring    │
│     Tool       │  │   Manager    │  │     Service      │
└────────────────┘  └──────────────┘  └──────────────────┘
      │
┌─────▼──────────────────────────────────────────────────────┐
│              External Services                              │
│  - Gemini AI (LLM & Vision)                                │
│  - Search APIs                                              │
│  - Firebase Database                                        │
└─────────────────────────────────────────────────────────────┘
```

### Agent Architecture

Each agent follows a layered architecture with shared infrastructure:

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Layer                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  process() - Main agent logic                        │  │
│  │  - Input validation                                   │  │
│  │  - Decision making                                    │  │
│  │  - LangChain chain execution                         │  │
│  │  - Output formatting                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  Capability Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Web Search   │  │  Decision    │  │  Context Access  │ │
│  │    Tool      │  │   Engine     │  │                  │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│               Infrastructure Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │   Circuit    │  │    Retry     │  │     Safety       │ │
│  │   Breaker    │  │    Logic     │  │   Guardrails     │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │  Monitoring  │  │    Cache     │  │     Logging      │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Component Interactions

### Health Assessment Flow

1. **Request Reception**: API receives health assessment request with medical report
2. **Orchestration**: OrchestratorAgent analyzes input and selects required agents
3. **Parallel Execution**: Independent agents execute concurrently
4. **Context Sharing**: Agents share intermediate results through ContextManager
5. **Sequential Execution**: Dependent agents execute after prerequisites complete
6. **Result Aggregation**: Orchestrator combines all agent outputs
7. **Safety Validation**: SafetyGuardrails validate final response
8. **Response Delivery**: API returns comprehensive health assessment

### Web Search Flow

1. **Search Request**: Agent needs external information
2. **Decision**: DecisionEngine determines if web search is needed
3. **Cache Check**: WebSearchTool checks cache for recent results
4. **Rate Limiting**: RateLimiter validates request is within limits
5. **Source Filtering**: MedicalSourceFilter ensures reliable sources
6. **Search Execution**: External search API called through CircuitBreaker
7. **Result Caching**: Results cached with TTL
8. **Citation Building**: Sources formatted with proper citations
9. **Result Return**: Validated results returned to agent

### OCR Processing Flow

1. **Image Upload**: Medical report image received
2. **Format Validation**: GeminiOCRService validates image format
3. **Vision API Call**: Image sent to Gemini Vision through CircuitBreaker
4. **Text Extraction**: Raw text extracted with confidence scores
5. **Structure Preservation**: Document structure maintained
6. **Structured Data Extraction**: Lab results, medications, vitals extracted
7. **Table/Chart Processing**: Visual elements processed separately
8. **Result Compilation**: All extracted data compiled with metadata
9. **Confidence Scoring**: Overall confidence calculated
10. **Result Return**: OCRResult returned to agent

### Error Handling Flow

1. **Error Detection**: Operation fails (API error, timeout, invalid data)
2. **Error Classification**: Error categorized (retryable, circuit-breaking, fatal)
3. **Retry Logic**: Retryable errors trigger exponential backoff retry
4. **Circuit Breaker**: Repeated failures open circuit breaker
5. **Graceful Degradation**: Fallback to cached data or partial results
6. **Error Logging**: Detailed error logged with context
7. **Monitoring Alert**: Critical errors trigger monitoring alerts
8. **User Response**: Appropriate error response returned to user

## Data Flow

### Input Data Flow

```
Medical Report (Image/PDF)
    │
    ├─> EnhancedExtractionAgent (OCR)
    │       │
    │       └─> Raw Text + Structured Data
    │               │
    │               └─> Context Manager
    │
    └─> DataExtractionAgent (Structured Extraction)
            │
            └─> Lab Results, Medications, Vitals, Diagnoses
                    │
                    └─> Context Manager
```

### Processing Data Flow

```
Context Manager (Shared State)
    │
    ├─> SeverityAgent
    │       └─> Severity Assessment + Emergency Flags
    │
    ├─> TreatmentExplorationAgent
    │       └─> Treatment Options (Web Search)
    │
    ├─> RecommendationAgent
    │       └─> Personalized Recommendations (Web Search)
    │
    ├─> LifestyleAgent
    │       └─> Lifestyle Interventions (Web Search)
    │
    ├─> ExplanationAgent
    │       └─> Medical Explanations (Web Search)
    │
    ├─> ValidationAgent
    │       └─> Data Validation Results
    │
    └─> ReflectionAgent
            └─> Quality Assessment
```

### Output Data Flow

```
All Agent Results
    │
    └─> OrchestratorAgent (Aggregation)
            │
            └─> Combined Assessment
                    │
                    ├─> SafetyGuardrails (Validation)
                    │       └─> Filtered Response
                    │
                    ├─> MonitoringService (Metrics)
                    │
                    └─> API Response
```

## Key Design Patterns

### 1. Circuit Breaker Pattern

Prevents cascading failures by opening circuit after repeated failures:

- **Closed State**: Normal operation, requests pass through
- **Open State**: After threshold failures, requests fail fast
- **Half-Open State**: After timeout, test requests allowed

### 2. Retry with Exponential Backoff

Handles transient failures gracefully:

- First retry: 1 second delay
- Second retry: 2 second delay
- Third retry: 4 second delay
- Maximum 3 retries before failure

### 3. Cache-Aside Pattern

Improves performance and reduces API costs:

- Check cache before external calls
- Populate cache on cache miss
- Expire cache entries after TTL
- Share cache across agents in session

### 4. Observer Pattern

Monitoring system observes all agent operations:

- Agents emit events (execution, decision, search)
- MonitoringService subscribes to events
- Metrics collected and aggregated
- Alerts triggered on anomalies

### 5. Strategy Pattern

Decision engine selects strategies dynamically:

- Multiple search strategies available
- Decision engine selects based on context
- Fallback strategies on failure
- Strategies can be added without code changes

### 6. Template Method Pattern

BaseHealthAgent defines agent lifecycle:

- Common initialization in base class
- Abstract process() method for agent logic
- Common error handling and monitoring
- Consistent behavior across all agents

## Scalability Considerations

### Horizontal Scaling

- Stateless agent design allows multiple instances
- Context stored in shared cache (Redis/Firebase)
- Load balancer distributes requests
- No session affinity required

### Vertical Scaling

- Parallel agent execution utilizes multiple cores
- Async I/O for external API calls
- Connection pooling for database access
- Lazy initialization reduces memory footprint

### Performance Optimization

- **Caching**: Web search results, treatment information, OCR results
- **Batching**: Multiple Gemini API calls batched when possible
- **Streaming**: Long-running operations stream partial results
- **Lazy Loading**: Agents initialized on first use
- **Connection Pooling**: Reuse connections to external services

### Cost Optimization

- **Cache Hit Rate**: Target 60%+ cache hit rate for web searches
- **Token Optimization**: Minimize Gemini API token usage
- **Rate Limiting**: Prevent excessive API calls
- **Circuit Breakers**: Fail fast to avoid wasted API calls
- **Monitoring**: Track costs per agent and operation

## Security Architecture

### API Key Management

- Keys stored in environment variables or secure vault
- Never logged or exposed in responses
- Key access logged for audit
- Support for key rotation without downtime

### Data Privacy

- Patient data sanitized in logs
- PII removed from monitoring metrics
- Secure transmission (HTTPS/TLS)
- Data retention policies enforced

### Input Validation

- All external data validated before processing
- Image format validation for OCR
- Medical data schema validation
- SQL injection prevention
- XSS prevention in responses

### Safety Guardrails

- Prevent specific medical diagnoses
- Prevent medication dosage recommendations
- Add medical disclaimers to all responses
- Detect emergency indicators
- Filter unreliable information sources

## Deployment Architecture

### Development Environment

- Local Django development server
- Mock external services for testing
- SQLite database
- File-based cache

### Staging Environment

- Docker containers
- Firebase database
- Redis cache
- Real external APIs with test keys
- Feature flags for gradual rollout

### Production Environment

- Kubernetes cluster for orchestration
- Load balancer for traffic distribution
- Firebase production database
- Redis cluster for distributed cache
- CDN for static assets
- Monitoring and alerting infrastructure
- Backup and disaster recovery

## Monitoring and Observability

### Metrics Collected

- **Agent Metrics**: Execution time, success rate, failure rate
- **API Metrics**: Request count, response time, error rate
- **Search Metrics**: Query count, cache hit rate, source distribution
- **Cost Metrics**: Gemini token usage, search API calls
- **Quality Metrics**: Confidence scores, validation results

### Logging Levels

- **DEBUG**: Detailed execution traces
- **INFO**: Agent decisions, search queries, normal operations
- **WARNING**: Retries, degraded performance, cache misses
- **ERROR**: Operation failures, validation errors
- **CRITICAL**: System failures, security violations

### Alerting Thresholds

- Error rate > 5%: Warning alert
- Error rate > 10%: Critical alert
- Response time > 30s: Warning alert
- Response time > 60s: Critical alert
- Circuit breaker open: Critical alert
- Cost spike > 50% above baseline: Warning alert

## Future Enhancements

### Planned Improvements

1. **Multi-Language Support**: Support for non-English medical reports
2. **Voice Input**: Audio transcription for voice-based reports
3. **Real-Time Collaboration**: Multiple agents working on same report
4. **Advanced Analytics**: Trend analysis across multiple reports
5. **Federated Learning**: Privacy-preserving model improvements
6. **Edge Deployment**: On-device processing for sensitive data

### Scalability Roadmap

1. **Phase 1**: Single-region deployment (current)
2. **Phase 2**: Multi-region deployment with geo-routing
3. **Phase 3**: Edge computing for low-latency processing
4. **Phase 4**: Federated architecture for data sovereignty

## References

- [Agent Behavior Documentation](AGENT_BEHAVIOR.md)
- [Configuration Guide](CONFIGURATION.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Design Document](../../../.kiro/specs/autonomous-ai-agents-refactor/design.md)
- [Requirements Document](../../../.kiro/specs/autonomous-ai-agents-refactor/requirements.md)
