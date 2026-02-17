import logging
import json
from typing import Dict, Any, Optional, List
from backend.agents.base_agent import BaseHealthAgent
from backend.treatment.knowledge_base import TreatmentKnowledgeBase

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
        pass

# Use a specific logger name
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
                            "name": "Sarpagandha",
                            "category": "Herbal Medicine (Strong)",
                            "mechanism": "Original source of Reserpine - lowers BP centrally",
                            "traditional_use": "Potent herb for high BP and insanity",
                            "effectiveness": "High - Very effective but significant side effects",
                            "evidence_level": "High - Basis for modern drugs",
                            "warning": "Can cause severe depression and nasal congestion. Use ONLY under strict expert supervision.",
                            "administration": "Strict dosage control required"
                        }
                    ],
                    "complementary_practices": {
                        "yoga": [
                            "Shavasana (Corpse Pose) for deep relaxation",
                            "Chandra Bhedana (Left Nostril Breathing)",
                            "Gentle stretching"
                        ],
                        "lifestyle": [
                            "Regular sleep schedule",
                            "Oil massage (Abhyanga)",
                            "Meditation aimed at stress reduction"
                        ],
                        "diet": [
                            "Reduce salt, sour, and pungent foods",
                            "Favor cooling foods",
                            "Hydration"
                        ]
                    },
                    "expected_timeline": "1-3 months for sustainable results",
                    "success_rate": "Moderate - best for stress-related hypertension",
                    "disclaimer": "Consult qualified Ayurvedic practitioners. Severe hypertension requires allopathic management. Do not stop prescribed medications without medical approval."
                },
                
                "integrative": {
                    "system_name": "Integrative Medicine",
                    "approach": "Lifestyle-first approach with medication as support",
                    "protocols": [
                        {
                            "name": "Cardiometabolic Balance Program",
                            "combines": ["Medical Management", "Stress Reduction", "Dietary Approaches"],
                            "components": {
                                "conventional": "Medications as needed for protection",
                                "lifestyle": "DASH diet + Regular movement",
                                "mind_body": "Daily mindfulness/meditation practice",
                                "supplements": "Fish oil, CoQ10, or Magnesium (evidence-based)"
                            },
                            "benefits": [
                                "Reduces reliance on high-dose medications",
                                "Protects end organs",
                                "Improves quality of life"
                            ]
                        }
                    ],
                    "safety_emphasis": "Check interactions between supplements and blood pressure medications.",
                    "disclaimer": "Integrative approach requires coordinated care team."
                }
            }
        }
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user request for treatment information.
        
        Args:
            input_data: Dictionary containing:
                - disease: The disease to explore (required)
                - system: Specific medical system (optional, defaults to all)
                - query: Specific question (optional)
                
        Returns:
            Dictionary with treatment information
        """
        if not self._validate_request(input_data):
            return self.format_agent_response(
                success=False,
                message="Invalid request: 'disease' is required"
            )
            
        disease = input_data.get("disease", "").lower().replace(" ", "_")
        system = input_data.get("system", "all").lower()
        
        self.log_agent_action(f"exploring_treatment", {"disease": disease, "system": system})
        
        try:
            # Check cache if enabled
            if CACHE_ENABLED:
                cached_data = self._get_from_cache(disease, system)
                if cached_data:
                    return self.format_agent_response(
                        success=True,
                        data=cached_data,
                        message="Treatment information retrieved from cache"
                    )
            
            # Get detailed information
            treatment_info = self._get_treatment_info(disease, system)
            
            # Store in cache if enabled
            if CACHE_ENABLED and treatment_info:
                self._cache_result(disease, system, treatment_info)
            
            return self.format_agent_response(
                success=True,
                data=treatment_info,
                message=f"Treatment information retrieved for {disease}"
            )
            
        except Exception as e:
            logger_treatment.error(f"Error processing treatment request: {str(e)}")
            return self.get_fallback_response(input_data)
            
    def _validate_request(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        return input_data and "disease" in input_data
        
    def _get_treatment_info(self, disease: str, system: str) -> Dict[str, Any]:
        """
        Retrieve treatment information from internal database or knowledge base.
        
        Args:
            disease: Disease name
            system: Medical system filter
            
        Returns:
            Treatment information dictionary
        """
        # 1. Try internal comprehensive DB first
        if disease in self.detailed_treatments:
            if system != "all" and system in self.detailed_treatments[disease]:
                return {system: self.detailed_treatments[disease][system]}
            elif system == "all":
                return self.detailed_treatments[disease]
        
        # 2. Fallback to general Knowledge Base
        kb_result = self.treatment_kb.get_treatments(disease)
        if kb_result:
            return kb_result
            
        # 3. Use LLM if no structured data found (and if enabled)
        if self.llm:
            return self._generate_treatment_info(disease, system)
            
        return {"message": "No detailed treatment information found for this condition."}

    def _generate_treatment_info(self, disease: str, system: str) -> Dict[str, Any]:
        """Generate treatment info using LLM as fallback."""
        if not self.treatment_chain:
            self.treatment_chain = self.create_agent_chain(
                system_prompt="You are an expert medical treatment assistant. Provide structured treatment options.",
                human_prompt="Provide comprehensive treatment options for {disease} in {system} system."
            )
            
        result = self.execute_chain(self.treatment_chain, {"disease": disease, "system": system})
        return {"generated_info": result}

    def _get_from_cache(self, disease: str, system: str) -> Optional[Dict[str, Any]]:
        """Retrieve from cache."""
        # Implementation depends on cache service availability
        return None 

    def _cache_result(self, disease: str, system: str, data: Dict[str, Any]):
        """Store result in cache."""
        pass
