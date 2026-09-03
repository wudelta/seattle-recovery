from django.conf import settings
from django.db import models

from .hierarchy import Initiative, Phase, Project, Step


# START: USER_POSITION_MODEL
# ======================================================================
class UserPosition(models.Model):
    """The current planning hierarchy position selected by a user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="planning_position",
    )

    project = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_positions",
    )

    initiative = models.ForeignKey(
        Initiative,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_positions",
    )

    phase = models.ForeignKey(
        Phase,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_positions",
    )

    step = models.ForeignKey(
        Step,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_positions",
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} planning position"
# ======================================================================
# END: USER_POSITION_MODEL
# ======================================================================

# START: TIME_ENTRY_MODEL
# ======================================================================
class TimeEntry(models.Model):
    """A period of time spent by a user working on a planning step."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="planning_time_entries",
    )

    step = models.ForeignKey(
        Step,
        on_delete=models.PROTECT,
        related_name="time_entries",
    )

    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user} / {self.step} / {self.started_at}"
# ======================================================================
# END: TIME_ENTRY_MODEL
# ======================================================================
