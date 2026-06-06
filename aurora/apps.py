# ======================================================================
# FILE: aurora/apps.py (PATCH 1 OF 1)
# START: APP INITIALIZATION & SIGNALS LIFECYCLE LINKAGE
# ======================================================================
from django.apps import AppConfig

class AuroraConfig(AppConfig):
    """Core configuration class for the Aurora engine application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aurora'

    def ready(self):
        """Force-loads blueprints, models, and graph node hooks into memory on bootstrap."""
        import aurora.nodes
        # THE CRITICAL LINK: Binds real-time Django signal loops directly to Neo4j graph nodes
        import aurora.signals 
# ======================================================================
# END: APP INITIALIZATION & SIGNALS LIFECYCLE LINKAGE
# ======================================================================
