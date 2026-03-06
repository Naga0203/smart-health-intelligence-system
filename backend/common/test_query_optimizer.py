"""
Tests for QueryOptimizer

Tests cover:
- Query analysis for missing indexes
- Batch operations for related data
- Cached query execution
- Query result limit enforcement
- Cache invalidation
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from firebase_admin import firestore

from .query_optimizer import QueryOptimizer, cached_query


@pytest.fixture
def mock_db():
    """Mock Firestore client."""
    db = Mock()
    return db


@pytest.fixture
def mock_cache():
    """Mock CacheService."""
    with patch('backend.common.query_optimizer.CacheService') as MockCache:
        cache_instance = MockCache.return_value
        cache_instance.get.return_value = None  # Default: cache miss
        cache_instance.set.return_value = True
        cache_instance.delete.return_value = True
        cache_instance.delete_pattern.return_value = True
        yield cache_instance


@pytest.fixture
def optimizer(mock_db, mock_cache):
    """QueryOptimizer instance with mocked dependencies."""
    with patch('backend.common.query_optimizer.CacheService'):
        opt = QueryOptimizer(mock_db)
        opt.cache = mock_cache
        return opt


class TestQueryAnalysis:
    """Test query analysis and index recommendations."""
    
    def test_single_filter_no_index_needed(self, optimizer):
        """Single filter doesn't require composite index."""
        filters = [{'field': 'age', 'op': '>=', 'value': 18}]
        
        analysis = optimizer.analyze_query('users', filters)
        
        assert analysis['collection'] == 'users'
        assert len(analysis['index_recommendations']) == 0
    
    def test_multiple_filters_requires_composite_index(self, optimizer):
        """Multiple filters require composite index."""
        filters = [
            {'field': 'age', 'op': '>=', 'value': 18},
            {'field': 'status', 'op': '==', 'value': 'active'}
        ]
        
        analysis = optimizer.analyze_query('users', filters)
        
        assert len(analysis['index_recommendations']) == 1
        rec = analysis['index_recommendations'][0]
        assert rec['type'] == 'composite_index'
        assert rec['collection'] == 'users'
        assert 'age' in rec['fields']
        assert 'status' in rec['fields']
    
    def test_filter_with_order_by_requires_composite_index(self, optimizer):
        """Filter with order_by requires composite index."""
        filters = [{'field': 'status', 'op': '==', 'value': 'active'}]
        order_by = [('created_at', 'DESCENDING')]
        
        analysis = optimizer.analyze_query('users', filters, order_by)
        
        assert len(analysis['index_recommendations']) == 1
        rec = analysis['index_recommendations'][0]
        assert 'status' in rec['fields']
        assert 'created_at' in rec['fields']
    
    def test_array_contains_with_other_filters_warning(self, optimizer):
        """array-contains with other filters generates warning."""
        filters = [
            {'field': 'tags', 'op': 'array-contains', 'value': 'premium'},
            {'field': 'status', 'op': '==', 'value': 'active'}
        ]
        
        analysis = optimizer.analyze_query('users', filters)
        
        assert len(analysis['warnings']) > 0
        assert 'array-contains' in analysis['warnings'][0]
    
    def test_multiple_inequality_fields_warning(self, optimizer):
        """Inequality filters on multiple fields generates warning."""
        filters = [
            {'field': 'age', 'op': '>=', 'value': 18},
            {'field': 'score', 'op': '>', 'value': 50}
        ]
        
        analysis = optimizer.analyze_query('users', filters)
        
        assert len(analysis['warnings']) > 0
        assert 'multiple fields' in analysis['warnings'][0].lower()


