"""
Test to verify no static medical data is loaded at startup.

This test ensures that the system uses dynamic retrieval instead of
static knowledge bases, validating Requirement 3.6.
"""

import pytest
import sys
from pathlib import Path


class TestNoStaticDataLoading:
    """Test suite to verify static data elimination."""
    
    def test_treatment_knowledge_base_not_importable(self):
        """Verify TreatmentKnowledgeBase class no longer exists."""
        with pytest.raises(ImportError):
            from treatment.knowledge_base import TreatmentKnowledgeBase
    
    def test_no_static_treatment_data_files(self):
        """Verify no static treatment data files exist."""
        backend_dir = Path(__file__).resolve().parent.parent
        
        # Check for JSON files with treatment data
        treatment_json_files = list(backend_dir.rglob('*treatment*.json'))
        disease_json_files = list(backend_dir.rglob('*disease*.json'))
        medical_json_files = list(backend_dir.rglob('*medical*.json'))
        
        # Filter out node_modules and other non-data directories
        def is_data_file(path):
            path_str = str(path)
            exclude_patterns = [
                'node_modules',
                '.git',
                '__pycache__',
                'migrations',
                'package.json',
                'tsconfig.json',
                'firebase-credentials.json',
                'dataset_config.json',
                'firestore_indexes.json'
            ]
            return not any(pattern in path_str for pattern in exclude_patterns)
        
        treatment_data_files = [f for f in treatment_json_files if is_data_file(f)]
        disease_data_files = [f for f in disease_json_files if is_data_file(f)]
        medical_data_files = [f for f in medical_json_files if is_data_file(f)]
        
        assert len(treatment_data_files) == 0, f"Found treatment data files: {treatment_data_files}"
        assert len(disease_data_files) == 0, f"Found disease data files: {disease_data_files}"
        assert len(medical_data_files) == 0, f"Found medical data files: {medical_data_files}"
    
    def test_no_static_csv_data_files(self):
        """Verify no static CSV files with medical data exist."""
        backend_dir = Path(__file__).resolve().parent.parent
        
        # Check for CSV files
        csv_files = list(backend_dir.rglob('*.csv'))
        
        # Filter out test fixtures and non-medical data
        def is_medical_data_file(path):
            path_str = str(path).lower()
            medical_keywords = ['disease', 'treatment', 'symptom', 'diagnosis', 'medication']
            exclude_patterns = ['node_modules', '.git', '__pycache__', 'test_fixtures']
            
            has_medical_keyword = any(keyword in path_str for keyword in medical_keywords)
            is_excluded = any(pattern in path_str for pattern in exclude_patterns)
            
            return has_medical_keyword and not is_excluded
        
        medical_csv_files = [f for f in csv_files if is_medical_data_file(f)]
        
        assert len(medical_csv_files) == 0, f"Found medical CSV files: {medical_csv_files}"
    
    def test_dynamic_treatment_retrieval_exists(self):
        """Verify DynamicTreatmentRetrieval is available and replaces static data."""
        from agents.infrastructure.dynamic_treatment import DynamicTreatmentRetrieval
        
        # Verify the class exists and can be imported
        assert DynamicTreatmentRetrieval is not None
        
        # Verify it has the expected methods for dynamic retrieval
        assert hasattr(DynamicTreatmentRetrieval, 'get_treatment_info')
        assert hasattr(DynamicTreatmentRetrieval, 'get_clinical_guidelines')
        assert hasattr(DynamicTreatmentRetrieval, 'get_drug_interactions')
        assert hasattr(DynamicTreatmentRetrieval, 'synthesize_treatment_info')
    
    def test_treatment_exploration_uses_dynamic_retrieval(self):
        """Verify TreatmentExplorationAgent uses DynamicTreatmentRetrieval."""
        from agents.treatment_exploration import TreatmentExplorationAgent
        from agents.infrastructure.config import AgentConfig
        
        # Create agent instance
        config = AgentConfig(agent_name="test_treatment_exploration")
        agent = TreatmentExplorationAgent(config)
        
        # Verify agent has dynamic_treatment attribute
        assert hasattr(agent, 'dynamic_treatment')
        assert agent.dynamic_treatment is not None
        
        # Verify it's an instance of DynamicTreatmentRetrieval
        from agents.infrastructure.dynamic_treatment import DynamicTreatmentRetrieval
        assert isinstance(agent.dynamic_treatment, DynamicTreatmentRetrieval)
    
    def test_no_hardcoded_treatment_data_in_code(self):
        """Verify no hardcoded treatment dictionaries remain in the codebase."""
        backend_dir = Path(__file__).resolve().parent.parent
        
        # Read all Python files in agents and treatment directories
        python_files = []
        python_files.extend(backend_dir.glob('agents/**/*.py'))
        python_files.extend(backend_dir.glob('treatment/**/*.py'))
        
        # Look for treatment-specific patterns (not educational content)
        suspicious_patterns = [
            '"allopathy": {',
            '"ayurveda": {',
            '"homeopathy": {',
            'common_approaches',
            'lifestyle_recommendations',
            'treatment_systems',
        ]
        
        files_with_hardcoded_data = []
        
        for py_file in python_files:
            # Skip test files and migrations
            if 'test_' in py_file.name or 'migration' in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Check for suspicious patterns indicating treatment data structures
                for pattern in suspicious_patterns:
                    if pattern in content:
                        # Make sure it's not in a comment or docstring
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if pattern in line:
                                stripped = line.strip()
                                # Skip comments, docstrings, and settings
                                if (not stripped.startswith('#') and 
                                    not stripped.startswith('"""') and
                                    'HEALTH_AI_SETTINGS' not in content):
                                    files_with_hardcoded_data.append((py_file, i+1, line.strip()))
            except Exception:
                # Skip files that can't be read
                pass
        
        assert len(files_with_hardcoded_data) == 0, (
            f"Found hardcoded treatment data structures in: {files_with_hardcoded_data}"
        )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
