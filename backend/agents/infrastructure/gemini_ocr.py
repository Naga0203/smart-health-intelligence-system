"""
Gemini OCR Service for vision-based text extraction.

Uses Gemini AI's vision capabilities for extracting text and structured
data from medical report images.

Requirements: 4.1, 4.2, 4.5, 14.1, 14.5
"""

import logging
import time
from typing import Dict, Any, List, Optional
import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from .models import OCRResult

logger = logging.getLogger('health_ai.agents.infrastructure')


class GeminiOCRService:
    """
    OCR service using Gemini AI vision capabilities.
    
    Requirements:
    - 4.1, 4.2: Use Gemini AI for OCR
    - 4.5: Handle multiple image formats
    - 14.1: Analyze medical images beyond text
    - 14.5: Extract handwritten text
    """
    
    SUPPORTED_FORMATS = ['jpeg', 'jpg', 'png', 'pdf', 'tiff', 'tif', 'webp']
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini OCR service.
        
        Args:
            api_key: Google API key for Gemini
        """
        self.api_key = api_key
        self.vision_model = None
        
        self._initialize_vision_model()
        
        logger.info("GeminiOCRService initialized")
    
    def _initialize_vision_model(self):
        """Initialize Gemini Vision model."""
        try:
            if not self.api_key:
                from django.conf import settings
                self.api_key = settings.GEMINI_API_KEY
            
            if self.api_key:
                self.vision_model = ChatGoogleGenerativeAI(
                    model="gemini-1.5-pro-vision",
                    google_api_key=self.api_key,
                    temperature=0  # Deterministic for OCR
                )
                logger.info("Gemini Vision model initialized")
            else:
                logger.warning("No API key available for Gemini Vision")
                
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Vision: {e}")
            self.vision_model = None
    
    def extract_text(self, image_data: bytes, image_format: str) -> OCRResult:
        """
        Extract text from medical report image.
        
        Requirements: 4.1, 4.2 - Extract text using Gemini Vision
        
        Args:
            image_data: Image bytes
            image_format: Image format (jpeg, png, pdf, tiff)
            
        Returns:
            OCRResult with extracted text and confidence scores
        """
        start_time = time.time()
        
        # Validate format
        if image_format.lower() not in self.SUPPORTED_FORMATS:
            logger.error(f"Unsupported image format: {image_format}")
            return OCRResult(
                text="",
                confidence=0.0,
                format=image_format,
                metadata={'error': f'Unsupported format: {image_format}'}
            )
        
        if not self.vision_model:
            logger.error("Gemini Vision model not available")
            return OCRResult(
                text="",
                confidence=0.0,
                format=image_format,
                metadata={'error': 'Vision model not available'}
            )
        
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Create vision message
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "Extract all text from this medical report image. "
                               "Preserve the structure and formatting as much as possible."
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/{image_format};base64,{image_base64}"
                    }
                ]
            )
            
            # Extract text
            response = self.vision_model.invoke([message])
            extracted_text = response.content
            
            extraction_time = time.time() - start_time
            
            logger.info(f"Text extracted: {len(extracted_text)} characters in {extraction_time:.2f}s")
            
            return OCRResult(
                text=extracted_text,
                confidence=0.9,  # Gemini Vision typically high confidence
                format=image_format,
                extraction_time=extraction_time,
                metadata={
                    'method': 'gemini_vision',
                    'model': 'gemini-1.5-pro-vision'
                }
            )
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                format=image_format,
                extraction_time=time.time() - start_time,
                metadata={'error': str(e)}
            )
    
    def extract_structured_data(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extract structured data from medical report image.
        
        Requirements: 4.7, 8.2 - Extract structured medical data
        
        Args:
            image_data: Image bytes
            
        Returns:
            Dictionary with structured data
        """
        if not self.vision_model:
            logger.error("Gemini Vision model not available")
            return {'error': 'Vision model not available'}
        
        try:
            # Encode image
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Create structured extraction message
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "Extract structured medical data from this report. "
                               "Identify and extract:\n"
                               "1. Lab results (test names, values, units, reference ranges)\n"
                               "2. Vital signs (blood pressure, heart rate, temperature, weight)\n"
                               "3. Medications (drug names, dosages, frequencies)\n"
                               "4. Diagnoses (conditions, ICD codes if present, dates)\n"
                               "5. Patient information (name, age, gender, ID)\n"
                               "6. Report metadata (date, provider, facility)\n\n"
                               "Format as JSON."
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{image_base64}"
                    }
                ]
            )
            
            response = self.vision_model.invoke([message])
            
            # Parse response (would need JSON parsing in production)
            structured_data = {
                'raw_response': response.content,
                'extraction_method': 'gemini_vision_structured'
            }
            
            logger.info("Structured data extracted from image")
            
            return structured_data
            
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            return {'error': str(e)}
    
    def extract_from_table(self, image_data: bytes) -> List[Dict[str, Any]]:
        """
        Extract data from tables in medical reports.
        
        Requirements: 14.4 - Extract data from tables
        
        Args:
            image_data: Image bytes
            
        Returns:
            List of table row dictionaries
        """
        if not self.vision_model:
            logger.error("Gemini Vision model not available")
            return []
        
        try:
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "Extract all tables from this medical report. "
                               "For each table, identify column headers and extract all rows. "
                               "Preserve the table structure and relationships."
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{image_base64}"
                    }
                ]
            )
            
            response = self.vision_model.invoke([message])
            
            # Parse table data (simplified - would need proper parsing)
            table_data = [{
                'raw_content': response.content,
                'extraction_method': 'gemini_vision_table'
            }]
            
            logger.info("Table data extracted from image")
            
            return table_data
            
        except Exception as e:
            logger.error(f"Error extracting table data: {e}")
            return []
    
    def extract_from_chart(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extract data points from charts and graphs.
        
        Requirements: 14.2 - Extract data from charts and graphs
        
        Args:
            image_data: Image bytes
            
        Returns:
            Dictionary with chart data
        """
        if not self.vision_model:
            logger.error("Gemini Vision model not available")
            return {'error': 'Vision model not available'}
        
        try:
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "Analyze this medical chart or graph. "
                               "Extract:\n"
                               "1. Chart type (line, bar, scatter, etc.)\n"
                               "2. Axis labels and units\n"
                               "3. Data points and values\n"
                               "4. Trends and patterns\n"
                               "5. Any annotations or important markers"
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{image_base64}"
                    }
                ]
            )
            
            response = self.vision_model.invoke([message])
            
            chart_data = {
                'analysis': response.content,
                'extraction_method': 'gemini_vision_chart'
            }
            
            logger.info("Chart data extracted from image")
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error extracting chart data: {e}")
            return {'error': str(e)}
    
    def handle_handwriting(self, image_data: bytes) -> str:
        """
        Extract text from handwritten notes.
        
        Requirements: 14.5 - Extract handwritten text
        
        Args:
            image_data: Image bytes
            
        Returns:
            Extracted handwritten text
        """
        if not self.vision_model:
            logger.error("Gemini Vision model not available")
            return ""
        
        try:
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "This image contains handwritten medical notes. "
                               "Extract all handwritten text. Be careful with medical terminology "
                               "and abbreviations. If text is unclear, indicate uncertainty."
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{image_base64}"
                    }
                ]
            )
            
            response = self.vision_model.invoke([message])
            
            logger.info("Handwritten text extracted from image")
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error extracting handwritten text: {e}")
            return ""
    
    def identify_report_type(self, image_data: bytes) -> str:
        """
        Identify the type of medical report.
        
        Requirements: 14.6 - Identify report type
        
        Args:
            image_data: Image bytes
            
        Returns:
            Report type (lab report, radiology, pathology, etc.)
        """
        if not self.vision_model:
            logger.error("Gemini Vision model not available")
            return "unknown"
        
        try:
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "Identify the type of this medical report. "
                               "Common types include: lab report, radiology report, pathology report, "
                               "discharge summary, consultation note, prescription, etc. "
                               "Respond with just the report type."
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{image_base64}"
                    }
                ]
            )
            
            response = self.vision_model.invoke([message])
            report_type = response.content.strip().lower()
            
            logger.info(f"Report type identified: {report_type}")
            
            return report_type
            
        except Exception as e:
            logger.error(f"Error identifying report type: {e}")
            return "unknown"
    
    def extract_report_headers(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extract header information from medical report.
        
        Requirements: 14.7 - Extract dates, patient IDs, provider info
        
        Args:
            image_data: Image bytes
            
        Returns:
            Dictionary with header information
        """
        if not self.vision_model:
            logger.error("Gemini Vision model not available")
            return {}
        
        try:
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "Extract header information from this medical report:\n"
                               "1. Report date\n"
                               "2. Patient name/ID\n"
                               "3. Provider name\n"
                               "4. Facility/institution name\n"
                               "5. Report ID/number\n"
                               "Format as JSON."
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{image_base64}"
                    }
                ]
            )
            
            response = self.vision_model.invoke([message])
            
            # Parse header info (simplified)
            header_info = {
                'raw_response': response.content,
                'extraction_method': 'gemini_vision_headers'
            }
            
            logger.info("Report headers extracted from image")
            
            return header_info
            
        except Exception as e:
            logger.error(f"Error extracting report headers: {e}")
            return {'error': str(e)}
