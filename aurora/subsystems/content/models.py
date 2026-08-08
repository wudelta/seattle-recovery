# ======================================================================
# FILE: aurora/subsystems/content/models.py
# START: STATIC_CONTENT_SCHEMA
# ======================================================================

import uuid

from django.conf import settings
from django.db import models


class StaticContent(models.Model):
    """Stores the HTML content for informational pages."""

    class ApplicationChoices(models.TextChoices):
        AURORA = "aurora", "Aurora"
        HOPEHUB = "hopehub", "HopeHub"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    application = models.CharField(
        max_length=10,
        choices=ApplicationChoices.choices,
        default=ApplicationChoices.AURORA,
    )
    title = models.CharField(max_length=255)
    html_content = models.TextField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"StaticContent: {self.title} "
            f"[{self.application}] (ID: {self.id})"
        )


# ======================================================================
# END: STATIC_CONTENT_SCHEMA
# ======================================================================