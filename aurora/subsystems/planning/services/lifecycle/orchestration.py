# ======================================================================
# FILE: aurora/subsystems/planning/services/lifecycle/orchestration.py
# START: PLANNING_LIFECYCLE_ORCHESTRATION
# ======================================================================

from django.db import transaction

from aurora.models import ExecutionStatus, Initiative, Phase, Step

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


def establish_initiative_work(
    initiative: Initiative,
    user,
) -> Step:
    """
    Establish a complete executable path for one Initiative.

    Existing ACTIVE Phase and Step state is treated as an explicit resume
    position and takes precedence over positional defaults.

    When an ACTIVE child does not exist, Planning selects the first unfinished
    child by position. COMPLETED and CANCELLED children are never selected.

    Position therefore defines predictable default execution order without
    preventing a developer from explicitly activating a different Phase or
    Step.
    """

    if initiative is None or not initiative.pk:
        raise PlanningLifecycleError(
            "A persisted Initiative is required."
        )

    if not user or not getattr(user, "is_authenticated", False):
        raise PlanningLifecycleError(
            "An authenticated user is required to activate Planning work."
        )

    with transaction.atomic():
        locked_initiative = (
            Initiative.objects
            .select_for_update()
            .get(pk=initiative.pk)
        )

        if locked_initiative.assigned_to_id != user.pk:
            raise PlanningLifecycleError(
                "The Initiative is not assigned to this user."
            )

        activate_initiative(
            locked_initiative
        )

        active_phases = list(
            Phase.objects
            .select_for_update()
            .filter(
                initiative=locked_initiative,
                assigned_to=user,
                status=ExecutionStatus.ACTIVE,
            )
            .order_by(
                "position",
                "pk",
            )
        )

        if len(active_phases) > 1:
            raise PlanningLifecycleError(
                "The ACTIVE Initiative has multiple ACTIVE Phases."
            )

        if active_phases:
            phase = active_phases[0]
        else:
            phase = (
                Phase.objects
                .select_for_update()
                .filter(
                    initiative=locked_initiative,
                    assigned_to=user,
                )
                .exclude(
                    status__in=[
                        ExecutionStatus.COMPLETED,
                        ExecutionStatus.CANCELLED,
                    ]
                )
                .order_by(
                    "position",
                    "pk",
                )
                .first()
            )

            if phase is None:
                raise PlanningLifecycleError(
                    "The ACTIVE Initiative has no unfinished Phase "
                    "assigned to this user."
                )

        active_steps = list(
            Step.objects
            .select_for_update()
            .filter(
                phase=phase,
                status=ExecutionStatus.ACTIVE,
            )
            .order_by(
                "position",
                "pk",
            )
        )

        if len(active_steps) > 1:
            raise PlanningLifecycleError(
                "The selected Phase has multiple ACTIVE Steps."
            )

        if active_steps:
            step = active_steps[0]
        else:
            step = (
                Step.objects
                .select_for_update()
                .filter(
                    phase=phase,
                )
                .exclude(
                    status__in=[
                        ExecutionStatus.COMPLETED,
                        ExecutionStatus.CANCELLED,
                    ]
                )
                .order_by(
                    "position",
                    "pk",
                )
                .first()
            )

            if step is None:
                raise PlanningLifecycleError(
                    "The selected Phase has no unfinished Step."
                )

        return activate_step_hierarchy(
            step,
            user,
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