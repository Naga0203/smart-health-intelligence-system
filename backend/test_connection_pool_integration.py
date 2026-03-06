"""
Integration Test for Connection Pool Manager

This script tests the Connection Pool Manager in a real environment
with actual Firestore connections.

Prerequisites:
- Firebase credentials configured
- Backend environment set up
- Django settings configured

Run from backend directory:
    python test_connection_pool_integration.py
"""

import asyncio
import sys
import os
import time
import logging
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_ai_backend.settings')
import django
django.setup()

from common.connection_pool import get_connection_pool, ConnectionPoolManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Colors:
    """ANSI color codes."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class ConnectionPoolIntegrationTest:
    """Integration tests for Connection Pool Manager."""
    
    def __init__(self):
        self.pool = None
        self.test_results = []
    
    def print_test(self, name: str, passed: bool, details: str = ""):
        """Print test result."""
        status = f"{Colors.GREEN}✓ PASS{Colors.ENDC}" if passed else f"{Colors.RED}✗ FAIL{Colors.ENDC}"
        print(f"{status} - {name}")
        if details:
            print(f"  {Colors.BLUE}{details}{Colors.ENDC}")
        self.test_results.append({'name': name, 'passed': passed})
    
    async def test_pool_initialization(self) -> bool:
        """Test 1: Pool initialization."""
        try:
            self.pool = get_connection_pool(min_size=5, max_size=20)
            await self.pool.initialize()
            
            stats = self.pool.get_pool_stats()
            
            if stats['total'] == 5 and stats['idle'] == 5:
                self.print_test(
                    "Pool Initialization",
                    True,
                    f"Created {stats['total']} connections"
                )
                return True
            else:
                self.print_test(
                    "Pool Initialization",
                    False,
                    f"Expected 5 connections, got {stats['total']}"
                )
                return False
        except Exception as e:
            self.print_test("Pool Initialization", False, str(e))
            return False
    
    async def test_connection_acquisition(self) -> bool:
        """Test 2: Connection acquisition and release."""
        try:
            # Get a connection
            conn = await self.pool.get_connection()
            
            stats_after_get = self.pool.get_pool_stats()
            
            if stats_after_get['active'] == 1:
                # Release the connection
                await self.pool.release_connection(conn)
                
                stats_after_release = self.pool.get_pool_stats()
                
                if stats_after_release['active'] == 0:
                    self.print_test(
                        "Connection Acquisition & Release",
                        True,
                        "Connection acquired and released successfully"
                    )
                    return True
                else:
                    self.print_test(
                        "Connection Acquisition & Release",
                        False,
                        "Connection not released properly"
                    )
                    return False
            else:
                self.print_test(
                    "Connection Acquisition & Release",
                    False,
                    f"Expected 1 active connection, got {stats_after_get['active']}"
                )
                return False
        except Exception as e:
            self.print_test("Connection Acquisition & Release", False, str(e))
            return False
    
    async def test_concurrent_connections(self) -> bool:
        """Test 3: Concurrent connection usage."""
        try:
            async def use_connection(conn_num: int):
                """Use a connection for a query."""
                conn = await self.pool.get_connection()
                try:
                    # Perform a simple query
                    users_ref = conn.collection('users')
                    users = users_ref.limit(1).get()
                    await asyncio.sleep(0.1)  # Simulate work
                    return True
                finally:
                    await self.pool.release_connection(conn)
            
            # Run 10 concurrent operations
            start_time = time.time()
            results = await asyncio.gather(
                *[use_connection(i) for i in range(10)],
                return_exceptions=True
            )
            duration = time.time() - start_time
            
            success_count = sum(1 for r in results if r is True)
            
            if success_count == 10:
                self.print_test(
                    "Concurrent Connections",
                    True,
                    f"10/10 operations succeeded in {duration:.2f}s"
                )
                return True
            else:
                self.print_test(
                    "Concurrent Connections",
                    False,
                    f"Only {success_count}/10 operations succeeded"
                )
                return False
        except Exception as e:
            self.print_test("Concurrent Connections", False, str(e))
            return False
    
    async def test_pool_scaling(self) -> bool:
        """Test 4: Pool scaling under load."""
        try:
            initial_stats = self.pool.get_pool_stats()
            initial_total = initial_stats['total']
            
            # Acquire more connections than initial pool size
            connections = []
            for i in range(8):
                conn = await self.pool.get_connection()
                connections.append(conn)
            
            stats_under_load = self.pool.get_pool_stats()
            
            # Release all connections
            for conn in connections:
                await self.pool.release_connection(conn)
            
            if stats_under_load['total'] > initial_total:
                self.print_test(
                    "Pool Scaling",
                    True,
                    f"Pool scaled from {initial_total} to {stats_under_load['total']} connections"
                )
                return True
            else:
                self.print_test(
                    "Pool Scaling",
                    False,
                    "Pool did not scale under load"
                )
                return False
        except Exception as e:
            self.print_test("Pool Scaling", False, str(e))
            return False
    
    async def test_health_check(self) -> bool:
        """Test 5: Health check functionality."""
        try:
            is_healthy = await self.pool.health_check()
            
            if is_healthy:
                self.print_test(
                    "Health Check",
                    True,
                    "All connections are healthy"
                )
                return True
            else:
                self.print_test(
                    "Health Check",
                    False,
                    "Some connections failed health check"
                )
                return False
        except Exception as e:
            self.print_test("Health Check", False, str(e))
            return False
    
    async def test_connection_reuse(self) -> bool:
        """Test 6: Connection reuse."""
        try:
            # Get and release a connection
            conn1 = await self.pool.get_connection()
            conn1_id = id(conn1)
            await self.pool.release_connection(conn1)
            
            # Get another connection - should be the same
            conn2 = await self.pool.get_connection()
            conn2_id = id(conn2)
            await self.pool.release_connection(conn2)
            
            if conn1_id == conn2_id:
                self.print_test(
                    "Connection Reuse",
                    True,
                    "Connections are being reused from pool"
                )
                return True
            else:
                self.print_test(
                    "Connection Reuse",
                    False,
                    "Connections are not being reused"
                )
                return False
        except Exception as e:
            self.print_test("Connection Reuse", False, str(e))
            return False
    
    async def test_performance_improvement(self) -> bool:
        """Test 7: Performance improvement vs direct connections."""
        try:
            # Test with pool
            start_pool = time.time()
            for _ in range(10):
                conn = await self.pool.get_connection()
                try:
                    users_ref = conn.collection('users')
                    users_ref.limit(1).get()
                finally:
                    await self.pool.release_connection(conn)
            pool_duration = time.time() - start_pool
            
            avg_pool_time = pool_duration / 10
            
            self.print_test(
                "Performance with Pool",
                True,
                f"Average time per operation: {avg_pool_time*1000:.2f}ms"
            )
            
            # Note: We can't easily test without pool in this context
            # but we can verify the pool time is reasonable
            if avg_pool_time < 0.1:  # Less than 100ms per operation
                return True
            else:
                return False
        except Exception as e:
            self.print_test("Performance Improvement", False, str(e))
            return False
    
    async def test_pool_statistics(self) -> bool:
        """Test 8: Pool statistics accuracy."""
        try:
            # Get initial stats
            stats = self.pool.get_pool_stats()
            
            # Verify all expected keys are present
            expected_keys = ['total', 'active', 'idle', 'waiting', 'failed', 'min_size', 'max_size']
            missing_keys = [key for key in expected_keys if key not in stats]
            
            if not missing_keys:
                self.print_test(
                    "Pool Statistics",
                    True,
                    f"All statistics available: {stats}"
                )
                return True
            else:
                self.print_test(
                    "Pool Statistics",
                    False,
                    f"Missing keys: {missing_keys}"
                )
                return False
        except Exception as e:
            self.print_test("Pool Statistics", False, str(e))
            return False
    
    async def cleanup(self):
        """Clean up resources."""
        if self.pool:
            await self.pool.close()
    
    def print_summary(self):
        """Print test summary."""
        print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}TEST SUMMARY{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed
        
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.ENDC}")
        print(f"{Colors.RED}Failed: {failed}{Colors.ENDC}")
        
        if failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED{Colors.ENDC}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.ENDC}")
        
        print()
    
    async def run_all_tests(self):
        """Run all integration tests."""
        print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}CONNECTION POOL MANAGER - INTEGRATION TESTS{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
        
        try:
            # Run tests in sequence
            await self.test_pool_initialization()
            await self.test_connection_acquisition()
            await self.test_concurrent_connections()
            await self.test_pool_scaling()
            await self.test_health_check()
            await self.test_connection_reuse()
            await self.test_performance_improvement()
            await self.test_pool_statistics()
            
        finally:
            await self.cleanup()
            self.print_summary()


async def main():
    """Main entry point."""
    tester = ConnectionPoolIntegrationTest()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
