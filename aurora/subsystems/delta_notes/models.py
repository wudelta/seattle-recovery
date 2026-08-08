# ======================================================================
# FILE: aurora/subsystems/delta_notes/models.py
# START: DELTA_NOTES_SCHEMA
# ======================================================================

from django.conf import settings
from django.db import models


class DeltaNotesEntry(models.Model):
    """
    Tracks daily developer intentions, active task execution blocks, and
    accumulated focus time per session window.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="delta_notes",
        help_text=(
            "The developer compiling this active workspace iteration note."
        ),
    )
    text = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed = models.BooleanField(default=False)
    total_seconds_logged = models.PositiveIntegerField(
        default=0,
        help_text="Total accumulated active focus time recorded in seconds.",
    )
    last_started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the active session timer toggle was engaged.",
    )

    class Meta:
        verbose_name = "Delta Notes Entry"
        verbose_name_plural = "Delta Notes Entries"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"DeltaNote {self.id} - "
            f"User: {self.user.username} "
            f"({self.created_at.strftime('%Y-%m-%d')})"
        )


# ======================================================================
# END: DELTA_NOTES_SCHEMA
# ======================================================================