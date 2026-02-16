"""
Unified Agents for AI Health Intelligence System

This file consolidates all agent logic from the backend/agents directory into a single file.
This structural change aims to simplify the agent architecture and rectify potential import circularities
or dependency issues.

Included Agents:
1. BaseHealthAgent
2. TreatmentExplorationAgent
3. DataExtractionAgent
4. LangChainValidationAgent
5. LangChainExplanationAgent
6. LifestyleModificationAgent
7. ReflectionAgent
8. RecommendationAgent
9. OrchestratorAgent

Corrected Imports and Structure:
- All external imports are adjusted to reference the 'backend' package if needed.
- Internal 'agents.' imports are removed as all classes are now in this file.
"""

import os
import sys
import logging
import json
import re
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

# Django setup might be needed if run standalone, but if imported from Django, settings are already there.
# Ensure 'backend' is in path if not already.
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'backend')
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# External Libraries
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Backend Imports
try:
    from backend.common.gemini_client import LangChainGeminiClient
    from backend.treatment.knowledge_base import TreatmentKnowledgeBase
except ImportError:
    # Fallback if running from a different context
    try:
        from common.gemini_client import LangChainGeminiClient
        from treatment.knowledge_base import TreatmentKnowledgeBase
    except ImportError as e:
        print(f"Warning: Could not import backend modules: {e}")
        # Mock for syntax check if needed, or fail.
        pass

# Initialize Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('health_ai.agents')

# =================================================================================================
# 1. Base Health Agent
# =================================================================================================

