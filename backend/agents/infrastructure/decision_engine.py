"""
Decision Engine for autonomous agent decision-making.

Enables agents to make autonomous decisions about actions, escalations,
conflict resolution, and source selection using LLM reasoning.

Requirements: 5.1, 5.2, 5.3, 5.4, 5.7
"""

import logging
from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .models import AgentDecision, SearchResult
from datetime import datetime

logger = logging.getLogger('health_ai.agents.infrastructure')


class DecisionEngine:
    """
    Engine for autonomous agent decision-making.
    
    Requirements:
    - 5.1: Decide which agents to invoke
    - 5.2: Decide on information completeness
    - 5.3: Resolve conflicts between sources
    - 5.4: Decide when to escalate
    - 5.7: Select best source from multiple options
    """
    
    def __init__(self, llm: Any = None):
        """
        Initialize decision engine.
        
        Args:
            llm: LangChain LLM instance for reasoning
        """
        self.llm = llm
        self.decision_log: List[AgentDecision] = []
        
        logger.info("DecisionEngine initialized")
    
    def decide_next_action(self, context: Dict[str, Any], options: List[str]) -> str:
        """
        Decide next action based on current context.
        
        Requirements: 5.1 - Autonomous decision on next action
        
        Args:
            context: Current context dictionary
            options: List of possible actions
            
        Returns:
            Selected action
        """
        if not self.llm:
            # Fallback: select first option
            logger.warning("No LLM available, using fallback decision")
            decision = options[0] if options else "continue"
            reasoning = "Fallback decision (no LLM available)"
        else:
            # Use LLM to reason about best action
            prompt = self._create_action_decision_prompt()
            chain = prompt | self.llm | StrOutputParser()
            
            try:
                response = chain.invoke({
                    'context': str(context),
                    'options': ', '.join(options)
                })
                
                # Parse response to extract decision
                decision = self._parse_decision_from_response(response, options)
                reasoning = response
                
            except Exception as e:
                logger.error(f"Error in LLM decision-making: {e}")
                decision = options[0] if options else "continue"
                reasoning = f"Fallback decision due to error: {e}"
        
        # Log decision
        agent_decision = AgentDecision(
            agent_name="decision_engine",
            decision_type="next_action",
            decision=decision,
            reasoning=reasoning,
            context=context
        )
        self.decision_log.append(agent_decision)
        
        logger.info(f"Next action decided: {decision}")
        
        return decision
    
    def should_search_web(self, query: str, context: Dict[str, Any]) -> bool:
        """
        Decide if web search is needed or if cached/context info is sufficient.
        
        Requirements: 5.2 - Decide on information completeness
        
        Args:
            query: Potential search query
            context: Current context with available information
            
        Returns:
            True if web search should be performed
        """
        # Check if information already in context
        if 'web_searches' in context:
            for search in context['web_searches']:
                if search.get('query', '').lower() == query.lower():
                    logger.info(f"Information already available in context for: {query}")
                    return False
        
        # Check if context has relevant information
        if self._has_relevant_info_in_context(query, context):
            logger.info(f"Relevant information found in context for: {query}")
            return False
        
        # Use LLM to decide if search is needed
        if self.llm:
            try:
                prompt = self._create_search_decision_prompt()
                chain = prompt | self.llm | StrOutputParser()
                
                response = chain.invoke({
                    'query': query,
                    'context': str(context)
                })
                
                should_search = 'yes' in response.lower() or 'search' in response.lower()
                
                logger.info(f"LLM decided search needed: {should_search} for query: {query}")
                return should_search
                
            except Exception as e:
                logger.error(f"Error in search decision: {e}")
                return True  # Default to searching on error
        
        # Default: perform search
        return True
    
    def should_escalate(self, situation: Dict[str, Any]) -> bool:
        """
        Decide if situation requires human review.
        
        Requirements: 5.4 - Decide when to escalate to human review
        
        Args:
            situation: Situation dictionary with context
            
        Returns:
            True if escalation is needed
        """
        # Check for emergency indicators
        if situation.get('is_emergency', False):
            logger.warning("Escalating due to emergency indicators")
            return True
        
        # Check for low confidence
        confidence = situation.get('confidence', 1.0)
        if confidence < 0.5:
            logger.warning(f"Escalating due to low confidence: {confidence}")
            return True
        
        # Check for conflicting information
        if situation.get('has_conflicts', False):
            logger.warning("Escalating due to conflicting information")
            return True
        
        # Use LLM for complex escalation decisions
        if self.llm:
            try:
                prompt = self._create_escalation_decision_prompt()
                chain = prompt | self.llm | StrOutputParser()
                
                response = chain.invoke({
                    'situation': str(situation)
                })
                
                should_escalate = 'yes' in response.lower() or 'escalate' in response.lower()
                
                if should_escalate:
                    logger.warning(f"LLM decided to escalate: {response}")
                
                return should_escalate
                
            except Exception as e:
                logger.error(f"Error in escalation decision: {e}")
                return False  # Default to not escalating on error
        
        return False
    
    def resolve_conflict(self, conflicting_info: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolve conflicts between multiple information sources.
        
        Requirements: 5.3 - Resolve conflicts using reasoning
        
        Args:
            conflicting_info: List of conflicting information dictionaries
            
        Returns:
            Resolved information dictionary
        """
        if not conflicting_info:
            return {}
        
        if len(conflicting_info) == 1:
            return conflicting_info[0]
        
        # Use LLM to resolve conflicts
        if self.llm:
            try:
                prompt = self._create_conflict_resolution_prompt()
                chain = prompt | self.llm | StrOutputParser()
                
                response = chain.invoke({
                    'conflicting_info': str(conflicting_info)
                })
                
                # Log resolution decision
                agent_decision = AgentDecision(
                    agent_name="decision_engine",
                    decision_type="conflict_resolution",
                    decision=response,
                    reasoning="LLM-based conflict resolution",
                    context={'conflicting_info': conflicting_info}
                )
                self.decision_log.append(agent_decision)
                
                logger.info("Conflict resolved using LLM reasoning")
                
                return {
                    'resolved_info': response,
                    'resolution_method': 'llm_reasoning',
                    'sources_considered': len(conflicting_info)
                }
                
            except Exception as e:
                logger.error(f"Error in conflict resolution: {e}")
        
        # Fallback: select source with highest quality score
        best_source = max(
            conflicting_info,
            key=lambda x: x.get('quality_score', 0.5)
        )
        
        logger.info("Conflict resolved using quality score fallback")
        
        return {
            'resolved_info': best_source,
            'resolution_method': 'quality_score',
            'sources_considered': len(conflicting_info)
        }
    
    def select_best_source(self, sources: List[SearchResult]) -> SearchResult:
        """
        Select most reliable source from multiple options.
        
        Requirements: 5.7 - Select most reliable source
        
        Args:
            sources: List of search results
            
        Returns:
            Best search result
        """
        if not sources:
            raise ValueError("No sources provided")
        
        if len(sources) == 1:
            return sources[0]
        
        # Sort by quality score (highest first)
        sorted_sources = sorted(
            sources,
            key=lambda x: x.quality_score,
            reverse=True
        )
        
        best_source = sorted_sources[0]
        
        logger.info(
            f"Selected best source: {best_source.source_domain} "
            f"(quality: {best_source.quality_score})"
        )
        
        # Log decision
        agent_decision = AgentDecision(
            agent_name="decision_engine",
            decision_type="source_selection",
            decision=best_source.url,
            reasoning=f"Selected based on quality score: {best_source.quality_score}",
            context={'total_sources': len(sources)}
        )
        self.decision_log.append(agent_decision)
        
        return best_source
    
    def _has_relevant_info_in_context(self, query: str, context: Dict[str, Any]) -> bool:
        """Check if context has relevant information for query."""
        query_lower = query.lower()
        
        # Check if query terms appear in context
        context_str = str(context).lower()
        query_terms = query_lower.split()
        
        # If most query terms are in context, consider it relevant
        matches = sum(1 for term in query_terms if term in context_str)
        relevance_threshold = len(query_terms) * 0.6
        
        return matches >= relevance_threshold
    
    def _parse_decision_from_response(self, response: str, options: List[str]) -> str:
        """Parse decision from LLM response."""
        response_lower = response.lower()
        
        # Check if any option appears in response
        for option in options:
            if option.lower() in response_lower:
                return option
        
        # Default to first option
        return options[0] if options else "continue"
    
    def _create_action_decision_prompt(self) -> ChatPromptTemplate:
        """Create prompt for action decision."""
        return ChatPromptTemplate.from_messages([
            ("system", "You are a decision-making assistant for a health AI system. "
                      "Analyze the context and select the best next action."),
            ("human", "Context: {context}\n\nAvailable options: {options}\n\n"
                     "Which action should be taken next? Explain your reasoning and state your decision clearly.")
        ])
    
    def _create_search_decision_prompt(self) -> ChatPromptTemplate:
        """Create prompt for search decision."""
        return ChatPromptTemplate.from_messages([
            ("system", "You are a decision-making assistant. Determine if a web search is needed "
                      "or if the available context already contains sufficient information."),
            ("human", "Query: {query}\n\nAvailable context: {context}\n\n"
                     "Should we perform a web search? Answer YES or NO and explain why.")
        ])
    
    def _create_escalation_decision_prompt(self) -> ChatPromptTemplate:
        """Create prompt for escalation decision."""
        return ChatPromptTemplate.from_messages([
            ("system", "You are a decision-making assistant for a health AI system. "
                      "Determine if a situation requires human review and escalation."),
            ("human", "Situation: {situation}\n\n"
                     "Should this be escalated to human review? Answer YES or NO and explain why.")
        ])
    
    def _create_conflict_resolution_prompt(self) -> ChatPromptTemplate:
        """Create prompt for conflict resolution."""
        return ChatPromptTemplate.from_messages([
            ("system", "You are a decision-making assistant. Analyze conflicting information "
                      "from multiple sources and provide a reasoned resolution."),
            ("human", "Conflicting information: {conflicting_info}\n\n"
                     "Analyze these sources and provide the most accurate information based on "
                     "source reliability, recency, and consistency.")
        ])
    
    def get_decision_log(self) -> List[AgentDecision]:
        """Get log of all decisions made."""
        return self.decision_log.copy()
    
    def clear_decision_log(self):
        """Clear decision log."""
        self.decision_log.clear()
        logger.info("Decision log cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get decision-making statistics."""
        from collections import Counter
        
        decision_types = Counter(d.decision_type for d in self.decision_log)
        
        return {
            'total_decisions': len(self.decision_log),
            'decision_types': dict(decision_types),
            'has_llm': bool(self.llm)
        }
