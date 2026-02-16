#!/usr/bin/env python
"""Set admin password for Django superuser."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_ai_backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.get(username='admin')
admin.set_password('admin123')
admin.save()
print("Admin password set to: admin123")
print("Username: admin")
print("You can change this password after logging in to Django admin.")
