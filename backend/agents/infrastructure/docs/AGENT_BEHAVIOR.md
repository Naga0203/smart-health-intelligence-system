# Agent Behavior Documentation

## Overview

This document describes the capabilities, decision-making logic, web search strategies, and error handling for each autonomous agent in the health intelligence system.

## Agent Catalog

### 1. OrchestratorAgent

**Purpose**: Coordinates multiple specialized agents to complete comprehensive health assessments.

**Capabilities**:
- Autonomous agent selection based on input data characteristics
- Parallel execution of independent agents
- Sequential execution of dependent agents
- Context sharing between agents
- Result aggregation and synthesis
- Timeout management
- Failure recovery

**Decision-Making Logic**:

```python
# Agent Selection Decision
if has_medical_report_image(input_data):
    agents.append(EnhancedExtractionAgent)
    
if has_structured_medical_data(input_data):
    agents.append(DataExtractionAgent)
    
if has_lab_results(input_data) or has_symptoms(input_data):
    agents.append(SeverityAgent)
    agents.append(TreatmentExplorationAgent)
    agents.append(RecommendationAgent)
    
if has_lifestyle_data(input_data):
    agents.append(LifestyleAgent)
    
# Always include validation and reflection
agents.append(ValidationAgent)
agents.append(ReflectionAgent)
agents.append(ExplanationAgent)

# Determine execution order
parallel_group_1 = [EnhancedExtractionAgent, DataExtractionAgent]
parallel_group_2 = [SeverityAgent, TreatmentExplorationAgent, LifestyleAgent]
parallel_group_3 = [RecommendationAgent, ExplanationAgent]
sequential = [ValidationAgent, ReflectionAgent]
```

**Error Handling**:
- Agent timeout: Continue with available results, log timeout
- Agent failure: Retry once, then continue without that agent's results
- Critical agent failure (extraction): Return error to user
- Partial results: Return with warning about incomplete assessment

**Monitoring**:
- Total orchestration time
- Number of agents invoked
- Parallel vs sequential execution time
- Agent failure rates
- Context size

---

### 2. DataExtractionAgent

**Purpose**: Extract structured medical data from text using Gemini AI.

**Capabilities**:
- Extract lab results (test names, values, units, reference ranges)
- Extract medications (drug names, dosages, frequencies, durations)
- Extract diagnoses (conditions, ICD codes, dates)
- Extract vital signs (BP, heart rate, temperature, weight with units)
- Clarify ambiguous medical terminology via web search
- Provide confidence scores for extractions

**Decision-Making Logic**:

```python
# Ambiguous Term Detection
if confidence_score < 0.7:
    if is_medical_term(term):
        # Search for clarification
        clarification = web_search(f"medical term {term} definition")
        re_extract_with_context(clarification)
    else:
        # Flag for human review
        flag_for_review(term, confidence_score)

# Extraction Strategy Selection
if has_structured_format(text):
    use_pattern_extraction()
else:
    use_llm_extraction()
```

**Web Search Strategy**:
- **Trigger**: Ambiguous medical terminology (confidence < 0.7)
- **Query Format**: "medical term [term] definition"
- **Sources**: Medical dictionaries, PubMed, medical encyclopedias
- **Usage**: Provide context to LLM for re-extraction

**Error Handling**:
- Invalid input: Return validation error
- Extraction failure: Return partial results with low confidence flags
- Web search failure: Continue with original extraction, flag uncertainty
- Timeout: Return partial extractions completed so far

**Output Format**:
```json
{
  "lab_results": [
    {
      "test_name": "Hemoglobin A1C",
      "value": 6.5,
      "unit": "%",
      "reference_range": "4.0-5.6",
      "confidence": 0.95
    }
  ],
  "medications": [
    {
      "drug_name": "Metformin",
      "dosage": "500mg",
      "frequency": "twice daily",
      "duration": "ongoing",
      "confidence": 0.90
    }
  ],
  "vital_signs": {
    "blood_pressure": "120/80 mmHg",
    "heart_rate": "72 bpm",
    "confidence": 0.92
  }
}
```

---

### 3. EnhancedExtractionAgent

