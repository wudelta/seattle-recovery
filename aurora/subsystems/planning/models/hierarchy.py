from django.conf import settings
from django.db import models

from .choices import EstimateConfidence, ExecutionStatus, RiskLevel


# START: PROJECT_MODEL
# ======================================================================
class Project(models.Model):
    """A product, application, or engineering domain containing initiatives."""

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    color = models.CharField(
        max_length=32,
        blank=True,
        help_text="Optional presentation color for planning interfaces.",
    )

    icon = models.CharField(
        max_length=64,
        blank=True,
        help_text="Optional icon identifier for planning interfaces.",
    )

    status = models.CharField(
        max_length=20,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.PLANNED,
        db_index=True,
    )

    position = models.PositiveIntegerField(default=0)

    active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=(
            "Whether this project remains available for normal engineering work."
        ),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="projects_created",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="projects_assigned",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["position", "title"]

    def __str__(self):
        return self.title
# ======================================================================
# END: PROJECT_MODEL
# ======================================================================

# START: INITIATIVE_MODEL
# ======================================================================
class Initiative(models.Model):
    """A top-level engineering objective within a Project."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="initiatives",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.PLANNED,
        db_index=True,
    )

    position = models.PositiveIntegerField(default=0)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="initiatives_created",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="initiatives_assigned",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["position", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "position"],
                name="unique_initiative_position_per_project",
            ),
        ]

    def __str__(self):
        return f"{self.project} / {self.title}"
# ======================================================================
# END: INITIATIVE_MODEL
# ======================================================================

# START: PHASE_MODEL
# ======================================================================
class Phase(models.Model):
    """A milestone within an Initiative."""

    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name="phases",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.PLANNED,
        db_index=True,
    )

    position = models.PositiveIntegerField(default=0)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="phases_created",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="phases_assigned",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["position", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["initiative", "position"],
                name="unique_phase_position_per_initiative",
            ),
        ]

    def __str__(self):
        return f"{self.initiative} / {self.title}"
# ======================================================================
# END: PHASE_MODEL
# ======================================================================

# START: STEP_MODEL
# ======================================================================
class Step(models.Model):
    """A single validated implementation task within a Phase."""

    phase = models.ForeignKey(
        Phase,
        on_delete=models.CASCADE,
        related_name="steps",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.PLANNED,
        db_index=True,
    )

    position = models.PositiveIntegerField(default=0)

    estimated_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated implementation effort in minutes.",
    )

    estimate_confidence = models.CharField(
        max_length=10,
        choices=EstimateConfidence.choices,
        null=True,
        blank=True,
        help_text="Confidence in the current implementation estimate.",
    )

    risk_level = models.CharField(
        max_length=10,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
        db_index=True,
        help_text="Potential impact if this implementation step fails.",
    )

    risk_description = models.TextField(
        blank=True,
        help_text="Reason this step carries implementation or operational risk.",
    )

    validation_description = models.TextField(
        blank=True,
        help_text="Deterministic evidence required to validate this step.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="steps_created",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="steps_assigned",
    )

    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="validated_steps",
    )

    validation_notes = models.TextField(
        blank=True,
        help_text="Observed validation results and supporting evidence.",
    )

    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="completed_steps",
        help_text=(
            "Developer who completed this Step. "
            "Historical attribution is independent of current Phase assignment."
        ),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["position", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["phase", "position"],
                name="unique_step_position_per_phase",
            ),
        ]

    def __str__(self):
        return f"{self.phase} / {self.title}"
# ======================================================================
# END: STEP_MODEL
# ======================================================================
