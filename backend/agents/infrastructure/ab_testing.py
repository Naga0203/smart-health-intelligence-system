"""
A/B Testing Infrastructure for agent migration.

Enables comparison of old and new agent implementations,
output comparison logging, and metrics collection.

Requirements: 19.4
"""

import logging
import json
import hashlib
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from .feature_flags import get_feature_flags

logger = logging.getLogger('health_ai.agents.infrastructure')


@dataclass
class ABTestResult:
    """Result from A/B test comparison."""
    
    agent_name: str
    test_id: str
    timestamp: str
    
    # Input
    input_hash: str
    input_summary: str
    
    # Old implementation
    old_output: Any
    old_duration: float
    old_success: bool
    old_error: Optional[str]
    
    # New implementation
    new_output: Any
    new_duration: float
    new_success: bool
    new_error: Optional[str]
    
    # Comparison
    outputs_match: bool
    performance_delta: float  # new - old (negative = faster)
    quality_score_old: Optional[float]
    quality_score_new: Optional[float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class ABTestLogger:
    """
    Logger for A/B test results.
    
    Requirements: 19.4 - Output comparison logging
    """
    
    def __init__(self, log_file: str = 'ab_test_results.jsonl'):
        """
        Initialize A/B test logger.
        
        Args:
            log_file: Path to log file (JSONL format)
        """
        self.log_file = log_file
        
    def log_result(self, result: ABTestResult):
        """
        Log A/B test result.
        
        Args:
            result: ABTestResult to log
        """
        try:
            with open(self.log_file, 'a') as f:
                f.write(result.to_json() + '\n')
            
            logger.info(f"A/B test result logged: {result.agent_name} - {result.test_id}")
        except Exception as e:
            logger.error(f"Failed to log A/B test result: {e}")
    
    def get_results(self, agent_name: Optional[str] = None, limit: int = 100) -> list:
        """
        Get A/B test results.
        
        Args:
            agent_name: Filter by agent name (optional)
            limit: Maximum number of results
            
        Returns:
            List of ABTestResult dictionaries
        """
        results = []
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    result = json.loads(line)
                    
                    if agent_name and result.get('agent_name') != agent_name:
                        continue
                    
                    results.append(result)
                    
                    if len(results) >= limit:
                        break
        except FileNotFoundError:
            logger.warning(f"A/B test log file not found: {self.log_file}")
        except Exception as e:
            logger.error(f"Failed to read A/B test results: {e}")
        
        return results


class ABTestComparator:
    """
    Comparator for A/B test outputs.
    
    Requirements: 19.4 - Output comparison
    """
    
    @staticmethod
    def compare_outputs(old_output: Any, new_output: Any) -> bool:
        """
        Compare outputs from old and new implementations.
        
        Args:
            old_output: Output from old implementation
            new_output: Output from new implementation
            
        Returns:
            True if outputs are equivalent
        """
        # Handle None cases
        if old_output is None and new_output is None:
            return True
        if old_output is None or new_output is None:
            return False
        
        # Handle dict outputs
        if isinstance(old_output, dict) and isinstance(new_output, dict):
            return ABTestComparator._compare_dicts(old_output, new_output)
        
        # Handle list outputs
        if isinstance(old_output, list) and isinstance(new_output, list):
            return ABTestComparator._compare_lists(old_output, new_output)
        
        # Handle string outputs
        if isinstance(old_output, str) and isinstance(new_output, str):
            return ABTestComparator._compare_strings(old_output, new_output)
        
        # Fallback to equality
        return old_output == new_output
    
    @staticmethod
    def _compare_dicts(old: dict, new: dict, ignore_keys: set = None) -> bool:
        """Compare dictionary outputs."""
        if ignore_keys is None:
            ignore_keys = {'timestamp', 'execution_time', 'request_id'}
        
        old_filtered = {k: v for k, v in old.items() if k not in ignore_keys}
        new_filtered = {k: v for k, v in new.items() if k not in ignore_keys}
        
        return old_filtered == new_filtered
    
    @staticmethod
    def _compare_lists(old: list, new: list) -> bool:
        """Compare list outputs."""
        if len(old) != len(new):
            return False
        
        return all(ABTestComparator.compare_outputs(o, n) for o, n in zip(old, new))
    
    @staticmethod
    def _compare_strings(old: str, new: str, similarity_threshold: float = 0.95) -> bool:
        """
        Compare string outputs with fuzzy matching.
        
        Allows for minor differences in formatting or wording.
        """
        # Exact match
        if old == new:
            return True
        
        # Normalize whitespace
        old_normalized = ' '.join(old.split())
        new_normalized = ' '.join(new.split())
        
        if old_normalized == new_normalized:
            return True
        
        # Calculate similarity (simple character-based)
        if len(old_normalized) == 0 and len(new_normalized) == 0:
            return True
        
        max_len = max(len(old_normalized), len(new_normalized))
        if max_len == 0:
            return True
        
        # Count matching characters
        matches = sum(1 for a, b in zip(old_normalized, new_normalized) if a == b)
        similarity = matches / max_len
        
        return similarity >= similarity_threshold
    
    @staticmethod
    def calculate_quality_score(output: Any, agent_name: str) -> Optional[float]:
        """
        Calculate quality score for output.
        
        Args:
            output: Agent output
            agent_name: Name of the agent
            
        Returns:
            Quality score (0-1) or None if not applicable
        """
        if not isinstance(output, dict):
            return None
        
        # Check for confidence score
        if 'confidence' in output:
            return float(output['confidence'])
        
        # Check for quality score
        if 'quality_score' in output:
            return float(output['quality_score'])
        
        # Check for completeness indicators
        score = 0.0
        checks = 0
        
        if 'error' in output:
            if output['error']:
                score += 0.0
            else:
                score += 1.0
            checks += 1
        
        if 'data' in output:
            if output['data']:
                score += 1.0
            checks += 1
        
        if 'citations' in output:
            if output['citations']:
                score += 1.0
            checks += 1
        
        return score / checks if checks > 0 else None


class ABTestRunner:
    """
    Runner for A/B tests.
    
    Requirements: 19.4 - A/B testing infrastructure
    """
    
    def __init__(self):
        """Initialize A/B test runner."""
        self.flags = get_feature_flags()
        self.logger = ABTestLogger()
        self.comparator = ABTestComparator()
    
    def run_ab_test(
        self,
        agent_name: str,
        input_data: Dict[str, Any],
        old_implementation: callable,
        new_implementation: callable
    ) -> ABTestResult:
        """
        Run A/B test comparing old and new implementations.
        
        Args:
            agent_name: Name of the agent
            input_data: Input data for the agent
            old_implementation: Callable for old implementation
            new_implementation: Callable for new implementation
            
        Returns:
            ABTestResult with comparison data
        """
        # Generate test ID
        input_str = json.dumps(input_data, sort_keys=True)
        input_hash = hashlib.md5(input_str.encode()).hexdigest()
        test_id = f"{agent_name}_{input_hash[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Run old implementation
        old_output, old_duration, old_success, old_error = self._run_implementation(
            old_implementation, input_data
        )
        
        # Run new implementation
        new_output, new_duration, new_success, new_error = self._run_implementation(
            new_implementation, input_data
        )
        
        # Compare outputs
        outputs_match = self.comparator.compare_outputs(old_output, new_output)
        performance_delta = new_duration - old_duration
        
        # Calculate quality scores
        quality_score_old = self.comparator.calculate_quality_score(old_output, agent_name)
        quality_score_new = self.comparator.calculate_quality_score(new_output, agent_name)
        
        # Create result
        result = ABTestResult(
            agent_name=agent_name,
            test_id=test_id,
            timestamp=datetime.now().isoformat(),
            input_hash=input_hash,
            input_summary=str(input_data)[:200],
            old_output=old_output,
            old_duration=old_duration,
            old_success=old_success,
            old_error=old_error,
            new_output=new_output,
            new_duration=new_duration,
            new_success=new_success,
            new_error=new_error,
            outputs_match=outputs_match,
            performance_delta=performance_delta,
            quality_score_old=quality_score_old,
            quality_score_new=quality_score_new
        )
        
        # Log result
        self.logger.log_result(result)
        
        # Log summary
        if outputs_match:
            logger.info(f"A/B test PASSED: {agent_name} - outputs match")
        else:
            logger.warning(f"A/B test MISMATCH: {agent_name} - outputs differ")
        
        if performance_delta < 0:
            logger.info(f"Performance IMPROVED: {abs(performance_delta):.2f}s faster")
        elif performance_delta > 0:
            logger.warning(f"Performance DEGRADED: {performance_delta:.2f}s slower")
        
        return result
    
    def _run_implementation(
        self,
        implementation: callable,
        input_data: Dict[str, Any]
    ) -> Tuple[Any, float, bool, Optional[str]]:
        """
        Run a single implementation and measure performance.
        
        Returns:
            Tuple of (output, duration, success, error)
        """
        import time
        
        start_time = time.time()
        output = None
        success = False
        error = None
        
        try:
            output = implementation(input_data)
            success = True
        except Exception as e:
            error = str(e)
            logger.error(f"Implementation failed: {e}")
        
        duration = time.time() - start_time
        
        return output, duration, success, error
    
    def should_run_ab_test(self, agent_name: str) -> bool:
        """
        Check if A/B test should run for this agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            True if A/B testing is enabled
        """
        return self.flags.is_ab_testing(agent_name)


# Global A/B test runner
_ab_test_runner: Optional[ABTestRunner] = None


def get_ab_test_runner() -> ABTestRunner:
    """Get global A/B test runner instance."""
    global _ab_test_runner
    
    if _ab_test_runner is None:
        _ab_test_runner = ABTestRunner()
    
    return _ab_test_runner
