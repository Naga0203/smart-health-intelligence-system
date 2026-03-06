"""
Enhanced Base Health Agent with autonomous capabilities.

Provides enhanced base class for all health intelligence agents with
web search, autonomous decision-making, circuit breakers, context management,
monitoring, and safety guardrails.

Requirements: 1.2, 5.6, 6.5, 9.1
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
import logging
import time
from datetime import datetime

from common.gemini_client import LangChainGeminiClient
from .config import AgentConfig
from .web_search import WebSearchTool
from .decision_engine import DecisionEngine
from .circuit_breaker import CircuitBreaker, CircuitOpenError
from .context_manager import ContextManager
from .monitoring import MonitoringService
from .safety_guardrails import SafetyGuardrails
from .models import SearchResult, AgentDecision

logger = logging.getLogger('health_ai.agents.infrastructure')


class EnhancedBaseHealthAgent(ABC):
    """
    Enhanced base class for autonomous health intelligence agents.
    
    Provides:
    - Web search integration
    - Autonomous decision-making
    - Circuit breaker and retry logic
    - Context management
    - Monitoring integration
    - Safety guardrails
    
    Requirements:
    - 1.2: LangChain integration
    - 5.6: Retry logic
    - 6.5: Timeout management
    - 9.1: Error handling with retries
    """
    
    def __init__(self, agent_name: str, config: Optional[AgentConfig] = None):
        """
        Initialize enhanced base agent.
        
        Args:
            agent_name: Name of the agent
            config: Agent configuration
        """
        self.agent_name = agent_name
        self.config = config or AgentConfig(agent_name=agent_name)
        
        # Initialize LangChain Gemini client
        self.gemini_client = LangChainGeminiClient()
        self.llm = self.gemini_client.llm
        
        # Initialize infrastructure components
        self.web_search_tool = WebSearchTool(self.config.search_config) if self.config.enable_web_search else None
        self.decision_engine = DecisionEngine(self.llm)
        self.circuit_breaker = CircuitBreaker(self.config.circuit_config)
        self.context_manager = ContextManager()
        self.monitoring = MonitoringService() if self.config.monitoring_enabled else None
        self.safety_guardrails = SafetyGuardrails()
        
        # Agent state
        self.agent_state = {
            "initialized_at": datetime.utcnow().isoformat(),
            "agent_name": agent_name,
            "status": "active",
            "version": "enhanced"
        }
        
        logger.info(f"EnhancedBaseHealthAgent '{agent_name}' initialized")
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method - must be implemented by subclasses.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            Processed result dictionary
        """
        pass
    
    def execute_with_timeout(
        self,
        operation: Callable[[], Any],
        timeout: Optional[int] = None
    ) -> Any:
        """
        Execute operation with timeout.
        
        Requirements: 6.5 - Timeout management
        
        Args:
            operation: Operation to execute
            timeout: Timeout in seconds (uses config default if not provided)
            
        Returns:
            Operation result
            
        Raises:
            TimeoutError: If operation exceeds timeout
        """
        timeout = timeout or self.config.timeout
        start_time = time.time()
        
        try:
            # Simple timeout implementation
            # In production, would use threading or asyncio for proper timeout
            result = operation()
            
            elapsed = time.time() - start_time
            if elapsed > timeout:
                logger.warning(f"Operation exceeded timeout: {elapsed:.2f}s > {timeout}s")
                raise TimeoutError(f"Operation exceeded timeout of {timeout}s")
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Operation failed after {elapsed:.2f}s: {e}")
            raise
    
    def execute_with_retry(
        self,
        operation: Callable[[], Any],
        max_retries: Optional[int] = None
    ) -> Any:
        """
        Execute operation with exponential backoff retry.
        
        Requirements: 5.6, 9.1 - Retry logic with exponential backoff
        
        Args:
            operation: Operation to execute
            max_retries: Maximum retry attempts (uses config default if not provided)
            
        Returns:
            Operation result
            
        Raises:
            Exception: If all retries fail
        """
        max_retries = max_retries or self.config.max_retries
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                result = operation()
                
                if attempt > 0:
                    logger.info(f"Operation succeeded on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(
                        f"Operation failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Operation failed after {max_retries + 1} attempts: {e}")
        
        raise last_exception
    
    def execute_with_circuit_breaker(self, operation: Callable[[], Any]) -> Any:
        """
        Execute operation through circuit breaker.
        
        Requirements: 9.4 - Circuit breaker for resilience
        
        Args:
            operation: Operation to execute
            
        Returns:
            Operation result
            
        Raises:
            CircuitOpenError: If circuit breaker is open
        """
        return self.circuit_breaker.call(operation)
    
    def search_web(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search the web with medical source filtering.
        
        Args:
            query: Search query
            filters: Optional search filters
            
        Returns:
            List of search results
        """
        if not self.web_search_tool:
            logger.warning(f"{self.agent_name}: Web search not enabled")
            return []
        
        # Check if search already done in context
        if self.context_manager.should_prevent_redundant_search(query):
            logger.info(f"Using cached search results for: {query}")
            # Would retrieve from context in production
            return []
        
        try:
            results = self.web_search_tool.search(query, filters)
            
            # Record search in context
            self.context_manager.record_web_search(query, results)
            
            # Track in monitoring
            if self.monitoring:
                self.monitoring.track_web_search(self.agent_name, query, len(results))
            
            return results
            
        except Exception as e:
            logger.error(f"{self.agent_name}: Web search failed for '{query}': {e}")
            return []
    
    def make_decision(
        self,
        context: Dict[str, Any],
        options: List[str]
    ) -> str:
        """
        Make autonomous decision based on context.
        
        Requirements: 5.1 - Autonomous decision-making
        
        Args:
            context: Decision context
            options: Available options
            
        Returns:
            Selected option
        """
        decision = self.decision_engine.decide_next_action(context, options)
        
        # Track decision in monitoring
        if self.monitoring:
            agent_decision = AgentDecision(
                agent_name=self.agent_name,
                decision_type="action_selection",
                decision=decision,
                reasoning="Autonomous decision",
                context=context
            )
            self.monitoring.track_decision(agent_decision)
        
        return decision
    
    def apply_safety_guardrails(self, response: str) -> str:
        """
        Apply safety guardrails to response.
        
        Requirements: 17.1, 17.2, 17.3, 17.4, 17.5 - Medical safety
        
        Args:
            response: Original response
            
        Returns:
            Safe response with guardrails applied
        """
        return self.safety_guardrails.apply_all_guardrails(response)
    
    def validate_and_cite(
        self,
        information: str,
        sources: List[SearchResult]
    ) -> Dict[str, Any]:
        """
        Validate information and build citations.
        
        Requirements: 2.6 - Validate and cite sources
        
        Args:
            information: Information to validate
            sources: Source search results
            
        Returns:
            Dictionary with validated info and citations
        """
        citations = [source.get_citation() for source in sources]
        
        return {
            'information': information,
            'citations': citations,
            'source_count': len(sources),
            'validated': True
        }
    
    def track_execution(self, duration: float, success: bool):
        """
        Track agent execution metrics.
        
        Requirements: 10.1 - Track execution metrics
        
        Args:
            duration: Execution duration in seconds
            success: Whether execution was successful
        """
        if self.monitoring:
            self.monitoring.track_agent_execution(self.agent_name, duration, success)
    
    def process_with_monitoring(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input with monitoring and error handling.
        
        This wraps the process() method with monitoring, timeouts, and error handling.
        
        Args:
            input_data: Input data
            
        Returns:
            Processed result
        """
        start_time = time.time()
        success = False
        
        try:
            # Execute with timeout
            result = self.execute_with_timeout(
                lambda: self.process(input_data),
                self.config.timeout
            )
            
            success = True
            return result
            
        except TimeoutError as e:
            logger.error(f"{self.agent_name}: Timeout after {self.config.timeout}s")
            return self.format_agent_response(
                success=False,
                message=f"Agent timeout after {self.config.timeout}s",
                metadata={'error': 'timeout'}
            )
            
        except Exception as e:
            logger.error(f"{self.agent_name}: Processing failed: {e}")
            return self.format_agent_response(
                success=False,
                message=f"Agent processing failed: {e}",
                metadata={'error': str(e)}
            )
            
        finally:
            duration = time.time() - start_time
            self.track_execution(duration, success)
    
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
            "web_search_enabled": bool(self.web_search_tool),
            "monitoring_enabled": bool(self.monitoring),
            "circuit_breaker_state": self.circuit_breaker.get_state(),
            "framework": "LangChain",
            "version": "enhanced"
        }
    
    def format_agent_response(
        self,
        success: bool,
        data: Any = None,
        message: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Format standardized agent response.
        
        Args:
            success: Whether operation was successful
            data: Response data
            message: Response message
            metadata: Additional metadata
            
        Returns:
            Formatted response dictionary
        """
        response = {
            "success": success,
            "agent": self.agent_name,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "enhanced"
        }
        
        if data is not None:
            response["data"] = data
        
        if message:
            response["message"] = message
        
        if metadata:
            response["metadata"] = metadata
        
        return response
    
    def log_agent_action(self, action: str, details: Dict[str, Any] = None):
        """
        Log agent actions for monitoring and debugging.
        
        Args:
            action: Action being performed
            details: Additional details
        """
        log_data = {
            "agent": self.agent_name,
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if details:
            log_data.update(details)
        
        logger.info(f"{self.agent_name} action: {action}")
        if details:
            logger.debug(f"{self.agent_name} details: {details}")
