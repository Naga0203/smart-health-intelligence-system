"""
Migration Tracking System for agent refactor.

Tracks migration status, performance metrics, and error rates
for old vs new agent implementations.

Requirements: 19.6
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
from .feature_flags import get_feature_flags, AgentImplementation
from .ab_testing import ABTestLogger

logger = logging.getLogger('health_ai.agents.infrastructure')


@dataclass
class AgentMetrics:
    """Metrics for a single agent implementation."""
    
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_duration: float = 0.0
    min_duration: Optional[float] = None
    max_duration: Optional[float] = None
    
    def add_execution(self, duration: float, success: bool):
        """Add execution metrics."""
        self.total_executions += 1
        
        if success:
            self.successful_executions += 1
        else:
            self.failed_executions += 1
        
        self.total_duration += duration
        
        if self.min_duration is None or duration < self.min_duration:
            self.min_duration = duration
        
        if self.max_duration is None or duration > self.max_duration:
            self.max_duration = duration
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate."""
        return 1.0 - self.success_rate
    
    @property
    def average_duration(self) -> float:
        """Calculate average duration."""
        if self.total_executions == 0:
            return 0.0
        return self.total_duration / self.total_executions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            **asdict(self),
            'success_rate': self.success_rate,
            'error_rate': self.error_rate,
            'average_duration': self.average_duration
        }


@dataclass
class MigrationStatus:
    """Migration status for a single agent."""
    
    agent_name: str
    current_version: str
    migration_stage: str  # not_started, testing, migrated, rolled_back
    
    # Timestamps
    testing_started: Optional[str] = None
    migration_completed: Optional[str] = None
    last_rollback: Optional[str] = None
    
    # Metrics
    old_metrics: AgentMetrics = None
    new_metrics: AgentMetrics = None
    
    # A/B test results
    ab_tests_run: int = 0
    ab_tests_passed: int = 0
    ab_tests_failed: int = 0
    
    # Issues
    issues: List[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.old_metrics is None:
            self.old_metrics = AgentMetrics()
        if self.new_metrics is None:
            self.new_metrics = AgentMetrics()
        if self.issues is None:
            self.issues = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'agent_name': self.agent_name,
            'current_version': self.current_version,
            'migration_stage': self.migration_stage,
            'testing_started': self.testing_started,
            'migration_completed': self.migration_completed,
            'last_rollback': self.last_rollback,
            'old_metrics': self.old_metrics.to_dict(),
            'new_metrics': self.new_metrics.to_dict(),
            'ab_tests': {
                'total': self.ab_tests_run,
                'passed': self.ab_tests_passed,
                'failed': self.ab_tests_failed,
                'pass_rate': self.ab_tests_passed / self.ab_tests_run if self.ab_tests_run > 0 else 0.0
            },
            'issues': self.issues
        }


