# ======================================================================
# FILE: aurora/subsystems/planning/services/lifecycle/phase.py
# START: PLANNING_PHASE_LIFECYCLE
# ======================================================================

from django.db import transaction
from django.utils import timezone

from aurora.models import ExecutionStatus, Phase

from aurora.subsystems.planning.services.lifecycle.exceptions import (
    PlanningLifecycleError,
)


def activate_phase(phase: Phase) -> Phase:
    """Make one Phase the ACTIVE resume Phase within its Initiative."""

    if phase is None or not phase.pk:
        raise PlanningLifecycleError(
            "A persisted Phase is required."
        )

    if phase.status == ExecutionStatus.COMPLETED:
        raise PlanningLifecycleError(
            "A completed Phase cannot be activated."
        )

    if phase.status == ExecutionStatus.CANCELLED:
        raise PlanningLifecycleError(
            "A cancelled Phase cannot be activated."
        )

    with transaction.atomic():
        locked = (
            Phase.objects
            .select_for_update()
            .select_related("initiative")
            .get(pk=phase.pk)
        )

        (
            Phase.objects
            .select_for_update()
            .filter(
                initiative=locked.initiative,
                status=ExecutionStatus.ACTIVE,
            )
            .exclude(pk=locked.pk)
            .update(
                status=ExecutionStatus.PAUSED,
            )
        )

        if locked.status != ExecutionStatus.ACTIVE:
            locked.status = ExecutionStatus.ACTIVE
            locked.save(
                update_fields=["status"]
            )

    return locked


def pause_phase(phase: Phase) -> Phase:
    """Pause one Phase without changing child Step lifecycle state."""

    if phase is None or not phase.pk:
        raise PlanningLifecycleError(
            "A persisted Phase is required."
        )

    with transaction.atomic():
        locked = (
            Phase.objects
            .select_for_update()
            .get(pk=phase.pk)
        )

        if locked.status != ExecutionStatus.ACTIVE:
            raise PlanningLifecycleError(
                "Only an ACTIVE Phase can be paused."
            )

        locked.status = ExecutionStatus.PAUSED
        locked.save(
            update_fields=["status"]
        )

    return locked


def evaluate_phase_completion(phase: Phase) -> dict[str, object]:
    """
    Evaluate whether a Phase is eligible for completion.

    This function is read-only. It reports eligibility and supporting
    evidence but performs no lifecycle mutation.

    CANCELLED Steps do not block completion. A Phase containing no
    executable Steps is not automatically eligible for completion.
    """

    if phase is None or not phase.pk:
        raise PlanningLifecycleError(
            "A persisted Phase is required."
        )

    current = (
        Phase.objects
        .prefetch_related("steps")
        .get(pk=phase.pk)
    )

    if current.status == ExecutionStatus.COMPLETED:
        return {
            "eligible": False,
            "phase_id": current.pk,
            "phase": current.title,
            "reason": "Phase is already completed.",
            "step_counts": {},
            "blocking_step_ids": [],
        }

    if current.status == ExecutionStatus.CANCELLED:
        return {
            "eligible": False,
            "phase_id": current.pk,
            "phase": current.title,
            "reason": "Cancelled Phases are not eligible for completion.",
            "step_counts": {},
            "blocking_step_ids": [],
        }

    steps = list(
        current.steps.all().order_by(
            "position",
            "pk",
        )
    )

    counts = {
        "total": len(steps),
        "completed": 0,
        "cancelled": 0,
        "unfinished": 0,
    }

    blocking_step_ids = []

    for step in steps:
        if step.status == ExecutionStatus.COMPLETED:
            counts["completed"] += 1
            continue

        if step.status == ExecutionStatus.CANCELLED:
            counts["cancelled"] += 1
            continue

        counts["unfinished"] += 1
        blocking_step_ids.append(step.pk)

    executable_count = (
        counts["total"]
        - counts["cancelled"]
    )

    if executable_count == 0:
        return {
            "eligible": False,
            "phase_id": current.pk,
            "phase": current.title,
            "reason": (
                "Phase has no non-cancelled Steps. "
                "Completion requires explicit review."
            ),
            "step_counts": counts,
            "blocking_step_ids": [],
        }

    if blocking_step_ids:
        return {
            "eligible": False,
            "phase_id": current.pk,
            "phase": current.title,
            "reason": (
                f"{len(blocking_step_ids)} non-cancelled "
                "Step(s) remain unfinished."
            ),
            "step_counts": counts,
            "blocking_step_ids": blocking_step_ids,
        }

    return {
        "eligible": True,
        "phase_id": current.pk,
        "phase": current.title,
        "reason": "All non-cancelled Steps are completed.",
        "step_counts": counts,
        "blocking_step_ids": [],
    }


