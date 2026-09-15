# ======================================================================
# FILE: aurora/subsystems/decision_engine/api/endpoint.py
# START: DECISION_ENGINE_ENDPOINTS
# ======================================================================

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from aurora.access import (
    can_access_aurora,
    can_reconcile_decision_engine,
)
from aurora.subsystems.decision_engine.services import (
    DecisionEngineReconciliationError,
    commit_selected_intake_to_work,
    get_raw_decision_engine_inbox,
)


def decision_engine_inbox_endpoint(request):
    """Expose the read-only actionable organizational inbox."""

    if not can_access_aurora(request.user):
        return JsonResponse(
            {"status": "ERROR", "message": "Aurora developer access is required."},
            status=403,
        )

    if request.method != "GET":
        return JsonResponse(
            {
                "status": "ERROR",
                "message": "Decision Engine raw inbox is read-only.",
            },
            status=405,
        )

    return JsonResponse({
        "status": "SUCCESS",
        **get_raw_decision_engine_inbox(request.user),
    })


@login_required
@require_http_methods(["POST"])
def decision_engine_commit_endpoint(request):
    """Commit one explicitly selected intake set to durable Decision Engine work."""

    if not can_reconcile_decision_engine(request.user):
        return JsonResponse(
            {
                "status": "ERROR",
                "message": (
                    "Initiative-owner Decision Engine reconciliation authority "
                    "is required."
                ),
            },
            status=403,
        )

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "status": "ERROR",
                "message": "Request body must contain valid JSON.",
            },
            status=400,
        )

    try:
        result = commit_selected_intake_to_work(
            request.user,
            title=payload.get("title"),
            description=payload.get("description"),
            reason=payload.get("reason"),
            sources=payload.get("sources"),
        )
    except DecisionEngineReconciliationError as exc:
        return JsonResponse(
            {"status": "ERROR", "message": str(exc)},
            status=400,
        )

    return JsonResponse({"status": "SUCCESS", **result}, status=201)


# ======================================================================
# END: DECISION_ENGINE_ENDPOINTS
# ======================================================================
