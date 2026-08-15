# ======================================================================
# FILE: aurora/subsystems/planning/services/lifecycle/initiative.py
# START: PLANNING_INITIATIVE_LIFECYCLE
# ======================================================================

from django.db import transaction

from aurora.models import ExecutionStatus, Initiative

from aurora.subsystems.planning.services.lifecycle.exceptions import (
    PlanningLifecycleError,
)


def activate_initiative(initiative: Initiative) -> Initiative:
    """Make one Initiative the current ACTIVE Initiative for its assignee."""

    if initiative is None or not initiative.pk:
        raise PlanningLifecycleError(
            "A persisted Initiative is required."
        )

    if initiative.status == ExecutionStatus.COMPLETED:
        raise PlanningLifecycleError(
            "A completed Initiative cannot be activated."
        )

    if initiative.status == ExecutionStatus.CANCELLED:
        raise PlanningLifecycleError(
            "A cancelled Initiative cannot be activated."
        )

    with transaction.atomic():
        locked = (
            Initiative.objects
            .select_for_update()
            .select_related("assigned_to")
            .get(pk=initiative.pk)
        )

        (
            Initiative.objects
            .select_for_update()
            .filter(
                assigned_to=locked.assigned_to,
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


def pause_initiative(initiative: Initiative) -> Initiative:
    """Pause one Initiative without changing child lifecycle state."""

    if initiative is None or not initiative.pk:
        raise PlanningLifecycleError(
            "A persisted Initiative is required."
        )

    with transaction.atomic():
        locked = (
            Initiative.objects
            .select_for_update()
            .get(pk=initiative.pk)
        )

        if locked.status != ExecutionStatus.ACTIVE:
            raise PlanningLifecycleError(
                "Only an ACTIVE Initiative can be paused."
            )

        locked.status = ExecutionStatus.PAUSED
        locked.save(
            update_fields=["status"]
        )

    return locked

# ======================================================================
# END: PLANNING_INITIATIVE_LIFECYCLE
# ======================================================================


# ======================================================================
# FILE: aurora/subsystems/planning/services/lifecycle/initiative.py
# START: PLANNING_INITIATIVE_COMPLETION
# ======================================================================

from django.utils import timezone


def evaluate_initiative_completion(
    initiative: Initiative,
) -> dict[str, object]:
    """
    Evaluate whether an Initiative is eligible for completion.

    This function is read-only.

    CANCELLED Phases do not block completion. An Initiative containing no
    non-cancelled Phases requires explicit review and is not automatically
    eligible.
    """

    if initiative is None or not initiative.pk:
        raise PlanningLifecycleError(
            "A persisted Initiative is required."
        )

    current = (
        Initiative.objects
        .prefetch_related("phases")
        .get(pk=initiative.pk)
    )

    if current.status == ExecutionStatus.COMPLETED:
        return {
            "eligible": False,
            "initiative_id": current.pk,
            "initiative": current.title,
            "reason": "Initiative is already completed.",
            "phase_counts": {},
            "blocking_phase_ids": [],
        }

    if current.status == ExecutionStatus.CANCELLED:
        return {
            "eligible": False,
            "initiative_id": current.pk,
            "initiative": current.title,
            "reason": (
                "Cancelled Initiatives are not eligible for completion."
            ),
            "phase_counts": {},
            "blocking_phase_ids": [],
        }

    phases = list(
        current.phases.all().order_by(
            "position",
            "pk",
        )
    )

    counts = {
        "total": len(phases),
        "completed": 0,
        "cancelled": 0,
        "unfinished": 0,
    }

    blocking_phase_ids = []

    for phase in phases:
        if phase.status == ExecutionStatus.COMPLETED:
            counts["completed"] += 1
            continue

        if phase.status == ExecutionStatus.CANCELLED:
            counts["cancelled"] += 1
            continue

        counts["unfinished"] += 1
        blocking_phase_ids.append(phase.pk)

    executable_count = (
        counts["total"]
        - counts["cancelled"]
    )

    if executable_count == 0:
        return {
            "eligible": False,
            "initiative_id": current.pk,
            "initiative": current.title,
            "reason": (
                "Initiative has no non-cancelled Phases. "
                "Completion requires explicit review."
            ),
            "phase_counts": counts,
            "blocking_phase_ids": [],
        }

    if blocking_phase_ids:
        return {
            "eligible": False,
            "initiative_id": current.pk,
            "initiative": current.title,
            "reason": (
                f"{len(blocking_phase_ids)} non-cancelled "
                "Phase(s) remain unfinished."
            ),
            "phase_counts": counts,
            "blocking_phase_ids": blocking_phase_ids,
        }

    return {
        "eligible": True,
        "initiative_id": current.pk,
        "initiative": current.title,
        "reason": "All non-cancelled Phases are completed.",
        "phase_counts": counts,
        "blocking_phase_ids": [],
    }


def complete_initiative(
    initiative: Initiative,
) -> Initiative:
    """
    Complete one Initiative after deterministic eligibility validation.
    """

    if initiative is None or not initiative.pk:
        raise PlanningLifecycleError(
            "A persisted Initiative is required."
        )

    with transaction.atomic():
        locked = (
            Initiative.objects
            .select_for_update()
            .get(pk=initiative.pk)
        )

        if locked.status == ExecutionStatus.COMPLETED:
            raise PlanningLifecycleError(
                "This Initiative is already completed."
            )

        if locked.status == ExecutionStatus.CANCELLED:
            raise PlanningLifecycleError(
                "A cancelled Initiative cannot be completed."
            )

        eligibility = evaluate_initiative_completion(
            locked
        )

        if not eligibility["eligible"]:
            raise PlanningLifecycleError(
                "Initiative is not eligible for completion: "
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


def request_initiative_completion(
    initiative: Initiative,
    *,
    auto: bool = False,
) -> dict[str, object]:
    """
    Evaluate an Initiative-completion request.

    REVIEW mode reports eligibility without mutation.

    AUTO mode bypasses human approval but never lifecycle validation.
    """

    eligibility = evaluate_initiative_completion(
        initiative
    )

    result = {
        "mode": (
            "AUTO"
            if auto
            else "REVIEW"
        ),
        "eligible": eligibility["eligible"],
        "initiative_id": eligibility["initiative_id"],
        "initiative": eligibility["initiative"],
        "reason": eligibility["reason"],
        "phase_counts": eligibility["phase_counts"],
        "blocking_phase_ids": (
            eligibility["blocking_phase_ids"]
        ),
        "review_required": False,
        "completed": False,
    }

    if not eligibility["eligible"]:
        return result

    if not auto:
        result["review_required"] = True
        return result

    completed = complete_initiative(
        initiative
    )

    result["completed"] = True
    result["completed_at"] = (
        completed.completed_at.isoformat()
    )

    return result


def approve_initiative_completion(
    initiative: Initiative,
) -> dict[str, object]:
    """Approve an Initiative-completion opportunity."""

    completed = complete_initiative(
        initiative
    )

    return {
        "decision": "APPROVED",
        "initiative_id": completed.pk,
        "initiative": completed.title,
        "completed": True,
        "completed_at": completed.completed_at.isoformat(),
    }


def reject_initiative_completion(
    initiative: Initiative,
    *,
    reason: str = "",
) -> dict[str, object]:
    """Reject an Initiative-completion opportunity without mutation."""

    if initiative is None or not initiative.pk:
        raise PlanningLifecycleError(
            "A persisted Initiative is required."
        )

    current = Initiative.objects.get(
        pk=initiative.pk
    )

    return {
        "decision": "REJECTED",
        "initiative_id": current.pk,
        "initiative": current.title,
        "completed": False,
        "reason": reason.strip(),
    }

# ======================================================================
# END: PLANNING_INITIATIVE_COMPLETION
# ======================================================================