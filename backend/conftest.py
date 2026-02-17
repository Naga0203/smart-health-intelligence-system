"""
Pytest configuration for backend tests.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir.parent))

# Mock Django before any imports
mock_settings = MagicMock()
mock_settings.MAX_FILE_SIZE_MB = 10
sys.modules['django'] = MagicMock()
sys.modules['django.conf'] = MagicMock()
sys.modules['django.conf'].settings = mock_settings

# Mock Firebase
sys.modules['firebase_admin'] = MagicMock()
sys.modules['firebase_admin.storage'] = MagicMock()

# Configure environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_ai_backend.settings')
