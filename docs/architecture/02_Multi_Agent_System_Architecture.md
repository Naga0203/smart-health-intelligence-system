# Multi-Agent System Architecture

## Overview

The SymptomSense Health AI system employs a sophisticated multi-agent architecture where specialized agents collaborate to process health assessments. Each agent has a specific responsibility and communicates through a central orchestrator.

## Agent Architecture Pattern

### Design Philosophy

The multi-agent system follows these principles:

1. **Single Responsibility**: Each agent handles one specific task
2. **Loose Coupling**: Agents communicate through standardized interfaces
3. **Orchestrated Workflow**: Central coordinator manages agent execution
4. **Fail-Safe**: Individual agent failures don't crash the entire system
5. **Extensibility**: New agents can be added without modifying existing ones

## Agent Hierarchy

```
                    ┌─────────────────────┐
                    │  Orchestrator Agent │
                    │   (Coordinator)     │
                    └──────────┬──────────┘
                               │
                               │ Manages Workflow
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐      ┌───────────────┐     ┌───────────────┐
│  Validation   │      │   Predictor   │     │  Extraction   │
│    Agent      │      │     Agent     │     │     Agent     │
└───────────────┘      └───────────────┘     └───────────────┘
        │                      │                      │
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐      ┌───────────────┐     ┌───────────────┐
│  Explanation  │      │Recommendation │     │   Severity    │
│    Agent      │      │     Agent     │     │     Agent     │
└───────────────┘      └───────────────┘     └───────────────┘
        │                      │                      │
        │                      │                      │
        └──────────────────────┴──────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Firestore DB      │
                    │  (Data Storage)     │
                    └─────────────────────┘
```

## Agent Specifications

### 1. Orchestrator Agent

**Purpose**: Central coordinator that manages the entire assessment workflow

**Responsibilities**:
- Receive user input from API
- Validate request structure
- Coordinate agent execution sequence
- Aggregate results from all agents
- Handle errors and fallbacks
- Store final assessment in database
- Return comprehensive response

**Algorithm**:
```
FUNCTION run_pipeline(user_input):
    // Step 1: Initialize
    assessment_id = generate_uuid()
    context = create_context(user_input)
    
    // Step 2: Input Sanitization
    sanitized_input = sanitize_input(user_input)
    
    // Step 3: Validation
    validation_result = ValidationAgent.validate(sanitized_input)
    IF validation_result.is_invalid:
        RETURN error_response(validation_result.errors)
    
    // Step 4: Data Extraction (if report uploaded)
    IF user_input.has_medical_report:
        extracted_data = ExtractionAgent.extract(user_input.report)
        context.merge(extracted_data)
    
    // Step 5: Prediction
    prediction_result = PredictorAgent.predict(context)
    
    // Step 6: Severity Assessment
    severity_result = SeverityAgent.assess(prediction_result)
    
    // Step 7: Explanation Generation
    explanation = ExplanationAgent.explain(
        symptoms=context.symptoms,
        prediction=prediction_result,
        severity=severity_result
    )
    
    // Step 8: Treatment Recommendations
    recommendations = RecommendationAgent.recommend(
        condition=prediction_result.top_condition,
        severity=severity_result.level,
        user_profile=context.user_profile
    )
    
    // Step 9: Store Assessment
    storage_result = store_assessment(
        assessment_id=assessment_id,
        user_id=context.user_id,
        input_data=sanitized_input,
        prediction=prediction_result,
        explanation=explanation,
        recommendations=recommendations
    )
    
    // Step 10: Return Response
    RETURN {
        assessment_id: assessment_id,
        prediction: prediction_result,
        severity: severity_result,
        explanation: explanation,
        recommendations: recommendations,
        confidence: prediction_result.confidence,
        timestamp: current_timestamp()
    }
END FUNCTION
```

**Error Handling**:
- Graceful degradation if agents fail
- Fallback to partial results
- Comprehensive error logging
- User-friendly error messages

---

### 2. Validation Agent

**Purpose**: Validate and sanitize user input using AI-powered checks

**Responsibilities**:
- Validate symptom descriptions
- Check data completeness
- Detect contradictions
- Verify medical terminology
- Flag suspicious inputs

