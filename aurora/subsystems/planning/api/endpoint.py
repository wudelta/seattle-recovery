# ======================================================================
# FILE: aurora/subsystems/planning/api/endpoint.py 
# START: PLANNING_ENDPOINT_ROUTER
# ======================================================================
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from aurora.subsystems.planning.api.initiatives import save_initiative
from aurora.subsystems.planning.api.payload import build_planning_payload
from aurora.subsystems.planning.api.phases import save_phase
from aurora.subsystems.planning.api.steps import save_step


@login_required
@require_http_methods(["GET", "POST"])
def planning_endpoint(request):
    """Reads the hierarchy or performs a supported planning operation."""
    if request.method == "GET":
        project_slug = str(
            request.GET.get("project", "")
        ).strip()

        initiative_id = str(
            request.GET.get("initiative", "")
        ).strip()

        return JsonResponse(
            build_planning_payload(
                project_slug=project_slug or None,
                initiative_id=initiative_id or None,
            )
        )

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "status": "error",
                "message": "Request body must contain valid JSON.",
            },
            status=400,
        )

    operation = str(
        payload.get("operation", "create_initiative")
    ).strip().lower()

    if operation in {
        "create_initiative",
        "save_initiative",
    }:
        return save_initiative(request, payload)

    if operation in {
        "create_phase",
        "save_phase",
    }:
        return save_phase(payload)

    if operation in {
        "create_step",
        "save_step",
    }:
        return save_step(payload)

    return JsonResponse(
        {
            "status": "error",
            "message": "The requested planning operation is not supported.",
        },
        status=400,
    )
# ======================================================================
# END: PLANNING_ENDPOINT_ROUTER 
# ======================================================================