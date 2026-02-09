"""
Dataset Analyzer Utility

This script analyzes your dataset and extracts:
1. Column names (features)
2. Feature types (numeric, categorical, binary)
3. Unique values for categorical features
4. Disease labels
5. Feature statistics

Use this to automatically configure the data extraction agent.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatasetAnalyzer:
    """Analyze dataset and extract feature information."""
    
    def __init__(self, dataset_path: str):
        """
        Initialize analyzer with dataset path.
        
        Args:
            dataset_path: Path to CSV dataset file
        """
        self.dataset_path = Path(dataset_path)
        self.df = None
        self.features = []
        self.target_column = None
        self.feature_info = {}
        
    def load_dataset(self) -> bool:
        """Load the dataset from CSV file."""
        try:
            logger.info(f"Loading dataset from: {self.dataset_path}")
            self.df = pd.read_csv(self.dataset_path)
            logger.info(f"Dataset loaded: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            return True
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            return False
    
    def identify_target_column(self, target_hints: List[str] = None) -> str:
        """
        Identify the target column (disease/prognosis).
        
        Args:
            target_hints: List of possible target column names
            
        Returns:
            Name of target column
        """
        if target_hints is None:
            target_hints = ['disease', 'prognosis', 'diagnosis', 'target', 'label', 'class']
        
        # Check for exact matches (case-insensitive)
        for col in self.df.columns:
            if col.lower() in target_hints:
                self.target_column = col
                logger.info(f"Target column identified: {col}")
                return col
        
        # If not found, assume last column is target
        self.target_column = self.df.columns[-1]
        logger.warning(f"Target column not found in hints, assuming last column: {self.target_column}")
        return self.target_column
    
    def analyze_features(self) -> Dict[str, Any]:
        """
        Analyze all features in the dataset.
        
        Returns:
            Dictionary with feature information
        """
        if self.df is None:
            raise ValueError("Dataset not loaded. Call load_dataset() first.")
        
        if self.target_column is None:
            self.identify_target_column()
        
        # Get feature columns (all except target)
        self.features = [col for col in self.df.columns if col != self.target_column]
        
        logger.info(f"Analyzing {len(self.features)} features...")
        
        for feature in self.features:
            self.feature_info[feature] = self._analyze_single_feature(feature)
        
        return self.feature_info
    
    def _analyze_single_feature(self, feature: str) -> Dict[str, Any]:
        """Analyze a single feature."""
        col_data = self.df[feature]
        
        info = {
            'name': feature,
            'dtype': str(col_data.dtype),
            'missing_count': int(col_data.isna().sum()),
            'missing_percent': float(col_data.isna().sum() / len(col_data) * 100),
            'unique_count': int(col_data.nunique())
        }
        
        # Determine feature type
        if col_data.dtype in ['int64', 'float64']:
            info['type'] = 'numeric'
            info['min'] = float(col_data.min()) if not col_data.isna().all() else None
            info['max'] = float(col_data.max()) if not col_data.isna().all() else None
            info['mean'] = float(col_data.mean()) if not col_data.isna().all() else None
            info['std'] = float(col_data.std()) if not col_data.isna().all() else None
            
            # Check if binary (0/1)
            unique_vals = col_data.dropna().unique()
            if len(unique_vals) == 2 and set(unique_vals).issubset({0, 1}):
                info['type'] = 'binary'
                info['values'] = [0, 1]
        else:
            info['type'] = 'categorical'
            unique_vals = col_data.dropna().unique()
            if len(unique_vals) <= 20:  # Only store if reasonable number
                info['values'] = [str(v) for v in unique_vals]
            else:
                info['values'] = f"Too many unique values ({len(unique_vals)})"
        
        return info
    
    def get_disease_list(self) -> List[str]:
        """Get list of all diseases in the dataset."""
        if self.target_column is None:
            self.identify_target_column()
        
        diseases = self.df[self.target_column].unique().tolist()
        logger.info(f"Found {len(diseases)} unique diseases")
        return diseases
    
    def generate_feature_config(self) -> Dict[str, Any]:
        """
        Generate configuration for data extraction agent.
        
        Returns:
            Configuration dictionary
        """
        if not self.feature_info:
            self.analyze_features()
        
        config = {
            'dataset_info': {
                'total_rows': int(self.df.shape[0]),
                'total_columns': int(self.df.shape[1]),
                'target_column': self.target_column,
                'num_diseases': int(self.df[self.target_column].nunique()),
                'num_features': len(self.features)
            },
            'features': {
                'all_features': self.features,
                'numeric_features': [f for f, info in self.feature_info.items() if info['type'] == 'numeric'],
                'binary_features': [f for f, info in self.feature_info.items() if info['type'] == 'binary'],
                'categorical_features': [f for f, info in self.feature_info.items() if info['type'] == 'categorical']
            },
            'feature_details': self.feature_info,
            'diseases': self.get_disease_list()
        }
        
        return config
    
    def save_config(self, output_path: str = 'config/dataset_config.json'):
        """Save configuration to JSON file."""
        config = self.generate_feature_config()
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Configuration saved to: {output_file}")
        return output_file
    
    def generate_summary_report(self) -> str:
        """Generate a human-readable summary report."""
        if not self.feature_info:
            self.analyze_features()
        
        diseases = self.get_disease_list()
        
        report = []
        report.append("="*80)
        report.append("DATASET ANALYSIS REPORT")
        report.append("="*80)
        report.append("")
        
        # Dataset Overview
        report.append("DATASET OVERVIEW")
        report.append("-"*80)
        report.append(f"Total Rows: {self.df.shape[0]:,}")
        report.append(f"Total Columns: {self.df.shape[1]}")
        report.append(f"Target Column: {self.target_column}")
        report.append(f"Number of Diseases: {len(diseases)}")
        report.append(f"Number of Features: {len(self.features)}")
        report.append("")
        
        # Feature Summary
        report.append("FEATURE SUMMARY")
        report.append("-"*80)
        numeric_features = [f for f, info in self.feature_info.items() if info['type'] == 'numeric']
        binary_features = [f for f, info in self.feature_info.items() if info['type'] == 'binary']
        categorical_features = [f for f, info in self.feature_info.items() if info['type'] == 'categorical']
        
        report.append(f"Numeric Features: {len(numeric_features)}")
        report.append(f"Binary Features: {len(binary_features)}")
        report.append(f"Categorical Features: {len(categorical_features)}")
        report.append("")
        
        # Feature Details
        report.append("FEATURE DETAILS")
        report.append("-"*80)
        for feature, info in self.feature_info.items():
            report.append(f"\n{feature}:")
            report.append(f"  Type: {info['type']}")
            report.append(f"  Missing: {info['missing_count']} ({info['missing_percent']:.1f}%)")
            report.append(f"  Unique Values: {info['unique_count']}")
            
            if info['type'] == 'numeric':
                report.append(f"  Range: [{info['min']:.2f}, {info['max']:.2f}]")
                report.append(f"  Mean: {info['mean']:.2f} (±{info['std']:.2f})")
            elif info['type'] == 'binary':
                report.append(f"  Values: {info['values']}")
            elif info['type'] == 'categorical' and isinstance(info['values'], list):
                report.append(f"  Values: {', '.join(info['values'][:5])}")
                if len(info['values']) > 5:
                    report.append(f"           ... and {len(info['values']) - 5} more")
        
        report.append("")
        
        # Disease List (first 20)
        report.append("DISEASES (First 20)")
        report.append("-"*80)
        for i, disease in enumerate(diseases[:20], 1):
            report.append(f"{i:3d}. {disease}")
        if len(diseases) > 20:
            report.append(f"     ... and {len(diseases) - 20} more diseases")
        
        report.append("")
        report.append("="*80)
        
        return "\n".join(report)
    
    def save_report(self, output_path: str = 'config/dataset_report.txt'):
        """Save summary report to text file."""
        report = self.generate_summary_report()
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Report saved to: {output_file}")
        return output_file


def analyze_dataset(dataset_path: str, 
                   target_column: str = None,
                   save_config: bool = True,
                   save_report: bool = True) -> Dict[str, Any]:
    """
    Convenience function to analyze a dataset.
    
    Args:
        dataset_path: Path to CSV dataset
        target_column: Name of target column (auto-detected if None)
        save_config: Whether to save configuration JSON
        save_report: Whether to save text report
        
    Returns:
        Configuration dictionary
    """
    analyzer = DatasetAnalyzer(dataset_path)
    
    # Load dataset
    if not analyzer.load_dataset():
        raise ValueError("Failed to load dataset")
    
    # Identify target column
    if target_column:
        analyzer.target_column = target_column
    else:
        analyzer.identify_target_column()
    
    # Analyze features
    analyzer.analyze_features()
    
    # Print summary
    print(analyzer.generate_summary_report())
    
    # Save outputs
    if save_config:
        analyzer.save_config()
    
    if save_report:
        analyzer.save_report()
    
    return analyzer.generate_feature_config()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python dataset_analyzer.py <dataset_path> [target_column]")
        print("\nExample:")
        print("  python dataset_analyzer.py data/disease_dataset.csv")
        print("  python dataset_analyzer.py data/disease_dataset.csv prognosis")
        sys.exit(1)
    
    dataset_path = sys.argv[1]
    target_column = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        config = analyze_dataset(dataset_path, target_column)
        print("\n✓ Analysis complete!")
        print(f"✓ Configuration saved to: config/dataset_config.json")
        print(f"✓ Report saved to: config/dataset_report.txt")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
