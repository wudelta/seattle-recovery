# ======================================================================
# FILE: aurora/subsystems/engineering_session/api/session_actions.py
# START: ENGINEERING_SESSION_LIFECYCLE_ACTIONS
# ======================================================================

from django.http import JsonResponse

from aurora.subsystems.engineering_session.api.common import (
    require_active_session,
)
from aurora.subsystems.engineering_session.api.serializers import (
    serialize_session,
    serialize_time_entry,
)
from aurora.subsystems.engineering_session.services import (
    end_session,
    get_session_workflow_status,
    start_session,
)
from aurora.subsystems.planning.services import (
    end_step_work,
    get_executable_step,
    start_step_work,
    validate_and_complete_step,
)


SESSION_ACTIONS = {
    "start",
    "end",
    "start_step_work",
    "end_step_work",
    "complete_step",
}


def handle_session_action(request, action):
    """Handle Engineering Session and active-Step workflow actions."""

    if action == "start":
        return _start_session_action(
            request
        )

    if action == "end":
        return _end_session_action(
            request
        )

    if action == "start_step_work":
        return _start_step_work_action(
            request
        )

    if action == "end_step_work":
        return _end_step_work_action(
            request
        )

    return _complete_step_action(
        request
    )


def _start_session_action(request):
    """Start one Engineering Session."""

    session = start_session(
        request.user
    )

    return JsonResponse(
        {
            "status": "success",
            "active": True,
            "session": serialize_session(
                session
            ),
        }
    )


def _end_session_action(request):
    """End the authenticated user's Engineering Session."""

    session = end_session(
        request.user
    )

    return JsonResponse(
        {
            "status": "success",
            "active": False,
            "session": serialize_session(
                session
            ),
        }
    )


def _start_step_work_action(request):
    """
    Start timing work against the lifecycle-authoritative ACTIVE Step.

    Starting a timer does not choose or activate Planning work.
    """

    require_active_session(
        request.user
    )

    time_entry = start_step_work(
        request.user
    )

    return JsonResponse(
        {
            "status": "success",
            "action": "start_step_work",
            "time_entry": serialize_time_entry(
                time_entry
            ),
            "workflow": get_session_workflow_status(
                request.user
            ),
        }
    )


def _end_step_work_action(request):
    """Stop timing the authenticated user's current Step work."""

    require_active_session(
        request.user
    )

    time_entry = end_step_work(
        request.user
    )

    return JsonResponse(
        {
            "status": "success",
            "action": "end_step_work",
            "time_entry": serialize_time_entry(
                time_entry
            ),
            "workflow": get_session_workflow_status(
                request.user
            ),
        }
    )


def _complete_step_action(request):
    """
    Validate and complete the lifecycle-authoritative ACTIVE Step.

    Validation evidence and lifecycle completion remain Planning-owned.
    """

    require_active_session(
        request.user
    )

    validation_notes = str(
        request.POST.get(
            "validation_notes",
            ""
        )
    ).strip()

    if not validation_notes:
        raise ValueError(
            "validation_notes is required to complete Planning work."
        )

    step = get_executable_step(
        request.user
    )

    lifecycle = validate_and_complete_step(
        step=step,
        user=request.user,
        validation_notes=validation_notes,
        auto_phase=False,
        auto_initiative=False,
    )

    return JsonResponse(
        {
            "status": "success",
            "action": "complete_step",
            "lifecycle": lifecycle,
            "workflow": get_session_workflow_status(
                request.user
            ),
        }
    )


# ======================================================================
# END: ENGINEERING_SESSION_LIFECYCLE_ACTIONS
# ======================================================================