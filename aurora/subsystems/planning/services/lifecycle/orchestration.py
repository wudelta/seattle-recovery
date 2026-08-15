# ======================================================================
# FILE: aurora/subsystems/planning/services/lifecycle/orchestration.py
# START: PLANNING_LIFECYCLE_ORCHESTRATION
# ======================================================================

from aurora.models import Step

from aurora.subsystems.planning.services.lifecycle.initiative import (
    request_initiative_completion,
)
from aurora.subsystems.planning.services.lifecycle.phase import (
    request_phase_completion,
)
from aurora.subsystems.planning.services.lifecycle.step import (
    complete_step,
)


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