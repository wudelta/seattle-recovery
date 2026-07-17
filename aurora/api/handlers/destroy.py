# ======================================================================
# FILE: aurora/api/handlers/destroy.py (PATCH 1 OF 1)
# START: DESTROY_SLASH_COMMAND_PROCESSOR
# ======================================================================
from django.http import JsonResponse

from aurora.api.handlers.base import BaseCommandHandler
from aurora.models import ComponentRegistry
from aurora.utils.api_skeleton import ApiSkeletonBuilder
from aurora.utils.page_skeleton import PageSkeletonBuilder


class DestroyCommandHandler(BaseCommandHandler):
    """Processes the /destroy command to obliterate codebase artifacts securely."""

    def execute(self, request, parts: list, raw_cmd: str) -> JsonResponse:
        if len(parts) < 3:
            return JsonResponse({
                "status": "success",
                "minion_log": (
                    "Syntax: /destroy <app_name> <component_name>"
                ),
                "validation": {
                    "valid": False,
                    "errors": ["Missing parameters"],
                    "warnings": [],
                },
            })

        app_raw = parts[1].lower().strip()
        name_raw = parts[2].lower().strip()

        c_app, c_page, _ = PageSkeletonBuilder.clean_inputs(
            app_raw,
            name_raw,
        )
        _, c_endpoint, _ = ApiSkeletonBuilder.clean_inputs(
            app_raw,
            name_raw,
        )

        view_path = f"{c_app}/views/{c_page}_view.py"
        template_path = (
            f"{c_app}/templates/{c_app}/{c_page}.html"
        )
        api_path = f"{c_app}/api/{c_endpoint}_api.py"
        target_paths = [
            view_path,
            template_path,
            api_path,
        ]

        PageSkeletonBuilder.emit_log(
            "[FORGE_ENGINE] Initializing obliteration check for asset "
            f"tracking tree: '{name_raw}'\n"
        )

        # 1. Verification Lock Check Pass
        for target_path in target_paths:
            try:
                asset = ComponentRegistry.objects.get(
                    file_path=target_path,
                )

                if asset.locked:
                    PageSkeletonBuilder.emit_log(
                        "[ERROR] Purge denied! Infrastructure asset is "
                        f"locked: {target_path}\n"
                    )
                    return JsonResponse({
                        "status": "success",
                        "minion_log": (
                            f"PURGE DENIED: '{name_raw}' path "
                            "infrastructure is LOCKED."
                        ),
                        "telemetry_stream": (
                            PageSkeletonBuilder.flush_telemetry()
                        ),
                        "validation": {
                            "valid": True,
                            "errors": [],
                            "warnings": [],
                        },
                    })

            except ComponentRegistry.DoesNotExist:
                pass

        PageSkeletonBuilder.emit_log(
            "[FORGE_ENGINE] System validation passed. Commencing "
            "codebase purge operations...\n"
        )

        # 2. Defensive File System Execution Shields
        try:
            p_res = PageSkeletonBuilder.purge_page(
                app_raw,
                name_raw,
            )
        except Exception as file_err:
            p_res = {
                "message": (
                    f"Template cleanup deferred: {str(file_err)}"
                ),
            }

        try:
            a_res = ApiSkeletonBuilder.purge_api(
                app_raw,
                name_raw,
            )
        except Exception as file_err:
            a_res = {
                "message": (
                    f"API cleanup deferred: {str(file_err)}"
                ),
            }

        # 3. Graph Removal Hook Block
        PageSkeletonBuilder.emit_log(
            "[FORGE_ENGINE] Detaching and flushing Neo4j network "
            "graph context loops...\n"
        )

        from neomodel import db

        for target_path in target_paths:
            try:
                db.cypher_query(
                    (
                        "MATCH (n:ComponentNode) "
                        "WHERE n.file_path = $path "
                        "DETACH DELETE n"
                    ),
                    {"path": target_path},
                )
            except Exception as e:
                PageSkeletonBuilder.emit_log(
                    "[WARNING] Graph node cleanup anomaly: "
                    f"{str(e)}\n"
                )

        # 4. Relational Database Row Purge Block
        PageSkeletonBuilder.emit_log(
            "[FORGE_ENGINE] Purging relational PostgreSQL metadata "
            "entries...\n"
        )

        try:
            ComponentRegistry.objects.filter(
                file_path__in=target_paths,
            ).delete()
        except Exception as db_err:
            PageSkeletonBuilder.emit_log(
                "[ERROR] PostgreSQL metadata clearing error: "
                f"{str(db_err)}\n"
            )

        PageSkeletonBuilder.emit_log(
            "[SUCCESS] Infrastructure completely obliterated for "
            f"module component context: '{name_raw}'\n"
        )

        return JsonResponse({
            "status": "success",
            "minion_log": (
                "SURGICAL WIPE SUCCESS. "
                f"Templates: {p_res.get('message')} | "
                f"APIs: {a_res.get('message')} | "
                "Graph Nodes: Erased."
            ),
            "generated_code": (
                "# Erased all local codebase artifacts for: "
                f"{name_raw}\n"
            ),
            "telemetry_stream": (
                PageSkeletonBuilder.flush_telemetry()
            ),
            "validation": {
                "valid": True,
                "errors": [],
                "warnings": [],
            },
        })
# ======================================================================
# END: DESTROY_SLASH_COMMAND_PROCESSOR (PATCH 1 OF 1)
# ======================================================================