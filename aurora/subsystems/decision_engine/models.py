# ======================================================================
# FILE: aurora/subsystems/decision_engine/models.py
# START: DECISION_ENGINE_WORK_SCHEMA
# ======================================================================

from django.conf import settings
from django.db import models


class DecisionEngineWork(models.Model):
    """
    Persist one durable organization-level body of work after explicit
    Decision Engine commit.

    This model deliberately does not encode intake disposition, aggregation,
    Planning linkage, approval state, assignment, priority, or execution state.
    Those concerns belong to later authoritative workflow.
    """

    title = models.CharField(max_length=255)
    description = models.TextField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="decision_engine_work_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "pk"]

    def __str__(self):
        return f"DecisionEngineWork {self.pk}: {self.title}"


class DecisionEngineSourceType(models.TextChoices):
    """Source authorities that may provide Decision Engine intake."""

    DELTA_NOTE = "DELTA_NOTE", "Delta Note"
    ENGINEERING_FINDING = "ENGINEERING_FINDING", "Engineering Finding"


class DecisionEngineDisposition(models.TextChoices):
    """Organization-level Decision Engine intake dispositions."""

    OPEN = "OPEN", "Open"
    DEFERRED = "DEFERRED", "Deferred"
    NEEDS_MITIGATION = "NEEDS_MITIGATION", "Needs Mitigation"
    WORK_COMMITTED = "WORK_COMMITTED", "Work Committed"
    REJECTED = "REJECTED", "Rejected"
    WITHDRAWN = "WITHDRAWN", "Withdrawn"


class DecisionEngineIntakeDisposition(models.Model):
    """Persist Decision Engine disposition without replacing source lifecycle."""

    source_type = models.CharField(
        max_length=32,
        choices=DecisionEngineSourceType.choices,
        db_index=True,
    )
    source_id = models.PositiveBigIntegerField()

    delta_note = models.ForeignKey(
        "DeltaNotesEntry",
        on_delete=models.SET_NULL,
        related_name="decision_engine_dispositions",
        null=True,
        blank=True,
    )
    engineering_finding = models.ForeignKey(
        "EngineeringFinding",
        on_delete=models.SET_NULL,
        related_name="decision_engine_dispositions",
        null=True,
        blank=True,
    )

    disposition = models.CharField(
        max_length=32,
        choices=DecisionEngineDisposition.choices,
        db_index=True,
    )
    resolving_work = models.ForeignKey(
        DecisionEngineWork,
        on_delete=models.PROTECT,
        related_name="intake_dispositions",
        null=True,
        blank=True,
    )

    authorized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="decision_engine_dispositions_authorized",
    )
    authorized_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()

    class Meta:
        ordering = ["authorized_at", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["source_type", "source_id"],
                name="uniq_decision_engine_source_disposition",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        disposition=DecisionEngineDisposition.WORK_COMMITTED,
                        resolving_work__isnull=False,
                    )
                    | (
                        ~models.Q(
                            disposition=DecisionEngineDisposition.WORK_COMMITTED
                        )
                        & models.Q(resolving_work__isnull=True)
                    )
                ),
                name="decision_engine_resolving_work_matches_disposition",
            ),
        ]

    def __str__(self):
        return f"{self.source_type}:{self.source_id} → {self.disposition}"


# ======================================================================
# END: DECISION_ENGINE_WORK_SCHEMA
# ======================================================================
