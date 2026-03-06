"""
Dynamic Treatment Retrieval service.

Replaces static treatment knowledge base with dynamic retrieval
from current medical sources using web search and AI synthesis.

Requirements: 3.3, 3.4, 7.1, 7.2, 7.3, 7.5
"""

import logging
from typing import Dict, Any, List, Optional
from .web_search import WebSearchTool
from .models import SearchResult
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger('health_ai.agents.infrastructure')


class DynamicTreatmentRetrieval:
    """
    Dynamic retrieval of treatment information from current sources.
    
    Requirements:
    - 3.3, 3.4: Replace static data with dynamic retrieval
    - 7.1: Search for current treatment guidelines
    - 7.2: Search across multiple medical systems
    - 7.3: Synthesize information from multiple sources
    - 7.5: Get drug interaction information
    """
    
    MEDICAL_SYSTEMS = ['allopathy', 'ayurveda', 'homeopathy']
    
    def __init__(self, web_search: WebSearchTool, llm: Any = None):
        """
        Initialize dynamic treatment retrieval.
        
        Args:
            web_search: WebSearchTool instance
            llm: LangChain LLM for synthesis
        """
        self.web_search = web_search
        self.llm = llm
        
        logger.info("DynamicTreatmentRetrieval initialized")
    
    def get_treatment_info(
        self,
        disease: str,
        medical_system: str = "allopathy"
    ) -> Dict[str, Any]:
        """
        Get current treatment information for a disease.
        
        Requirements: 3.3, 3.4, 7.1 - Dynamic treatment retrieval
        
        Args:
            disease: Disease name
            medical_system: Medical system (allopathy, ayurveda, homeopathy)
            
        Returns:
            Treatment information with citations
        """
        if medical_system not in self.MEDICAL_SYSTEMS:
            logger.warning(f"Unknown medical system: {medical_system}, using allopathy")
            medical_system = "allopathy"
        
        # Construct search query
        query = f"{disease} treatment {medical_system}"
        
        # Search for treatment information
        try:
            search_results = self.web_search.search(query)
            
            if not search_results:
                logger.warning(f"No treatment information found for {disease}")
                return {
                    'disease': disease,
                    'medical_system': medical_system,
                    'treatment_info': 'No current treatment information available',
                    'sources': [],
                    'success': False
                }
            
            # Synthesize information from sources
            synthesized_info = self.synthesize_treatment_info(search_results)
            
            logger.info(
                f"Retrieved treatment info for {disease} ({medical_system}): "
                f"{len(search_results)} sources"
            )
            
            return {
                'disease': disease,
                'medical_system': medical_system,
                'treatment_info': synthesized_info,
                'sources': [r.get_citation() for r in search_results],
                'source_count': len(search_results),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving treatment info for {disease}: {e}")
            return {
                'disease': disease,
                'medical_system': medical_system,
                'treatment_info': f'Error retrieving treatment information: {e}',
                'sources': [],
                'success': False
            }
    
    def get_clinical_guidelines(self, condition: str) -> Dict[str, Any]:
        """
        Get current clinical practice guidelines.
        
        Requirements: 7.1 - Search for clinical guidelines
        
        Args:
            condition: Medical condition
            
        Returns:
            Clinical guidelines with citations
        """
        try:
            # Use specialized clinical guidelines search
            search_results = self.web_search.search_clinical_guidelines(condition)
            
            if not search_results:
                logger.warning(f"No clinical guidelines found for {condition}")
                return {
                    'condition': condition,
                    'guidelines': 'No current clinical guidelines available',
                    'sources': [],
                    'success': False
                }
            
            # Synthesize guidelines
            synthesized_guidelines = self.synthesize_treatment_info(search_results)
            
            logger.info(
                f"Retrieved clinical guidelines for {condition}: "
                f"{len(search_results)} sources"
            )
            
            return {
                'condition': condition,
                'guidelines': synthesized_guidelines,
                'sources': [r.get_citation() for r in search_results],
                'source_count': len(search_results),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving clinical guidelines for {condition}: {e}")
            return {
                'condition': condition,
                'guidelines': f'Error retrieving guidelines: {e}',
                'sources': [],
                'success': False
            }
    
    def get_drug_interactions(self, medications: List[str]) -> Dict[str, Any]:
        """
        Get drug interaction information.
        
        Requirements: 7.5 - Search for drug interactions dynamically
        
        Args:
            medications: List of medication names
            
        Returns:
            Drug interaction information
        """
        if not medications:
            return {
                'medications': [],
                'interactions': 'No medications provided',
                'success': False
            }
        
        try:
            # Search for each drug's interactions
            all_interactions = []
            
            for drug in medications:
                drug_info = self.web_search.search_drug_information(drug)
                all_interactions.append(drug_info)
            
            # If multiple drugs, search for specific interactions
            if len(medications) > 1:
                interaction_query = f"{' '.join(medications)} drug interactions"
                interaction_results = self.web_search.search(interaction_query)
                
                synthesized_interactions = self.synthesize_treatment_info(interaction_results)
            else:
                synthesized_interactions = "Single medication - check individual drug information"
            
            logger.info(f"Retrieved drug interactions for {len(medications)} medications")
            
            return {
                'medications': medications,
                'interactions': synthesized_interactions,
                'individual_drug_info': all_interactions,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving drug interactions: {e}")
            return {
                'medications': medications,
                'interactions': f'Error retrieving interactions: {e}',
                'success': False
            }
    
    def synthesize_treatment_info(self, sources: List[SearchResult]) -> str:
        """
        Synthesize treatment information from multiple sources.
        
        Requirements: 7.3 - Synthesize information from multiple sources
        
        Args:
            sources: List of search results
            
        Returns:
            Synthesized information string
        """
        if not sources:
            return "No sources available for synthesis"
        
        # If LLM available, use it to synthesize
        if self.llm:
            try:
                prompt = self._create_synthesis_prompt()
                chain = prompt | self.llm | StrOutputParser()
                
                # Prepare source content
                source_content = "\n\n".join([
                    f"Source {i+1} ({s.source_domain}):\n{s.snippet}"
                    for i, s in enumerate(sources[:5])  # Limit to top 5 sources
                ])
                
                synthesized = chain.invoke({
                    'sources': source_content
                })
                
                logger.info("Treatment information synthesized using LLM")
                return synthesized
                
            except Exception as e:
                logger.error(f"Error in LLM synthesis: {e}")
        
        # Fallback: concatenate snippets
        synthesis = "Treatment information from multiple sources:\n\n"
        
        for i, source in enumerate(sources[:5], 1):
            synthesis += f"{i}. {source.snippet} (Source: {source.source_domain})\n\n"
        
        logger.info("Treatment information synthesized using fallback method")
        return synthesis
    
    def get_multi_system_treatment(self, disease: str) -> Dict[str, Any]:
        """
        Get treatment information across all medical systems.
        
        Requirements: 7.2 - Search across multiple medical systems
        
        Args:
            disease: Disease name
            
        Returns:
            Treatment information for all systems
        """
        results = {}
        
        for system in self.MEDICAL_SYSTEMS:
            results[system] = self.get_treatment_info(disease, system)
        
        logger.info(f"Retrieved multi-system treatment info for {disease}")
        
        return {
            'disease': disease,
            'systems': results,
            'systems_searched': len(self.MEDICAL_SYSTEMS)
        }
    
    def _create_synthesis_prompt(self) -> ChatPromptTemplate:
        """Create prompt for information synthesis."""
        return ChatPromptTemplate.from_messages([
            ("system", "You are a medical information synthesis assistant. "
                      "Analyze multiple sources and create a coherent, accurate summary. "
                      "Focus on treatment approaches, evidence levels, and important considerations. "
                      "Always emphasize that this is for educational purposes and professional "
                      "consultation is required."),
            ("human", "Synthesize the following medical information from multiple sources:\n\n"
                     "{sources}\n\n"
                     "Provide a clear, coherent summary of the treatment information.")
        ])
    
    def get_evidence_based_treatment(
        self,
        disease: str,
        include_evidence_levels: bool = True
    ) -> Dict[str, Any]:
        """
        Get evidence-based treatment information with evidence levels.
        
        Requirements: 7.4 - Include evidence levels in treatment info
        
        Args:
            disease: Disease name
            include_evidence_levels: Whether to include evidence level analysis
            
        Returns:
            Treatment information with evidence levels
        """
        # Get treatment information
        treatment_info = self.get_treatment_info(disease)
        
        if not treatment_info['success']:
            return treatment_info
        
        # If evidence levels requested and LLM available, analyze evidence
        if include_evidence_levels and self.llm:
            try:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are a medical evidence analysis assistant. "
                              "Analyze treatment information and identify evidence levels "
                              "(e.g., randomized controlled trials, meta-analyses, expert opinion)."),
                    ("human", "Analyze the evidence levels in this treatment information:\n\n"
                             "{treatment_info}\n\n"
                             "Identify and categorize the evidence levels.")
                ])
                
                chain = prompt | self.llm | StrOutputParser()
                
                evidence_analysis = chain.invoke({
                    'treatment_info': treatment_info['treatment_info']
                })
                
                treatment_info['evidence_analysis'] = evidence_analysis
                logger.info(f"Evidence levels analyzed for {disease}")
                
            except Exception as e:
                logger.error(f"Error analyzing evidence levels: {e}")
                treatment_info['evidence_analysis'] = "Evidence level analysis unavailable"
        
        return treatment_info
