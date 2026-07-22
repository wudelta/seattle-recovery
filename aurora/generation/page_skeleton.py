# ======================================================================
# FILE: aurora/utils/page_skeleton.py (PATCH 1 OF 5)
# START: PACKAGED_IMPORTS_AND_INPUT_SANITIZATION
# ======================================================================
import os
import sys
import re
from aurora.utils.telemetry import TelemetryLogger

class PageSkeletonBuilder:
    """Automated multi-app builder and destroyer with public/private scoping mechanics."""

    @classmethod
    def emit_log(cls, text: str):
        """Writes to terminal STDOUT and stores the text in the shared thread-safe telemetry buffer."""
        sys.stdout.write(text)
        sys.stdout.flush()
        TelemetryLogger.emit(text)

    @classmethod
    def flush_telemetry(cls) -> str:
        """Returns the accumulated logs as a single string and clears the buffer."""
        return TelemetryLogger.flush()

    @classmethod
    def clean_inputs(cls, app_name: str, page_name: str):
        """Sanitizes configuration arguments and computes class-based naming conventions."""
        app = re.sub(r'[^a-zA-Z0-9_]', '', app_name.lower().strip())
        page = re.sub(r'[^a-zA-Z0-9_]', '', page_name.lower().strip())
        cls_name = "".join([part.capitalize() for part in page.split("_")]) + "View"
        return app, page, cls_name
# ======================================================================
# END: PACKAGED_IMPORTS_AND_INPUT_SANITIZATION (PATCH 1 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/utils/page_skeleton.py (PATCH 2 OF 5)
# START: PATH_RESOLUTION_AND_HTML_TEMPLATE_FORGE
# ======================================================================
    @classmethod
    def forge_page(cls, target_app: str, page_name: str, visibility: str) -> dict:
        app, page, class_name = cls.clean_inputs(target_app, page_name)
        if not app or not page:
            cls.emit_log("[FORGE_ENGINE] [ERROR] Invalid parameters provided to forge page.\n")
            return {"status": "error", "message": "Invalid architectural parameters."}
        is_private = visibility.lower().strip() != "public"
        base_dir = os.getcwd()
        if not os.path.exists(os.path.join(base_dir, app)):
            cls.emit_log(f"[FORGE_ENGINE] [ERROR] Target app directory '{app}' does not exist on host.\n")
            return {"status": "error", "message": f"Target app directory '{app}' does not exist on this machine."}
        view_file = os.path.join(base_dir, app, 'views', f'{page}_view.py')
        view_init = os.path.join(base_dir, app, 'views', '__init__.py')
        template_file = os.path.join(base_dir, app, 'templates', app, f'{page}.html')
        urls_file = os.path.join(base_dir, app, 'urls.py')
        if os.path.exists(view_file) or os.path.exists(template_file):
            cls.emit_log(f"[FORGE_ENGINE] [ERROR] Collision detected: Component '{page}' already exists in app '{app}'.\n")
            return {"status": "error", "message": f"Collision: Component '{page}' already exists in app '{app}'."}
        base_template_extends = f"{app}/{app}_base.html"
        try:
            # 1. HTML Template Generation with Embedded Comment Anchors
            cls.emit_log(f"[FORGE_ENGINE] Writing layout template file artifact: {template_file}\n")
            os.makedirs(os.path.dirname(template_file), exist_ok=True)
            with open(template_file, 'w') as f:
                f.write(
                    f'{{% extends "{base_template_extends}" %}}\n'
                    f'{{% load static %}}\n\n'
                    f'{{% block title %}}{page.replace("_", " ").title()} | Under Construction ({visibility.upper()}){{% endblock %}}\n\n'
                    f'{{% block content %}}\n'
                    f'<!-- ====================================================================== -->\n'
                    f'<!-- START: FORGED_UI_CONSOLE_CONTAINER -->\n'
                    f'<!-- ====================================================================== -->\n'
                    f'<div class="d-flex flex-column align-items-center justify-content-center text-center p-5 rounded bg-black" style="min-height: 60vh;">\n'
                    f'  <div class="spinner-border text-warning mb-4" role="status" style="width: 3rem; height: 3rem;"></div>\n'
                    f'  <h2 class="display-5 text-warning font-monospace">🚧 Under Construction ({visibility.upper()}) 🚧</h2>\n'
                    f'  <p class="lead text-muted font-monospace mt-2">The class-based structure for <strong>{class_name}</strong> has been forged in <strong>{app}</strong>.</p>\n'
                    f'  <a href="{{{{ return_path }}}}" class="btn btn-outline-warning btn-sm font-monospace mt-3">Return to Dashboard</a>\n'
                    f'</div>\n'
                    f'<!-- ====================================================================== -->\n'
                    f'<!-- END: FORGED_UI_CONSOLE_CONTAINER -->\n'
                    f'<!-- ====================================================================== -->\n'
                    f'{{% endblock %}}\n'
                )
