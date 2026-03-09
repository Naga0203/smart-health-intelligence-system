#!/usr/bin/env python3
"""
Emergency Rollback Script

Automated script for rolling back ALL agents to old implementations.
Use only in critical production incidents.

Usage:
    python scripts/emergency_rollback.py <reason>

Example:
    python scripts/emergency_rollback.py "Critical production incident - high error rates"
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from agents.infrastructure.rollback import emergency_rollback
import json


def main():
    if len(sys.argv) < 2:
        print("Usage: python emergency_rollback.py <reason>")
        print("\nExample:")
        print('  python emergency_rollback.py "Critical production incident"')
        sys.exit(1)
    
    reason = ' '.join(sys.argv[1:])
    
    print("\n" + "="*60)
    print("⚠️  EMERGENCY ROLLBACK - ALL AGENTS")
    print("="*60)
    print(f"\nREASON: {reason}")
    print("\nThis will rollback ALL agents to old implementations.")
    print("This action should only be used in critical production incidents.")
    print("\n" + "="*60)
    
    # Confirm
    confirm = input("\nAre you ABSOLUTELY SURE? Type 'EMERGENCY ROLLBACK' to confirm: ")
    if confirm != 'EMERGENCY ROLLBACK':
        print("\nEmergency rollback cancelled")
        sys.exit(0)
    
    print("\n🚨 Executing emergency rollback...")
    
    # Execute rollback
    result = emergency_rollback(reason)
    
    # Print result
    print("\n" + "="*60)
    print("EMERGENCY ROLLBACK RESULT")
    print("="*60)
    print(json.dumps(result, indent=2))
    
    successful = result['successful_rollbacks']
    total = result['total_agents']
    
    print(f"\n{'='*60}")
    if successful == total:
        print(f"✓ Emergency rollback completed: {successful}/{total} agents")
        print("\nAll agents have been rolled back to old implementations.")
    else:
        print(f"⚠️  Partial rollback: {successful}/{total} agents")
        print(f"Failed rollbacks: {result['failed_rollbacks']}")
        print("\nSome agents failed to rollback. Check logs for details.")
    
    print("\nNext steps:")
    print("1. Monitor system stability")
    print("2. Check error logs")
    print("3. Verify critical functionality")
    print("4. Investigate root cause")
    print("5. Document incident")
    print("6. Plan remediation")
    print("="*60)


if __name__ == '__main__':
    main()
