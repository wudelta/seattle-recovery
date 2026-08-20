# ======================================================================
# FILE: aurora/subsystems/engineering_session/services/status.py
# START: ENGINEERING_SESSION_STATUS_SERVICE
# ======================================================================

from aurora.models import (
    ComponentRegistry,
    DeltaNotesEntry,
    UserPosition,
)
from aurora.subsystems.planning.services import (
    PlanningTimeTrackingError,
    get_active_time_entry,
    get_executable_step,
)


def _serialize_navigation(position) -> dict[str, object]:
    """Return Planning UI navigation state."""

    return {
        "project": (
            position.project.title
            if position and position.project
            else None
        ),
        "project_slug": (
            position.project.slug
            if position and position.project
            else None
        ),
        "initiative": (
            position.initiative.title
            if position and position.initiative
            else None
        ),
        "phase": (
            position.phase.title
            if position and position.phase
            else None
        ),
        "step": (
            position.step.title
            if position and position.step
            else None
        ),
        "step_id": (
            position.step_id
            if position
            else None
        ),
    }


def _serialize_active_time_entry(
    active_time_entry,
) -> dict[str, object] | None:
    """Return the user's current open Planning TimeEntry."""

    if active_time_entry is None:
        return None

    return {
        "id": active_time_entry.id,
        "step_id": active_time_entry.step_id,
        "step": active_time_entry.step.title,
        "started_at": (
            active_time_entry.started_at.isoformat()
        ),
    }


def _serialize_executable_work(
    user,
    active_time_entry,
) -> dict[str, object]:
    """Return lifecycle-authoritative executable Planning state."""

    try:
        step = get_executable_step(user)
    except PlanningTimeTrackingError as error:
        return {
            "project": None,
            "project_slug": None,
            "initiative": None,
            "phase": None,
            "step": None,
            "step_id": None,
            "available": False,
            "reason": str(error),
            "active_time_entry": (
                _serialize_active_time_entry(
                    active_time_entry
                )
            ),
        }

    phase = step.phase
    initiative = phase.initiative
    project = initiative.project

    return {
        "project": project.title,
        "project_slug": project.slug,
        "initiative": initiative.title,
        "phase": phase.title,
        "step": step.title,
        "step_id": step.pk,
        "available": True,
        "reason": None,
        "active_time_entry": (
            _serialize_active_time_entry(
                active_time_entry
            )
        ),
    }


def get_session_workflow_status(user) -> dict[str, object]:
    """Return current cross-subsystem status for the engineering workflow."""

    position = (
        UserPosition.objects
        .select_related(
            "project",
            "initiative",
            "phase",
            "step",
        )
        .filter(user=user)
        .first()
    )

    active_time_entry = get_active_time_entry(user)

    return {
        "planning": {
            "executable": _serialize_executable_work(
                user,
                active_time_entry,
            ),
            "navigation": _serialize_navigation(
                position
            ),
        },
        "delta_notes": {
            "unprocessed_count": (
                DeltaNotesEntry.objects
                .filter(
                    user=user,
                    processed=False,
                )
                .count()
            ),
        },
        "component_registry": {
            "pending_enrichment_count": (
                ComponentRegistry.objects
                .filter(
                    status="ACTIVE",
                    analysis_status="PENDING",
                )
                .count()
            ),
        },
    }

# ======================================================================
# END: ENGINEERING_SESSION_STATUS_SERVICE
# ======================================================================