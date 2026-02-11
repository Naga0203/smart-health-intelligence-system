"""
Base Agent class for LangChain-based AI Health Intelligence System

This provides a common foundation for all AI agents using LangChain framework.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from common.gemini_client import LangChainGeminiClient
import logging
from datetime import datetime

logger = logging.getLogger('health_ai.agents')


class BaseHealthAgent(ABC):
    """
    Base class for all health intelligence agents using LangChain.
    
    Provides common functionality:
    - LangChain integration
    - Gemini LLM access
    - Logging and error handling
    - Agent state management
    """
    
    def __init__(self, agent_name: str):
        """
        Initialize the base agent.
        
        Args:
            agent_name: Name of the agent for logging and identification
        """
        self.agent_name = agent_name
        self.gemini_client = LangChainGeminiClient()
        self.llm = self.gemini_client.llm
        self.agent_state = {
            "initialized_at": datetime.utcnow().isoformat(),
            "agent_name": agent_name,
            "status": "active"
        }
        
        logger.info(f"{agent_name} agent initialized with LangChain")
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for the agent.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            Processed result dictionary
        """
        pass
    
    def create_agent_chain(self, system_prompt: str, human_prompt: str) -> Any:
        """
        Create a LangChain processing chain for the agent.
        
        Args:
            system_prompt: System prompt template
            human_prompt: Human prompt template
            
        Returns:
            LangChain chain or None if LLM unavailable
        """
        if not self.llm:
            logger.warning(f"{self.agent_name} agent: LLM not available, using fallback")
            return None
        
        try:
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", human_prompt)
            ])
            
            chain = prompt_template | self.llm | StrOutputParser()
            return chain
            
        except Exception as e:
            logger.error(f"{self.agent_name} agent: Error creating chain - {str(e)}")
            return None
    
    def execute_chain(self, chain: Any, input_data: Dict[str, Any]) -> Optional[str]:
        """
        Execute a LangChain chain with error handling.
        
        Args:
            chain: LangChain chain to execute
            input_data: Input data for the chain
            
        Returns:
            Chain output or None if failed
        """
        if not chain:
            return None
        
        try:
            result = chain.invoke(input_data)
            logger.info(f"{self.agent_name} agent: Chain executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"{self.agent_name} agent: Chain execution failed - {str(e)}")
            return None
    
    def get_fallback_response(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get fallback response when LLM is unavailable.
        
        Args:
            input_data: Original input data
            
        Returns:
            Fallback response dictionary
        """
        return {
            "success": False,
            "agent": self.agent_name,
            "message": f"{self.agent_name} agent fallback response",
            "fallback_used": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def log_agent_action(self, action: str, details: Dict[str, Any] = None):
        """
        Log agent actions for monitoring and debugging.
        
        Args:
            action: Action being performed
            details: Additional details about the action
        """
        log_data = {
            "agent": self.agent_name,
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if details:
            log_data.update(details)
        
        logger.info(f"{self.agent_name} agent action: {action}")
        if details:
            logger.debug(f"{self.agent_name} agent details: {details}")
    
    def update_agent_state(self, updates: Dict[str, Any]):
        """
        Update agent state with new information.
        
        Args:
            updates: State updates to apply
        """
        self.agent_state.update(updates)
        self.agent_state["last_updated"] = datetime.utcnow().isoformat()
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get current agent status and capabilities.
        
        Returns:
            Agent status dictionary
        """
        return {
            "agent_name": self.agent_name,
            "state": self.agent_state,
            "llm_available": bool(self.llm),
            "gemini_status": self.gemini_client.get_client_status(),
            "framework": "LangChain"
        }
    
    def validate_input(self, input_data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """
        Validate input data for required fields.
        
        Args:
            input_data: Input data to validate
            required_fields: List of required field names
            
        Returns:
            Validation result dictionary
        """
        missing_fields = [field for field in required_fields if field not in input_data]
        
        if missing_fields:
            return {
                "valid": False,
                "missing_fields": missing_fields,
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }
        
        return {"valid": True}
    
    def format_agent_response(self, success: bool, data: Any = None, 
                            message: str = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Format standardized agent response.
        
        Args:
            success: Whether the operation was successful
            data: Response data
            message: Response message
            metadata: Additional metadata
            
        Returns:
            Formatted response dictionary
        """
        response = {
            "success": success,
            "agent": self.agent_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if data is not None:
            response["data"] = data
        
        if message:
            response["message"] = message
        
        if metadata:
            response["metadata"] = metadata
        
        return response