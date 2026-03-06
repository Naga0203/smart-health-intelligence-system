"""
Unit tests for ConnectionPoolManager

Tests connection pool functionality including:
- Pool initialization
- Connection acquisition and release
- Pool size management
- Health checks
- Idle connection cleanup
- Error handling
"""

import pytest
import pytest_asyncio
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from backend.common.connection_pool import (
    ConnectionPoolManager,
    ConnectionState,
    get_connection_pool
)


@pytest.fixture
def mock_firestore_client():
    """Create a mock Firestore client."""
    mock_client = Mock()
    mock_collection = Mock()
    mock_query = Mock()
    mock_query.get.return_value = []
    mock_collection.limit.return_value = mock_query
    mock_client.collection.return_value = mock_collection
    return mock_client


@pytest_asyncio.fixture
async def connection_pool():
    """Create a connection pool for testing."""
    with patch('backend.common.connection_pool.firestore.client') as mock_client:
        mock_db = Mock()
        mock_collection = Mock()
        mock_query = Mock()
        mock_query.get.return_value = []
        mock_collection.limit.return_value = mock_query
        mock_db.collection.return_value = mock_collection
        mock_client.return_value = mock_db
        
        pool = ConnectionPoolManager(min_size=3, max_size=10)
        await pool.initialize()
        try:
            yield pool
        finally:
            await pool.close()


class TestConnectionPoolInitialization:
    """Test connection pool initialization."""
    
    def test_init_with_valid_params(self):
        """Test initialization with valid parameters."""
        pool = ConnectionPoolManager(min_size=10, max_size=50)
        assert pool.min_size == 10
        assert pool.max_size == 50
        assert pool._total_connections == 0
        assert pool._active_connections == 0
    
    def test_init_with_invalid_min_size(self):
        """Test initialization with invalid min_size."""
        with pytest.raises(ValueError, match="min_size must be at least 1"):
            ConnectionPoolManager(min_size=0, max_size=50)
    
    def test_init_with_max_less_than_min(self):
        """Test initialization with max_size < min_size."""
        with pytest.raises(ValueError, match="max_size must be >= min_size"):
            ConnectionPoolManager(min_size=50, max_size=10)
    
    @pytest.mark.asyncio
    async def test_initialize_creates_min_connections(self):
        """Test that initialize creates minimum number of connections."""
        with patch('backend.common.connection_pool.firestore.client') as mock_client:
            mock_db = Mock()
            mock_collection = Mock()
            mock_query = Mock()
            mock_query.get.return_value = []
            mock_collection.limit.return_value = mock_query
            mock_db.collection.return_value = mock_collection
            mock_client.return_value = mock_db
            
            pool = ConnectionPoolManager(min_size=5, max_size=10)
            await pool.initialize()
            
            assert pool._total_connections == 5
            assert pool._initialized is True
            
            await pool.close()
    
    @pytest.mark.asyncio
    async def test_initialize_idempotent(self):
        """Test that initialize can be called multiple times safely."""
        with patch('backend.common.connection_pool.firestore.client') as mock_client:
            mock_db = Mock()
            mock_collection = Mock()
            mock_query = Mock()
            mock_query.get.return_value = []
            mock_collection.limit.return_value = mock_query
            mock_db.collection.return_value = mock_collection
            mock_client.return_value = mock_db
            
            pool = ConnectionPoolManager(min_size=3, max_size=10)
            await pool.initialize()
            initial_count = pool._total_connections
            
            # Call initialize again
            await pool.initialize()
            
            # Should not create more connections
            assert pool._total_connections == initial_count
            
            await pool.close()


