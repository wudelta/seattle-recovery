# aurora/apps.py
from django.apps import AppConfig

class AuroraConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aurora'

    def ready(self):
        # Force-loads your blueprints and hooks into memory on initialization
        import aurora.nodes
        import aurora.signals  # <-- THE CRITICAL LINK: Binds your live databases together!
