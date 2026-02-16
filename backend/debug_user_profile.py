
import os
import sys
import django
from django.conf import settings
from django.test import RequestFactory
from unittest.mock import MagicMock

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_ai_backend.settings')
django.setup()

from rest_framework.test import APIClient, force_authenticate
from common.firebase_auth import FirebaseUser

settings.ALLOWED_HOSTS += ['testserver']

# Create a mock user
mock_user = FirebaseUser(
    uid='test_user_123',
    email='test@example.com',
    display_name='Test User',
    email_verified=True
)

client = APIClient()
client.force_authenticate(user=mock_user)

print("Calling UserProfileAPIView via APIClient...")
try:
    response = client.get('/api/user/profile/')
    print(f"Response status code: {response.status_code}")
    # print(f"Response data: {response.data}") 
except Exception as e:
    print(f"Exception caught during client execution: {e}")

print("Checking for last_error.txt...")
if os.path.exists('last_error.txt'):
    with open('last_error.txt', 'r') as f:
        print("\n--- CONTENT OF last_error.txt ---")
        print(f.read())
        print("--- END OF CONTENT ---")
else:
    print("last_error.txt was not created.")
