#!/usr/bin/env python3
"""
Rollback Agent Script

Automated script for rolling back a single agent to old implementation.

Usage:
    python scripts/rollback_agent.py <agent_name> <reason>

Example:
    python scripts/rollback_agent.py treatment_exploration "High error rate in production"
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from agents.infrastructure.rollback import get_rollback_executor
import json


def main():
    if len(sys.argv) < 3:
        print("Usage: python rollback_agent.py <agent_name> <reason>")
        print("\nAvailable agents:")
        print("  - orchestrator")
        print("  - data_extraction")
        print("  - enhanced_extraction")
        print("  - explanation")
        print("  - lifestyle")
        print("  - recommendation")
        print("  - reflection")
        print("  - severity")
        print("  - treatment_exploration")
        print("  - validation")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    reason = ' '.join(sys.argv[2:])
    
    print(f"\n{'='*60}")
    print(f"ROLLBACK AGENT: {agent_name}")
    print(f"REASON: {reason}")
    print(f"{'='*60}\n")
    
    # Confirm
    confirm = input("Are you sure you want to rollback? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Rollback cancelled")
        sys.exit(0)
    
    # Execute rollback
    executor = get_rollback_executor()
    result = executor.execute_rollback(agent_name, reason)
    
    # Print result
    print("\n" + "="*60)
    print("ROLLBACK RESULT")
    print("="*60)
    print(json.dumps(result, indent=2))
    
    if result['success']:
        print("\n✓ Rollback completed successfully")
        print("\nNext steps:")
        print("1. Monitor error logs")
        print("2. Check performance metrics")
        print("3. Verify functionality")
        print("4. Document the issue")
    else:
        print("\n✗ Rollback failed")
        print(f"Error: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
