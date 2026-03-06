"""
Connection Pool Manager for Firestore

Manages a pool of reusable Firestore connections to minimize connection overhead
and improve performance. Implements connection health checks, request queuing,
and idle connection cleanup.

Requirements:
- Maintain 10-50 connections to Firestore
- Queue requests for up to 5 seconds when pool exhausted
- Close idle connections after 300 seconds
- Monitor connection health and replace failed connections
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from firebase_admin import firestore
import firebase_admin
from .errors import DatabaseError

logger = logging.getLogger('health_ai.connection_pool')


@dataclass
class ConnectionState:
    """State information for a pooled connection."""
    connection: Any
    created_at: float
    last_used: float
    in_use: bool
    health_check_failed: bool = False
    use_count: int = 0


@dataclass
class CircuitBreakerState:
    """Circuit breaker state for Firestore connections."""
    failure_count: int = 0
    last_failure_time: float = 0
    state: str = "closed"  # closed, open, half_open
    cooldown_until: float = 0


class ConnectionPoolManager:
    """
    Manages a pool of Firestore connections with health checks and automatic cleanup.
    
    Features:
    - Configurable pool size (min: 10, max: 50)
    - Connection reuse to minimize overhead
    - Request queuing with 5-second timeout
    - Idle connection cleanup after 300 seconds
    - Automatic health checks and connection replacement
    """
    
    def __init__(self, min_size: int = 10, max_size: int = 50):
        """
        Initialize connection pool.
        
        Args:
            min_size: Minimum number of connections to maintain (default: 10)
            max_size: Maximum number of connections allowed (default: 50)
        """
        if min_size < 1:
            raise ValueError("min_size must be at least 1")
        if max_size < min_size:
            raise ValueError("max_size must be >= min_size")
        
        self.min_size = min_size
        self.max_size = max_size
        
        # Connection pool storage
        self._connections: Dict[str, ConnectionState] = {}
        self._available_connections: asyncio.Queue = asyncio.Queue()
        self._waiting_requests: asyncio.Queue = asyncio.Queue()
        
        # Pool statistics
        self._total_connections = 0
        self._active_connections = 0
        self._failed_connections = 0
        self._last_health_check = time.time()
        
        # Locks for thread safety
        self._pool_lock = asyncio.Lock()
        self._initialized = False
        
        # Health check configuration
        self.health_check_interval = 60  # seconds
        self.idle_timeout = 300  # seconds
        self.request_timeout = 5  # seconds
        
        # Circuit breaker configuration (Requirement 1.1)
        self.circuit_breaker = CircuitBreakerState()
        self.circuit_breaker_threshold = 5  # failures before opening
        self.circuit_breaker_cooldown = 60  # seconds
        
        # Retry configuration (Requirement 1.1)
        self.max_retries = 3
        self.retry_base_delay = 0.5  # seconds
        
        # Query timeout (Requirement 1.2)
        self.query_timeout = 10  # seconds
        
        logger.info(f"ConnectionPoolManager initialized (min: {min_size}, max: {max_size})")
    
    async def initialize(self):
        """Initialize the connection pool with minimum connections."""
        if self._initialized:
            return
        
        async with self._pool_lock:
            if self._initialized:
                return
            
            logger.info(f"Initializing connection pool with {self.min_size} connections")
            
            # Create minimum number of connections
            for i in range(self.min_size):
                try:
                    conn = await self._create_connection()
                    conn_id = f"conn_{i}_{time.time()}"
                    
                    state = ConnectionState(
                        connection=conn,
                        created_at=time.time(),
                        last_used=time.time(),
                        in_use=False
                    )
                    
                    self._connections[conn_id] = state
                    await self._available_connections.put(conn_id)
                    self._total_connections += 1
                    
                    logger.debug(f"Created connection: {conn_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to create initial connection {i}: {e}")
                    self._failed_connections += 1
            
            self._initialized = True
            logger.info(f"Connection pool initialized with {self._total_connections} connections")
            
            # Start background tasks
            asyncio.create_task(self._health_check_loop())
            asyncio.create_task(self._cleanup_idle_connections_loop())
    
    async def _create_connection(self) -> Any:
        """
        Create a new Firestore connection with exponential backoff retry.
        
        Requirement 1.1: Exponential backoff retry (3 attempts)
        
        Returns:
            Firestore client instance
            
        Raises:
            DatabaseError: If connection fails after all retries
        """
        for attempt in range(self.max_retries):
            try:
                # Check circuit breaker
                if not self._check_circuit_breaker():
                    raise DatabaseError(
                        "Circuit breaker is open - Firestore unavailable",
                        operation="create_connection"
                    )
                
                # Get Firestore client
                db = firestore.client()
                
                # Verify connection works with timeout
                await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, 
                        lambda: db.collection('_health_check').limit(1).get()
                    ),
                    timeout=self.query_timeout
                )
                
                # Reset circuit breaker on success
                self._record_success()
                
                return db
                
            except asyncio.TimeoutError:
                logger.error(f"Connection creation timeout (attempt {attempt + 1}/{self.max_retries})")
                self._record_failure()
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.retry_base_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    raise DatabaseError(
                        "Connection creation timed out after all retries",
                        operation="create_connection",
                        details={"attempts": self.max_retries, "timeout": self.query_timeout}
                    )
                    
            except Exception as e:
                logger.error(f"Failed to create Firestore connection (attempt {attempt + 1}/{self.max_retries}): {e}")
                self._record_failure()
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.retry_base_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    raise DatabaseError(
                        f"Failed to create connection after {self.max_retries} attempts",
                        operation="create_connection",
                        details={"error": str(e), "attempts": self.max_retries}
                    )
    
    def _check_circuit_breaker(self) -> bool:
        """
        Check if circuit breaker allows operations.
        
        Requirement 1.1: Circuit breaker (5 failures, 60s cooldown)
        
        Returns:
            True if operations are allowed, False if circuit is open
        """
        current_time = time.time()
        
        if self.circuit_breaker.state == "open":
            # Check if cooldown period has passed
            if current_time >= self.circuit_breaker.cooldown_until:
                logger.info("Circuit breaker entering half-open state")
                self.circuit_breaker.state = "half_open"
                return True
            else:
                remaining = self.circuit_breaker.cooldown_until - current_time
                logger.warning(f"Circuit breaker is open - {remaining:.1f}s remaining")
                return False
        
        return True
    
    def _record_failure(self):
        """
        Record a connection failure for circuit breaker.
        
        Requirement 1.1: Circuit breaker (5 failures, 60s cooldown)
        """
        self.circuit_breaker.failure_count += 1
        self.circuit_breaker.last_failure_time = time.time()
        
        if self.circuit_breaker.failure_count >= self.circuit_breaker_threshold:
            self.circuit_breaker.state = "open"
            self.circuit_breaker.cooldown_until = time.time() + self.circuit_breaker_cooldown
            logger.critical(
                f"Circuit breaker opened after {self.circuit_breaker.failure_count} failures. "
                f"Cooldown: {self.circuit_breaker_cooldown}s"
            )
    
    def _record_success(self):
        """Record a successful operation for circuit breaker."""
        if self.circuit_breaker.state == "half_open":
            logger.info("Circuit breaker closing after successful operation")
            self.circuit_breaker.state = "closed"
            self.circuit_breaker.failure_count = 0
        elif self.circuit_breaker.state == "closed":
            # Gradually reduce failure count on success
            self.circuit_breaker.failure_count = max(0, self.circuit_breaker.failure_count - 1)
    
    async def get_connection(self) -> Any:
        """
        Get a connection from the pool.
        
        Waits up to 5 seconds if all connections are in use.
        Creates new connections if pool is not at max capacity.
        
        Returns:
            Firestore connection
            
        Raises:
            TimeoutError: If no connection available within timeout
        """
        if not self._initialized:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            # Try to get an available connection with timeout
            conn_id = await asyncio.wait_for(
                self._available_connections.get(),
                timeout=self.request_timeout
            )
            
            async with self._pool_lock:
                if conn_id in self._connections:
                    state = self._connections[conn_id]
                    state.in_use = True
                    state.last_used = time.time()
                    state.use_count += 1
                    self._active_connections += 1
                    
                    logger.debug(f"Connection acquired: {conn_id} (active: {self._active_connections})")
                    return state.connection
                else:
                    # Connection was removed, try again
                    return await self.get_connection()
                    
        except asyncio.TimeoutError:
            # No connection available, try to create a new one if under max
            async with self._pool_lock:
                if self._total_connections < self.max_size:
                    try:
                        conn = await self._create_connection()
                        conn_id = f"conn_{self._total_connections}_{time.time()}"
                        
                        state = ConnectionState(
                            connection=conn,
                            created_at=time.time(),
                            last_used=time.time(),
                            in_use=True
                        )
                        
                        self._connections[conn_id] = state
                        self._total_connections += 1
                        self._active_connections += 1
                        
                        logger.info(f"Created new connection under load: {conn_id}")
                        return state.connection
                        
                    except Exception as e:
                        logger.error(f"Failed to create connection under load: {e}")
                        self._failed_connections += 1
            
            # Could not get or create connection
            elapsed = time.time() - start_time
            logger.warning(f"Connection request timed out after {elapsed:.2f}s")
            raise TimeoutError(f"No connection available within {self.request_timeout}s timeout")
    
    async def release_connection(self, conn: Any) -> None:
        """
        Return a connection to the pool.
        
        Args:
            conn: Firestore connection to release
        """
        async with self._pool_lock:
            # Find the connection in the pool
            conn_id = None
            for cid, state in self._connections.items():
                if state.connection is conn:
                    conn_id = cid
                    break
            
            if conn_id is None:
                logger.warning("Attempted to release unknown connection")
                return
            
            state = self._connections[conn_id]
            state.in_use = False
            state.last_used = time.time()
            self._active_connections -= 1
            
            # Return to available pool
            await self._available_connections.put(conn_id)
            
            logger.debug(f"Connection released: {conn_id} (active: {self._active_connections})")
    
    def get_pool_stats(self) -> Dict[str, int]:
        """
        Get current pool statistics.
        
        Returns:
            Dictionary with pool statistics:
            - total: Total connections in pool
            - active: Connections currently in use
            - idle: Connections available for use
            - waiting: Requests waiting for connections
            - failed: Failed connection attempts
        """
        idle_connections = self._total_connections - self._active_connections
        
        return {
            'total': self._total_connections,
            'active': self._active_connections,
            'idle': idle_connections,
            'waiting': self._waiting_requests.qsize(),
            'failed': self._failed_connections,
            'min_size': self.min_size,
            'max_size': self.max_size
        }
    
    async def health_check(self) -> bool:
        """
        Check health of all connections and replace failed ones.
        
        Returns:
            True if all connections are healthy, False otherwise
        """
        logger.debug("Running connection pool health check")
        
        all_healthy = True
        failed_connections = []
        
        async with self._pool_lock:
            for conn_id, state in list(self._connections.items()):
                if state.in_use:
                    # Skip connections currently in use
                    continue
                
                try:
                    # Perform health check
                    is_healthy = await self._check_connection_health(state.connection)
                    
                    if not is_healthy:
                        logger.warning(f"Connection {conn_id} failed health check")
                        state.health_check_failed = True
                        failed_connections.append(conn_id)
                        all_healthy = False
                    else:
                        state.health_check_failed = False
                        
                except Exception as e:
                    logger.error(f"Health check error for {conn_id}: {e}")
                    state.health_check_failed = True
                    failed_connections.append(conn_id)
                    all_healthy = False
            
            # Replace failed connections
            for conn_id in failed_connections:
                await self._replace_connection(conn_id)
            
            self._last_health_check = time.time()
        
        logger.info(f"Health check complete. Healthy: {all_healthy}, Replaced: {len(failed_connections)}")
        return all_healthy
    
    async def _check_connection_health(self, conn: Any) -> bool:
        """
        Check if a connection is healthy.
        
        Args:
            conn: Firestore connection to check
            
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Try a simple query to verify connection
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: conn.collection('_health_check').limit(1).get()
            )
            return True
        except Exception as e:
            logger.debug(f"Connection health check failed: {e}")
            return False
    
    async def _replace_connection(self, conn_id: str) -> None:
        """
        Replace a failed connection with a new one.
        
        Args:
            conn_id: ID of connection to replace
        """
        try:
            # Remove old connection
            if conn_id in self._connections:
                old_state = self._connections[conn_id]
                del self._connections[conn_id]
                self._total_connections -= 1
                self._failed_connections += 1
                
                logger.info(f"Removing failed connection: {conn_id}")
            
            # Create new connection
            new_conn = await self._create_connection()
            new_conn_id = f"conn_replacement_{time.time()}"
            
            new_state = ConnectionState(
                connection=new_conn,
                created_at=time.time(),
                last_used=time.time(),
                in_use=False
            )
            
            self._connections[new_conn_id] = new_state
            await self._available_connections.put(new_conn_id)
            self._total_connections += 1
            
            logger.info(f"Replaced connection {conn_id} with {new_conn_id}")
            
        except Exception as e:
            logger.error(f"Failed to replace connection {conn_id}: {e}")
            self._failed_connections += 1
    
    async def _cleanup_idle_connections(self) -> None:
        """Clean up connections that have been idle for too long."""
        current_time = time.time()
        idle_threshold = current_time - self.idle_timeout
        
        connections_to_remove = []
        
        async with self._pool_lock:
            for conn_id, state in list(self._connections.items()):
                # Don't remove if in use or if we're at minimum size
                if state.in_use or self._total_connections <= self.min_size:
                    continue
                
                # Check if idle for too long
                if state.last_used < idle_threshold:
                    connections_to_remove.append(conn_id)
            
            # Remove idle connections
            for conn_id in connections_to_remove:
                del self._connections[conn_id]
                self._total_connections -= 1
                logger.info(f"Removed idle connection: {conn_id}")
        
        if connections_to_remove:
            logger.info(f"Cleaned up {len(connections_to_remove)} idle connections")
    
    async def _health_check_loop(self) -> None:
        """Background task to periodically check connection health."""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self.health_check()
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
    
    async def _cleanup_idle_connections_loop(self) -> None:
        """Background task to periodically clean up idle connections."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self._cleanup_idle_connections()
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def close(self) -> None:
        """Close all connections and shut down the pool."""
        logger.info("Closing connection pool")
        
        async with self._pool_lock:
            for conn_id in list(self._connections.keys()):
                del self._connections[conn_id]
            
            self._total_connections = 0
            self._active_connections = 0
            self._initialized = False
        
        logger.info("Connection pool closed")
    
    async def execute_query_with_timeout(self, query_func, timeout: Optional[float] = None):
        """
        Execute a Firestore query with timeout handling.
        
        Requirement 1.2: Handle query timeouts (10 seconds)
        
        Args:
            query_func: Callable that executes the query
            timeout: Timeout in seconds (default: self.query_timeout)
            
        Returns:
            Query result
            
        Raises:
            DatabaseError: If query times out or fails
        """
        timeout = timeout or self.query_timeout
        
        try:
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, query_func),
                timeout=timeout
            )
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"Query timeout after {timeout}s")
            raise DatabaseError(
                f"Query timed out after {timeout} seconds",
                operation="query_execution",
                details={"timeout": timeout}
            )
        except Exception as e:
            # Check for index missing error (Requirement 1.1)
            error_msg = str(e).lower()
            if "index" in error_msg or "composite" in error_msg:
                logger.error(f"Index missing error: {e}")
                raise DatabaseError(
                    "Query requires a database index. Please create the required index.",
                    operation="query_execution",
                    details={
                        "error": str(e),
                        "suggestion": "Check Firestore console for index creation link"
                    }
                )
            else:
                logger.error(f"Query execution error: {e}")
                raise DatabaseError(
                    "Query execution failed",
                    operation="query_execution",
                    details={"error": str(e)}
                )


# Singleton instance
_connection_pool: Optional[ConnectionPoolManager] = None


def get_connection_pool(min_size: int = 10, max_size: int = 50) -> ConnectionPoolManager:
    """
    Get the singleton connection pool instance.
    
    Args:
        min_size: Minimum pool size (only used on first call)
        max_size: Maximum pool size (only used on first call)
        
    Returns:
        ConnectionPoolManager instance
    """
    global _connection_pool
    
    if _connection_pool is None:
        _connection_pool = ConnectionPoolManager(min_size=min_size, max_size=max_size)
    
    return _connection_pool
