# ======================================================================
# FILE: aurora/subsystems/planning/services/validation.py
# START: PLANNING_STEP_VALIDATION_SERVICE
# ======================================================================

from django.db import transaction
from django.utils import timezone

from aurora.models import Step, StepValidation
from aurora.subsystems.planning.services.lifecycle import (
    complete_step_and_evaluate_parents,
)


class PlanningValidationError(RuntimeError):
    """Raised when Step validation evidence cannot be persisted."""


def validate_and_complete_step(
    *,
    step: Step,
    user,
    validation_notes: str,
    auto_phase: bool = False,
    auto_initiative: bool = False,
):
    """
    Persist validation evidence and immediately complete one Step.

    Validation evidence and lifecycle completion are one database transaction.
    """

    if step is None or not step.pk:
        raise PlanningValidationError(
            "A persisted Step is required."
        )

    if not user or not getattr(user, "is_authenticated", False):
        raise PlanningValidationError(
            "An authenticated validator is required."
        )

    notes = str(validation_notes).strip()

    if not notes:
        raise PlanningValidationError(
            "Validation evidence is required."
        )

    with transaction.atomic():
        locked = (
            Step.objects
            .select_for_update()
            .get(pk=step.pk)
        )

        validation, _created = StepValidation.objects.update_or_create(
            step=locked,
            defaults={
                "notes": notes,
                "validated_by": user,
                "validated_at": timezone.now(),
            },
        )

        # Retain legacy Step-level validation fields during staged migration.
        locked.validation_notes = notes
        locked.validated_by = user
        locked.save(
            update_fields=[
                "validation_notes",
                "validated_by",
            ]
        )

        lifecycle = complete_step_and_evaluate_parents(
            locked,
            user,
            auto_phase=auto_phase,
            auto_initiative=auto_initiative,
        )

    return lifecycle


# ======================================================================
# END: PLANNING_STEP_VALIDATION_SERVICE
# ======================================================================