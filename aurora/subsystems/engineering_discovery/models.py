# ======================================================================
# FILE: aurora/subsystems/engineering_discovery/models.py
# START: ENGINEERING_FINDING_SCHEMA
# ======================================================================

from django.conf import settings
from django.db import models

from aurora.subsystems.planning.models import Phase, Step


class EngineeringFindingCategory(models.TextChoices):
    BROKEN_HANSEL_TRAIL = "BROKEN_HANSEL_TRAIL", "Broken Hansel Trail"
    DEAD_END = "DEAD_END", "Dead End"
    NEEDED_SOLUTION = "NEEDED_SOLUTION", "Needed Solution"
    INEFFICIENT_NAVIGATION = "INEFFICIENT_NAVIGATION", "Inefficient Navigation"
    AUTHORITY_CONFLICT = "AUTHORITY_CONFLICT", "Authority Conflict"
    BOUNDARY_VIOLATION = "BOUNDARY_VIOLATION", "Boundary Violation"
    VALIDATION_GAP = "VALIDATION_GAP", "Validation Gap"


class EngineeringFindingBlockingClassification(models.TextChoices):
    BLOCKING = "BLOCKING", "Blocking"
    NON_BLOCKING = "NON_BLOCKING", "Non-blocking"


class EngineeringFindingResolutionState(models.TextChoices):
    UNRESOLVED = "UNRESOLVED", "Unresolved"
    RESOLVED = "RESOLVED", "Resolved"


class EngineeringFinding(models.Model):
    """
    Persist one evidence-backed engineering problem encountered during required work.

    The originating Planning Step is the provenance anchor. Phase, Initiative,
    and Project remain derivable through the Planning hierarchy and are not
    redundantly persisted.
    """

    originating_step = models.ForeignKey(
        Step,
        on_delete=models.PROTECT,
        related_name="engineering_findings",
    )
    remedial_phase = models.ForeignKey(
        Phase,
        on_delete=models.PROTECT,
        related_name="engineering_findings_remediated",
        null=True,
        blank=True,
        help_text=(
            "Planning Phase created to resolve this BLOCKING finding, when routed."
        ),
    )
    discovered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="engineering_findings_discovered",
    )

    category = models.CharField(
        max_length=40,
        choices=EngineeringFindingCategory.choices,
        db_index=True,
    )
    blocking_classification = models.CharField(
        max_length=20,
        choices=EngineeringFindingBlockingClassification.choices,
        db_index=True,
    )
    resolution_state = models.CharField(
        max_length=20,
        choices=EngineeringFindingResolutionState.choices,
        default=EngineeringFindingResolutionState.UNRESOLVED,
        db_index=True,
    )

    observed_condition = models.TextField(
        help_text="Concrete engineering problem that was encountered.",
    )
    evidence = models.TextField(
        blank=True,
        help_text=(
            "Concrete repository or execution evidence supporting the finding. "
            "May be blank when deterministic reproduction steps are sufficient."
        ),
    )
    steps_to_reproduce = models.TextField(
        blank=True,
        help_text=(
            "Deterministic procedure that reproduces or exposes the observed "
            "condition, when applicable."
        ),
    )

    resolution_evidence = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "pk"]

    def __str__(self):
        return (
            f"EngineeringFinding {self.pk}: "
            f"{self.category} / Step {self.originating_step_id}"
        )


# ======================================================================
# END: ENGINEERING_FINDING_SCHEMA
# ======================================================================
