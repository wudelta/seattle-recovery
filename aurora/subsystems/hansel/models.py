# ======================================================================
# FILE: aurora/subsystems/hansel/models.py
# START: HANSEL_TRAIL_MODEL
# ======================================================================

from django.conf import settings
from django.db import models


class HanselTrailOutcome(models.TextChoices):
    """Observed outcome of one Hansel repository-discovery trail."""

    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    SUFFICIENT = "SUFFICIENT", "Sufficient Authority"
    INCOMPLETE = "INCOMPLETE", "Incomplete"
    BROKEN = "BROKEN", "Broken Trail"
    REDISCOVERED = "REDISCOVERED", "Required Rediscovery"


class HanselTrail(models.Model):
    """
    One repository-discovery trail performed for a Planning Step.

    The trail records whether Hansel successfully routed engineering work
    from its canonical entry point to sufficient repository authority.

    It records observed discovery outcomes rather than generic application
    telemetry.
    """

    step = models.ForeignKey(
        "aurora.Step",
        on_delete=models.PROTECT,
        related_name="hansel_trails",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="hansel_trails",
    )

    outcome = models.CharField(
        max_length=32,
        choices=HanselTrailOutcome.choices,
        default=HanselTrailOutcome.IN_PROGRESS,
    )

    entry_authority = models.CharField(
        max_length=500,
        default="aurora/subsystems/hansel/contracts/HANSEL.md",
    )

    notes = models.TextField(
        blank=True,
    )

    started_at = models.DateTimeField(
        auto_now_add=True,
    )

    ended_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = [
            "-started_at",
        ]

    def __str__(self):
        return (
            f"{self.step} / "
            f"{self.get_outcome_display()}"
        )


class HanselTrailAuthority(models.Model):
    """One repository authority reached by a Hansel discovery trail."""

    trail = models.ForeignKey(
        HanselTrail,
        on_delete=models.CASCADE,
        related_name="authorities",
    )

    authority_path = models.CharField(
        max_length=500,
    )

    class Meta:
        ordering = [
            "pk",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "trail",
                    "authority_path",
                ],
                name="unique_hansel_trail_authority",
            ),
        ]

    def __str__(self):
        return self.authority_path


# ======================================================================
# END: HANSEL_TRAIL_MODEL
# ======================================================================