"""
Treatment Exploration Agent for AI Health Intelligence System

This agent provides comprehensive, detailed information about treatment options
across multiple medical systems for various diseases.

Systems Covered:
- Allopathy (English/Modern Medicine)
- Homeopathy
- Ayurveda
- Integrative approaches

Validates: Requirements 4.1, 4.3, 4.4
"""

from typing import Dict, Any, List, Optional
import logging
from agents.base_agent import BaseHealthAgent
from treatment.knowledge_base import TreatmentKnowledgeBase

logger = logging.getLogger('health_ai.treatment_exploration')


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
        
        logger.info("TreatmentExplorationAgent initialized")
    
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
                # Similar structure for hypertension treatments
            },
            
            "heart_disease": {
                # Similar structure for heart disease treatments
            }
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method - explore treatment options.
        
        Args:
            input_data: Dict with disease and optional preferences
            
        Returns:
            Treatment exploration result
        """
        try:
            disease = input_data.get("disease")
            systems = input_data.get("systems", ["all"])
            user_context = input_data.get("user_context", {})
            
            result = self.explore_treatments(disease, systems, user_context)
            
            return self.format_agent_response(
                success=True,
                data=result,
                message=f"Treatment options explored for {disease}"
            )
            
        except Exception as e:
            logger.error(f"Treatment exploration error: {str(e)}")
            return self.format_agent_response(
                success=False,
                message=f"Error exploring treatments: {str(e)}",
                data={"error": str(e)}
            )
    
    def explore_treatments(self, disease: str, systems: List[str] = None,
                          user_context: Dict = None) -> Dict[str, Any]:
        """
        Explore comprehensive treatment options for a disease.
        
        Args:
            disease: Disease name
            systems: List of systems to explore ("all" or specific systems)
            user_context: User age, gender, existing conditions, medications
            
        Returns:
            Comprehensive treatment exploration
        """
        if systems is None or "all" in systems:
            systems = ["allopathy", "homeopathy", "ayurveda", "integrative"]
        
        disease_treatments = self.detailed_treatments.get(disease, {})
        
        if not disease_treatments:
            return {
                "disease": disease,
                "available": False,
                "message": "Detailed treatment information not yet available for this condition",
                "general_guidance": "Please consult with healthcare professionals for treatment options"
            }
        
        exploration = {
            "disease": disease.replace("_", " ").title(),
            "systems_explored": systems,
            "treatment_options": {},
            "comparison_summary": self._generate_comparison_summary(disease, systems),
            "general_guidance": self._get_general_guidance(disease),
            "safety_priorities": self._get_safety_priorities(),
            "next_steps": self._get_next_steps(disease, user_context)
        }
        
        # Add details for each requested system
        for system in systems:
            if system in disease_treatments:
                system_data = disease_treatments[system]
                exploration["treatment_options"][system] = {
                    "system_name": system_data.get("system_name"),
                    "primary_goal": system_data.get("primary_goal"),
                    "approach": system_data.get("approach_philosophy", ""),
                    "treatments": system_data.get("treatments", []),
                    "expected_timeline": system_data.get("expected_timeline"),
                    "success_rate": system_data.get("success_rate"),
                    "disclaimer": system_data.get("disclaimer")
                }
                
                # Add complementary practices if available (Ayurveda)
                if "complementary_practices" in system_data:
                    exploration["treatment_options"][system]["complementary_practices"] = system_data["complementary_practices"]
                
                # Add integration notes if available
                if "integration_notes" in system_data:
                    exploration["treatment_options"][system]["integration_notes"] = system_data["integration_notes"]
        
        return exploration
    
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