# ======================================================================
# END: PATH_RESOLUTION_AND_HTML_TEMPLATE_FORGE (PATCH 2 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/utils/page_skeleton.py (PATCH 3 OF 5)
# START: CLASS_BASED_VIEW_GENERATION_AND_WHITE_LIST_REGISTRATION
# ======================================================================
            # 2. Class-Based View Generation with Explicit Module Anchors
            cls.emit_log(f"[FORGE_ENGINE] Synthesizing View subclass python module: {view_file}\n")
            os.makedirs(os.path.dirname(view_file), exist_ok=True)
            with open(view_file, 'w') as f:
                mixin_import = "from django.contrib.auth.mixins import LoginRequiredMixin\n" if is_private else ""
                mixin_inheritance = "LoginRequiredMixin, " if is_private else ""
                f.write(
                    f'# ======================================================================\n'
                    f'# FILE: {app}/views/{page}_view.py\n'
                    f'# START: PACKAGED_IMPORTS_AND_DEPENDENCIES\n'
                    f'# ======================================================================\n'
                    f'from django.views.generic import TemplateView\n{mixin_import}'
                    f'# ======================================================================\n'
                    f'# END: PACKAGED_IMPORTS_AND_DEPENDENCIES\n'
                    f'# ======================================================================\n\n'
                    f'# ======================================================================\n'
                    f'# START: CLASS_BASED_VIEW_ROUTING\n'
                    f'# ======================================================================\n'
                    f'class {class_name}({mixin_inheritance}TemplateView):\n'
                    f'    template_name = "{app}/{page}.html"\n\n'
                    f'    def get_context_data(self, **kwargs):\n'
                    f'        context = super().get_context_data(**kwargs)\n'
                    f'        context["page_title"] = "{page.replace("_", " ").title()}"\n'
                    f'        context["return_path"] = "/hopehub/" if "{app}" == "hopehub" else "/aurora/"\n'
                    f'        return context\n'
                    f'# ======================================================================\n'
                    f'# END: CLASS_BASED_VIEW_ROUTING\n'
                    f'# ======================================================================\n'
                )

            # 3. Inject to views/__init__.py package whitelist safely
            if os.path.exists(view_init):
                cls.emit_log(f"[FORGE_ENGINE] Registering {class_name} to views initialization exports layer: {view_init}\n")
                with open(view_init, 'r') as f:
                    content = f.read()
                import_stmt = f"from .{page}_view import {class_name}\n"
                if import_stmt not in content:
                    content = import_stmt + content
                if "__all__ = [" in content:
                    parts = content.split("__all__ = [")
                    sub_parts = parts[1].split("]", 1)
                    inner_all = sub_parts[0].strip()
                    if inner_all and not inner_all.endswith(","):
                        inner_all += ","
                    inner_all += f"\n    '{class_name}',"
                    sub_parts[0] = f"\n    {inner_all.strip()}\n"
                    parts[1] = "]".join(sub_parts)
                    content = "__all__ = [".join(parts)
                with open(view_init, 'w') as f:
                    f.write(content)
# ======================================================================
# END: CLASS_BASED_VIEW_GENERATION_AND_WHITE_LIST_REGISTRATION (PATCH 3 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/utils/page_skeleton.py (PATCH 4 OF 5)
# START: CLEAN_URL_ROUTING_INJECTION_AND_FORGE_COMPLETION
# ======================================================================
            # 4. Inject into target urls.py pattern loop safely
            if os.path.exists(urls_file):
                cls.emit_log(
                    f"[FORGE_ENGINE] Injecting layout routing pathway "
                    f"to URL dispatcher configuration: {urls_file}\n"
                )
                with open(urls_file, 'r') as f:
                    urls_content = f.read()

                if "urlpatterns = [" in urls_content:
                    parts = urls_content.split("urlpatterns = [")
                    sub_parts = parts[1].split("]", 1)
                    inner_urls = sub_parts[0].rstrip()
                    url_route = (
                        f"    path('{page}/', views.{class_name}.as_view(), "
                        f"name='{page}'),"
                    )

                    if url_route.strip() not in inner_urls:
                        sub_parts[0] = f"{inner_urls}\n{url_route}\n"

                    parts[1] = "]".join(sub_parts)
                    urls_content = "urlpatterns = [".join(parts)

                with open(urls_file, 'w') as f:
                    f.write(urls_content)

            cls.emit_log(
                f"[FORGE_ENGINE] SUCCESS: Architectural canvas "
                f"'{class_name}' successfully compiled.\n"
            )
            return {
                "status": "success",
                "message": (
                    f"Successfully forged '{class_name}' inside app "
                    f"'{app}' ({visibility})."
                ),
            }

        except Exception as e:
            cls.emit_log(
                f"[FORGE_ENGINE] [CRITICAL] Compilation exception caught "
                f"inside forge layer: {str(e)}\n"
            )
            return {
                "status": "error",
                "message": f"Failed to execute forge sequence: {str(e)}",
            }
