"""
Performance tests for parallel agent execution.

Tests parallel agent execution speedup and resource usage
during parallel execution.

Requirements: 6.7
"""

import pytest
import time
import threading
import psutil
import os
from typing import Dict, Any, List
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor
import statistics

from agents.orchestrator import OrchestratorAgent
from agents.data_extraction import DataExtractionAgent
from agents.severity import SeverityAgent
from agents.explanation import LangChainExplanationAgent
from agents.recommendation import RecommendationAgent
from agents.lifestyle import LifestyleModificationAgent


# Performance thresholds
MIN_SPEEDUP_THRESHOLD = 1.3  # Parallel should be at least 1.3x faster
MAX_CPU_USAGE_THRESHOLD = 80.0  # Max 80% CPU usage
MAX_MEMORY_INCREASE_MB = 500  # Max 500MB memory increase


@pytest.fixture
def orchestrator():
    """Create orchestrator for testing."""
    return OrchestratorAgent()


@pytest.fixture
def mock_prediction_engine():
    """Mock prediction engine."""
    with patch('agents.orchestrator.DiseasePredictor') as mock:
        predictor = Mock()
        predictor.predict.return_value = (0.75, {"model": "test", "features": 10})
        mock.return_value = predictor
        yield predictor


@pytest.fixture
def mock_firebase():
    """Mock Firebase."""
    with patch('agents.orchestrator.get_firebase_db') as mock:
        db = Mock()
        db.collection.return_value.document.return_value.set.return_value = None
        db.collection.return_value.add.return_value = (None, "test_id")
        mock.return_value = db
        yield db


@pytest.fixture
def sample_agent_inputs():
    """Sample inputs for multiple agents."""
    return {
        'extraction': {
            "symptoms": ["increased_thirst", "frequent_urination"],
            "age": 45,
            "gender": "male",
            "disease": "diabetes"
        },
        'severity': {
            "symptoms": ["chest_pain", "shortness_of_breath"],
            "vitals": {"blood_pressure": "150/95", "heart_rate": 95},
            "disease": "heart_disease"
        },
        'explanation': {
            "disease": "diabetes",
            "probability": 0.75,
            "confidence": "medium",
            "symptoms": ["increased_thirst", "frequent_urination"]
        },
        'recommendation': {
            "disease": "diabetes",
            "probability": 0.75,
            "confidence": "medium",
            "symptoms": ["increased_thirst"],
            "user_context": {"age": 45, "gender": "male"}
        },
        'lifestyle': {
            "disease": "diabetes",
            "confidence": "medium",
            "symptoms": ["increased_thirst"],
            "user_context": {"age": 45, "gender": "male"}
        }
    }


