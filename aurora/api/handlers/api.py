# ======================================================================
# FILE: aurora/api/handlers/api.py (PATCH 1 OF 1)
# START: API_SLASH_COMMAND_PROCESSOR
# ======================================================================
from django.http import JsonResponse

from aurora.api.handlers.base import BaseCommandHandler
from aurora.generation.api_skeleton import ApiSkeletonBuilder
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

        user_instance = (
            request.user
            if request.user and request.user.is_authenticated
            else None
        )

        if not user_instance:
            TelemetryLogger.emit(
                "[FORGE_ENGINE] [FAIL] API generation requires an "
                "authenticated developer identity.\n"
            )

            return JsonResponse({
                "status": "success",
                "minion_log": (
                    "Forge halted: authenticated developer identity "
                    "required."
                ),
                "telemetry_stream": TelemetryLogger.flush(),
                "validation": {
                    "valid": False,
                    "errors": [
                        "Authenticated developer identity required.",
                    ],
                    "warnings": [],
                },
            })

        app = parts[1].lower().strip()
        endpoint = parts[2].lower().strip()
        visibility = (
            parts[3].lower().strip()
            if len(parts) > 3
            else "private"
        )

        clean_app, clean_endpoint, function_name = (
            ApiSkeletonBuilder.clean_inputs(
                app,
                endpoint,
            )
        )
        path = f"{clean_app}/api/{clean_endpoint}_api.py"

        TelemetryLogger.emit(
            "[FORGE_ENGINE] Initializing forge sequence for API "
            f"endpoint: '{path}'\n"
        )

        result = ApiSkeletonBuilder.forge_api(
            clean_app,
            clean_endpoint,
            visibility,
        )

        if result.get("status") == "error":
            return JsonResponse({
                "status": "success",
                "minion_log": (
                    f"Forge halted: {result.get('message')}"
                ),
                "telemetry_stream": TelemetryLogger.flush(),
                "validation": {
                    "valid": False,
                    "errors": [result.get("message")],
                    "warnings": [],
                },
            })

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
            TelemetryLogger.emit(
                "[ERROR] API route generated, but workspace "
                f"synchronization failed: {failures[0]}\n"
            )

            return JsonResponse({
                "status": "success",
                "minion_log": (
                    "Forge generated the API endpoint, but deterministic "
                    "workspace synchronization failed."
                ),
                "telemetry_stream": TelemetryLogger.flush(),
                "validation": {
                    "valid": False,
                    "errors": failures,
                    "warnings": [],
                },
            })

        TelemetryLogger.emit(
            "[SUCCESS] API route generated and synchronized through the "
            f"workspace pipeline: {path}\n"
        )

        return JsonResponse({
            "status": "success",
            "minion_log": (
                f"FORGE SUCCESS: {result.get('message')} "
                f"({synchronization['classification']} -> synchronized)."
            ),
            "generated_code": (
                "# API Path registered: "
                f"path('api/{clean_endpoint}/', "
                f"api_commands.{function_name})\n"
            ),
            "telemetry_stream": TelemetryLogger.flush(),
            "validation": {
                "valid": True,
                "errors": [],
                "warnings": [],
            },
        })
# ======================================================================
# END: API_SLASH_COMMAND_PROCESSOR (PATCH 1 OF 1)
# ======================================================================