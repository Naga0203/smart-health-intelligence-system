"""
Google Gemini Client for AI Health Intelligence System

This client provides a wrapper around Google's Generative AI API for explanation generation.
It includes error handling, rate limiting, and fallback mechanisms.

Validates: Requirements 9.1, 9.2, 9.4
"""

import google.generativeai as genai
from typing import Dict, Any, Optional
import logging
import time
from datetime import datetime, timedelta
from django.conf import settings
import json

logger = logging.getLogger('health_ai.gemini')


class GeminiClient:
    """
    Wrapper class for Google Gemini API with health-specific safeguards.
    
    Key constraints:
    - Used ONLY for explanation and reasoning
    - NEVER for medical diagnosis or disease prediction
    - Includes rate limiting and error handling
    """
    
    def __init__(self):
        """Initialize the Gemini client with API key and safety settings."""
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = "gemini-1.5-flash"
        self.model = None
        self.last_request_time = None
        self.min_request_interval = 1.0  # Minimum seconds between requests
        
        # Rate limiting
        self.requests_per_minute = 60
        self.request_timestamps = []
        
        # Fallback explanations for API failures
        self.fallback_explanations = {
            "LOW": "Based on the provided symptoms, our system has low confidence in this assessment. We recommend consulting with a healthcare professional for proper evaluation.",
            "MEDIUM": "The symptoms you've provided suggest a moderate risk level. This assessment is for informational purposes only and should not replace professional medical advice.",
            "HIGH": "The symptoms indicate a higher risk level that warrants attention. Please consult with a healthcare professional for proper diagnosis and treatment options."
        }
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Gemini API client."""
        try:
            if not self.api_key:
                logger.warning("Gemini API key not provided - using fallback explanations only")
                return
            
            genai.configure(api_key=self.api_key)
            
            # Configure safety settings to prevent harmful content
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_MEDICAL",
                    "threshold": "BLOCK_NONE"  # We handle medical disclaimers ourselves
                },
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
            
            # Generation configuration
            generation_config = {
                "temperature": 0.3,  # Lower temperature for more consistent explanations
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 500,  # Limit response length
            }
            
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            
            logger.info("Gemini client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            self.model = None
    
    def generate_explanation(self, disease: str, probability: float, confidence: str, symptoms: list) -> str:
        """
        Generate a human-readable explanation for a health risk assessment.
        
        Args:
            disease: The disease being assessed
            probability: Risk probability (0.0 to 1.0)
            confidence: Confidence level (LOW, MEDIUM, HIGH)
            symptoms: List of symptoms provided by user
            
        Returns:
            Generated explanation text
        """
        try:
            # Check rate limiting
            if not self._check_rate_limit():
                logger.warning("Rate limit exceeded, using fallback explanation")
                return self._get_fallback_explanation(confidence)
            
            # If no API key or model failed to initialize, use fallback
            if not self.model:
                return self._get_fallback_explanation(confidence)
            
            # Create the prompt
            prompt = self._create_explanation_prompt(disease, probability, confidence, symptoms)
            
            # Generate explanation
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                explanation = response.text.strip()
                logger.info(f"Generated explanation for {disease} with {confidence} confidence")
                return explanation
            else:
                logger.warning("Empty response from Gemini API")
                return self._get_fallback_explanation(confidence)
                
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return self._get_fallback_explanation(confidence)
    
    def _create_explanation_prompt(self, disease: str, probability: float, confidence: str, symptoms: list) -> str:
        """Create a prompt for explanation generation."""
        symptoms_text = ", ".join(symptoms)
        probability_percent = round(probability * 100, 1)
        
        prompt = f"""
You are an AI assistant helping to explain health risk assessments. Your role is to provide clear, educational explanations while emphasizing that this is NOT medical diagnosis.

CRITICAL REQUIREMENTS:
- This is NOT a medical diagnosis
- Always emphasize consulting healthcare professionals
- Use simple, non-medical language
- Be supportive but not alarming
- Focus on education, not treatment advice

Assessment Details:
- Condition assessed: {disease}
- Risk probability: {probability_percent}%
- Confidence level: {confidence}
- Symptoms provided: {symptoms_text}

Please explain:
1. What this risk assessment means in simple terms
2. Why the confidence level is {confidence}
3. What factors contributed to this assessment
4. The importance of professional medical consultation

Keep the explanation under 300 words and maintain a supportive, educational tone.
"""
        return prompt
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        current_time = time.time()
        
        # Remove timestamps older than 1 minute
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if current_time - ts < 60
        ]
        
        # Check requests per minute limit
        if len(self.request_timestamps) >= self.requests_per_minute:
            return False
        
        # Check minimum interval between requests
        if (self.last_request_time and 
            current_time - self.last_request_time < self.min_request_interval):
            return False
        
        # Update tracking
        self.request_timestamps.append(current_time)
        self.last_request_time = current_time
        
        return True
    
    def _get_fallback_explanation(self, confidence: str) -> str:
        """Get fallback explanation when API is unavailable."""
        base_explanation = self.fallback_explanations.get(
            confidence, 
            self.fallback_explanations["MEDIUM"]
        )
        
        disclaimer = ("\n\nIMPORTANT: This assessment is for informational purposes only "
                     "and does not constitute medical advice. Please consult with a "
                     "qualified healthcare professional for proper diagnosis and treatment.")
        
        return base_explanation + disclaimer
    
    def get_client_status(self) -> Dict[str, Any]:
        """Get the current status of the Gemini client."""
        return {
            "api_configured": bool(self.api_key),
            "model_initialized": bool(self.model),
            "model_name": self.model_name,
            "rate_limit_status": {
                "requests_in_last_minute": len(self.request_timestamps),
                "max_requests_per_minute": self.requests_per_minute,
                "last_request_time": self.last_request_time
            },
            "fallback_available": True
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the Gemini API connection."""
        try:
            if not self.model:
                return {
                    "success": False,
                    "error": "Model not initialized",
                    "fallback_available": True
                }
            
            # Simple test prompt
            test_prompt = "Respond with 'Connection successful' if you can read this."
            response = self.model.generate_content(test_prompt)
            
            if response and response.text:
                return {
                    "success": True,
                    "response": response.text.strip(),
                    "model_name": self.model_name
                }
            else:
                return {
                    "success": False,
                    "error": "Empty response from API",
                    "fallback_available": True
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_available": True
            }