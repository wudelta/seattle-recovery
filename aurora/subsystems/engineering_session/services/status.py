# ======================================================================
# FILE: aurora/subsystems/engineering_session/services/status.py
# START: ENGINEERING_SESSION_STATUS_SERVICE
# ======================================================================

from aurora.models import (
    ComponentRegistry,
    DeltaNotesEntry,
    UserPosition,
)


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

    step = position.step if position else None

    return {
        "planning": {
            "project": (
                position.project.title
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
                step.title
                if step
                else None
            ),
            "step_id": (
                step.id
                if step
                else None
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
# FILE: aurora/subsystems/engineering_session/services/status.py
# END: ENGINEERING_SESSION_STATUS_SERVICE
# ======================================================================