**Purpose**: Extract text and structured data from medical report images using Gemini Vision.

**Capabilities**:
- OCR text extraction from images (JPEG, PNG, PDF, TIFF)
- Preserve document structure (sections, tables, lists)
- Extract data from charts and graphs
- Extract data from tables
- Handle handwritten notes
- Identify report type (lab, radiology, pathology)
- Extract header information (dates, patient ID, provider)

**Decision-Making Logic**:

```python
# Report Type Detection
report_type = identify_report_type(image)

if report_type == "lab_report":
    focus_on_tables_and_values()
elif report_type == "radiology":
    focus_on_findings_and_impressions()
elif report_type == "pathology":
    focus_on_diagnosis_and_staging()

# Extraction Strategy
if has_tables(image):
    extract_tables_separately()
    
if has_charts(image):
    extract_chart_data_points()
    
if has_handwriting(image):
    use_handwriting_extraction()
```

**Error Handling**:
- Unsupported format: Return format error
- Corrupted image: Return corruption error with details
- Low confidence extraction: Flag sections for review
- Vision API failure: Retry with exponential backoff, then fail gracefully

**Output Format**:
```json
{
  "text": "Full extracted text...",
  "report_type": "lab_report",
  "confidence": 0.88,
  "structured_data": {
    "header": {
      "patient_id": "12345",
      "date": "2024-01-15",
      "provider": "Dr. Smith"
    },
    "tables": [...],
    "charts": [...]
  },
  "low_confidence_sections": [...]
}
```

---

### 4. SeverityAgent

**Purpose**: Assess severity of health conditions and detect emergencies.

**Capabilities**:
- Assess severity levels (low, moderate, high, critical)
- Detect emergency medical indicators
- Search for severity criteria and clinical guidelines
- Escalate critical situations for human review
- Provide urgency recommendations

**Decision-Making Logic**:

```python
# Emergency Detection
emergency_keywords = [
    'chest pain', 'difficulty breathing', 'severe bleeding',
    'loss of consciousness', 'stroke symptoms', 'heart attack'
]

if any(keyword in symptoms for keyword in emergency_keywords):
    severity = "CRITICAL"
    escalate_to_human_review()
    recommend_immediate_medical_attention()
    
# Severity Assessment
if has_abnormal_vitals(data):
    search_severity_criteria(condition)
    assess_with_clinical_guidelines()
    
if multiple_risk_factors(data):
    increase_severity_level()
```

**Web Search Strategy**:
- **Trigger**: Abnormal lab values, concerning symptoms
- **Query Format**: "[condition] severity criteria clinical guidelines"
- **Sources**: Clinical practice guidelines, medical associations
- **Usage**: Inform severity assessment with current standards

**Error Handling**:
- Missing data: Request additional information or assess with available data
- Conflicting indicators: Search for tiebreaker criteria
- Search failure: Use conservative severity assessment

**Output Format**:
```json
{
  "severity": "moderate",
  "emergency_detected": false,
  "urgency": "schedule_appointment_within_week",
  "reasoning": "Elevated A1C indicates uncontrolled diabetes...",
  "escalated": false
}
```

---

### 5. TreatmentExplorationAgent

**Purpose**: Provide current treatment information from multiple medical systems.

**Capabilities**:
- Search for treatment guidelines (allopathy, ayurveda, homeopathy)
- Synthesize information from multiple sources
- Include evidence levels and clinical trial data
- Search for drug interactions and contraindications
- Cite all sources
- Add medical disclaimers

**Decision-Making Logic**:

```python
# Multi-System Search
for medical_system in ['allopathy', 'ayurveda', 'homeopathy']:
    treatments = search_treatments(condition, medical_system)
    all_treatments.extend(treatments)

# Source Selection
prioritize_by_evidence_level(all_treatments)
prioritize_by_source_quality(all_treatments)

# Drug Interaction Check
if has_current_medications(user_profile):
    for treatment in all_treatments:
        interactions = search_drug_interactions(
            treatment.medications,
            user_profile.current_medications
        )
        treatment.add_interactions(interactions)
```