**Algorithm**:
```
FUNCTION validate(input_data):
    errors = []
    warnings = []
    
    // Basic Validation
    IF input_data.symptoms is empty:
        errors.append("Symptoms are required")
    
    IF input_data.age < 0 OR input_data.age > 150:
        errors.append("Invalid age")
    
    // AI-Powered Validation
    gemini_prompt = create_validation_prompt(input_data)
    ai_response = GeminiClient.generate(gemini_prompt)
    
    validation_result = parse_ai_validation(ai_response)
    
    IF validation_result.has_contradictions:
        warnings.append(validation_result.contradictions)
    
    IF validation_result.has_unclear_symptoms:
        warnings.append("Some symptoms are unclear")
    
    // Medical Terminology Check
    FOR symptom IN input_data.symptoms:
        IF is_medical_term(symptom):
            standardized = standardize_term(symptom)
            input_data.symptoms.replace(symptom, standardized)
    
    RETURN {
        is_valid: len(errors) == 0,
        errors: errors,
        warnings: warnings,
        sanitized_input: input_data
    }
END FUNCTION
```

**Validation Checks**:
1. **Required Fields**: Symptoms, age, gender
2. **Data Types**: Correct types for all fields
3. **Range Validation**: Age, vitals within acceptable ranges
4. **Logical Consistency**: No contradictory information
5. **Medical Terminology**: Proper medical terms used

---

### 3. Predictor Agent

**Purpose**: Predict potential health conditions using machine learning

**Responsibilities**:
- Preprocess input features
- Run ML model inference
- Calculate confidence scores
- Rank predictions
- Provide top-N predictions

**Algorithm**:
```
FUNCTION predict(context):
    // Step 1: Feature Extraction
    features = extract_features(context)
    
    // Step 2: Preprocessing
    normalized_features = normalize(features)
    encoded_features = encode_multi_hot(normalized_features)
    
    // Step 3: Model Inference
    model_input = prepare_tensor(encoded_features)
    raw_predictions = ml_model.forward(model_input)
    
    // Step 4: Post-processing
    probabilities = sigmoid(raw_predictions)
    sorted_predictions = sort_by_probability(probabilities)
    
    // Step 5: Confidence Calculation
    top_predictions = sorted_predictions[:5]
    confidence_score = calculate_confidence(top_predictions)
    
    // Step 6: Risk Assessment
    risk_level = assess_risk(top_predictions[0])
    
    RETURN {
        top_condition: top_predictions[0].name,
        probability: top_predictions[0].probability,
        all_predictions: top_predictions,
        confidence: confidence_score,
        risk_level: risk_level,
        risk_factors: identify_risk_factors(context, top_predictions[0])
    }
END FUNCTION
```

**ML Model Architecture**:
```
Input Layer (Multi-hot Encoded Features)
    │
    ▼
Dense Layer (512 neurons, ReLU)
    │
    ▼
Dropout (0.3)
    │
    ▼
Dense Layer (256 neurons, ReLU)
    │
    ▼
Dropout (0.3)
    │
    ▼
Dense Layer (128 neurons, ReLU)
    │
    ▼
Output Layer (N diseases, Sigmoid)
    │
    ▼
Multi-label Predictions
```

**Confidence Scoring Algorithm**:
```
FUNCTION calculate_confidence(predictions):
    top_prob = predictions[0].probability
    second_prob = predictions[1].probability
    
    // Separation between top predictions
    separation = top_prob - second_prob
    
    // Absolute confidence
    absolute_confidence = top_prob
    
    // Combined confidence score
    confidence = (0.7 * absolute_confidence) + (0.3 * separation)
    
    RETURN min(confidence, 1.0)
END FUNCTION
```

---

### 4. Explanation Agent

**Purpose**: Generate human-readable explanations using AI

**Responsibilities**:
- Explain prediction reasoning
- Describe symptoms-condition relationship
- Provide medical context
- Simplify medical jargon
- Generate patient-friendly language

