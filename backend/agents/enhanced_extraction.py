"""
Enhanced Extraction Agent for Medical Report Processing

Extends DataExtractionAgent to handle medical report files (PDF, images)
and extract structured medical data using Google Gemini AI with OCR capabilities.

Validates: Requirements 3.1, 3.2, 3.5, 3.6
"""

import logging
import json
from typing import Dict, Any, Optional, List, BinaryIO
from io import BytesIO
from datetime import datetime
import time

from backend.agents.data_extraction import DataExtractionAgent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from django.conf import settings

logger = logging.getLogger('health_ai.enhanced_extraction')


class EnhancedExtractionAgent(DataExtractionAgent):
    """
    Enhanced agent for extracting structured medical data from report files.
    
    Extends DataExtractionAgent with capabilities for:
    - PDF text extraction using Gemini
    - Image OCR using Gemini Vision
    - Medical terminology parsing and standardization
    - Structured data extraction with confidence scoring
    """
    
    def __init__(self):
        """Initialize the enhanced extraction agent."""
        super().__init__()
        self.agent_name = "EnhancedExtractionAgent"
        
        # Initialize Gemini Vision client for document processing
        self.gemini_vision_client = self._initialize_vision_client()
        
        # Load extraction prompt template
        self.extraction_prompt_template = self._load_extraction_prompt()
        
        # Medical terminology mappings for standardization
        self.medical_term_mappings = {
            'bp': 'blood_pressure',
            'blood pressure': 'blood_pressure',
            'temp': 'temperature',
            'temperature': 'temperature',
            'hr': 'heart_rate',
            'heart rate': 'heart_rate',
            'pulse': 'heart_rate',
            'wt': 'weight',
            'weight': 'weight',
            'ht': 'height',
            'height': 'height',
            'bmi': 'bmi',
            'glucose': 'glucose',
            'blood sugar': 'glucose',
            'cholesterol': 'cholesterol',
            'chol': 'cholesterol'
        }
        
        logger.info("EnhancedExtractionAgent initialized")
    
    def _initialize_vision_client(self) -> Optional[ChatGoogleGenerativeAI]:
        """Initialize Gemini Vision client for document processing."""
        try:
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            if not api_key:
                logger.warning("Gemini API key not configured")
                return None
            
            # Use Gemini 1.5 Pro for vision capabilities
            vision_client = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                google_api_key=api_key,
                temperature=0.1,  # Low temperature for consistent extraction
                max_output_tokens=2048
            )
            
            logger.info("Gemini Vision client initialized")
            return vision_client
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Vision client: {e}")
            return None
    
    def _load_extraction_prompt(self) -> str:
        """Load the medical data extraction prompt template."""
        return """You are a medical data extraction specialist. Extract structured medical information from the following medical report text.

Report Text:
{report_text}

Extract the following information in JSON format:

1. Symptoms: List of symptoms mentioned
2. Vitals: Blood pressure, heart rate, temperature, weight, height
3. Lab Results: Test name, value, unit, reference range, date
4. Medications: Name, dosage, frequency, start date
5. Diagnoses: Condition, ICD code (if present), date, status

Rules:
- Only extract information explicitly stated in the report
- Use null for missing information
- Standardize units (e.g., kg for weight, cm for height)
- Format dates as YYYY-MM-DD
- Include confidence level (0.0-1.0) for each extracted field

Output Format:
{{
  "symptoms": [...],
  "vitals": {{
    "blood_pressure": "120/80" or null,
    "heart_rate": 72 or null,
    "temperature": 98.6 or null,
    "weight": 70.5 or null,
    "height": 175.0 or null
  }},
  "lab_results": [
    {{
      "test_name": "Glucose",
      "value": 95.0,
      "unit": "mg/dL",
      "reference_range": "70-100",
      "date": "2024-01-15"
    }}
  ],
  "medications": [
    {{
      "name": "Metformin",
      "dosage": "500mg",
      "frequency": "twice daily",
      "start_date": "2024-01-10"
    }}
  ],
  "diagnoses": [
    {{
      "condition": "Type 2 Diabetes",
      "icd_code": "E11.9",
      "date": "2024-01-15",
      "status": "active"
    }}
  ],
  "confidence_scores": {{
    "overall": 0.85,
    "symptoms": 0.9,
    "vitals": 0.8,
    "lab_results": 0.85,
    "medications": 0.9,
    "diagnoses": 0.8
  }}
}}

Return ONLY the JSON object, no additional text."""
    
    def extract_from_report(self, file_stream: BinaryIO, file_type: str) -> Dict[str, Any]:
        """
        Extract medical data from report file.
        
        Args:
            file_stream: File content as stream
            file_type: MIME type of file ('application/pdf', 'image/jpeg', 'image/png')
            
        Returns:
            Dictionary with:
                - success: bool
                - extracted_data: ExtractedMedicalData dict
                - confidence_scores: Dict[str, float]
                - metadata: ExtractionMetadata dict
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting extraction for file type: {file_type}")
            
            # Step 1: Extract text from file
            if file_type == 'application/pdf':
                raw_text = self._process_pdf(file_stream)
            elif file_type in ['image/jpeg', 'image/png']:
                raw_text = self._process_image(file_stream)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            if not raw_text or len(raw_text.strip()) < 10:
                return {
                    'success': False,
                    'error_code': 'no_text_extracted',
                    'message': 'Could not extract readable text from the report',
                    'extracted_data': None,
                    'confidence_scores': None,
                    'metadata': {
                        'extraction_time_seconds': time.time() - start_time,
                        'ocr_used': file_type.startswith('image/'),
                        'pages_processed': 1,
                        'gemini_model': 'gemini-1.5-pro'
                    }
                }
            
            # Step 2: Parse medical text into structured data
            extracted_data = self._parse_medical_text(raw_text)
            
            # Step 3: Validate extracted data
            validation_result = self._validate_extracted_data(extracted_data)
            
            if not validation_result['valid']:
                logger.warning(f"Validation issues: {validation_result['errors']}")
            
            # Log flagged fields and low confidence fields
            if validation_result.get('flagged_fields'):
                logger.warning(f"Flagged fields for review: {validation_result['flagged_fields']}")
            
            if validation_result.get('low_confidence_fields'):
                logger.info(f"Low confidence fields: {validation_result['low_confidence_fields']}")
            
            # Step 4: Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(extracted_data, raw_text)
            
            extraction_time = time.time() - start_time
            
            metadata = {
                'extraction_time_seconds': round(extraction_time, 2),
                'ocr_used': file_type.startswith('image/'),
                'pages_processed': 1,
                'gemini_model': 'gemini-1.5-pro',
                'text_length': len(raw_text),
                'validation_passed': validation_result['valid'],
                'flagged_fields': validation_result.get('flagged_fields', []),
                'low_confidence_fields': validation_result.get('low_confidence_fields', [])
            }
            
            logger.info(f"Extraction completed in {extraction_time:.2f}s")
            
            return {
                'success': True,
                'extracted_data': extracted_data,
                'confidence_scores': confidence_scores,
                'metadata': metadata,
                'validation_result': validation_result
            }
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return {
                'success': False,
                'error_code': 'extraction_failed',
                'message': str(e),
                'extracted_data': None,
                'confidence_scores': None,
                'metadata': {
                    'extraction_time_seconds': time.time() - start_time,
                    'ocr_used': file_type.startswith('image/') if file_type else False,
                    'pages_processed': 0,
                    'gemini_model': 'gemini-1.5-pro'
                }
            }
    
    def _process_pdf(self, file_stream: BinaryIO) -> str:
        """
        Extract text from PDF using Gemini.
        
        Args:
            file_stream: PDF file stream
            
        Returns:
            Extracted text content
        """
        try:
            if not self.gemini_vision_client:
                raise Exception("Gemini Vision client not initialized")
            
            # Read PDF bytes
            pdf_bytes = file_stream.read()
            if hasattr(file_stream, 'seek'):
                file_stream.seek(0)
            
            # Use Gemini to extract text from PDF
            import base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "Extract all text content from this medical report PDF. Return only the text, preserving structure and formatting."
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:application/pdf;base64,{pdf_base64}"
                    }
                ]
            )
            
            response = self.gemini_vision_client.invoke([message])
            extracted_text = response.content
            
            logger.info(f"Extracted {len(extracted_text)} characters from PDF")
            
            return extracted_text
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            raise Exception(f"Failed to process PDF: {str(e)}")
    
    def _process_image(self, file_stream: BinaryIO) -> str:
        """
        Extract text from image using Gemini OCR.
        
        Args:
            file_stream: Image file stream
            
        Returns:
            Extracted text content via OCR
        """
        try:
            if not self.gemini_vision_client:
                raise Exception("Gemini Vision client not initialized")
            
            # Read image bytes
            image_bytes = file_stream.read()
            if hasattr(file_stream, 'seek'):
                file_stream.seek(0)
            
            # Use Gemini Vision for OCR
            import base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "Extract all text content from this medical report image using OCR. Return only the text, preserving structure and formatting."
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{image_base64}"
                    }
                ]
            )
            
            response = self.gemini_vision_client.invoke([message])
            extracted_text = response.content
            
            logger.info(f"Extracted {len(extracted_text)} characters from image via OCR")
            
            return extracted_text
            
        except Exception as e:
            logger.error(f"Image OCR processing failed: {e}")
            raise Exception(f"Failed to process image: {str(e)}")
    
    def _parse_medical_text(self, text: str) -> Dict[str, Any]:
        """
        Parse extracted text into structured medical data.
        
        Args:
            text: Raw text extracted from report
            
        Returns:
            Structured medical data dictionary
        """
        try:
            if not self.gemini_vision_client:
                raise Exception("Gemini client not initialized")
            
            # Format prompt with extracted text
            prompt = self.extraction_prompt_template.format(report_text=text)
            
            # Use Gemini to parse medical data
            message = HumanMessage(content=prompt)
            response = self.gemini_vision_client.invoke([message])
            
            # Parse JSON response
            response_text = response.content.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            extracted_data = json.loads(response_text)
            
            logger.info("Successfully parsed medical text into structured data")
            
            return extracted_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            # Return empty structure
            return self._get_empty_extraction_structure()
        except Exception as e:
            logger.error(f"Medical text parsing failed: {e}")
            return self._get_empty_extraction_structure()
    
    def _get_empty_extraction_structure(self) -> Dict[str, Any]:
        """Get empty extraction structure for fallback."""
        return {
            'symptoms': [],
            'vitals': {
                'blood_pressure': None,
                'heart_rate': None,
                'temperature': None,
                'weight': None,
                'height': None
            },
            'lab_results': [],
            'medications': [],
            'diagnoses': [],
            'confidence_scores': {
                'overall': 0.0,
                'symptoms': 0.0,
                'vitals': 0.0,
                'lab_results': 0.0,
                'medications': 0.0,
                'diagnoses': 0.0
            }
        }
    
    def _validate_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted data for type and range validation.
        
        Validates: Requirements 4.1, 4.2, 4.4
        
        Args:
            data: Extracted medical data
            
        Returns:
            Validation result with:
                - valid: bool (overall validation status)
                - errors: List[str] (specific field errors)
                - flagged_fields: List[str] (fields requiring user review)
                - low_confidence_fields: List[str] (fields with confidence < 0.7)
        """
        errors = []
        flagged_fields = []
        low_confidence_fields = []
        
        # Check required top-level fields
        required_fields = ['symptoms', 'vitals', 'lab_results', 'medications', 'diagnoses', 'confidence_scores']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Validate vitals structure and types
        if 'vitals' in data and isinstance(data['vitals'], dict):
            vital_fields = ['blood_pressure', 'heart_rate', 'temperature', 'weight', 'height']
            for field in vital_fields:
                if field not in data['vitals']:
                    errors.append(f"Missing vital field: {field}")
                else:
                    # Validate data types and ranges for vitals
                    value = data['vitals'][field]
                    if value is not None:
                        validation_error = self._validate_vital_field(field, value)
                        if validation_error:
                            errors.append(validation_error)
                            flagged_fields.append(f"vitals.{field}")
        
        # Validate data types for top-level fields
        if 'symptoms' in data and not isinstance(data['symptoms'], list):
            errors.append("Symptoms must be a list")
        
        if 'lab_results' in data:
            if not isinstance(data['lab_results'], list):
                errors.append("Lab results must be a list")
            else:
                # Validate each lab result structure
                for idx, lab_result in enumerate(data['lab_results']):
                    lab_errors = self._validate_lab_result(lab_result, idx)
                    errors.extend(lab_errors)
                    if lab_errors:
                        flagged_fields.append(f"lab_results[{idx}]")
        
        if 'medications' in data:
            if not isinstance(data['medications'], list):
                errors.append("Medications must be a list")
            else:
                # Validate each medication structure
                for idx, medication in enumerate(data['medications']):
                    med_errors = self._validate_medication(medication, idx)
                    errors.extend(med_errors)
                    if med_errors:
                        flagged_fields.append(f"medications[{idx}]")
        
        if 'diagnoses' in data:
            if not isinstance(data['diagnoses'], list):
                errors.append("Diagnoses must be a list")
            else:
                # Validate each diagnosis structure
                for idx, diagnosis in enumerate(data['diagnoses']):
                    diag_errors = self._validate_diagnosis(diagnosis, idx)
                    errors.extend(diag_errors)
                    if diag_errors:
                        flagged_fields.append(f"diagnoses[{idx}]")
        
        # Validate confidence scores and flag low confidence fields
        if 'confidence_scores' in data:
            scores = data['confidence_scores']
            if not isinstance(scores, dict):
                errors.append("Confidence scores must be a dictionary")
            else:
                for key, value in scores.items():
                    if not isinstance(value, (int, float)) or not (0.0 <= value <= 1.0):
                        errors.append(f"Invalid confidence score for {key}: {value}")
                    elif value < 0.7 and key != 'overall':
                        # Flag fields with low confidence (Requirement 4.3)
                        low_confidence_fields.append(key)
        
        is_valid = len(errors) == 0
        
        return {
            'valid': is_valid,
            'errors': errors if not is_valid else [],
            'flagged_fields': flagged_fields,
            'low_confidence_fields': low_confidence_fields
        }
    
    def _validate_vital_field(self, field: str, value: Any) -> Optional[str]:
        """
        Validate a single vital field for type and range.
        
        Validates: Requirement 4.1
        
        Args:
            field: Name of the vital field
            value: Value to validate
            
        Returns:
            Error message if validation fails, None otherwise
        """
        try:
            if field == 'blood_pressure':
                # Should be string in format "120/80"
                if not isinstance(value, str):
                    return f"blood_pressure must be a string, got {type(value).__name__}"
                if '/' not in value:
                    return f"blood_pressure must be in format 'systolic/diastolic', got '{value}'"
                parts = value.split('/')
                if len(parts) != 2:
                    return f"blood_pressure must have exactly 2 parts, got {len(parts)}"
                try:
                    systolic = int(parts[0])
                    diastolic = int(parts[1])
                    if not (50 <= systolic <= 250):
                        return f"blood_pressure systolic out of range (50-250): {systolic}"
                    if not (30 <= diastolic <= 150):
                        return f"blood_pressure diastolic out of range (30-150): {diastolic}"
                except ValueError:
                    return f"blood_pressure values must be numeric, got '{value}'"
            
            elif field == 'heart_rate':
                # Should be integer
                if not isinstance(value, (int, float)):
                    return f"heart_rate must be a number, got {type(value).__name__}"
                heart_rate = int(value)
                if not (30 <= heart_rate <= 250):
                    return f"heart_rate out of range (30-250): {heart_rate}"
            
            elif field == 'temperature':
                # Should be float (in Fahrenheit)
                if not isinstance(value, (int, float)):
                    return f"temperature must be a number, got {type(value).__name__}"
                temp = float(value)
                if not (90.0 <= temp <= 110.0):
                    return f"temperature out of range (90-110°F): {temp}"
            
            elif field == 'weight':
                # Should be float (in kg)
                if not isinstance(value, (int, float)):
                    return f"weight must be a number, got {type(value).__name__}"
                weight = float(value)
                if not (1.0 <= weight <= 500.0):
                    return f"weight out of range (1-500 kg): {weight}"
            
            elif field == 'height':
                # Should be float (in cm)
                if not isinstance(value, (int, float)):
                    return f"height must be a number, got {type(value).__name__}"
                height = float(value)
                if not (30.0 <= height <= 300.0):
                    return f"height out of range (30-300 cm): {height}"
            
            return None
            
        except Exception as e:
            return f"Validation error for {field}: {str(e)}"
    
    def _validate_lab_result(self, lab_result: Any, index: int) -> List[str]:
        """
        Validate a lab result structure.
        
        Validates: Requirement 4.1
        
        Args:
            lab_result: Lab result dictionary
            index: Index in the lab_results list
            
        Returns:
            List of error messages
        """
        errors = []
        
        if not isinstance(lab_result, dict):
            errors.append(f"lab_results[{index}] must be a dictionary")
            return errors
        
        # Check required fields
        required_fields = ['test_name', 'value', 'unit', 'reference_range', 'date']
        for field in required_fields:
            if field not in lab_result:
                errors.append(f"lab_results[{index}] missing required field: {field}")
        
        # Validate types
        if 'test_name' in lab_result and not isinstance(lab_result['test_name'], str):
            errors.append(f"lab_results[{index}].test_name must be a string")
        
        if 'value' in lab_result and not isinstance(lab_result['value'], (int, float)):
            errors.append(f"lab_results[{index}].value must be a number")
        
        if 'unit' in lab_result and not isinstance(lab_result['unit'], str):
            errors.append(f"lab_results[{index}].unit must be a string")
        
        if 'reference_range' in lab_result and not isinstance(lab_result['reference_range'], str):
            errors.append(f"lab_results[{index}].reference_range must be a string")
        
        if 'date' in lab_result and not isinstance(lab_result['date'], str):
            errors.append(f"lab_results[{index}].date must be a string")
        
        return errors
    
    def _validate_medication(self, medication: Any, index: int) -> List[str]:
        """
        Validate a medication structure.
        
        Validates: Requirement 4.1
        
        Args:
            medication: Medication dictionary
            index: Index in the medications list
            
        Returns:
            List of error messages
        """
        errors = []
        
        if not isinstance(medication, dict):
            errors.append(f"medications[{index}] must be a dictionary")
            return errors
        
        # Check required fields
        required_fields = ['name', 'dosage', 'frequency', 'start_date']
        for field in required_fields:
            if field not in medication:
                errors.append(f"medications[{index}] missing required field: {field}")
        
        # Validate types
        if 'name' in medication and not isinstance(medication['name'], str):
            errors.append(f"medications[{index}].name must be a string")
        
        if 'dosage' in medication and not isinstance(medication['dosage'], str):
            errors.append(f"medications[{index}].dosage must be a string")
        
        if 'frequency' in medication and not isinstance(medication['frequency'], str):
            errors.append(f"medications[{index}].frequency must be a string")
        
        if 'start_date' in medication and not isinstance(medication['start_date'], str):
            errors.append(f"medications[{index}].start_date must be a string")
        
        return errors
    
    def _validate_diagnosis(self, diagnosis: Any, index: int) -> List[str]:
        """
        Validate a diagnosis structure.
        
        Validates: Requirement 4.1
        
        Args:
            diagnosis: Diagnosis dictionary
            index: Index in the diagnoses list
            
        Returns:
            List of error messages
        """
        errors = []
        
        if not isinstance(diagnosis, dict):
            errors.append(f"diagnoses[{index}] must be a dictionary")
            return errors
        
        # Check required fields
        required_fields = ['condition', 'date', 'status']
        for field in required_fields:
            if field not in diagnosis:
                errors.append(f"diagnoses[{index}] missing required field: {field}")
        
        # Validate types
        if 'condition' in diagnosis and not isinstance(diagnosis['condition'], str):
            errors.append(f"diagnoses[{index}].condition must be a string")
        
        if 'icd_code' in diagnosis and diagnosis['icd_code'] is not None:
            if not isinstance(diagnosis['icd_code'], str):
                errors.append(f"diagnoses[{index}].icd_code must be a string or null")
        
        if 'date' in diagnosis and not isinstance(diagnosis['date'], str):
            errors.append(f"diagnoses[{index}].date must be a string")
        
        if 'status' in diagnosis:
            if not isinstance(diagnosis['status'], str):
                errors.append(f"diagnoses[{index}].status must be a string")
            elif diagnosis['status'] not in ['active', 'resolved', 'chronic']:
                errors.append(f"diagnoses[{index}].status must be 'active', 'resolved', or 'chronic'")
        
        return errors
    
    def _calculate_confidence_scores(self, data: Dict[str, Any], raw_text: str) -> Dict[str, float]:
        """
        Calculate confidence scores for each data category.
        
        Validates: Requirements 4.2, 4.3
        
        Args:
            data: Extracted medical data
            raw_text: Original text from report
            
        Returns:
            Dictionary of confidence scores (0.0-1.0) with fields flagged if < 0.7
        """
        # Use confidence scores from extraction if available and valid
        if 'confidence_scores' in data and isinstance(data['confidence_scores'], dict):
            scores = data['confidence_scores']
            # Validate all scores are in valid range
            all_valid = all(
                isinstance(v, (int, float)) and 0.0 <= v <= 1.0 
                for v in scores.values()
            )
            if all_valid:
                return scores
        
        # Calculate confidence scores based on data completeness and quality
        scores = {}
        
        # Symptoms confidence - based on presence and count
        symptoms = data.get('symptoms', [])
        if symptoms and isinstance(symptoms, list):
            # Higher confidence with more symptoms (up to 5)
            symptom_count = len(symptoms)
            scores['symptoms'] = min(0.6 + (symptom_count * 0.08), 1.0)
        else:
            scores['symptoms'] = 0.0
        
        # Vitals confidence - based on completeness
        vitals = data.get('vitals', {})
        if isinstance(vitals, dict):
            vital_fields = ['blood_pressure', 'heart_rate', 'temperature', 'weight', 'height']
            non_null_vitals = sum(1 for field in vital_fields if vitals.get(field) is not None)
            
            if non_null_vitals > 0:
                # Base confidence on completeness
                completeness_score = non_null_vitals / len(vital_fields)
                # Adjust based on data quality (presence of validation errors)
                scores['vitals'] = min(0.5 + (completeness_score * 0.4), 1.0)
            else:
                scores['vitals'] = 0.0
        else:
            scores['vitals'] = 0.0
        
        # Lab results confidence - based on presence and structure
        lab_results = data.get('lab_results', [])
        if lab_results and isinstance(lab_results, list):
            # Check completeness of lab result fields
            complete_results = 0
            for result in lab_results:
                if isinstance(result, dict):
                    required_fields = ['test_name', 'value', 'unit', 'reference_range', 'date']
                    if all(field in result and result[field] is not None for field in required_fields):
                        complete_results += 1
            
            if complete_results > 0:
                completeness_ratio = complete_results / len(lab_results)
                scores['lab_results'] = min(0.6 + (completeness_ratio * 0.3), 1.0)
            else:
                scores['lab_results'] = 0.4  # Some data but incomplete
        else:
            scores['lab_results'] = 0.0
        
        # Medications confidence - based on presence and structure
        medications = data.get('medications', [])
        if medications and isinstance(medications, list):
            # Check completeness of medication fields
            complete_meds = 0
            for med in medications:
                if isinstance(med, dict):
                    required_fields = ['name', 'dosage', 'frequency', 'start_date']
                    if all(field in med and med[field] is not None for field in required_fields):
                        complete_meds += 1
            
            if complete_meds > 0:
                completeness_ratio = complete_meds / len(medications)
                scores['medications'] = min(0.6 + (completeness_ratio * 0.3), 1.0)
            else:
                scores['medications'] = 0.4  # Some data but incomplete
        else:
            scores['medications'] = 0.0
        
        # Diagnoses confidence - based on presence and structure
        diagnoses = data.get('diagnoses', [])
        if diagnoses and isinstance(diagnoses, list):
            # Check completeness of diagnosis fields
            complete_diags = 0
            for diag in diagnoses:
                if isinstance(diag, dict):
                    required_fields = ['condition', 'date', 'status']
                    if all(field in diag and diag[field] is not None for field in required_fields):
                        complete_diags += 1
            
            if complete_diags > 0:
                completeness_ratio = complete_diags / len(diagnoses)
                scores['diagnoses'] = min(0.6 + (completeness_ratio * 0.3), 1.0)
            else:
                scores['diagnoses'] = 0.4  # Some data but incomplete
        else:
            scores['diagnoses'] = 0.0
        
        # Overall confidence - weighted average of non-zero scores
        # Give more weight to critical fields (vitals, lab_results, diagnoses)
        weights = {
            'symptoms': 0.15,
            'vitals': 0.25,
            'lab_results': 0.25,
            'medications': 0.15,
            'diagnoses': 0.20
        }
        
        weighted_sum = sum(scores.get(field, 0.0) * weight for field, weight in weights.items())
        total_weight = sum(weights.values())
        scores['overall'] = round(weighted_sum / total_weight, 2)
        
        # Round all scores to 2 decimal places
        scores = {k: round(v, 2) for k, v in scores.items()}
        
        return scores
