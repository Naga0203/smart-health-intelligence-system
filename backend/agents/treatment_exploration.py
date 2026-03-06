"""
Treatment Exploration Agent - Migrated to Enhanced Architecture.

Provides comprehensive treatment information across multiple medical systems
using dynamic retrieval instead of static data.

Requirements: 1.1, 1.2, 1.3, 1.5, 3.1, 3.3, 3.4, 7.1, 7.2, 7.3, 7.4, 7.5, 7.7, 7.8, 1.6
"""

import logging
from typing import Dict, Any, Optional, List

from .infrastructure.enhanced_base_agent import EnhancedBaseHealthAgent
from .infrastructure.config import AgentConfig
from .infrastructure.dynamic_treatment import DynamicTreatmentRetrieval

logger = logging.getLogger('health_ai.treatment_exploration')


class TreatmentExplorationAgent(EnhancedBaseHealthAgent):
    """
    AI agent for exploring detailed treatment options across medical systems.
    
    Migrated to use:
    - Enhanced BaseHealthAgent with autonomous capabilities
    - DynamicTreatmentRetrieval for current treatment information
    - Web search for latest guidelines
    - Multi-system treatment search (allopathy, ayurveda, homeopathy)
    - Drug interaction searches
    - Evidence level inclusion
    - Source citations
    - Safety guardrails
    
    Requirements:
    - 1.1, 1.2, 1.3: LangChain framework with Gemini AI
    - 1.5: Autonomous decision-making
    - 1.6: Preserve existing functionality
    - 3.1, 3.3, 3.4: Replace static data with dynamic retrieval
    - 7.1: Web search for current treatment guidelines
    - 7.2: Multi-system treatment search
    - 7.3: Synthesize information from multiple sources
    - 7.4: Include evidence levels
    - 7.5: Drug interaction searches
    - 7.7: Cite sources
    - 7.8: Medical disclaimers
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the treatment exploration agent.
        
        Args:
            config: Agent configuration (uses defaults if not provided)
        """
        # Initialize with enhanced base agent
        if config is None:
            config = AgentConfig(
                agent_name="TreatmentExplorationAgent",
                enable_web_search=True,
                enable_caching=True,
                monitoring_enabled=True
            )
        
        super().__init__("TreatmentExplorationAgent", config)
        
        # Initialize dynamic treatment retrieval service
        self.dynamic_treatment = DynamicTreatmentRetrieval(
            web_search=self.web_search_tool,
            llm=self.llm
        )
        
        logger.info("TreatmentExplorationAgent initialized with enhanced architecture")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user request for treatment information.
        
        Requirements: 1.6 - Preserve existing functionality
        
        Args:
            input_data: Dictionary containing:
                - disease: The disease to explore (required)
                - system: Specific medical system (optional, defaults to all)
                - query: Specific question (optional)
                - medications: List of medications for interaction check (optional)
                - include_evidence: Whether to include evidence levels (optional, default True)
                
        Returns:
            Dictionary with treatment information
        """
        # Validate request
        if not self._validate_request(input_data):
            return self.format_agent_response(
                success=False,
                message="Invalid request: 'disease' is required"
            )
        
        disease = input_data.get("disease", "").strip()
        system = input_data.get("system", "all").lower()
        medications = input_data.get("medications", [])
        include_evidence = input_data.get("include_evidence", True)
        
        self.log_agent_action(
            "exploring_treatment",
            {"disease": disease, "system": system, "medications": medications}
        )
        
        try:
            # Decide whether to search for specific system or all systems
            if system == "all":
                # Requirement 7.2: Multi-system treatment search
                treatment_info = self._get_multi_system_treatment(disease, include_evidence)
            else:
                # Single system search
                treatment_info = self._get_single_system_treatment(
                    disease, system, include_evidence
                )
            
            # Requirement 7.5: Drug interaction searches
            if medications:
                drug_interactions = self._get_drug_interactions(medications)
                treatment_info['drug_interactions'] = drug_interactions
            
            # Requirement 7.7: Cite sources
            # Sources are already included in treatment_info from dynamic retrieval
            
            # Requirement 7.8: Add medical disclaimers
            treatment_info['disclaimer'] = self._get_medical_disclaimer()
            
            # Apply safety guardrails to all text content
            treatment_info = self._apply_safety_to_treatment_info(treatment_info)
            
            return self.format_agent_response(
                success=True,
                data=treatment_info,
                message=f"Treatment information retrieved for {disease}"
            )
            
        except Exception as e:
            logger.error(f"Error processing treatment request: {e}")
            return self.format_agent_response(
                success=False,
                message=f"Error retrieving treatment information: {e}",
                metadata={'error': str(e)}
            )
    
    def _validate_request(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data.
        
        Args:
            input_data: Input dictionary
            
        Returns:
            True if valid, False otherwise
        """
        return (
            input_data is not None and
            "disease" in input_data and
            input_data["disease"].strip()
        )
    
    def _get_multi_system_treatment(
        self,
        disease: str,
        include_evidence: bool
    ) -> Dict[str, Any]:
        """
        Get treatment information across all medical systems.
        
        Requirements: 7.2 - Multi-system treatment search
        
        Args:
            disease: Disease name
            include_evidence: Whether to include evidence levels
            
        Returns:
            Treatment information for all systems
        """
        logger.info(f"Retrieving multi-system treatment for {disease}")
        
        # Use dynamic retrieval for multi-system search
        multi_system_info = self.dynamic_treatment.get_multi_system_treatment(disease)
        
        # If evidence levels requested, get evidence-based analysis
        if include_evidence:
            # Requirement 7.4: Include evidence levels
            evidence_info = self.dynamic_treatment.get_evidence_based_treatment(
                disease,
                include_evidence_levels=True
            )
            multi_system_info['evidence_analysis'] = evidence_info.get('evidence_analysis')
        
        # Get clinical guidelines
        # Requirement 7.1: Web search for current treatment guidelines
        guidelines = self.dynamic_treatment.get_clinical_guidelines(disease)
        multi_system_info['clinical_guidelines'] = guidelines
        
        return multi_system_info
    
    def _get_single_system_treatment(
        self,
        disease: str,
        system: str,
        include_evidence: bool
    ) -> Dict[str, Any]:
        """
        Get treatment information for a specific medical system.
        
        Requirements: 3.3, 3.4 - Dynamic retrieval replaces static data
        
        Args:
            disease: Disease name
            system: Medical system (allopathy, ayurveda, homeopathy)
            include_evidence: Whether to include evidence levels
            
        Returns:
            Treatment information for specified system
        """
        logger.info(f"Retrieving {system} treatment for {disease}")
        
        # Use dynamic retrieval instead of static data
        if include_evidence:
            # Requirement 7.4: Include evidence levels
            treatment_info = self.dynamic_treatment.get_evidence_based_treatment(
                disease,
                include_evidence_levels=True
            )
        else:
            treatment_info = self.dynamic_treatment.get_treatment_info(disease, system)
        
        # Get clinical guidelines
        # Requirement 7.1: Web search for current treatment guidelines
        guidelines = self.dynamic_treatment.get_clinical_guidelines(disease)
        treatment_info['clinical_guidelines'] = guidelines
        
        return treatment_info
    
    def _get_drug_interactions(self, medications: List[str]) -> Dict[str, Any]:
        """
        Get drug interaction information.
        
        Requirements: 7.5 - Drug interaction searches
        
        Args:
            medications: List of medication names
            
        Returns:
            Drug interaction information
        """
        logger.info(f"Checking drug interactions for {len(medications)} medications")
        
        # Use dynamic retrieval for drug interactions
        interactions = self.dynamic_treatment.get_drug_interactions(medications)
        
        # Check for emergency indicators in interactions
        if interactions.get('success'):
            interaction_text = str(interactions.get('interactions', ''))
            if self.safety_guardrails.check_emergency_indicators(interaction_text):
                interactions['warning'] = (
                    "IMPORTANT: Potential serious drug interactions detected. "
                    "Consult a healthcare professional immediately."
                )
        
        return interactions
    
    def _get_medical_disclaimer(self) -> str:
        """
        Get comprehensive medical disclaimer.
        
        Requirements: 7.8 - Medical disclaimers
        
        Returns:
            Medical disclaimer text
        """
        return (
            "MEDICAL DISCLAIMER: This information is for educational purposes only "
            "and is not a substitute for professional medical advice, diagnosis, or treatment. "
            "Always seek the advice of your physician or other qualified health provider "
            "with any questions you may have regarding a medical condition. "
            "Never disregard professional medical advice or delay in seeking it because "
            "of information provided here. Treatment decisions should be made in consultation "
            "with qualified healthcare professionals. Medication dosages must be prescribed "
            "and monitored by licensed physicians. If you think you may have a medical emergency, "
            "call your doctor or emergency services immediately."
        )
    
    def _apply_safety_to_treatment_info(
        self,
        treatment_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply safety guardrails to treatment information.
        
        Requirements: 17.1, 17.2, 17.4, 17.5 - Safety guardrails
        
        Args:
            treatment_info: Treatment information dictionary
            
        Returns:
            Treatment information with safety guardrails applied
        """
        # Apply safety guardrails to text fields
        def apply_to_text(obj):
            if isinstance(obj, str):
                return self.safety_guardrails.apply_all_guardrails(obj)
            elif isinstance(obj, dict):
                return {k: apply_to_text(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [apply_to_text(item) for item in obj]
            else:
                return obj
        
        return apply_to_text(treatment_info)
    
    def get_treatment_comparison(
        self,
        disease: str,
        systems: List[str]
    ) -> Dict[str, Any]:
        """
        Compare treatment approaches across specified medical systems.
        
        Requirements: 7.2, 7.3 - Multi-system search and synthesis
        
        Args:
            disease: Disease name
            systems: List of medical systems to compare
            
        Returns:
            Comparison of treatment approaches
        """
        logger.info(f"Comparing treatment approaches for {disease} across {systems}")
        
        comparison = {
            'disease': disease,
            'systems_compared': systems,
            'treatments': {}
        }
        
        # Get treatment info for each system
        for system in systems:
            treatment_info = self.dynamic_treatment.get_treatment_info(disease, system)
            comparison['treatments'][system] = treatment_info
        
        # Use LLM to synthesize comparison if available
        if self.llm:
            try:
                from langchain_core.prompts import ChatPromptTemplate
                from langchain_core.output_parsers import StrOutputParser
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are a medical information synthesis assistant. "
                              "Compare treatment approaches across different medical systems "
                              "objectively, noting similarities, differences, and evidence levels."),
                    ("human", "Compare these treatment approaches for {disease}:\n\n{treatments}\n\n"
                             "Provide an objective comparison highlighting key differences and similarities.")
                ])
                
                chain = prompt | self.llm | StrOutputParser()
                
                treatments_text = "\n\n".join([
                    f"{system}: {info.get('treatment_info', 'N/A')}"
                    for system, info in comparison['treatments'].items()
                ])
                
                comparison['synthesis'] = chain.invoke({
                    'disease': disease,
                    'treatments': treatments_text
                })
                
            except Exception as e:
                logger.error(f"Error synthesizing comparison: {e}")
                comparison['synthesis'] = "Comparison synthesis unavailable"
        
        # Apply safety guardrails
        comparison = self._apply_safety_to_treatment_info(comparison)
        comparison['disclaimer'] = self._get_medical_disclaimer()
        
        return comparison
    
    def search_treatment_guidelines(
        self,
        condition: str,
        guideline_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for specific treatment guidelines.
        
        Requirements: 7.1 - Web search for current treatment guidelines
        
        Args:
            condition: Medical condition
            guideline_type: Type of guidelines (e.g., 'clinical', 'emergency')
            
        Returns:
            Treatment guidelines with citations
        """
        logger.info(f"Searching treatment guidelines for {condition}")
        
        # Get clinical guidelines
        guidelines = self.dynamic_treatment.get_clinical_guidelines(condition)
        
        # If specific guideline type requested, refine search
        if guideline_type:
            query = f"{condition} {guideline_type} treatment guidelines"
            search_results = self.search_web(query)
            
            if search_results:
                # Synthesize guideline-specific information
                synthesized = self.dynamic_treatment.synthesize_treatment_info(search_results)
                guidelines['specific_guidelines'] = synthesized
                guidelines['sources'].extend([r.get_citation() for r in search_results])
        
        # Apply safety guardrails
        guidelines = self._apply_safety_to_treatment_info(guidelines)
        guidelines['disclaimer'] = self._get_medical_disclaimer()
        
        return guidelines
