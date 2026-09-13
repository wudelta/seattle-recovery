# ======================================================================
# FILE: aurora/subsystems/decision_engine/api/endpoint.py
# START: DECISION_ENGINE_INBOX_ENDPOINT
# ======================================================================

from django.http import JsonResponse

from aurora.access import can_access_aurora
from aurora.subsystems.decision_engine.services import (
    get_raw_decision_engine_inbox,
)


def decision_engine_inbox_endpoint(request):
    """Expose the read-only raw organizational inbox."""

    if not can_access_aurora(request.user):
        return JsonResponse(
            {"status": "ERROR", "message": "Aurora developer access is required."},
            status=403,
        )

    if request.method != "GET":
        return JsonResponse(
            {"status": "ERROR", "message": "Decision Engine raw inbox is read-only."},
            status=405,
        )

    return JsonResponse({
        "status": "SUCCESS",
        **get_raw_decision_engine_inbox(request.user),
    })


# ======================================================================
# END: DECISION_ENGINE_INBOX_ENDPOINT
# ======================================================================
