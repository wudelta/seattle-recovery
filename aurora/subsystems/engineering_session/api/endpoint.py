# ======================================================================
# FILE: aurora/subsystems/engineering_session/api/endpoint.py
# START: ENGINEERING_SESSION_API_ENDPOINT
# ======================================================================

from django.http import JsonResponse

from aurora.subsystems.engineering_session.services import (
    EngineeringSessionError,
    end_session,
    get_active_session,
    get_session_workflow_status,
    start_session,
)


def _serialize_session(session):
    """Return stable API data for one EngineeringSession."""

    if session is None:
        return None

    return {
        "id": session.id,
        "started_at": session.started_at.isoformat(),
        "ended_at": (
            session.ended_at.isoformat()
            if session.ended_at
            else None
        ),
    }


def engineering_session_endpoint(request):
    """Read or change the authenticated user's Engineering Session."""

    if request.method == "GET":
        session = get_active_session(request.user)
        workflow = get_session_workflow_status(request.user)

        return JsonResponse(
            {
                "status": "success",
                "active": session is not None,
                "session": _serialize_session(session),
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

    action = request.POST.get("action")

    try:
        if action == "start":
            session = start_session(request.user)

            return JsonResponse(
                {
                    "status": "success",
                    "active": True,
                    "session": _serialize_session(session),
                }
            )

        if action == "end":
            session = end_session(request.user)

            return JsonResponse(
                {
                    "status": "success",
                    "active": False,
                    "session": _serialize_session(session),
                }
            )

    except EngineeringSessionError as error:
        return JsonResponse(
            {
                "status": "error",
                "message": str(error),
            },
            status=400,
        )

    return JsonResponse(
        {
            "status": "error",
            "message": f"Unknown action: {action}",
        },
        status=400,
    )

# ======================================================================
# FILE: aurora/subsystems/engineering_session/api/endpoint.py
# END: ENGINEERING_SESSION_API_ENDPOINT
# ======================================================================