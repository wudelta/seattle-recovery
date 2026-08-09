# ======================================================================
# FILE: aurora/apps.py
# START: AURORA_APPLICATION_CONFIGURATION
# ======================================================================

from django.apps import AppConfig


class AuroraConfig(AppConfig):
    """Django application configuration for Aurora."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "aurora"


# ======================================================================
# END: AURORA_APPLICATION_CONFIGURATION
# ======================================================================