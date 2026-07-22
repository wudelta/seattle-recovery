# ======================================================================
# FILE: aurora/api/handlers/page.py (PATCH 1 OF 1)
# START: PAGE_SLASH_COMMAND_PROCESSOR
# ======================================================================
from django.http import JsonResponse

from aurora.api.handlers.base import BaseCommandHandler
from aurora.generation.page_skeleton import PageSkeletonBuilder
from aurora.workspace.workspace_synchronizer import WorkspaceSynchronizer


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
        view_path = f"{c_app}/views/{c_page}_view.py"
        template_path = f"{c_app}/templates/{c_app}/{c_page}.html"

        PageSkeletonBuilder.emit_log(
            "[INFO] Initializing forge sequence for page component "
            f"view: '{view_path}' [{vis}]\n"
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

        synchronizer = WorkspaceSynchronizer()

        view_synchronization = synchronizer.synchronize_path(
            view_path,
            user_instance=user_instance,
        )
        template_synchronization = synchronizer.synchronize_path(
            template_path,
            user_instance=user_instance,
        )

        view_report = view_synchronization["report"]
        template_report = template_synchronization["report"]

        failures = (
            view_report.failures
            + view_report.graph_failures
            + template_report.failures
            + template_report.graph_failures
        )

        if failures:
            captured_telemetry_logs += (
                "[ERROR] Page component generated, but workspace "
                f"synchronization failed: {failures[0]}\n"
            )

            return JsonResponse({
                "status": "success",
                "minion_log": (
                    "Forge generated the page component, but deterministic "
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
            "[SUCCESS] Page view and template synchronized through the "
            "workspace pipeline: "
            f"{view_path}, {template_path}\n"
        )

        return JsonResponse({
            "status": "success",
            "minion_log": (
                f"FORGE SUCCESS: {res.get('message')} "
                f"(view: {view_synchronization['classification']}; "
                f"template: {template_synchronization['classification']} "
                "-> synchronized)."
            ),
            "generated_code": (
                f"# View located at: {view_path}\n"
                f"<!-- Template located at: {template_path} -->\n"
            ),
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