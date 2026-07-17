# ======================================================================
# FILE: aurora/apps.py (PATCH 1 OF 1)
# START: APP_INITIALIZATION_WITHOUT_SIGNAL_BINDING
# ======================================================================
from django.apps import AppConfig


class AuroraConfig(AppConfig):
    """Core configuration class for the Aurora engine application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "aurora"

    def ready(self):
        """Load Aurora graph node definitions during application startup."""
        import aurora.nodes
# ======================================================================
# END: APP_INITIALIZATION_WITHOUT_SIGNAL_BINDING (PATCH 1 OF 1)
# ======================================================================