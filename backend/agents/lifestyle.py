"""
Lifestyle Modification Agent for AI Health Intelligence System

This agent generates personalized lifestyle recommendations based on health conditions
and risk factors, including diet, exercise, stress management, and preventive care.

Validates: Requirements for comprehensive health guidance
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from agents.base_agent import BaseHealthAgent

logger = logging.getLogger('health_ai.lifestyle')


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
        
        logger.info("LifestyleModificationAgent initialized")
    
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
            logger.error(f"Error in lifestyle recommendation processing: {str(e)}")
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
        logger.info(f"Generating lifestyle recommendations for {disease}")
        
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
        
        logger.info(f"Lifestyle recommendations generated for {disease}")
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
