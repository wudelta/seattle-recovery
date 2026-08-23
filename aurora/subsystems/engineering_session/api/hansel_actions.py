# ======================================================================
# FILE: aurora/subsystems/engineering_session/api/hansel_actions.py
# START: ENGINEERING_SESSION_HANSEL_ACTIONS
# ======================================================================

from django.http import JsonResponse

from aurora.subsystems.engineering_session.api.common import (
    require_active_session,
)
from aurora.subsystems.hansel.services import (
    complete_hansel_trail,
    start_hansel_trail,
)


HANSEL_ACTIONS = {
    "start_hansel_trail",
    "complete_hansel_trail",
}


def handle_hansel_action(
    request,
    action,
):
    """Handle explicit Hansel discovery-trail actions."""

    if action == "start_hansel_trail":
        return _start_hansel_trail_action(
            request
        )

    return _complete_hansel_trail_action(
        request
    )


def _start_hansel_trail_action(
    request,
):
    """Begin discovery for the lifecycle-authoritative ACTIVE Step."""

    require_active_session(
        request.user
    )

    trail = start_hansel_trail(
        request.user
    )

    return JsonResponse(
        {
            "status": "success",
            "action": "start_hansel_trail",
            "trail": _serialize_trail(
                trail
            ),
        }
    )


def _complete_hansel_trail_action(
    request,
):
    """Persist one observed Hansel trail outcome."""

    require_active_session(
        request.user
    )

    trail_id = request.POST.get(
        "trail_id"
    )

    if not trail_id:
        raise ValueError(
            "trail_id is required."
        )

    outcome = request.POST.get(
        "outcome",
        "",
    )

    authority_paths = request.POST.getlist(
        "authority_paths"
    )

    notes = request.POST.get(
        "notes",
        "",
    )

    trail = complete_hansel_trail(
        trail_id=int(trail_id),
        user=request.user,
        outcome=outcome,
        authority_paths=authority_paths,
        notes=notes,
    )

    return JsonResponse(
        {
            "status": "success",
            "action": "complete_hansel_trail",
            "trail": _serialize_trail(
                trail
            ),
        }
    )


def _serialize_trail(
    trail,
) -> dict[str, object]:
    """Serialize one Hansel trail and its reached authorities."""

    return {
        "id": trail.pk,
        "step_id": trail.step_id,
        "step": trail.step.title,
        "outcome": trail.outcome,
        "entry_authority": trail.entry_authority,
        "authorities": list(
            trail.authorities.values_list(
                "authority_path",
                flat=True,
            )
        ),
        "notes": trail.notes,
        "started_at": trail.started_at.isoformat(),
        "ended_at": (
            trail.ended_at.isoformat()
            if trail.ended_at
            else None
        ),
    }


# ======================================================================
# END: ENGINEERING_SESSION_HANSEL_ACTIONS
# ======================================================================