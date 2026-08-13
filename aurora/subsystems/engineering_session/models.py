# ======================================================================
# FILE: aurora/subsystems/engineering_session/models.py
# START: ENGINEERING_SESSION_MODEL
# ======================================================================

from django.conf import settings
from django.db import models


class EngineeringSession(models.Model):
    """One bounded period of active Aurora engineering work."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="engineering_sessions",
    )

    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user} / {self.started_at}"

# ======================================================================
# FILE: aurora/subsystems/engineering_session/models.py
# END: ENGINEERING_SESSION_MODEL
# ======================================================================