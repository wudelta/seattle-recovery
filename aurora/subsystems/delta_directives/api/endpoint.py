# ======================================================================
# FILE: aurora/subsystems/delta_directives/api/endpoint.py
# START: API_ENDPOINT_LOGIC
# ======================================================================
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from aurora.models import DeltaDirectives


@login_required
def directives_endpoint(request):
    """Provide read-only inspection access to Delta Directives."""

    if request.method != "GET":
        return JsonResponse(
            {
                "status": "ERROR",
                "message": (
                    "Delta Directives are read-only through this API. "
                    "Directive mutation must use the controlled deployment workflow."
                ),
            },
            status=405,
        )

    status_scope = request.GET.get("status", "all")
    id_query = request.GET.get("id")

    if id_query:
        try:
            asset = DeltaDirectives.objects.get(id=id_query)
        except DeltaDirectives.DoesNotExist:
            return JsonResponse(
                {
                    "status": "ERROR",
                    "message": "Requested prompt configuration missing.",
                },
                status=404,
            )

        return JsonResponse(
            {
                "status": "SUCCESS",
                "asset": {
                    "id": str(asset.id),
                    "directive_name": asset.directive_name,
                    "instructions": asset.instructions,
                    "constraints": asset.constraints,
                    "is_active": asset.is_active,
                    "author": asset.created_by.username,
                    "date_modified": asset.date_modified.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                },
            }
        )

    queryset = DeltaDirectives.objects.all().order_by("directive_name")

    if status_scope == "active":
        queryset = queryset.filter(is_active=True)
    elif status_scope == "inactive":
        queryset = queryset.filter(is_active=False)

    payload = [
        {
            "id": str(item.id),
            "directive_name": item.directive_name,
            "is_active": item.is_active,
            "date_modified": item.date_modified.strftime("%m/%d %H:%M"),
        }
        for item in queryset
    ]

    return JsonResponse(
        {
            "status": "SUCCESS",
            "inventory": payload,
        }
    )


# ======================================================================
# END: API_ENDPOINT_LOGIC
# ======================================================================