class TestBatchOperations:
    """Test batch_get operations."""
    
    def test_batch_get_multiple_documents(self, optimizer, mock_db):
        """Batch get fetches multiple documents efficiently."""
        # Setup mock documents
        doc1 = Mock()
        doc1.exists = True
        doc1.id = 'doc1'
        doc1.to_dict.return_value = {'name': 'User 1'}
        
        doc2 = Mock()
        doc2.exists = True
        doc2.id = 'doc2'
        doc2.to_dict.return_value = {'name': 'User 2'}
        
        mock_db.get_all.return_value = [doc1, doc2]
        mock_db.collection.return_value.document.return_value = Mock()
        
        # Execute batch get
        doc_ids = ['doc1', 'doc2']
        results = optimizer.batch_get('users', doc_ids)
        
        # Verify results
        assert len(results) == 2
        assert results[0]['id'] == 'doc1'
        assert results[0]['name'] == 'User 1'
        assert results[1]['id'] == 'doc2'
        assert results[1]['name'] == 'User 2'
        
        # Verify single batch call
        mock_db.get_all.assert_called_once()
    
    def test_batch_get_empty_list(self, optimizer):
        """Batch get with empty list returns empty results."""
        results = optimizer.batch_get('users', [])
        assert results == []
    
    def test_batch_get_nonexistent_documents(self, optimizer, mock_db):
        """Batch get handles nonexistent documents."""
        doc1 = Mock()
        doc1.exists = False
        
        doc2 = Mock()
        doc2.exists = True
        doc2.id = 'doc2'
        doc2.to_dict.return_value = {'name': 'User 2'}
        
        mock_db.get_all.return_value = [doc1, doc2]
        mock_db.collection.return_value.document.return_value = Mock()
        
        results = optimizer.batch_get('users', ['doc1', 'doc2'])
        
        # Only existing document returned
        assert len(results) == 1
        assert results[0]['id'] == 'doc2'
    
    def test_batch_get_error_handling(self, optimizer, mock_db):
        """Batch get handles errors appropriately."""
        mock_db.get_all.side_effect = Exception("Firestore error")
        mock_db.collection.return_value.document.return_value = Mock()
        
        with pytest.raises(Exception) as exc_info:
            optimizer.batch_get('users', ['doc1'])
        
        assert "Firestore error" in str(exc_info.value)


class TestCachedQuery:
    """Test cached query execution."""
    
    def test_cached_query_cache_hit(self, optimizer, mock_cache, mock_db):
        """Cached query returns cached results on cache hit."""
        cached_data = [{'id': 'doc1', 'name': 'Cached User'}]
        mock_cache.get.return_value = cached_data
        
        filters = [{'field': 'status', 'op': '==', 'value': 'active'}]
        results = optimizer.cached_query('users', filters)
        
        assert results == cached_data
        # Database should not be queried
        mock_db.collection.assert_not_called()
    
    def test_cached_query_cache_miss_executes_query(self, optimizer, mock_cache, mock_db):
        """Cached query executes query on cache miss."""
        mock_cache.get.return_value = None  # Cache miss
        
        # Setup mock query chain
        mock_doc = Mock()
        mock_doc.to_dict.return_value = {'name': 'User 1'}
        mock_doc.id = 'doc1'
        
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.stream.return_value = [mock_doc]
        
        mock_db.collection.return_value = mock_query
        
        # Execute query
        filters = [{'field': 'status', 'op': '==', 'value': 'active'}]
        results = optimizer.cached_query('users', filters, limit=10)
        
        # Verify query execution
        assert len(results) == 1
        assert results[0]['id'] == 'doc1'
        assert results[0]['name'] == 'User 1'
        
        # Verify caching
        mock_cache.set.assert_called_once()
        call_args = mock_cache.set.call_args
        assert call_args[0][1] == results  # Cached data matches results
    
    def test_cached_query_enforces_max_limit(self, optimizer, mock_cache, mock_db):
        """Cached query enforces MAX_QUERY_RESULTS limit."""
        mock_cache.get.return_value = None
        
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.stream.return_value = []
        
        mock_db.collection.return_value = mock_query
        
        # Request more than max
        filters = [{'field': 'status', 'op': '==', 'value': 'active'}]
        optimizer.cached_query('users', filters, limit=500)
        
        # Verify limit was capped
        mock_query.limit.assert_called_with(QueryOptimizer.MAX_QUERY_RESULTS)
    
    def test_cached_query_with_order_by(self, optimizer, mock_cache, mock_db):
        """Cached query handles order_by clauses."""
        mock_cache.get.return_value = None
        
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.stream.return_value = []
        
        mock_db.collection.return_value = mock_query
        
        filters = [{'field': 'status', 'op': '==', 'value': 'active'}]
        order_by = [('created_at', 'DESCENDING')]
        
        optimizer.cached_query('users', filters, order_by=order_by)
        
        # Verify order_by was applied
        mock_query.order_by.assert_called_once()
    
    def test_cached_query_ttl_bounds(self, optimizer, mock_cache, mock_db):
        """Cached query enforces TTL bounds (60-3600 seconds)."""
        mock_cache.get.return_value = None
        
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.stream.return_value = []
        
        mock_db.collection.return_value = mock_query
        
        filters = [{'field': 'status', 'op': '==', 'value': 'active'}]
        
        # Test TTL too low
        optimizer.cached_query('users', filters, ttl=30)
        call_args = mock_cache.set.call_args
        assert call_args[0][2] >= 60  # TTL should be at least 60
        
        # Test TTL too high
        mock_cache.reset_mock()
        optimizer.cached_query('users', filters, ttl=5000)
        call_args = mock_cache.set.call_args
        assert call_args[0][2] <= 3600  # TTL should be at most 3600
    
    def test_cached_query_multiple_filters(self, optimizer, mock_cache, mock_db):
        """Cached query handles multiple filters."""
        mock_cache.get.return_value = None
        
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.stream.return_value = []
        
        mock_db.collection.return_value = mock_query
        
        filters = [
            {'field': 'status', 'op': '==', 'value': 'active'},
            {'field': 'age', 'op': '>=', 'value': 18}
        ]
        
        optimizer.cached_query('users', filters)
        
        # Verify both filters applied
        assert mock_query.where.call_count == 2