# ======================================================================
# END: CLEAN_URL_ROUTING_INJECTION_AND_FORGE_COMPLETION (PATCH 4 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/utils/page_skeleton.py (PATCH 5 OF 5)
# START: SURGICAL_COMPONENT_PURGE_ROUTINE
# ======================================================================
    @classmethod
    def purge_page(cls, target_app: str, page_name: str) -> dict:
        """Surgically removes forged filesystem artifacts and legacy metadata."""
        app, page, class_name = cls.clean_inputs(target_app, page_name)
        base_dir = os.getcwd()
        view_file = os.path.join(base_dir, app, 'views', f'{page}_view.py')
        view_init = os.path.join(base_dir, app, 'views', '__init__.py')
        template_file = os.path.join(
            base_dir,
            app,
            'templates',
            app,
            f'{page}.html',
        )
        urls_file = os.path.join(base_dir, app, 'urls.py')
        logs = []

        cls.emit_log(
            f"[FORGE_ENGINE] Initializing surgical wipe operation for "
            f"component module: {app}/{page}\n"
        )

        try:
            if os.path.exists(view_file):
                os.remove(view_file)
                logs.append(f"Deleted view: {page}_view.py")
                cls.emit_log(
                    f"[FORGE_ENGINE] [PURGE] Physically erased view "
                    f"controller script: {view_file}\n"
                )

            if os.path.exists(template_file):
                os.remove(template_file)
                logs.append(f"Deleted template: {page}.html")
                cls.emit_log(
                    f"[FORGE_ENGINE] [PURGE] Physically erased template "
                    f"HTML layout: {template_file}\n"
                )

            if os.path.exists(view_init):
                with open(view_init, 'r') as f:
                    lines = f.readlines()

                clean_lines = [
                    line
                    for line in lines
                    if f"{page}_view" not in line
                    and f"'{class_name}'" not in line
                ]

                with open(view_init, 'w') as f:
                    f.writelines(clean_lines)

                logs.append("Scrubbed package exporter.")
                cls.emit_log(
                    f"[FORGE_ENGINE] [PURGE] Cleaned package whitelist "
                    f"references inside: {view_init}\n"
                )

            if os.path.exists(urls_file):
                with open(urls_file, 'r') as f:
                    lines = f.readlines()

                clean_lines = [
                    line
                    for line in lines
                    if f"views.{class_name}.as_view()" not in line
                    and f"'{page}/'" not in line
                ]

                with open(urls_file, 'w') as f:
                    f.writelines(clean_lines)

                logs.append("Erased url routing node.")
                cls.emit_log(
                    f"[FORGE_ENGINE] [PURGE] Cleaned application URL "
                    f"configuration space: {urls_file}\n"
                )

            try:
                from aurora.models import ComponentRegistry
                from neomodel import db

                rel_view_path = f"{app}/views/{page}_view.py"
                ComponentRegistry.objects.filter(
                    file_path=rel_view_path
                ).delete()
                db.cypher_query(
                    (
                        "MATCH (n:ComponentNode) "
                        "WHERE n.file_path = $path "
                        "DETACH DELETE n"
                    ),
                    {"path": rel_view_path},
                )
                logs.append("Purged controller view metadata mappings.")

            except Exception as scrub_err:
                cls.emit_log(
                    f"[WARNING] Database mirror cleanup anomaly: "
                    f"{str(scrub_err)}\n"
                )

            cls.emit_log(
                f"[FORGE_ENGINE] Wipe routing complete for {page}. "
                f"Status: Success.\n"
            )
            return {
                "status": "success",
                "message": (
                    " | ".join(logs)
                    if logs
                    else "No structural components found to purge."
                ),
            }

        except Exception as e:
            cls.emit_log(
                f"[FORGE_ENGINE] [CRITICAL] Wipe failure occurred during "
                f"unlinking procedure: {str(e)}\n"
            )
            return {
                "status": "error",
                "message": f"Surgical wipe failure: {str(e)}",
            }
# ======================================================================
# END: SURGICAL_COMPONENT_PURGE_ROUTINE (PATCH 5 OF 5)
# ======================================================================s