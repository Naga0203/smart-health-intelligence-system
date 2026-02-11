"""
Treatment Knowledge Base for AI Health Intelligence System

This module contains informational treatment data across multiple medical systems.
All information is educational only and includes appropriate disclaimers.

Validates: Requirements 4.1, 4.3, 4.4
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger('health_ai.treatment')


class TreatmentKnowledgeBase:
    """
    Knowledge base containing treatment information across multiple medical systems.
    
    IMPORTANT CONSTRAINTS:
    - Educational information only
    - No specific prescriptions or dosages
    - No direct medical advice
    - Clear disclaimers for each system
    """
    
    def __init__(self):
        """Initialize the treatment knowledge base."""
        self.treatments = self._initialize_treatment_data()
        logger.info("TreatmentKnowledgeBase initialized")
    
    def _initialize_treatment_data(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive treatment data for supported conditions."""
        return {
            "diabetes": {
                "allopathy": {
                    "approach": "Blood sugar monitoring and medication management",
                    "focus": "Insulin regulation and glucose control through evidence-based medicine",
                    "common_approaches": [
                        "Blood glucose monitoring",
                        "Insulin therapy (Type 1) or oral medications (Type 2)",
                        "Dietary counseling with carbohydrate counting",
                        "Regular HbA1c testing",
                        "Screening for complications"
                    ],
                    "lifestyle_recommendations": [
                        "Regular blood sugar monitoring",
                        "Consistent meal timing",
                        "Regular physical activity",
                        "Weight management",
                        "Foot care and eye exams"
                    ],
                    "disclaimer": "Requires medical supervision and regular monitoring. Medication dosages must be prescribed by qualified physicians."
                },
                "ayurveda": {
                    "approach": "Diet regulation and lifestyle balance based on individual constitution",
                    "focus": "Holistic body constitution (Prakriti) assessment and natural remedies to balance doshas",
                    "common_approaches": [
                        "Constitutional assessment (Vata, Pitta, Kapha)",
                        "Dietary modifications based on Ayurvedic principles",
                        "Herbal formulations like Guduchi, Jamun, Karela",
                        "Panchakarma detoxification therapies",
                        "Yoga and meditation practices"
                    ],
                    "lifestyle_recommendations": [
                        "Regular meal times aligned with natural rhythms",
                        "Specific yoga asanas for diabetes management",
                        "Meditation and stress reduction techniques",
                        "Seasonal dietary adjustments",
                        "Oil massage (Abhyanga) for circulation"
                    ],
                    "disclaimer": "Consult qualified Ayurvedic practitioners. Should complement, not replace, conventional medical care."
                },
                "homeopathy": {
                    "approach": "Individualized symptom-based treatment using highly diluted substances",
                    "focus": "Constitutional remedies based on complete symptom picture and individual characteristics",
                    "common_approaches": [
                        "Detailed case taking including mental and emotional symptoms",
                        "Constitutional remedy selection",
                        "Miasmatic treatment approach",
                        "Potency selection based on individual sensitivity",
                        "Regular follow-up and remedy adjustment"
                    ],
                    "lifestyle_recommendations": [
                        "Stress management and emotional balance",
                        "Regular exercise appropriate to constitution",
                        "Dietary modifications based on individual response",
                        "Adequate sleep and rest",
                        "Avoiding suppressive treatments when possible"
                    ],
                    "disclaimer": "Requires qualified homeopathic consultation. Treatment duration varies by individual. Should be integrated with conventional monitoring."
                },
                "lifestyle": {
                    "approach": "Diet, exercise, and stress management for blood sugar control",
                    "focus": "Preventive care and healthy habits to manage glucose levels naturally",
                    "common_approaches": [
                        "Low glycemic index diet planning",
                        "Regular aerobic and resistance exercise",
                        "Weight management strategies",
                        "Stress reduction techniques",
                        "Sleep hygiene improvement"
                    ],
                    "lifestyle_recommendations": [
                        "Eat balanced meals with complex carbohydrates",
                        "Exercise for at least 150 minutes per week",
                        "Maintain healthy body weight",
                        "Monitor blood sugar regularly",
                        "Stay hydrated and limit processed foods"
                    ],
                    "disclaimer": "General wellness information only. Individual needs may vary. Consult healthcare providers for personalized advice."
                }
            },
            
            "heart_disease": {
                "allopathy": {
                    "approach": "Cardiovascular risk reduction through medication and lifestyle modification",
                    "focus": "Evidence-based treatments to improve heart function and prevent complications",
                    "common_approaches": [
                        "Cardiac risk assessment and monitoring",
                        "Blood pressure and cholesterol management",
                        "Antiplatelet therapy when indicated",
                        "Cardiac rehabilitation programs",
                        "Regular cardiovascular screening"
                    ],
                    "lifestyle_recommendations": [
                        "Heart-healthy diet (Mediterranean or DASH)",
                        "Regular cardiovascular exercise",
                        "Smoking cessation",
                        "Stress management",
                        "Regular blood pressure monitoring"
                    ],
                    "disclaimer": "Requires cardiologist supervision. Emergency symptoms need immediate medical attention."
                },
                "ayurveda": {
                    "approach": "Heart health through circulation improvement and stress reduction",
                    "focus": "Strengthening heart function (Hridaya) and improving circulation through natural methods",
                    "common_approaches": [
                        "Herbs like Arjuna, Pushkarmool for heart strength",
                        "Pranayama (breathing exercises) for circulation",
                        "Meditation for stress and blood pressure reduction",
                        "Dietary modifications for heart health",
                        "Gentle detoxification therapies"
                    ],
                    "lifestyle_recommendations": [
                        "Early morning walks and gentle exercise",
                        "Heart-healthy spices like turmeric and garlic",
                        "Regular meditation and stress reduction",
                        "Adequate sleep (7-8 hours)",
                        "Avoiding excessive salt and processed foods"
                    ],
                    "disclaimer": "Consult qualified Ayurvedic practitioners. Acute cardiac symptoms require immediate conventional medical care."
                },
                "homeopathy": {
                    "approach": "Constitutional treatment addressing underlying cardiovascular susceptibility",
                    "focus": "Individual remedy selection based on complete symptom picture and cardiac symptoms",
                    "common_approaches": [
                        "Constitutional remedies for cardiovascular health",
                        "Acute remedies for specific cardiac symptoms",
                        "Treatment of underlying miasmatic tendencies",
                        "Emotional and mental symptom consideration",
                        "Integration with conventional cardiac monitoring"
                    ],
                    "lifestyle_recommendations": [
                        "Stress reduction and emotional balance",
                        "Gentle, regular exercise",
                        "Heart-healthy dietary choices",
                        "Adequate rest and sleep",
                        "Regular monitoring of cardiac health"
                    ],
                    "disclaimer": "Requires qualified homeopathic consultation. Acute cardiac symptoms need immediate conventional medical attention."
                },
                "lifestyle": {
                    "approach": "Heart-healthy lifestyle modifications for cardiovascular wellness",
                    "focus": "Preventive strategies to maintain heart health and reduce cardiovascular risk",
                    "common_approaches": [
                        "Heart-healthy diet implementation",
                        "Regular cardiovascular exercise program",
                        "Stress management techniques",
                        "Smoking cessation support",
                        "Weight management strategies"
                    ],
                    "lifestyle_recommendations": [
                        "Follow Mediterranean or DASH diet patterns",
                        "Exercise 150 minutes per week (moderate intensity)",
                        "Maintain healthy weight (BMI 18.5-24.9)",
                        "Limit sodium intake to less than 2300mg daily",
                        "Practice stress reduction techniques daily"
                    ],
                    "disclaimer": "General wellness information. Individual cardiovascular risk factors require professional assessment."
                }
            },
            
            "hypertension": {
                "allopathy": {
                    "approach": "Blood pressure control through medication and lifestyle modification",
                    "focus": "Achieving target blood pressure levels to prevent cardiovascular complications",
                    "common_approaches": [
                        "Regular blood pressure monitoring",
                        "Antihypertensive medications as prescribed",
                        "Lifestyle modification counseling",
                        "Cardiovascular risk assessment",
                        "Monitoring for target organ damage"
                    ],
                    "lifestyle_recommendations": [
                        "DASH diet implementation",
                        "Regular aerobic exercise",
                        "Sodium restriction (less than 2300mg daily)",
                        "Weight management",
                        "Limited alcohol consumption"
                    ],
                    "disclaimer": "Requires medical supervision for blood pressure monitoring and medication management."
                },
                "ayurveda": {
                    "approach": "Blood pressure management through stress reduction and circulation improvement",
                    "focus": "Balancing Vata and Pitta doshas to maintain healthy blood pressure naturally",
                    "common_approaches": [
                        "Stress reduction through meditation and yoga",
                        "Herbs like Sarpagandha, Jatamansi for blood pressure",
                        "Dietary modifications to reduce Pitta",
                        "Abhyanga (oil massage) for circulation",
                        "Pranayama for nervous system balance"
                    ],
                    "lifestyle_recommendations": [
                        "Regular meditation and stress management",
                        "Gentle yoga and breathing exercises",
                        "Cooling foods and spices",
                        "Regular sleep schedule",
                        "Avoiding excessive heat and stress"
                    ],
                    "disclaimer": "Consult qualified Ayurvedic practitioners. Regular blood pressure monitoring remains essential."
                },
                "homeopathy": {
                    "approach": "Constitutional treatment addressing hypertensive tendency",
                    "focus": "Individual remedy selection based on complete symptom picture and constitutional type",
                    "common_approaches": [
                        "Constitutional remedies for hypertension",
                        "Treatment of underlying stress and anxiety",
                        "Addressing emotional factors contributing to hypertension",
                        "Miasmatic treatment approach",
                        "Regular monitoring and remedy adjustment"
                    ],
                    "lifestyle_recommendations": [
                        "Stress management and relaxation techniques",
                        "Regular, moderate exercise",
                        "Healthy dietary choices",
                        "Adequate sleep and rest",
                        "Emotional balance and mental health care"
                    ],
                    "disclaimer": "Requires qualified homeopathic consultation. Blood pressure monitoring and conventional care may be necessary."
                },
                "lifestyle": {
                    "approach": "Lifestyle modifications for natural blood pressure management",
                    "focus": "Evidence-based lifestyle changes to reduce blood pressure and cardiovascular risk",
                    "common_approaches": [
                        "DASH diet implementation",
                        "Regular physical activity program",
                        "Weight management strategies",
                        "Stress reduction techniques",
                        "Sodium reduction strategies"
                    ],
                    "lifestyle_recommendations": [
                        "Eat plenty of fruits, vegetables, and whole grains",
                        "Exercise regularly (150 minutes moderate intensity weekly)",
                        "Maintain healthy weight",
                        "Limit sodium to less than 2300mg daily",
                        "Practice stress management techniques"
                    ],
                    "disclaimer": "General wellness information. Blood pressure should be monitored regularly by healthcare professionals."
                }
            }
        }
    
    def get_treatment_info(self, disease: str, confidence: str) -> Optional[Dict[str, Any]]:
        """
        Get treatment information for a specific disease.
        
        Args:
            disease: The disease/condition
            confidence: Confidence level (LOW, MEDIUM, HIGH)
            
        Returns:
            Treatment information dictionary or None if not available
        """
        # Only provide treatment information for MEDIUM and HIGH confidence
        if confidence == "LOW":
            logger.info(f"Treatment information blocked for LOW confidence assessment of {disease}")
            return None
        
        treatment_data = self.treatments.get(disease)
        if not treatment_data:
            logger.warning(f"No treatment information available for {disease}")
            return None
        
        logger.info(f"Providing treatment information for {disease} with {confidence} confidence")
        return treatment_data
    
    def get_system_info(self, system: str, disease: str) -> Optional[Dict[str, Any]]:
        """Get information for a specific treatment system."""
        treatment_data = self.treatments.get(disease, {})
        return treatment_data.get(system)
    
    def get_supported_diseases(self) -> List[str]:
        """Get list of diseases with treatment information."""
        return list(self.treatments.keys())
    
    def get_supported_systems(self) -> List[str]:
        """Get list of supported treatment systems."""
        return ["allopathy", "ayurveda", "homeopathy", "lifestyle"]
    
    def format_treatment_response(self, disease: str, confidence: str) -> Dict[str, Any]:
        """Format treatment information for API response."""
        treatment_info = self.get_treatment_info(disease, confidence)
        
        if not treatment_info:
            return {
                "available": False,
                "reason": "Treatment information not available for this confidence level",
                "recommendation": "Please consult with healthcare professionals for treatment guidance"
            }
        
        formatted_response = {
            "available": True,
            "disease": disease.replace("_", " ").title(),
            "confidence_required": confidence,
            "systems": {},
            "general_disclaimer": (
                "All treatment information is for educational purposes only. "
                "Always consult with qualified healthcare professionals before "
                "starting any treatment. Different medical systems may have "
                "varying approaches and effectiveness for different individuals."
            )
        }
        
        for system, info in treatment_info.items():
            formatted_response["systems"][system] = {
                "name": system.title(),
                "approach": info["approach"],
                "focus": info["focus"],
                "recommendations": info["lifestyle_recommendations"],
                "disclaimer": info["disclaimer"]
            }
        
        return formatted_response
    
    def get_knowledge_base_summary(self) -> Dict[str, Any]:
        """Get summary of the knowledge base."""
        return {
            "supported_diseases": self.get_supported_diseases(),
            "supported_systems": self.get_supported_systems(),
            "total_entries": len(self.treatments),
            "confidence_requirement": "MEDIUM or HIGH confidence required for treatment information",
            "disclaimer": "All information is educational only and requires professional consultation"
        }