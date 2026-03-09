"""
Alerting System for agent monitoring.

Provides alerting capabilities for performance degradation, high error rates,
API failures, and safety violations.

Requirements: 10.7
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from .monitoring import MonitoringService

logger = logging.getLogger('health_ai.agents.infrastructure')


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of alerts."""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    HIGH_ERROR_RATE = "high_error_rate"
    API_FAILURE = "api_failure"
    SAFETY_VIOLATION = "safety_violation"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


@dataclass
class AlertRule:
    """
    Rule for triggering alerts.
    
    Defines conditions that trigger alerts and the actions to take.
    """
    name: str
    alert_type: AlertType
    severity: AlertSeverity
    condition: Callable[[Dict[str, Any]], bool]
    message_template: str
    cooldown_minutes: int = 15  # Minimum time between alerts of same type
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def should_trigger(self, context: Dict[str, Any]) -> bool:
        """
        Check if alert should be triggered.
        
        Args:
            context: Context data for evaluation
            
        Returns:
            True if alert should be triggered
        """
        if not self.enabled:
            return False
        
        # Check cooldown period
        if self.last_triggered:
            cooldown = timedelta(minutes=self.cooldown_minutes)
            if datetime.utcnow() - self.last_triggered < cooldown:
                return False
        
        # Evaluate condition
        try:
            return self.condition(context)
        except Exception as e:
            logger.error(f"Error evaluating alert rule {self.name}: {e}")
            return False
    
    def trigger(self, context: Dict[str, Any]) -> str:
        """
        Trigger the alert and generate message.
        
        Args:
            context: Context data for message generation
            
        Returns:
            Alert message
        """
        self.last_triggered = datetime.utcnow()
        self.trigger_count += 1
        
        # Format message with context
        try:
            message = self.message_template.format(**context)
        except KeyError as e:
            message = f"{self.message_template} (missing context: {e})"
        
        return message