**Algorithm**:
```
FUNCTION explain(symptoms, prediction, severity):
    // Step 1: Create Explanation Prompt
    prompt = """
    You are a medical AI assistant. Explain the following:
    
    Symptoms: {symptoms}
    Predicted Condition: {prediction.top_condition}
    Probability: {prediction.probability}
    Severity: {severity.level}
    
    Provide:
    1. Why these symptoms suggest this condition
    2. Key risk factors identified
    3. What the patient should know
    4. When to seek immediate care
    
    Use simple, patient-friendly language.
    """
    
    // Step 2: Generate AI Explanation
    ai_response = GeminiClient.generate(prompt)
    
    // Step 3: Parse and Structure
    explanation = parse_explanation(ai_response)
    
    // Step 4: Add Medical Context
    explanation.medical_context = get_condition_info(
        prediction.top_condition
    )
    
    // Step 5: Add Risk Drivers
    explanation.risk_drivers = identify_key_drivers(
        symptoms, prediction
    )
    
    RETURN {
        summary: explanation.summary,
        detailed_explanation: explanation.details,
        risk_drivers: explanation.risk_drivers,
        medical_context: explanation.medical_context,
        urgency_level: severity.urgency,
        next_steps: explanation.next_steps
    }
END FUNCTION
```

**Explanation Components**:
1. **Summary**: Brief overview (2-3 sentences)
2. **Detailed Explanation**: Comprehensive analysis
3. **Risk Drivers**: Key factors contributing to prediction
4. **Medical Context**: Background information about condition
5. **Next Steps**: Recommended actions

---

### 5. Recommendation Agent

**Purpose**: Generate personalized treatment recommendations

**Responsibilities**:
- Query treatment knowledge base
- Personalize recommendations
- Provide multi-system treatments (Allopathy, Ayurveda, Homeopathy, Lifestyle)
- Include dosage and precautions
- Consider user profile and contraindications

**Algorithm**:
```
FUNCTION recommend(condition, severity, user_profile):
    recommendations = {}
    
    // Step 1: Allopathic Treatment
    allopathy = TreatmentKB.query(
        system="allopathy",
        condition=condition,
        severity=severity
    )
    recommendations.allopathy = personalize(allopathy, user_profile)
    
    // Step 2: Ayurvedic Treatment
    ayurveda = TreatmentKB.query(
        system="ayurveda",
        condition=condition,
        severity=severity
    )
    recommendations.ayurveda = personalize(ayurveda, user_profile)
    
    // Step 3: Homeopathic Treatment
    homeopathy = TreatmentKB.query(
        system="homeopathy",
        condition=condition,
        severity=severity
    )
    recommendations.homeopathy = personalize(homeopathy, user_profile)
    
    // Step 4: Lifestyle Modifications
    lifestyle = generate_lifestyle_recommendations(
        condition=condition,
        user_profile=user_profile
    )
    recommendations.lifestyle = lifestyle
    
    // Step 5: Add Precautions
    FOR system IN recommendations:
        recommendations[system].precautions = get_precautions(
            condition, system, user_profile
        )
    
    // Step 6: Prioritize Recommendations
    recommendations.priority_order = prioritize_treatments(
        recommendations, severity
    )
    
    RETURN recommendations
END FUNCTION
```

**Personalization Factors**:
- Age and gender
- Existing conditions
- Medication allergies
- Pregnancy status
- Lifestyle preferences
- Cultural considerations

---

### 6. Extraction Agent

**Purpose**: Extract structured data from medical reports (PDF/Images)

**Responsibilities**:
- Process PDF documents
- Perform OCR on images
- Extract medical data (symptoms, vitals, lab results, medications, diagnoses)
- Validate extracted data
- Calculate confidence scores

**Algorithm**:
```
FUNCTION extract(report_file):
    // Step 1: File Type Detection
    file_type = detect_file_type(report_file)
    
    // Step 2: Text Extraction
    IF file_type == "PDF":
        raw_text = extract_pdf_text(report_file)
    ELSE IF file_type IN ["JPG", "PNG"]:
        raw_text = perform_ocr(report_file)
    ELSE:
        RETURN error("Unsupported file type")
    
    // Step 3: AI-Powered Extraction
    extraction_prompt = """
    Extract structured medical information from this report:
    
    {raw_text}
    
    Extract:
    - Symptoms
    - Vitals (BP, HR, temp, weight, height)
    - Lab Results (test name, value, unit, reference range)
    - Medications (name, dosage, frequency)
    - Diagnoses (condition, ICD code, status)
    
    Return as JSON with confidence scores.
    """
    
    ai_response = GeminiClient.generate(extraction_prompt)
    extracted_data = parse_json(ai_response)
    
    // Step 4: Validation
    validation_result = validate_extracted_data(extracted_data)
    
    // Step 5: Confidence Scoring
    confidence_scores = calculate_extraction_confidence(
        extracted_data, raw_text
    )
    
    RETURN {
        symptoms: extracted_data.symptoms,
        vitals: extracted_data.vitals,
        lab_results: extracted_data.lab_results,
        medications: extracted_data.medications,
        diagnoses: extracted_data.diagnoses,
        confidence_scores: confidence_scores,
        extraction_metadata: {
            ocr_used: file_type != "PDF",
            pages_processed: count_pages(report_file),
            extraction_time: elapsed_time
        }
    }
END FUNCTION
```