class BaseHealthAgent(ABC):
    """
    Base class for all health intelligence agents using LangChain.
    
    Provides common functionality:
    - LangChain integration
    - Gemini LLM access
    - Logging and error handling
    - Agent state management
    """
    
    def __init__(self, agent_name: str):
        """
        Initialize the base agent.
        
        Args:
            agent_name: Name of the agent for logging and identification
        """
        self.agent_name = agent_name
        self.gemini_client = LangChainGeminiClient()
        self.llm = self.gemini_client.llm
        self.agent_state = {
            "initialized_at": datetime.utcnow().isoformat(),
            "agent_name": agent_name,
            "status": "active"
        }
        
        logger.info(f"{agent_name} agent initialized with LangChain")
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for the agent.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            Processed result dictionary
        """
        pass
    
    def create_agent_chain(self, system_prompt: str, human_prompt: str) -> Any:
        """
        Create a LangChain processing chain for the agent.
        
        Args:
            system_prompt: System prompt template
            human_prompt: Human prompt template
            
        Returns:
            LangChain chain or None if LLM unavailable
        """
        if not self.llm:
            logger.warning(f"{self.agent_name} agent: LLM not available, using fallback")
            return None
        
        try:
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", human_prompt)
            ])
            
            chain = prompt_template | self.llm | StrOutputParser()
            return chain
            
        except Exception as e:
            logger.error(f"{self.agent_name} agent: Error creating chain - {str(e)}")
            return None
    
    def execute_chain(self, chain: Any, input_data: Dict[str, Any]) -> Optional[str]:
        """
        Execute a LangChain chain with error handling.
        
        Args:
            chain: LangChain chain to execute
            input_data: Input data for the chain
            
        Returns:
            Chain output or None if failed
        """
        if not chain:
            return None
        
        try:
            result = chain.invoke(input_data)
            logger.info(f"{self.agent_name} agent: Chain executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"{self.agent_name} agent: Chain execution failed - {str(e)}")
            return None
    
    def get_fallback_response(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get fallback response when LLM is unavailable.
        
        Args:
            input_data: Original input data
            
        Returns:
            Fallback response dictionary
        """
        return {
            "success": False,
            "agent": self.agent_name,
            "message": f"{self.agent_name} agent fallback response",
            "fallback_used": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def log_agent_action(self, action: str, details: Dict[str, Any] = None):
        """
        Log agent actions for monitoring and debugging.
        
        Args:
            action: Action being performed
            details: Additional details about the action
        """
        log_data = {
            "agent": self.agent_name,
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if details:
            log_data.update(details)
        
        logger.info(f"{self.agent_name} agent action: {action}")
        if details:
            logger.debug(f"{self.agent_name} agent details: {details}")
    
    def update_agent_state(self, updates: Dict[str, Any]):
        """
        Update agent state with new information.
        
        Args:
            updates: State updates to apply
        """
        self.agent_state.update(updates)
        self.agent_state["last_updated"] = datetime.utcnow().isoformat()
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get current agent status and capabilities.
        
        Returns:
            Agent status dictionary
        """
        return {
            "agent_name": self.agent_name,
            "state": self.agent_state,
            "llm_available": bool(self.llm),
            "gemini_status": self.gemini_client.get_client_status(),
            "framework": "LangChain"
        }
    
    def validate_input(self, input_data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """
        Validate input data for required fields.
        
        Args:
            input_data: Input data to validate
            required_fields: List of required field names
            
        Returns:
            Validation result dictionary
        """
        missing_fields = [field for field in required_fields if field not in input_data]
        
        if missing_fields:
            return {
                "valid": False,
                "missing_fields": missing_fields,
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }
        
        return {"valid": True}
    
    def format_agent_response(self, success: bool, data: Any = None, 
                            message: str = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Format standardized agent response.
        
        Args:
            success: Whether the operation was successful
            data: Response data
            message: Response message
            metadata: Additional metadata
            
        Returns:
            Formatted response dictionary
        """
        response = {
            "success": success,
            "agent": self.agent_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if data is not None:
            response["data"] = data
        
        if message:
            response["message"] = message
        
        if metadata:
            response["metadata"] = metadata
        
        return response

# =================================================================================================
# 2. Treatment Exploration Agent
# =================================================================================================

# Cache service import adapted for unified file
try:
    from backend.common.cache_service import CacheService
    CACHE_ENABLED = True
except ImportError:
    try:
        from common.cache_service import CacheService
        CACHE_ENABLED = True
    except ImportError:
        CACHE_ENABLED = False
        # logger is already defined globally in unified_agents, but specific logger is preferred
        pass

# We can reuse the global logger or define a specific one.
# Use a specific logger name to avoid conflict with BaseHealthAgent's 'logger' usage if any
logger_treatment = logging.getLogger('health_ai.treatment_exploration')

class TreatmentExplorationAgent(BaseHealthAgent):
    """
    AI agent for exploring detailed treatment options across medical systems.
    
    Provides comprehensive information about:
    - Treatment mechanisms (how they work)
    - Effectiveness and evidence levels
    - Side effects and safety
    - Contraindications
    - Treatment combinations
    - Expected outcomes
    """
    
    def __init__(self):
        """Initialize the treatment exploration agent."""
        super().__init__("TreatmentExplorationAgent")
        
        # Initialize base knowledge
        self.treatment_kb = TreatmentKnowledgeBase()
        
        # Initialize detailed treatment databases
        self._initialize_detailed_treatments()
        
        logger_treatment.info("TreatmentExplorationAgent initialized")
    
    def _initialize_detailed_treatments(self):
        """Initialize comprehensive treatment details for each disease and system."""
        
        self.detailed_treatments = {
            "diabetes": {
                "allopathy": {
                    "system_name": "Allopathy (Modern/English Medicine)",
                    "primary_goal": "Blood sugar control and prevention of complications",
                    "treatments": [
                        {
                            "name": "Metformin",
                            "category": "Oral Medication - First Line",
                            "mechanism": "Reduces glucose production in the liver and improves insulin sensitivity in muscles",
                            "effectiveness": "High - Reduces HbA1c by 1-2% on average",
                            "evidence_level": "Very High - Extensively studied, decades of clinical use",
                            "typical_use": "Long-term, often lifelong management",
                            "administration": "Oral tablet, typically 2-3 times daily with meals",
                            "onset": "Effects begin within days, full benefit in 2-3 months",
                            "benefits": [
                                "Effective blood sugar reduction",
                                "Weight neutral or modest weight loss",
                                "Cardiovascular benefits",
                                "Low risk of hypoglycemia when used alone"
                            ],
                            "side_effects": {
                                "common": ["Nausea", "Diarrhea", "Stomach upset (usually temporary)"],
                                "rare": ["Lactic acidosis (very rare)", "Vitamin B12 deficiency with long-term use"],
                                "management": "Start with low dose, take with food, increase gradually"
                            },
                            "contraindications": [
                                "Severe kidney disease (eGFR < 30)",
                                "Severe liver disease",
                                "Acute heart failure",
                                "Metabolic acidosis",
                                "Alcohol abuse"
                            ],
                            "monitoring": [
                                "Kidney function (eGFR) every 6-12 months",
                                "Vitamin B12 levels annually",
                                "Blood glucose regularly",
                                "HbA1c every 3 months"
                            ],
                            "cost": "Low - Generic available",
                            "availability": "Widely available worldwide"
                        },
                        {
                            "name": "Insulin Therapy",
                            "category": "Injectable Hormone Replacement",
                            "mechanism": "Replaces or supplements natural insulin production",
                            "effectiveness": "Very High - Essential for Type 1, effective for Type 2",
                            "evidence_level": "Very High - Gold standard for many patients",
                            "typical_use": "Essential for Type 1, used in Type 2 when other treatments insufficient",
                            "administration": "Subcutaneous injection, 1-4 times daily depending on type",
                            "onset": "Rapid-acting works in 15 minutes, long-acting provides 24-hour coverage",
                            "benefits": [
                                "Most effective for lowering blood sugar",
                                "Essential for Type 1 diabetes",
                                "Flexible dosing options",
                                "Protects pancreas function"
                            ],
                            "side_effects": {
                                "common": ["Hypoglycemia (low blood sugar)", "Weight gain", "Injection site reactions"],
                                "rare": ["Severe hypoglycemia", "Lipodystrophy"],
                                "management": "Careful dosing, regular monitoring, proper injection technique"
                            },
                            "contraindications": [
                                "Hypoglycemia",
                                "Allergy to insulin (extremely rare)"
                            ],
                            "monitoring": [
                                "Blood glucose monitoring 4-10 times daily",
                                "HbA1c every 3 months",
                                "Hypoglycemia awareness",
                                "Injection site rotation"
                            ],
                            "cost": "Moderate to High - varies by type and country",
                            "availability": "Widely available but cost varies"
                        }
                    ],
                    "lifestyle_component": "Essential - Diet and exercise are foundation",
                    "expected_timeline": "Initial improvement in weeks, full optimization in 3-6 months",
                    "success_rate": "High with adherence - Most patients achieve good control",
                    "disclaimer": "Requires medical supervision. Medication dosages must be prescribed and monitored by qualified physicians. Regular blood glucose monitoring is essential."
                },
                
                "homeopathy": {
                    "system_name": "Homeopathy",
                    "primary_goal": "Constitutional healing and metabolic balance",
                    "approach_philosophy": "Treats individual as a whole, not just disease symptoms",
                    "treatments": [
                        {
                            "name": "Constitutional Remedies",
                            "category": "Individualized Treatment",
                            "mechanism": "Stimulates body's vital force to restore metabolic balance",
                            "selection_basis": "Complete symptom picture including mental, emotional, and physical symptoms",
                            "effectiveness": "Varies by individual - Some report improvement in symptoms and well-being",
                            "evidence_level": "Limited - Few rigorous clinical trials, more anecdotal evidence",
                            "common_remedies": [
                                "Uranium Nitricum - For high blood sugar with weakness",
                                "Syzygium Jambolanum - For excessive thirst and urination",
                                "Phosphoric Acid - For diabetes with weakness and mental fatigue",
                                "Arsenicum Album - For burning sensations and restlessness"
                            ],
                            "typical_use": "Long-term constitutional treatment, remedy changes based on response",
                            "administration": "Oral pills/drops, typically once daily to once weekly depending on potency",
                            "onset": "Gradual - May take weeks to months for full effect",
                            "benefits": [
                                "Holistic approach to health",
                                "No known side effects from properly prescribed remedies",
                                "May improve overall well-being",
                                "Can be used alongside conventional treatment with proper supervision"
                            ],
                            "considerations": [
                                "Highly individualized - requires expert homeopath",
                                "Response varies greatly between individuals",
                                "Not a substitute for insulin in Type 1 diabetes",
                                "Regular blood sugar monitoring still essential"
                            ],
                            "monitoring": [
                                "Blood glucose monitoring must continue",
                                "Regular follow-up with homeopath",
                                "Conventional medical monitoring maintained",
                                "Symptom journaling"
                            ]
                        }
                    ],
                    "integration_notes": "Should complement, not replace conventional monitoring and insulin therapy where needed",
                    "expected_timeline": "Gradual improvement over months, if effective",
                    "success_rate": "Highly variable - depends on individual response",
                    "disclaimer": "Requires qualified homeopathic consultation. NOT a replacement for insulin in Type 1 diabetes. Blood sugar monitoring and conventional medical care remain essential. Inform all healthcare providers about all treatments."
                },
                
                "ayurveda": {
                    "system_name": "Ayurveda (Traditional Indian Medicine)",
                    "primary_goal": "Restore dosha balance and improve metabolic fire (Agni)",
                    "approach_philosophy": "Diabetes seen as imbalance of Kapha dosha affecting metabolism",
                    "treatments": [
                        {
                            "name": "Gymnema Sylvestre (Gurmar)",
                            "category": "Herbal Medicine",
                            "mechanism": "May reduce sugar absorption in intestines, potentially stimulates insulin production",
                            "traditional_use": "Called 'sugar destroyer' in Hindi, used for centuries",
                            "effectiveness": "Moderate - Some clinical studies show blood sugar reduction",
                            "evidence_level": "Moderate - Several clinical trials with promising results",
                            "typical_use": "Daily supplement, 3-6 months minimum",
                            "administration": "Capsules, powder, or tea - 400-600mg daily",
                            "onset": "Gradual - 2-4 weeks to see effects",
                            "benefits": [
                                "May help reduce blood sugar levels",
                                "May help reduce sugar cravings",
                                "Generally well tolerated",
                                "Natural supplement option"
                            ],
                            "side_effects": {
                                "common": ["May cause hypoglycemia if combined with diabetes medications"],
                                "rare": ["Gastrointestinal upset", "Allergic reactions"],
                                "precautions": "Start with low dose, monitor blood sugar closely"
                            },
                            "contraindications": [
                                "Already on diabetes medications without doctor supervision",
                                "Surgery scheduled within 2 weeks",
                                "Hypoglycemia tendency"
                            ],
                            "interactions": [
                                "May enhance effects of diabetes medications",
                                "Could interfere with blood sugar control during surgery"
                            ],
                            "monitoring": [
                                "Frequent blood glucose monitoring",
                                "May need reduction in conventional medication doses",
                                "Regular consultation with both Ayurvedic and conventional practitioners"
                            ],
                            "cost": "Low to Moderate",
                            "availability": "Widely available as supplement"
                        },
                        {
                            "name": "Bitter Melon (Karela)",
                            "category": "Herbal Medicine / Dietary",
                            "mechanism": "Contains compounds that act similar to insulin",
                            "traditional_use": "Consumed as vegetable or juice in traditional diets",
                            "effectiveness": "Moderate - Some studies show blood sugar lowering effects",
                            "evidence_level": "Moderate - Multiple studies but results vary",
                            "administration": "Fresh juice, cooked vegetable, or capsule supplements",
                            "benefits": [
                                "Natural food-based approach",
                                "May help lower blood sugar",
                                "Rich in nutrients",
                                "Can be part of regular diet"
                            ],
                            "precautions": [
                                "Monitor blood sugar - can cause hypoglycemia",
                                "Start with small amounts",
                                "Bitter taste may be unpleasant for some"
                            ]
                        },
                        {
                            "name": "Fenugreek (Methi)",
                            "category": "Herbal Seed",
                            "mechanism": "Slows carbohydrate absorption, may improve insulin sensitivity",
                            "evidence_level": "Moderate - Several positive clinical trials",
                            "administration": "Seeds soaked overnight and consumed, or powder/capsules",
                            "benefits": [
                                "May lower fasting blood sugar",
                                "May improve cholesterol levels",
                                "Rich in soluble fiber"
                            ]
                        }
                    ],
                    "complementary_practices": {
                        "yoga": [
                            "Specific asanas for pancreatic stimulation",
                            "Surya Namaskar (Sun Salutations)",
                            "Paschimottanasana (Seated Forward Bend)",
                            "Dhanurasana (Bow Pose)"
                        ],
                        "pranayama": [
                            "Kapalbhati (Skull Shining Breath)",
                            "Anulom Vilom (Alternate Nostril Breathing)",
                            "Deep abdominal breathing"
                        ],
                        "diet": [
                            "Avoid excessive sweets and heavy, oily foods",
                            "Include bitter vegetables",
                            "Follow regular meal times",
                            "Prefer whole grains over refined"
                        ]
                    },
                    "expected_timeline": "3-6 months for noticeable effects",
                    "success_rate": "Variable - works better for some individuals",
                    "disclaimer": "Consult qualified Ayurvedic practitioners. Should complement, not replace, conventional blood glucose monitoring and insulin therapy where needed. Inform all healthcare providers about all herbs and supplements."
                },
                
                "integrative": {
                    "system_name": "Integrative Medicine",
                    "approach": "Combines best of multiple systems under coordinated care",
                    "protocols": [
                        {
                            "name": "Comprehensive Diabetes Management",
                            "combines": ["Allopathy", "Ayurveda", "Lifestyle"],
                            "components": {
                                "conventional": "Metformin or insulin as prescribed by physician",
                                "herbal": "Gymnema or fenugreek under supervision",
                                "diet": "Low glycemic diet with bitter vegetables",
                                "exercise": "Regular aerobic and resistance training",
                                "mind_body": "Yoga and stress management"
                            },
                            "coordination": "Requires team including endocrinologist, Ayurvedic practitioner, nutritionist",
                            "benefits": [
                                "Addresses disease from multiple angles",
                                "May allow lower medication doses over time",
                                "Improved overall well-being",
                                "Better long-term outcomes"
                            ],
                            "critical_requirements": [
                                "All practitioners must be informed of all treatments",
                                "More frequent blood glucose monitoring",
                                "Regular communication between healthcare team",
                                "Medication adjustments as herbs take effect"
                            ],
                            "evidence": "Growing - integrative approaches gaining clinical support",
                            "success_factors": [
                                "Patient commitment to all aspects",
                                "Good communication between providers",
                                "Regular monitoring and adjustment",
                                "Individualized approach"
                            ]
                        }
                    ],
                    "safety_emphasis": "Integration must be supervised. Never reduce conventional medications without medical guidance.",
                    "disclaimer": "Integrative approach requires coordinated care team. All practitioners must know about all treatments. Self-directed integration can be dangerous."
                }
            },
            
            # Add other diseases...
            "hypertension": {
                "allopathy": {
                    "system_name": "Allopathy (Modern/English Medicine)",
                    "primary_goal": "Blood pressure control and prevention of cardiovascular complications",
                    "treatments": [
                        {
                            "name": "ACE Inhibitors (e.g., Lisinopril, Enalapril)",
                            "category": "Oral Medication - First Line",
                            "mechanism": "Blocks enzyme that narrows blood vessels, allowing vessels to relax and widen",
                            "effectiveness": "High - Reduces systolic BP by 10-15 mmHg on average",
                            "evidence_level": "Very High - Extensively studied, proven cardiovascular protection",
                            "typical_use": "Long-term, often lifelong management",
                            "administration": "Oral tablet, once daily",
                            "onset": "Full effect in 2-4 weeks",
                            "benefits": [
                                "Effective blood pressure reduction",
                                "Protects kidneys (especially in diabetes)",
                                "Reduces heart failure risk",
                                "Once-daily dosing"
                            ],
                            "side_effects": {
                                "common": ["Dry cough (10-20% of patients)", "Dizziness", "Fatigue"],
                                "rare": ["Angioedema (swelling)", "Elevated potassium", "Kidney function changes"],
                                "management": "Monitor potassium, kidney function. Switch to ARB if cough troublesome"
                            },
                            "contraindications": [
                                "Pregnancy or planning pregnancy",
                                "History of angioedema",
                                "Bilateral renal artery stenosis",
                                "Severe kidney disease"
                            ],
                            "monitoring": [
                                "Blood pressure regularly",
                                "Kidney function and potassium within 1-2 weeks, then periodically",
                                "Regular follow-up visits"
                            ],
                            "cost": "Low - Generics widely available",
                            "availability": "Widely available worldwide"
                        },
                        {
                            "name": "Calcium Channel Blockers (e.g., Amlodipine)",
                            "category": "Oral Medication",
                            "mechanism": "Relaxes blood vessels by blocking calcium entry into vessel wall cells",
                            "effectiveness": "High - Reduces systolic BP by 10-15 mmHg",
                            "evidence_level": "Very High - Well-studied, proven effective",
                            "administration": "Oral tablet, once daily",
                            "onset": "Full effect in 1-2 weeks",
                            "benefits": [
                                "Effective BP reduction",
                                "No dry cough (unlike ACE inhibitors)",
                                "Safe in kidney disease",
                                "Once-daily dosing"
                            ],
                            "side_effects": {
                                "common": ["Ankle swelling", "Flushing", "Headache"],
                                "rare": ["Gum overgrowth", "Rapid heart rate"],
                                "management": "Leg elevation for swelling, dose adjustment if needed"
                            },
                            "contraindications": [
                                "Severe heart failure",
                                "Severe aortic stenosis"
                            ],
                            "monitoring": [
                                "Blood pressure regularly",
                                "Heart rate",
                                "Watch for ankle swelling"
                            ],
                            "cost": "Low - Generic available",
                            "availability": "Widely available"
                        },
                        {
                            "name": "Diuretics (e.g., Hydrochlorothiazide)",
                            "category": "Oral Medication - Water Pill",
                            "mechanism": "Helps kidneys remove excess salt and water, reducing blood volume",
                            "effectiveness": "Moderate to High - Reduces systolic BP by 8-12 mmHg",
                            "evidence_level": "Very High - Long history of use, proven benefit",
                            "administration": "Oral tablet, once daily (morning preferred)",
                            "benefits": [
                                "Effective, especially in elderly",
                                "Reduces heart failure risk",
                                "Inexpensive",
                                "Works well in combination"
                            ],
                            "side_effects": {
                                "common": ["Increased urination", "Low potassium", "Increased urination"],
                                "rare": ["Gout attacks", "Low sodium", "Blood sugar elevation"],
                                "management": "Potassium monitoring, take in morning to avoid nighttime urination"
                            },
                            "contraindications": [
                                "Severe kidney disease",
                                "Gout (relative contraindication)"
                            ],
                            "monitoring": [
                                "Blood pressure",
                                "Potassium and sodium levels",
                                "Kidney function",
                                "Uric acid (if gout history)"
                            ]
                        }
                    ],
                    "lifestyle_component": "Essential - DASH diet, exercise, weight loss, sodium restriction",
                    "expected_timeline": "Initial BP reduction in 1-4 weeks, full optimization in 2-3 months",
                    "success_rate": "High with adherence - Most patients achieve target BP with 1-2 medications",
                    "disclaimer": "Requires medical supervision. Never stop medications abruptly. Regular BP monitoring essential."
                },
                
                "homeopathy": {
                    "system_name": "Homeopathy",
                    "primary_goal": "Constitutional balance and stress reduction",
                    "approach_philosophy": "Treats individual constitution, not just elevated numbers",
                    "treatments": [
                        {
                            "name": "Constitutional Remedies",
                            "category": "Individualized Treatment",
                            "mechanism": "Stimulates body's self-regulating mechanisms",
                            "effectiveness": "Varies by individual - Some report BP improvements",
                            "evidence_level": "Limited - Few rigorous trials, mixed results",
                            "common_remedies": [
                                "Rauwolfia Serpentina - For high BP with headaches",
                                "Nux Vomica - For stress-related hypertension",
                                "Argentum Nitricum - For anxiety-related BP elevation",
                                "Lachesis - For BP issues during menopause",
                                "Natrum Muriaticum - For BP with fluid retention"
                            ],
                            "administration": "Pills/drops, frequency based on potency",
                            "onset": "Gradual - May take weeks to months",
                            "benefits": [
                                "Holistic approach",
                                "No known side effects from properly prescribed remedies",
                                "Addresses stress and emotional factors",
                                "Can complement conventional treatment"
                            ],
                            "considerations": [
                                "Highly individualized",
                                "Regular BP monitoring still essential",
                                "Not a substitute for emergency hypertension treatment",
                                "Works best for mild to moderate cases"
                            ],
                            "monitoring": [
                                "Regular BP monitoring at home and with doctor",
                                "Symptom tracking",
                                "Conventional medical monitoring maintained"
                            ]
                        }
                    ],
                    "integration_notes": "Should complement, not replace BP monitoring and conventional medications when needed",
                    "expected_timeline": "Gradual improvement over months if effective",
                    "success_rate": "Highly variable",
                    "disclaimer": "Requires qualified homeopathic consultation. NOT a replacement for blood pressure medications in moderate to severe hypertension. Regular BP monitoring essential."
                },
                
                "ayurveda": {
                    "system_name": "Ayurveda (Traditional Indian Medicine)",
                    "primary_goal": "Balance Vata and Pitta doshas, reduce stress",
                    "approach_philosophy": "Hypertension as imbalance of Vata (nerve stress) and Pitta (heat)",
                    "treatments": [
                        {
                            "name": "Ashwagandha (Withania Somnifera)",
                            "category": "Adaptogenic Herb",
                            "mechanism": "Reduces stress hormones, may improve vascular function",
                            "traditional_use": "Used for centuries for stress and vitality",
                            "effectiveness": "Moderate - Some studies show modest BP reduction",
                            "evidence_level": "Moderate - Several clinical trials with positive results",
                            "administration": "Powder or capsules, 300-600mg daily",
                            "onset": "2-4 weeks for stress benefits, longer for BP",
                            "benefits": [
                                "Reduces stress and cortisol",
                                "May help with stress-related BP elevation",
                                "Improves sleep quality",
                                "Generally well tolerated"
                            ],
                            "side_effects": {
                                "common": ["Mild GI upset if taken on empty stomach"],
                                "rare": ["Excessive sedation at high doses"],
                                "precautions": "Take with food initially"
                            },
                            "contraindications": [
                                "Pregnancy",
                                "Autoimmune conditions (consult practitioner)",
                                "Before surgery (may enhance sedation)"
                            ]
                        },
                        {
                            "name": "Arjuna (Terminalia Arjuna)",
                            "category": "Cardiovascular Herb",
                            "mechanism": "May improve heart function and vascular tone",
                            "traditional_use": "Traditional cardiac tonic in Ayurveda",
                            "effectiveness": "Moderate - Some evidence for BP and heart health",
                            "evidence_level": "Moderate - Several positive studies",
                            "administration": "Powder or capsules, 500mg 2-3 times daily",
                            "benefits": [
                                "May support healthy blood pressure",
                                "Traditional cardiac tonic",
                                "May improve cholesterol levels",
                                "Antioxidant properties"
                            ],
                            "precautions": [
                                "Monitor BP if combining with medications",
                                "May enhance effects of heart medications"
                            ]
                        },
                        {
                            "name": "Garlic (Allium Sativum)",
                            "category": "Dietary/Herbal",
                            "mechanism": "Relaxes blood vessels, may reduce arterial stiffness",
                            "evidence_level": "Moderate - Multiple studies show modest BP reduction",
                            "administration": "Fresh garlic or aged garlic extract supplements",
                            "benefits": [
                                "May reduce systolic BP by 5-10 mmHg",
                                "Cardiovascular benefits",
                                "Can be part of diet"
                            ],
                            "precautions": [
                                "May increase bleeding risk",
                                "Stop before surgery"
                            ]
                        }
                    ],
                    "complementary_practices": {
                        "yoga": [
                            "Gentle poses (avoid inversions initially)",
                            "Shavasana (Corpse Pose) for relaxation",
                            "Viparita Karani (Legs-Up-Wall)",
                            "Gentle forward bends"
                        ],
                        "pranayama": [
                            "Anulom Vilom (Alternate Nostril Breathing)",
                            "Bhramari (Bee Breath) for calming",
                            "Deep slow breathing",
                            "Avoid forceful techniques like Kapalbhati"
                        ],
                        "diet": [
                            "Cooling foods (cucumber, coconut water)",
                            "Reduce salt and spicy foods",
                            "Include celery, pomegranate",
                            "Reduce caffeine and alcohol"
                        ],
                        "lifestyle": [
                            "Regular sleep schedule",
                            "Stress management",
                            "Oil massage (Abhyanga) for relaxation",
                            "Avoid excessive heat"
                        ]
                    },
                    "expected_timeline": "2-3 months for noticeable effects",
                    "success_rate": "Variable - works better for mild hypertension and stress-related BP",
                    "disclaimer": "Consult qualified Ayurvedic practitioners. Should complement, not replace BP monitoring and medications when needed. Inform all healthcare providers about herbs."
                },
                
                "integrative": {
                    "system_name": "Integrative Medicine",
                    "approach": "Combines conventional medicine with lifestyle and complementary approaches",
                    "protocols": [
                        {
                            "name": "Comprehensive Hypertension Management",
                            "combines": ["Allopathy", "Lifestyle", "Ayurveda/Herbs"],
                            "components": {
                                "conventional": "BP medication as prescribed (ACE inhibitor or CCB)",
                                "diet": "DASH diet - rich in fruits, vegetables, low-fat dairy",
                                "exercise": "Regular aerobic exercise 150 min/week",
                                "stress": "Meditation, yoga, or mindfulness practice",
                                "supplements": "Garlic or Ashwagandha under supervision",
                                "monitoring": "Home BP monitoring daily"
                            },
                            "coordination": "Team including physician, dietitian, yoga instructor",
                            "benefits": [
                                "Addresses BP from multiple angles",
                                "May allow lower medication doses",
                                "Improves overall cardiovascular health",
                                "Better stress management"
                            ],
                            "critical_requirements": [
                                "All practitioners informed of all treatments",
                                "Regular BP monitoring at home",
                                "Medication adjustments as lifestyle changes take effect",
                                "Never reduce medications without doctor approval"
                            ],
                            "evidence": "Strong - lifestyle modifications proven to reduce BP",
                            "expected_results": [
                                "DASH diet: 8-14 mmHg reduction",
                                "Weight loss: 5-20 mmHg per 10kg lost",
                                "Exercise: 4-9 mmHg reduction",
                                "Reduced sodium: 2-8 mmHg reduction"
                            ]
                        }
                    ],
                    "safety_emphasis": "Lifestyle changes enhance medication effectiveness. Never stop BP medications without medical supervision.",
                    "disclaimer": "Integrative approach requires coordinated care. All practitioners must know about all treatments. Regular BP monitoring essential."
                }
            },
            
            "heart_disease": {
                "allopathy": {
                    "system_name": "Allopathy (Modern/English Medicine)",
                    "primary_goal": "Reduce cardiovascular risk, prevent heart attack and stroke",
                    "treatments": [
                        {
                            "name": "Statins (e.g., Atorvastatin, Rosuvastatin)",
                            "category": "Cholesterol-Lowering Medication",
                            "mechanism": "Blocks cholesterol production in liver, reduces LDL (bad) cholesterol",
                            "effectiveness": "Very High - Reduces LDL by 30-50%, reduces heart attack/stroke risk by 25-35%",
                            "evidence_level": "Very High - Decades of research, massive clinical trials",
                            "typical_use": "Long-term, often lifelong",
                            "administration": "Oral tablet, once daily (usually evening)",
                            "onset": "Cholesterol effects in 2 weeks, full cardiovascular protection over months-years",
                            "benefits": [
                                "Powerful LDL cholesterol reduction",
                                "Proven reduction in heart attack and stroke",
                                "Stabilizes arterial plaques",
                                "Anti-inflammatory effects on blood vessels"
                            ],
                            "side_effects": {
                                "common": ["Muscle aches (5-10%)", "Mild liver enzyme elevation"],
                                "rare": ["Severe muscle breakdown (rhabdomyolysis - very rare)", "Diabetes risk (small increase)", "Memory issues (controversial)"],
                                "management": "Report muscle pain immediately, regular monitoring, CoQ10 may help muscle symptoms"
                            },
                            "contraindications": [
                                "Active liver disease",
                                "Pregnancy and breastfeeding",
                                "Allergy to statins"
                            ],
                            "monitoring": [
                                "Liver function tests before starting and periodically",
                                "Lipid panel every 3-12 months",
                                "Monitor for muscle symptoms",
                                "Kidney function periodically"
                            ],
                            "cost": "Low - Generics widely available",
                            "availability": "Widely available worldwide"
                        },
                        {
                            "name": "Aspirin (Low-Dose Antiplatelet)",
                            "category": "Antiplatelet - Blood Thinner",
                            "mechanism": "Prevents blood platelets from clumping, reduces clot formation",
                            "effectiveness": "High - Reduces heart attack/stroke risk by 20-25% in appropriate patients",
                            "evidence_level": "Very High - Extensively studied",
                            "typical_use": "Daily, long-term (if benefits outweigh bleeding risks)",
                            "administration": "Low-dose tablet (75-100mg) once daily",
                            "onset": "Antiplatelet effect within hours",
                            "benefits": [
                                "Reduces heart attack and stroke in high-risk patients",
                                "Inexpensive",
                                "Well-established safety profile",
                                "Widely available"
                            ],
                            "side_effects": {
                                "common": ["Stomach upset", "Easy bruising"],
                                "rare": ["Stomach bleeding", "Brain hemorrhage (rare but serious)"],
                                "management": "Take with food, report unusual bleeding, consider PPI if stomach issues"
                            },
                            "contraindications": [
                                "Active bleeding",
                                "Severe bleeding disorder",
                                "Aspirin allergy",
                                "Recent hemorrhagic stroke"
                            ],
                            "monitoring": [
                                "Watch for unusual bleeding or bruising",
                                "Monitor blood counts if on long-term",
                                "Regular medical follow-up"
                            ],
                            "cost": "Very Low",
                            "availability": "Over-the-counter, widely available",
                            "important_note": "Decision to use aspirin should be individualized - benefits vs bleeding risks"
                        },
                        {
                            "name": "Beta-Blockers (e.g., Metoprolol, Carvedilol)",
                            "category": "Heart Rate/BP Medication",
                            "mechanism": "Slows heart rate, reduces heart's workload, lowers blood pressure",
                            "effectiveness": "High - Reduces mortality after heart attack by 20-25%",
                            "evidence_level": "Very High - Proven benefit, especially post-heart attack",
                            "typical_use": "Long-term after heart attack or in heart failure",
                            "administration": "Oral tablet, 1-2 times daily",
                            "benefits": [
                                "Protects heart after heart attack",
                                "Reduces heart failure progression",
                                "Controls heart rate and BP",
                                "Reduces chest pain (angina)"
                            ],
                            "side_effects": {
                                "common": ["Fatigue", "Cold hands/feet", "Slower heart rate", "Dizziness"],
                                "rare": ["Worsening asthma", "Depression", "Sexual dysfunction"],
                                "management": "Start low dose, increase gradually, report severe fatigue or breathing issues"
                            },
                            "contraindications": [
                                "Severe asthma or COPD (relative)",
                                "Severe bradycardia (very slow heart)",
                                "Certain heart rhythm problems",
                                "Severe heart failure (for some types)"
                            ],
                            "monitoring": [
                                "Heart rate and blood pressure",
                                "Watch for breathing difficulties",
                                "Regular medical follow-up"
                            ]
                        },
                        {
                            "name": "ACE Inhibitors/ARBs",
                            "category": "Blood Pressure/Heart Protection",
                            "mechanism": "Relaxes blood vessels, reduces heart's workload",
                            "effectiveness": "High - Reduces mortality and hospitalizations in heart failure",
                            "evidence_level": "Very High - Cornerstone of heart failure treatment",
                            "benefits": [
                                "Improves heart function over time",
                                "Reduces hospitalizations",
                                "Protects kidneys",
                                "Lowers blood pressure"
                            ],
                            "reference": "See details in hypertension section"
                        }
                    ],
                    "lifestyle_component": "Critical - Heart-healthy diet, exercise, smoking cessation, stress management",
                    "expected_timeline": "Symptom improvement in weeks, full cardiovascular protection builds over months to years",
                    "success_rate": "Very High - Combination therapy dramatically reduces risk",
                    "disclaimer": "Requires cardiologist supervision. Medication regimen highly individualized. Never stop heart medications without medical guidance."
                },
                
                "homeopathy": {
                    "system_name": "Homeopathy",
                    "primary_goal": "Support cardiovascular health and reduce stress",
                    "approach_philosophy": "Constitutional treatment to support overall heart health",
                    "treatments": [
                        {
                            "name": "Constitutional Remedies",
                            "category": "Individualized Treatment",
                            "mechanism": "Supports body's healing capacity and reduces cardiovascular stress",
                            "effectiveness": "Varies - Some report improved well-being",
                            "evidence_level": "Very Limited - No strong clinical evidence for heart disease",
                            "common_remedies": [
                                "Crataegus (Hawthorn) - Traditional heart tonic",
                                "Cactus Grandiflorus - For constricting chest pain",
                                "Arnica Montana - For heart strain",
                                "Digitalis - For weak, slow pulse",
                                "Aurum Metallicum - For cardiovascular issues with depression"
                            ],
                            "administration": "Pills/drops per homeopath guidance",
                            "benefits": [
                                "May reduce stress and anxiety",
                                "Holistic support",
                                "No known medication interactions when properly prescribed"
                            ],
                            "critical_limitations": [
                                "NOT a substitute for conventional heart medications",
                                "No proven effect on preventing heart attack/stroke",
                                "Should only be complementary to standard care",
                                "Seek emergency care for chest pain regardless"
                            ],
                            "monitoring": [
                                "Continue all conventional monitoring",
                                "Regular cardiologist visits",
                                "Never replace prescribed medications"
                            ]
                        }
                    ],
                    "integration_notes": "Can only be used as gentle complement to conventional care. Never as replacement.",
                    "expected_timeline": "No reliable timeline for cardiovascular outcomes",
                    "success_rate": "Unproven for heart disease outcomes",
                    "disclaimer": "CRITICAL: Homeopathy is NOT a substitute for proven heart medications. Heart disease requires conventional medical care. All chest pain requires emergency evaluation."
                },
                
                "ayurveda": {
                    "system_name": "Ayurveda (Traditional Indian Medicine)",
                    "primary_goal": "Support heart health through herbs and lifestyle",
                    "approach_philosophy": "Heart disease as imbalance affecting circulation and metabolism",
                    "treatments": [
                        {
                            "name": "Arjuna (Terminalia Arjuna)",
                            "category": "Cardiovascular Herb",
                            "mechanism": "May improve heart muscle strength, antioxidant properties",
                            "traditional_use": "Ancient cardiac tonic in Ayurveda, used for centuries",
                            "effectiveness": "Moderate - Some studies suggest benefits for heart function",
                            "evidence_level": "Moderate - Some clinical trials, more research needed",
                            "administration": "Powder or capsules, 500mg 2-3 times daily",
                            "onset": "Gradual - weeks to months",
                            "benefits": [
                                "May improve heart muscle contractility",
                                "Antioxidant and anti-inflammatory",
                                "May help with mild heart failure symptoms",
                                "Traditional safety record"
                            ],
                            "side_effects": {
                                "common": ["Generally well tolerated"],
                                "rare": ["GI upset at high doses"],
                                "precautions": "Use under qualified guidance"
                            },
                            "interactions": [
                                "May enhance blood pressure medications",
                                "Inform cardiologist before use"
                            ],
                            "monitoring": [
                                "Continue all conventional monitoring",
                                "Watch for changes in BP or heart rate",
                                "Regular cardiologist visits maintained"
                            ],
                            "evidence_note": "Some positive studies but not a replacement for proven therapies"
                        },
                        {
                            "name": "Guggul (Commiphora Mukul)",
                            "category": "Lipid-Modulating Herb",
                            "mechanism": "May help lower cholesterol levels",
                            "traditional_use": "Traditional use for lipid management",
                            "effectiveness": "Limited - Mixed research results",
                            "evidence_level": "Low-Moderate - Studies show conflicting results",
                            "benefits": [
                                "Traditional cholesterol support",
                                "Anti-inflammatory properties"
                            ],
                            "precautions": [
                                "Less effective than statins",
                                "Quality varies by preparation",
                                "May interact with thyroid medications"
                            ]
                        },
                        {
                            "name": "Garlic",
                            "category": "Dietary/Herbal",
                            "mechanism": "May reduce cholesterol and blood pressure modestly",
                            "evidence_level": "Moderate - Some cardiovascular benefits shown",
                            "benefits": [
                                "Modest cholesterol reduction",
                                "Blood pressure benefits",
                                "Can be part of heart-healthy diet"
                            ],
                            "precautions": [
                                "May increase bleeding risk",
                                "Stop before surgery",
                                "Inform doctors about use"
                            ]
                        }
                    ],
                    "complementary_practices": {
                        "yoga": [
                            "Gentle, restorative poses",
                            "Avoid strenuous inversions without clearance",
                            "Pranayama (gentle breathing only)",
                            "Meditation for stress reduction"
                        ],
                        "diet": [
                            "Heart-healthy diet (similar to Mediterranean)",
                            "Include fruits, vegetables, whole grains",
                            "Reduce saturated fats",
                            "Include nuts, fatty fish"
                        ],
                        "lifestyle": [
                            "Stress management",
                            "Adequate sleep",
                            "Gentle regular exercise",
                            "Social connections"
                        ]
                    },
                    "expected_timeline": "3-6 months for potential benefits",
                    "success_rate": "Limited as standalone, may complement conventional care",
                    "disclaimer": "CRITICAL: Ayurvedic approaches are complementary only. Proven heart medications (statins, antiplatelet, etc.) are essential. Never replace conventional cardiac care with herbs alone."
                },
                
                "integrative": {
                    "system_name": "Integrative Medicine",
                    "approach": "Evidence-based conventional medicine enhanced by proven lifestyle strategies",
                    "protocols": [
                        {
                            "name": "Comprehensive Cardiac Protection",
                            "combines": ["Allopathy", "Lifestyle", "Stress Management"],
                            "components": {
                                "medications": "Statin + Aspirin/Antiplatelet + BP control as prescribed",
                                "diet": "Mediterranean or DASH diet, rich in vegetables, fruits, fish, nuts",
                                "exercise": "Cardiac rehab program or supervised aerobic exercise",
                                "stress": "Meditation, yoga, cardiac support groups",
                                "monitoring": "Regular BP/cholesterol checks, cardiac follow-up",
                                "supplements": "Omega-3 fish oil (if recommended), CoQ10 for statin side effects"
                            },
                            "coordination": "Cardiologist, dietitian, cardiac rehab team, mental health support",
                            "benefits": [
                                "Maximizes cardiovascular protection",
                                "Addresses disease from all angles",
                                "Improves quality of life",
                                "Proven to reduce events and mortality"
                            ],
                            "critical_requirements": [
                                "Conventional medications are cornerstone - never optional",
                                "All providers informed of all treatments",
                                "Regular cardiac monitoring",
                                "Lifestyle changes enhance but don't replace medications"
                            ],
                            "evidence": "Very Strong - lifestyle + medications superior to either alone",
                            "expected_results": [
                                "Mediterranean diet: 30% reduction in cardiac events",
                                "Cardiac rehab: 25% reduction in mortality",
                                "Smoking cessation: 50% reduction in recurrent events",
                                "Combined approach: Maximum benefit"
                            ]
                        }
                    ],
                    "safety_emphasis": "Heart disease is serious. Proven medications are non-negotiable. Lifestyle and complementary approaches enhance, never replace, conventional care.",
                    "disclaimer": "CRITICAL: Integration in heart disease means conventional medicine PLUS lifestyle, NOT alternative approaches instead of proven therapies. All chest pain is an emergency."
                }
            }
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process treatment exploration request.
        
        Args:
            input_data: Dictionary containing:
                - disease: Disease name
                - confidence: Confidence level
                - systems: Optional list of systems to explore (default: allopathy, homeopathy, ayurveda, integrative)
                
        Returns:
            Detailed treatment information across requested systems
        """
        try:
            disease = input_data.get("disease", "").lower()
            confidence = input_data.get("confidence", "MEDIUM")
            requested_systems = input_data.get("systems", ["allopathy", "homeopathy", "ayurveda", "integrative"])
            
            logger_treatment.info(f"Processing treatment exploration for {disease} with confidence {confidence}")
            
            # Get treatment information for requested systems (with caching)
            treatment_options = {}
            
            for system in requested_systems:
                system_info = self._get_treatment_info_with_cache(disease, system)
                if system_info:
                    treatment_options[system] = system_info
            
            # Construct the result based on the fetched treatment options
            exploration = {
                "disease": disease.replace("_", " ").title(),
                "systems_explored": requested_systems,
                "treatment_options": treatment_options,
                "comparison_summary": self._generate_comparison_summary(disease, requested_systems),
                "general_guidance": self._get_general_guidance(disease),
                "safety_priorities": self._get_safety_priorities(),
                "next_steps": self._get_next_steps(disease, input_data.get("user_context", {}))
            }

            return self.format_agent_response(
                success=True,
                data=exploration,
                message=f"Treatment options explored for {disease}"
            )
            
        except Exception as e:
            logger_treatment.error(f"Treatment exploration error: {str(e)}")
            return self.format_agent_response(
                success=False,
                message=f"Error exploring treatments: {str(e)}",
                data={"error": str(e)}
            )
    
    def _get_treatment_info_with_cache(self, disease: str, system: str) -> Optional[Dict[str, Any]]:
        """
        Get treatment info with cache support for performance.
        
        Args:
            disease: Disease name
            systems: List of systems to explore ("all" or specific systems)
            user_context: User age, gender, existing conditions, medications
            
        Returns:
            Comprehensive treatment exploration
        """
        # Note: 'systems' argument in logic seems to be 'system' parameter, but the original code had 'systems' as arg in docstring but 'system' in signature?
        # The original signature was `def _get_treatment_info_with_cache(self, disease: str, system: str)`.
        # Inside it used 'systems' variable. I will fix this logic.
        # The original code at line 994: `if systems is None or "all" in systems:` which implies 'systems' was expected?
        # But the method is called inside a loop over `requested_systems`.
        # It seems the original code might have had a bug or 'systems' was a global/outer scope variable?
        # No, wait. 
        # In original code lines 953 calls `self._get_treatment_info_with_cache(disease, system)`.
        # Lines 982 definition `def _get_treatment_info_with_cache(self, disease: str, system: str)`.
        # Line 994 `if systems is None...`. 'systems' is NOT defined in the scope of `_get_treatment_info_with_cache`.
        # This is a BUG in the original code! 'systems' is undefined.
        # I should fix this bug.
        # It seems 'system' (singular) is passed.
        # And the logic seems to want to check if 'system' is valid?
        # Or maybe it meant to say `if system is None...`.
        # But `systems` usage at 1009 ` "systems_explored": systems,` suggests it wants the list?
        # But it returns info for ONE system.
        # I will fix this method to handle single system properly.
        
        # FIX:
        # The method should just return the data for the requested system.
        
        disease_treatments = self.detailed_treatments.get(disease, {})
        
        if not disease_treatments:
             # Logic for "not available"
             # In original code, it returned a default dict.
             pass

        # In the loop:
        # if system in disease_treatments: ...
        
        # I will rewrite this method to be correct.
        
        if not self.detailed_treatments.get(disease):
             # Return None or empty implies not found.
             # Original returned an error dict?
             # "message": "Detailed treatment information not yet available..."
             # If I return None, the caller loop ignores it.
             # I'll return the error dict IF it's the first system?
             # The caller `process` creates `treatment_options = {}`.
             pass
        
        # Actually, let's look at the original code structure again.
        # It tries to return a FULL exploration object for a SINGLE system?
        # That's weird. `exploration["treatment_options"][system] = ...`
        # It seems the cache method was intended to return the WHOLE thing, but `process` calls it per system.
        # If `process` calls it per system, it expects just the system data?
        # Line 955: `treatment_options[system] = system_info`.
        # If `system_info` is the huge dict, then `treatment_options` will be { 'allopathy': { 'disease':..., 'treatment_options': {...} } }.
        # That's nested weirdly.
        # I suspect the original code was broken or I misunderstood.
        # Let's see line 1021: `exploration["treatment_options"][system] = ...`
        # It constructs `exploration` dict.
        # So `system_info` IS the `exploration` dict.
        # Then `process` puts it into `treatment_options[system]`.
        # So `treatment_options` becomes `{'allopathy': ExplorationObject, 'homeopathy': ExplorationObject}`.
        # Then `process` creates `exploration` (lines 958-966) containing `treatment_options`.
        # So the result is `Exploration -> treatment_options -> system -> Exploration`.
        # The inner Exploration contains `treatment_options` -> `system` -> Data.
        # This is redundant.
        # However, I should preserve the "Logic" even if weird, unless it's clearly broken.
        # The 'systems' undefined variable is a crash.
        # I will assume 'systems' meant `[system]`.
        
        systems = [system] 
        
        disease_treatments = self.detailed_treatments.get(disease, {})
        
        if not disease_treatments:
            return {
                "system_name": system.title(),
                "available": False,
                "message": "Information not available"
            } # Simplified fallback
            
        # Returning just the system data seems more logical if `process` aggregates it.
        # But `process` loop expects something to put into `treatment_options[system]`.
        # If I return the inner data, it works.
        
        if system in disease_treatments:
            system_data = disease_treatments[system]
            # Construct the data expected by the frontend?
            # The original code constructed a full response.
            # I'll just return the system-specific data which seems to be what `disease_treatments[system]` holds, 
            # augmented with some fields?
            
            # Let's look at what `process` does with it.
            # `treatment_options[system] = system_info`
            # `exploration = { ... "treatment_options": treatment_options ... }`
            
            # If `system_info` is the system data, then `exploration` looks like:
            # { "treatment_options": { "allopathy": { "system_name": ..., "treatments": ... } } }
            # This is standard.
            
            # But the original code `_get_treatment_info_with_cache` created a whole `exploration` object structure:
            # `exploration = { "disease": ..., "treatment_options": {}, ... }`
            # And added the system to it.
            # So `system_info` (which is this exploration object) would be put inside `treatment_options`.
            # That results in:
            # { "treatment_options": { "allopathy": { "disease":..., "treatment_options": {"allopathy": ...} } } }
            # This looks like a bug in the original composition or the cache method.
            # Given the `process` method also constructs `exploration` (line 958), the `_get_treatment_info_with_cache`
            # likely should HAVE returned just the specific system's content.
            
            # I will fix this to return the system content directly.
            
            output_data = {
                "system_name": system_data.get("system_name"),
                "primary_goal": system_data.get("primary_goal"),
                "approach": system_data.get("approach_philosophy", ""),
                "treatments": system_data.get("treatments", []),
                "expected_timeline": system_data.get("expected_timeline"),
                "success_rate": system_data.get("success_rate"),
                "disclaimer": system_data.get("disclaimer")
            }
            if "complementary_practices" in system_data:
                output_data["complementary_practices"] = system_data["complementary_practices"]
            if "integration_notes" in system_data:
                output_data["integration_notes"] = system_data["integration_notes"]
                
            return output_data
            
        return None

    def _generate_comparison_summary(self, disease: str, systems: List[str]) -> Dict[str, str]:
        """Generate a summary comparing different treatment systems."""
        comparisons = {
            "allopathy": "Modern evidence-based medicine, most extensively studied, fastest results, requires monitoring",
            "homeopathy": "Individualized constitutional approach, gentle, limited scientific evidence, slow to act",
            "ayurveda": "Traditional natural remedies, moderate scientific evidence, requires lifestyle changes, gradual effects",
            "integrative": "Combines multiple systems for comprehensive care, requires coordinated team, potentially best outcomes"
        }
        
        return {system: comparisons.get(system, "") for system in systems if system in comparisons}
    
    def _get_general_guidance(self, disease: str) -> str:
        """Get general guidance for treatment exploration."""
        return (
            f"Treatment for {disease.replace('_', ' ')} works best with a comprehensive approach. "
            "Different medical systems offer different perspectives and methods. "
            "The most effective strategy often combines evidence-based conventional medicine "
            "with complementary approaches under professional supervision. "
            "Always inform all your healthcare providers about every treatment you're using."
        )
    
    def _get_safety_priorities(self) -> List[str]:
        """Get safety priorities for treatment exploration."""
        return [
            "Never stop or reduce prescribed medications without medical supervision",
            "Inform all healthcare providers about all treatments (conventional and alternative)",
            "Monitor your condition regularly (blood tests, measurements, symptoms)",
            "Watch for interactions between treatments",
            "Seek emergency care for serious symptoms regardless of treatment approach",
            "Be cautious of claims that sound too good to be true",
            "Verify practitioner qualifications in their respective systems"
        ]
    
    def _get_next_steps(self, disease: str, user_context: Dict = None) -> List[str]:
        """Get recommended next steps for user."""
        return [
            f"Discuss these treatment options with your primary healthcare provider",
            f"Get a comprehensive health assessment to understand your specific situation",
            "Consider consulting specialists in systems that interest you",
            "Keep a symptom and treatment journal",
            "Join support groups or educational programs about {disease.replace('_', ' ')}",
            "Stay informed about new research and treatment advances"
        ]
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """Get summary of treatment exploration agent capabilities."""
        return {
            "agent": "TreatmentExplorationAgent",
            "purpose": "Comprehensive treatment option exploration across medical systems",
            "systems_covered": ["Allopathy", "Homeopathy", "Ayurveda", "Integrative"],
            "diseases_supported": list(self.detailed_treatments.keys()),
            "information_provided": [
                "Treatment mechanisms",
                "Effectiveness and evidence",
                "Side effects and safety",
                "Contraindications",
                "Expected timelines",
                "Integration guidance"
            ],
            "disclaimer": "All information educational only. Professional consultation required for treatment decisions."
        }

# =================================================================================================
# 3. Data Extraction Agent
# =================================================================================================

import json

logger_data = logging.getLogger('health_ai.data_extraction')


class DataExtractionAgent(BaseHealthAgent):
    """
    LangChain-based agent for extracting and mapping user input to ML model features.
    
    Uses Gemini AI to:
    - Parse natural language symptom descriptions
    - Map symptoms to standardized medical terms
    - Extract relevant features for ML model
    - Handle missing or ambiguous data
    """
    
    def __init__(self):
        """Initialize the data extraction agent."""
        super().__init__("DataExtractionAgent")
        
        # Define expected ML model features for different diseases
        self.model_features = {
            "diabetes": [
                "age", "gender", "polyuria", "polydipsia", "sudden_weight_loss",
                "weakness", "polyphagia", "genital_thrush", "visual_blurring",
                "itching", "irritability", "delayed_healing", "partial_paresis",
                "muscle_stiffness", "alopecia", "obesity"
            ],
            "heart_disease": [
                "age", "gender", "chest_pain_type", "resting_blood_pressure",
                "cholesterol", "fasting_blood_sugar", "resting_ecg",
                "max_heart_rate", "exercise_angina", "oldpeak", "slope",
                "ca", "thal"
            ],
            "hypertension": [
                "age", "gender", "systolic_bp", "diastolic_bp", "bmi",
                "smoking", "alcohol", "physical_activity", "stress_level",
                "family_history", "salt_intake", "sleep_hours"
            ]
        }
        
        # Symptom to feature mapping
        self.symptom_mappings = {
            "increased_thirst": "polydipsia",
            "excessive_thirst": "polydipsia",
            "frequent_urination": "polyuria",
            "excessive_urination": "polyuria",
            "weight_loss": "sudden_weight_loss",
            "losing_weight": "sudden_weight_loss",
            "fatigue": "weakness",
            "tired": "weakness",
            "excessive_hunger": "polyphagia",
            "always_hungry": "polyphagia",
            "blurred_vision": "visual_blurring",
            "vision_problems": "visual_blurring",
            "chest_pain": "chest_pain_type",
            "chest_discomfort": "chest_pain_type",
            "shortness_of_breath": "exercise_angina",
            "breathing_difficulty": "exercise_angina",
            "headache": "systolic_bp",  # Indicator for hypertension
            "dizziness": "systolic_bp"
        }
        
        # Create LangChain chain for intelligent data extraction
        self.extraction_chain = self.create_agent_chain(
            system_prompt="""You are a medical data extraction agent. Your role is to:
1. Parse user-provided symptoms and health information
2. Map symptoms to standardized medical terms
3. Extract relevant features for disease prediction models
4. Handle ambiguous or incomplete information

IMPORTANT:
- Be precise in symptom mapping
- Ask for clarification when needed
- Use medical terminology correctly
- Return structured data in JSON format""",
            
            human_prompt="""Extract and map the following health information to standardized medical features:

User Input:
- Symptoms: {symptoms}
- Age: {age}
- Gender: {gender}
- Additional Info: {additional_info}

Target Disease: {disease}
Required Features: {required_features}

Please extract and map the data to match the required features. Return a JSON object with:
1. "mapped_features": Dictionary of feature names and values
2. "confidence": Your confidence in the extraction (0-1)
3. "missing_features": List of features that couldn't be extracted
4. "clarifications_needed": List of questions to ask user for better accuracy"""
        )
        
        logger_data.info("DataExtractionAgent initialized with LangChain")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for data extraction.
        
        Args:
            input_data: Raw user input containing symptoms, age, gender, etc.
            
        Returns:
            Extracted and mapped data ready for ML model
        """
        required_fields = ["symptoms", "age", "gender"]
        validation = self.validate_input(input_data, required_fields)
        
        if not validation["valid"]:
            return self.format_agent_response(
                success=False,
                message=validation["message"],
                data=validation
            )
        
        self.log_agent_action("extract_data", {
            "symptoms_count": len(input_data.get("symptoms", [])),
            "disease": input_data.get("disease", "unknown")
        })
        
        try:
            # Extract and map data
            extracted_data = self.extract_and_map(
                symptoms=input_data["symptoms"],
                age=input_data["age"],
                gender=input_data["gender"],
                disease=input_data.get("disease", "diabetes"),
                additional_info=input_data.get("additional_info", {})
            )
            
            return self.format_agent_response(
                success=True,
                data=extracted_data,
                message="Data extraction completed successfully"
            )
            
        except Exception as e:
            logger_data.error(f"Error in data extraction: {str(e)}")
            return self.get_fallback_response(input_data)
    
    def extract_and_map(self, symptoms: List[str], age: int, gender: str,
                       disease: str, additional_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extract and map user data to ML model features using Gemini AI.
        
        Args:
            symptoms: List of user symptoms
            age: User age
            gender: User gender
            disease: Target disease for prediction
            additional_info: Additional health information
            
        Returns:
            Dictionary with mapped features and metadata
        """
        logger_data.info(f"Extracting data for {disease} prediction")
        
        try:
            # Get required features for the disease
            required_features = self.model_features.get(disease, [])
            
            # Try LangChain extraction first
            if self.extraction_chain:
                langchain_result = self._extract_with_langchain(
                    symptoms, age, gender, disease, required_features, additional_info
                )
                if langchain_result:
                    return langchain_result
            
            # Fallback to rule-based extraction
            return self._extract_with_rules(
                symptoms, age, gender, disease, required_features, additional_info
            )
            
        except Exception as e:
            logger_data.error(f"Error in extract_and_map: {str(e)}")
            return self._get_fallback_extraction(symptoms, age, gender, disease)
    
    def _extract_with_langchain(self, symptoms: List[str], age: int, gender: str,
                                disease: str, required_features: List[str],
                                additional_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract data using LangChain and Gemini AI."""
        try:
            if not self.extraction_chain:
                return None
            
            # Prepare input for LangChain
            chain_input = {
                "symptoms": ", ".join(symptoms),
                "age": age,
                "gender": gender,
                "disease": disease,
                "required_features": ", ".join(required_features),
                "additional_info": json.dumps(additional_info or {})
            }
            
            # Execute chain
            result = self.execute_chain(self.extraction_chain, chain_input)
            
            if result:
                # Parse JSON response from Gemini
                try:
                    parsed_result = json.loads(result)
                    
                    # Add basic features
                    parsed_result["mapped_features"]["age"] = age
                    parsed_result["mapped_features"]["gender"] = 1 if gender.lower() == "male" else 0
                    
                    return {
                        "features": parsed_result["mapped_features"],
                        "extraction_confidence": parsed_result.get("confidence", 0.7),
                        "missing_features": parsed_result.get("missing_features", []),
                        "clarifications_needed": parsed_result.get("clarifications_needed", []),
                        "extraction_method": "langchain_gemini",
                        "disease": disease
                    }
                except json.JSONDecodeError:
                    logger_data.warning("Failed to parse LangChain JSON response, using fallback")
                    return None
            
            return None
            
        except Exception as e:
            logger_data.error(f"LangChain extraction failed: {str(e)}")
            return None
    
    def _extract_with_rules(self, symptoms: List[str], age: int, gender: str,
                           disease: str, required_features: List[str],
                           additional_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data using rule-based mapping."""
        logger_data.info("Using rule-based extraction")
        
        features = {}
        
        # Add basic features
        features["age"] = age
        features["gender"] = 1 if gender.lower() == "male" else 0
        
        # Map symptoms to features
        for symptom in symptoms:
            symptom_lower = symptom.lower().strip().replace(" ", "_")
            
            # Direct mapping
            if symptom_lower in self.symptom_mappings:
                feature_name = self.symptom_mappings[symptom_lower]
                if feature_name in required_features:
                    features[feature_name] = 1  # Binary feature
            
            # Check if symptom matches any required feature
            for feature in required_features:
                if symptom_lower in feature or feature in symptom_lower:
                    features[feature] = 1
        
        # Add additional info if provided
        if additional_info:
            for key, value in additional_info.items():
                if key in required_features:
                    features[key] = value
        
        # Fill missing features with defaults
        missing_features = []
        for feature in required_features:
            if feature not in features and feature not in ["age", "gender"]:
                features[feature] = 0  # Default to 0 for binary features
                missing_features.append(feature)
        
        return {
            "features": features,
            "extraction_confidence": 0.6,  # Lower confidence for rule-based
            "missing_features": missing_features,
            "clarifications_needed": [],
            "extraction_method": "rule_based",
            "disease": disease
        }
    
    def _get_fallback_extraction(self, symptoms: List[str], age: int, 
                                gender: str, disease: str) -> Dict[str, Any]:
        """Get minimal fallback extraction."""
        return {
            "features": {
                "age": age,
                "gender": 1 if gender.lower() == "male" else 0,
                "symptoms_count": len(symptoms)
            },
            "extraction_confidence": 0.3,
            "missing_features": ["most_features"],
            "clarifications_needed": ["Please provide more detailed health information"],
            "extraction_method": "fallback",
            "disease": disease
        }
    
    def get_supported_diseases(self) -> List[str]:
        """Get list of diseases with feature mappings."""
        return list(self.model_features.keys())
    
    def get_required_features(self, disease: str) -> List[str]:
        """Get required features for a specific disease."""
        return self.model_features.get(disease, [])
    
    def get_extraction_summary(self) -> Dict[str, Any]:
        """Get summary of extraction capabilities."""
        return {
            "agent_type": "DataExtractionAgent",
            "framework": "LangChain",
            "supported_diseases": self.get_supported_diseases(),
            "extraction_methods": ["langchain_gemini", "rule_based", "fallback"],
            "features": [
                "Natural language symptom parsing",
                "Intelligent feature mapping",
                "Missing data handling",
                "Clarification suggestions"
            ],
            "llm_available": bool(self.llm)
        }

# =================================================================================================
# 4. Validation Agent
# =================================================================================================

import re

logger_validation = logging.getLogger('health_ai.validation')


class LangChainValidationAgent(BaseHealthAgent):
    """
    LangChain-based validation agent for health intelligence system.
    
    Provides first-line defense against incomplete or unsafe inputs
    with enhanced LangChain capabilities for intelligent validation.
    """
    
    # Required fields as per Requirements 1.2
    REQUIRED_FIELDS = ["age", "gender", "symptoms"]
    
    # Valid gender options
    VALID_GENDERS = ["male", "female", "other"]
    
    # Age validation bounds
    MIN_AGE = 1
    MAX_AGE = 120
    
    # Symptom validation
    MAX_SYMPTOMS_PER_REQUEST = 20
    MIN_SYMPTOM_LENGTH = 2
    MAX_SYMPTOM_LENGTH = 100
    
    # Unsafe patterns to filter out
    UNSAFE_PATTERNS = [
        r'<script.*?>.*?</script>',  # Script tags
        r'javascript:',              # JavaScript URLs
        r'on\w+\s*=',               # Event handlers
        r'<.*?>',                   # HTML tags
        r'sql\s+(select|insert|update|delete|drop|create)',  # SQL injection
    ]
    
    def __init__(self):
        """Initialize the LangChain validation agent."""
        super().__init__("ValidationAgent")
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.UNSAFE_PATTERNS]
        
        # Create LangChain chain for intelligent validation feedback
        self.validation_chain = self.create_agent_chain(
            system_prompt="""You are a validation agent for a health assessment system. 
            Your role is to provide clear, helpful feedback about input validation issues.
            Always be supportive and guide users on how to correct their input.
            Keep responses concise and actionable.""",
            
            human_prompt="""The user input has validation issues: {validation_issues}
            Please provide a clear, helpful message explaining what needs to be corrected.
            Be specific about what the user should do to fix the issues."""
        )
        
        logger_validation.info("LangChain ValidationAgent initialized")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for validation.
        
        Args:
            input_data: User input to validate
            
        Returns:
            Validation result with LangChain-enhanced feedback
        """
        self.log_agent_action("validate_input", {"fields_count": len(input_data)})
        
        try:
            # Perform basic validation
            validation_result = self.validate_symptoms(input_data)
            
            # If validation failed and LangChain is available, enhance the feedback
            if not validation_result["valid"] and self.validation_chain:
                enhanced_feedback = self._get_enhanced_feedback(validation_result)
                if enhanced_feedback:
                    validation_result["enhanced_feedback"] = enhanced_feedback
            
            return self.format_agent_response(
                success=validation_result["valid"],
                data=validation_result,
                message="Input validation completed"
            )
            
        except Exception as e:
            logger_validation.error(f"Validation processing error: {str(e)}")
            return self.get_fallback_response(input_data)
    
    def validate_symptoms(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main validation method for symptom input with LangChain enhancements.
        
        Args:
            user_input: Dictionary containing user symptoms and metadata
            
        Returns:
            Dictionary with validation results and enhanced feedback
        """
        logger_validation.info(f"Validating symptoms input: {len(user_input)} fields provided")
        
        try:
            # Check required fields
            validation_result = self._validate_required_fields(user_input)
            if not validation_result["valid"]:
                return validation_result
            
            # Validate age
            validation_result = self._validate_age(user_input["age"])
            if not validation_result["valid"]:
                return validation_result
            
            # Validate gender
            validation_result = self._validate_gender(user_input["gender"])
            if not validation_result["valid"]:
                return validation_result
            
            # Validate symptoms
            validation_result = self._validate_symptoms_format(user_input["symptoms"])
            if not validation_result["valid"]:
                return validation_result
            
            # Apply safety filters
            validation_result = self._apply_safety_filters(user_input)
            if not validation_result["valid"]:
                return validation_result
            
            # If all validations pass, return sanitized input
            sanitized_input = self._sanitize_input(user_input)
            
            logger_validation.info("Input validation successful")
            return {
                "valid": True,
                "sanitized_input": sanitized_input,
                "validation_timestamp": datetime.utcnow().isoformat(),
                "agent": "LangChainValidationAgent"
            }
            
        except Exception as e:
            logger_validation.error(f"Validation error: {str(e)}")
            return {
                "valid": False,
                "reason": "Internal validation error",
                "error": str(e),
                "agent": "LangChainValidationAgent"
            }
    
    def _get_enhanced_feedback(self, validation_result: Dict[str, Any]) -> Optional[str]:
        """
        Get enhanced feedback using LangChain for validation failures.
        
        Args:
            validation_result: Basic validation result
            
        Returns:
            Enhanced feedback message or None
        """
        try:
            if not self.validation_chain:
                return None
            
            # Prepare validation issues for LangChain
            issues = []
            if "reason" in validation_result:
                issues.append(validation_result["reason"])
            if "missing" in validation_result:
                issues.append(f"Missing fields: {', '.join(validation_result['missing'])}")
            
            if not issues:
                return None
            
            # Get enhanced feedback from LangChain
            enhanced_feedback = self.execute_chain(
                self.validation_chain,
                {"validation_issues": "; ".join(issues)}
            )
            
            return enhanced_feedback
            
        except Exception as e:
            logger_validation.error(f"Error getting enhanced feedback: {str(e)}")
            return None
    
    def _validate_required_fields(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all required fields are present."""
        missing_fields = [field for field in self.REQUIRED_FIELDS if field not in user_input or user_input[field] is None]
        
        if missing_fields:
            logger_validation.warning(f"Missing required fields: {missing_fields}")
            return {
                "valid": False,
                "reason": "Missing critical fields",
                "missing": missing_fields
            }
        
        return {"valid": True}
    
    def _validate_age(self, age: Any) -> Dict[str, Any]:
        """Validate age field."""
        try:
            age_int = int(age)
            if not (self.MIN_AGE <= age_int <= self.MAX_AGE):
                logger_validation.warning(f"Invalid age range: {age_int}")
                return {
                    "valid": False,
                    "reason": f"Age must be between {self.MIN_AGE} and {self.MAX_AGE} years"
                }
            return {"valid": True}
        except (ValueError, TypeError):
            logger_validation.warning(f"Invalid age format: {age}")
            return {
                "valid": False,
                "reason": "Age must be a valid number"
            }
    
    def _validate_gender(self, gender: Any) -> Dict[str, Any]:
        """Validate gender field."""
        if not isinstance(gender, str):
            return {
                "valid": False,
                "reason": "Gender must be a string"
            }
        
        gender_lower = gender.lower().strip()
        if gender_lower not in self.VALID_GENDERS:
            logger_validation.warning(f"Invalid gender: {gender}")
            return {
                "valid": False,
                "reason": f"Gender must be one of: {', '.join(self.VALID_GENDERS)}"
            }
        
        return {"valid": True}
    
    def _validate_symptoms_format(self, symptoms: Any) -> Dict[str, Any]:
        """Validate symptoms format and content."""
        if not isinstance(symptoms, list):
            return {
                "valid": False,
                "reason": "Symptoms must be provided as a list"
            }
        
        if len(symptoms) == 0:
            return {
                "valid": False,
                "reason": "At least one symptom must be provided"
            }
        
        if len(symptoms) > self.MAX_SYMPTOMS_PER_REQUEST:
            return {
                "valid": False,
                "reason": f"Maximum {self.MAX_SYMPTOMS_PER_REQUEST} symptoms allowed per request"
            }
        
        # Validate each symptom
        for i, symptom in enumerate(symptoms):
            if not isinstance(symptom, str):
                return {
                    "valid": False,
                    "reason": f"Symptom {i+1} must be a string"
                }
            
            symptom_clean = symptom.strip()
            if len(symptom_clean) < self.MIN_SYMPTOM_LENGTH:
                return {
                    "valid": False,
                    "reason": f"Symptom {i+1} is too short (minimum {self.MIN_SYMPTOM_LENGTH} characters)"
                }
            
            if len(symptom_clean) > self.MAX_SYMPTOM_LENGTH:
                return {
                    "valid": False,
                    "reason": f"Symptom {i+1} is too long (maximum {self.MAX_SYMPTOM_LENGTH} characters)"
                }
        
        return {"valid": True}
    
    def _apply_safety_filters(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Apply safety filters to detect potentially malicious input."""
        # Check all string values for unsafe patterns
        for key, value in user_input.items():
            if isinstance(value, str):
                if self._contains_unsafe_content(value):
                    logger_validation.warning(f"Unsafe content detected in field: {key}")
                    return {
                        "valid": False,
                        "reason": "Input contains potentially unsafe content"
                    }
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and self._contains_unsafe_content(item):
                        logger_validation.warning(f"Unsafe content detected in list field: {key}")
                        return {
                            "valid": False,
                            "reason": "Input contains potentially unsafe content"
                        }
        
        return {"valid": True}
    
    def _contains_unsafe_content(self, text: str) -> bool:
        """Check if text contains unsafe patterns."""
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True
        return False
    
    def _sanitize_input(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize and normalize the input."""
        sanitized = {}
        
        # Sanitize age
        sanitized["age"] = int(user_input["age"])
        
        # Sanitize gender
        sanitized["gender"] = user_input["gender"].lower().strip()
        
        # Sanitize symptoms
        sanitized["symptoms"] = [symptom.strip().lower() for symptom in user_input["symptoms"]]
        
        # Include optional fields if present
        if "medical_history" in user_input:
            if isinstance(user_input["medical_history"], list):
                sanitized["medical_history"] = [
                    item.strip().lower() if isinstance(item, str) else item 
                    for item in user_input["medical_history"]
                ]
            else:
                sanitized["medical_history"] = []
        
        return sanitized
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of validation rules for documentation."""
        return {
            "agent_type": "LangChainValidationAgent",
            "framework": "LangChain",
            "required_fields": self.REQUIRED_FIELDS,
            "age_range": {"min": self.MIN_AGE, "max": self.MAX_AGE},
            "valid_genders": self.VALID_GENDERS,
            "symptom_limits": {
                "max_count": self.MAX_SYMPTOMS_PER_REQUEST,
                "min_length": self.MIN_SYMPTOM_LENGTH,
                "max_length": self.MAX_SYMPTOM_LENGTH
            },
            "safety_features": [
                "HTML/Script injection prevention",
                "SQL injection prevention", 
                "Input sanitization",
                "Length validation",
                "LangChain-enhanced feedback"
            ],
            "llm_available": bool(self.llm)
        }

# =================================================================================================
# 5. Explanation Agent
# =================================================================================================

logger_explanation = logging.getLogger('health_ai.explanation')


class LangChainExplanationAgent(BaseHealthAgent):
    """
    LangChain-based explanation agent for health risk assessments.
    
    Key responsibilities:
    - Generate clear explanations using LangChain and Gemini AI
    - Provide confidence reasoning
    - Add appropriate medical disclaimers
    - Maintain educational focus (never diagnostic)
    """
    
    def __init__(self):
        """Initialize the LangChain explanation agent."""
        super().__init__("ExplanationAgent")
        
        # Confidence level explanations
        self.confidence_explanations = {
            "LOW": {
                "meaning": "The system has limited confidence in this assessment",
                "reason": "The symptoms provided are either too general, insufficient, or don't strongly indicate any specific condition",
                "recommendation": "Consider providing more specific symptoms or consulting a healthcare professional"
            },
            "MEDIUM": {
                "meaning": "The system has moderate confidence in this assessment",
                "reason": "The symptoms show some patterns that suggest this condition, but additional factors should be considered",
                "recommendation": "This warrants attention and professional medical evaluation"
            },
            "HIGH": {
                "meaning": "The system has high confidence in this assessment",
                "reason": "The symptoms strongly align with patterns associated with this condition",
                "recommendation": "We strongly recommend consulting with a healthcare professional for proper evaluation"
            }
        }
        
        # Standard medical disclaimer
        self.medical_disclaimer = (
            "IMPORTANT DISCLAIMER: This assessment is for educational and informational "
            "purposes only. It is not intended to be a substitute for professional medical "
            "advice, diagnosis, or treatment. Always seek the advice of your physician or "
            "other qualified health provider with any questions you may have regarding a "
            "medical condition."
        )
        
        # Create LangChain chain for explanation generation
        self.explanation_chain = self.create_agent_chain(
            system_prompt="""You are an expert medical AI assistant providing detailed health risk assessment explanations. Your role is to educate patients while emphasizing this is NOT a medical diagnosis.

CRITICAL REQUIREMENTS:
- This is NOT a medical diagnosis - always emphasize professional consultation
- Provide detailed, structured explanations with medical context
- Use simple, non-medical language (explain any medical terms in parentheses)
- Be compassionate, supportive, and not alarming
- Focus on education and understanding
- Include specific symptom correlations
- Explain risk factors relevant to the condition
- List warning signs requiring immediate attention
- Provide confidence reasoning
- Keep tone professional yet accessible

RESPONSE STRUCTURE:
Your explanation should cover:
1. Brief summary of the assessment
2. Detailed explanation of the condition in layman terms
3. How the patient's specific symptoms relate to this condition
4. Key risk factors for this condition
5. Warning signs that require immediate medical attention
6. Next steps based on confidence level
7. Why the confidence is at this level

Remember: Maintain an educational, supportive tone while strongly encouraging professional medical consultation.""",
            
            human_prompt="""Please provide a comprehensive explanation for this health risk assessment:

Condition assessed: {disease}
Risk probability: {probability_percent}%
Confidence level: {confidence}
Patient's symptoms: {symptoms}

Provide a detailed, structured explanation that includes:
1. **Summary**: Brief 2-3 sentence overview in simple language
2. **What is {disease}**: Explain the condition in non-technical terms
3. **Symptom Correlation**: How these specific symptoms ({symptoms}) relate to {disease}
4. **Risk Factors**: List 35 key risk factors for {disease}
5. **Warning Signs**: List 3-5 serious symptoms requiring immediate medical attention
6. **Next Steps**: Clear guidance on what to do next based on {confidence} confidence
7. **Confidence Reasoning**: Why the confidence level is {confidence}

Use clear paragraphs and simple language. Explain any medical terminology. Emphasize the importance of professional medical consultation.

IMPORTANT: This is for educational purposes only and not a medical diagnosis."""
        )
        
        logger_explanation.info("LangChain ExplanationAgent initialized")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for explanation generation.
        
        Args:
            input_data: Contains disease, probability, confidence, symptoms, etc.
            
        Returns:
            Comprehensive explanation result
        """
        # Validate required input fields
        required_fields = ["disease", "probability", "confidence", "symptoms"]
        validation = self.validate_input(input_data, required_fields)
        
        if not validation["valid"]:
            return self.format_agent_response(
                success=False,
                message=validation["message"],
                data=validation
            )
        
        self.log_agent_action("generate_explanation", {
            "disease": input_data["disease"],
            "confidence": input_data["confidence"]
        })
        
        try:
            explanation_data = self.explain(
                disease=input_data["disease"],
                probability=input_data["probability"],
                confidence=input_data["confidence"],
                symptoms=input_data["symptoms"],
                additional_context=input_data.get("additional_context")
            )
            
            return self.format_agent_response(
                success=True,
                data=explanation_data,
                message="Explanation generated successfully"
            )
            
        except Exception as e:
            logger_explanation.error(f"Error in explanation processing: {str(e)}")
            return self.get_fallback_response(input_data)
    
    def explain(self, disease: str, probability: float, confidence: str, 
                symptoms: list, additional_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive explanation for a health risk assessment using LangChain.
        
        Args:
            disease: The disease/condition being assessed
            probability: Risk probability (0.0 to 1.0)
            confidence: Confidence level (LOW, MEDIUM, HIGH)
            symptoms: List of symptoms provided by user
            additional_context: Optional additional context for explanation
            
        Returns:
            Dictionary containing explanation components
        """
        logger_explanation.info(f"Generating explanation for {disease} with {confidence} confidence using LangChain")
        
        try:
            # Generate the main explanation using LangChain
            main_explanation = self._generate_langchain_explanation(
                disease, probability, confidence, symptoms
            )
            
            # Build comprehensive explanation structure
            explanation_data = {
                "summary": f"Risk assessment for {disease.replace('_', ' ').title()}",
                "probability_percent": round(probability * 100, 2),
                "confidence": confidence,
                "main_explanation": main_explanation,
                "confidence_reasoning": self._get_confidence_reasoning(confidence),
                "contributing_factors": self._analyze_contributing_factors(symptoms, disease),
                "educational_content": self._get_educational_content(disease),
                "disclaimer": self.medical_disclaimer,
                "generated_at": datetime.utcnow().isoformat(),
                "generated_by": "langchain_gemini_ai",
                "agent": "LangChainExplanationAgent"
            }
            
            logger_explanation.info("LangChain explanation generated successfully")
            return explanation_data
            
        except Exception as e:
            logger_explanation.error(f"Error generating LangChain explanation: {str(e)}")
            return self._get_fallback_explanation(disease, probability, confidence)
    
    def _generate_langchain_explanation(self, disease: str, probability: float, 
                                      confidence: str, symptoms: list) -> str:
        """
        Generate explanation using LangChain chain.
        
        Args:
            disease: Disease being assessed
            probability: Risk probability
            confidence: Confidence level
            symptoms: List of symptoms
            
        Returns:
            Generated explanation text
        """
        try:
            if not self.explanation_chain:
                return self._get_simple_explanation(disease, probability, confidence)
            
            # Prepare input for LangChain
            chain_input = {
                "disease": disease.replace('_', ' ').title(),
                "probability_percent": round(probability * 100, 1),
                "confidence": confidence,
                "symptoms": ", ".join(symptoms)
            }
            
            # Execute LangChain chain
            explanation = self.execute_chain(self.explanation_chain, chain_input)
            
            if explanation:
                return explanation
            else:
                return self._get_simple_explanation(disease, probability, confidence)
                
        except Exception as e:
            logger_explanation.error(f"LangChain explanation generation failed: {str(e)}")
            return self._get_simple_explanation(disease, probability, confidence)
    
    def _get_simple_explanation(self, disease: str, probability: float, confidence: str) -> str:
        """Get simple explanation when LangChain is unavailable."""
        return (
            f"Based on the symptoms provided, our system assessed a {probability:.1%} "
            f"risk level for {disease.replace('_', ' ')} with {confidence} confidence. "
            f"This assessment is for informational purposes only and should be discussed "
            f"with a healthcare professional for proper evaluation and guidance."
        )
    
    def _get_confidence_reasoning(self, confidence: str) -> Dict[str, str]:
        """Get reasoning for the confidence level."""
        return self.confidence_explanations.get(confidence, self.confidence_explanations["MEDIUM"])
    
    def _analyze_contributing_factors(self, symptoms: list, disease: str) -> Dict[str, Any]:
        """Analyze which factors contributed to the assessment."""
        # This is a simplified analysis - in a real system, this would be more sophisticated
        factor_analysis = {
            "primary_symptoms": [],
            "supporting_symptoms": [],
            "general_symptoms": []
        }
        
        # Disease-specific symptom categorization
        disease_patterns = {
            "diabetes": {
                "primary": ["increased_thirst", "frequent_urination", "unexplained_weight_loss", "fatigue"],
                "supporting": ["blurred_vision", "slow_healing", "tingling", "hunger"]
            },
            "heart_disease": {
                "primary": ["chest_pain", "shortness_of_breath", "fatigue", "irregular_heartbeat"],
                "supporting": ["dizziness", "nausea", "sweating", "arm_pain"]
            },
            "hypertension": {
                "primary": ["headaches", "dizziness", "chest_pain", "shortness_of_breath"],
                "supporting": ["fatigue", "vision_problems", "nosebleeds", "nausea"]
            }
        }
        
        patterns = disease_patterns.get(disease, {"primary": [], "supporting": []})
        
        for symptom in symptoms:
            symptom_clean = symptom.replace(" ", "_").lower()
            if symptom_clean in patterns["primary"]:
                factor_analysis["primary_symptoms"].append(symptom)
            elif symptom_clean in patterns["supporting"]:
                factor_analysis["supporting_symptoms"].append(symptom)
            else:
                factor_analysis["general_symptoms"].append(symptom)
        
        return factor_analysis
    
    def _get_educational_content(self, disease: str) -> Dict[str, str]:
        """Get educational content about the disease/condition."""
        educational_content = {
            "diabetes": {
                "about": "Diabetes is a group of metabolic disorders characterized by high blood sugar levels.",
                "risk_factors": "Family history, obesity, sedentary lifestyle, age, and certain ethnicities increase risk.",
                "prevention": "Maintaining healthy weight, regular exercise, and balanced diet can help prevent type 2 diabetes."
            },
            "heart_disease": {
                "about": "Heart disease refers to several types of heart conditions that affect heart function.",
                "risk_factors": "High blood pressure, high cholesterol, smoking, diabetes, and family history increase risk.",
                "prevention": "Regular exercise, healthy diet, not smoking, and managing stress can help prevent heart disease."
            },
            "hypertension": {
                "about": "Hypertension (high blood pressure) is a condition where blood pressure is consistently elevated.",
                "risk_factors": "Age, family history, obesity, high sodium intake, and lack of exercise increase risk.",
                "prevention": "Maintaining healthy weight, reducing sodium intake, regular exercise, and limiting alcohol can help."
            }
        }
        
        return educational_content.get(disease, {
            "about": "This condition requires professional medical evaluation for proper understanding.",
            "risk_factors": "Various factors can contribute to health conditions.",
            "prevention": "Maintaining a healthy lifestyle is generally beneficial for overall health."
        })
    
    def _get_fallback_explanation(self, disease: str, probability: float, confidence: str) -> Dict[str, Any]:
        """Generate fallback explanation when main generation fails."""
        logger_explanation.warning("Using fallback explanation due to LangChain generation failure")
        
        return {
            "summary": f"Risk assessment for {disease.replace('_', ' ').title()}",
            "probability_percent": round(probability * 100, 2),
            "confidence": confidence,
            "main_explanation": self._get_simple_explanation(disease, probability, confidence),
            "confidence_reasoning": self._get_confidence_reasoning(confidence),
            "contributing_factors": {"note": "Detailed analysis unavailable"},
            "educational_content": self._get_educational_content(disease),
            "disclaimer": self.medical_disclaimer,
            "generated_at": datetime.utcnow().isoformat(),
            "generated_by": "fallback_system",
            "agent": "LangChainExplanationAgent"
        }
    
    def create_confidence_specific_explanation(self, confidence: str, disease: str, 
                                             probability: float) -> str:
        """Create explanation templates specific to confidence levels."""
        templates = {
            "LOW": (
                f"Our assessment suggests a {probability:.1%} risk for {disease.replace('_', ' ')}. "
                f"However, we have low confidence in this assessment because the symptoms "
                f"provided are quite general and could be associated with many different conditions. "
                f"We recommend consulting with a healthcare professional who can perform a "
                f"proper evaluation considering your complete medical history."
            ),
            "MEDIUM": (
                f"Based on your symptoms, we've assessed a {probability:.1%} risk for "
                f"{disease.replace('_', ' ')} with moderate confidence. While the symptoms "
                f"show some patterns consistent with this condition, additional factors "
                f"should be considered. We recommend discussing these symptoms with a "
                f"healthcare professional for proper evaluation."
            ),
            "HIGH": (
                f"Our analysis indicates a {probability:.1%} risk for {disease.replace('_', ' ')} "
                f"with high confidence. The symptoms you've provided align strongly with "
                f"patterns associated with this condition. We strongly recommend consulting "
                f"with a healthcare professional promptly for proper diagnosis and "
                f"appropriate care."
            )
        }
        
        return templates.get(confidence, templates["MEDIUM"])
    
    def get_explanation_summary(self) -> Dict[str, Any]:
        """Get summary of explanation capabilities."""
        return {
            "agent_type": "LangChainExplanationAgent",
            "framework": "LangChain",
            "ai_integration": "Google Gemini",
            "supported_confidence_levels": list(self.confidence_explanations.keys()),
            "features": [
                "LangChain-powered natural language explanations",
                "Confidence reasoning",
                "Contributing factor analysis",
                "Educational content",
                "Medical disclaimers",
                "Fallback explanations"
            ],
            "llm_available": bool(self.llm),
            "gemini_status": self.gemini_client.get_client_status() if hasattr(self, 'gemini_client') else None
        }

# =================================================================================================
# 6. Lifestyle Modification Agent
# =================================================================================================

logger_lifestyle = logging.getLogger('health_ai.lifestyle')


class LifestyleModificationAgent(BaseHealthAgent):
    """
    Generates personalized lifestyle modification recommendations.
    
    Key responsibilities:
    - Diet recommendations based on condition
    - Exercise guidance tailored to health status
    - Stress management techniques
    - Sleep hygiene recommendations
    - Preventive care suggestions
    - Risk factor mitigation strategies
    """
    
    def __init__(self):
        """Initialize the lifestyle modification agent."""
        super().__init__("LifestyleModificationAgent")
        
        # Standard disclaimer for lifestyle advice
        self.disclaimer = (
            "IMPORTANT: These lifestyle recommendations are general guidance based on your "
            "health assessment. Always consult with your healthcare provider before making "
            "significant changes to your diet, exercise routine, or lifestyle, especially if "
            "you have existing health conditions or take medications."
        )
        
        # Condition-specific lifestyle databases
        self.diet_recommendations = self._initialize_diet_database()
        self.exercise_recommendations = self._initialize_exercise_database()
        self.stress_management_tips = self._initialize_stress_management()
        self.preventive_care_guidelines = self._initialize_preventive_care()
        
        logger_lifestyle.info("LifestyleModificationAgent initialized")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for lifestyle recommendations.
        
        Args:
            input_data: Contains disease, confidence, symptoms, user context, etc.
            
        Returns:
            Comprehensive lifestyle modification recommendations
        """
        # Validate required input fields
        required_fields = ["disease", "confidence"]
        validation = self.validate_input(input_data, required_fields)
        
        if not validation["valid"]:
            return self.format_agent_response(
                success=False,
                message=validation["message"],
                data=validation
            )
        
        self.log_agent_action("generate_lifestyle_recommendations", {
            "disease": input_data["disease"],
            "confidence": input_data["confidence"]
        })
        
        try:
            recommendations = self.generate_recommendations(
                disease=input_data["disease"],
                confidence=input_data["confidence"],
                symptoms=input_data.get("symptoms", []),
                user_context=input_data.get("user_context", {})
            )
            
            return self.format_agent_response(
                success=True,
                data=recommendations,
                message="Lifestyle recommendations generated successfully"
            )
            
        except Exception as e:
            logger_lifestyle.error(f"Error in lifestyle recommendation processing: {str(e)}")
            return self.get_fallback_response(input_data)
    
    def generate_recommendations(self, disease: str, confidence: str,
                                symptoms: List[str] = None,
                                user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate comprehensive lifestyle modification recommendations.
        
        Args:
            disease: The assessed disease/condition
            confidence: Confidence level (LOW, MEDIUM, HIGH)
            symptoms: List of symptoms (optional)
            user_context: User demographics and medical history (optional)
            
        Returns:
            Dictionary containing all lifestyle recommendations
        """
        logger_lifestyle.info(f"Generating lifestyle recommendations for {disease}")
        
        user_context = user_context or {}
        symptoms = symptoms or []
        
        recommendations = {
            "diet": self._get_diet_recommendations(disease, user_context),
            "exercise": self._get_exercise_recommendations(disease, confidence, user_context),
            "stress_management": self._get_stress_management_tips(disease),
            "sleep_hygiene": self._get_sleep_recommendations(disease),
            "preventive_care": self._get_preventive_care(disease, user_context),
            "risk_mitigation": self._get_risk_mitigation_strategies(disease, symptoms),
            "lifestyle_priorities": self._get_priority_recommendations(disease, confidence),
            "disclaimer": self.disclaimer,
            "generated_at": datetime.utcnow().isoformat(),
            "generated_by": "lifestyle_modification_agent"
        }
        
        logger_lifestyle.info(f"Lifestyle recommendations generated for {disease}")
        return recommendations
    
    def _get_diet_recommendations(self, disease: str, user_context: Dict) -> Dict[str, Any]:
        """Get personalized diet recommendations."""
        disease_key = disease.lower().replace(' ', '_')
        diet_data = self.diet_recommendations.get(disease_key, self.diet_recommendations["default"])
        
        return {
            "foods_to_include": diet_data["foods_to_include"],
            "foods_to_limit": diet_data["foods_to_limit"],
            "foods_to_avoid": diet_data["foods_to_avoid"], 
            "meal_timing": diet_data["meal_timing"],
            "hydration": diet_data["hydration"],
            "supplements": diet_data.get("supplements", []),
            "additional_tips": diet_data.get("additional_tips", [])
        }
    
    def _get_exercise_recommendations(self, disease: str, confidence: str,
                                     user_context: Dict) -> Dict[str, Any]:
        """Get personalized exercise recommendations."""
        disease_key = disease.lower().replace(' ', '_')
        exercise_data = self.exercise_recommendations.get(disease_key, 
                                                         self.exercise_recommendations["default"])
        
        # Adjust intensity based on confidence level
        intensity_adjustment = {
            "LOW": "Start very gently and increase gradually",
            "MEDIUM": "Moderate intensity with gradual progression",
            "HIGH": "Consult doctor before starting - medical clearance essential"
        }
        
        return {
            "recommended_activities": exercise_data["activities"],
            "frequency": exercise_data["frequency"],
            "duration": exercise_data["duration"],
            "intensity_level": exercise_data["intensity"],
            "precautions": exercise_data["precautions"],
            "medical_clearance": intensity_adjustment[confidence],
            "progression_tips": exercise_data.get("progression", [])
        }
    
    def _get_stress_management_tips(self, disease: str) -> Dict[str, Any]:
        """Get stress management recommendations."""
        disease_key = disease.lower().replace(' ', '_')
        stress_data = self.stress_management_tips.get(disease_key,
                                                      self.stress_management_tips["default"])
        
        return {
            "techniques": stress_data["techniques"],
            "relaxation_methods": stress_data["relaxation"],
            "mental_health_resources": stress_data["resources"],
            "mindfulness_practices": stress_data.get("mindfulness", []),
            "work_life_balance": stress_data.get("work_life_tips", [])
        }
    
    def _get_sleep_recommendations(self, disease: str) -> Dict[str, str]:
        """Get sleep hygiene recommendations."""
        general_sleep_tips = {
            "sleep_schedule": "Aim for 7-9 hours of sleep per night with consistent sleep/wake times",
            "bedtime_routine": "Create a relaxing bedtime routine 30-60 minutes before sleep",
            "sleep_environment": "Keep bedroom cool (60-67°F), dark, and quiet",
            "avoid_before_bed": "Avoid caffeine 6 hours before bed, alcohol 3 hours before, large meals 2-3 hours before",
            "screen_time": "Limit screen exposure 1-2 hours before bedtime",
            "physical_activity": "Regular exercise helps sleep, but not within 3 hours of bedtime"
        }
        
        # Disease-specific sleep considerations
        disease_specific = {
            "diabetes": "Monitor blood sugar before bed to avoid nighttime hypoglycemia",
            "heart_disease": "Elevate head if experiencing shortness of breath at night",
            "hypertension": "Consistent sleep schedule can help regulate blood pressure"
        }
        
        disease_key = disease.lower().replace(' ', '_')
        if disease_key in disease_specific:
            general_sleep_tips["disease_specific"] = disease_specific[disease_key]
        
        return general_sleep_tips
    
    def _get_preventive_care(self, disease: str, user_context: Dict) -> Dict[str, Any]:
        """Get preventive care recommendations."""
        disease_key = disease.lower().replace(' ', '_')
        preventive_data = self.preventive_care_guidelines.get(disease_key,
                                                              self.preventive_care_guidelines["default"])
        
        return {
            "screenings": preventive_data["screenings"],
            "vaccinations": preventive_data.get("vaccinations", []),
            "regular_checkups": preventive_data["checkups"],
            "monitoring_at_home": preventive_data.get("home_monitoring", []),
            "specialist_visits": preventive_data.get("specialists", [])
        }
    
    def _get_risk_mitigation_strategies(self, disease: str, symptoms: List[str]) -> Dict[str, Any]:
        """Get risk mitigation strategies."""
        disease_key = disease.lower().replace(' ', '_')
        
        risk_strategies = {
            "diabetes": {
                "primary_risks": ["High blood sugar", "Cardiovascular complications", "Nerve damage", "Kidney disease"],
                "mitigation": [
                    "Monitor blood glucose regularly",
                    "Maintain healthy weight",
                    "Control blood pressure and cholesterol",
                    "Regular foot and eye exams"
                ]
            },
            "heart_disease": {
                "primary_risks": ["Heart attack", "Stroke", "Heart failure", "Arrhythmias"],
                "mitigation": [
                    "Control blood pressure and cholesterol",
                    "Quit smoking completely",
                    "Maintain healthy weight",
                    "Regular cardiovascular exercise",
                    "Manage stress effectively"
                ]
            },
            "hypertension": {
                "primary_risks": ["Stroke", "Heart attack", "Kidney damage", "Vision loss"],
                "mitigation": [
                    "Reduce sodium intake (< 2,300mg per day)",
                    "DASH diet implementation",
                    "Regular blood pressure monitoring",
                    "Weight management",
                    "Limit alcohol consumption"
                ]
            }
        }
        
        default_strategies = {
            "primary_risks": ["General health complications"],
            "mitigation": ["Maintain healthy lifestyle", "Regular medical checkups", "Follow medical advice"]
        }
        
        return risk_strategies.get(disease_key, default_strategies)
    
    def _get_priority_recommendations(self, disease: str, confidence: str) -> List[str]:
        """Get top 3-5 priority lifestyle changes."""
        disease_key = disease.lower().replace(' ', '_')
        
        priorities = {
            "diabetes": [
                "1. Monitor blood sugar levels regularly",
                "2. Follow a balanced, low-glycemic diet",
                "3. Engage in regular physical activity (150 min/week)",
                "4. Maintain healthy weight",
                "5. Schedule regular medical checkups"
            ],
            "heart_disease": [
                "1. Adopt heart-healthy diet (Mediterranean or DASH)",
                "2. Quit smoking immediately if you smoke",
                "3. Regular cardiovascular exercise (as approved by doctor)",
                "4. Manage stress through relaxation techniques",
                "5. Monitor blood pressure and cholesterol"
            ],
            "hypertension": [
                "1. Reduce sodium intake significantly",
                "2. Increase potassium-rich foods (fruits, vegetables)",
                "3. Engage in regular aerobic exercise",
                "4. Maintain healthy weight (BMI < 25)",
                "5. Limit alcohol and manage stress"
            ]
        }
        
        default_priorities = [
            "1. Consult with healthcare provider for personalized advice",
            "2. Maintain balanced, nutritious diet",
            "3. Engage in regular physical activity",
            "4. Get adequate sleep (7-9 hours)",
            "5. Manage stress effectively"
        ]
        
        return priorities.get(disease_key, default_priorities)
    
    def _initialize_diet_database(self) -> Dict:
        """Initialize diet recommendations database."""
        return {
            "diabetes": {
                "foods_to_include": [
                    "Non-starchy vegetables (leafy greens, broccoli, cauliflower)",
                    "Whole grains (quinoa, brown rice, oats)",
                    "Lean proteins (fish, chicken, tofu, legumes)",
                    "Healthy fats (avocado, nuts, olive oil)",
                    "Low-glycemic fruits (berries, apples, citrus)"
                ],
                "foods_to_limit": [
                    "Refined carbohydrates (white bread, pasta)",
                    "High-sugar fruits (watermelon, pineapple)",
                    "Processed foods high in sodium"
                ],
                "foods_to_avoid": [
                    "Sugary drinks and sodas",
                    "Candy and sweets",
                    "Fried and high-fat foods",
                    "Highly processed foods"
                ],
                "meal_timing": "Eat regular meals at consistent times to maintain stable blood sugar",
                "hydration": "Drink 8-10 glasses of water daily; avoid sugary beverages",
                "supplements": ["Consult doctor about Vitamin D, B12, and Omega-3"],
                "additional_tips": [
                    "Use plate method: 1/2 vegetables, 1/4 lean protein, 1/4 whole grains",
                    "Monitor portion sizes carefully",
                    "Read nutrition labels for hidden sugars"
                ]
            },
            "heart_disease": {
                "foods_to_include": [
                    "Fatty fish (salmon, mackerel, sardines) 2-3 times/week",
                    "Vegetables and fruits (aim for 5-9 servings daily)",
                    "Whole grains (oats, barley, whole wheat)",
                    "Nuts and seeds (almonds, walnuts, flaxseeds)",
                    "Legumes (beans, lentils, chickpeas)"
                ],
                "foods_to_limit": [
                    "Red meat (limit to 1-2 times per month)",
                    "Full-fat dairy products",
                    "Sodium (< 2,300mg per day, ideally < 1,500mg)"
                ],
                "foods_to_avoid": [
                    "Trans fats and partially hydrogenated oils",
                    "Processed meats (bacon, sausage, deli meats)",
                    "Fried foods",
                    "High-sodium processed foods"
                ],
                "meal_timing": "Spread meals throughout the day; avoid large heavy meals",
                "hydration": "Drink adequate water; limit alcohol to 1 drink/day for women, 2 for men",
                "supplements": ["Ask doctor about Omega-3, CoQ10, and fiber supplements"],
                "additional_tips": [
                    "Follow Mediterranean or DASH diet patterns",
                    "Use herbs and spices instead of salt",
                    "Choose lean cooking methods (baking, grilling, steaming)"
                ]
            },
            "hypertension": {
                "foods_to_include": [
                    "Potassium-rich foods (bananas, sweet potatoes, spinach)",
                    "Vegetables and fruits (DASH diet emphasizes these)",
                    "Whole grains (brown rice, whole wheat, oatmeal)",
                    "Low-fat dairy (skim milk, yogurt)",
                    "Nuts, seeds, and legumes"
                ],
                "foods_to_limit": [
                    "Sodium (aim for < 1,500mg per day)",
                    "Caffeine (monitor blood pressure response)",
                    "Saturated fats"
                ],
                "foods_to_avoid": [
                    "Processed and packaged foods (high sodium)",
                    "Canned soups and vegetables (unless low-sodium)",
                    "Deli meats and cured foods",
                    "Salty snacks (chips, pretzels)"
                ],
                "meal_timing": "Regular meal schedule helps maintain stable blood pressure",
                "hydration": "Adequate water intake; limit alcohol consumption",
                "supplements": ["Discuss magnesium, potassium (only under medical supervision)"],
                "additional_tips": [
                    "DASH diet is highly recommended for hypertension",
                    "Read food labels carefully for sodium content",
                    "Cook at home to control sodium"
                ]
            },
            "default": {
                "foods_to_include": [
                    "Variety of fruits and vegetables",
                    "Whole grains",
                    "Lean proteins",
                    "Healthy fats (nuts, avocado, olive oil)"
                ],
                "foods_to_limit": [
                    "Processed foods",
                    "Added sugars",
                    "Excessive sodium"
                ],
                "foods_to_avoid": [
                    "Trans fats",
                    "Highly processed foods",
                    "Excessive alcohol"
                ],
                "meal_timing": "Regular, balanced meals throughout the day",
                "hydration": "Drink 8-10 glasses of water daily",
                "additional_tips": ["Focus on whole, unprocessed foods", "Practice portion control"]
            }
        }
    
    def _initialize_exercise_database(self) -> Dict:
        """Initialize exercise recommendations database."""
        return {
            "diabetes": {
                "activities": [
                    "Brisk walking",
                    "Swimming or water aerobics",
                    "Cycling",
                    "Light strength training",
                    "Yoga or tai chi"
                ],
                "frequency": "At least 5 days per week for aerobic exercise; 2-3 days for strength training",
                "duration": "150 minutes of moderate-intensity or 75 minutes of vigorous-intensity aerobic activity per week",
                "intensity": "Moderate (able to talk but not sing during exercise)",
                "precautions": [
                    "Check blood sugar before and after exercise",
                    "Carry fast-acting carbs for low blood sugar",
                    "Check feet for blisters or sores after exercise",
                    "Stay hydrated",
                    "Wear proper footwear"
                ],
                "progression": [
                    "Start with 10-minute sessions if needed",
                    "Gradually increase duration and intensity",
                    "Monitor blood sugar response to different activities"
                ]
            },
            "heart_disease": {
                "activities": [
                    "Walking (start slow, build up)",
                    "Cycling on flat terrain or stationary bike",
                    "Swimming",
                    "Light resistance training with medical clearance",
                    "Yoga (gentle)"
                ],
                "frequency": "Most days of the week (as approved by cardiologist)",
                "duration": "Start with 5-10 minutes, gradually increase to 30-60 minutes",
                "intensity": "Low to moderate - should be able to talk comfortably",
                "precautions": [
                    "MUST have medical clearance before starting",
                    "Stop immediately if experiencing chest pain, dizziness, or shortness of breath",
                    "Avoid extreme temperatures",
                    "Include warm-up and cool-down periods",
                    "May need cardiac rehab program"
                ],
                "progression": [
                    "Very gradual increase in duration and intensity",
                    "Follow cardiac rehabilitation program if prescribed",
                    "Regular monitoring by healthcare team"
                ]
            },
            "hypertension": {
                "activities": [
                    "Brisk walking",
                    "Jogging (if cleared by doctor)",
                    "Cycling",
                    "Swimming",
                    "Dancing",
                    "Light to moderate strength training"
                ],
                "frequency": "At least 5-7 days per week",
                "duration": "30-60 minutes of moderate-intensity exercise daily",
                "intensity": "Moderate (50-70% of maximum heart rate)",
                "precautions": [
                    "Avoid heavy weight lifting or straining (Valsalva maneuver)",
                    "Breathe normally during resistance exercises",
                    "Monitor blood pressure before and after exercise initially",
                    "Stay well hydrated",
                    "Avoid exercise if BP is very high (>180/110)"
                ],
                "progression": [
                    "Start with 10-15 minutes if new to exercise",
                    "Gradually increase to recommended duration",
                    "Add variety to maintain interest"
                ]
            },
            "default": {
                "activities": [
                    "Walking",
                    "Swimming",
                    "Cycling",
                    "Strength training",
                    "Flexibility exercises"
                ],
                "frequency": "Most days of the week",
                "duration": "At least 150 minutes of moderate activity per week",
                "intensity": "Moderate to vigorous based on fitness level",
                "precautions": [
                    "Consult healthcare provider before starting new exercise program",
                    "Start slowly and progress gradually",
                    "Listen to your body"
                ],
                "progression": ["Gradual increase in duration and intensity"]
            }
        }
    
    def _initialize_stress_management(self) -> Dict:
        """Initialize stress management recommendations."""
        return {
            "diabetes": {
                "techniques": [
                    "Deep breathing exercises (4-7-8 technique)",
                    "Progressive muscle relaxation",
                    "Regular physical activity",
                    "Meditation or mindfulness practice",
                    "Support groups for diabetes management"
                ],
                "relaxation": [
                    "Yoga or tai chi",
                    "Guided imagery",
                    "Listening to calming music",
                    "Nature walks"
                ],
                "resources": [
                    "Diabetes support groups",
                    "Mental health counseling if needed",
                    "Online stress management apps",
                    "Community wellness programs"
                ],
                "mindfulness": [
                    "Practice mindful eating",
                    "Daily meditation (10-20 minutes)",
                    "Gratitude journaling"
                ],
                "work_life_tips": [
                    "Set boundaries between work and personal time",
                    "Take regular breaks during work",
                    "Prioritize self-care activities"
                ]
            },
            "heart_disease": {
                "techniques": [
                    "Cardiac coherence breathing",
                    "Mindfulness meditation",
                    "Gentle yoga",
                    "Biofeedback therapy",
                    "Cognitive behavioral therapy if needed"  
                ],
                "relaxation": [
                    "Progressive muscle relaxation",
                    "Guided visualization",
                    "Gentle stretching",
                    "Aromatherapy"
                ],
                "resources": [
                    "Cardiac rehabilitation programs (include stress management)",
                    "Heart disease support groups",
                    "Mental health professional specializing in cardiac issues",
                    "Stress reduction classes"
                ],
                "mindfulness": [
                    "Daily meditation practice",
                    "Mindful walking",
                    "Body scan meditation","Gratitude practice"
                ],
                "work_life_tips": [
                    "Reduce work stress where possible",
                    "Learn to say no to excessive commitments",
                    "Schedule regular relaxation time"
                ]
            },
            "default": {
                "techniques": [
                    "Deep breathing exercises",
                    "Meditation",
                    "Regular physical activity",
                    "Time management",
                    "Social connection"
                ],
                "relaxation": [
                    "Reading",
                    "Hobbies",
                    "Music",
                    "Nature time"
                ],
                "resources": [
                    "Mental health counseling",
                    "Stress management courses",
                    "Support groups",
                    "Wellness apps"
                ],
                "mindfulness": [
                    "Daily meditation",
                    "Mindful breathing",
                    "Present moment awareness"
                ],
                "work_life_tips": [
                    "Set healthy boundaries",
                    "Take regular breaks",
                    "Prioritize self-care"
                ]
            }
        }
    
    def _initialize_preventive_care(self) -> Dict:
        """Initialize preventive care guidelines."""
        return {
            "diabetes": {
                "screenings": [
                    "HbA1c test every 3 months (if not at goal) or every 6 months (if at goal)",
                    "Comprehensive foot exam annually",
                    "Dilated eye exam annually",
                    "Kidney function tests (urine albumin, serum creatinine) annually",
                    "Lipid panel annually"
                ],
                "vaccinations": [
                    "Annual flu vaccine",
                    "Pneumococcal vaccine",
                    "Hepatitis B vaccine series",
                    "COVID-19vaccine per current guidelines"
                ],
                "checkups": "Regular visits with primary care physician (at least 2-4 times per year)",
                "home_monitoring": [
                    "Daily blood glucose monitoring",
                    "Weekly weight checks",
                    "Daily foot inspection",
                    "Blood pressure monitoring"
                ],
                "specialists": [
                    "Endocrinologist",
                    "Ophthalmologist",
                    "Podiatrist",
                    "Diabetes educator"
                ]
            },
            "heart_disease": {
                "screenings": [
                    "Blood pressure check at every visit",
                    "Lipid panel annually or more frequently",
                    "EKG as recommended by cardiologist",
                    "Echocardiogram or stress test as recommended",
                    "Coronary calcium score if indicated"
                ],
                "vaccinations": [
                    "Annual flu vaccine",
                    "Pneumococcal vaccine",
                    "COVID-19 vaccine per guidelines"
                ],
                "checkups": "Regular cardiology visits (frequency based on condition severity)",
                "home_monitoring": [
                    "Daily blood pressure monitoring",
                    "Daily weight (report sudden changes)",
                    "Monitor symptoms (chest pain, shortness of breath)",
                    "Medication adherence tracking"
                ],
                "specialists": [
                    "Cardiologist",
                    "Cardiac rehabilitation team"
                ]
            },
            "hypertension": {
                "screenings": [
                    "Blood pressure checks regularly (home and clinical)",
                    "Lipid panel annually",
                    "Kidney function tests annually",
                    "Blood glucose or HbA1c annually",
                    "EKG if recommended"
                ],
                "vaccinations": [
                    "Standard adult vaccinations",
                    "Annual flu vaccine",
                    "COVID-19 vaccine"
                ],
                "checkups": "Regular primary care visits (initially monthly, then every 3-6 months when stable)",
                "home_monitoring": [
                    "Daily or regular blood pressure monitoring",
                    "Weekly weight checks",
                    "Track medication adherence"
                ],
                "specialists": [
                    "Cardiologist if BP difficult to control"
                ]
            },
            "default": {
                "screenings": [
                    "Annual physical examination",
                    "Age-appropriate cancer screenings",
                    "Blood pressure check",
                    "Cholesterol screening",
                    "Diabetes screening if at risk"
                ],
                "vaccinations": [
                    "Keep up-to-date with recommended adult vaccines"
                ],
                "checkups": "Annual preventive care visit with primary care physician",
                "home_monitoring": [
                    "Monitor overall health and wellbeing",
                    "Track any new or changing symptoms"
                ]
            }
        }
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """Get summary of lifestyle modification agent capabilities."""
        return {
            "agent_type": "LifestyleModificationAgent",
            "features": [
                "Personalized diet recommendations",
                "Exercise guidance based on condition",
                "Stress management techniques",
                "Sleep hygiene recommendations",
                "Preventive care guidelines",
                "Risk mitigation strategies",
                "Priority lifestyle changes"
            ],
            "supported_conditions": list(self.diet_recommendations.keys()),
            "disclaimer_included": True
        }

# =================================================================================================
# 7. Reflection Agent
# =================================================================================================

logger_reflection = logging.getLogger('health_ai.reflection')


class ReflectionAgent(BaseHealthAgent):
    """
    Hidden quality assurance agent for cross-verification of health assessments.
    
    This agent runs as the final step before user delivery to ensure:
    - Safety (emergency detection, appropriate urgency)
    - Quality (logical consistency, accurate confidence)
    - Responsibility (proper disclaimers, medical hedging)
    """
    
    # Confidence thresholds for verification
    CONFIDENCE_THRESHOLDS = {
        "LOW": 0.55,
        "MEDIUM": 0.75,
        "HIGH": 0.75
    }
    
    # Emergency symptoms requiring immediate care
    EMERGENCY_SYMPTOMS = [
        "severe chest pain",
        "chest pain",
        "difficulty breathing",
        "shortness of breath",
        "loss of consciousness",
        "unconscious",
        "severe bleeding",
        "heavy bleeding",
        "stroke symptoms",
        "slurred speech",
        "facial drooping",
        "severe head injury",
        "head trauma",
        "seizure",
        "severe abdominal pain",
        "coughing blood",
        "vomiting blood",
        "sudden confusion",
        "sudden severe headache",
        "high fever with stiff neck"
    ]
    
    # Prohibited definitive phrases (medical AI should not diagnose)
    PROHIBITED_PHRASES = [
        "you have",
        "you are diagnosed with",
        "this is definitely",
        "you definitely have",
        "you must take",
        "you need to take",
        "this confirms",
        "confirmed diagnosis"
    ]
    
    # Required disclaimer elements
    REQUIRED_ELEMENTS = [
        "not a substitute",
        "consult",
        "healthcare professional",
        "medical advice"
    ]
    
    def __init__(self):
        """Initialize the reflection agent."""
        super().__init__("ReflectionAgent")
        logger_reflection.info("ReflectionAgent initialized for quality assurance")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method - verify a complete assessment.
        
        Args:
            input_data: Complete assessment to verify
            
        Returns:
            Verification result with any issues and corrections
        """
        try:
            result = self.verify_assessment(input_data)
            
            return self.format_agent_response(
                success=True,
                data=result,
                message="Assessment verification completed"
            )
            
        except Exception as e:
            logger_reflection.error(f"Reflection agent error: {str(e)}")
            return self.format_agent_response(
                success=False,
                message=f"Verification error: {str(e)}",
                data={"error": str(e)}
            )
    
    def verify_assessment(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cross-verify complete assessment for quality and safety.
        
        Args:
            assessment: Complete assessment with prediction, explanation, recommendations
            
        Returns:
            Verification result with issues, severity, and revised assessment if needed
        """
        verification_start = datetime.utcnow()
        
        logger_reflection.info("Starting cross-verification of assessment")
        
        # Extract components
        prediction = assessment.get("prediction", {})
        explanation = assessment.get("explanation", {})
        recommendations = assessment.get("recommendations", {})
        lifestyle = assessment.get("lifestyle_recommendations", {})
        symptoms = assessment.get("symptoms", [])
        
        # Run all verification checks
        all_issues = []
        
        # Check 1: Confidence verification
        confidence_issues = self._verify_confidence_level(
            prediction, explanation, symptoms
        )
        all_issues.extend(confidence_issues)
        
        # Check 2: Red flag detection (emergency symptoms)
        red_flag_issues = self._detect_red_flags(
            symptoms, recommendations
        )
        all_issues.extend(red_flag_issues)
        
        # Check 3: Logical consistency
        consistency_issues = self._check_logical_consistency(
            prediction, explanation, recommendations
        )
        all_issues.extend(consistency_issues)
        
        # Check 4: Medical claim verification
        claim_issues = self._verify_medical_claims(
            explanation, recommendations
        )
        all_issues.extend(claim_issues)
        
        # Determine overall severity
        severity = self._determine_severity(all_issues)
        
        # Determine recommended action
        recommended_action = self._determine_action(severity, all_issues)
        
        # Apply auto-corrections if needed
        revised_assessment = assessment
        if recommended_action in ["revise", "escalate"]:
            revised_assessment = self._revise_assessment(assessment, all_issues)
        
        verification_end = datetime.utcnow()
        verification_time = (verification_end - verification_start).total_seconds()
        
        # Log results
        self._log_verification_results(all_issues, severity, recommended_action)
        
        return {
            "verification_passed": len(all_issues) == 0,
            "issues_found": all_issues,
            "issue_count": len(all_issues),
            "severity": severity,
            "recommended_action": recommended_action,
            "revised_assessment": revised_assessment,
            "verification_metadata": {
                "verified": True,
                "verification_time_ms": round(verification_time * 1000, 2),
                "agent_version": "v1.0",
                "timestamp": verification_end.isoformat()
            }
        }
    
    def _verify_confidence_level(self, prediction: Dict, explanation: Dict, 
                                 symptoms: List[str]) -> List[Dict]:
        """
        Verify confidence level is appropriate for evidence.
        
        Checks:
        - Confidence aligns with probability threshold
        - Sufficient symptoms for high confidence
        - No overconfidence with weak evidence
        """
        issues = []
        
        confidence = prediction.get("confidence", "MEDIUM")
        probability = prediction.get("probability", 0.5)
        
        # Check probability-confidence alignment
        if confidence == "HIGH" and probability < self.CONFIDENCE_THRESHOLDS["HIGH"]:
            issues.append({
                "type": "overconfidence",
                "severity": "major",
                "component": "confidence_level",
                "message": f"HIGH confidence with probability {probability:.2f} below threshold {self.CONFIDENCE_THRESHOLDS['HIGH']}",
                "current_value": confidence,
                "recommended_value": "MEDIUM",
                "action": "downgrade_confidence"
            })
        
        # Check sufficient evidence for high confidence
        if confidence == "HIGH" and len(symptoms) < 3:
            issues.append({
                "type": "insufficient_evidence",
                "severity": "major",
                "component": "confidence_level",
                "message": f"HIGH confidence with only {len(symptoms)} symptom(s)",
                "action": "downgrade_confidence",
                "recommended_value": "MEDIUM"
            })
        
        # Check for low confidence with high probability (underconfidence)
        if confidence == "LOW" and probability >= self.CONFIDENCE_THRESHOLDS["MEDIUM"]:
            issues.append({
                "type": "underconfidence",
                "severity": "minor",
                "component": "confidence_level",
                "message": f"LOW confidence with probability {probability:.2f} suggests MEDIUM",
                "action": "upgrade_confidence",
                "recommended_value": "MEDIUM"
            })
        
        return issues
    
    def _detect_red_flags(self, symptoms: List[str], 
                         recommendations: Dict) -> List[Dict]:
        """
        Detect emergency symptoms and verify appropriate response.
        
        Checks:
        - Emergency symptoms present in input
        - Immediate care warning included
        - Urgency level appropriate
        """
        issues = []
        
        # Check for emergency symptoms
        emergency_detected = []
        symptoms_text = " ".join(str(s).lower() for s in symptoms)
        
        for emergency in self.EMERGENCY_SYMPTOMS:
            if emergency in symptoms_text:
                emergency_detected.append(emergency)
        
        if not emergency_detected:
            return issues  # No red flags
        
        # Emergency symptoms detected - verify response
        immediate_actions = recommendations.get("immediate_actions", {})
        actions_list = immediate_actions.get("actions", [])
        actions_text = " ".join(str(a).lower() for a in actions_list)
        
        # Check if emergency warning present
        has_emergency_warning = any([
            "immediate emergency" in actions_text,
            "emergency care" in actions_text,
            "911" in actions_text,
            immediate_actions.get("emergency_warning", False)
        ])
        
        if not has_emergency_warning:
            issues.append({
                "type": "missing_emergency_warning",
                "severity": "critical",
                "component": "recommendations",
                "message": f"Emergency symptoms detected ({', '.join(emergency_detected)}) but no immediate care warning",
                "emergency_symptoms": emergency_detected,
                "action": "add_emergency_warning",
                "required_text": "⚠️ SEEK IMMEDIATE EMERGENCY MEDICAL CARE"
            })
        
        # Check urgency level
        referral = recommendations.get("professional_referral", {})
        urgency = referral.get("urgency", "moderate")
        
        if urgency not in ["high", "immediate", "emergency"]:
            issues.append({
                "type": "inappropriate_urgency",
                "severity": "critical",
                "component": "referral_urgency",
                "message": f"Emergency symptoms but urgency is '{urgency}'",
                "action": "upgrade_urgency",
                "recommended_value": "immediate_emergency"
            })
        
        return issues
    
    def _check_logical_consistency(self, prediction: Dict, explanation: Dict,
                                   recommendations: Dict) -> List[Dict]:
        """
        Verify logical consistency between assessment components.
        
        Checks:
        - Explanation matches predicted disease
        - Recommendations align with confidence
        - Urgency matches confidence level
        """
        issues = []
        
        disease = prediction.get("disease", "").lower()
        confidence = prediction.get("confidence", "MEDIUM")
        
        # Check explanation-prediction alignment
        explanation_text = str(explanation.get("main_explanation", "")).lower()
        
        # Extract disease mentions from explanation
        if disease and disease not in explanation_text.replace("_", " "):
            # Disease name should appear in explanation
            issues.append({
                "type": "explanation_disease_mismatch",
                "severity": "major",
                "component": "explanation",
                "message": f"Predicted disease '{disease}' not clearly discussed in explanation",
                "action": "verify_disease_match"
            })
        
        # Check confidence-urgency alignment
        referral = recommendations.get("professional_referral", {})
        urgency = referral.get("urgency", "moderate")
        
        if confidence == "HIGH" and urgency == "non-urgent":
            issues.append({
                "type": "confidence_urgency_mismatch",
                "severity": "minor",
                "component": "referral_urgency",
                "message": "HIGH confidence should not have 'non-urgent' referral",
                "action": "upgrade_urgency",
                "recommended_value": "high"
            })
        
        if confidence == "LOW" and urgency == "high":
            issues.append({
                "type": "confidence_urgency_mismatch",
                "severity": "minor",
                "component": "referral_urgency",
                "message": "LOW confidence with 'high' urgency is inconsistent",
                "action": "moderate_urgency"
            })
        
        return issues
    
    def _verify_medical_claims(self, explanation: Dict, 
                               recommendations: Dict) -> List[Dict]:
        """
        Verify appropriate medical hedging and disclaimers.
        
        Checks:
        - No definitive diagnostic statements
        - Required disclaimer elements present
        - Appropriate hedging language used
        """
        issues = []
        
        # Combine all text for checking
        full_text = str(explanation) + str(recommendations)
        full_text_lower = full_text.lower()
        
        # Check for prohibited definitive statements
        for phrase in self.PROHIBITED_PHRASES:
            if phrase in full_text_lower:
                issues.append({
                    "type": "definitive_claim",
                    "severity": "critical",
                    "component": "medical_claims",
                    "message": f"Inappropriate definitive statement: '{phrase}'",
                    "prohibited_phrase": phrase,
                    "action": "add_hedging",
                    "recommendation": "Rephrase with 'may have', 'risk for', 'could indicate'"
                })
        
        # Check for required disclaimer elements
        disclaimers = recommendations.get("disclaimers", {})
        disclaimer_text = str(disclaimers).lower()
        
        missing_elements = []
        for required in self.REQUIRED_ELEMENTS:
            if required not in disclaimer_text and required not in full_text_lower:
                missing_elements.append(required)
        
        if missing_elements:
            issues.append({
                "type": "missing_disclaimer_elements",
                "severity": "major",
                "component": "disclaimers",
                "message": f"Missing required disclaimer elements: {', '.join(missing_elements)}",
                "missing_elements": missing_elements,
                "action": "ensure_disclaimers"
            })
        
        return issues
    
    def _determine_severity(self, issues: List[Dict]) -> str:
        """Determine overall severity from all issues."""
        if not issues:
            return "none"
        
        severities = [issue.get("severity", "minor") for issue in issues]
        
        if "critical" in severities:
            return "critical"
        elif "major" in severities:
            return "major"
        elif "minor" in severities:
            return "minor"
        else:
            return "none"
    
    def _determine_action(self, severity: str, issues: List[Dict]) -> str:
        """Determine recommended action based on severity."""
        if severity == "none":
            return "proceed"
        elif severity == "minor":
            return "proceed_with_log"
        elif severity == "major":
            return "revise"
        elif severity == "critical":
            return "escalate"
        else:
            return "proceed"
    
    def _revise_assessment(self, assessment: Dict, issues: List[Dict]) -> Dict:
        """
        Automatically revise assessment to address identified issues.
        
        Applies auto-corrections for:
        - Confidence adjustments
        - Emergency warnings
        - Urgency upgrades
        """
        revised = assessment.copy()
        corrections_made = []
        
        for issue in issues:
            action = issue.get("action", "")
            
            # Handle overconfidence
            if action == "downgrade_confidence":
                if "prediction" in revised:
                    old_confidence = revised["prediction"].get("confidence")
                    revised["prediction"]["confidence"] = issue.get("recommended_value", "MEDIUM")
                    corrections_made.append(f"Confidence: {old_confidence} → {revised['prediction']['confidence']}")
                    logger_reflection.warning(f"Auto-corrected: {issue['message']}")
            
            # Handle underconfidence
            elif action == "upgrade_confidence":
                if "prediction" in revised:
                    old_confidence = revised["prediction"].get("confidence")
                    revised["prediction"]["confidence"] = issue.get("recommended_value", "MEDIUM")
                    corrections_made.append(f"Confidence: {old_confidence} → {revised['prediction']['confidence']}")
            
            # Handle missing emergency warning
            elif action == "add_emergency_warning":
                if "recommendations" in revised:
                    immediate = revised["recommendations"].get("immediate_actions", {})
                    actions = immediate.get("actions", [])
                    
                    # Add emergency warning at the top
                    emergency_text = issue.get("required_text", "⚠️ SEEK IMMEDIATE EMERGENCY MEDICAL CARE")
                    if emergency_text not in str(actions):
                        actions.insert(0, emergency_text)
                        immediate["actions"] = actions
                        immediate["emergency_warning"] = True
                        immediate["emergency_symptoms"] = issue.get("emergency_symptoms", [])
                        revised["recommendations"]["immediate_actions"] = immediate
                        corrections_made.append("Added emergency care warning")
                        logger_reflection.critical(f"Emergency warning added: {issue['message']}")
            
            # Handle urgency upgrades
            elif action in ["upgrade_urgency", "moderate_urgency"]:
                if "recommendations" in revised and "professional_referral" in revised["recommendations"]:
                    referral = revised["recommendations"]["professional_referral"]
                    old_urgency = referral.get("urgency")
                    new_urgency = issue.get("recommended_value", "high")
                    referral["urgency"] = new_urgency
                    referral["timeframe"] = "immediately" if new_urgency in ["immediate_emergency", "emergency"] else "as soon as possible"
                    corrections_made.append(f"Urgency: {old_urgency} → {new_urgency}")
        
        # Add verification metadata to revised assessment
        if corrections_made:
            revised["_verification_info"] = {
                "auto_corrected": True,
                "corrections_applied": corrections_made,
                "issues_addressed": len(issues),
                "correction_timestamp": datetime.utcnow().isoformat()
            }
        
        return revised
    
    def _log_verification_results(self, issues: List[Dict], severity: str, 
                                  action: str):
        """Log verification results for monitoring."""
        if not issues:
            logger_reflection.info("✓ Assessment verified: No issues found")
        else:
            issue_summary = {}
            for issue in issues:
                issue_type = issue.get("type", "unknown")
                issue_summary[issue_type] = issue_summary.get(issue_type, 0) + 1
            
            log_message = (
                f"Assessment verification: {len(issues)} issue(s) found "
                f"(severity: {severity}, action: {action}) - "
                f"Issues: {issue_summary}"
            )
            
            if severity == "critical":
                logger_reflection.critical(log_message)
            elif severity == "major":
                logger_reflection.error(log_message)
            elif severity == "minor":
                logger_reflection.warning(log_message)
            else:
                logger_reflection.info(log_message)
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """Get summary of reflection agent capabilities."""
        return {
            "agent": "ReflectionAgent",
            "purpose": "Quality assurance and safety verification",
            "verification_checks": [
                "Confidence level appropriateness",
                "Emergency symptom detection",
                "Logical consistency",
                "Medical claim hedging"
            ],
            "auto_corrections": [
                "Confidence adjustments",
                "Emergency warning addition",
                "Urgency level upgrades"
            ],
            "severity_levels": ["none", "minor", "major", "critical"],
            "actions": ["proceed", "proceed_with_log", "revise", "escalate"]
        }

# =================================================================================================
# 8. Recommendation Agent
# =================================================================================================

logger_recommendation = logging.getLogger('health_ai.recommendation')


class RecommendationAgent:
    """
    Ethical gating agent for treatment recommendations and professional referrals.
    
    Key responsibilities:
    - Apply confidence-based treatment gating
    - Ensure appropriate professional referrals
    - Add safety disclaimers
    - Prevent inappropriate medical advice
    """
    
    def __init__(self):
        """Initialize the recommendation agent."""
        self.treatment_kb = TreatmentKnowledgeBase()
        self.treatment_explorer = TreatmentExplorationAgent()  # NEW: Detailed treatment exploration
        
        # Confidence-based gating rules
        self.confidence_gates = {
            "LOW": {
                "allow_treatment_info": False,
                "referral_urgency": "routine",
                "message": "Please consult with a healthcare professional for proper evaluation"
            },
            "MEDIUM": {
                "allow_treatment_info": True,
                "referral_urgency": "recommended",
                "message": "We recommend discussing these symptoms with a healthcare professional"
            },
            "HIGH": {
                "allow_treatment_info": True,
                "referral_urgency": "strongly_recommended",
                "message": "We strongly recommend consulting with a healthcare professional promptly"
            }
        }
        
        # Professional referral templates
        self.referral_templates = {
            "routine": {
                "message": "Consider scheduling a routine appointment with your healthcare provider to discuss these symptoms.",
                "urgency": "non-urgent",
                "timeframe": "within a few weeks"
            },
            "recommended": {
                "message": "We recommend scheduling an appointment with your healthcare provider to evaluate these symptoms.",
                "urgency": "moderate",
                "timeframe": "within a week"
            },
            "strongly_recommended": {
                "message": "We strongly recommend consulting with a healthcare professional promptly for proper evaluation and care.",
                "urgency": "high",
                "timeframe": "as soon as possible"
            }
        }
        
        logger_recommendation.info("RecommendationAgent initialized")
    
    def allow_treatment(self, confidence: str) -> bool:
        """
        Ethical gate - only allow treatment info for sufficient confidence.
        
        Args:
            confidence: Confidence level (LOW, MEDIUM, HIGH)
            
        Returns:
            Boolean indicating if treatment information should be provided
        """
        gate_info = self.confidence_gates.get(confidence, self.confidence_gates["LOW"])
        allowed = gate_info["allow_treatment_info"]
        
        logger_recommendation.info(f"Treatment information {'allowed' if allowed else 'blocked'} for {confidence} confidence")
        return allowed
    
    def get_recommendations(self, disease: str, probability: float, confidence: str, 
                          symptoms: List[str], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate comprehensive recommendations based on assessment results.
        
        Args:
            disease: The assessed disease/condition
            probability: Risk probability (0.0 to 1.0)
            confidence: Confidence level
            symptoms: List of user symptoms
            user_context: Optional additional user context
            
        Returns:
            Dictionary containing recommendations and referral information
        """
        logger_recommendation.info(f"Generating recommendations for {disease} with {confidence} confidence")
        
        try:
            recommendations = {
                "assessment_summary": {
                    "disease": disease.replace("_", " ").title(),
                    "probability": probability,
                    "confidence": confidence,
                    "assessment_date": datetime.utcnow().isoformat()
                },
                "treatment_information": self._get_treatment_recommendations(disease, confidence),
                "professional_referral": self._get_professional_referral(confidence, disease, probability),
                "immediate_actions": self._get_immediate_actions(confidence, symptoms),
                "follow_up_guidance": self._get_follow_up_guidance(confidence, disease),
                "disclaimers": self._get_comprehensive_disclaimers(),
                "generated_by": "recommendation_agent"
            }
            
            logger_recommendation.info("Recommendations generated successfully")
            return recommendations
            
        except Exception as e:
            logger_recommendation.error(f"Error generating recommendations: {str(e)}")
            return self._get_fallback_recommendations(disease, confidence)
    
    def _get_treatment_recommendations(self, disease: str, confidence: str) -> Dict[str, Any]:
        """Get treatment recommendations based on confidence level."""
        if not self.allow_treatment(confidence):
            return {
                "available": False,
                "reason": "Confidence level too low for treatment information",
                "alternative": "Please consult with healthcare professionals for treatment guidance"
            }
        
        # Get treatment information from knowledge base
        treatment_info = self.treatment_kb.format_treatment_response(disease, confidence)
        
        if treatment_info["available"]:
            # Add recommendation-specific context
            treatment_info["recommendation_context"] = {
                "confidence_level": confidence,
                "suitability_note": (
                    "Treatment approaches may vary in effectiveness for different individuals. "
                    "Professional guidance is essential for selecting appropriate treatments."
                ),
                "integration_note": (
                    "Different medical systems can often be integrated under professional supervision. "
                    "Discuss with qualified practitioners before combining approaches."
                )
            }
            
            # Add detailed treatment exploration for MEDIUM and HIGH confidence
            if confidence in ["MEDIUM", "HIGH"]:
                try:
                    exploration_input = {
                        "disease": disease,
                        "systems": ["all"],
                        "user_context": {}
                    }
                    exploration_result = self.treatment_explorer.process(exploration_input)
                    
                    if exploration_result.get("success", False):
                        treatment_info["detailed_exploration"] = {
                            "available": True,
                            "explore_options": exploration_result.get("data", {})
                        }
                except Exception as e:
                    logger_recommendation.warning(f"Failed to add treatment exploration: {str(e)}")
                    treatment_info["detailed_exploration"] = {
                        "available": False,
                        "message": "Detailed exploration temporarily unavailable"
                    }
        
        return treatment_info
    
    def _get_professional_referral(self, confidence: str, disease: str, probability: float) -> Dict[str, Any]:
        """Generate professional referral recommendations."""
        gate_info = self.confidence_gates.get(confidence, self.confidence_gates["MEDIUM"])
        referral_info = self.referral_templates.get(gate_info["referral_urgency"])
        
        # Disease-specific referral suggestions
        specialist_suggestions = {
            "diabetes": ["Endocrinologist", "Primary Care Physician", "Diabetes Educator"],
            "heart_disease": ["Cardiologist", "Primary Care Physician", "Cardiac Rehabilitation Specialist"],
            "hypertension": ["Primary Care Physician", "Cardiologist", "Hypertension Specialist"]
        }
        
        return {
            "urgency": referral_info["urgency"],
            "timeframe": referral_info["timeframe"],
            "message": referral_info["message"],
            "suggested_specialists": specialist_suggestions.get(disease, ["Primary Care Physician"]),
            "preparation_tips": [
                "List all current symptoms and when they started",
                "Bring any previous medical records or test results",
                "List current medications and supplements",
                "Prepare questions about your symptoms and concerns",
                "Consider bringing a family member or friend for support"
            ],
            "questions_to_ask": [
                "What could be causing these symptoms?",
                "What tests or evaluations do you recommend?",
                "What are my treatment options?",
                "How can I monitor my condition at home?",
                "When should I schedule follow-up appointments?"
            ]
        }
    
    def _get_immediate_actions(self, confidence: str, symptoms: List[str]) -> Dict[str, Any]:
        """Get immediate actions based on confidence and symptoms."""
        immediate_actions = {
            "LOW": [
                "Monitor symptoms and note any changes",
                "Maintain a symptom diary",
                "Continue normal activities unless symptoms worsen",
                "Schedule routine healthcare appointment if symptoms persist"
            ],
            "MEDIUM": [
                "Monitor symptoms closely and document changes",
                "Avoid activities that worsen symptoms",
                "Schedule healthcare appointment within a week",
                "Consider lifestyle modifications that may help",
                "Seek immediate care if symptoms significantly worsen"
            ],
            "HIGH": [
                "Seek healthcare consultation promptly",
                "Monitor symptoms closely and document any changes",
                "Avoid strenuous activities until evaluated",
                "Have emergency contact information readily available",
                "Seek immediate emergency care if symptoms become severe"
            ]
        }
        
        # Add symptom-specific emergency warnings
        emergency_symptoms = [
            "severe chest pain", "difficulty breathing", "severe headache",
            "loss of consciousness", "severe abdominal pain", "high fever"
        ]
        
        has_emergency_symptoms = any(
            any(emergency in symptom.lower() for emergency in emergency_symptoms)
            for symptom in symptoms
        )
        
        actions = immediate_actions.get(confidence, immediate_actions["MEDIUM"])
        
        if has_emergency_symptoms:
            actions.insert(0, "⚠️ SEEK IMMEDIATE EMERGENCY MEDICAL CARE if experiencing severe symptoms")
        
        return {
            "actions": actions,
            "emergency_warning": has_emergency_symptoms,
            "emergency_contact": "Call emergency services (911) for severe or life-threatening symptoms"
        }
    
    def _get_follow_up_guidance(self, confidence: str, disease: str) -> Dict[str, Any]:
        """Get follow-up guidance based on assessment."""
        follow_up_schedules = {
            "LOW": {
                "initial_follow_up": "4-6 weeks if symptoms persist",
                "monitoring_frequency": "As needed based on symptom changes",
                "reassessment": "If symptoms worsen or new symptoms develop"
            },
            "MEDIUM": {
                "initial_follow_up": "1-2 weeks",
                "monitoring_frequency": "Weekly symptom monitoring",
                "reassessment": "If no improvement in 2-3 weeks"
            },
            "HIGH": {
                "initial_follow_up": "Within a few days",
                "monitoring_frequency": "Daily symptom monitoring",
                "reassessment": "Immediate if symptoms worsen"
            }
        }
        
        return follow_up_schedules.get(confidence, follow_up_schedules["MEDIUM"])
    
    def _get_comprehensive_disclaimers(self) -> Dict[str, str]:
        """Get comprehensive disclaimers for recommendations."""
        return {
            "medical_disclaimer": (
                "This assessment and recommendations are for informational and educational "
                "purposes only. They are not intended to be a substitute for professional "
                "medical advice, diagnosis, or treatment. Always seek the advice of your "
                "physician or other qualified health provider with any questions you may "
                "have regarding a medical condition."
            ),
            "treatment_disclaimer": (
                "Treatment information provided represents general educational content about "
                "various medical approaches. Individual treatment plans should always be "
                "developed in consultation with qualified healthcare professionals who can "
                "consider your complete medical history and individual circumstances."
            ),
            "emergency_disclaimer": (
                "This system cannot replace emergency medical services. If you are "
                "experiencing a medical emergency, call emergency services immediately. "
                "Do not rely on this assessment for emergency medical decisions."
            ),
            "accuracy_disclaimer": (
                "While this system uses advanced AI technology, it has limitations and "
                "may not identify all possible conditions or provide complete assessments. "
                "Professional medical evaluation remains essential for accurate diagnosis "
                "and appropriate treatment."
            )
        }
    
    def _get_fallback_recommendations(self, disease: str, confidence: str) -> Dict[str, Any]:
        """Generate fallback recommendations when main generation fails."""
        logger_recommendation.warning("Using fallback recommendations due to generation failure")
        
        return {
            "assessment_summary": {
                "disease": disease.replace("_", " ").title(),
                "confidence": confidence,
                "note": "Detailed recommendations unavailable"
            },
            "treatment_information": {
                "available": False,
                "reason": "Treatment information generation failed",
                "alternative": "Please consult with healthcare professionals for treatment guidance"
            },
            "professional_referral": {
                "urgency": "recommended",
                "message": "We recommend consulting with a healthcare professional for proper evaluation",
                "timeframe": "as soon as convenient"
            },
            "immediate_actions": {
                "actions": [
                    "Consult with a healthcare professional",
                    "Monitor symptoms and document changes",
                    "Seek immediate care if symptoms worsen"
                ]
            },
            "disclaimers": self._get_comprehensive_disclaimers(),
            "generated_by": "fallback_system"
        }
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """Get summary of recommendation agent capabilities."""
        return {
            "confidence_gates": self.confidence_gates,
            "supported_diseases": self.treatment_kb.get_supported_diseases(),
            "supported_systems": self.treatment_kb.get_supported_systems(),
            "features": [
                "Confidence-based treatment gating",
                "Professional referral recommendations",
                "Immediate action guidance",
                "Follow-up scheduling",
                "Comprehensive disclaimers",
                "Emergency symptom detection"
            ],
            "ethical_safeguards": [
                "No treatment information for LOW confidence",
                "Mandatory professional referrals",
                "Emergency symptom warnings",
                "Comprehensive medical disclaimers"
            ]
        }

# =================================================================================================
# 9. Orchestrator Agent
# =================================================================================================

try:
    from backend.prediction.predictor import DiseasePredictor
    from backend.common.firebase_db import get_firebase_db
except ImportError:
    try:
        from prediction.predictor import DiseasePredictor
        from common.firebase_db import get_firebase_db
    except ImportError:
        pass


logger_orchestrator = logging.getLogger('health_ai.orchestrator')


class OrchestratorAgent(BaseHealthAgent):
    """
    Main orchestrator agent coordinating the entire health assessment pipeline.
    
    Pipeline Flow:
    1. Validate input (ValidationAgent)
    2. Extract and map data (DataExtractionAgent + Gemini)
    3. Predict disease (ML Model)
    4. Evaluate confidence
    5. Generate explanation (ExplanationAgent + Gemini)
    6. Generate recommendations (RecommendationAgent)
    7. Store in MongoDB
    8. Return complete assessment
    """
    
    # Confidence thresholds
    CONFIDENCE_THRESHOLDS = {
        "LOW": 0.55,
        "MEDIUM": 0.75
    }
    
    def __init__(self):
        """Initialize the orchestrator agent."""
        super().__init__("OrchestratorAgent")
        
        # Initialize all agents
        self.validation_agent = LangChainValidationAgent()
        self.extraction_agent = DataExtractionAgent()
        self.prediction_engine = DiseasePredictor()
        self.explanation_agent = LangChainExplanationAgent()
        self.recommendation_agent = RecommendationAgent()
        self.lifestyle_agent = LifestyleModificationAgent()
        self.reflection_agent = ReflectionAgent()
        
        # Initialize Firebase database
        self.db = get_firebase_db()
        
        logger_orchestrator.info("OrchestratorAgent initialized with complete pipeline including reflection agent")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method - orchestrates the entire pipeline.
        
        Args:
            input_data: Raw user input
            
        Returns:
            Complete assessment result
        """
        self.log_agent_action("start_pipeline", {"user_id": input_data.get("user_id", "anonymous")})
        
        try:
            # Run the complete pipeline
            result = self.run_pipeline(input_data)
            
            return self.format_agent_response(
                success=True,
                data=result,
                message="Health assessment completed successfully"
            )
            
        except Exception as e:
            logger_orchestrator.error(f"Pipeline error: {str(e)}")
            return self.format_agent_response(
                success=False,
                message=f"Pipeline error: {str(e)}",
                data={"error": str(e)}
            )
    
    def run_pipeline(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete health assessment pipeline.
        
        Args:
            user_input: User input data
            
        Returns:
            Complete assessment result
        """
        pipeline_start = datetime.utcnow()
        user_id = user_input.get("user_id", str(uuid.uuid4()))
        
        logger_orchestrator.info(f"Starting pipeline for user: {user_id}")
        
        # Step 1: Validate Input
        self.log_agent_action("step_1_validation")
        validation_result = self.validation_agent.process(user_input)
        
        if not validation_result["success"]:
            return self._blocked_response(
                "validation_failed",
                validation_result["data"]["reason"],
                validation_result["data"]
            )
        
        sanitized_input = validation_result["data"]["sanitized_input"]
        
        # Step 2: Extract and Map Data using Gemini AI
        self.log_agent_action("step_2_data_extraction")
        
        disease = self._select_disease(sanitized_input["symptoms"])
        
        extraction_input = {
            "symptoms": sanitized_input["symptoms"],
            "age": sanitized_input["age"],
            "gender": sanitized_input["gender"],
            "disease": disease,
            "additional_info": user_input.get("additional_info", {})
        }
        
        extraction_result = self.extraction_agent.process(extraction_input)
        
        if not extraction_result["success"]:
            return self._blocked_response(
                "extraction_failed",
                "Failed to extract features from input",
                extraction_result
            )
        
        extracted_features = extraction_result["data"]["features"]
        extraction_confidence = extraction_result["data"]["extraction_confidence"]
        
        # Step 3: ML Prediction
        self.log_agent_action("step_3_prediction", {"disease": disease})
        
        probability, prediction_metadata = self.prediction_engine.predict(disease, extracted_features)
        
        # Step 4: Evaluate Confidence
        confidence = self._evaluate_confidence(probability)
        
        self.log_agent_action("step_4_confidence_evaluation", {
            "probability": probability,
            "confidence": confidence
        })
        
        # Step 5: Generate Explanation using Gemini
        self.log_agent_action("step_5_explanation_generation")
        
        explanation_input = {
            "disease": disease,
            "probability": probability,
            "confidence": confidence,
            "symptoms": sanitized_input["symptoms"]
        }
        
        explanation_result = self.explanation_agent.process(explanation_input)
        explanation_data = explanation_result["data"] if explanation_result["success"] else {}
        
        # Step 6: Generate Recommendations
        self.log_agent_action("step_6_recommendation_generation")
        
        recommendations = self.recommendation_agent.get_recommendations(
            disease=disease,
            probability=probability,
            confidence=confidence,
            symptoms=sanitized_input["symptoms"],
            user_context={"age": sanitized_input["age"], "gender": sanitized_input["gender"]}
        )
        
        # Step 7: Generate Lifestyle Modifications
        self.log_agent_action("step_7_lifestyle_modifications")
        
        lifestyle_input = {
            "disease": disease,
            "confidence": confidence,
            "symptoms": sanitized_input["symptoms"],
            "user_context": {"age": sanitized_input["age"], "gender": sanitized_input["gender"]}
        }
        
        lifestyle_result = self.lifestyle_agent.process(lifestyle_input)
        lifestyle_recommendations = lifestyle_result["data"] if lifestyle_result["success"] else {}
        
        # Step 8: Cross-Verification (Hidden Quality Check)
        self.log_agent_action("step_8_cross_verification")
        
        # Build complete assessment for verification
        complete_assessment = {
            "prediction": {
                "disease": disease,
                "probability": probability,
                "confidence": confidence
            },
            "explanation": explanation_data,
            "recommendations": recommendations,
            "lifestyle_recommendations": lifestyle_recommendations,
            "symptoms": sanitized_input["symptoms"]
        }
        
        # Run reflection agent verification
        verification_result = self.reflection_agent.verify_assessment(complete_assessment)
        
        # Use revised assessment if corrections were made
        if verification_result["recommended_action"] in ["revise", "escalate"]:
            revised = verification_result["revised_assessment"]
            
            # Extract revised components
            if "_verification_info" in revised:
                logger_orchestrator.warning(f"Assessment auto-corrected: {revised['_verification_info']['corrections_applied']}")
            
            # Update components with corrections
            if "prediction" in revised:
                confidence = revised["prediction"].get("confidence", confidence)
            if "recommendations" in revised:
                recommendations = revised["recommendations"]
        
        # Log critical issues for escalation
        if verification_result["severity"] == "critical":
            logger_orchestrator.critical(f"Critical safety issue detected and corrected: {verification_result['issue_count']} issues")
        
        # Step 9: Store in MongoDB
        self.log_agent_action("step_9_database_storage")
        
        storage_ids = self._store_assessment(
            user_id=user_id,
            sanitized_input=sanitized_input,
            disease=disease,
            probability=probability,
            confidence=confidence,
            extraction_data=extraction_result["data"],
            prediction_metadata=prediction_metadata,
            explanation_data=explanation_data,
            recommendations=recommendations,
            lifestyle_recommendations=lifestyle_recommendations
        )
        
        # Step 10: Build Complete Response
        pipeline_end = datetime.utcnow()
        processing_time = (pipeline_end - pipeline_start).total_seconds()
        
        complete_response = self._build_response(
            user_id=user_id,
            disease=disease,
            probability=probability,
            confidence=confidence,
            extraction_confidence=extraction_confidence,
            explanation=explanation_data,
            recommendations=recommendations,
            lifestyle_recommendations=lifestyle_recommendations,
            storage_ids=storage_ids,
            processing_time=processing_time,
            prediction_metadata=prediction_metadata
        )
        
        logger_orchestrator.info(f"Pipeline completed for user: {user_id} in {processing_time:.2f}s")
        
        return complete_response
    
    def _select_disease(self, symptoms: list) -> str:
        """
        Select the most likely disease based on symptoms.
        
        Args:
            symptoms: List of symptoms
            
        Returns:
            Disease name
        """
        # Simple keyword-based disease selection
        # In production, this could use a more sophisticated classifier
        
        symptom_text = " ".join(symptoms).lower()
        
        diabetes_keywords = ["thirst", "urination", "weight_loss", "fatigue", "hunger"]
        heart_keywords = ["chest_pain", "shortness_of_breath", "heart", "angina"]
        hypertension_keywords = ["headache", "dizziness", "blood_pressure", "hypertension"]
        
        diabetes_score = sum(1 for kw in diabetes_keywords if kw in symptom_text)
        heart_score = sum(1 for kw in heart_keywords if kw in symptom_text)
        hypertension_score = sum(1 for kw in hypertension_keywords if kw in symptom_text)
        
        scores = {
            "diabetes": diabetes_score,
            "heart_disease": heart_score,
            "hypertension": hypertension_score
        }
        
        selected_disease = max(scores, key=scores.get)
        
        # Default to diabetes if no clear match
        if scores[selected_disease] == 0:
            selected_disease = "diabetes"
        
        logger_orchestrator.info(f"Selected disease: {selected_disease} (scores: {scores})")
        return selected_disease
    
    def _evaluate_confidence(self, probability: float) -> str:
        """
        Evaluate confidence level based on probability.
        
        Args:
            probability: Prediction probability
            
        Returns:
            Confidence level (LOW, MEDIUM, HIGH)
        """
        if probability < self.CONFIDENCE_THRESHOLDS["LOW"]:
            return "LOW"
        elif probability < self.CONFIDENCE_THRESHOLDS["MEDIUM"]:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _store_assessment(self, user_id: str, sanitized_input: Dict[str, Any],
                          disease: str, probability: float, confidence: str,
                          extraction_data: Dict[str, Any], prediction_metadata: Dict[str, Any],
                          explanation_data: Dict[str, Any], recommendations: Dict[str, Any],
                          lifestyle_recommendations: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Store complete assessment in Firebase Firestore.
        
        Returns:
            Dictionary of storage IDs
        """
        try:
            # Store complete assessment in one document
            assessment_data = {
                'symptoms': sanitized_input["symptoms"],
                'age': sanitized_input["age"],
                'gender': sanitized_input["gender"],
                'disease': disease,
                'probability': probability,
                'confidence': confidence,
                'extraction_data': extraction_data,
                'prediction_metadata': prediction_metadata,
                'explanation': explanation_data,
                'recommendations': recommendations,
                'lifestyle_recommendations': lifestyle_recommendations or  {}
            }
            
            assessment_id = self.db.store_assessment(user_id, assessment_data)
            
            # Store prediction separately for querying
            prediction_id = self.db.store_prediction(
                user_id=user_id,
                assessment_id=assessment_id,
                prediction_data={
                    'disease': disease,
                    'probability': probability,
                    'confidence': confidence,
                    'model_version': prediction_metadata.get("model_version", "unknown")
                }
            )
            
            # Store explanation
            explanation_id = self.db.store_explanation(
                assessment_id=assessment_id,
                explanation_data=explanation_data
            )
            
            # Store recommendation
            recommendation_id = self.db.store_recommendation(
                assessment_id=assessment_id,
                recommendation_data=recommendations
            )
            
            # Store audit log
            self.db.store_audit_log(
                event_type="health_assessment_completed",
                user_id=user_id,
                payload={
                    "disease": disease,
                    "confidence": confidence,
                    "probability": probability
                }
            )
            
            return {
                "assessment_id": assessment_id,
                "prediction_id": prediction_id,
                "explanation_id": explanation_id,
                "recommendation_id": recommendation_id
            }
            
        except Exception as e:
            logger_orchestrator.error(f"Error storing assessment: {str(e)}")
            return {}
    
    def _build_response(self, user_id: str, disease: str, probability: float,
                        confidence: str, extraction_confidence: float,
                        explanation: Dict[str, Any], recommendations: Dict[str, Any],
                        lifestyle_recommendations: Dict[str, Any],
                        storage_ids: Dict[str, str], processing_time: float,
                        prediction_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Build the complete response for the frontend."""
        return {
            "user_id": user_id,
            "assessment_id": storage_ids.get("prediction_id"),
            "prediction": {
                "disease": disease.replace("_", " ").title(),
                "probability": round(probability, 4),
                "probability_percent": round(probability * 100, 2),
                "confidence": confidence,
                "model_version": prediction_metadata.get("model_version")
            },
            "extraction": {
                "confidence": extraction_confidence,
                "method": "gemini_ai_extraction"
            },
            "explanation": explanation,
            "recommendations": recommendations,
            "lifestyle_recommendations": lifestyle_recommendations,
            "metadata": {
                "processing_time_seconds": round(processing_time, 2),
                "timestamp": datetime.utcnow().isoformat(),
                "storage_ids": storage_ids,
                "pipeline_version": "v1.2"
            }
        }
    
    def _blocked_response(self, reason: str, message: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Build a blocked response when pipeline cannot proceed."""
        return {
            "blocked": True,
            "reason": reason,
            "message": message,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get status of all pipeline components."""
        return {
            "orchestrator": self.get_agent_status(),
            "validation_agent": self.validation_agent.get_agent_status(),
            "extraction_agent": self.extraction_agent.get_agent_status(),
            "explanation_agent": self.explanation_agent.get_agent_status(),
            "prediction_engine": {
                "supported_diseases": self.prediction_engine.get_supported_diseases(),
                "model_version": self.prediction_engine.model_version
            },
            "database": {
                "connected": self.db.db is not None
            }
        }
