# ======================================================================
# FILE: aurora/subsystems/engineering_session/api/endpoint.py
# START: ENGINEERING_SESSION_API_ENDPOINT
# ======================================================================

from django.http import JsonResponse

from aurora.models import DeltaNotesEntry, Initiative, Phase
from aurora.subsystems.engineering_session.api.completion_actions import (
    COMPLETION_ACTIONS,
    handle_completion_action,
)
from aurora.subsystems.engineering_session.api.delta_note_actions import (
    DELTA_NOTE_ACTIONS,
    handle_delta_note_action,
)
from aurora.subsystems.engineering_session.api.registry_actions import (
    REGISTRY_ACTIONS,
    handle_registry_action,
)
from aurora.subsystems.engineering_session.api.serializers import (
    serialize_session,
)
from aurora.subsystems.engineering_session.api.session_actions import (
    SESSION_ACTIONS,
    handle_session_action,
)
from aurora.subsystems.engineering_session.services import (
    EngineeringSessionError,
    EngineeringSessionPlanningError,
    get_active_session,
    get_session_workflow_status,
)
from aurora.subsystems.planning.io.exceptions import (
    PlanningImportError,
    PlanningSchemaError,
)
from aurora.subsystems.planning.services import (
    PlanningGenerationError,
    PlanningLifecycleError,
    PlanningTimeTrackingError,
)


def _dispatch_post_action(request, action):
    """Route one Engineering Session POST action to its owning module."""

    if action in SESSION_ACTIONS:
        return handle_session_action(
            request,
            action,
        )

    if action in DELTA_NOTE_ACTIONS:
        return handle_delta_note_action(
            request,
            action,
        )

    if action in REGISTRY_ACTIONS:
        return handle_registry_action(
            request,
            action,
        )

    if action in COMPLETION_ACTIONS:
        return handle_completion_action(
            request,
            action,
        )

    return JsonResponse(
        {
            "status": "error",
            "message": f"Unknown action: {action}",
        },
        status=400,
    )


def engineering_session_endpoint(request):
    """Read or change the authenticated user's Engineering Session."""

    if request.method == "GET":
        session = get_active_session(
            request.user
        )
        workflow = get_session_workflow_status(
            request.user
        )

        return JsonResponse(
            {
                "status": "success",
                "active": session is not None,
                "session": serialize_session(
                    session
                ),
                "workflow": workflow,
            }
        )

    if request.method != "POST":
        return JsonResponse(
            {
                "status": "error",
                "message": "Method not allowed.",
            },
            status=405,
        )

    action = request.POST.get(
        "action"
    )

    try:
        return _dispatch_post_action(
            request,
            action,
        )

    except (
        EngineeringSessionError,
        EngineeringSessionPlanningError,
        PlanningGenerationError,
        PlanningImportError,
        PlanningLifecycleError,
        PlanningSchemaError,
        PlanningTimeTrackingError,
    ) as error:
        return JsonResponse(
            {
                "status": "error",
                "message": str(error),
            },
            status=400,
        )

    except (
        DeltaNotesEntry.DoesNotExist,
        Phase.DoesNotExist,
        Initiative.DoesNotExist,
        ValueError,
        TypeError,
    ):
        return JsonResponse(
            {
                "status": "error",
                "message": "Invalid workflow target.",
            },
            status=400,
        )


# ======================================================================
# END: ENGINEERING_SESSION_API_ENDPOINT
# ======================================================================
