"""
Setup Script for Multi-Disease Model Integration

This script helps you integrate your 715-disease model and dataset:
1. Analyzes your dataset
2. Extracts features and disease list
3. Updates the data extraction agent
4. Updates the orchestrator
5. Tests the integration

Usage:
    python setup_multi_disease_model.py <dataset_path> [model_path]

Example:
    python setup_multi_disease_model.py data/disease_symptoms.csv models/disease_model.pkl
"""

import sys
import json
from pathlib import Path
from utils.dataset_analyzer import DatasetAnalyzer


def setup_multi_disease_system(dataset_path: str, model_path: str = None):
    """
    Complete setup for multi-disease system.
    
    Args:
        dataset_path: Path to your CSV dataset
        model_path: Path to your trained model (optional)
    """
    print("="*80)
    print("MULTI-DISEASE MODEL SETUP")
    print("="*80)
    print()
    
    # Step 1: Analyze Dataset
    print("[1/5] Analyzing dataset...")
    print("-"*80)
    
    analyzer = DatasetAnalyzer(dataset_path)
    
    if not analyzer.load_dataset():
        print("✗ Failed to load dataset")
        return False
    
    # Identify target column
    analyzer.identify_target_column(['disease', 'prognosis', 'diagnosis'])
    
    # Analyze features
    analyzer.analyze_features()
    
    # Get configuration
    config = analyzer.generate_feature_config()
    
    print(f"✓ Dataset analyzed successfully")
    print(f"  - Rows: {config['dataset_info']['total_rows']:,}")
    print(f"  - Features: {config['dataset_info']['num_features']}")
    print(f"  - Diseases: {config['dataset_info']['num_diseases']}")
    print()
    
    # Step 2: Save Configuration
    print("[2/5] Saving configuration...")
    print("-"*80)
    
    config_file = analyzer.save_config()
    report_file = analyzer.save_report()
    
    print(f"✓ Configuration saved to: {config_file}")
    print(f"✓ Report saved to: {report_file}")
    print()
    
    # Step 3: Update Data Extraction Agent
    print("[3/5] Updating data extraction agent...")
    print("-"*80)
    
    update_data_extraction_agent(config)
    
    print(f"✓ Data extraction agent updated")
    print(f"  - Features configured: {len(config['features']['all_features'])}")
    print()
    
    # Step 4: Update Orchestrator
    print("[4/5] Updating orchestrator...")
    print("-"*80)
    
    update_orchestrator()
    
    print(f"✓ Orchestrator updated to use multi-disease predictor")
    print()
    
    # Step 5: Verify Model
    print("[5/5] Verifying model setup...")
    print("-"*80)
    
    if model_path and Path(model_path).exists():
        print(f"✓ Model file found: {model_path}")
        print(f"  Copy this file to: models/multi_disease_model.pkl")
    else:
        print(f"⚠ Model file not provided or not found")
        print(f"  Place your trained model at: models/multi_disease_model.pkl")
    
    print()
    
    # Summary
    print("="*80)
    print("SETUP COMPLETE!")
    print("="*80)
    print()
    print("Next Steps:")
    print("1. Review the configuration: config/dataset_config.json")
    print("2. Review the report: config/dataset_report.txt")
    
    if model_path and Path(model_path).exists():
        print(f"3. Copy your model: cp {model_path} models/multi_disease_model.pkl")
    else:
        print("3. Place your trained model at: models/multi_disease_model.pkl")
    
    print("4. Test the system: python test_multi_disease.py")
    print()
    
    return True


def update_data_extraction_agent(config: dict):
    """Update data extraction agent with new features."""
    
    # Create updated agent configuration
    agent_config = {
        'model_features': {
            'multi_disease': config['features']['all_features']
        },
        'feature_types': {
            'numeric': config['features']['numeric_features'],
            'binary': config['features']['binary_features'],
            'categorical': config['features']['categorical_features']
        },
        'diseases': config['diseases']
    }
    
    # Save agent configuration
    config_dir = Path('config')
    config_dir.mkdir(exist_ok=True)
    
    with open(config_dir / 'agent_config.json', 'w') as f:
        json.dump(agent_config, f, indent=2)


def update_orchestrator():
    """Create updated orchestrator configuration."""
    
    orchestrator_config = {
        'predictor_type': 'multi_disease',
        'model_path': 'models/multi_disease_model.pkl',
        'config_path': 'config/dataset_config.json',
        'confidence_thresholds': {
            'LOW': 0.55,
            'MEDIUM': 0.75,
            'HIGH': 0.90
        }
    }
    
    config_dir = Path('config')
    config_dir.mkdir(exist_ok=True)
    
    with open(config_dir / 'orchestrator_config.json', 'w') as f:
        json.dump(orchestrator_config, f, indent=2)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python setup_multi_disease_model.py <dataset_path> [model_path]")
        print()
        print("Example:")
        print("  python setup_multi_disease_model.py data/disease_symptoms.csv")
        print("  python setup_multi_disease_model.py data/disease_symptoms.csv models/model.pkl")
        print()
        sys.exit(1)
    
    dataset_path = sys.argv[1]
    model_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(dataset_path).exists():
        print(f"✗ Error: Dataset file not found: {dataset_path}")
        sys.exit(1)
    
    try:
        success = setup_multi_disease_system(dataset_path, model_path)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
