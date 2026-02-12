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

# Import cache service for performance optimization
try:
    from common.cache_service import CacheService
    CACHE_ENABLED = True
except ImportError:
    CACHE_ENABLED = False
    logger.warning("Cache service not available, caching disabled for treatment exploration")

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
            
            logger.info(f"Processing treatment exploration for {disease} with confidence {confidence}")
            
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
            logger.error(f"Treatment exploration error: {str(e)}")
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
