# ======================================================================
# FILE: aurora/api/handlers/api.py (PATCH 1 OF 1)
# START: API_SLASH_COMMAND_PROCESSOR
# ======================================================================
from django.http import JsonResponse

from aurora.api.handlers.base import BaseCommandHandler
from aurora.utils.api_skeleton import ApiSkeletonBuilder
from aurora.utils.telemetry import TelemetryLogger
from aurora.utils.workspace_synchronizer import WorkspaceSynchronizer


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

        TelemetryLogger.emit(
            "[FORGE_ENGINE] Initializing forge sequence for API "
            f"streaming endpoint: '{path}'\n"
        )

        res = ApiSkeletonBuilder.forge_api(c_app, c_endpoint, vis)
        captured_telemetry_logs = TelemetryLogger.flush()

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

        synchronization = WorkspaceSynchronizer().synchronize_path(
            path,
            user_instance=user_instance,
        )
        synchronization_report = synchronization["report"]

        failures = (
            synchronization_report.failures
            + synchronization_report.graph_failures
        )

        if failures:
            captured_telemetry_logs += (
                "[ERROR] API route generated, but workspace "
                f"synchronization failed: {failures[0]}\n"
            )

            return JsonResponse({
                "status": "success",
                "minion_log": (
                    "Forge generated the API endpoint, but deterministic "
                    "workspace synchronization failed."
                ),
                "telemetry_stream": captured_telemetry_logs,
                "validation": {
                    "valid": False,
                    "errors": failures,
                    "warnings": [],
                },
            })

        captured_telemetry_logs += (
            "[SUCCESS] API route generated and synchronized through the "
            f"workspace pipeline: {path}\n"
        )

        return JsonResponse({
            "status": "success",
            "minion_log": (
                f"FORGE SUCCESS: {res.get('message')} "
                f"({synchronization['classification']} -> synchronized)."
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