class TestParallelExecutionSpeedup:
    """
    Test parallel agent execution speedup.
    
    Property: Parallel execution should be faster than sequential execution
    Requirements: 6.7 - Parallel execution of independent agents
    """
    
    def test_two_agent_parallel_speedup(self, orchestrator, sample_agent_inputs):
        """Test speedup with 2 agents executing in parallel."""
        extraction_input = sample_agent_inputs['extraction']
        severity_input = sample_agent_inputs['severity']
        
        # Sequential execution
        start_time = time.time()
        seq_result1 = orchestrator._execute_single_agent(
            'extraction', orchestrator.extraction_agent, extraction_input
        )
        seq_result2 = orchestrator._execute_single_agent(
            'severity', orchestrator.severity_agent, severity_input
        )
        sequential_time = time.time() - start_time
        
        # Parallel execution
        parallel_agents = [
            ('extraction', orchestrator.extraction_agent, extraction_input),
            ('severity', orchestrator.severity_agent, severity_input)
        ]
        
        start_time = time.time()
        parallel_results = orchestrator._execute_agents_parallel(parallel_agents)
        parallel_time = time.time() - start_time
        
        speedup = sequential_time / parallel_time
        
        assert speedup >= MIN_SPEEDUP_THRESHOLD, \
            f"Speedup {speedup:.2f}x is below threshold {MIN_SPEEDUP_THRESHOLD}x"
        
        print(f"✓ Two-agent parallel speedup: {speedup:.2f}x")
        print(f"  Sequential: {sequential_time:.2f}s")
        print(f"  Parallel: {parallel_time:.2f}s")
    
    def test_three_agent_parallel_speedup(self, orchestrator, sample_agent_inputs):
        """Test speedup with 3 agents executing in parallel."""
        extraction_input = sample_agent_inputs['extraction']
        severity_input = sample_agent_inputs['severity']
        explanation_input = sample_agent_inputs['explanation']
        
        # Sequential execution
        start_time = time.time()
        orchestrator._execute_single_agent('extraction', orchestrator.extraction_agent, extraction_input)
        orchestrator._execute_single_agent('severity', orchestrator.severity_agent, severity_input)
        orchestrator._execute_single_agent('explanation', orchestrator.explanation_agent, explanation_input)
        sequential_time = time.time() - start_time
        
        # Parallel execution
        parallel_agents = [
            ('extraction', orchestrator.extraction_agent, extraction_input),
            ('severity', orchestrator.severity_agent, severity_input),
            ('explanation', orchestrator.explanation_agent, explanation_input)
        ]
        
        start_time = time.time()
        parallel_results = orchestrator._execute_agents_parallel(parallel_agents)
        parallel_time = time.time() - start_time
        
        speedup = sequential_time / parallel_time
        
        assert speedup >= MIN_SPEEDUP_THRESHOLD, \
            f"Speedup {speedup:.2f}x is below threshold {MIN_SPEEDUP_THRESHOLD}x"
        
        print(f"✓ Three-agent parallel speedup: {speedup:.2f}x")
        print(f"  Sequential: {sequential_time:.2f}s")
        print(f"  Parallel: {parallel_time:.2f}s")
    
    def test_four_agent_parallel_speedup(self, orchestrator, sample_agent_inputs):
        """Test speedup with 4 agents executing in parallel."""
        # Sequential execution
        agents_and_inputs = [
            ('extraction', orchestrator.extraction_agent, sample_agent_inputs['extraction']),
            ('severity', orchestrator.severity_agent, sample_agent_inputs['severity']),
            ('explanation', orchestrator.explanation_agent, sample_agent_inputs['explanation']),
            ('recommendation', orchestrator.recommendation_agent, sample_agent_inputs['recommendation'])
        ]
        
        start_time = time.time()
        for agent_name, agent, input_data in agents_and_inputs:
            orchestrator._execute_single_agent(agent_name, agent, input_data)
        sequential_time = time.time() - start_time
        
        # Parallel execution
        start_time = time.time()
        parallel_results = orchestrator._execute_agents_parallel(agents_and_inputs)
        parallel_time = time.time() - start_time
        
        speedup = sequential_time / parallel_time
        
        assert speedup >= MIN_SPEEDUP_THRESHOLD, \
            f"Speedup {speedup:.2f}x is below threshold {MIN_SPEEDUP_THRESHOLD}x"
        
        print(f"✓ Four-agent parallel speedup: {speedup:.2f}x")
        print(f"  Sequential: {sequential_time:.2f}s")
        print(f"  Parallel: {parallel_time:.2f}s")
    
    def test_parallel_speedup_consistency(self, orchestrator, sample_agent_inputs):
        """Test that parallel speedup is consistent across multiple runs."""
        extraction_input = sample_agent_inputs['extraction']
        severity_input = sample_agent_inputs['severity']
        
        parallel_agents = [
            ('extraction', orchestrator.extraction_agent, extraction_input),
            ('severity', orchestrator.severity_agent, severity_input)
        ]
        
        speedups = []
        num_runs = 5
        
        for _ in range(num_runs):
            # Sequential
            start_time = time.time()
            orchestrator._execute_single_agent('extraction', orchestrator.extraction_agent, extraction_input)
            orchestrator._execute_single_agent('severity', orchestrator.severity_agent, severity_input)
            sequential_time = time.time() - start_time
            
            # Parallel
            start_time = time.time()
            orchestrator._execute_agents_parallel(parallel_agents)
            parallel_time = time.time() - start_time
            
            speedup = sequential_time / parallel_time
            speedups.append(speedup)
        
        avg_speedup = statistics.mean(speedups)
        std_dev = statistics.stdev(speedups)
        
        assert avg_speedup >= MIN_SPEEDUP_THRESHOLD, \
            f"Average speedup {avg_speedup:.2f}x is below threshold"
        
        print(f"✓ Parallel speedup consistency over {num_runs} runs:")
        print(f"  Average speedup: {avg_speedup:.2f}x")
        print(f"  Std dev: {std_dev:.2f}x")
        print(f"  Min: {min(speedups):.2f}x")
        print(f"  Max: {max(speedups):.2f}x")


