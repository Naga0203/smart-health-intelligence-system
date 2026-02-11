"""
LangChain-based Gemini Client for AI Health Intelligence System

This client provides a LangChain wrapper around Google's Generative AI API 
for explanation generation with enhanced agent capabilities.

Validates: Requirements 9.1, 9.2, 9.4
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing import Dict, Any, Optional, List
import logging
import time
from datetime import datetime, timedelta
from django.conf import settings

logger = logging.getLogger('health_ai.gemini')


class LangChainGeminiClient:
    """
    LangChain-based wrapper for Google Gemini API with health-specific safeguards.
    
    Key features:
    - LangChain integration for better agent orchestration
    - Used ONLY for explanation and reasoning
    - NEVER for medical diagnosis or disease prediction
    - Includes rate limiting and error handling
    """
    
    def __init__(self):
        """Initialize the LangChain Gemini client with API key and safety settings."""
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = "gemini-2.5-flash"
        self.llm = None
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
        """Initialize the LangChain Gemini client."""
        try:
            if not self.api_key:
                logger.warning("Gemini API key not provided - using fallback explanations only")
                return
            
            # Initialize LangChain ChatGoogleGenerativeAI
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=0.3,  # Lower temperature for more consistent explanations
                max_output_tokens=500,  # Limit response length
                top_p=0.8,
                top_k=40,
                safety_settings={
                    "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
                    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE", 
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
                    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
                }
            )
            
            logger.info("LangChain Gemini client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain Gemini client: {str(e)}")
            self.llm = None
    
    def generate_explanation(self, disease: str, probability: float, confidence: str, symptoms: list) -> str:
        """
        Generate a human-readable explanation for a health risk assessment using LangChain.
        
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
            if not self.llm:
                return self._get_fallback_explanation(confidence)
            
            # Create the LangChain prompt template
            prompt_template = self._create_langchain_prompt_template()
            
            # Create the chain
            chain = prompt_template | self.llm | StrOutputParser()
            
            # Prepare input data
            input_data = {
                "disease": disease.replace('_', ' ').title(),
                "probability_percent": round(probability * 100, 1),
                "confidence": confidence,
                "symptoms": ", ".join(symptoms)
            }
            
            # Generate explanation using the chain
            explanation = chain.invoke(input_data)
            
            if explanation:
                explanation = explanation.strip()
                logger.info(f"Generated explanation for {disease} with {confidence} confidence using LangChain")
                return explanation
            else:
                logger.warning("Empty response from LangChain Gemini")
                return self._get_fallback_explanation(confidence)
                
        except Exception as e:
            logger.error(f"Error generating explanation with LangChain: {str(e)}")
            return self._get_fallback_explanation(confidence)
    
    def _create_langchain_prompt_template(self) -> ChatPromptTemplate:
        """Create a LangChain prompt template for explanation generation."""
        system_template = """You are an AI assistant helping to explain health risk assessments. Your role is to provide clear, educational explanations while emphasizing that this is NOT medical diagnosis.

CRITICAL REQUIREMENTS:
- This is NOT a medical diagnosis
- Always emphasize consulting healthcare professionals
- Use simple, non-medical language
- Be supportive but not alarming
- Focus on education, not treatment advice
- Keep explanations under 300 words
- Maintain a supportive, educational tone"""

        human_template = """Please explain this health risk assessment:

Condition assessed: {disease}
Risk probability: {probability_percent}%
Confidence level: {confidence}
Symptoms provided: {symptoms}

Please explain:
1. What this risk assessment means in simple terms
2. Why the confidence level is {confidence}
3. What factors contributed to this assessment
4. The importance of professional medical consultation

Remember: This is for educational purposes only and not a medical diagnosis."""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])
    
    def generate_agent_response(self, agent_type: str, context: Dict[str, Any]) -> str:
        """
        Generate agent-specific responses using LangChain.
        
        Args:
            agent_type: Type of agent (validation, explanation, recommendation)
            context: Context data for the agent
            
        Returns:
            Generated agent response
        """
        try:
            if not self.llm:
                return self._get_agent_fallback(agent_type, context)
            
            # Create agent-specific prompt
            prompt_template = self._create_agent_prompt_template(agent_type)
            
            # Create the chain
            chain = prompt_template | self.llm | StrOutputParser()
            
            # Generate response
            response = chain.invoke(context)
            
            if response:
                logger.info(f"Generated {agent_type} agent response using LangChain")
                return response.strip()
            else:
                return self._get_agent_fallback(agent_type, context)
                
        except Exception as e:
            logger.error(f"Error generating {agent_type} agent response: {str(e)}")
            return self._get_agent_fallback(agent_type, context)
    
    def _create_agent_prompt_template(self, agent_type: str) -> ChatPromptTemplate:
        """Create agent-specific prompt templates."""
        templates = {
            "validation": {
                "system": "You are a validation agent for a health assessment system. Provide clear, helpful feedback about input validation issues.",
                "human": "The user input has validation issues: {validation_issues}. Please provide a clear, helpful message explaining what needs to be corrected."
            },
            "explanation": {
                "system": "You are an explanation agent for health risk assessments. Provide clear, educational explanations while emphasizing this is not medical diagnosis.",
                "human": "Explain this health assessment: Disease: {disease}, Probability: {probability}%, Confidence: {confidence}, Symptoms: {symptoms}"
            },
            "recommendation": {
                "system": "You are a recommendation agent for health assessments. Provide appropriate professional referral recommendations based on confidence levels.",
                "human": "Provide recommendations for: Disease: {disease}, Confidence: {confidence}, Probability: {probability}%. Focus on professional referrals and next steps."
            }
        }
        
        template = templates.get(agent_type, templates["explanation"])
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(template["system"]),
            HumanMessagePromptTemplate.from_template(template["human"])
        ])
    
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
    
    def _get_agent_fallback(self, agent_type: str, context: Dict[str, Any]) -> str:
        """Get fallback response for agent-specific requests."""
        fallbacks = {
            "validation": "Please check your input and ensure all required fields are provided correctly.",
            "explanation": f"Assessment completed with {context.get('confidence', 'MEDIUM')} confidence. Please consult healthcare professionals for detailed explanation.",
            "recommendation": "We recommend consulting with a healthcare professional for proper evaluation and guidance."
        }
        
        return fallbacks.get(agent_type, fallbacks["explanation"])
    
    def create_conversation_chain(self, system_prompt: str) -> Any:
        """
        Create a LangChain conversation chain for complex interactions.
        
        Args:
            system_prompt: System prompt for the conversation
            
        Returns:
            LangChain conversation chain
        """
        if not self.llm:
            return None
        
        prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
        
        return prompt_template | self.llm | StrOutputParser()
    
    def get_client_status(self) -> Dict[str, Any]:
        """Get the current status of the LangChain Gemini client."""
        return {
            "api_configured": bool(self.api_key),
            "model_initialized": bool(self.llm),
            "model_name": self.model_name,
            "framework": "LangChain",
            "rate_limit_status": {
                "requests_in_last_minute": len(self.request_timestamps),
                "max_requests_per_minute": self.requests_per_minute,
                "last_request_time": self.last_request_time
            },
            "fallback_available": True
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the LangChain Gemini connection."""
        try:
            if not self.llm:
                return {
                    "success": False,
                    "error": "LangChain model not initialized",
                    "fallback_available": True
                }
            
            # Simple test using LangChain
            test_chain = self.create_conversation_chain(
                "You are a test assistant. Respond with 'LangChain connection successful' if you can read this."
            )
            
            if test_chain:
                response = test_chain.invoke({"input": "Test connection"})
                return {
                    "success": True,
                    "response": response,
                    "framework": "LangChain",
                    "model_name": self.model_name
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create test chain",
                    "fallback_available": True
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_available": True
            }