def complete_phase(phase: Phase) -> Phase:
    """
    Complete one Phase after deterministic eligibility validation.

    This transition always re-evaluates eligibility immediately before
    mutation. It cannot be used to bypass the completion rules.
    """

    if phase is None or not phase.pk:
        raise PlanningLifecycleError(
            "A persisted Phase is required."
        )

    with transaction.atomic():
        locked = (
            Phase.objects
            .select_for_update()
            .get(pk=phase.pk)
        )

        if locked.status == ExecutionStatus.COMPLETED:
            raise PlanningLifecycleError(
                "This Phase is already completed."
            )

        if locked.status == ExecutionStatus.CANCELLED:
            raise PlanningLifecycleError(
                "A cancelled Phase cannot be completed."
            )

        eligibility = evaluate_phase_completion(
            locked
        )

        if not eligibility["eligible"]:
            raise PlanningLifecycleError(
                "Phase is not eligible for completion: "
                f"{eligibility['reason']}"
            )

        locked.status = ExecutionStatus.COMPLETED
        locked.completed_at = timezone.now()
        locked.save(
            update_fields=[
                "status",
                "completed_at",
            ]
        )

    return locked


def request_phase_completion(
    phase: Phase,
    *,
    auto: bool = False,
) -> dict[str, object]:
    """
    Evaluate a Phase-completion request.

    REVIEW mode reports eligibility but performs no mutation.

    AUTO mode uses the same eligibility evaluation and, when eligible,
    performs the normal complete_phase() transition.

    Automation therefore bypasses human approval only. It never bypasses
    lifecycle validation.
    """

    eligibility = evaluate_phase_completion(
        phase
    )

    result = {
        "mode": (
            "AUTO"
            if auto
            else "REVIEW"
        ),
        "eligible": eligibility["eligible"],
        "phase_id": eligibility["phase_id"],
        "phase": eligibility["phase"],
        "reason": eligibility["reason"],
        "step_counts": eligibility["step_counts"],
        "blocking_step_ids": (
            eligibility["blocking_step_ids"]
        ),
        "review_required": False,
        "completed": False,
    }

    if not eligibility["eligible"]:
        return result

    if not auto:
        result["review_required"] = True
        return result

    completed = complete_phase(
        phase
    )

    result["completed"] = True
    result["review_required"] = False
    result["completed_at"] = (
        completed.completed_at.isoformat()
    )

    return result


def approve_phase_completion(phase: Phase) -> dict[str, object]:
    """
    Approve a previously surfaced Phase-completion opportunity.

    Eligibility is checked again at approval time so stale UI state cannot
    force an invalid lifecycle transition.
    """

    completed = complete_phase(
        phase
    )

    return {
        "decision": "APPROVED",
        "phase_id": completed.pk,
        "phase": completed.title,
        "completed": True,
        "completed_at": completed.completed_at.isoformat(),
    }


def reject_phase_completion(
    phase: Phase,
    *,
    reason: str = "",
) -> dict[str, object]:
    """
    Reject a Phase-completion opportunity without changing Planning state.

    Rejection evidence is returned to the caller for presentation or future
    persistence. Planning does not yet own a durable review-decision model.
    """

    if phase is None or not phase.pk:
        raise PlanningLifecycleError(
            "A persisted Phase is required."
        )

    current = Phase.objects.get(
        pk=phase.pk
    )

    return {
        "decision": "REJECTED",
        "phase_id": current.pk,
        "phase": current.title,
        "completed": False,
        "reason": reason.strip(),
    }

# ======================================================================
# END: PLANNING_PHASE_LIFECYCLE
# ======================================================================
