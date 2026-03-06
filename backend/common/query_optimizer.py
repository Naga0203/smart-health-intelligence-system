"""
Query Optimizer for Firebase Firestore

Optimizes database queries through:
- Query analysis and index recommendations
- Batch operations for related data
- Automatic query result caching
- Query result limit enforcement
- Integration with CacheManager

Requirements: 1.1, 1.3, 1.4, 1.5
"""

import logging
import hashlib
import json
from typing import Any, Dict, List, Optional, Callable
from functools import wraps
from datetime import datetime

from firebase_admin import firestore
from .cache_service import CacheService
from .errors import DatabaseError

logger = logging.getLogger('health_ai.query_optimizer')


class QueryOptimizer:
    """
    Optimizes Firestore queries with caching, batching, and analysis.
    
    Features:
    - Query analysis for missing indexes
    - Batch operations for multiple documents
    - Automatic query result caching
    - Query result limit enforcement (100 documents max)
    - Integration with CacheManager
    """
    
    # Maximum documents per query (Requirement 1.5)
    MAX_QUERY_RESULTS = 100
    
    # Default cache TTL for queries (5 minutes)
    DEFAULT_QUERY_TTL = 300
    
    def __init__(self, db_client: firestore.Client):
        """
        Initialize QueryOptimizer.
        
        Args:
            db_client: Firestore client instance
        """
        self.db = db_client
        self.cache = CacheService()
        logger.info("QueryOptimizer initialized")
    
    def analyze_query(self, collection: str, filters: List[Dict[str, Any]], 
                     order_by: Optional[List[tuple]] = None) -> Dict[str, Any]:
        """
        Analyze query and identify missing indexes.
        
        Requirement 1.1: Identify missing indexes and log recommendations
        
        Args:
            collection: Collection name
            filters: List of filter conditions [{'field': 'age', 'op': '>=', 'value': 18}]
            order_by: List of order_by tuples [('created_at', 'DESCENDING')]
            
        Returns:
            Analysis result with index recommendations
        """
        analysis = {
            'collection': collection,
            'filters': filters,
            'order_by': order_by or [],
            'index_recommendations': [],
            'warnings': []
        }
        
        # Check for composite index needs
        if len(filters) > 1 or (filters and order_by):
            # Multiple filters or filter + order_by requires composite index
            index_fields = []
            
            # Add filter fields
            for f in filters:
                field = f.get('field')
                if field and field not in index_fields:
                    index_fields.append(field)
            
            # Add order_by fields
            if order_by:
                for field, direction in order_by:
                    if field not in index_fields:
                        index_fields.append(field)
            
            if len(index_fields) > 1:
                recommendation = {
                    'type': 'composite_index',
                    'collection': collection,
                    'fields': index_fields,
                    'reason': 'Multiple filters or filter with order_by requires composite index'
                }
                analysis['index_recommendations'].append(recommendation)
                logger.info(f"Index recommendation for {collection}: {index_fields}")
        
        # Check for array-contains with other filters
        array_contains_filters = [f for f in filters if f.get('op') == 'array-contains']
        if array_contains_filters and len(filters) > 1:
            analysis['warnings'].append(
                'array-contains with other filters requires composite index'
            )
        
        # Check for inequality filters on multiple fields
        inequality_fields = set()
        for f in filters:
            if f.get('op') in ['<', '<=', '>', '>=', '!=']:
                inequality_fields.add(f.get('field'))
        
        if len(inequality_fields) > 1:
            analysis['warnings'].append(
                f'Inequality filters on multiple fields ({inequality_fields}) requires composite index'
            )
        
        return analysis
    
    def batch_get(self, collection: str, doc_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch multiple documents in a single batch operation.
        
        Requirement 1.3: Use batch operations to minimize round trips
        
        Args:
            collection: Collection name
            doc_ids: List of document IDs to fetch
            
        Returns:
            List of document data dictionaries
        """
        if not doc_ids:
            return []
        
        try:
            # Firestore batch get
            doc_refs = [self.db.collection(collection).document(doc_id) for doc_id in doc_ids]
            docs = self.db.get_all(doc_refs)
            
            results = []
            for doc in docs:
                if doc.exists:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    results.append(data)
            
            logger.info(f"Batch fetched {len(results)}/{len(doc_ids)} documents from {collection}")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch_get for {collection}: {e}")
            raise
    
    def _generate_query_key(self, collection: str, filters: List[Dict], 
                           order_by: Optional[List[tuple]] = None,
                           limit: Optional[int] = None) -> str:
        """
        Generate cache key for query.
        
        Args:
            collection: Collection name
            filters: Filter conditions
            order_by: Order by clauses
            limit: Result limit
            
        Returns:
            Cache key string
        """
        # Create deterministic representation
        query_repr = {
            'collection': collection,
            'filters': sorted(filters, key=lambda x: x.get('field', '')),
            'order_by': order_by or [],
            'limit': limit
        }
        
        # Hash the representation
        query_str = json.dumps(query_repr, sort_keys=True)
        query_hash = hashlib.sha256(query_str.encode()).hexdigest()[:16]
        
        return f"query:{collection}:{query_hash}"
    
    def cached_query(self, collection: str, filters: List[Dict[str, Any]],
                    order_by: Optional[List[tuple]] = None,
                    limit: Optional[int] = None,
                    ttl: int = DEFAULT_QUERY_TTL) -> List[Dict[str, Any]]:
        """
        Execute query with automatic caching.
        
        Requirements:
        - 1.4: Cache query results with appropriate TTL
        - 1.5: Limit query results to 100 documents max
        
        Args:
            collection: Collection name
            filters: List of filter conditions [{'field': 'age', 'op': '>=', 'value': 18}]
            order_by: List of order_by tuples [('created_at', 'DESCENDING')]
            limit: Maximum results (capped at MAX_QUERY_RESULTS)
            ttl: Cache TTL in seconds (60-3600)
            
        Returns:
            List of document data dictionaries
            
        Raises:
            DatabaseError: If query fails or times out
        """
        # Enforce TTL bounds (60-3600 seconds)
        ttl = max(60, min(3600, ttl))
        
        # Enforce result limit (Requirement 1.5)
        if limit is None or limit > self.MAX_QUERY_RESULTS:
            limit = self.MAX_QUERY_RESULTS
            logger.debug(f"Query limit capped at {self.MAX_QUERY_RESULTS}")
        
        # Generate cache key
        cache_key = self._generate_query_key(collection, filters, order_by, limit)
        
        # Try cache first (Requirement 1.4)
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache HIT for query: {collection}")
            return cached_result
        
        logger.debug(f"Cache MISS for query: {collection}")
        
        # Analyze query for index recommendations (Requirement 1.1)
        analysis = self.analyze_query(collection, filters, order_by)
        if analysis['index_recommendations']:
            for rec in analysis['index_recommendations']:
                logger.warning(f"Index recommendation: {rec}")
        
        # Execute query with error handling
        try:
            query_ref = self.db.collection(collection)
            
            # Apply filters
            for f in filters:
                field = f.get('field')
                op = f.get('op')
                value = f.get('value')
                
                if field and op and value is not None:
                    query_ref = query_ref.where(field, op, value)
            
            # Apply order_by
            if order_by:
                for field, direction in order_by:
                    direction_enum = (firestore.Query.DESCENDING 
                                    if direction.upper() == 'DESCENDING' 
                                    else firestore.Query.ASCENDING)
                    query_ref = query_ref.order_by(field, direction=direction_enum)
            
            # Apply limit
            query_ref = query_ref.limit(limit)
            
            # Execute with timeout handling
            docs = query_ref.stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            logger.info(f"Query executed: {collection}, returned {len(results)} documents")
            
            # Cache results
            self.cache.set(cache_key, results, ttl)
            
            return results
            
        except Exception as e:
            # Check for index missing error
            error_msg = str(e).lower()
            if "index" in error_msg or "composite" in error_msg:
                logger.error(f"Index missing error for {collection}: {e}")
                raise DatabaseError(
                    f"Query on {collection} requires a database index",
                    operation="cached_query",
                    details={
                        "collection": collection,
                        "error": str(e),
                        "filters": filters,
                        "order_by": order_by,
                        "suggestion": "Check Firestore console for index creation link"
                    }
                )
            else:
                logger.error(f"Error executing cached_query for {collection}: {e}")
                raise DatabaseError(
                    f"Query execution failed for {collection}",
                    operation="cached_query",
                    details={"collection": collection, "error": str(e)}
                )
    
    def invalidate_query_cache(self, collection: str, 
                              filters: Optional[List[Dict]] = None) -> bool:
        """
        Invalidate cached query results.
        
        Args:
            collection: Collection name
            filters: Specific filters to invalidate, or None for all queries on collection
            
        Returns:
            True if successful
        """
        if filters:
            # Invalidate specific query
            cache_key = self._generate_query_key(collection, filters)
            return self.cache.delete(cache_key)
        else:
            # Invalidate all queries for collection
            pattern = f"query:{collection}:*"
            return self.cache.delete_pattern(pattern)


def cached_query(collection: str, ttl: int = QueryOptimizer.DEFAULT_QUERY_TTL):
    """
    Decorator for automatic query caching.
    
    Usage:
        @cached_query('users', ttl=600)
        def get_active_users(db, min_age):
            # Query logic here
            return results
    
    Args:
        collection: Collection name for cache key generation
        ttl: Cache TTL in seconds
        
    Returns:
        Decorated function with caching
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key_parts = [
                'query_func',
                collection,
                func.__name__,
                str(args),
                str(sorted(kwargs.items()))
            ]
            cache_key = ':'.join(cache_key_parts)
            cache_key_hash = hashlib.sha256(cache_key.encode()).hexdigest()[:16]
            final_key = f"query_func:{collection}:{cache_key_hash}"
            
            # Try cache
            cache_service = CacheService()
            cached_result = cache_service.get(final_key)
            if cached_result is not None:
                logger.debug(f"Cache HIT for {func.__name__}")
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache_service.set(final_key, result, ttl)
            logger.debug(f"Cache SET for {func.__name__}")
            
            return result
        
        return wrapper
    return decorator
