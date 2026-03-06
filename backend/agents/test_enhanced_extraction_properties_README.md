# Property-Based Tests for EnhancedExtractionAgent

## Overview

This test suite validates universal correctness properties of the EnhancedExtractionAgent using property-based testing with Hypothesis. Property-based tests verify that certain properties hold true across a wide range of inputs, providing stronger guarantees than example-based unit tests.

## Properties Tested

### Property 1: Agent Migration Preserves Functionality
**Validates: Requirement 1.6**

For any valid extracted medical data, the migrated agent should validate and process it correctly, maintaining all required fields and structure.

**Test:** `test_property_1_migration_preserves_functionality`

**Invariants:**
- Validation result contains all required fields (valid, errors, flagged_fields, low_confidence_fields)
- Valid data has no errors
- All required data fields are preserved (symptoms, vitals, lab_results, medications, diagnoses, confidence_scores)

### Property 10: Extraction Operations Include Confidence Scores
**Validates: Requirements 4.6, 8.7, 14.8**

For any extraction operation, the result should include confidence scores for all major data categories.

**Test:** `test_property_10_confidence_scores_included`

**Invariants:**
- All required confidence score fields are present (overall, symptoms, vitals, lab_results, medications, diagnoses)
- All scores are in valid range [0.0, 1.0]
- All scores are rounded to 2 decimal places

### Property 11: OCR Extracts Structured Medical Data
**Validates: Requirements 4.7, 8.2**

For any medical report, OCR should extract structured data including lab results, vitals, medications, and diagnoses.

**Test:** `test_property_11_ocr_extracts_structured_data`

**Invariants:**
- Extraction succeeds for all supported file types
- Extracted data contains all required structured fields
- Vitals contain all expected sub-fields (blood_pressure, heart_rate, temperature, weight, height)

### Property 52: Image Analysis Extracts Chart Data
**Validates: Requirement 14.2**

For any medical report image containing charts or graphs, the agent should extract chart data and analysis.

**Test:** `test_property_52_chart_data_extraction`

**Invariants:**
- Extraction succeeds for image file types
- Result contains chart_analysis field
- Chart analysis has expected structure (analysis or extraction_method)
- Metadata indicates whether charts were found

### Property 54: Table Extraction Preserves Structure
**Validates: Requirement 14.4**

For any medical report containing tables, the extraction should preserve the table structure and relationships.

**Test:** `test_property_54_table_structure_preservation`

**Invariants:**
- Extraction succeeds for all supported file types
- Result contains table_data field as a list
- Each table entry is a dictionary with content or extraction method
- Metadata accurately reflects whether tables were found

### Property 56: Report Type Is Identified
**Validates: Requirement 14.6**

For any medical report, the agent should identify the report type (lab report, radiology, pathology, etc.).

**Test:** `test_property_56_report_type_identification`

**Invariants:**
- Extraction succeeds for all supported file types
- Result contains report_type field as a string
- Report type matches the identified type
- Metadata includes the report type

### Additional Properties

#### Validation Consistency
For any extracted data, validation should produce the same result when called multiple times.

**Test:** `test_property_validation_consistency`

**Invariants:**
- Multiple validation calls produce identical results
- Valid status, errors, flagged fields, and low confidence fields are consistent

#### Confidence Score Determinism
For any extracted data and text, confidence scores should be the same when calculated multiple times.

**Test:** `test_property_confidence_deterministic`

**Invariants:**
- Multiple confidence calculations produce identical scores
- All scores remain in valid range [0.0, 1.0]

## Running the Tests

### Run all property tests:
```bash
pytest backend/agents/test_enhanced_extraction_properties.py -v
```

### Run specific property test:
```bash
pytest backend/agents/test_enhanced_extraction_properties.py::TestEnhancedExtractionProperties::test_property_1_migration_preserves_functionality -v
```

### Run with more examples (slower but more thorough):
```bash
pytest backend/agents/test_enhanced_extraction_properties.py --hypothesis-show-statistics
```

### Run with hypothesis verbosity:
```bash
pytest backend/agents/test_enhanced_extraction_properties.py -v --hypothesis-verbosity=verbose
```

## Test Strategies

The test suite uses Hypothesis strategies to generate test data:

### `medical_report_text()`
Generates realistic medical report text with:
- Random symptoms from a predefined list
- Valid vital signs (blood pressure, heart rate)
- Structured report format

### `extracted_medical_data()`
Generates valid extracted medical data structures with:
- Lists of symptoms
- Complete vitals dictionary with valid ranges
- Lab results with proper structure
- Medications with required fields
- Diagnoses with valid status values
- Confidence scores in valid range [0.0, 1.0]

## Mocking Strategy

The tests use extensive mocking to isolate the agent logic from external dependencies:

1. **GeminiOCRService**: Mocked to return controlled OCR results
2. **LLM calls**: Mocked to return predictable structured data
3. **File I/O**: Uses BytesIO for in-memory file streams

This allows testing the agent's logic without requiring actual API calls or file processing.

## Interpreting Failures

### Falsifying Examples
When Hypothesis finds a failing case, it will:
1. Show the minimal failing example
2. Save it for regression testing
3. Attempt to shrink the example to the simplest failing case

### Common Failure Patterns

**Validation Failures:**
- Check if the generated data violates any validation rules
- Verify that validation logic handles edge cases

**Confidence Score Failures:**
- Ensure scores are always in [0.0, 1.0] range
- Check rounding logic for edge cases

**Structure Preservation Failures:**
- Verify that all required fields are present
- Check that data types match expectations

## Integration with CI/CD

These property tests should be run:
- On every commit (with default example count)
- Nightly with increased example count (--hypothesis-seed=random)
- Before releases with maximum thoroughness

## Maintenance

When adding new features to EnhancedExtractionAgent:

1. **Add new properties** if the feature introduces new invariants
2. **Update strategies** if new data structures are added
3. **Extend mocking** if new external dependencies are introduced
4. **Document properties** in this README

## References

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Property-Based Testing Guide](https://hypothesis.works/articles/what-is-property-based-testing/)
- Design Document: `.kiro/specs/autonomous-ai-agents-refactor/design.md`
- Requirements Document: `.kiro/specs/autonomous-ai-agents-refactor/requirements.md`