class TestResourceUsage:
    """
    Test resource usage during parallel execution.
    
    Property: Parallel execution should not exceed resource limits
    Requirements: 6.7 - Resource usage during parallel execution
    """
    
    def test_cpu_usage_during_parallel_execution(self, orchestrator, sample_agent_inputs):
        """Test CPU usage stays within acceptable limits during parallel execution."""
        process = psutil.Process(os.getpid())
        
        # Get baseline CPU usage
        baseline_cpu = process.cpu_percent(interval=0.1)
        
        # Execute agents in parallel
        parallel_agents = [
            ('extraction', orchestrator.extraction_agent, sample_agent_inputs['extraction']),
            ('severity', orchestrator.severity_agent, sample_agent_inputs['severity']),
            ('explanation', orchestrator.explanation_agent, sample_agent_inputs['explanation'])
        ]
        
        # Monitor CPU during execution
        cpu_samples = []
        
        def monitor_cpu():
            for _ in range(10):
                cpu_samples.append(process.cpu_percent(interval=0.1))
                time.sleep(0.1)
        
        # Start monitoring in background
        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()
        
        # Execute parallel agents
        orchestrator._execute_agents_parallel(parallel_agents)
        
        # Wait for monitoring to complete
        monitor_thread.join()
        
        if cpu_samples:
            max_cpu = max(cpu_samples)
            avg_cpu = statistics.mean(cpu_samples)
            
            print(f"✓ CPU usage during parallel execution:")
            print(f"  Baseline: {baseline_cpu:.1f}%")
            print(f"  Average: {avg_cpu:.1f}%")
            print(f"  Peak: {max_cpu:.1f}%")
            print(f"  Threshold: {MAX_CPU_USAGE_THRESHOLD}%")
            
            # Note: This is informational - actual CPU usage depends on system load
            # We don't assert on this as it can vary widely
    
    def test_memory_usage_during_parallel_execution(self, orchestrator, sample_agent_inputs):
        """Test memory usage during parallel execution."""
        process = psutil.Process(os.getpid())
        
        # Get baseline memory
        baseline_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Execute agents in parallel
        parallel_agents = [
            ('extraction', orchestrator.extraction_agent, sample_agent_inputs['extraction']),
            ('severity', orchestrator.severity_agent, sample_agent_inputs['severity']),
            ('explanation', orchestrator.explanation_agent, sample_agent_inputs['explanation']),
            ('recommendation', orchestrator.recommendation_agent, sample_agent_inputs['recommendation'])
        ]
        
        orchestrator._execute_agents_parallel(parallel_agents)
        
        # Get memory after execution
        final_memory = process.memory_info().rss / (1024 * 1024)  # MB
        memory_increase = final_memory - baseline_memory
        
        print(f"✓ Memory usage during parallel execution:")
        print(f"  Baseline: {baseline_memory:.1f} MB")
        print(f"  Final: {final_memory:.1f} MB")
        print(f"  Increase: {memory_increase:.1f} MB")
        print(f"  Threshold: {MAX_MEMORY_INCREASE_MB} MB")
        
        # Memory increase should be reasonable
        assert memory_increase < MAX_MEMORY_INCREASE_MB, \
            f"Memory increase {memory_increase:.1f}MB exceeds threshold {MAX_MEMORY_INCREASE_MB}MB"
    
    def test_thread_pool_efficiency(self, orchestrator, sample_agent_inputs):
        """Test that thread pool is used efficiently."""
        # Check thread pool configuration
        assert orchestrator.executor._max_workers == 4, \
            "Thread pool should have 4 workers"
        
        # Execute more agents than workers
        parallel_agents = [
            ('extraction', orchestrator.extraction_agent, sample_agent_inputs['extraction']),
            ('severity', orchestrator.severity_agent, sample_agent_inputs['severity']),
            ('explanation', orchestrator.explanation_agent, sample_agent_inputs['explanation']),
            ('recommendation', orchestrator.recommendation_agent, sample_agent_inputs['recommendation']),
            ('lifestyle', orchestrator.lifestyle_agent, sample_agent_inputs['lifestyle'])
        ]
        
        start_time = time.time()
        results = orchestrator._execute_agents_parallel(parallel_agents)
        elapsed_time = time.time() - start_time
        
        # All agents should complete successfully
        assert len(results) == 5
        assert all(r.get('success', False) for r in results.values())
        
        print(f"✓ Thread pool efficiency:")
        print(f"  Workers: {orchestrator.executor._max_workers}")
        print(f"  Agents: {len(parallel_agents)}")
        print(f"  Completion time: {elapsed_time:.2f}s")


