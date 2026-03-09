"""
Monitoring Dashboards for agent observability.

Provides dashboard functionality for visualizing agent execution metrics,
web search usage, Gemini API usage, and error rates.

Requirements: 10.6
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .monitoring import MonitoringService

logger = logging.getLogger('health_ai.agents.infrastructure')


class MonitoringDashboard:
    """
    Base class for monitoring dashboards.
    
    Requirements: 10.6 - Provide real-time dashboards for agent performance
    """
    
    def __init__(self, monitoring_service: MonitoringService):
        """
        Initialize dashboard.
        
        Args:
            monitoring_service: MonitoringService instance
        """
        self.monitoring = monitoring_service
        logger.info(f"{self.__class__.__name__} initialized")
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get dashboard data.
        
        Returns:
            Dictionary containing dashboard data
        """
        raise NotImplementedError("Subclasses must implement get_data()")


class AgentExecutionDashboard(MonitoringDashboard):
    """
    Dashboard for agent execution metrics.
    
    Displays:
    - Total executions per agent
    - Success/failure rates
    - Average execution times
    - Recent execution history
    """
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get agent execution metrics for dashboard.
        
        Returns:
            Dictionary with agent execution data
        """
        all_metrics = self.monitoring.get_all_metrics()
        
        agent_data = []
        for agent_name, metrics in all_metrics.items():
            agent_data.append({
                'agent_name': agent_name,
                'total_executions': metrics.total_executions,
                'successful_executions': metrics.successful_executions,
                'failed_executions': metrics.failed_executions,
                'success_rate': metrics.get_success_rate(),
                'failure_rate': metrics.get_failure_rate(),
                'average_duration': metrics.average_duration,
                'last_execution': metrics.last_execution.isoformat() if metrics.last_execution else None
            })
        
        # Sort by total executions descending
        agent_data.sort(key=lambda x: x['total_executions'], reverse=True)
        
        summary = self.monitoring.get_summary()
        
        return {
            'title': 'Agent Execution Metrics',
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_agents': summary['total_agents'],
                'total_executions': summary['total_executions'],
                'overall_success_rate': summary['overall_success_rate']
            },
            'agents': agent_data
        }


class WebSearchDashboard(MonitoringDashboard):
    """
    Dashboard for web search usage.
    
    Displays:
    - Total searches per agent
    - Search frequency
    - Most active agents
    """
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get web search usage metrics for dashboard.
        
        Returns:
            Dictionary with web search data
        """
        all_metrics = self.monitoring.get_all_metrics()
        
        search_data = []
        total_searches = 0
        
        for agent_name, metrics in all_metrics.items():
            if metrics.web_searches_performed > 0:
                search_data.append({
                    'agent_name': agent_name,
                    'searches_performed': metrics.web_searches_performed,
                    'searches_per_execution': (
                        metrics.web_searches_performed / metrics.total_executions
                        if metrics.total_executions > 0 else 0
                    )
                })
                total_searches += metrics.web_searches_performed
        
        # Sort by searches performed descending
        search_data.sort(key=lambda x: x['searches_performed'], reverse=True)
        
        return {
            'title': 'Web Search Usage',
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_searches': total_searches,
                'agents_using_search': len(search_data)
            },
            'agents': search_data
        }