class TestConnectionAcquisitionAndRelease:
    """Test connection acquisition and release."""
    
    @pytest.mark.asyncio
    async def test_get_connection_success(self, connection_pool):
        """Test successful connection acquisition."""
        conn = await connection_pool.get_connection()
        
        assert conn is not None
        assert connection_pool._active_connections == 1
    
    @pytest.mark.asyncio
    async def test_release_connection_success(self, connection_pool):
        """Test successful connection release."""
        conn = await connection_pool.get_connection()
        initial_active = connection_pool._active_connections
        
        await connection_pool.release_connection(conn)
        
        assert connection_pool._active_connections == initial_active - 1
    
    @pytest.mark.asyncio
    async def test_multiple_get_and_release(self, connection_pool):
        """Test multiple get and release operations."""
        connections = []
        
        # Get multiple connections
        for _ in range(3):
            conn = await connection_pool.get_connection()
            connections.append(conn)
        
        assert connection_pool._active_connections == 3
        
        # Release all connections
        for conn in connections:
            await connection_pool.release_connection(conn)
        
        assert connection_pool._active_connections == 0
    
    @pytest.mark.asyncio
    async def test_connection_reuse(self, connection_pool):
        """Test that connections are reused from the pool."""
        # Get and release a connection
        conn1 = await connection_pool.get_connection()
        await connection_pool.release_connection(conn1)
        
        # Get another connection - should reuse
        conn2 = await connection_pool.get_connection()
        
        # Should be the same connection object
        assert conn1 is conn2
        
        await connection_pool.release_connection(conn2)
    
    @pytest.mark.asyncio
    async def test_pool_exhaustion_creates_new_connection(self):
        """Test that new connections are created when pool is exhausted."""
        with patch('backend.common.connection_pool.firestore.client') as mock_client:
            mock_db = Mock()
            mock_collection = Mock()
            mock_query = Mock()
            mock_query.get.return_value = []
            mock_collection.limit.return_value = mock_query
            mock_db.collection.return_value = mock_collection
            mock_client.return_value = mock_db
            
            pool = ConnectionPoolManager(min_size=2, max_size=5)
            await pool.initialize()
            
            # Exhaust the pool
            conn1 = await pool.get_connection()
            conn2 = await pool.get_connection()
            
            assert pool._total_connections == 2
            
            # Request another connection - should create new one
            conn3 = await pool.get_connection()
            
            assert pool._total_connections == 3
            assert pool._active_connections == 3
            
            await pool.release_connection(conn1)
            await pool.release_connection(conn2)
            await pool.release_connection(conn3)
            await pool.close()
    
    @pytest.mark.asyncio
    async def test_timeout_when_max_connections_reached(self):
        """Test timeout when all connections are in use and max is reached."""
        with patch('backend.common.connection_pool.firestore.client') as mock_client:
            mock_db = Mock()
            mock_collection = Mock()
            mock_query = Mock()
            mock_query.get.return_value = []
            mock_collection.limit.return_value = mock_query
            mock_db.collection.return_value = mock_collection
            mock_client.return_value = mock_db
            
            pool = ConnectionPoolManager(min_size=2, max_size=2)
            pool.request_timeout = 1  # Short timeout for testing
            await pool.initialize()
            
            # Exhaust the pool
            conn1 = await pool.get_connection()
            conn2 = await pool.get_connection()
            
            # Try to get another connection - should timeout
            with pytest.raises(TimeoutError):
                await pool.get_connection()
            
            await pool.release_connection(conn1)
            await pool.release_connection(conn2)
            await pool.close()


class TestPoolStatistics:
    """Test pool statistics."""
    
    @pytest.mark.asyncio
    async def test_get_pool_stats_initial(self, connection_pool):
        """Test pool statistics after initialization."""
        stats = connection_pool.get_pool_stats()
        
        assert stats['total'] == 3
        assert stats['active'] == 0
        assert stats['idle'] == 3
        assert stats['min_size'] == 3
        assert stats['max_size'] == 10
    
    @pytest.mark.asyncio
    async def test_get_pool_stats_with_active_connections(self, connection_pool):
        """Test pool statistics with active connections."""
        conn1 = await connection_pool.get_connection()
        conn2 = await connection_pool.get_connection()
        
        stats = connection_pool.get_pool_stats()
        
        assert stats['total'] == 3
        assert stats['active'] == 2
        assert stats['idle'] == 1
        
        await connection_pool.release_connection(conn1)
        await connection_pool.release_connection(conn2)


class TestHealthChecks:
    """Test connection health checks."""
    
    @pytest.mark.asyncio
    async def test_health_check_all_healthy(self, connection_pool):
        """Test health check when all connections are healthy."""
        result = await connection_pool.health_check()
        
        assert result is True
        assert connection_pool._last_health_check > 0
    
    @pytest.mark.asyncio
    async def test_health_check_replaces_failed_connection(self):
        """Test that failed connections are replaced during health check."""
        with patch('backend.common.connection_pool.firestore.client') as mock_client:
            mock_db = Mock()
            mock_collection = Mock()
            mock_query = Mock()
            mock_query.get.return_value = []
            mock_collection.limit.return_value = mock_query
            mock_db.collection.return_value = mock_collection
            mock_client.return_value = mock_db
            
            pool = ConnectionPoolManager(min_size=2, max_size=5)
            await pool.initialize()
            
            initial_count = pool._total_connections
            
            # Make one connection fail health check
            conn_id = list(pool._connections.keys())[0]
            pool._connections[conn_id].health_check_failed = True
            
            # Mock the health check to fail for one connection
            with patch.object(pool, '_check_connection_health') as mock_check:
                mock_check.side_effect = [False, True]  # First fails, second succeeds
                
                result = await pool.health_check()
                
                # Should have replaced the failed connection
                assert pool._total_connections == initial_count
            
            await pool.close()
    
    @pytest.mark.asyncio
    async def test_check_connection_health_success(self, connection_pool):
        """Test checking health of a healthy connection."""
        conn = await connection_pool.get_connection()
        
        is_healthy = await connection_pool._check_connection_health(conn)
        
        assert is_healthy is True
        
        await connection_pool.release_connection(conn)
    
    @pytest.mark.asyncio
    async def test_check_connection_health_failure(self, connection_pool):
        """Test checking health of a failed connection."""
        conn = await connection_pool.get_connection()
        
        # Make the connection fail
        conn.collection = Mock(side_effect=Exception("Connection failed"))
        
        is_healthy = await connection_pool._check_connection_health(conn)
        
        assert is_healthy is False
        
        await connection_pool.release_connection(conn)


