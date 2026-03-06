"""
Circuit Breaker for external service resilience.

Implements the circuit breaker pattern to prevent cascading failures
when external services (Gemini AI, web search APIs) are unavailable.

Requirements: 9.4
"""

import time
import logging
from typing import Callable, Any, Optional
from .config import CircuitConfig

logger = logging.getLogger('health_ai.agents.infrastructure')


class CircuitOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Circuit breaker for external service calls.
    
    States:
    - closed: Normal operation, requests pass through
    - open: Service is failing, requests are blocked
    - half_open: Testing if service has recovered
    
    Requirements: 9.4 - Circuit breakers prevent cascading failures
    """
    
    def __init__(self, config: Optional[CircuitConfig] = None):
        """
        Initialize circuit breaker.
        
        Args:
            config: Circuit breaker configuration
        """
        self.config = config or CircuitConfig()
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open
        self.open_until: Optional[float] = None
        
        logger.info(
            f"CircuitBreaker initialized: threshold={self.config.failure_threshold}, "
            f"timeout={self.config.timeout}s"
        )
    
    def call(self, operation: Callable[[], Any]) -> Any:
        """
        Execute operation through circuit breaker.
        
        Requirements: 9.4 - Circuit breaker prevents cascading failures
        
        Args:
            operation: Callable to execute
            
        Returns:
            Result from operation
            
        Raises:
            CircuitOpenError: If circuit is open
        """
        if self.is_open():
            remaining = self.open_until - time.time() if self.open_until else 0
            raise CircuitOpenError(
                f"Circuit breaker is open. Retry in {remaining:.1f}s. "
                f"Failures: {self.failure_count}/{self.config.failure_threshold}"
            )
        
        try:
            result = operation()
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise
    
    def record_success(self):
        """
        Record successful operation.
        
        Requirements: 9.4 - Circuit breaker state management
        """
        if self.state == "half_open":
            # Service has recovered, close the circuit
            logger.info("Circuit breaker closing after successful operation in half-open state")
            self.state = "closed"
            self.failure_count = 0
            self.last_failure_time = None
            self.open_until = None
        elif self.state == "closed":
            # Gradually reduce failure count on success
            if self.failure_count > 0:
                self.failure_count = max(0, self.failure_count - 1)
                logger.debug(f"Circuit breaker failure count reduced to {self.failure_count}")
    
    def record_failure(self):
        """
        Record failed operation.
        
        Requirements: 9.4 - Circuit breaker opens after threshold
        """
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        logger.warning(
            f"Circuit breaker recorded failure {self.failure_count}/{self.config.failure_threshold}"
        )
        
        if self.failure_count >= self.config.failure_threshold:
            self._open_circuit()
    
    def _open_circuit(self):
        """Open the circuit breaker."""
        self.state = "open"
        self.open_until = time.time() + self.config.timeout
        
        logger.critical(
            f"Circuit breaker OPENED after {self.failure_count} failures. "
            f"Will attempt recovery in {self.config.timeout}s"
        )
    
    def is_open(self) -> bool:
        """
        Check if circuit is open (blocking calls).
        
        Requirements: 9.4 - Circuit breaker prevents calls when open
        
        Returns:
            True if circuit is open, False otherwise
        """
        if self.state == "closed":
            return False
        
        if self.state == "open":
            # Check if timeout period has passed
            if self.open_until and time.time() >= self.open_until:
                logger.info("Circuit breaker entering half-open state")
                self.state = "half_open"
                return False
            return True
        
        # half_open state allows requests through
        return False
    
    def get_state(self) -> str:
        """Get current circuit breaker state."""
        return self.state
    
    def get_failure_count(self) -> int:
        """Get current failure count."""
        return self.failure_count
    
    def reset(self):
        """
        Manually reset the circuit breaker.
        
        This should be used cautiously, typically only for testing
        or administrative purposes.
        """
        logger.info("Circuit breaker manually reset")
        self.state = "closed"
        self.failure_count = 0
        self.last_failure_time = None
        self.open_until = None
    
    def get_status(self) -> dict:
        """
        Get circuit breaker status.
        
        Returns:
            Status dictionary with current state and metrics
        """
        status = {
            'state': self.state,
            'failure_count': self.failure_count,
            'failure_threshold': self.config.failure_threshold,
            'is_open': self.is_open()
        }
        
        if self.last_failure_time:
            status['last_failure_time'] = self.last_failure_time
            status['time_since_last_failure'] = time.time() - self.last_failure_time
        
        if self.open_until:
            status['open_until'] = self.open_until
            status['time_until_half_open'] = max(0, self.open_until - time.time())
        
        return status
