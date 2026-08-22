# ======================================================================
# FILE: aurora/subsystems/planning/services/lifecycle/orchestration.py
# START: PLANNING_LIFECYCLE_ORCHESTRATION
# ======================================================================

from django.db import transaction

from aurora.models import Step

from aurora.subsystems.planning.services.lifecycle.exceptions import (
    PlanningLifecycleError,
)
from aurora.subsystems.planning.services.lifecycle.initiative import (
    activate_initiative,
    request_initiative_completion,
)
from aurora.subsystems.planning.services.lifecycle.phase import (
    activate_phase,
    request_phase_completion,
)
from aurora.subsystems.planning.services.lifecycle.step import (
    activate_step,
    complete_step,
)


def activate_step_hierarchy(
    step: Step,
    user,
) -> Step:
    """
    Establish one Step as the lifecycle-authoritative resume point.

    The Step's actual ORM ancestry determines the Initiative and Phase.
    UserPosition is intentionally not consulted.

    Activation changes Planning lifecycle state only. It never starts,
    stops, or otherwise mutates TimeEntry records.
    """

    if step is None or not step.pk:
        raise PlanningLifecycleError(
            "A persisted Step is required."
        )

    if not user or not getattr(user, "is_authenticated", False):
        raise PlanningLifecycleError(
            "An authenticated user is required to activate Planning work."
        )

    with transaction.atomic():
        locked_step = (
            Step.objects
            .select_for_update()
            .select_related(
                "phase",
                "phase__initiative",
            )
            .get(pk=step.pk)
        )

        phase = locked_step.phase
        initiative = phase.initiative

        if initiative.assigned_to_id != user.pk:
            raise PlanningLifecycleError(
                "The Step's Initiative is not assigned to this user."
            )

        if phase.assigned_to_id != user.pk:
            raise PlanningLifecycleError(
                "The Step's Phase is not assigned to this user."
            )

        activate_initiative(
            initiative
        )

        activate_phase(
            phase
        )

        activated_step = activate_step(
            locked_step
        )

    return activated_step


def complete_step_and_evaluate_parents(
    step: Step,
    user,
    *,
    auto_phase: bool = False,
    auto_initiative: bool = False,
) -> dict[str, object]:
    """
    Complete one Step and evaluate parent completion opportunities.

    Phase and Initiative automation are independent. AUTO bypasses only
    human approval; each level still performs its normal eligibility checks.
    """

    completed_step = complete_step(
        step,
        user,
    )

    phase = completed_step.phase

    phase_result = request_phase_completion(
        phase,
        auto=auto_phase,
    )

    result = {
        "step": {
            "id": completed_step.pk,
            "title": completed_step.title,
            "status": completed_step.status,
            "completed_by": (
                completed_step.completed_by.username
                if completed_step.completed_by
                else None
            ),
            "completed_at": (
                completed_step.completed_at.isoformat()
                if completed_step.completed_at
                else None
            ),
        },
        "phase_completion": phase_result,
        "initiative_completion": None,
    }

    if not phase_result["completed"]:
        return result

    initiative = phase.initiative

    initiative_result = request_initiative_completion(
        initiative,
        auto=auto_initiative,
    )

    result["initiative_completion"] = initiative_result

    return result


# ======================================================================
# END: PLANNING_LIFECYCLE_ORCHESTRATION
# ======================================================================