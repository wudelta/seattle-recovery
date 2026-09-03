# ======================================================================
# FILE: aurora/subsystems/planning/api/worker_resources.py
# START: PLANNING_WORKER_RESOURCES
# ======================================================================

from aurora.models import ExecutionStatus, Initiative
from aurora.subsystems.planning.api.payload import build_planning_payload
from aurora.subsystems.planning.services.time_tracking import (
    PlanningTimeTrackingError,
    get_executable_step,
)


class PlanningWorkerResourceError(ValueError):
    """Raised when a bounded Planning worker resource cannot be resolved."""


def get_initiative_worker_resource(
    initiative_id: int,
    *,
    user,
) -> dict[str, object]:
    """
    Return one Initiative hierarchy through Planning's existing read authority.

    This is a read-only worker-facing application resource. It deliberately
    reuses the Planning payload/serializer boundary rather than exposing ORM
    objects or lifecycle services to AI-worker orchestration.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        raise PlanningWorkerResourceError(
            "An authenticated user is required to read Planning resources."
        )

    try:
        initiative = (
            Initiative.objects
            .select_related("project")
            .get(pk=initiative_id)
        )
    except (Initiative.DoesNotExist, TypeError, ValueError) as exc:
        raise PlanningWorkerResourceError(
            "The requested Planning Initiative does not exist."
        ) from exc

    payload = build_planning_payload(
        project_slug=initiative.project.slug,
        initiative_id=initiative.pk,
    )

    active_initiative = payload.get("active_initiative")

    if (
        not isinstance(active_initiative, dict)
        or active_initiative.get("id") != initiative.pk
    ):
        raise PlanningWorkerResourceError(
            "Planning could not resolve the requested Initiative hierarchy."
        )

    return {
        "resource": f"planning/initiatives/{initiative.pk}",
        "initiative": active_initiative,
    }


def get_current_execution_worker_resource(
    *,
    user,
) -> dict[str, object]:
    """
    Return the user's current executable Planning path as plain worker data.

    Planning owns lifecycle resolution. Consumers receive only serialized
    Initiative, Phase, and Step state and never Planning ORM objects.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        raise PlanningWorkerResourceError(
            "An authenticated user is required to read Planning resources."
        )

    has_active_initiative = Initiative.objects.filter(
        assigned_to=user,
        status=ExecutionStatus.ACTIVE,
    ).exists()

    if not has_active_initiative:
        return {
            "resource": "planning/execution/current",
            "initiative": None,
            "phase": None,
            "step": None,
        }

    try:
        step = get_executable_step(user)
    except PlanningTimeTrackingError as exc:
        raise PlanningWorkerResourceError(str(exc)) from exc

    phase = step.phase
    initiative = phase.initiative

    return {
        "resource": "planning/execution/current",
        "initiative": {
            "id": initiative.pk,
            "title": initiative.title,
            "description": initiative.description,
            "status": initiative.status,
        },
        "phase": {
            "id": phase.pk,
            "title": phase.title,
            "description": phase.description,
            "status": phase.status,
        },
        "step": {
            "id": step.pk,
            "title": step.title,
            "description": step.description,
            "status": step.status,
            "validation_description": step.validation_description,
            "estimated_minutes": step.estimated_minutes,
            "estimate_confidence": step.estimate_confidence,
            "estimate_confidence_label": (
                step.get_estimate_confidence_display()
                if step.estimate_confidence
                else None
            ),
        },
    }


# ======================================================================
# END: PLANNING_WORKER_RESOURCES
# ======================================================================
