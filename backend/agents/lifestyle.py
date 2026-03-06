import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .infrastructure.enhanced_base_agent import EnhancedBaseHealthAgent
from .infrastructure.config import AgentConfig

logger_lifestyle = logging.getLogger('health_ai.lifestyle')

class LifestyleModificationAgent(EnhancedBaseHealthAgent):
    """
    Enhanced AI agent for generating personalized lifestyle modification recommendations.
    
    Key responsibilities:
    - Generate evidence-based lifestyle recommendations using LangChain and Gemini AI
    - Search web for current evidence-based lifestyle interventions
    - Personalize recommendations based on user profile (age, gender, medical history)
    - Replace static lifestyle data with dynamic retrieval
    - Cite sources for all recommendations
    - Apply safety guardrails to all outputs
    - Monitor and track recommendation generation
    
    Features:
    - Diet planning (culturally appropriate, Indian/Western context)
    - Exercise recommendations based on mobility, age, and condition
    - Stress management techniques
    - Sleep hygiene optimization
    - Evidence-based interventions from current medical literature
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the enhanced lifestyle modification agent."""
        super().__init__("LifestyleModificationAgent", config)
        
        # Create LangChain chain for lifestyle recommendations
        self.lifestyle_chain = self.create_agent_chain(
            system_prompt="""You are an expert lifestyle and wellness coach specializing in chronic disease management and evidence-based health interventions.
            Your role is to provide personalized, actionable lifestyle modifications based on current medical evidence.
            
            Focus on 4 pillars:
            1. Diet & Nutrition (Culturally appropriate, e.g., Indian context if relevant)
            2. Physical Activity (Safe, age-appropriate, condition-specific)
            3. Stress Management (Evidence-based techniques)
            4. Sleep Hygiene (Scientifically validated practices)
            
            Guidelines:
            - Base recommendations on current medical evidence and research
            - Be encouraging, practical, and compassionate
            - Start with small, achievable changes
            - Consider the user's age, gender, and medical condition
            - Provide clear "Do's" and "Don'ts"
            - Cite evidence when available from web context
            - Personalize based on user profile
            - Include contraindications and safety considerations
            - Emphasize consulting healthcare professionals for medical decisions
            
            CRITICAL: This is educational guidance, not medical advice. Always recommend professional consultation for medical decisions.
            """,
            
            human_prompt="""Create a personalized, evidence-based lifestyle modification plan for a patient with:

Condition: {disease} (Risk Level: {risk_level})
Demographics: {age} year old {gender}
Symptoms: {symptoms}
Medical History: {medical_history}

{web_context}

Provide a structured JSON response with:
{{
  "diet_plan": [
    {{"recommendation": "specific dietary advice", "evidence": "brief evidence basis", "priority": "high/medium/low"}},
    ...
  ],
  "exercise_plan": [
    {{"activity": "specific exercise", "frequency": "how often", "duration": "how long", "safety_notes": "precautions", "priority": "high/medium/low"}},
    ...
  ],
  "stress_management": [
    {{"technique": "specific technique", "how_to": "brief instructions", "evidence": "brief evidence basis"}},
    ...
  ],
  "sleep_hygiene": [
    {{"tip": "specific sleep tip", "rationale": "why it helps"}},
    ...
  ],
  "immediate_actions": [
    "top 3 priorities to start immediately"
  ],
  "contraindications": [
    "activities or foods to avoid based on condition"
  ],
  "personalization_notes": "how this plan is tailored to the patient's profile"
}}

Use clear, actionable language. Include evidence basis where available. Emphasize safety and professional consultation."""
        )
        
        logger_lifestyle.info("Enhanced LifestyleModificationAgent initialized with web search capabilities")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for lifestyle recommendation generation with monitoring and error handling.
        
        Args:
            input_data: User data including disease, age, gender, symptoms, medical history
            
        Returns:
            Dictionary with personalized lifestyle recommendations, citations, and safety guardrails applied
        """
        return self.process_with_monitoring(input_data)
    
    def _process_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal processing method called by process_with_monitoring.
        
        Args:
            input_data: User data including disease, user_context, symptoms
            
        Returns:
            Dictionary with lifestyle recommendations
        """
        # Validate required input fields
        required_fields = ["disease", "user_context"]
        validation = self.validate_input(input_data, required_fields)
        
        if not validation["valid"]:
            return self.format_agent_response(
                success=False,
                message=validation["message"],
                data=validation
            )
            
        self.log_agent_action("generate_lifestyle_plan", {
            "disease": input_data["disease"],
            "age": input_data.get("user_context", {}).get("age")
        })
        
        try:
            user_context = input_data["user_context"]
            age = user_context.get("age", 30)
            gender = user_context.get("gender", "unknown")
            symptoms = input_data.get("symptoms", [])
            medical_history = user_context.get("medical_history", "Not provided")
            
            # Generate recommendations with retry logic
            recommendations = self.execute_with_retry(
                lambda: self._generate_lifestyle_recommendations(
                    disease=input_data["disease"],
                    risk_level=input_data.get("confidence", "MEDIUM"),
                    age=age,
                    gender=gender,
                    symptoms=symptoms,
                    medical_history=medical_history
                )
            )
            
            if recommendations:
                return self.format_agent_response(
                    success=True,
                    data=recommendations,
                    message="Personalized evidence-based lifestyle plan generated"
                )
            else:
                # Fallback to template-based generation
                return self.format_agent_response(
                    success=True,
                    data=self._generate_template_plan(input_data["disease"], age),
                    message="Standard lifestyle plan generated (Fallback)"
                )
            
        except Exception as e:
            logger_lifestyle.error(f"Error generating lifestyle plan: {str(e)}")
            return self.get_fallback_response(input_data)
    
    def _generate_lifestyle_recommendations(
        self, 
        disease: str, 
        risk_level: str, 
        age: int,
        gender: str, 
        symptoms: List[str],
        medical_history: str
    ) -> Optional[Dict[str, Any]]:
        """
        Generate evidence-based lifestyle recommendations using LangChain with web search.
        
        Args:
            disease: The disease/condition
            risk_level: Risk level (LOW, MEDIUM, HIGH)
            age: Patient age
            gender: Patient gender
            symptoms: List of symptoms
            medical_history: Patient medical history
            
        Returns:
            Dictionary containing lifestyle recommendations with citations
        """
        logger_lifestyle.info(f"Generating evidence-based lifestyle plan for {disease} using LangChain with web search")
        
        try:
            # Search web for evidence-based lifestyle interventions
            web_sources = []
            if self.config.enable_web_search:
                web_sources = self._search_lifestyle_interventions(disease, symptoms)
            
            # Generate recommendations using LangChain with web context
            recommendations = self._generate_with_langchain(
                disease=disease,
                risk_level=risk_level,
                age=age,
                gender=gender,
                symptoms=symptoms,
                medical_history=medical_history,
                web_sources=web_sources
            )
            
            if recommendations:
                # Apply safety guardrails
                if isinstance(recommendations, dict) and "text_plan" in recommendations:
                    recommendations["text_plan"] = self.apply_safety_guardrails(recommendations["text_plan"])
                
                # Add citations and metadata
                recommendations["sources"] = self._format_citations(web_sources) if web_sources else []
                recommendations["generated_at"] = datetime.utcnow().isoformat()
                recommendations["generated_by"] = "langchain_gemini_ai_enhanced"
                recommendations["agent"] = "LifestyleModificationAgent"
                recommendations["personalization"] = {
                    "age": age,
                    "gender": gender,
                    "condition": disease
                }
                
                logger_lifestyle.info("Evidence-based lifestyle plan generated successfully with citations")
                return recommendations
            
            return None
            
        except Exception as e:
            logger_lifestyle.error(f"Error generating evidence-based lifestyle plan: {str(e)}")
            return None
    
    def _search_lifestyle_interventions(self, disease: str, symptoms: List[str]) -> List[Dict]:
        """
        Search web for evidence-based lifestyle interventions.
        
        Args:
            disease: Disease/condition
            symptoms: List of symptoms
            
        Returns:
            List of search results from reliable medical sources
        """
        try:
            # Search for evidence-based lifestyle interventions
            query = f"{disease.replace('_', ' ')} evidence-based lifestyle interventions diet exercise management"
            search_results = self.search_web(
                query=query,
                filters={"source_types": ["medical_literature", "clinical_guidelines"]}
            )
            
            self.log_agent_action("web_search_lifestyle", {
                "disease": disease,
                "results_count": len(search_results)
            })
            
            return search_results
            
        except Exception as e:
            logger_lifestyle.error(f"Web search for lifestyle interventions failed: {str(e)}")
            return []
    
    def _format_citations(self, web_sources: List[Dict]) -> List[Dict[str, str]]:
        """
        Format web sources into proper citations.
        
        Args:
            web_sources: List of search results
            
        Returns:
            List of formatted citations
        """
        citations = []
        for idx, source in enumerate(web_sources[:5], 1):  # Limit to top 5 sources
            citation = {
                "number": idx,
                "title": source.get("title", "Medical Source"),
                "url": source.get("url", ""),
                "source": source.get("source_domain", ""),
                "accessed": datetime.utcnow().strftime("%Y-%m-%d")
            }
            citations.append(citation)
        
        return citations
            
    def _generate_with_langchain(
        self, 
        disease: str, 
        risk_level: str, 
        age: int, 
        gender: str, 
        symptoms: List[str],
        medical_history: str,
        web_sources: List[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate plan using LangChain with web context.
        
        Args:
            disease: Disease/condition
            risk_level: Risk level
            age: Patient age
            gender: Patient gender
            symptoms: List of symptoms
            medical_history: Medical history
            web_sources: Optional web search results for evidence
            
        Returns:
            Dictionary with lifestyle recommendations or None if generation fails
        """
        try:
            if not self.lifestyle_chain:
                return None
            
            # Prepare web context if available
            web_context = ""
            if web_sources:
                web_context = "\n\nEvidence-based context from reliable medical sources:\n"
                for source in web_sources[:3]:  # Use top 3 sources
                    web_context += f"- {source.get('snippet', '')} (Source: {source.get('source_domain', 'medical database')})\n"
            
            chain_input = {
                "disease": disease.replace('_', ' ').title(),
                "risk_level": risk_level,
                "age": age,
                "gender": gender,
                "symptoms": ", ".join(symptoms) if symptoms else "None specified",
                "medical_history": medical_history,
                "web_context": web_context
            }
            
            # Execute LangChain chain with circuit breaker
            result = self.execute_with_circuit_breaker(
                lambda: self.execute_chain(self.lifestyle_chain, chain_input)
            )
            
            if result:
                # Try to parse JSON result
                try:
                    import json
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
        """
        Generate template-based plan as fallback.
        
        Args:
            disease: Disease/condition
            age: Patient age
            
        Returns:
            Dictionary with basic lifestyle recommendations
        """
        # Simplified templates for common conditions
        templates = {
            "diabetes": {
                "diet_plan": [
                    {"recommendation": "Reduce sugar and refined carbs", "priority": "high"},
                    {"recommendation": "Increase fiber intake (vegetables, whole grains)", "priority": "high"},
                    {"recommendation": "Eat at regular intervals", "priority": "medium"},
                    {"recommendation": "Stay hydrated (8-10 glasses water daily)", "priority": "medium"}
                ],
                "exercise_plan": [
                    {"activity": "Moderate walking", "frequency": "daily", "duration": "30 minutes", "priority": "high"},
                    {"activity": "Light resistance training", "frequency": "2-3 times/week", "duration": "20 minutes", "safety_notes": "Consult doctor first", "priority": "medium"},
                    {"activity": "Yoga for flexibility", "frequency": "3 times/week", "duration": "20 minutes", "priority": "medium"}
                ],
                "stress_management": [
                    {"technique": "Deep breathing exercises", "how_to": "5 minutes, 3 times daily"},
                    {"technique": "Meditation", "how_to": "10 minutes daily, morning or evening"}
                ],
                "sleep_hygiene": [
                    {"tip": "Maintain consistent sleep schedule", "rationale": "Helps regulate blood sugar"},
                    {"tip": "Avoid screens 1 hour before bed", "rationale": "Improves sleep quality"}
                ],
                "immediate_actions": [
                    "Monitor blood sugar regularly",
                    "Consult dietician for meal planning",
                    "Check feet daily for injuries"
                ],
                "contraindications": [
                    "Avoid high-sugar foods and beverages",
                    "Avoid intense exercise without medical clearance"
                ],
                "personalization_notes": "Plan adjusted for diabetes management"
            },
            "heart_disease": {
                "diet_plan": [
                    {"recommendation": "Reduce sodium intake", "priority": "high"},
                    {"recommendation": "Increase omega-3 fatty acids (fish, nuts)", "priority": "high"},
                    {"recommendation": "Eat more fruits and vegetables", "priority": "high"},
                    {"recommendation": "Limit saturated fats", "priority": "high"}
                ],
                "exercise_plan": [
                    {"activity": "Light walking", "frequency": "daily", "duration": "20-30 minutes", "safety_notes": "Start slow, monitor heart rate", "priority": "high"},
                    {"activity": "Gentle stretching", "frequency": "daily", "duration": "10 minutes", "priority": "medium"}
                ],
                "stress_management": [
                    {"technique": "Progressive muscle relaxation", "how_to": "10 minutes daily"},
                    {"technique": "Mindfulness meditation", "how_to": "15 minutes daily"}
                ],
                "sleep_hygiene": [
                    {"tip": "Sleep on left side", "rationale": "Reduces heart strain"},
                    {"tip": "Keep bedroom cool", "rationale": "Promotes better sleep"}
                ],
                "immediate_actions": [
                    "Monitor blood pressure regularly",
                    "Take prescribed medications as directed",
                    "Know emergency symptoms (chest pain, shortness of breath)"
                ],
                "contraindications": [
                    "Avoid high-sodium processed foods",
                    "Avoid strenuous exercise without medical clearance"
                ],
                "personalization_notes": "Plan adjusted for heart health"
            },
            "hypertension": {
                "diet_plan": [
                    {"recommendation": "Follow DASH diet principles", "priority": "high"},
                    {"recommendation": "Reduce sodium to <2300mg daily", "priority": "high"},
                    {"recommendation": "Increase potassium-rich foods", "priority": "medium"},
                    {"recommendation": "Limit alcohol consumption", "priority": "medium"}
                ],
                "exercise_plan": [
                    {"activity": "Brisk walking", "frequency": "5 days/week", "duration": "30 minutes", "priority": "high"},
                    {"activity": "Swimming or cycling", "frequency": "2-3 times/week", "duration": "30 minutes", "priority": "medium"}
                ],
                "stress_management": [
                    {"technique": "Yoga", "how_to": "30 minutes, 3 times weekly"},
                    {"technique": "Deep breathing", "how_to": "5 minutes, multiple times daily"}
                ],
                "sleep_hygiene": [
                    {"tip": "Aim for 7-9 hours nightly", "rationale": "Poor sleep raises blood pressure"},
                    {"tip": "Create relaxing bedtime routine", "rationale": "Reduces stress"}
                ],
                "immediate_actions": [
                    "Monitor blood pressure daily",
                    "Reduce salt in cooking",
                    "Start walking routine"
                ],
                "contraindications": [
                    "Avoid high-sodium foods",
                    "Avoid excessive caffeine"
                ],
                "personalization_notes": "Plan adjusted for blood pressure management"
            }
        }
        
        # Return disease-specific template or default to diabetes template
        plan = templates.get(disease.lower(), templates["diabetes"])
        plan["generated_by"] = "template_fallback"
        plan["generated_at"] = datetime.utcnow().isoformat()
        plan["agent"] = "LifestyleModificationAgent"
        plan["sources"] = []
        
        return plan