**Web Search Strategy**:
- **Trigger**: Every treatment query (no static data)
- **Query Formats**:
  - "clinical practice guidelines [condition] treatment"
  - "[condition] allopathic treatment evidence"
  - "[condition] ayurvedic treatment"
  - "drug interactions [drug1] [drug2]"
- **Sources**: Clinical guidelines, PubMed, medical associations, ayurvedic databases
- **Caching**: Cache treatment info for 24 hours

**Error Handling**:
- No results found: Broaden search, try alternative terms
- Conflicting information: Present multiple viewpoints with evidence levels
- Search failure: Return cached results if available, otherwise error

**Output Format**:
```json
{
  "treatments": [
    {
      "medical_system": "allopathy",
      "treatment": "Metformin + lifestyle modification",
      "evidence_level": "Level A - Strong evidence",
      "sources": ["ADA Guidelines 2024", "NEJM 2023"],
      "interactions": ["None with current medications"],
      "contraindications": []
    }
  ],
  "disclaimer": "This information is for educational purposes..."
}
```

---

### 6. RecommendationAgent

**Purpose**: Generate personalized health recommendations based on user profile and current guidelines.

**Capabilities**:
- Search for current clinical guidelines
- Personalize based on age, gender, medical history
- Search for contraindications specific to user profile
- Prioritize by clinical importance and evidence strength
- Include actionable steps
- Detect medication conflicts
- Cite sources

**Decision-Making Logic**:

```python
# Personalization
recommendations = generate_base_recommendations(health_data)

for rec in recommendations:
    # Check contraindications
    contraindications = search_contraindications(
        rec,
        user_profile.age,
        user_profile.gender,
        user_profile.conditions,
        user_profile.medications
    )
    
    if contraindications:
        rec.flag_contraindication(contraindications)
        rec.adjust_or_remove()
    
    # Add personalized context
    rec.personalize(user_profile)

# Prioritization
prioritize_by_clinical_importance(recommendations)
prioritize_by_evidence_strength(recommendations)
prioritize_by_actionability(recommendations)
```

**Web Search Strategy**:
- **Trigger**: Every recommendation generation
- **Query Formats**:
  - "clinical guidelines [condition] management"
  - "[intervention] contraindications [age/gender/condition]"
  - "[recommendation] evidence-based practice"
- **Sources**: Clinical practice guidelines, systematic reviews, medical associations
- **Caching**: Cache guidelines for 7 days

**Error Handling**:
- Contraindication detected: Remove or modify recommendation
- Medication conflict: Flag prominently, suggest alternatives
- Search failure: Use cached guidelines, note information may be outdated

**Output Format**:
```json
{
  "recommendations": [
    {
      "priority": 1,
      "category": "medication_management",
      "recommendation": "Discuss A1C results with physician",
      "actionable_steps": [
        "Schedule appointment within 2 weeks",
        "Bring current medication list",
        "Prepare questions about treatment options"
      ],
      "evidence": "ADA Standards of Care 2024",
      "personalization": "Given your age (55) and current medications...",
      "conflicts": []
    }
  ]
}
```

---

### 7. LifestyleAgent

**Purpose**: Provide evidence-based lifestyle intervention recommendations.

**Capabilities**:
- Search for evidence-based lifestyle interventions
- Personalize based on user profile and preferences
- Cover diet, exercise, stress management, sleep
- Cite sources for all recommendations
- Provide actionable, specific guidance

**Decision-Making Logic**:

```python
# Intervention Selection
if has_diabetes(health_data):
    interventions.extend(search_diabetes_lifestyle_interventions())
    
if has_hypertension(health_data):
    interventions.extend(search_hypertension_lifestyle_interventions())

# Personalization
for intervention in interventions:
    if conflicts_with_profile(intervention, user_profile):
        modify_or_remove(intervention)
    
    add_specific_guidance(intervention, user_profile)
```

**Web Search Strategy**:
- **Trigger**: Every lifestyle recommendation request
- **Query Formats**:
  - "evidence-based lifestyle interventions [condition]"
  - "[condition] diet recommendations clinical guidelines"
  - "[condition] exercise guidelines"
- **Sources**: Clinical guidelines, systematic reviews, nutrition databases
- **Caching**: Cache interventions for 7 days