class MigrationTracker:
    """
    Tracker for agent migration progress.
    
    Requirements: 19.6 - Track migration status for each agent
    """
    
    def __init__(self, storage_file: str = 'migration_status.json'):
        """
        Initialize migration tracker.
        
        Args:
            storage_file: Path to storage file
        """
        self.storage_file = storage_file
        self.flags = get_feature_flags()
        self.ab_logger = ABTestLogger()
        self.statuses: Dict[str, MigrationStatus] = {}
        
        self._load_status()
    
    def _load_status(self):
        """Load migration status from storage."""
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                
                for agent_name, status_dict in data.items():
                    # Reconstruct metrics
                    old_metrics = AgentMetrics(**status_dict['old_metrics'])
                    new_metrics = AgentMetrics(**status_dict['new_metrics'])
                    
                    # Reconstruct status
                    status = MigrationStatus(
                        agent_name=status_dict['agent_name'],
                        current_version=status_dict['current_version'],
                        migration_stage=status_dict['migration_stage'],
                        testing_started=status_dict.get('testing_started'),
                        migration_completed=status_dict.get('migration_completed'),
                        last_rollback=status_dict.get('last_rollback'),
                        old_metrics=old_metrics,
                        new_metrics=new_metrics,
                        ab_tests_run=status_dict.get('ab_tests_run', 0),
                        ab_tests_passed=status_dict.get('ab_tests_passed', 0),
                        ab_tests_failed=status_dict.get('ab_tests_failed', 0),
                        issues=status_dict.get('issues', [])
                    )
                    
                    self.statuses[agent_name] = status
            
            logger.info(f"Migration status loaded from {self.storage_file}")
        except FileNotFoundError:
            logger.info("No existing migration status found, starting fresh")
        except Exception as e:
            logger.error(f"Failed to load migration status: {e}")
    
    def _save_status(self):
        """Save migration status to storage."""
        try:
            data = {
                agent_name: status.to_dict()
                for agent_name, status in self.statuses.items()
            }
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("Migration status saved")
        except Exception as e:
            logger.error(f"Failed to save migration status: {e}")
    
    def get_agent_status(self, agent_name: str) -> MigrationStatus:
        """
        Get migration status for an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            MigrationStatus for the agent
        """
        if agent_name not in self.statuses:
            # Create new status
            version = self.flags.get_agent_version(agent_name)
            
            if version == AgentImplementation.OLD:
                stage = 'not_started'
            elif version == AgentImplementation.BOTH:
                stage = 'testing'
            else:
                stage = 'migrated'
            
            self.statuses[agent_name] = MigrationStatus(
                agent_name=agent_name,
                current_version=version.value,
                migration_stage=stage
            )
        
        return self.statuses[agent_name]
    
    def update_agent_version(self, agent_name: str):
        """
        Update agent version from feature flags.
        
        Args:
            agent_name: Name of the agent
        """
        status = self.get_agent_status(agent_name)
        version = self.flags.get_agent_version(agent_name)
        
        old_version = status.current_version
        status.current_version = version.value
        
        # Update migration stage
        if version == AgentImplementation.OLD:
            if old_version != 'old':
                status.migration_stage = 'rolled_back'
                status.last_rollback = datetime.now().isoformat()
        elif version == AgentImplementation.BOTH:
            if status.migration_stage == 'not_started':
                status.migration_stage = 'testing'
                status.testing_started = datetime.now().isoformat()
        elif version == AgentImplementation.NEW:
            status.migration_stage = 'migrated'
            status.migration_completed = datetime.now().isoformat()
        
        self._save_status()
        logger.info(f"Agent {agent_name} version updated: {old_version} -> {version.value}")
    
    def record_execution(
        self,
        agent_name: str,
        version: str,
        duration: float,
        success: bool
    ):
        """
        Record agent execution metrics.
        
        Requirements: 19.6 - Track performance metrics for old vs new
        
        Args:
            agent_name: Name of the agent
            version: 'old' or 'new'
            duration: Execution duration in seconds
            success: Whether execution succeeded
        """
        status = self.get_agent_status(agent_name)
        
        if version == 'old':
            status.old_metrics.add_execution(duration, success)
        elif version == 'new':
            status.new_metrics.add_execution(duration, success)
        
        self._save_status()
    
    def record_ab_test_result(self, agent_name: str, passed: bool):
        """
        Record A/B test result.
        
        Args:
            agent_name: Name of the agent
            passed: Whether outputs matched
        """
        status = self.get_agent_status(agent_name)
        
        status.ab_tests_run += 1
        
        if passed:
            status.ab_tests_passed += 1
        else:
            status.ab_tests_failed += 1
        
        self._save_status()
    
    def add_issue(self, agent_name: str, issue: str):
        """
        Add issue to agent migration.
        
        Args:
            agent_name: Name of the agent
            issue: Issue description
        """
        status = self.get_agent_status(agent_name)
        
        timestamp = datetime.now().isoformat()
        status.issues.append(f"[{timestamp}] {issue}")
        
        self._save_status()
        logger.warning(f"Issue added for {agent_name}: {issue}")
    
    def get_overall_status(self) -> Dict[str, Any]:
        """
        Get overall migration status.
        
        Returns:
            Overall status summary
        """
        # Update all agent versions
        for agent_name in self.flags.AGENT_FLAGS.keys():
            self.update_agent_version(agent_name)
        
        total_agents = len(self.flags.AGENT_FLAGS)
        not_started = sum(1 for s in self.statuses.values() if s.migration_stage == 'not_started')
        testing = sum(1 for s in self.statuses.values() if s.migration_stage == 'testing')
        migrated = sum(1 for s in self.statuses.values() if s.migration_stage == 'migrated')
        rolled_back = sum(1 for s in self.statuses.values() if s.migration_stage == 'rolled_back')
        
        return {
            'total_agents': total_agents,
            'not_started': not_started,
            'testing': testing,
            'migrated': migrated,
            'rolled_back': rolled_back,
            'completion_percentage': (migrated / total_agents * 100) if total_agents > 0 else 0,
            'agents': {
                name: status.to_dict()
                for name, status in self.statuses.items()
            }
        }
    
    def get_comparison_report(self, agent_name: str) -> Dict[str, Any]:
        """
        Get comparison report for old vs new implementation.
        
        Requirements: 19.6 - Track performance metrics and error rates
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Comparison report
        """
        status = self.get_agent_status(agent_name)
        
        old = status.old_metrics
        new = status.new_metrics
        
        # Calculate improvements
        performance_improvement = None
        if old.average_duration > 0 and new.average_duration > 0:
            performance_improvement = (
                (old.average_duration - new.average_duration) / old.average_duration * 100
            )
        
        error_rate_change = None
        if old.total_executions > 0 and new.total_executions > 0:
            error_rate_change = new.error_rate - old.error_rate
        
        return {
            'agent_name': agent_name,
            'migration_stage': status.migration_stage,
            'old_implementation': {
                'executions': old.total_executions,
                'success_rate': old.success_rate,
                'error_rate': old.error_rate,
                'avg_duration': old.average_duration,
                'min_duration': old.min_duration,
                'max_duration': old.max_duration
            },
            'new_implementation': {
                'executions': new.total_executions,
                'success_rate': new.success_rate,
                'error_rate': new.error_rate,
                'avg_duration': new.average_duration,
                'min_duration': new.min_duration,
                'max_duration': new.max_duration
            },
            'comparison': {
                'performance_improvement_percent': performance_improvement,
                'error_rate_change': error_rate_change,
                'new_is_faster': new.average_duration < old.average_duration if old.average_duration > 0 and new.average_duration > 0 else None,
                'new_is_more_reliable': new.error_rate < old.error_rate if old.total_executions > 0 and new.total_executions > 0 else None
            },
            'ab_testing': {
                'tests_run': status.ab_tests_run,
                'pass_rate': status.ab_tests_passed / status.ab_tests_run if status.ab_tests_run > 0 else 0
            },
            'issues': status.issues
        }
    
    def generate_migration_report(self, output_file: str = 'migration_report.json'):
        """
        Generate comprehensive migration report.
        
        Args:
            output_file: Path to output file
        """
        overall = self.get_overall_status()
        
        comparisons = {
            agent_name: self.get_comparison_report(agent_name)
            for agent_name in self.flags.AGENT_FLAGS.keys()
        }
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'overall_status': overall,
            'agent_comparisons': comparisons
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Migration report generated: {output_file}")
        
        return report


# Global migration tracker
_migration_tracker: Optional[MigrationTracker] = None


def get_migration_tracker() -> MigrationTracker:
    """Get global migration tracker instance."""
    global _migration_tracker
    
    if _migration_tracker is None:
        _migration_tracker = MigrationTracker()
    
    return _migration_tracker
