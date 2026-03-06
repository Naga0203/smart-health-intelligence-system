"""
Data model classes for autonomous AI agents.

Provides data structures for search results, OCR results, agent decisions,
and agent metrics.

Requirements: 2.6, 4.6, 5.8, 10.1
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class SearchResult:
    """
    Result from web search operation.
    
    Requirements: 2.6 - Web search results with citations
    """
    title: str
    url: str
    snippet: str
    source_domain: str
    quality_score: float  # 0.0 to 1.0
    publication_date: Optional[datetime] = None
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate search result data."""
        if not self.title:
            raise ValueError("title is required")
        if not self.url:
            raise ValueError("url is required")
        if not 0.0 <= self.quality_score <= 1.0:
            raise ValueError(f"quality_score must be between 0.0 and 1.0, got {self.quality_score}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'title': self.title,
            'url': self.url,
            'snippet': self.snippet,
            'source_domain': self.source_domain,
            'quality_score': self.quality_score,
            'publication_date': self.publication_date.isoformat() if self.publication_date else None,
            'content': self.content,
            'metadata': self.metadata
        }
    
    def get_citation(self) -> str:
        """
        Get formatted citation for this search result.
        
        Requirements: 2.6 - Citations for web search results
        """
        citation = f"{self.title}. {self.source_domain}"
        if self.publication_date:
            citation += f" ({self.publication_date.strftime('%Y-%m-%d')})"
        citation += f". {self.url}"
        return citation


@dataclass
class OCRResult:
    """
    Result from OCR extraction operation.
    
    Requirements: 4.6 - OCR results with confidence scores
    """
    text: str
    confidence: float  # 0.0 to 1.0
    structured_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    extraction_time: float = 0.0  # Seconds
    pages_processed: int = 1
    format: str = "unknown"
    
    def __post_init__(self):
        """Validate OCR result data."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
        if self.pages_processed < 0:
            raise ValueError(f"pages_processed must be non-negative, got {self.pages_processed}")
        if self.extraction_time < 0:
            raise ValueError(f"extraction_time must be non-negative, got {self.extraction_time}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'text': self.text,
            'confidence': self.confidence,
            'structured_data': self.structured_data,
            'metadata': self.metadata,
            'extraction_time': self.extraction_time,
            'pages_processed': self.pages_processed,
            'format': self.format
        }
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if extraction confidence is above threshold."""
        return self.confidence >= threshold
    
    def get_low_confidence_fields(self, threshold: float = 0.7) -> List[str]:
        """
        Get list of structured data fields with low confidence.
        
        Requirements: 8.8 - Flag low confidence extractions for review
        """
        low_confidence = []
        for key, value in self.structured_data.items():
            if isinstance(value, dict) and 'confidence' in value:
                if value['confidence'] < threshold:
                    low_confidence.append(key)
        return low_confidence


@dataclass
class AgentDecision:
    """
    Record of autonomous agent decision.
    
    Requirements: 5.8 - Audit log of autonomous decisions
    """
    agent_name: str
    decision_type: str  # next_action, escalate, search, source_selection, etc.
    decision: str
    reasoning: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 1.0  # 0.0 to 1.0
    
    def __post_init__(self):
        """Validate agent decision data."""
        if not self.agent_name:
            raise ValueError("agent_name is required")
        if not self.decision_type:
            raise ValueError("decision_type is required")
        if not self.decision:
            raise ValueError("decision is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'agent_name': self.agent_name,
            'decision_type': self.decision_type,
            'decision': self.decision,
            'reasoning': self.reasoning,
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'confidence': self.confidence
        }
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if decision confidence is above threshold."""
        return self.confidence >= threshold


@dataclass
class AgentMetrics:
    """
    Metrics for agent performance tracking.
    
    Requirements: 10.1 - Track agent execution metrics
    """
    agent_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_duration: float = 0.0  # Seconds
    web_searches_performed: int = 0
    gemini_tokens_used: int = 0
    cache_hit_rate: float = 0.0  # 0.0 to 1.0
    last_execution: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate agent metrics data."""
        if not self.agent_name:
            raise ValueError("agent_name is required")
        if self.total_executions < 0:
            raise ValueError(f"total_executions must be non-negative, got {self.total_executions}")
        if self.successful_executions < 0:
            raise ValueError(f"successful_executions must be non-negative, got {self.successful_executions}")
        if self.failed_executions < 0:
            raise ValueError(f"failed_executions must be non-negative, got {self.failed_executions}")
        if not 0.0 <= self.cache_hit_rate <= 1.0:
            raise ValueError(f"cache_hit_rate must be between 0.0 and 1.0, got {self.cache_hit_rate}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'agent_name': self.agent_name,
            'total_executions': self.total_executions,
            'successful_executions': self.successful_executions,
            'failed_executions': self.failed_executions,
            'average_duration': self.average_duration,
            'web_searches_performed': self.web_searches_performed,
            'gemini_tokens_used': self.gemini_tokens_used,
            'cache_hit_rate': self.cache_hit_rate,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None
        }
    
    def get_success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_executions == 0:
            return 0.0
        return (self.successful_executions / self.total_executions) * 100
    
    def get_failure_rate(self) -> float:
        """Calculate failure rate as percentage."""
        if self.total_executions == 0:
            return 0.0
        return (self.failed_executions / self.total_executions) * 100
    
    def record_execution(self, success: bool, duration: float):
        """
        Record a new execution.
        
        Args:
            success: Whether the execution was successful
            duration: Execution duration in seconds
        """
        self.total_executions += 1
        if success:
            self.successful_executions += 1
        else:
            self.failed_executions += 1
        
        # Update average duration
        if self.average_duration == 0.0:
            self.average_duration = duration
        else:
            self.average_duration = (
                (self.average_duration * (self.total_executions - 1) + duration) 
                / self.total_executions
            )
        
        self.last_execution = datetime.utcnow()
    
    def record_web_search(self):
        """Record a web search operation."""
        self.web_searches_performed += 1
    
    def record_gemini_tokens(self, tokens: int):
        """Record Gemini API token usage."""
        self.gemini_tokens_used += tokens
    
    def update_cache_hit_rate(self, hits: int, total: int):
        """Update cache hit rate."""
        if total > 0:
            self.cache_hit_rate = hits / total