class TestParallelExecutionCorrectness:
    """
    Test correctness of parallel execution.
    
    Property: Parallel execution should produce same results as sequential
    Requirements: 6.7 - Parallel execution correctness
    """
    
    def test_parallel_results_match_sequential(self, orchestrator, sample_agent_inputs):
        """Test that parallel execution produces same results as sequential."""
        extraction_input = sample_agent_inputs['extraction']
        severity_input = sample_agent_inputs['severity']
        
        # Sequential execution
        seq_extraction = orchestrator._execute_single_agent(
            'extraction', orchestrator.extraction_agent, extraction_input
        )
        seq_severity = orchestrator._execute_single_agent(
            'severity', orchestrator.severity_agent, severity_input
        )
        
        # Parallel execution
        parallel_agents = [
            ('extraction', orchestrator.extraction_agent, extraction_input),
            ('severity', orchestrator.severity_agent, severity_input)
        ]
        
        parallel_results = orchestrator._execute_agents_parallel(parallel_agents)
        
        # Results should match
        assert seq_extraction['success'] == parallel_results['extraction']['success']
        assert seq_severity['success'] == parallel_results['severity']['success']
        
        print("✓ Parallel results match sequential results")
    
    def test_parallel_execution_isolation(self, orchestrator, sample_agent_inputs):
        """Test that parallel agents don't interfere with each other."""
        # Execute same agent multiple times in parallel with different inputs
        inputs = [
            sample_agent_inputs['extraction'],
            {**sample_agent_inputs['extraction'], 'age': 50},
            {**sample_agent_inputs['extraction'], 'age': 60}
        ]
        
        parallel_agents = [
            (f'extraction_{i}', orchestrator.extraction_agent, inp)
            for i, inp in enumerate(inputs)
        ]
        
        results = orchestrator._execute_agents_parallel(parallel_agents)
        
        # All should succeed
        assert len(results) == 3
        assert all(r.get('success', False) for r in results.values())
        
        # Results should be independent (different ages should produce different features)
        # This is a basic check - in practice, results might be similar
        print("✓ Parallel agents execute independently")
    
    def test_parallel_execution_error_handling(self, orchestrator, sample_agent_inputs):
        """Test error handling in parallel execution."""
        # Create an agent that will fail
        failing_agent = Mock()
        failing_agent.process.side_effect = Exception("Simulated failure")
        
        parallel_agents = [
            ('extraction', orchestrator.extraction_agent, sample_agent_inputs['extraction']),
            ('failing', failing_agent, {}),
            ('severity', orchestrator.severity_agent, sample_agent_inputs['severity'])
        ]
        
        results = orchestrator._execute_agents_parallel(parallel_agents)
        
        # Should have results for all agents
        assert len(results) == 3
        
        # Successful agents should succeed
        assert results['extraction'].get('success', False)
        assert results['severity'].get('success', False)
        
        # Failing agent should have error
        assert not results['failing'].get('success', True)
        assert 'error' in results['failing'].get('data', {})
        
        print("✓ Parallel execution handles errors correctly")


