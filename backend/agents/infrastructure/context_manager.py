"""
Context Manager for agent memory and session management.

Manages conversation context, agent memory, and information sharing
between agents within a session.

Requirements: 6.3, 6.4, 16.1, 16.2, 16.6, 16.7
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger('health_ai.agents.infrastructure')


class ContextManager:
    """
    Manage conversation context and agent memory.
    
    Requirements:
    - 16.1: Maintain context within session
    - 16.2: Store agent decisions in context
    - 16.6: Limit context size
    - 16.7: Summarize context when too large
    """
    
    def __init__(self, max_context_size: int = 10000):
        """
        Initialize context manager.
        
        Args:
            max_context_size: Maximum context size in characters
        """
        self.max_context_size = max_context_size
        self.context: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
        self.session_id: Optional[str] = None
        self.created_at: datetime = datetime.utcnow()
        
        logger.info(f"ContextManager initialized with max_size={max_context_size}")
    
    def add_to_context(self, key: str, value: Any):
        """
        Add information to current context.
        
        Requirements: 16.1, 16.2 - Add and maintain context
        
        Args:
            key: Context key
            value: Context value
        """
        self.context[key] = value
        
        # Add to history
        self.history.append({
            'action': 'add',
            'key': key,
            'timestamp': datetime.utcnow().isoformat(),
            'value_type': type(value).__name__
        })
        
        logger.debug(f"Added to context: {key} ({type(value).__name__})")
        
        # Check if context size exceeds limit
        if self._get_context_size() > self.max_context_size:
            logger.warning(f"Context size exceeded {self.max_context_size}, summarizing...")
            self._summarize_old_context()
    
    def get_context(self, key: Optional[str] = None) -> Any:
        """
        Get current context or specific key.
        
        Requirements: 16.1 - Access context within session
        
        Args:
            key: Optional specific key to retrieve
            
        Returns:
            Full context dict or specific value
        """
        if key is None:
            return self.context.copy()
        return self.context.get(key)
    
    def has_key(self, key: str) -> bool:
        """Check if key exists in context."""
        return key in self.context
    
    def remove_from_context(self, key: str):
        """
        Remove key from context.
        
        Args:
            key: Context key to remove
        """
        if key in self.context:
            del self.context[key]
            self.history.append({
                'action': 'remove',
                'key': key,
                'timestamp': datetime.utcnow().isoformat()
            })
            logger.debug(f"Removed from context: {key}")
    
    def summarize_context(self) -> str:
        """
        Summarize context when it becomes too large.
        
        Requirements: 16.7 - Summarize context when approaching size limit
        
        Returns:
            Summary string
        """
        summary_parts = []
        
        # Summarize key information
        if 'agent_decisions' in self.context:
            decisions = self.context['agent_decisions']
            summary_parts.append(f"Made {len(decisions)} agent decisions")
        
        if 'web_searches' in self.context:
            searches = self.context['web_searches']
            summary_parts.append(f"Performed {len(searches)} web searches")
        
        if 'extracted_data' in self.context:
            summary_parts.append("Extracted medical data from reports")
        
        # Add session info
        summary_parts.append(f"Session started at {self.created_at.isoformat()}")
        
        summary = "; ".join(summary_parts)
        logger.info(f"Context summarized: {summary}")
        
        return summary
    
    def _summarize_old_context(self):
        """
        Summarize and compress old context data.
        
        Requirements: 16.7 - Summarize older information when context too large
        """
        # Create summary of current context
        summary = self.summarize_context()
        
        # Keep only essential recent data
        essential_keys = ['current_task', 'user_profile', 'session_id']
        new_context = {k: v for k, v in self.context.items() if k in essential_keys}
        
        # Add summary
        new_context['context_summary'] = summary
        new_context['summarized_at'] = datetime.utcnow().isoformat()
        
        # Replace context
        old_size = self._get_context_size()
        self.context = new_context
        new_size = self._get_context_size()
        
        logger.info(f"Context summarized: {old_size} -> {new_size} characters")
    
    def _get_context_size(self) -> int:
        """
        Get approximate size of context in characters.
        
        Requirements: 16.6 - Track context size
        
        Returns:
            Context size in characters
        """
        try:
            return len(json.dumps(self.context))
        except (TypeError, ValueError):
            # Fallback for non-serializable objects
            return len(str(self.context))
    
    def clear_context(self):
        """
        Clear context at end of session.
        
        Requirements: 16.5 - Clear context when session ends
        """
        logger.info(f"Clearing context for session {self.session_id}")
        self.context.clear()
        self.history.clear()
        self.session_id = None
    
    def share_context(self, agent_name: str, data: Dict[str, Any]):
        """
        Share context between agents.
        
        Requirements: 6.3, 6.4 - Enable agents to share context
        
        Args:
            agent_name: Name of agent sharing data
            data: Data to share
        """
        if 'shared_data' not in self.context:
            self.context['shared_data'] = {}
        
        self.context['shared_data'][agent_name] = {
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Agent {agent_name} shared context data")
    
    def get_shared_context(self, agent_name: Optional[str] = None) -> Any:
        """
        Get shared context from specific agent or all agents.
        
        Requirements: 6.3, 6.4 - Access shared context
        
        Args:
            agent_name: Optional specific agent name
            
        Returns:
            Shared context data
        """
        shared_data = self.context.get('shared_data', {})
        
        if agent_name:
            return shared_data.get(agent_name, {}).get('data')
        
        return shared_data
    
    def set_session_id(self, session_id: str):
        """Set session ID for this context."""
        self.session_id = session_id
        self.context['session_id'] = session_id
        logger.info(f"Session ID set: {session_id}")
    
    def get_session_id(self) -> Optional[str]:
        """Get current session ID."""
        return self.session_id
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get context modification history."""
        return self.history.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get context manager status.
        
        Returns:
            Status dictionary with metrics
        """
        return {
            'session_id': self.session_id,
            'context_size': self._get_context_size(),
            'max_context_size': self.max_context_size,
            'context_keys': list(self.context.keys()),
            'history_length': len(self.history),
            'created_at': self.created_at.isoformat(),
            'has_summary': 'context_summary' in self.context
        }
    
    def should_prevent_redundant_search(self, query: str) -> bool:
        """
        Check if query was already searched in this session.
        
        Requirements: 16.8 - Prevent redundant web searches
        
        Args:
            query: Search query to check
            
        Returns:
            True if search should be prevented (already done)
        """
        if 'web_searches' not in self.context:
            return False
        
        searches = self.context['web_searches']
        query_lower = query.lower().strip()
        
        for search in searches:
            if search.get('query', '').lower().strip() == query_lower:
                logger.info(f"Preventing redundant search for: {query}")
                return True
        
        return False
    
    def record_web_search(self, query: str, results: List[Any]):
        """
        Record web search in context.
        
        Requirements: 16.8 - Track searches to prevent redundancy
        
        Args:
            query: Search query
            results: Search results
        """
        if 'web_searches' not in self.context:
            self.context['web_searches'] = []
        
        self.context['web_searches'].append({
            'query': query,
            'result_count': len(results),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        logger.debug(f"Recorded web search: {query} ({len(results)} results)")
