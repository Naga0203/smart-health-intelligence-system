# Property-Based Tests for DataExtractionAgent

## Overview

This test suite implements property-based testing (PBT) for the DataExtractionAgent using the Hypothesis framework. Property-based tests validate universal correctness properties that should hold across all valid inputs, providing stronger guarantees than example-based unit tests.

## Properties Tested

### Property 1: Agent Migration Preserves Functionality (Requirement 1.6)

**Invariant**: For any valid input (symptoms, age, gender, disease), the migrated agent implementation should produce outputs with the same structure and key fields as the original implementation.

**What it validates**:
- Output structure consistency (success, data, features, confidence_scores)
- Presence of required fields (age, gender)
- Confidence scores exist for all extracted features
- Confidence values are in valid range [0.0, 1.0]
- Error handling for missing required fields

**Test methods**:
- `test_migrated_agent_preserves_output_structure`: Validates output structure across random inputs
- `test_migrated_agent_handles_missing_fields_consistently`: Validates error handling

### Property 32: Medication Extraction Includes Complete Details (Requirement 8.3)

**Invariant**: For any medical report containing medications, the extraction should include drug name, dosage, frequency, and duration (when available).

**What it validates**:
- Medications are extracted as a list
- Each medication has a non-empty drug name
- Dosage information is preserved when present
- Frequency information is preserved when present
- Duration information is preserved when present
- Confidence scores are provided for medication extraction

**Test methods**:
- `test_medication_extraction_includes_all_details`: Validates complete medication detail extraction

### Property 33: Diagnosis Extraction Includes Codes and Dates (Requirement 8.4)

**Invariant**: For any medical report containing diagnoses, the extraction should include condition name, ICD codes (when present), and diagnosis dates (when present).

**What it validates**:
- Diagnoses are extracted as a list
- Each diagnosis has a non-empty condition name
- ICD codes are preserved when present in input
- Diagnosis dates are preserved when present in input
- Confidence scores are provided for diagnosis extraction

**Test methods**:
- `test_diagnosis_extraction_includes_codes_and_dates`: Validates complete diagnosis detail extraction

### Property 34: Vital Signs Extraction Includes Units (Requirement 8.5)

**Invariant**: For any medical report containing vital signs, the extraction should include measurement values with appropriate units (mmHg, bpm, °F/°C, kg/lbs, etc.).

**What it validates**:
- Vital signs are extracted as a dictionary
- Each vital sign with a value includes appropriate units:
  - Blood pressure: mmHg
  - Heart rate: bpm
  - Temperature: °F or °C
  - Weight: kg or lbs
- Confidence scores are provided for vital signs extraction

**Test methods**:
- `test_vital_signs_extraction_includes_units`: Validates units are included with all vital sign measurements

### Property 35: Ambiguous Terms Trigger Clarification Searches (Requirement 8.6)

**Invariant**: For any extraction containing ambiguous medical terms, the agent should identify the terms, perform web searches to clarify them, and include clarifications in the output.

**What it validates**:
- Ambiguous medical terms are identified
- Web search is triggered for clarification
- Clarifications are included in the result
- Clarifications are non-empty strings
- Re-extraction with clarified terms can improve confidence

**Test methods**:
- `test_ambiguous_terms_trigger_web_search`: Validates web search is triggered for ambiguous terms
- `test_clarified_terms_improve_extraction_confidence`: Validates clarification improves extraction quality

## Running the Tests

### Run all property-based tests:
```bash
cd backend
pytest agents/test_data_extraction_properties.py -v -m pbt
```

### Run specific property test class:
```bash
pytest agents/test_data_extraction_properties.py::TestProperty1_MigrationPreservesFunctionality -v
```

### Run with more examples (default is 50-100):
```bash
pytest agents/test_data_extraction_properties.py -v --hypothesis-show-statistics
```

### Run with hypothesis verbosity:
```bash
pytest agents/test_data_extraction_properties.py -v --hypothesis-verbosity=verbose
```

## Test Data Generation

The tests use Hypothesis strategies to generate random but valid test data:

- **symptoms_strategy**: Generates lists of 1-10 symptoms (3-50 characters each)
- **age_strategy**: Generates ages between 1-120
- **gender_strategy**: Generates "male", "female", or "other"
- **disease_strategy**: Generates "diabetes", "heart_disease", or "hypertension"
- **medication_strategy**: Generates medication dictionaries with name, dosage, frequency, duration
- **diagnosis_strategy**: Generates diagnosis dictionaries with condition, ICD code, date
- **vital_signs_strategy**: Generates vital signs with appropriate units
- **ambiguous_terms_strategy**: Generates lists of medical abbreviations and ambiguous terms

## Mocking Strategy

The tests use mocking to isolate the DataExtractionAgent from external dependencies:

1. **LangChain Gemini Client**: Mocked to avoid actual API calls
2. **Web Search Tool**: Mocked to return predefined search results
3. **Extraction Chain**: Mocked to return controlled JSON responses
4. **Monitoring**: Disabled for tests

## Expected Behavior

### Successful Extraction
When extraction succeeds, the result should have:
```python
{
    "success": True,
    "data": {
        "features": {...},
        "confidence_scores": {...},
        "extraction_confidence": 0.0-1.0,
        "missing_features": [...],
        "ambiguous_terms": [...],
        "extraction_method": "langchain_gemini_enhanced"
    }
}
```

### Failed Extraction
When extraction fails (e.g., missing required fields), the result should have:
```python
{
    "success": False,
    "message": "Error description",
    "metadata": {
        "missing_fields": [...]
    }
}
```

## Confidence Scoring

All confidence scores must be in the range [0.0, 1.0]:
- 1.0: High confidence (e.g., explicitly provided age, gender)
- 0.8-0.9: Good confidence (e.g., direct symptom mapping, extracted medications)
- 0.6-0.7: Medium confidence (e.g., fuzzy matching)
- 0.3-0.5: Low confidence (e.g., default values, fallback extraction)

## Integration with CI/CD

These property-based tests should be run as part of the CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run Property-Based Tests
  run: |
    cd backend
    pytest agents/test_data_extraction_properties.py -v -m pbt --hypothesis-show-statistics
```

## Troubleshooting

### Tests are slow
Property-based tests generate many examples. To speed up during development:
```python
@settings(max_examples=10)  # Reduce from default 50-100
```

### Flaky tests
If tests fail intermittently, check:
1. Mock setup is consistent
2. No shared state between tests
3. Hypothesis seed for reproducibility: `--hypothesis-seed=12345`

### Hypothesis finds a failing example
Hypothesis will print the minimal failing example. Use it to:
1. Add it as a regression test
2. Fix the underlying issue
3. Re-run to verify the fix

## References

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Property-Based Testing Guide](https://hypothesis.works/articles/what-is-property-based-testing/)
- Requirements Document: `.kiro/specs/autonomous-ai-agents-refactor/requirements.md`
- Design Document: `.kiro/specs/autonomous-ai-agents-refactor/design.md`
