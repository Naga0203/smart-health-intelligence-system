
import os
import sys
import django
from django.conf import settings
import traceback

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_ai_backend.settings')
django.setup()

from rest_framework.test import APIClient
from common.firebase_auth import FirebaseUser

# Ensure allowed hosts
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS += ['testserver']

# Create a mock user
mock_user = FirebaseUser(
    uid='test_user_123', # Using the same user ID we created earlier
    email='test@example.com',
    display_name='Test User',
    email_verified=True
)

client = APIClient()
client.force_authenticate(user=mock_user)

print("Calling AssessmentHistoryAPIView via APIClient...")
try:
    response = client.get('/api/user/assessments/?page=1&page_size=10')
    print(f"Response status code: {response.status_code}")
    
    if response.status_code == 500:
        print("Got 500 Error. Trying to print response content...")
        print(response.content)
    else:
        print("Response data sample:")
        print(str(response.data)[:500])

except Exception as e:
    print(f"Exception caught during client execution: {e}")
    traceback.print_exc()

