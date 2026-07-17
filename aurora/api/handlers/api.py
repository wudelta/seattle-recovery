# ======================================================================
# FILE: aurora/api/handlers/api.py (PATCH 1 OF 1)
# START: API_SLASH_COMMAND_PROCESSOR
# ======================================================================
from django.http import JsonResponse

from aurora.api.handlers.base import BaseCommandHandler
from aurora.utils.api_skeleton import ApiSkeletonBuilder
from aurora.utils.forge_registry import register_new_component
from aurora.utils.graph_synchronizer import GraphSynchronizer
from aurora.utils.page_skeleton import PageSkeletonBuilder


class ApiCommandHandler(BaseCommandHandler):
    """Processes the /api command layout to forge functional API endpoints."""

    def execute(self, request, parts: list, raw_cmd: str) -> JsonResponse:
        if len(parts) < 3:
            return JsonResponse({
                "status": "success",
                "minion_log": (
                    "Syntax: /api <app_name> <endpoint_name> [visibility]"
                ),
                "validation": {
                    "valid": False,
                    "errors": ["Missing parameters"],
                    "warnings": [],
                },
            })

        app = parts[1].lower().strip()
        endpoint = parts[2].lower().strip()
        vis = parts[3].lower().strip() if len(parts) > 3 else "private"

        c_app, c_endpoint, f_name = ApiSkeletonBuilder.clean_inputs(
            app,
            endpoint,
        )
        path = f"{c_app}/api/{c_endpoint}_api.py"

        PageSkeletonBuilder.emit_log(
            "[FORGE_ENGINE] Initializing forge sequence for API "
            f"streaming endpoint: '{path}'\n"
        )

        res = ApiSkeletonBuilder.forge_api(c_app, c_endpoint, vis)
        captured_telemetry_logs = PageSkeletonBuilder.flush_telemetry()

        if res.get("status") == "error":
            return JsonResponse({
                "status": "success",
                "minion_log": f"Forge halted: {res.get('message')}",
                "telemetry_stream": captured_telemetry_logs,
                "validation": {
                    "valid": False,
                    "errors": [res.get("message")],
                    "warnings": [],
                },
            })

        user_instance = (
            request.user
            if request.user and request.user.is_authenticated
            else None
        )

        if not user_instance:
            from django.contrib.auth import get_user_model

            user_model = get_user_model()
            user_instance = user_model.objects.filter(
                is_staff=True,
            ).first()

            if not user_instance:
                user_instance = user_model.objects.create_user(
                    username="test_api_operator",
                    is_staff=True,
                )

        asset = register_new_component(
            path,
            f_name,
            vis,
            user_instance,
            "ENTRY_POINT",
            (
                "Automated function-based JSON stream endpoint inside "
                f"{c_app}/api."
            ),
        )

        graph_report = GraphSynchronizer().synchronize_components([asset])

        if graph_report.failures:
            failure_message = graph_report.failures[0]
            captured_telemetry_logs += (
                "[ERROR] API route registration completed, but graph "
                f"synchronization failed: {failure_message}\n"
            )

            return JsonResponse({
                "status": "success",
                "minion_log": (
                    "Forge generated and registered the API endpoint, "
                    "but graph synchronization failed."
                ),
                "telemetry_stream": captured_telemetry_logs,
                "validation": {
                    "valid": False,
                    "errors": [failure_message],
                    "warnings": [],
                },
            })

        captured_telemetry_logs += (
            "[SUCCESS] API route generated, registered, and graph "
            f"synchronized. Registry ID: {asset.id}\n"
        )

        return JsonResponse({
            "status": "success",
            "minion_log": (
                f"FORGE SUCCESS: {res.get('message')} "
                f"(Postgres UUID: {asset.id} -> Graph synchronized)."
            ),
            "generated_code": (
                f"# API Path registered: "
                f"path('api/{c_endpoint}/', api_commands.{f_name})\n"
            ),
            "telemetry_stream": captured_telemetry_logs,
            "validation": {
                "valid": True,
                "errors": [],
                "warnings": [],
            },
        })
# ======================================================================
# END: API_SLASH_COMMAND_PROCESSOR (PATCH 1 OF 1)
# ======================================================================