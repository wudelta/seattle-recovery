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


# ======================================================================
# END: DECISION_ENGINE_WORK_SCHEMA
# ======================================================================
