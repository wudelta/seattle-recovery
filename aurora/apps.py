# aurora/apps.py
from django.apps import AppConfig

class AuroraConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aurora'

    def ready(self):
        # Force-load the node schemas and signal hooks during memory initialization
        import aurora.nodes
        import aurora.signals  # <-- ADD THIS LINE HERE