**Output Format**:
```json
{
  "lifestyle_recommendations": [
    {
      "category": "diet",
      "recommendation": "Mediterranean diet pattern",
      "specific_guidance": [
        "Include 2-3 servings of vegetables per meal",
        "Choose whole grains over refined grains",
        "Limit added sugars to <25g per day"
      ],
      "evidence": "ADA Nutrition Therapy 2024",
      "expected_benefit": "May reduce A1C by 0.5-1.0%"
    }
  ]
}
```

---

### 8. ExplanationAgent

**Purpose**: Provide clear explanations of medical terms and concepts.

**Capabilities**:
- Explain medical terminology in plain language
- Search for current medical explanations
- Provide context and relevance
- Cite sources
- Include safety disclaimers

**Web Search Strategy**:
- **Trigger**: Complex medical terms or concepts
- **Query Formats**:
  - "[medical term] explanation patient education"
  - "[medical concept] simple explanation"
- **Sources**: Patient education resources, medical encyclopedias
- **Caching**: Cache explanations for 30 days

**Output Format**:
```json
{
  "explanations": [
    {
      "term": "Hemoglobin A1C",
      "simple_explanation": "A blood test that shows your average blood sugar level over the past 2-3 months",
      "relevance": "Used to diagnose and monitor diabetes",
      "source": "ADA Patient Education 2024"
    }
  ]
}
```

---

### 9. ValidationAgent

**Purpose**: Validate data quality and consistency.

**Capabilities**:
- Validate data completeness
- Check for inconsistencies
- Verify data ranges and formats
- Flag suspicious values
- Search for validation criteria when needed

**Decision-Making Logic**:

```python
# Completeness Check
required_fields = get_required_fields(data_type)
missing_fields = [f for f in required_fields if f not in data]

# Consistency Check
if has_conflicting_values(data):
    flag_inconsistency(data)

# Range Validation
for field, value in data.items():
    if not in_valid_range(field, value):
        if should_search_range(field):
            valid_range = search_valid_range(field)
            revalidate(field, value, valid_range)
        else:
            flag_out_of_range(field, value)
```

**Output Format**:
```json
{
  "validation_result": "passed_with_warnings",
  "warnings": [
    "Blood pressure value unusually high - verify accuracy"
  ],
  "errors": [],
  "completeness": 0.95
}
```

---

### 10. ReflectionAgent

**Purpose**: Self-evaluate the quality of agent outputs.

**Capabilities**:
- Assess output completeness
- Evaluate output coherence
- Check citation quality
- Verify safety compliance
- Provide quality scores

**Decision-Making Logic**:

```python
# Quality Assessment
quality_score = 0.0

# Completeness
if all_required_sections_present(output):
    quality_score += 0.3
    
# Coherence
if output_is_coherent(output):
    quality_score += 0.3
    
# Citations
if all_claims_cited(output):
    quality_score += 0.2
    
# Safety
if safety_compliant(output):
    quality_score += 0.2
else:
    flag_safety_issue(output)
```

**Output Format**:
```json
{
  "quality_score": 0.85,
  "completeness": 0.90,
  "coherence": 0.88,
  "citation_quality": 0.80,
  "safety_compliance": 1.0,
  "issues": [],
  "suggestions": ["Consider adding more specific guidance for diet recommendations"]
}
```

---

## Common Behaviors

### All Agents

**Initialization**:
- Load configuration from environment
- Initialize Gemini client
- Initialize web search tool
- Initialize monitoring
- Set up circuit breakers

**Execution Pattern**:
1. Validate input
2. Check context for relevant information
3. Make autonomous decisions
4. Execute LangChain chains
5. Handle errors with retry logic
6. Log decisions and metrics
7. Return formatted output

**Error Handling**:
- Retry transient failures (3 attempts, exponential backoff)
- Circuit breaker for repeated failures
- Graceful degradation when services unavailable
- Detailed error logging
- User-friendly error messages

**Monitoring**:
- Execution time tracking
- Success/failure rate tracking
- Decision logging
- Resource usage tracking
- Cost tracking (API calls, tokens)

**Safety**:
- Input validation
- Output sanitization
- Medical disclaimer inclusion
- Emergency detection
- Source reliability verification

