"""
Audit Logging System for agent monitoring.

Provides comprehensive audit logging for autonomous decisions, safety interventions,
API key access, and errors with context.

Requirements: 5.8, 9.8, 11.5, 17.8
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger('health_ai.agents.infrastructure')


class AuditEventType(Enum):
    """Types of audit events."""
    AUTONOMOUS_DECISION = "autonomous_decision"
    SAFETY_INTERVENTION = "safety_intervention"
    API_KEY_ACCESS = "api_key_access"
    ERROR = "error"
    AGENT_EXECUTION = "agent_execution"
    WEB_SEARCH = "web_search"
    GEMINI_USAGE = "gemini_usage"
    CONTEXT_CHANGE = "context_change"


@dataclass
class AuditLogEntry:
    """
    Audit log entry.
    
    Captures all relevant information about an auditable event.
    """
    event_type: str
    timestamp: str
    agent_name: Optional[str]
    event_data: Dict[str, Any]
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    severity: str = "info"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class AuditLogger:
    """
    Audit logging system for comprehensive event tracking.
    
    Requirements:
    - 5.8: Log all autonomous decisions
    - 9.8: Log all errors with context
    - 11.5: Log all API key access
    - 17.8: Log all safety interventions
    """
    
    def __init__(self, firebase_db=None):
        """
        Initialize audit logger.
        
        Args:
            firebase_db: Optional Firebase database instance for persistence
        """
        self.firebase_db = firebase_db
        self.log_entries: List[AuditLogEntry] = []
        self.max_memory_entries = 1000  # Keep last 1000 entries in memory
        
        logger.info("AuditLogger initialized")
    
    def log_autonomous_decision(
        self,
        agent_name: str,
        decision_type: str,
        decision: str,
        reasoning: str,
        context: Dict[str, Any],
        confidence: float = 1.0,
        session_id: Optional[str] = None
    ):
        """
        Log autonomous agent decision.
        
        Requirements: 5.8 - Log all autonomous decisions made
        
        Args:
            agent_name: Name of agent making decision
            decision_type: Type of decision (next_action, escalate, search, etc.)
            decision: The decision made
            reasoning: Reasoning behind the decision
            context: Context data used for decision
            confidence: Confidence score (0-1)
            session_id: Optional session identifier
        """
        entry = AuditLogEntry(
            event_type=AuditEventType.AUTONOMOUS_DECISION.value,
            timestamp=datetime.utcnow().isoformat(),
            agent_name=agent_name,
            session_id=session_id,
            event_data={
                'decision_type': decision_type,
                'decision': decision,
                'reasoning': reasoning,
                'context': context,
                'confidence': confidence
            }
        )
        
        self._add_entry(entry)
        
        logger.info(
            f"Autonomous decision logged: {agent_name} - {decision_type}: {decision}"
        )
    
    def log_safety_intervention(
        self,
        agent_name: str,
        intervention_type: str,
        original_content: str,
        modified_content: str,
        reason: str,
        session_id: Optional[str] = None
    ):
        """
        Log safety guardrail intervention.
        
        Requirements: 17.8 - Log all safety-related interventions
        
        Args:
            agent_name: Name of agent
            intervention_type: Type of intervention (diagnosis_filter, dosage_filter, disclaimer_add, etc.)
            original_content: Original content before intervention
            modified_content: Content after intervention
            reason: Reason for intervention
            session_id: Optional session identifier
        """
        entry = AuditLogEntry(
            event_type=AuditEventType.SAFETY_INTERVENTION.value,
            timestamp=datetime.utcnow().isoformat(),
            agent_name=agent_name,
            session_id=session_id,
            severity="warning",
            event_data={
                'intervention_type': intervention_type,
                'original_content': original_content,
                'modified_content': modified_content,
                'reason': reason
            }
        )
        
        self._add_entry(entry)
        
        logger.warning(
            f"Safety intervention logged: {agent_name} - {intervention_type}"
        )
    
    def log_api_key_access(
        self,
        agent_name: str,
        key_type: str,
        success: bool,
        reason: Optional[str] = None
    ):
        """
        Log API key access attempt.
        
        Requirements: 11.5 - Log all API key access attempts
        
        Args:
            agent_name: Name of agent requesting key
            key_type: Type of API key (gemini, search, etc.)
            success: Whether access was successful
            reason: Optional reason for failure
        """
        entry = AuditLogEntry(
            event_type=AuditEventType.API_KEY_ACCESS.value,
            timestamp=datetime.utcnow().isoformat(),
            agent_name=agent_name,
            severity="warning" if not success else "info",
            event_data={
                'key_type': key_type,
                'success': success,
                'reason': reason
            }
        )
        
        self._add_entry(entry)
        
        status = "successful" if success else "failed"
        logger.info(f"API key access logged: {agent_name} - {key_type} ({status})")
    
    def log_error(
        self,
        agent_name: str,
        error_type: str,
        error_message: str,
        context: Dict[str, Any],
        stack_trace: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """
        Log error with full context.
        
        Requirements: 9.8 - Log all errors with context
        
        Args:
            agent_name: Name of agent where error occurred
            error_type: Type/class of error
            error_message: Error message
            context: Context data (input, state, etc.)
            stack_trace: Optional stack trace
            session_id: Optional session identifier
        """
        entry = AuditLogEntry(
            event_type=AuditEventType.ERROR.value,
            timestamp=datetime.utcnow().isoformat(),
            agent_name=agent_name,
            session_id=session_id,
            severity="error",
            event_data={
                'error_type': error_type,
                'error_message': error_message,
                'context': context,
                'stack_trace': stack_trace
            }
        )
        
        self._add_entry(entry)
        
        logger.error(
            f"Error logged: {agent_name} - {error_type}: {error_message}"
        )
    
    def log_agent_execution(
        self,
        agent_name: str,
        operation: str,
        duration: float,
        success: bool,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ):
        """
        Log agent execution.
        
        Args:
            agent_name: Name of agent
            operation: Operation performed
            duration: Execution duration in seconds
            success: Whether execution was successful
            input_data: Input data (sanitized)
            output_data: Output data (sanitized)
            session_id: Optional session identifier
        """
        entry = AuditLogEntry(
            event_type=AuditEventType.AGENT_EXECUTION.value,
            timestamp=datetime.utcnow().isoformat(),
            agent_name=agent_name,
            session_id=session_id,
            event_data={
                'operation': operation,
                'duration': duration,
                'success': success,
                'input_data': self._sanitize_data(input_data),
                'output_data': self._sanitize_data(output_data) if output_data else None
            }
        )
        
        self._add_entry(entry)
    
    def log_web_search(
        self,
        agent_name: str,
        query: str,
        results_count: int,
        sources: List[str],
        session_id: Optional[str] = None
    ):
        """
        Log web search activity.
        
        Args:
            agent_name: Name of agent
            query: Search query
            results_count: Number of results
            sources: List of source URLs
            session_id: Optional session identifier
        """
        entry = AuditLogEntry(
            event_type=AuditEventType.WEB_SEARCH.value,
            timestamp=datetime.utcnow().isoformat(),
            ag