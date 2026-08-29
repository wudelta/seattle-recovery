# ======================================================================
# FILE: aurora/subsystems/planning/api/worker_resources.py
# START: PLANNING_WORKER_RESOURCES
# ======================================================================

from aurora.models import Initiative
from aurora.subsystems.planning.api.payload import build_planning_payload


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


# ======================================================================
# END: PLANNING_WORKER_RESOURCES
# ======================================================================