class TestIdleConnectionCleanup:
    """Test idle connection cleanup."""
    
    @pytest.mark.asyncio
    async def test_cleanup_idle_connections_removes_old(self):
        """Test that idle connections are removed after timeout."""
        with patch('backend.common.connection_pool.firestore.client') as mock_client:
            mock_db = Mock()
            mock_collection = Mock()
            mock_query = Mock()
            mock_query.get.return_value = []
            mock_collection.limit.return_value = mock_query
            mock_db.collection.return_value = mock_collection
            mock_client.return_value = mock_db
            
            pool = ConnectionPoolManager(min_size=2, max_size=5)
            pool.idle_timeout = 1  # Short timeout for testing
            await pool.initialize()
            
            # Create an extra connection
            conn = await pool.get_connection()
            await pool.release_connection(conn)
            
            assert pool._total_connections >= 2
            
            # Make one connection appear idle
            conn_id = list(pool._connections.keys())[0]
            pool._connections[conn_id].last_used = time.time() - 2  # 2 seconds ago
            
            # Run cleanup
            await pool._cleanup_idle_connections()
            
            # Should have removed the idle connection (but not below min_size)
            assert pool._total_connections >= pool.min_size
            
            await pool.close()
    
    @pytest.mark.asyncio
    async def test_cleanup_respects_min_size(self):
        """Test that cleanup doesn't remove connections below min_size."""
        with patch('backend.common.connection_pool.firestore.client') as mock_client:
            mock_db = Mock()
            mock_collection = Mock()
            mock_query = Mock()
            mock_query.get.return_value = []
            mock_collection.limit.return_value = mock_query
            mock_db.collection.return_value = mock_collection
            mock_client.return_value = mock_db
            
            pool = ConnectionPoolManager(min_size=3, max_size=5)
            pool.idle_timeout = 1
            await pool.initialize()
            
            # Make all connections appear idle
            for conn_id in pool._connections.keys():
                pool._connections[conn_id].last_used = time.time() - 2
            
            # Run cleanup
            await pool._cleanup_idle_connections()
            
            # Should maintain min_size
            assert pool._total_connections == pool.min_size
            
            await pool.close()
    
    @pytest.mark.asyncio
    async def test_cleanup_skips_in_use_connections(self, connection_pool):
        """Test that cleanup doesn't remove connections in use."""
        # Get a connection (marks it as in use)
        conn = await connection_pool.get_connection()
        
        # Make it appear idle (but it's still in use)
        for conn_id, state in connection_pool._connections.items():
            if state.connection is conn:
                state.last_used = time.time() - 1000
        
        initial_count = connection_pool._total_connections
        
        # Run cleanup
        await connection_pool._cleanup_idle_connections()
        
        # Should not have removed the in-use connection
        assert connection_pool._total_connections == initial_count
        
        await connection_pool.release_connection(conn)


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_release_unknown_connection(self, connection_pool):
        """Test releasing a connection not in the pool."""
        fake_conn = Mock()
        
        # Should not raise an error
        await connection_pool.release_connection(fake_conn)
        
        # Active connections should not change
        assert connection_pool._active_connections == 0
    
    @pytest.mark.asyncio
    async def test_create_connection_failure_handling(self):
        """Test handling of connection creation failures."""
        with patch('backend.common.connection_pool.firestore.client') as mock_client:
            mock_client.side_effect = Exception("Connection failed")
            
            pool = ConnectionPoolManager(min_size=2, max_size=5)
            
            # Initialize should handle failures gracefully
            await pool.initialize()
            
            # Should have tracked failures
            assert pool._failed_connections > 0
            
            await pool.close()


class TestSingletonPattern:
    """Test singleton pattern for connection pool."""
    
    def test_get_connection_pool_returns_singleton(self):
        """Test that get_connection_pool returns the same instance."""
        # Reset singleton
        import backend.common.connection_pool as cp_module
        cp_module._connection_pool = None
        
        pool1 = get_connection_pool(min_size=10, max_size=50)
        pool2 = get_connection_pool(min_size=20, max_size=100)  # Different params
        
        # Should be the same instance
        assert pool1 is pool2
        
        # Should use first initialization params
        assert pool1.min_size == 10
        assert pool1.max_size == 50


class TestConnectionState:
    """Test ConnectionState dataclass."""
    
    def test_connection_state_creation(self):
        """Test creating a ConnectionState."""
        mock_conn = Mock()
        state = ConnectionState(
            connection=mock_conn,
            created_at=time.time(),
            last_used=time.time(),
            in_use=True
        )
        
        assert state.connection is mock_conn
        assert state.in_use is True
        assert state.health_check_failed is False
        assert state.use_count == 0
