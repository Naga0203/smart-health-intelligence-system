import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_agent import BaseHealthAgent

logger_lifestyle = logging.getLogger('health_ai.lifestyle')

class LifestyleModificationAgent(BaseHealthAgent):
    """
    AI agent for generating personalized lifestyle modification recommendations.
    
    Features:
    - Diet planning (Indian/Western context)
    - Exercise recommendations based on mobility and age
    - Stress management techniques
    - Sleep hygiene optimization
    """
    
    def __init__(self):
        """Initialize the lifestyle modification agent."""
        super().__init__("LifestyleModificationAgent")
        
        # Create LangChain chain for lifestyle recommendations
        self.lifestyle_chain = self.create_agent_chain(
            system_prompt="""You are an expert lifestyle and wellness coach specializing in chronic disease management.
            Your role is to provide personalized, actionable lifestyle modifications.
            
            Focus on 4 pillars:
            1. Diet & Nutrition (Culturally appropriate, e.g., Indian context if relevant)
            2. Physical Activity (Safe, age-appropriate)
            3. Stress Management
            4. Sleep Hygiene
            
            Guidelines:
            - Be encouraging and practical
            - Start with small, achievable changes
            - Consider the user's age and condition
            - Provide clear "Do's" and "Don'ts"
            """,
            
            human_prompt="""Create a lifestyle modification plan for a patient with:
            Condition: {disease} (Risk Level: {risk_level})
            Demographics: {age} year old {gender}
            Symptoms: {symptoms}
            
            Provide a structured JSON response with:
            1. diet_plan (list of recommendations)
            2. exercise_plan (list of safe activities)
            3. stress_management (techniques)
            4. sleep_hygiene (tips)
            5. immediate_actions (top 3 priorities)
            """
        )
        
        logger_lifestyle.info("LifestyleModificationAgent initialized")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate lifestyle recommendations.
        
        Args:
            input_data: User data including disease, age, gender, symptoms
            
        Returns:
            Dictionary with lifestyle recommendations
        """
        required_fields = ["disease", "user_context"]
        if not all(field in input_data for field in required_fields):
            return self.get_fallback_response(input_data)
            
        self.log_agent_action("generate_lifestyle_plan", {"disease": input_data["disease"]})
        
        try:
            user_context = input_data["user_context"]
            age = user_context.get("age", 30)
            gender = user_context.get("gender", "unknown")
            symptoms = input_data.get("symptoms", [])
            
            # 1. Try LangChain generation
            if self.lifestyle_chain:
                recommendations = self._generate_with_langchain(
                    disease=input_data["disease"],
                    risk_level=input_data.get("confidence", "MEDIUM"),
                    age=age,
                    gender=gender,
                    symptoms=symptoms
                )
                
                if recommendations:
                    return self.format_agent_response(
                        success=True,
                        data=recommendations,
                        message="Personalized lifestyle plan generated"
                    )
            
            # 2. Fallback to template-based generation
            return self.format_agent_response(
                success=True,
                data=self._generate_template_plan(input_data["disease"], age),
                message="Standard lifestyle plan generated (Fallback)"
            )
            
        except Exception as e:
            logger_lifestyle.error(f"Error generating lifestyle plan: {str(e)}")
            return self.get_fallback_response(input_data)
            
    def _generate_with_langchain(self, disease: str, risk_level: str, age: int, 
                               gender: str, symptoms: List[str]) -> Optional[Dict[str, Any]]:
        """Generate plan using LangChain."""
        try:
            chain_input = {
                "disease": disease,
                "risk_level": risk_level,
                "age": age,
                "gender": gender,
                "symptoms": ", ".join(symptoms) if symptoms else "None specified"
            }
            
            result = self.execute_chain(self.lifestyle_chain, chain_input)
            
            if result:
                # Try to parse JSON result
                try:
                    # Clean up markdown code blocks if present
                    if "```json" in result:
                        result = result.split("```json")[1].split("```")[0].strip()
                    elif "```" in result:
                        result = result.split("```")[1].split("```")[0].strip()
                        
                    return json.loads(result)
                except json.JSONDecodeError:
                    # Return as text if not JSON
                    return {"text_plan": result}
                    
            return None
            
        except Exception as e:
            logger_lifestyle.error(f"LangChain generation failed: {str(e)}")
            return None
            
    def _generate_template_plan(self, disease: str, age: int) -> Dict[str, Any]:
        """Generate template-based plan."""
        # Simplified templates
        templates = {
            "diabetes": {
                "diet_plan": [
                    "Reduce sugar and refined carbs",
                    "Increase fiber intake (vegetables, whole grains)",
                    "Eat at regular intervals",
                    "Stay hydrated"
                ],
                "exercise_plan": [
                    "30 minutes moderate walking daily",
                    "Light resistance training (if approved via doctor)",
                    "Yoga for flexibility"
                ],
                "stress_management": [
                    "Deep breathing exercises",
                    "Meditation (10 mins daily)"
                ],
                "immediate_actions": [
                    "Monitor blood sugar",
                    "Consult dietician",
                    "Check feet daily"
                ]
            }
            # Add other diseases...
        }
        
        return templates.get(disease, templates["diabetes"])  # Default to diabetes
