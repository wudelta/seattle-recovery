# ======================================================================
# FILE: aurora/subsystems/planning/services/workflow.py
# START: PLANNING_WORKER_WORKFLOW
# ======================================================================

from django.db import transaction

from aurora.models import ExecutionStatus, Initiative, Phase
from aurora.subsystems.planning.services.lifecycle import (
    approve_phase_completion,
    establish_initiative_work,
    request_initiative_completion,
)
from aurora.subsystems.planning.services.lifecycle.exceptions import (
    PlanningLifecycleError,
)
from aurora.subsystems.planning.services.time_tracking import (
    PlanningTimeTrackingError,
    get_executable_step,
)
from aurora.subsystems.planning.services.validation import (
    PlanningValidationError,
    validate_and_complete_step,
)


class PlanningWorkflowError(RuntimeError):
    """Raised when a worker-facing Planning workflow cannot proceed."""


def _serialize_step(step) -> dict[str, object]:
    """Return the minimal worker-facing identity for one Step."""
    return {
        "id": step.pk,
        "title": step.title,
        "status": step.status,
        "phase_id": step.phase_id,
        "initiative_id": step.phase.initiative_id,
    }


def _get_active_initiative(
    user,
) -> Initiative:
    """Resolve the single ACTIVE Initiative assigned to one worker."""
    active_initiatives = list(
        Initiative.objects.filter(
            assigned_to=user,
            status=ExecutionStatus.ACTIVE,
        ).order_by(
            "pk",
        )
    )

    if len(active_initiatives) != 1:
        raise PlanningWorkflowError(
            "The worker must have exactly one ACTIVE Initiative."
        )

    return active_initiatives[0]


def _get_active_phase(
    initiative: Initiative,
    user,
) -> Phase:
    """Resolve the single ACTIVE Phase for one ACTIVE Initiative."""
    active_phases = list(
        Phase.objects.filter(
            initiative=initiative,
            assigned_to=user,
            status=ExecutionStatus.ACTIVE,
        ).order_by(
            "position",
            "pk",
        )
    )

    if len(active_phases) != 1:
        raise PlanningWorkflowError(
            "The ACTIVE Initiative must have exactly one ACTIVE Phase."
        )

    return active_phases[0]


def complete_current_work(
    user,
    *,
    validation_notes: str,
) -> dict[str, object]:
    """
    Validate and complete the current executable Step.

    The workflow advances automatically only while no human-review boundary
    has been reached.
    """
    try:
        step = get_executable_step(
            user
        )
    except PlanningTimeTrackingError as exc:
        raise PlanningWorkflowError(
            str(exc)
        ) from exc

    initiative = step.phase.initiative

    try:
        with transaction.atomic():
            lifecycle = validate_and_complete_step(
                step=step,
                user=user,
                validation_notes=validation_notes,
            )

            phase_completion = lifecycle[
                "phase_completion"
            ]

            if phase_completion["review_required"]:
                return {
                    "state": "PHASE_REVIEW_REQUIRED",
                    "completed_step": lifecycle["step"],
                    "phase_completion": phase_completion,
                    "initiative_completion": lifecycle[
                        "initiative_completion"
                    ],
                    "next_step": None,
                }

            initiative_completion = lifecycle[
                "initiative_completion"
            ]

            if (
                initiative_completion is not None
                and initiative_completion["review_required"]
            ):
                return {
                    "state": "INITIATIVE_REVIEW_REQUIRED",
                    "completed_step": lifecycle["step"],
                    "phase_completion": phase_completion,
                    "initiative_completion": initiative_completion,
                    "next_step": None,
                }

            next_step = establish_initiative_work(
                initiative,
                user,
            )

            return {
                "state": "NEXT_STEP_READY",
                "completed_step": lifecycle["step"],
                "phase_completion": phase_completion,
                "initiative_completion": initiative_completion,
                "next_step": _serialize_step(
                    next_step
                ),
            }

    except (
        PlanningLifecycleError,
        PlanningValidationError,
    ) as exc:
        raise PlanningWorkflowError(
            str(exc)
        ) from exc


def approve_current_phase(
    user,
) -> dict[str, object]:
    """
    Approve the current Phase and establish the next permitted worker action.

    Initiative completion remains an explicit human-review boundary.
    """
    initiative = _get_active_initiative(
        user,
    )

    phase = _get_active_phase(
        initiative,
        user,
    )

    try:
        with transaction.atomic():
            phase_completion = approve_phase_completion(
                phase
            )

            initiative_completion = request_initiative_completion(
                initiative,
                auto=False,
            )

            if initiative_completion["review_required"]:
                return {
                    "state": "INITIATIVE_REVIEW_REQUIRED",
                    "phase_completion": phase_completion,
                    "initiative_completion": initiative_completion,
                    "next_step": None,
                }

            next_step = establish_initiative_work(
                initiative,
                user,
            )

            return {
                "state": "NEXT_STEP_READY",
                "phase_completion": phase_completion,
                "initiative_completion": initiative_completion,
                "next_step": _serialize_step(
                    next_step
                ),
            }

    except PlanningLifecycleError as exc:
        raise PlanningWorkflowError(
            str(exc)
        ) from exc


# ======================================================================
# END: PLANNING_WORKER_WORKFLOW
# ======================================================================