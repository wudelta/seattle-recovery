from django.conf import settings
from django.db import models

from .hierarchy import Initiative


# START: INITIATIVE_SOURCE_DELTA_NOTE_MODEL
# ======================================================================
class InitiativeSourceDeltaNote(models.Model):
    """Link one Planning Initiative to one source Delta Note."""

    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name="source_delta_notes",
    )

    delta_note = models.ForeignKey(
        "aurora.DeltaNotesEntry",
        on_delete=models.PROTECT,
        related_name="planning_initiatives",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [
            "created_at",
            "pk",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "initiative",
                    "delta_note",
                ],
                name="unique_initiative_source_delta_note",
            ),
        ]

    def __str__(self):
        return (
            f"{self.initiative} / "
            f"Delta Note {self.delta_note_id}"
        )
# ======================================================================
# END: INITIATIVE_SOURCE_DELTA_NOTE_MODEL
# ======================================================================

# START: INITIATIVE_POST_MORTEM_MODEL
# ======================================================================


class InitiativePostMortem(models.Model):
    """Structured improvement evidence captured during Initiative closeout."""

    initiative = models.OneToOneField(
        Initiative,
        on_delete=models.CASCADE,
        related_name="post_mortem",
    )

    summary = models.TextField(
        blank=True,
        help_text=(
            "Concise retrospective summary of the completed Initiative."
        ),
    )

    successes = models.TextField(
        blank=True,
        help_text=(
            "Approaches, decisions, or workflow behavior worth preserving."
        ),
    )

    friction = models.TextField(
        blank=True,
        help_text=(
            "Observed problems, inefficiencies, surprises, or failed "
            "assumptions encountered during execution."
        ),
    )

    planning_improvements = models.TextField(
        blank=True,
        help_text=(
            "Durable improvements suggested for Planning contracts, "
            "estimation, lifecycle behavior, or execution workflow."
        ),
    )

    hansel_improvements = models.TextField(
        blank=True,
        help_text=(
            "Durable improvements suggested for Hansel routing, "
            "authority discovery, validation, or reconciliation."
        ),
    )

    follow_up = models.TextField(
        blank=True,
        help_text=(
            "Concrete improvement work that should be considered after "
            "Initiative closeout."
        ),
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="initiative_post_mortems",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Post-mortem / {self.initiative}"


# ======================================================================
# END: INITIATIVE_POST_MORTEM_MODEL
# ======================================================================