**OCR Processing**:
- Google Gemini Vision API for image-to-text
- Text preprocessing and cleaning
- Medical terminology recognition
- Layout analysis for structured data

---

### 7. Severity Agent

**Purpose**: Assess the severity and urgency of the predicted condition

**Responsibilities**:
- Calculate severity score
- Determine urgency level
- Identify red flags
- Recommend care level (self-care, primary care, emergency)

**Algorithm**:
```
FUNCTION assess(prediction_result):
    severity_score = 0
    red_flags = []
    
    // Factor 1: Condition Severity
    condition_severity = get_base_severity(
        prediction_result.top_condition
    )
    severity_score += condition_severity * 0.4
    
    // Factor 2: Symptom Severity
    symptom_severity = assess_symptom_severity(
        prediction_result.symptoms
    )
    severity_score += symptom_severity * 0.3
    
    // Factor 3: Prediction Confidence
    confidence_factor = prediction_result.confidence
    severity_score += confidence_factor * 0.2
    
    // Factor 4: Risk Factors
    risk_factor_score = count_risk_factors(
        prediction_result.risk_factors
    )
    severity_score += risk_factor_score * 0.1
    
    // Red Flag Detection
    red_flags = detect_red_flags(prediction_result.symptoms)
    IF len(red_flags) > 0:
        severity_score = max(severity_score, 0.8)
    
    // Determine Level
    IF severity_score >= 0.8 OR len(red_flags) > 0:
        level = "CRITICAL"
        urgency = "Seek emergency care immediately"
        care_level = "Emergency Room"
    ELSE IF severity_score >= 0.6:
        level = "HIGH"
        urgency = "Consult doctor within 24 hours"
        care_level = "Primary Care"
    ELSE IF severity_score >= 0.4:
        level = "MODERATE"
        urgency = "Schedule appointment within a week"
        care_level = "Primary Care"
    ELSE:
        level = "LOW"
        urgency = "Monitor symptoms, self-care"
        care_level = "Self-Care"
    
    RETURN {
        severity_score: severity_score,
        level: level,
        urgency: urgency,
        care_level: care_level,
        red_flags: red_flags,
        reasoning: explain_severity(severity_score, red_flags)
    }
END FUNCTION
```

**Red Flag Symptoms**:
- Chest pain
- Difficulty breathing
- Severe bleeding
- Loss of consciousness
- Severe head injury
- Stroke symptoms
- Severe allergic reaction

---

## Agent Communication Protocol

### Message Format

```json
{
  "agent_id": "string",
  "timestamp": "ISO 8601",
  "context": {
    "assessment_id": "uuid",
    "user_id": "string",
    "session_id": "string"
  },
  "input": {
    // Agent-specific input data
  },
  "output": {
    // Agent-specific output data
  },
  "status": "success | error | warning",
  "errors": [],
  "warnings": [],
  "execution_time_ms": 0
}
```

### Error Handling Strategy

1. **Graceful Degradation**: Continue with partial results if agent fails
2. **Retry Logic**: Retry failed agents with exponential backoff
3. **Fallback Mechanisms**: Use cached or default values
4. **Error Propagation**: Report errors to orchestrator
5. **User Notification**: Inform user of limitations

## Performance Optimization

### Caching Strategy

- **Prediction Cache**: Cache ML predictions for identical inputs
- **Treatment Cache**: Cache treatment recommendations
- **AI Response Cache**: Cache Gemini API responses
- **TTL**: 1 hour for most caches

### Parallel Execution

Agents that don't depend on each other run in parallel:
- Explanation Agent + Recommendation Agent (after prediction)
- Multiple treatment system queries (Allopathy, Ayurveda, Homeopathy)

### Async Processing

- Medical report extraction runs asynchronously
- User receives job ID and polls for completion
- Background processing doesn't block API response

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Maintained By**: SymptomSense Development Team