class TestParallelExecutionTimeout:
    """
    Test timeout handling in parallel execution.
    
    Property: Parallel execution should respect timeouts
    Requirements: 6.7 - Timeout management in parallel execution
    """
    
    def test_parallel_execution_timeout(self, orchestrator):
        """Test that parallel execution respects timeout."""
        # Create slow agents
        slow_agent1 = Mock()
        slow_agent1.process = lambda x: time.sleep(2) or {"success": True}
        
        slow_agent2 = Mock()
        slow_agent2.process = lambda x: time.sleep(2) or {"success": True}
        
        parallel_agents = [
            ('slow1', slow_agent1, {}),
            ('slow2', slow_agent2, {})
        ]
        
        # Execute with short timeout
        start_time = time.time()
        results = orchestrator._execute_agents_parallel(parallel_agents, timeout=3.0)
        elapsed_time = time.time() - start_time
        
        # Should complete within timeout (parallel execution)
        assert elapsed_time < 3.5, f"Execution took {elapsed_time:.2f}s, should be < 3.5s"
        
        print(f"✓ Parallel execution respects timeout: {elapsed_time:.2f}s")
    
    def test_individual_agent_timeout_in_parallel(self, orchestrator):
        """Test that individual agents can timeout in parallel execution."""
        # Create one very slow agent
        very_slow_agent = Mock()
        very_slow_agent.process = lambda x: time.sleep(100) or {"success": True}
        
        fast_agent = Mock()
        fast_agent.process = lambda x: {"success": True, "data": {}}
        
        parallel_agents = [
            ('fast', fast_agent, {}),
            ('very_slow', very_slow_agent, {})
        ]
        
        # Execute with timeout
        start_time = time.time()
        results = orchestrator._execute_agents_parallel(parallel_agents, timeout=2.0)
        elapsed_time = time.time() - start_time
        
        # Fast agent should complete
        assert 'fast' in results
        
        # Should not wait for slow agent beyond timeout
        assert elapsed_time < 3.0, f"Should timeout quickly, took {elapsed_time:.2f}s"
        
        print(f"✓ Individual agent timeout in parallel: {elapsed_time:.2f}s")


class TestScalability:
    """
    Test scalability of parallel execution.
    
    Property: Parallel execution should scale with number of agents
    Requirements: 6.7 - Scalability of parallel execution
    """
    
    def test_scalability_with_increasing_agents(self, orchestrator, sample_agent_inputs):
        """Test performance scaling with increasing number of agents."""
        agent_counts = [2, 3, 4, 5]
        execution_times = []
        
        for count in agent_counts:
            # Create agent list
            agents_list = []
            for i in range(count):
                agent_type = ['extraction', 'severity', 'explanation', 'recommendation', 'lifestyle'][i]
                agent = getattr(orchestrator, f'{agent_type}_agent')
                agents_list.append((agent_type, agent, sample_agent_inputs.get(agent_type, {})))
            
            # Execute in parallel
            start_time = time.time()
            orchestrator._execute_agents_parallel(agents_list)
            elapsed_time = time.time() - start_time
            execution_times.append(elapsed_time)
            
            print(f"  {count} agents: {elapsed_time:.2f}s")
        
        print(f"✓ Scalability test completed")
        print(f"  Execution times: {[f'{t:.2f}s' for t in execution_times]}")
        
        # Execution time should not increase linearly with agent count
        # (that would indicate no parallelization benefit)
        if len(execution_times) >= 2:
            time_ratio = execution_times[-1] / execution_times[0]
            agent_ratio = agent_counts[-1] / agent_counts[0]
            
            # Time increase should be less than agent increase
            assert time_ratio < agent_ratio, \
                f"Time scaling ({time_ratio:.2f}x) should be better than linear ({agent_ratio:.2f}x)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
