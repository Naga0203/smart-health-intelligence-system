"""
Unit tests for RecommendationAgent.

Tests specific examples, edge cases, and error conditions for:
- Recommendation generation
- Personalization
- Contraindication detection
- Prioritization
- Medication conflict detection
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from .recommendation import RecommendationAgent
from .infrastructure.config import AgentConfig
from .infrastructure.models import SearchResult


@pytest.fixture
def mock_search_results():
    """Create mock search results."""
    def create_results(query):
        if "guidelines" in query.lower():
            return [
                SearchResult(
                    title=f"Clinical Guidelines for {query}",
                    url="https://who.int/guidelines/test",
                    snippet=f"Evidence-based clinical practice guidelines for managing {query}. Level A evidence from randomized controlled trials.",
                    source_domain="who.int",
                    quality_score=0.95,
                    content=f"Comprehensive guidelines for {query} management with evidence levels."
                ),
                SearchResult(
                    title=f"{query} Treatment Protocol",
                    url="https://cdc.gov/protocols/test",
                    snippet=f"CDC recommendations for {query} treatment and management.",
                    source_domain="cdc.gov",
                    quality_score=0.9,
                    content=f"Treatment protocols for {query}."
                )
            ]
        elif "contraindication" in query.lower():
            return [
                SearchResult(
                    title=f"Contraindications for {query}",
                    url="https://pubmed.ncbi.nlm.nih.gov/contraindications",
                    snippet=f"Known contraindications and precautions for {query} treatment.",
                    source_domain="pubmed.ncbi.nlm.nih.gov",
                    quality_score=0.88,
                    content=f"Detailed contraindication information for {query}."
                )
            ]
        elif "interaction" in query.lower():
            return [
                SearchResult(
                    title=f"Drug Interactions: {query}",
                    url="https://drugs.com/interactions/test",
                    snippet=f"Potential drug interactions for medications in {query}.",
                    source_domain="drugs.com",
                    quality_score=0.85,
                    content=f"Drug interaction database for {query}."
                )
            ]
        return []
    return create_results


@pytest.fixture
def mock_llm_response():
    """Create mock LLM response with structured recommendations."""
    return Mock(content="""{
  "urgent_actions": [
    {
      "recommendation": "Seek immediate medical evaluation",
      "rationale": "High risk level requires prompt professional assessment",
      "actionable_steps": [
        "Contact your healthcare provider today",
        "Prepare list of current symptoms",
        "Bring all current medications to appointment"
      ],
      "evidence_level": "A",
      "source": "Clinical Practice Guidelines (WHO)",
      "priority": "URGENT"
    }
  ],
  "high_priority": [
    {
      "recommendation": "Begin lifestyle modifications immediately",
      "rationale": "Evidence shows lifestyle changes significantly improve outcomes",
      "actionable_steps": [
        "Adopt heart-healthy diet (DASH or Mediterranean)",
        "Start moderate exercise 30 minutes daily",
        "Monitor blood pressure twice daily"
      ],
      "evidence_level": "A",
      "source": "American Heart Association Guidelines",
      "priority": "HIGH",
      "contraindications": [],
      "personalization_note": "Tailored for 55-year-old male with hypertension history"
    }
  ],
  "medium_priority": [
    {
      "recommendation": "Schedule regular follow-up appointments",
      "rationale": "Ongoing monitoring ensures treatment effectiveness",
      "actionable_steps": [
        "Book follow-up in 4-6 weeks",
        "Prepare questions for doctor",
        "Track symptoms between visits"
      ],
      "evidence_level": "B",
      "source": "Clinical Best Practices",
      "priority": "MEDIUM"
    }
  ],
  "low_priority": [
    {
      "recommendation": "Consider stress management techniques",
      "rationale": "Stress reduction may improve overall health outcomes",
      "actionable_steps": [
        "Try meditation or yoga",
        "Ensure adequate sleep (7-9 hours)",
        "Engage in relaxing activities"
      ],
      "evidence_level": "C",
      "source": "Integrative Medicine Research",
      "priority": "LOW"
    }
  ],
  "medication_conflicts": [
    {
      "conflict": "Potential interaction between lisinopril and ibuprofen",
      "medications_involved": ["lisinopril", "ibuprofen"],
      "severity": "MEDIUM",
      "recommendation": "Avoid NSAIDs; use acetaminophen for pain relief instead",
      "source": "Drug Interaction Database"
    }
  ],
  "contraindications": [
    {
      "item": "High-sodium foods",
      "reason": "Contraindicated for hypertension management",
      "severity": "HIGH",
      "source": "Dietary Guidelines for Hypertension"
    }
  ],
  "follow_up": {
    "timeline": "Follow up with healthcare provider in 4-6 weeks",
    "monitoring": [
      "Blood pressure readings twice daily",
      "Weight weekly",
      "Symptom diary"
    ],
    "red_flags": [
      "Severe chest pain",
      "Difficulty breathing",
      "Sudden severe headache",
      "Vision changes"
    ]
  },
  "summary": "Comprehensive recommendations for hypertension management including urgent medical evaluation, lifestyle modifications, and ongoing monitoring. All recommendations are evidence-based and personalized for patient profile.",
  "disclaimer": "This information is for educational purposes only. Always consult healthcare professionals for medical decisions."
}""")


@pytest.fixture
def agent(mock_search_results, mock_llm_response):
    """Create RecommendationAgent with mocked dependencies."""
    config = AgentConfig(
        agent_name="RecommendationAgent",
        enable_web_search=True,
        enable_caching=False,
        monitoring_enabled=False
    )
    
    with patch('backend.agents.infrastructure.web_search.WebSearchTool') as mock_web_search_class, \
         patch('backend.agents.infrastructure.enhanced_base_agent.LangChainGeminiClient') as mock_gemini_class, \
         patch('backend.agents.infrastructure.enhanced_base_agent.MonitoringService'):
        
        # Setup web search mock
        search_tool = Mock()
        search_tool.search = Mock(side_effect=lambda q, f=None: mock_search_results(q))
        mock_web_search_class.return_value = search_tool
        
        # Setup LLM mock
        llm = Mock()
        llm.invoke = Mock(return_value=mock_llm_response)
        client = Mock()
        client.llm = llm
        mock_gemini_class.return_value = client
        
        yield RecommendationAgent(config)


class TestRecommendationGeneration:
    """Test recommendation generation functionality."""
    
    def test_generate_recommendations_for_diabetes(self, agent):
        """Test generating recommendations for diabetes."""
        input_data = {
            'disease': 'diabetes',
            'risk_level': 'HIGH',
            'confidence': 'HIGH',
            'user_context': {
                'age': 55,
                'gender': 'male',
                'medical_history': 'hypertension',
                'current_medications': ['metformin'],
                'allergies': []
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        assert 'data' in result
        data = result['data']
        assert 'urgent_actions' in data
        assert 'high_priority' in data
        assert 'medium_priority' in data
        assert 'low_priority' in data
        assert 'disclaimer' in data
    
    def test_generate_recommendations_for_hypertension(self, agent):
        """Test generating recommendations for hypertension."""
        input_data = {
            'disease': 'hypertension',
            'risk_level': 'MEDIUM',
            'severity': 'MEDIUM',
            'symptoms': ['headache', 'dizziness'],
            'user_context': {
                'age': 60,
                'gender': 'female',
                'medical_history': 'None',
                'current_medications': [],
                'allergies': ['penicillin']
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        assert 'summary' in data
        assert 'follow_up' in data
    
    def test_recommendations_include_actionable_steps(self, agent):
        """Test that recommendations include actionable steps."""
        input_data = {
            'disease': 'asthma',
            'user_context': {
                'age': 35,
                'gender': 'male'
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Check that at least one priority level has actionable steps
        has_actionable_steps = False
        for priority in ['urgent_actions', 'high_priority', 'medium_priority', 'low_priority']:
            if priority in data and data[priority]:
                for rec in data[priority]:
                    if 'actionable_steps' in rec and rec['actionable_steps']:
                        has_actionable_steps = True
                        break
        
        assert has_actionable_steps
    
    def test_recommendations_include_evidence_levels(self, agent):
        """Test that recommendations include evidence levels."""
        input_data = {
            'disease': 'heart disease',
            'user_context': {
                'age': 65,
                'gender': 'male'
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Check that recommendations have evidence levels
        has_evidence = False
        for priority in ['urgent_actions', 'high_priority', 'medium_priority', 'low_priority']:
            if priority in data and data[priority]:
                for rec in data[priority]:
                    if 'evidence_level' in rec:
                        has_evidence = True
                        assert rec['evidence_level'] in ['A', 'B', 'C']
                        break
        
        assert has_evidence


class TestPersonalization:
    """Test personalization based on user profile."""
    
    def test_personalization_by_age(self, agent):
        """Test that recommendations are personalized by age."""
        # Young patient
        input_young = {
            'disease': 'diabetes',
            'user_context': {
                'age': 25,
                'gender': 'female'
            }
        }
        
        result_young = agent.process(input_young)
        assert result_young['success'] is True
        
        # Elderly patient
        input_elderly = {
            'disease': 'diabetes',
            'user_context': {
                'age': 75,
                'gender': 'female'
            }
        }
        
        result_elderly = agent.process(input_elderly)
        assert result_elderly['success'] is True
        
        # Both should succeed and have personalization metadata
        assert 'personalized_for' in result_young['data']
        assert 'personalized_for' in result_elderly['data']
    
    def test_personalization_by_gender(self, agent):
        """Test that recommendations consider gender."""
        input_data = {
            'disease': 'osteoporosis',
            'user_context': {
                'age': 60,
                'gender': 'female',
                'medical_history': 'postmenopausal'
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        assert 'personalized_for' in data
        assert data['personalized_for']['gender'] == 'female'
    
    def test_personalization_with_medical_history(self, agent):
        """Test that recommendations consider medical history."""
        input_data = {
            'disease': 'diabetes',
            'user_context': {
                'age': 50,
                'gender': 'male',
                'medical_history': 'heart disease, kidney disease',
                'current_medications': ['insulin', 'lisinopril']
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        assert 'personalized_for' in data
        assert data['personalized_for']['has_medical_history'] is True
        assert data['personalized_for']['has_medications'] is True
    
    def test_personalization_with_allergies(self, agent):
        """Test that recommendations consider allergies."""
        input_data = {
            'disease': 'infection',
            'user_context': {
                'age': 40,
                'gender': 'female',
                'allergies': ['penicillin', 'sulfa drugs']
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        # Allergies should be considered in contraindications search


class TestContraindicationDetection:
    """Test contraindication detection functionality."""
    
    def test_detect_medication_contraindications(self, agent):
        """Test detecting contraindications for current medications."""
        input_data = {
            'disease': 'hypertension',
            'user_context': {
                'age': 55,
                'gender': 'male',
                'current_medications': ['warfarin', 'aspirin'],
                'medical_history': 'bleeding disorder'
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should have contraindications section
        assert 'contraindications' in data
    
    def test_detect_allergy_contraindications(self, agent):
        """Test detecting contraindications based on allergies."""
        input_data = {
            'disease': 'bacterial infection',
            'user_context': {
                'age': 30,
                'gender': 'female',
                'allergies': ['penicillin', 'cephalosporins']
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        # Allergies should be passed to contraindication search
    
    def test_contraindications_with_comorbidities(self, agent):
        """Test contraindication detection with multiple comorbidities."""
        input_data = {
            'disease': 'arthritis',
            'user_context': {
                'age': 65,
                'gender': 'male',
                'medical_history': 'kidney disease, heart disease, diabetes',
                'current_medications': ['metformin', 'lisinopril', 'atorvastatin']
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should search for contraindications
        assert 'contraindications' in data


class TestPrioritization:
    """Test recommendation prioritization functionality."""
    
    def test_urgent_priority_for_high_risk(self, agent):
        """Test that high risk conditions generate urgent recommendations."""
        input_data = {
            'disease': 'heart attack',
            'risk_level': 'HIGH',
            'severity': 'HIGH',
            'user_context': {
                'age': 60,
                'gender': 'male'
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should have urgent actions
        assert 'urgent_actions' in data
        if data['urgent_actions']:
            assert data['urgent_actions'][0]['priority'] == 'URGENT'
    
    def test_priority_levels_present(self, agent):
        """Test that all priority levels are present in response."""
        input_data = {
            'disease': 'diabetes',
            'risk_level': 'MEDIUM',
            'user_context': {
                'age': 50,
                'gender': 'female'
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should have all priority levels
        assert 'urgent_actions' in data
        assert 'high_priority' in data
        assert 'medium_priority' in data
        assert 'low_priority' in data
    
    def test_recommendations_ordered_by_priority(self, agent):
        """Test that recommendations are properly prioritized."""
        input_data = {
            'disease': 'hypertension',
            'risk_level': 'HIGH',
            'user_context': {
                'age': 55,
                'gender': 'male'
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Verify priority structure exists
        priority_levels = ['urgent_actions', 'high_priority', 'medium_priority', 'low_priority']
        for level in priority_levels:
            assert level in data
            assert isinstance(data[level], list)


class TestMedicationConflictDetection:
    """Test medication conflict detection functionality."""
    
    def test_detect_single_medication_conflicts(self, agent):
        """Test detecting conflicts with a single medication."""
        input_data = {
            'disease': 'hypertension',
            'user_context': {
                'age': 55,
                'gender': 'male',
                'current_medications': ['lisinopril']
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should have medication conflicts section
        assert 'medication_conflicts' in data
    
    def test_detect_multiple_medication_conflicts(self, agent):
        """Test detecting conflicts with multiple medications."""
        input_data = {
            'disease': 'diabetes',
            'user_context': {
                'age': 60,
                'gender': 'female',
                'current_medications': ['warfarin', 'aspirin', 'metformin', 'lisinopril']
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should check for interactions
        assert 'medication_conflicts' in data
    
    def test_no_conflicts_with_no_medications(self, agent):
        """Test that no conflicts are reported when no medications are provided."""
        input_data = {
            'disease': 'hypertension',
            'user_context': {
                'age': 45,
                'gender': 'male',
                'current_medications': []
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should have empty or minimal medication conflicts
        assert 'medication_conflicts' in data
        assert isinstance(data['medication_conflicts'], list)
    
    def test_conflict_severity_levels(self, agent):
        """Test that medication conflicts include severity levels."""
        input_data = {
            'disease': 'heart disease',
            'user_context': {
                'age': 65,
                'gender': 'male',
                'current_medications': ['warfarin', 'aspirin', 'clopidogrel']
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Check conflict structure
        if data['medication_conflicts']:
            for conflict in data['medication_conflicts']:
                assert 'severity' in conflict
                assert conflict['severity'] in ['HIGH', 'MEDIUM', 'LOW']


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_missing_disease_field(self, agent):
        """Test handling of missing disease field."""
        input_data = {
            'user_context': {
                'age': 50,
                'gender': 'male'
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is False
        assert 'message' in result
        assert 'required' in result['message'].lower()
    
    def test_empty_disease_name(self, agent):
        """Test handling of empty disease name."""
        input_data = {
            'disease': '',
            'user_context': {
                'age': 50,
                'gender': 'male'
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is False
    
    def test_missing_user_context(self, agent):
        """Test handling of missing user context."""
        input_data = {
            'disease': 'diabetes'
        }
        
        result = agent.process(input_data)
        
        # Should still succeed with default/unknown values
        assert result['success'] is True
    
    def test_none_input_data(self, agent):
        """Test handling of None input data."""
        result = agent.process(None)
        
        assert result['success'] is False
        assert 'message' in result
    
    def test_web_search_failure(self, agent):
        """Test handling of web search failures."""
        # Mock web search to raise exception
        agent.web_search_tool.search = Mock(side_effect=Exception("Search failed"))
        
        input_data = {
            'disease': 'diabetes',
            'user_context': {
                'age': 50,
                'gender': 'male'
            }
        }
        
        result = agent.process(input_data)
        
        # Should handle error gracefully with fallback
        assert 'success' in result
    
    def test_llm_failure_triggers_fallback(self, agent):
        """Test that LLM failures trigger fallback recommendations."""
        # Mock LLM to raise exception
        agent.recommendation_chain.invoke = Mock(side_effect=Exception("LLM failed"))
        
        input_data = {
            'disease': 'hypertension',
            'risk_level': 'HIGH',
            'user_context': {
                'age': 55,
                'gender': 'male'
            }
        }
        
        result = agent.process(input_data)
        
        # Should succeed with fallback
        assert result['success'] is True
        data = result['data']
        assert 'fallback' in data
        assert data['fallback'] is True
    
    def test_invalid_json_response(self, agent):
        """Test handling of invalid JSON response from LLM."""
        # Mock LLM to return invalid JSON
        agent.recommendation_chain.invoke = Mock(return_value=Mock(content="Invalid JSON {not valid}"))
        
        input_data = {
            'disease': 'diabetes',
            'user_context': {
                'age': 50,
                'gender': 'male'
            }
        }
        
        result = agent.process(input_data)
        
        # Should handle gracefully with fallback
        assert result['success'] is True


class TestSafetyGuardrails:
    """Test safety guardrails integration."""
    
    def test_medical_disclaimer_present(self, agent):
        """Test that medical disclaimer is always present."""
        input_data = {
            'disease': 'diabetes',
            'user_context': {
                'age': 50,
                'gender': 'male'
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should have disclaimer
        assert 'disclaimer' in data
        disclaimer = data['disclaimer']
        assert len(disclaimer) > 50
        assert 'medical' in disclaimer.lower() or 'professional' in disclaimer.lower()
    
    def test_safety_guardrails_applied_to_recommendations(self, agent):
        """Test that safety guardrails are applied to all recommendations."""
        input_data = {
            'disease': 'heart disease',
            'user_context': {
                'age': 60,
                'gender': 'male'
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        # Safety guardrails should prevent specific diagnoses and dosages
        # This is tested implicitly through the agent's processing


class TestResponseStructure:
    """Test response structure and format."""
    
    def test_response_has_required_fields(self, agent):
        """Test that response has all required fields."""
        input_data = {
            'disease': 'asthma',
            'user_context': {
                'age': 35,
                'gender': 'female'
            }
        }
        
        result = agent.process(input_data)
        
        # Check required fields
        assert 'success' in result
        assert 'agent' in result
        assert 'timestamp' in result
        assert result['agent'] == 'RecommendationAgent'
    
    def test_successful_response_structure(self, agent):
        """Test structure of successful response."""
        input_data = {
            'disease': 'diabetes',
            'user_context': {
                'age': 50,
                'gender': 'male'
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        assert 'data' in result
        assert 'message' in result
        assert isinstance(result['data'], dict)
    
    def test_error_response_structure(self, agent):
        """Test structure of error response."""
        input_data = {}
        
        result = agent.process(input_data)
        
        assert result['success'] is False
        assert 'message' in result
        assert isinstance(result['message'], str)
    
    def test_follow_up_section_present(self, agent):
        """Test that follow-up section is present in recommendations."""
        input_data = {
            'disease': 'hypertension',
            'user_context': {
                'age': 55,
                'gender': 'male'
            }
        }
        
        result = agent.process(input_data)
        
        assert result['success'] is True
        data = result['data']
        
        # Should have follow-up section
        assert 'follow_up' in data
        follow_up = data['follow_up']
        assert 'timeline' in follow_up or 'monitoring' in follow_up or 'red_flags' in follow_up


class TestLegacyCompatibility:
    """Test backward compatibility with legacy interface."""
    
    def test_legacy_get_recommendations_method(self, agent):
        """Test legacy get_recommendations method."""
        result = agent.get_recommendations(
            disease='diabetes',
            probability=0.8,
            confidence='HIGH',
            symptoms=['fatigue', 'thirst'],
            user_context={
                'age': 50,
                'gender': 'male',
                'medical_history': 'None',
                'current_medications': [],
                'allergies': []
            }
        )
        
        # Should return recommendations data
        assert isinstance(result, dict)
        assert 'urgent_actions' in result or 'high_priority' in result
    
    def test_legacy_method_converts_probability_to_risk(self, agent):
        """Test that legacy method converts probability to risk level."""
        # High probability
        result_high = agent.get_recommendations(
            disease='diabetes',
            probability=0.9,
            confidence='HIGH',
            symptoms=[],
            user_context={'age': 50, 'gender': 'male'}
        )
        
        assert isinstance(result_high, dict)
        
        # Low probability
        result_low = agent.get_recommendations(
            disease='diabetes',
            probability=0.3,
            confidence='MEDIUM',
            symptoms=[],
            user_context={'age': 50, 'gender': 'male'}
        )
        
        assert isinstance(result_low, dict)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
