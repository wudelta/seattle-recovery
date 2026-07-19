# ======================================================================
# FILE: aurora/api/handlers/bind.py (PATCH 1 OF 1)
# START: DETERMINISTIC_PAGE_API_BINDING
# ======================================================================
import os

from django.http import JsonResponse

from aurora.api.handlers.base import BaseCommandHandler
from aurora.utils.telemetry import TelemetryLogger
from aurora.utils.workspace_synchronizer import WorkspaceSynchronizer


class BindCommandHandler(BaseCommandHandler):
    """Binds an existing page template to an existing API endpoint."""

    def execute(self, request, parts: list, raw_cmd: str) -> JsonResponse:
        if len(parts) < 4:
            return JsonResponse({
                "status": "success",
                "minion_log": (
                    "Syntax: /bind <app_name> <page_name> <api_name>"
                ),
                "validation": {
                    "valid": False,
                    "errors": ["Missing parameters"],
                    "warnings": [],
                },
            })

        app_name = parts[1].lower().strip()
        page_name = parts[2].lower().strip()
        api_name = parts[3].lower().strip()

        TelemetryLogger.emit(
            "[BIND_ENGINE] Starting page-to-API binding: "
            f"{app_name}.{page_name} -> {api_name}\n"
        )

        template_candidates = [
            os.path.join(
                app_name,
                "templates",
                app_name,
                f"{page_name}.html",
            ),
            os.path.join(
                app_name,
                "templates",
                f"{page_name}.html",
            ),
        ]

        target_html_path = next(
            (
                path
                for path in template_candidates
                if os.path.isfile(path)
            ),
            None,
        )

        if not target_html_path:
            message = (
                "Binding halted: expected page template does not exist. "
                f"Checked: {', '.join(template_candidates)}"
            )
            TelemetryLogger.emit(f"[ERROR] {message}\n")

            return JsonResponse({
                "status": "success",
                "minion_log": message,
                "telemetry_stream": TelemetryLogger.flush(),
                "validation": {
                    "valid": False,
                    "errors": [message],
                    "warnings": [],
                },
            })

        api_path = os.path.join(
            app_name,
            "api",
            f"{api_name}_api.py",
        )

        if not os.path.isfile(api_path):
            message = (
                "Binding halted: expected API module does not exist: "
                f"{api_path}"
            )
            TelemetryLogger.emit(f"[ERROR] {message}\n")

            return JsonResponse({
                "status": "success",
                "minion_log": message,
                "telemetry_stream": TelemetryLogger.flush(),
                "validation": {
                    "valid": False,
                    "errors": [message],
                    "warnings": [],
                },
            })

        TelemetryLogger.emit(
            f"[BIND_ENGINE] Page template confirmed: {target_html_path}\n"
        )
        TelemetryLogger.emit(
            f"[BIND_ENGINE] API module confirmed: {api_path}\n"
        )

        bound_template = (
            "<div class='container mt-4'>\n"
            "  <div class='card shadow-sm'>\n"
            "    <div class='card-header bg-primary text-white'>\n"
            f"      <h5 class='mb-0'>Live Data: {api_name}</h5>\n"
            "    </div>\n"
            "    <div class='card-body'>\n"
            "      <pre id='json_payload_render' "
            "class='bg-light p-3 border rounded'>"
            "Loading payload...</pre>\n"
            "    </div>\n"
            "  </div>\n"
            "</div>\n"
            "<script>\n"
            "  document.addEventListener('DOMContentLoaded', function() {\n"
            f"    fetch('/{app_name}/api/{api_name}/')\n"
            "      .then(response => {\n"
            "        if (!response.ok) {\n"
            "          throw new Error('API request failed');\n"
            "        }\n"
            "        return response.json();\n"
            "      })\n"
            "      .then(data => {\n"
            "        document.getElementById(\n"
            "          'json_payload_render'\n"
            "        ).textContent = JSON.stringify(data, null, 2);\n"
            "      })\n"
            "      .catch(error => {\n"
            "        document.getElementById(\n"
            "          'json_payload_render'\n"
            "        ).textContent = 'Failed to retrieve API payload.';\n"
            "      });\n"
            "  });\n"
            "</script>\n"
        )

        try:
            with open(target_html_path, "w", encoding="utf-8") as template:
                template.write(bound_template)
        except OSError as error:
            message = (
                "Binding failed while writing the page template: "
                f"{error}"
            )
            TelemetryLogger.emit(f"[ERROR] {message}\n")

            return JsonResponse({
                "status": "success",
                "minion_log": message,
                "telemetry_stream": TelemetryLogger.flush(),
                "validation": {
                    "valid": False,
                    "errors": [str(error)],
                    "warnings": [],
                },
            })

        TelemetryLogger.emit(
            f"[BIND_ENGINE] Page template updated: {target_html_path}\n"
        )

        user_instance = (
            request.user
            if request.user and request.user.is_authenticated
            else None
        )

        synchronization = WorkspaceSynchronizer().synchronize_path(
            target_html_path,
            user_instance=user_instance,
        )
        synchronization_report = synchronization["report"]

        failures = (
            synchronization_report.failures
            + synchronization_report.graph_failures
        )

        if failures:
            TelemetryLogger.emit(
                "[ERROR] Page binding was written, but workspace "
                f"synchronization failed: {failures[0]}\n"
            )

            return JsonResponse({
                "status": "success",
                "minion_log": (
                    "Page binding was written, but deterministic "
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
            "[SUCCESS] Page bound to API and synchronized through the "
            f"workspace pipeline: {target_html_path}\n"
        )

        return JsonResponse({
            "status": "success",
            "minion_log": (
                f"Binding complete: {target_html_path} now requests "
                f"'/{app_name}/api/{api_name}/'."
            ),
            "telemetry_stream": TelemetryLogger.flush(),
            "validation": {
                "valid": True,
                "errors": [],
                "warnings": [],
            },
        })
# ======================================================================
# END: DETERMINISTIC_PAGE_API_BINDING (PATCH 1 OF 1)
# ======================================================================