class TestCacheInvalidation:
    """Test cache invalidation."""
    
    def test_invalidate_specific_query(self, optimizer, mock_cache):
        """Invalidate specific query cache."""
        filters = [{'field': 'status', 'op': '==', 'value': 'active'}]
        
        result = optimizer.invalidate_query_cache('users', filters)
        
        assert result is True
        mock_cache.delete.assert_called_once()
    
    def test_invalidate_all_collection_queries(self, optimizer, mock_cache):
        """Invalidate all queries for a collection."""
        result = optimizer.invalidate_query_cache('users')
        
        assert result is True
        mock_cache.delete_pattern.assert_called_once()
        call_args = mock_cache.delete_pattern.call_args
        assert 'users' in call_args[0][0]


class TestCachedQueryDecorator:
    """Test @cached_query decorator."""
    
    def test_decorator_caches_function_results(self, mock_db):
        """Decorator caches function results."""
        with patch('backend.common.query_optimizer.CacheService') as MockCache:
            cache_instance = MockCache.return_value
            cache_instance.get.return_value = None  # First call: cache miss
            cache_instance.set.return_value = True
            
            @cached_query('users', ttl=600)
            def get_active_users(db, min_age):
                return [{'id': '1', 'age': min_age}]
            
            # First call
            result1 = get_active_users(mock_db, 18)
            assert result1 == [{'id': '1', 'age': 18}]
            cache_instance.set.assert_called_once()
            
            # Second call with cache hit
            cache_instance.get.return_value = [{'id': '1', 'age': 18}]
            result2 = get_active_users(mock_db, 18)
            assert result2 == [{'id': '1', 'age': 18}]
    
    def test_decorator_different_args_different_cache_keys(self, mock_db):
        """Decorator uses different cache keys for different arguments."""
        with patch('backend.common.query_optimizer.CacheService') as MockCache:
            cache_instance = MockCache.return_value
            cache_instance.get.return_value = None
            cache_instance.set.return_value = True
            
            @cached_query('users', ttl=600)
            def get_users_by_age(db, age):
                return [{'age': age}]
            
            # Call with different arguments
            get_users_by_age(mock_db, 18)
            get_users_by_age(mock_db, 25)
            
            # Should have different cache keys
            assert cache_instance.set.call_count == 2


class TestEdgeCases:
    """Test edge cases and error scenarios."""
    
    def test_empty_filters_list(self, optimizer, mock_cache, mock_db):
        """Handle empty filters list."""
        mock_cache.get.return_value = None
        
        mock_query = Mock()
        mock_query.limit.return_value = mock_query
        mock_query.stream.return_value = []
        
        mock_db.collection.return_value = mock_query
        
        results = optimizer.cached_query('users', [])
        
        assert results == []
        # No where clauses should be applied
        mock_query.where.assert_not_called()
    
    def test_query_execution_error(self, optimizer, mock_cache, mock_db):
        """Handle query execution errors."""
        mock_cache.get.return_value = None
        
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.stream.side_effect = Exception("Query failed")
        
        mock_db.collection.return_value = mock_query
        
        filters = [{'field': 'status', 'op': '==', 'value': 'active'}]
        
        with pytest.raises(Exception) as exc_info:
            optimizer.cached_query('users', filters)
        
        assert "Query failed" in str(exc_info.value)
    
    def test_none_limit_uses_default(self, optimizer, mock_cache, mock_db):
        """None limit uses MAX_QUERY_RESULTS."""
        mock_cache.get.return_value = None
        
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.stream.return_value = []
        
        mock_db.collection.return_value = mock_query
        
        filters = [{'field': 'status', 'op': '==', 'value': 'active'}]
        optimizer.cached_query('users', filters, limit=None)
        
        mock_query.limit.assert_called_with(QueryOptimizer.MAX_QUERY_RESULTS)
