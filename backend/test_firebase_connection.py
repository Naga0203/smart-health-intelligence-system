
import os
import sys
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_ai_backend.settings')
django.setup()

from common.firebase_db import get_firebase_db
import logging

# Configure logging to print to console
logging.basicConfig(level=logging.DEBUG)

print("Attempting to get Firebase DB...")
try:
    db = get_firebase_db()
    print("Firebase DB instance obtained.")
    
    print("Attempting to perform health check...")
    if db.health_check():
        print("Health check PASSED.")
    else:
        print("Health check FAILED.")
        
    print("Attempting to access a non-existent document to query...")
    try:
        doc = db.db.collection('users').limit(1).get()
        print(f"Query executed. Result count: {len(list(doc))}")
    except Exception as e:
        print(f"Query FAILED: {e}")

except Exception as e:
    print(f"Main execution FAILED: {e}")
