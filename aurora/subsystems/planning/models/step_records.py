from django.conf import settings
from django.db import models

from .hierarchy import Step


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
