# ======================================================================
# FILE: aurora/subsystems/planning/models.py
# START: RUNTIME_IMPORTS_AND_DEPENDENCIES
# ======================================================================

from django.conf import settings
from django.db import models

# ======================================================================
# END: RUNTIME_IMPORTS_AND_DEPENDENCIES
# ======================================================================


# ======================================================================
# FILE: aurora/subsystems/planning/models.py
# START: EXECUTION_PLAN_CHOICES
# ======================================================================
class ExecutionStatus(models.TextChoices):
    """Shared lifecycle states for execution planning."""

    PLANNED = "PLANNED", "Planned"
    ACTIVE = "ACTIVE", "Active"
    PAUSED = "PAUSED", "Paused"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class EstimateConfidence(models.TextChoices):
    """Confidence levels for implementation effort estimates."""

    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"


class RiskLevel(models.TextChoices):
    """Potential implementation impact associated with a planning step."""

    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"
    CRITICAL = "CRITICAL", "Critical"
# ======================================================================
# END: EXECUTION_PLAN_CHOICES
# ======================================================================


# ======================================================================
# FILE: aurora/subsystems/planning/models.py
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


# ======================================================================
# FILE: aurora/subsystems/planning/models.py
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


# ======================================================================
# FILE: aurora/subsystems/planning/models.py
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

# ======================================================================
# FILE: aurora/subsystems/planning/models.py
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

# ======================================================================
# FILE: aurora/subsystems/planning/models.py
# START: STEP_SUPPORTING_MODELS
# ======================================================================
class StepDocument(models.Model):
    """The engineering narrative associated with a planning step."""

    step = models.OneToOneField(
        Step,
        on_delete=models.CASCADE,
        related_name="document",
    )

    technical_design = models.TextField(
        blank=True,
        help_text=(
            "The intended technical approach for implementing this step."
        ),
    )

    dependencies = models.TextField(
        blank=True,
        help_text=(
            "Components, services, decisions, or prior work required "
            "by this step."
        ),
    )

    assumptions = models.TextField(
        blank=True,
        help_text=(
            "Known assumptions that influence the implementation approach."
        ),
    )

    implementation_notes = models.TextField(
        blank=True,
        help_text=(
            "Important observations and decisions recorded during "
            "implementation."
        ),
    )

    discussion = models.TextField(
        blank=True,
        help_text=(
            "Planning discussion and design history relevant to this step."
        ),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Document / {self.step}"


class StepValidation(models.Model):
    """The validation requirements and evidence for a planning step."""

    step = models.OneToOneField(
        Step,
        on_delete=models.CASCADE,
        related_name="validation",
    )

    description = models.TextField(
        blank=True,
        help_text=(
            "Deterministic evidence required to validate this step."
        ),
    )

    notes = models.TextField(
        blank=True,
        help_text=(
            "Observed validation results and supporting evidence."
        ),
    )

    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="step_validations",
    )

    validated_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Validation / {self.step}"


class StepFile(models.Model):
    """A planned or observed repository file impact for a planning step."""

    class Role(models.TextChoices):
        PLANNED = "PLANNED", "Planned"
        ACTUAL = "ACTUAL", "Actual"

    step = models.ForeignKey(
        Step,
        on_delete=models.CASCADE,
        related_name="files",
    )

    file_path = models.CharField(
        max_length=500,
        help_text=(
            "Repository-relative path planned for or observed during "
            "implementation."
        ),
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        db_index=True,
    )

    reason = models.TextField(
        blank=True,
        help_text=(
            "Why this file is expected to change or why it was modified."
        ),
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="step_files_recorded",
        help_text=(
            "The user who recorded this file impact. Blank values may "
            "represent deterministic or automated discovery."
        ),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["role", "file_path"]
        constraints = [
            models.UniqueConstraint(
                fields=["step", "file_path", "role"],
                name="unique_step_file_path_per_role",
            ),
        ]

    def __str__(self):
        return (
            f"{self.step} / "
            f"{self.get_role_display()} / "
            f"{self.file_path}"
        )
# ======================================================================
# END: STEP_SUPPORTING_MODELS
# ======================================================================


# ======================================================================
# FILE: aurora/subsystems/planning/models.py
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


# ======================================================================
# FILE: aurora/subsystems/planning/models.py
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