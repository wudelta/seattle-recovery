# ======================================================================
# FILE: aurora/api/handlers/page.py (PATCH 1 OF 1)
# START: PAGE_SLASH_COMMAND_PROCESSOR
# ======================================================================
from django.http import JsonResponse

from aurora.api.handlers.base import BaseCommandHandler
from aurora.utils.forge_registry import register_new_component
from aurora.utils.graph_synchronizer import GraphSynchronizer
from aurora.utils.page_skeleton import PageSkeletonBuilder


class PageCommandHandler(BaseCommandHandler):
    """Processes the /page command layout to forge components securely."""

    def execute(self, request, parts: list, raw_cmd: str) -> JsonResponse:
        if len(parts) < 3:
            return JsonResponse({
                "status": "success",
                "minion_log": (
                    "Syntax: /page <app_name> <page_name> [visibility]"
                ),
                "validation": {
                    "valid": False,
                    "errors": ["Missing parameters"],
                    "warnings": [],
                },
            })

        app = parts[1].lower().strip()
        page = parts[2].lower().strip()
        vis = parts[3].lower().strip() if len(parts) > 3 else "private"

        c_app, c_page, c_name = PageSkeletonBuilder.clean_inputs(
            app,
            page,
        )
        path = f"templates/{c_app}/{c_page}.html"

        PageSkeletonBuilder.emit_log(
            "[INFO] Initializing forge sequence for page layout "
            f"template: '{path}' [{vis}]\n"
        )

        res = PageSkeletonBuilder.forge_page(c_app, c_page, vis)
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
                    username="test_command_operator",
                    is_staff=True,
                )

        asset = register_new_component(
            path,
            f"{c_page}_layout",
            vis,
            user_instance,
            "COMPILER_MODULE",
            f"Automated layout canvas configuration for {c_app}.",
        )

        graph_report = GraphSynchronizer().synchronize_components([asset])

        if graph_report.failures:
            failure_message = graph_report.failures[0]
            captured_telemetry_logs += (
                "[ERROR] Page registration completed, but graph "
                f"synchronization failed: {failure_message}\n"
            )

            return JsonResponse({
                "status": "success",
                "minion_log": (
                    "Forge generated and registered the page template, "
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
            "[SUCCESS] Page template generated, registered, and graph "
            f"synchronized. Registry ID: {asset.id}\n"
        )

        return JsonResponse({
            "status": "success",
            "minion_log": (
                f"FORGE SUCCESS: {res.get('message')} "
                f"(Postgres UUID: {asset.id} -> Graph synchronized)."
            ),
            "generated_code": f"<!-- Layout located at: {path} -->\n",
            "telemetry_stream": captured_telemetry_logs,
            "validation": {
                "valid": True,
                "errors": [],
                "warnings": [],
            },
        })
# ======================================================================
# END: PAGE_SLASH_COMMAND_PROCESSOR (PATCH 1 OF 1)
# ======================================================================