class GeminiUsageDashboard(MonitoringDashboard):
    """
    Dashboard for Gemini API usage.
    
    Displays:
    - Total tokens used per agent
    - Token usage trends
    - Cost estimates
    """
    
    # Gemini pricing (approximate, as of 2024)
    COST_PER_1K_TOKENS = 0.00025  # $0.00025 per 1K tokens for Gemini Pro
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get Gemini API usage metrics for dashboard.
        
        Returns:
            Dictionary with Gemini usage data
        """
        all_metrics = self.monitoring.get_all_metrics()
        
        usage_data = []
        total_tokens = 0
        
        for agent_name, metrics in all_metrics.items():
            if metrics.gemini_tokens_used > 0:
                cost = (metrics.gemini_tokens_used / 1000) * self.COST_PER_1K_TOKENS
                usage_data.append({
                    'agent_name': agent_name,
                    'tokens_used': metrics.gemini_tokens_used,
                    'estimated_cost': cost,
                    'tokens_per_execution': (
                        metrics.gemini_tokens_used / metrics.total_executions
                        if metrics.total_executions > 0 else 0
                    )
                })
                total_tokens += metrics.gemini_tokens_used
        
        # Sort by tokens used descending
        usage_data.sort(key=lambda x: x['tokens_used'], reverse=True)
        
        total_cost = (total_tokens / 1000) * self.COST_PER_1K_TOKENS
        
        return {
            'title': 'Gemini API Usage',
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_tokens': total_tokens,
                'total_cost': total_cost,
                'agents_using_gemini': len(usage_data)
            },
            'agents': usage_data
        }


class ErrorRateDashboard(MonitoringDashboard):
    """
    Dashboard for error rates and alerts.
    
    Displays:
    - Error rates per agent
    - Recent alerts
    - Critical issues
    """
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get error rate metrics for dashboard.
        
        Returns:
            Dictionary with error rate data
        """
        all_metrics = self.monitoring.get_all_metrics()
        
        error_data = []
        for agent_name, metrics in all_metrics.items():
            if metrics.total_executions > 0:
                error_data.append({
                    'agent_name': agent_name,
                    'total_executions': metrics.total_executions,
                    'failed_executions': metrics.failed_executions,
                    'failure_rate': metrics.get_failure_rate(),
                    'status': self._get_status(metrics.get_failure_rate())
                })
        
        # Sort by failure rate descending
        error_data.sort(key=lambda x: x['failure_rate'], reverse=True)
        
        # Get recent alerts
        alerts = self.monitoring.get_alerts()
        recent_alerts = sorted(alerts, key=lambda x: x['timestamp'], reverse=True)[:10]
        
        # Count alerts by severity
        alert_counts = {
            'critical': len([a for a in alerts if a['severity'] == 'critical']),
            'warning': len([a for a in alerts if a['severity'] == 'warning']),
            'info': len([a for a in alerts if a['severity'] == 'info'])
        }
        
        return {
            'title': 'Error Rates and Alerts',
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_alerts': len(alerts),
                'critical_alerts': alert_counts['critical'],
                'warning_alerts': alert_counts['warning']
            },
            'agents': error_data,
            'recent_alerts': recent_alerts,
            'alert_counts': alert_counts
        }
    
    def _get_status(self, failure_rate: float) -> str:
        """
        Get status based on failure rate.
        
        Args:
            failure_rate: Failure rate percentage
            
        Returns:
            Status string (healthy, warning, critical)
        """
        if failure_rate < 5.0:
            return 'healthy'
        elif failure_rate < 20.0:
            return 'warning'
        else:
            return 'critical'


class DashboardManager:
    """
    Manager for all monitoring dashboards.
    
    Provides unified access to all dashboard types.
    """
    
    def __init__(self, monitoring_service: MonitoringService):
        """
        Initialize dashboard manager.
        
        Args:
            monitoring_service: MonitoringService instance
        """
        self.monitoring = monitoring_service
        self.dashboards = {
            'agent_execution': AgentExecutionDashboard(monitoring_service),
            'web_search': WebSearchDashboard(monitoring_service),
            'gemini_usage': GeminiUsageDashboard(monitoring_service),
            'error_rates': ErrorRateDashboard(monitoring_service)
        }
        logger.info("DashboardManager initialized with all dashboards")
    
    def get_dashboard(self, dashboard_name: str) -> Optional[Dict[str, Any]]:
        """
        Get data for specific dashboard.
        
        Args:
            dashboard_name: Name of dashboard (agent_execution, web_search, gemini_usage, error_rates)
            
        Returns:
            Dashboard data dictionary or None if not found
        """
        dashboard = self.dashboards.get(dashboard_name)
        if dashboard:
            return dashboard.get_data()
        
        logger.warning(f"Dashboard not found: {dashboard_name}")
        return None
    
    def get_all_dashboards(self) -> Dict[str, Dict[str, Any]]:
        """
        Get data for all dashboards.
        
        Returns:
            Dictionary mapping dashboard names to their data
        """
        return {
            name: dashboard.get_data()
            for name, dashboard in self.dashboards.items()
        }
    
    def get_overview(self) -> Dict[str, Any]:
        """
        Get high-level overview across all dashboards.
        
        Returns:
            Overview dictionary with key metrics
        """
        summary = self.monitoring.get_summary()
        
        return {
            'title': 'Monitoring Overview',
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': {
                'total_agents': summary['total_agents'],
                'total_executions': summary['total_executions'],
                'success_rate': summary['overall_success_rate'],
                'total_web_searches': summary['total_web_searches'],
                'total_gemini_tokens': summary['total_gemini_tokens'],
                'total_decisions': summary['total_decisions'],
                'total_alerts': summary['total_alerts'],
                'critical_alerts': summary['critical_alerts']
            },
            'status': self._get_overall_status(summary)
        }
    
    def _get_overall_status(self, summary: Dict[str, Any]) -> str:
        """
        Determine overall system status.
        
        Args:
            summary: Monitoring summary
            
        Returns:
            Status string (healthy, degraded, critical)
        """
        if summary['critical_alerts'] > 0:
            return 'critical'
        elif summary['overall_success_rate'] < 90.0:
            return 'degraded'
        else:
            return 'healthy'
