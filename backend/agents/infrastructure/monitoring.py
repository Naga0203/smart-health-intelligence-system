"""
Monitoring Service for agent observability.

Tracks agent execution metrics, web search usage, Gemini API usage,
autonomous decisions, and provides alerting capabilities.

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.7
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .models import AgentMetrics, AgentDecision

logger = logging.getLogger('health_ai.agents.infrastructure')


class MonitoringService:
    """
    Service for monitoring agent behavior and performance.
    
    Requirements:
    - 10.1: Track execution time for each agent
    - 10.2: Track web searches performed
    - 10.3: Track Gemini AI API usage and costs
    - 10.4: Log autonomous decisions
    - 10.5: Track success and failure rates
    - 10.7: Send alerts for performance degradation
    """
    
    def __init__(self, firebase_db=None):
        """
        Initialize monitoring service.
        
        Args:
            firebase_db: Optional Firebase database instance for persistence
        """
        self.firebase_db = firebase_db
        self.metrics: Dict[str, AgentMetrics] = {}
        self.decisions: list[AgentDecision] = []
        self.alerts: list[Dict[str, Any]] = []
        
        # Alert thresholds
        self.failure_rate_threshold = 0.3  # 30%
        self.avg_duration_threshold = 30.0  # seconds
        
        logger.info("MonitoringService initialized")
    
    def track_agent_execution(self, agent_name: str, duration: float, success: bool):
        """
        Track agent execution metrics.
        
        Requirements: 10.1, 10.5 - Track execution time and success rates
        
        Args:
            agent_name: Name of the agent
            duration: Execution duration in seconds
            success: Whether execution was successful
        """
        if agent_name not in self.metrics:
            self.metrics[agent_name] = AgentMetrics(agent_name=agent_name)
        
        metrics = self.metrics[agent_name]
        metrics.record_execution(success, duration)
        
        logger.info(
            f"Agent {agent_name} execution tracked: "
            f"duration={duration:.2f}s, success={success}"
        )
        
        # Check for performance degradation
        self._check_performance_alerts(agent_name, metrics)
        
        # Persist to Firebase if available
        if self.firebase_db:
            self._persist_metrics(agent_name, metrics)
    
    def track_web_search(self, agent_name: str, query: str, results_count: int):
        """
        Track web search usage.
        
        Requirements: 10.2 - Track web searches performed by each agent
        
        Args:
            agent_name: Name of the agent
            query: Search query
            results_count: Number of results returned
        """
        if agent_name not in self.metrics:
            self.metrics[agent_name] = AgentMetrics(agent_name=agent_name)
        
        self.metrics[agent_name].record_web_search()
        
        logger.info(
            f"Web search tracked for {agent_name}: "
            f"query='{query}', results={results_count}"
        )
        
        # Log search details
        if self.firebase_db:
            self._log_web_search(agent_name, query, results_count)
    
    def track_gemini_usage(self, agent_name: str, tokens: int, cost: float):
        """
        Track Gemini AI API usage and costs.
        
        Requirements: 10.3 - Track Gemini AI API usage and costs
        
        Args:
            agent_name: Name of the agent
            tokens: Number of tokens used
            cost: Estimated cost in USD
        """
        if agent_name not in self.metrics:
            self.metrics[agent_name] = AgentMetrics(agent_name=agent_name)
        
        self.metrics[agent_name].record_gemini_tokens(tokens)
        
        logger.info(
            f"Gemini usage tracked for {agent_name}: "
            f"tokens={tokens}, cost=${cost:.4f}"
        )
        
        # Log usage details
        if self.firebase_db:
            self._log_gemini_usage(agent_name, tokens, cost)
    
    def track_decision(self, decision: AgentDecision):
        """
        Track autonomous agent decision.
        
        Requirements: 10.4 - Log autonomous decisions with reasoning
        
        Args:
            decision: AgentDecision instance
        """
        self.decisions.append(decision)
        
        logger.info(
            f"Decision tracked for {decision.agent_name}: "
            f"type={decision.decision_type}, decision='{decision.decision}'"
        )
        
        # Persist decision
        if self.firebase_db:
            self._persist_decision(decision)
    
    def get_agent_metrics(self, agent_name: str) -> Optional[AgentMetrics]:
        """
        Get metrics for specific agent.
        
        Requirements: 10.5 - Provide agent performance metrics
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            AgentMetrics instance or None if not found
        """
        return self.metrics.get(agent_name)
    
    def get_all_metrics(self) -> Dict[str, AgentMetrics]:
        """Get metrics for all agents."""
        return self.metrics.copy()
    
    def get_decisions(self, agent_name: Optional[str] = None) -> list[AgentDecision]:
        """
        Get autonomous decisions, optionally filtered by agent.
        
        Args:
            agent_name: Optional agent name to filter by
            
        Returns:
            List of AgentDecision instances
        """
        if agent_name:
            return [d for d in self.decisions if d.agent_name == agent_name]
        return self.decisions.copy()
    
    def send_alert(self, alert_type: str, message: str, severity: str = "warning"):
        """
        Send alert for performance degradation or errors.
        
        Requirements: 10.7 - Send alerts when performance degrades
        
        Args:
            alert_type: Type of alert (performance, error, etc.)
            message: Alert message
            severity: Alert severity (info, warning, critical)
        """
        alert = {
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.alerts.append(alert)
        
        # Log based on severity
        if severity == "critical":
            logger.critical(f"ALERT [{alert_type}]: {message}")
        elif severity == "warning":
            logger.warning(f"ALERT [{alert_type}]: {message}")
        else:
            logger.info(f"ALERT [{alert_type}]: {message}")
        
        # Persist alert
        if self.firebase_db:
            self._persist_alert(alert)
    
    def _check_performance_alerts(self, agent_name: str, metrics: AgentMetrics):
        """
        Check if agent performance has degraded and send alerts.
        
        Requirements: 10.7 - Alert on performance degradation
        
        Args:
            agent_name: Name of the agent
            metrics: Agent metrics
        """
        # Check failure rate
        failure_rate = metrics.get_failure_rate() / 100.0
        if failure_rate > self.failure_rate_threshold:
            self.send_alert(
                alert_type="high_failure_rate",
                message=f"Agent {agent_name} failure rate is {failure_rate*100:.1f}% "
                       f"(threshold: {self.failure_rate_threshold*100:.1f}%)",
                severity="warning"
            )
        
        # Check average duration
        if metrics.average_duration > self.avg_duration_threshold:
            self.send_alert(
                alert_type="slow_execution",
                message=f"Agent {agent_name} average duration is {metrics.average_duration:.2f}s "
                       f"(threshold: {self.avg_duration_threshold}s)",
                severity="warning"
            )
    
    def get_alerts(self, severity: Optional[str] = None) -> list[Dict[str, Any]]:
        """
        Get alerts, optionally filtered by severity.
        
        Args:
            severity: Optional severity to filter by
            
        Returns:
            List of alert dictionaries
        """
        if severity:
            return [a for a in self.alerts if a['severity'] == severity]
        return self.alerts.copy()
    
    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts.clear()
        logger.info("All alerts cleared")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get monitoring summary across all agents.
        
        Returns:
            Summary dictionary with aggregate metrics
        """
        total_executions = sum(m.total_executions for m in self.metrics.values())
        total_successes = sum(m.successful_executions for m in self.metrics.values())
        total_failures = sum(m.failed_executions for m in self.metrics.values())
        total_searches = sum(m.web_searches_performed for m in self.metrics.values())
        total_tokens = sum(m.gemini_tokens_used for m in self.metrics.values())
        
        return {
            'total_agents': len(self.metrics),
            'total_executions': total_executions,
            'total_successes': total_successes,
            'total_failures': total_failures,
            'overall_success_rate': (total_successes / total_executions * 100) if total_executions > 0 else 0,
            'total_web_searches': total_searches,
            'total_gemini_tokens': total_tokens,
            'total_decisions': len(self.decisions),
            'total_alerts': len(self.alerts),
            'critical_alerts': len([a for a in self.alerts if a['severity'] == 'critical'])
        }
    
    def _persist_metrics(self, agent_name: str, metrics: AgentMetrics):
        """Persist metrics to Firebase."""
        try:
            if self.firebase_db:
                self.firebase_db.collection('agent_metrics').document(agent_name).set(
                    metrics.to_dict()
                )
        except Exception as e:
            logger.error(f"Failed to persist metrics for {agent_name}: {e}")
    
    def _persist_decision(self, decision: AgentDecision):
        """Persist decision to Firebase."""
        try:
            if self.firebase_db:
                self.firebase_db.collection('agent_decisions').add(
                    decision.to_dict()
                )
        except Exception as e:
            logger.error(f"Failed to persist decision: {e}")
    
    def _persist_alert(self, alert: Dict[str, Any]):
        """Persist alert to Firebase."""
        try:
            if self.firebase_db:
                self.firebase_db.collection('agent_alerts').add(alert)
        except Exception as e:
            logger.error(f"Failed to persist alert: {e}")
    
    def _log_web_search(self, agent_name: str, query: str, results_count: int):
        """Log web search details to Firebase."""
        try:
            if self.firebase_db:
                self.firebase_db.collection('web_searches').add({
                    'agent_name': agent_name,
                    'query': query,
                    'results_count': results_count,
                    'timestamp': datetime.utcnow().isoformat()
                })
        except Exception as e:
            logger.error(f"Failed to log web search: {e}")
    
    def _log_gemini_usage(self, agent_name: str, tokens: int, cost: float):
        """Log Gemini usage details to Firebase."""
        try:
            if self.firebase_db:
                self.firebase_db.collection('gemini_usage').add({
                    'agent_name': agent_name,
                    'tokens': tokens,
                    'cost': cost,
                    'timestamp': datetime.utcnow().isoformat()
                })
        except Exception as e:
            logger.error(f"Failed to log Gemini usage: {e}")
