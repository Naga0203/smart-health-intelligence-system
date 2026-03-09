#!/usr/bin/env python3
"""
Generate Migration Report Script

Generates comprehensive migration status report.

Usage:
    python scripts/generate_migration_report.py [output_file]

Example:
    python scripts/generate_migration_report.py migration_report.json
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from agents.infrastructure.migration_tracking import get_migration_tracker
import json


def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'migration_report.json'
    
    print(f"\nGenerating migration report...")
    
    tracker = get_migration_tracker()
    report = tracker.generate_migration_report(output_file)
    
    print(f"\n{'='*60}")
    print("MIGRATION STATUS REPORT")
    print(f"{'='*60}\n")
    
    overall = report['overall_status']
    
    print(f"Total Agents: {overall['total_agents']}")
    print(f"Not Started: {overall['not_started']}")
    print(f"Testing: {overall['testing']}")
    print(f"Migrated: {overall['migrated']}")
    print(f"Rolled Back: {overall['rolled_back']}")
    print(f"Completion: {overall['completion_percentage']:.1f}%")
    
    print(f"\n{'='*60}")
    print("AGENT STATUS")
    print(f"{'='*60}\n")
    
    for agent_name, status in overall['agents'].items():
        stage = status['migration_stage']
        version = status['current_version']
        
        emoji = {
            'not_started': '⚪',
            'testing': '🟡',
            'migrated': '🟢',
            'rolled_back': '🔴'
        }.get(stage, '⚪')
        
        print(f"{emoji} {agent_name:25} {stage:15} (version: {version})")
        
        # Show metrics if available
        old_metrics = status['old_metrics']
        new_metrics = status['new_metrics']
        
        if old_metrics['total_executions'] > 0 or new_metrics['total_executions'] > 0:
            print(f"   Old: {old_metrics['total_executions']} executions, "
                  f"{old_metrics['success_rate']*100:.1f}% success, "
                  f"{old_metrics['average_duration']:.2f}s avg")
            
            if new_metrics['total_executions'] > 0:
                print(f"   New: {new_metrics['total_executions']} executions, "
                      f"{new_metrics['success_rate']*100:.1f}% success, "
                      f"{new_metrics['average_duration']:.2f}s avg")
        
        # Show issues if any
        if status['issues']:
            print(f"   Issues: {len(status['issues'])}")
            for issue in status['issues'][-3:]:  # Show last 3
                print(f"     - {issue[:80]}")
        
        print()
    
    print(f"{'='*60}")
    print(f"\nReport saved to: {output_file}")


if __name__ == '__main__':
    main()
