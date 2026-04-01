"""
Clinical Guidelines Agent

AI agent for generating comprehensive clinical guidelines for treatment-disease combinations.
Leverages LangChain framework and Gemini AI to provide evidence-based clinical information.

Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 7.1
"""

import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .infrastructure.enhanced_base_agent import EnhancedBaseHealthAgent
from .infrastructure.config import AgentConfig

logger = logging.getLogger('health_ai.agents.clinical_guidelines')

# Maximum allowed length for treatment/disease input strings
_MAX_INPUT_LENGTH = 200
# Pattern for allowed characters in treatment/disease names
_SAFE_INPUT_PATTERN = re.compile(r'^[\w\s\-\(\)\.,/]+$')


class ClinicalGuidelinesAgent(EnhancedBaseHealthAgent):
    """
    AI agent for generating comprehensive clinical guidelines for treatment-disease combinations.

    Inherits from EnhancedBaseHealthAgent to leverage:
    - LangChain framework integration with Gemini AI
    - Web search capabilities for current research
    - Safety guardrails for medical content
    - Circuit breaker and retry logic
    - Monitoring and logging

    Generates:
    - Treatment details and mechanisms
    - Disease-specific protocols
    - Research evidence and studies
    - Clinical recommendations
    - Dosage guidelines (when applicable)
    - Contraindications and warnings

    Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the Clinical Guidelines Agent.

        Args:
            config: Optional AgentConfig for customizing agent behaviour.
                    Defaults to standard AgentConfig with 30-second timeout.
        """
        super().__init__("ClinicalGuidelinesAgent", config)

        # LangChain chain for generating clinical guidelines content
        self.guidelines_chain = self.create_agent_chain(
            system_prompt="""You are a clinical pharmacologist and evidence-based medicine specialist.
Your role is to provide comprehensive, accurate clinical guidelines for specific treatment-disease combinations.

Guidelines for your responses:
- Base all information on current, peer-reviewed medical evidence
- Include specific mechanisms of action and clinical protocols
- Reference established clinical guidelines (e.g., WHO, NICE, AHA) where applicable
- Clearly distinguish between strong evidence and emerging research
- Always include appropriate safety warnings and contraindications
- Use precise medical terminology while remaining accessible to healthcare professionals
- Include a medical disclaimer emphasising professional consultation

CRITICAL: This information is for qualified healthcare professionals only.
Always recommend consulting current clinical guidelines and specialist advice for individual patient decisions.""",

            human_prompt="""Generate comprehensive clinical guidelines for the following treatment-disease combination:

Treatment: {treatment}
Disease: {disease}

Provide a structured JSON response with exactly these fields:
{{
  "treatment_details": "Detailed description of the treatment, its mechanism of action, pharmacology, and clinical use for this disease",
  "disease_protocols": "Disease-specific treatment protocols, staging considerations, and standard of care guidelines",
  "research_evidence": "Summary of key research studies, clinical trials, and evidence base supporting this treatment",
  "clinical_recommendations": "Specific clinical recommendations for healthcare practitioners managing this treatment",
  "dosage_guidelines": "Dosage information, administration routes, titration schedules, and monitoring parameters (or empty string if not applicable)",
  "contraindications": "Absolute and relative contraindications, drug interactions, warnings, and precautions",
  "sources": ["Citation 1", "Citation 2", "Citation 3"],
  "disclaimer": "Medical disclaimer text"
}}

Ensure all fields contain substantive, evidence-based content. The dosage_guidelines field may be an empty string if not applicable."""
        )

        logger.info("ClinicalGuidelinesAgent initialized")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method — delegates to process_with_monitoring for
        timeout enforcement, error handling, and metrics tracking.

        Args:
            input_data: {
                "treatment": str,  # Required
                "disease": str     # Required
            }

        Returns:
            Standardised agent response dict (see format_agent_response).
        """
        return self.process_with_monitoring(input_data)

    # ------------------------------------------------------------------
    # Internal processing
    # ------------------------------------------------------------------

    def _process_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core processing logic called by process_with_monitoring.

        Orchestrates input validation, content generation, safety guardrails,
        and response formatting.

        Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8
        """
        # 1. Validate and sanitize inputs
        validation = self._validate_request(input_data)
        if not validation["valid"]:
            return self.format_agent_response(
                success=False,
                message=validation["message"]
            )

        treatment = validation["treatment"]
        disease = validation["disease"]

        self.log_agent_action("generate_clinical_guidelines", {
            "treatment": treatment,
            "disease": disease
        })

        try:
            # 2. Generate all content sections
            guidelines_data = self.execute_with_retry(
                lambda: self._generate_guidelines(treatment, disease)
            )

            if guidelines_data:
                return self.format_agent_response(
                    success=True,
                    data=guidelines_data,
                    message="Clinical guidelines retrieved successfully"
                )

            # 3. Fallback if generation returned nothing
            return self.format_agent_response(
                success=False,
                message="Unable to generate clinical guidelines. Please try again."
            )

        except TimeoutError as e:
            logger.error(
                f"ClinicalGuidelinesAgent: timeout generating guidelines for "
                f"treatment='{treatment}' disease='{disease}': {e}"
            )
            return self.format_agent_response(
                success=False,
                message="Request timeout: Clinical guidelines generation exceeded the time limit. Please try again.",
                metadata={"error": "timeout"}
            )

        except Exception as e:
            # Detect LLM / API service errors by inspecting the exception type name and message
            error_type = type(e).__name__
            error_str = str(e).lower()
            is_llm_error = any(
                indicator in error_str or indicator in error_type.lower()
                for indicator in (
                    "quota", "rate limit", "ratelimit", "resource_exhausted",
                    "service unavailable", "unavailable", "api error",
                    "google.api_core", "generativeai", "gemini",
                )
            )

            if is_llm_error:
                logger.error(
                    f"ClinicalGuidelinesAgent: LLM service error for "
                    f"treatment='{treatment}' disease='{disease}': {e}",
                    exc_info=True,
                )
                return self.format_agent_response(
                    success=False,
                    message="AI service temporarily unavailable. Please try again later.",
                    metadata={"error": "llm_service_error", "error_type": error_type}
                )

            logger.error(
                f"ClinicalGuidelinesAgent: processing failed for "
                f"treatment='{treatment}' disease='{disease}': {e}",
                exc_info=True,
            )
            return self.format_agent_response(
                success=False,
                message=f"Error generating clinical guidelines: {str(e)}",
                metadata={"error": "processing_error", "error_type": error_type}
            )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_request(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize treatment and disease parameters.

        Checks:
        - Both fields are present and non-empty
        - Neither field exceeds the maximum allowed length
        - Both fields contain only safe characters (prevents injection)

        Requirements: 7.1

        Args:
            input_data: Raw input dictionary from the caller.

        Returns:
            Dict with keys:
                valid (bool): Whether validation passed.
                message (str): Error description when valid=False.
                treatment (str): Sanitized treatment value (when valid=True).
                disease (str): Sanitized disease value (when valid=True).
        """
        if not input_data:
            return {"valid": False, "message": "Input data is required"}

        treatment = input_data.get("treatment", "")
        disease = input_data.get("disease", "")

        # Presence checks
        if not treatment or not str(treatment).strip():
            return {"valid": False, "message": "Missing required parameter: treatment"}
        if not disease or not str(disease).strip():
            return {"valid": False, "message": "Missing required parameter: disease"}

        treatment = str(treatment).strip()
        disease = str(disease).strip()

        # Length checks
        if len(treatment) > _MAX_INPUT_LENGTH:
            return {"valid": False, "message": f"Parameter 'treatment' exceeds maximum length of {_MAX_INPUT_LENGTH}"}
        if len(disease) > _MAX_INPUT_LENGTH:
            return {"valid": False, "message": f"Parameter 'disease' exceeds maximum length of {_MAX_INPUT_LENGTH}"}

        # Character safety checks (prevent injection attacks)
        if not _SAFE_INPUT_PATTERN.match(treatment):
            return {"valid": False, "message": "Parameter 'treatment' contains invalid characters"}
        if not _SAFE_INPUT_PATTERN.match(disease):
            return {"valid": False, "message": "Parameter 'disease' contains invalid characters"}

        return {
            "valid": True,
            "message": "Validation passed",
            "treatment": treatment,
            "disease": disease
        }

    # ------------------------------------------------------------------
    # Content generation
    # ------------------------------------------------------------------

    def _generate_guidelines(self, treatment: str, disease: str) -> Optional[Dict[str, Any]]:
        """
        Generate all clinical guidelines content using LangChain + Gemini AI.

        Falls back to individually generated sections if the unified chain fails.

        Args:
            treatment: Sanitized treatment name.
            disease: Sanitized disease name.

        Returns:
            Dict with all required clinical guidelines fields, or None on failure.
        """
        logger.info(f"Generating clinical guidelines for {treatment} / {disease}")

        # --- Attempt unified LangChain generation ---
        if self.guidelines_chain:
            result = self._generate_with_langchain(treatment, disease)
            if result:
                result = self._apply_safety_guardrails(result)
                result["generated_at"] = datetime.utcnow().isoformat()
                result["generated_by"] = "langchain_gemini_ai"
                return result

        # --- Fallback: generate each section individually ---
        logger.warning("Unified chain unavailable, falling back to individual section generation")
        return self._generate_sections_individually(treatment, disease)

    def _generate_with_langchain(self, treatment: str, disease: str) -> Optional[Dict[str, Any]]:
        """
        Invoke the unified LangChain chain and parse the JSON response.

        Args:
            treatment: Treatment name.
            disease: Disease name.

        Returns:
            Parsed dict or None if generation/parsing fails.
        """
        try:
            result = self.execute_with_circuit_breaker(
                lambda: self.execute_chain(self.guidelines_chain, {
                    "treatment": treatment,
                    "disease": disease
                })
            )

            if not result:
                return None

            import json
            # Strip markdown code fences if present
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()

            parsed = json.loads(result)

            # Ensure all required fields are present
            required = [
                "treatment_details", "disease_protocols", "research_evidence",
                "clinical_recommendations", "contraindications", "sources", "disclaimer"
            ]
            if not all(field in parsed for field in required):
                logger.warning("LangChain response missing required fields")
                return None

            # Ensure dosage_guidelines key exists (optional field)
            parsed.setdefault("dosage_guidelines", "")

            return parsed

        except Exception as e:
            logger.error(f"LangChain generation failed: {e}")
            return None

    def _generate_sections_individually(self, treatment: str, disease: str) -> Optional[Dict[str, Any]]:
        """
        Generate each content section using dedicated LangChain chains.

        Used as a fallback when the unified chain is unavailable or fails.

        Args:
            treatment: Treatment name.
            disease: Disease name.

        Returns:
            Dict with all required fields, or None if all generation fails.
        """
        try:
            data: Dict[str, Any] = {
                "treatment_details": self._generate_treatment_details(treatment, disease),
                "disease_protocols": self._generate_disease_protocols(treatment, disease),
                "research_evidence": self._generate_research_evidence(treatment, disease),
                "clinical_recommendations": self._generate_clinical_recommendations(treatment, disease),
                "dosage_guidelines": self._generate_dosage_guidelines(treatment, disease),
                "contraindications": self._generate_contraindications(treatment, disease),
                "sources": self._collect_sources(treatment, disease),
                "disclaimer": self._get_medical_disclaimer(),
            }

            # Verify we have at least the core required fields
            required = [
                "treatment_details", "disease_protocols", "research_evidence",
                "clinical_recommendations", "contraindications"
            ]
            if not all(data.get(f) for f in required):
                logger.error("Individual section generation produced incomplete data")
                return None

            return self._apply_safety_guardrails(data)

        except Exception as e:
            logger.error(f"Individual section generation failed: {e}")
            return None

    # ------------------------------------------------------------------
    # Individual section generators
    # ------------------------------------------------------------------

    def _generate_treatment_details(self, treatment: str, disease: str) -> str:
        """Generate treatment mechanism and details. Requirements: 3.2"""
        chain = self.create_agent_chain(
            system_prompt="You are a clinical pharmacologist. Provide concise, evidence-based treatment information.",
            human_prompt="Describe the mechanism of action, pharmacology, and clinical use of {treatment} for {disease}. Be concise and evidence-based."
        )
        result = self.execute_chain(chain, {"treatment": treatment, "disease": disease})
        return self.apply_safety_guardrails(result) if result else f"Treatment details for {treatment} in {disease} management."

    def _generate_disease_protocols(self, treatment: str, disease: str) -> str:
        """Generate disease-specific protocols. Requirements: 3.3"""
        chain = self.create_agent_chain(
            system_prompt="You are a clinical specialist. Provide disease-specific treatment protocols.",
            human_prompt="Describe the disease-specific protocols and standard of care for using {treatment} in {disease}."
        )
        result = self.execute_chain(chain, {"treatment": treatment, "disease": disease})
        return self.apply_safety_guardrails(result) if result else f"Standard protocols for {treatment} in {disease}."

    def _generate_research_evidence(self, treatment: str, disease: str) -> str:
        """Generate research evidence summary. Requirements: 3.4"""
        # Attempt web search for current evidence
        search_results = self.search_web(
            f"{treatment} {disease} clinical trial evidence research",
            filters={"source_types": ["medical_literature", "clinical_guidelines"]}
        )

        web_context = ""
        if search_results:
            web_context = "\n\nRecent research context:\n" + "\n".join(
                f"- {r.get('snippet', '')}" for r in search_results[:3]
            )

        chain = self.create_agent_chain(
            system_prompt="You are a medical researcher. Summarise clinical evidence concisely.",
            human_prompt=f"Summarise the research evidence and clinical trials for {{treatment}} in {{disease}}.{web_context}"
        )
        result = self.execute_chain(chain, {"treatment": treatment, "disease": disease})
        return self.apply_safety_guardrails(result) if result else f"Research evidence for {treatment} in {disease}."

    def _generate_clinical_recommendations(self, treatment: str, disease: str) -> str:
        """Generate clinical recommendations. Requirements: 3.5"""
        chain = self.create_agent_chain(
            system_prompt="You are a clinical guidelines expert. Provide practitioner-focused recommendations.",
            human_prompt="Provide clinical recommendations for healthcare practitioners using {treatment} for {disease}."
        )
        result = self.execute_chain(chain, {"treatment": treatment, "disease": disease})
        return self.apply_safety_guardrails(result) if result else f"Clinical recommendations for {treatment} in {disease}."

    def _generate_dosage_guidelines(self, treatment: str, disease: str) -> str:
        """Generate dosage guidelines when applicable. Requirements: 3.6"""
        chain = self.create_agent_chain(
            system_prompt="You are a clinical pharmacist. Provide dosage information when applicable.",
            human_prompt="Provide dosage guidelines, administration routes, and monitoring parameters for {treatment} in {disease}. Return an empty string if dosage information is not applicable."
        )
        result = self.execute_chain(chain, {"treatment": treatment, "disease": disease})
        if result:
            cleaned = result.strip()
            return self.apply_safety_guardrails(cleaned) if cleaned else ""
        return ""

    def _generate_contraindications(self, treatment: str, disease: str) -> str:
        """Generate contraindications and warnings. Requirements: 3.7"""
        chain = self.create_agent_chain(
            system_prompt="You are a clinical safety specialist. Provide comprehensive contraindication information.",
            human_prompt="List the contraindications, drug interactions, warnings, and precautions for {treatment} in {disease}."
        )
        result = self.execute_chain(chain, {"treatment": treatment, "disease": disease})
        return self.apply_safety_guardrails(result) if result else f"Consult prescribing information for {treatment} contraindications."

    def _collect_sources(self, treatment: str, disease: str) -> List[str]:
        """Collect source citations from web search results."""
        search_results = self.search_web(
            f"{treatment} {disease} clinical guidelines",
            filters={"source_types": ["medical_literature", "clinical_guidelines"]}
        )
        sources = [
            r.get("title", r.get("url", "Medical reference"))
            for r in search_results[:5]
            if r.get("title") or r.get("url")
        ]
        return sources if sources else [
            "Clinical pharmacology references",
            "Current medical literature",
            "Established clinical guidelines"
        ]

    # ------------------------------------------------------------------
    # Safety and disclaimer
    # ------------------------------------------------------------------

    def _apply_safety_guardrails(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply safety guardrails to all text fields in the guidelines data.

        For professional clinical content we apply content filtering (diagnosis
        language softening, dosage pattern removal) without appending patient-
        facing disclaimers to every individual field — the top-level disclaimer
        field covers that requirement.

        Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7

        Args:
            data: Raw guidelines dict.

        Returns:
            Dict with safety guardrails applied to all string fields.
        """
        text_fields = [
            "treatment_details", "disease_protocols", "research_evidence",
            "clinical_recommendations", "dosage_guidelines", "contraindications"
        ]
        for field in text_fields:
            value = data.get(field)
            if value and isinstance(value, str):
                # Apply content filtering only (no per-field disclaimer injection)
                filtered = self.safety_guardrails.prevent_diagnosis(value)
                filtered = self.safety_guardrails.prevent_dosage_recommendation(filtered)
                data[field] = filtered
                self.safety_guardrails._log_intervention(
                    "field_guardrails_applied", f"field={field}"
                )

        # Ensure disclaimer is always present and non-empty
        if not data.get("disclaimer"):
            data["disclaimer"] = self._get_medical_disclaimer()

        # Ensure sources is always a list
        if not isinstance(data.get("sources"), list):
            data["sources"] = [data["sources"]] if data.get("sources") else []

        return data

    def _get_medical_disclaimer(self) -> str:
        """Return the standard medical disclaimer. Requirements: 3.4, 3.7"""
        return (
            "MEDICAL DISCLAIMER: This information is intended for qualified healthcare "
            "professionals only and is provided for educational purposes. It does not "
            "constitute medical advice and should not replace clinical judgement or "
            "consultation with appropriate specialists. Always refer to current clinical "
            "guidelines, the patient's individual circumstances, and up-to-date prescribing "
            "information before making treatment decisions. The authors accept no liability "
            "for clinical decisions made based on this information."
        )