class AlertingSystem:
    """
    Alerting system for monitoring agent behavior.
    
    Requirements: 10.7 - Send alerts for various conditions
    """
    
    def __init__(self, monitoring_service: MonitoringService):
        """
        Initialize alerting system.
        
        Args:
            monitoring_service: MonitoringService instance
        """
        self.monitoring = monitoring_service
        self.rules: List[AlertRule] = []
        self.alert_handlers: List[Callable[[Dict[str, Any]], None]] = []
        
        # Set up default alert rules
        self._setup_default_rules()
        
        logger.info("AlertingSystem initialized")
    
    def _setup_default_rules(self):
        """Set up default alert rules."""
        
        # Performance degradation alert
        self.add_rule(AlertRule(
            name="slow_agent_execution",
            alert_type=AlertType.PERFORMANCE_DEGRADATION,
            severity=AlertSeverity.WARNING,
            condition=lambda ctx: ctx.get('average_duration', 0) > 30.0,
            message_template="Agent {agent_name} average execution time is {average_duration:.2f}s (threshold: 30s)",
            cooldown_minutes=15
        ))
        
        # High error rate alert
        self.add_rule(AlertRule(
            name="high_failure_rate",
            alert_type=AlertType.HIGH_ERROR_RATE,
            severity=AlertSeverity.WARNING,
            condition=lambda ctx: ctx.get('failure_rate', 0) > 30.0,
            message_template="Agent {agent_name} failure rate is {failure_rate:.1f}% (threshold: 30%)",
            cooldown_minutes=10
        ))
        
        # Critical error rate alert
        self.add_rule(AlertRule(
            name="critical_failure_rate",
            alert_type=AlertType.HIGH_ERROR_RATE,
            severity=AlertSeverity.CRITICAL,
            condition=lambda ctx: ctx.get('failure_rate', 0) > 50.0,
            message_template="CRITICAL: Agent {agent_name} failure rate is {failure_rate:.1f}% (threshold: 50%)",
            cooldown_minutes=5
        ))
        
        # API failure alert
        self.add_rule(AlertRule(
            name="gemini_api_failure",
            alert_type=AlertType.API_FAILURE,
            severity=AlertSeverity.CRITICAL,
            condition=lambda ctx: ctx.get('api_name') == 'gemini' and ctx.get('consecutive_failures', 0) >= 3,
            message_template="Gemini API experiencing failures: {consecutive_failures} consecutive failures",
            cooldown_minutes=5
        ))
        
        # Web search API failure alert
        self.add_rule(AlertRule(
            name="search_api_failure",
            alert_type=AlertType.API_FAILURE,
            severity=AlertSeverity.WARNING,
            condition=lambda ctx: ctx.get('api_name') == 'search' and ctx.get('consecutive_failures', 0) >= 3,
            message_template="Search API experiencing failures: {consecutive_failures} consecutive failures",
            cooldown_minutes=10
        ))
        
        # Safety violation alert
        self.add_rule(AlertRule(
            name="safety_violation",
            alert_type=AlertType.SAFETY_VIOLATION,
            severity=AlertSeverity.CRITICAL,
            condition=lambda ctx: ctx.get('violation_type') is not None,
            message_template="Safety violation detected: {violation_type} in agent {agent_name}",
            cooldown_minutes=0  # Always alert on safety violations
        ))
        
        # Circuit breaker open alert
        self.add_rule(AlertRule(
            name="circuit_breaker_open",
            alert_type=AlertType.CIRCUIT_BREAKER_OPEN,
            severity=AlertSeverity.CRITICAL,
            condition=lambda ctx: ctx.get('circuit_state') == 'open',
            message_template="Circuit breaker opened for {service_name} after {failure_count} failures",
            cooldown_minutes=5
        ))
        
        # Rate limit exceeded alert
        self.add_rule(AlertRule(
            name="rate_limit_exceeded",
            alert_type=AlertType.RATE_LIMIT_EXCEEDED,
            severity=AlertSeverity.WARNING,
            condition=lambda ctx: ctx.get('rate_limit_exceeded', False),
            message_template="Rate limit exceeded for {service_name}: {requests_count} requests in {time_window}",
            cooldown_minutes=15
        ))
    
    def add_rule(self, rule: AlertRule):
        """
        Add alert rule.
        
        Args:
            rule: AlertRule instance
        """
        self.rules.append(rule)
        logger.info(f"Alert rule added: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove alert rule by name.
        
        Args:
            rule_name: Name of rule to remove
            
        Returns:
            True if rule was removed
        """
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                self.rules.pop(i)
                logger.info(f"Alert rule removed: {rule_name}")
                return True
        return False
    
    def enable_rule(self, rule_name: str):
        """Enable alert rule."""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = True
                logger.info(f"Alert rule enabled: {rule_name}")
                return
    
    def disable_rule(self, rule_name: str):
        """Disable alert rule."""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = False
                logger.info(f"Alert rule disabled: {rule_name}")
                return
    
    def add_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """
        Add alert handler.
        
        Handlers are called when alerts are triggered.
        
        Args:
            handler: Callable that receives alert dictionary
        """
        self.alert_handlers.append(handler)
        logger.info(f"Alert handler added: {handler.__name__}")
    
    def check_rules(self, context: Dict[str, Any]):
        """
        Check all alert rules against context.
        
        Args:
            context: Context data for rule evaluation
        """
        for rule in self.rules:
            if rule.should_trigger(context):
                message = rule.trigger(context)
                self._send_alert(rule, message, context)
    
    def check_agent_performance(self, agent_name: str):
        """
        Check agent performance and trigger alerts if needed.
        
        Args:
            agent_name: Name of agent to check
        """
        metrics = self.monitoring.get_agent_metrics(agent_name)
        if not metrics:
            return
        
        context = {
            'agent_name': agent_name,
            'average_duration': metrics.average_duration,
            'failure_rate': metrics.get_failure_rate(),
            'total_executions': metrics.total_executions
        }
        
        self.check_rules(context)
    
    def report_api_failure(self, api_name: str, consecutive_failures: int):
        """
        Report API failure for alerting.
        
        Args:
            api_name: Name of API (gemini, search, etc.)
            consecutive_failures: Number of consecutive failures
        """
        context = {
            'api_name': api_name,
            'consecutive_failures': consecutive_failures
        }
        
        self.check_rules(context)
    
    def report_safety_violation(self, agent_name: str, violation_type: str, details: str):
        """
        Report safety violation for alerting.
        
        Args:
            agent_name: Name of agent
            violation_type: Type of violation
            details: Violation details
        """
        context = {
            'agent_name': agent_name,
            'violation_type': violation_type,
            'details': details
        }
        
        self.check_rules(context)
        
        # Always log safety violations
        logger.critical(
            f"Safety violation in {agent_name}: {violation_type} - {details}"
        )
    
    def report_circuit_breaker(self, service_name: str, circuit_state: str, failure_count: int):
        """
        Report circuit breaker state change.
        
        Args:
            service_name: Name of service
            circuit_state: Circuit state (open, closed, half-open)
            failure_count: Number of failures
        """
        context = {
            'service_name': service_name,
            'circuit_state': circuit_state,
            'failure_count': failure_count
        }
        
        self.check_rules(context)
    
    def report_rate_limit(self, service_name: str, requests_count: int, time_window: str):
        """
        Report rate limit exceeded.
        
        Args:
            service_name: Name of service
            requests_count: Number of requests
            time_window: Time window (e.g., "1 minute")
        """
        context = {
            'service_name': service_name,
            'rate_limit_exceeded': True,
            'requests_count': requests_count,
            'time_window': time_window
        }
        
        self.check_rules(context)
    
    def _send_alert(self, rule: AlertRule, message: str, context: Dict[str, Any]):
        """
        Send alert through monitoring service and handlers.
        
        Args:
            rule: Alert rule that triggered
            message: Alert message
            context: Alert context
        """
        # Send through monitoring service
        self.monitoring.send_alert(
            alert_type=rule.alert_type.value,
            message=message,
            severity=rule.severity.value
        )
        
        # Call custom handlers
        alert_data = {
            'rule_name': rule.name,
            'alert_type': rule.alert_type.value,
            'severity': rule.severity.value,
            'message': message,
            'context': context,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        for handler in self.alert_handlers:
            try:
                handler(alert_data)
            except Exception as e:
                logger.error(f"Error in alert handler {handler.__name__}: {e}")
    
    def get_rule_stats(self) -> List[Dict[str, Any]]:
        """
        Get statistics for all alert rules.
        
        Returns:
            List of rule statistics
        """
        return [
            {
                'name': rule.name,
                'alert_type': rule.alert_type.value,
                'severity': rule.severity.value,
                'enabled': rule.enabled,
                'trigger_count': rule.trigger_count,
                'last_triggered': rule.last_triggered.isoformat() if rule.last_triggered else None
            }
            for rule in self.rules
        ]
    
    def reset_rule_stats(self):
        """Reset trigger counts and timestamps for all rules."""
        for rule in self.rules:
            rule.trigger_count = 0
            rule.last_triggered = None
        logger.info("Alert rule statistics reset")


# Example alert handlers

def log_alert_handler(alert: Dict[str, Any]):
    """
    Simple handler that logs alerts.
    
    Args:
        alert: Alert dictionary
    """
    severity = alert['severity']
    message = alert['message']
    
    if severity == 'critical':
        logger.critical(f"ALERT: {message}")
    elif severity == 'warning':
        logger.warning(f"ALERT: {message}")
    else:
        logger.info(f"ALERT: {message}")


def email_alert_handler(alert: Dict[str, Any]):
    """
    Handler that sends email alerts (placeholder).
    
    In production, this would integrate with an email service.
    
    Args:
        alert: Alert dictionary
    """
    # Placeholder for email integration
    logger.info(f"Would send email alert: {alert['message']}")


def slack_alert_handler(alert: Dict[str, Any]):
    """
    Handler that sends Slack alerts (placeholder).
    
    In production, this would integrate with Slack API.
    
    Args:
        alert: Alert dictionary
    """
    # Placeholder for Slack integration
    logger.info(f"Would send Slack alert: {alert['message']}")
