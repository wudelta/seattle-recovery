# ======================================================================
# FILE: aurora/api/endpoints.py (PATCH 1 OF 2)
# START: STANDARD_DJANGO_WEB_VIEW_ENDPOINT_IMPORTS
# ======================================================================
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from aurora.generation.page_skeleton import PageSkeletonBuilder
from aurora.models import ComponentRegistry
# ======================================================================
# END: STANDARD_DJANGO_WEB_VIEW_ENDPOINT_IMPORTS (PATCH 1 OF 2)
# ======================================================================


# ======================================================================
# FILE: aurora/api/endpoints.py (PATCH 2 OF 2)
# START: UNLOCKED_COMPONENTS_AND_BIND_COMMAND_ROUTING_VIEW
# ======================================================================
@csrf_exempt
@login_required
def unlocked_components_endpoint(request):
    """Manage unlocked ComponentRegistry records."""
    if request.method == "GET":
        unlocked_assets = (
            ComponentRegistry.objects
            .filter(locked=False)
            .order_by("-date_created")
        )

        payload = [
            {
                "id": str(asset.id),
                "name": asset.name,
                "path": asset.file_path,
            }
            for asset in unlocked_assets
        ]

        return JsonResponse({
            "status": "success",
            "components": payload,
        })

    if request.method == "POST":
        target_id = request.POST.get("component_id")

        if target_id:
            ComponentRegistry.objects.filter(
                id=target_id,
            ).update(
                locked=True,
            )

            PageSkeletonBuilder.emit_log(
                "[SUCCESS] Security state mutated. "
                f"Locked registry record token UUID: {target_id}\n"
            )

            return JsonResponse({
                "status": "success",
                "telemetry_stream": (
                    PageSkeletonBuilder.flush_telemetry()
                ),
            })

        return JsonResponse(
            {
                "status": "error",
                "message": "Missing component_id parameter.",
            },
            status=400,
        )

    return JsonResponse(
        {
            "status": "error",
            "message": "Method not allowed",
        },
        status=405,
    )


@csrf_exempt
@login_required
def bind_command_endpoint(request):
    """Route raw /bind commands to the standalone bind handler."""
    if request.method != "POST":
        return JsonResponse(
            {
                "status": "error",
                "message": "Method not allowed",
            },
            status=405,
        )

    raw_cmd = request.POST.get(
        "blueprint",
        "",
    ).strip()

    if not raw_cmd.startswith("/bind"):
        return JsonResponse({
            "status": "success",
            "minion_log": (
                "Invalid console engine routing path. "
                "Expected /bind prefix."
            ),
            "validation": {
                "valid": False,
                "errors": [
                    "Invalid command format",
                ],
                "warnings": [],
            },
        })

    parts = [
        part.strip()
        for part in raw_cmd.split(" ")
        if part.strip()
    ]

    from aurora.api.handlers.bind import BindCommandHandler

    handler = BindCommandHandler()

    return handler.execute(
        request,
        parts,
        raw_cmd,
    )
# ======================================================================
# END: UNLOCKED_COMPONENTS_AND_BIND_COMMAND_ROUTING_VIEW (PATCH 2 OF 2)
# ======================================================================