---

## Decision Engine

The DecisionEngine is used by all agents for autonomous decision-making.

**Capabilities**:
- Decide next action from multiple options
- Decide if web search is needed
- Decide if escalation is required
- Resolve conflicts between sources
- Select best source from multiple options

**Decision Process**:
1. Analyze current context
2. Evaluate available options
3. Use LLM reasoning to assess each option
4. Select best option based on criteria
5. Log decision and reasoning
6. Return decision

**Example Decision**:
```python
context = {
    "user_query": "treatment for diabetes",
    "cached_results": None,
    "last_search": None
}

options = ["use_cached_results", "perform_web_search", "request_more_info"]

decision = decision_engine.decide_next_action(context, options)
# Returns: "perform_web_search"
# Reasoning: "No cached results available and query requires current information"
```

---

## Web Search Strategies

### Medical Literature Search
- **Use Case**: Treatment information, clinical guidelines
- **Sources**: PubMed, medical journals, clinical practice guidelines
- **Query Construction**: Include medical terms, "clinical guidelines", "evidence-based"
- **Result Filtering**: Peer-reviewed sources, recent publications (< 5 years)

### Drug Information Search
- **Use Case**: Drug interactions, contraindications, side effects
- **Sources**: Drug databases, FDA, pharmaceutical references
- **Query Construction**: Drug names, "interactions", "contraindications"
- **Result Filtering**: Official drug information sources

### Patient Education Search
- **Use Case**: Medical term explanations, condition information
- **Sources**: Patient education resources, medical encyclopedias
- **Query Construction**: Medical term + "patient education" or "simple explanation"
- **Result Filtering**: Reputable patient education sites

### Lifestyle Intervention Search
- **Use Case**: Diet, exercise, lifestyle recommendations
- **Sources**: Clinical guidelines, systematic reviews, nutrition databases
- **Query Construction**: Condition + "lifestyle interventions" or "diet recommendations"
- **Result Filtering**: Evidence-based sources, clinical guidelines

---

## Error Recovery Strategies

### Retry Strategy
```python
attempt = 0
while attempt < max_retries:
    try:
        result = operation()
        return result
    except RetryableError:
        attempt += 1
        wait_time = 2 ** attempt  # Exponential backoff
        time.sleep(wait_time)
        
raise MaxRetriesExceeded()
```

### Fallback Strategy
```python
try:
    result = primary_operation()
except PrimaryOperationFailed:
    try:
        result = fallback_operation()
    except FallbackOperationFailed:
        result = default_response()
        
return result
```

### Circuit Breaker Strategy
```python
if circuit_breaker.is_open():
    return cached_result_or_error()
    
try:
    result = external_service_call()
    circuit_breaker.record_success()
    return result
except ServiceError:
    circuit_breaker.record_failure()
    raise
```

---

## Performance Characteristics

### Expected Response Times

| Agent | Typical | Maximum |
|-------|---------|---------|
| DataExtractionAgent | 2-5s | 10s |
| EnhancedExtractionAgent | 5-10s | 30s |
| SeverityAgent | 1-3s | 10s |
| TreatmentExplorationAgent | 5-15s | 30s |
| RecommendationAgent | 5-15s | 30s |
| LifestyleAgent | 3-8s | 20s |
| ExplanationAgent | 2-5s | 10s |
| ValidationAgent | 1-2s | 5s |
| ReflectionAgent | 2-4s | 10s |
| OrchestratorAgent | 15-45s | 120s |

### Resource Usage

- **Memory**: 200-500 MB per agent instance
- **CPU**: 1-2 cores per agent during execution
- **Network**: 1-10 MB per request (varies with image size)
- **API Calls**: 2-10 Gemini calls, 0-5 search calls per agent

### Cost Estimates

- **Gemini API**: $0.01-0.05 per health assessment
- **Search API**: $0.001-0.01 per health assessment
- **Total**: $0.02-0.10 per health assessment

---

## References

- [Architecture Documentation](ARCHITECTURE.md)
- [Configuration Guide](CONFIGURATION.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Design Document](../../../.kiro/specs/autonomous-ai-agents-refactor/design.md)
