from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'common'

    def ready(self):
        """Initialize Firebase when the app is ready."""
        try:
            from .firebase_db import FirebaseDatabase
            # Initialize Firebase connection
            FirebaseDatabase()
        except ImportError:
            pass
        except Exception as e:
            import logging
            logger = logging.getLogger('health_ai.common')
            logger.error(f"Failed to initialize Firebase on startup: {e}")
