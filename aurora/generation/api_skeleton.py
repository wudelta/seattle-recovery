# ======================================================================
# FILE: aurora/utils/api_skeleton.py (PATCH 1 OF 5)
# START: PACKAGED_IMPORTS_AND_INPUT_SANITIZATION
# ======================================================================
import os
import re
import traceback

from django.conf import settings

from aurora.utils.telemetry import TelemetryLogger


class ApiSkeletonBuilder:
    """Automated multi-app builder and destroyer to forge functional API endpoints with visibility safety."""

    @classmethod
    def emit_log(cls, text: str):
        """Routes utility trace metrics directly into the shared master telemetry buffer pool."""
        TelemetryLogger.emit(text)

    @staticmethod
    def clean_inputs(app_name: str, endpoint_name: str):
        app = re.sub(r'[^a-zA-Z0-9_]', '', app_name.lower().strip())
        page = re.sub(r'[^a-zA-Z0-9_]', '', endpoint_name.lower().strip())
        func_name = f"{page}_endpoint"
        return app, page, func_name
# ======================================================================
# END: PACKAGED_IMPORTS_AND_INPUT_SANITIZATION (PATCH 1 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/utils/api_skeleton.py (PATCH 2 OF 5)
# START: PATH_RESOLUTION_AND_FUNCTION_VIEW_FORGE
# ======================================================================
    @classmethod
    def forge_api(
        cls,
        target_app: str,
        endpoint_name: str,
        visibility: str,
    ) -> dict:
        app, endpoint, func_name = cls.clean_inputs(
            target_app,
            endpoint_name,
        )

        if not app or not endpoint:
            cls.emit_log(
                "[FORGE_ENGINE] [FAIL] Invalid parameters provided "
                "to forge API.\n"
            )
            return {
                "status": "error",
                "message": "Invalid architectural parameters.",
            }

        is_private = visibility.lower().strip() != "public"
        base_dir = str(settings.BASE_DIR)
        app_dir = os.path.join(base_dir, app)
        api_dir = os.path.join(app_dir, "api")

        if not os.path.isdir(app_dir):
            cls.emit_log(
                "[FORGE_ENGINE] [FAIL] Target app directory "
                f"'{app}' does not exist on host.\n"
            )
            return {
                "status": "error",
                "message": (
                    f"Target app directory '{app}' does not exist."
                ),
            }

        if not os.path.isdir(api_dir):
            cls.emit_log(
                "[FORGE_ENGINE] [FAIL] Target API directory does not "
                f"exist: '{app}/api'.\n"
            )
            return {
                "status": "error",
                "message": (
                    f"Target API directory '{app}/api' does not exist. "
                    "Directory creation requires an explicit "
                    "architectural operation."
                ),
            }

        view_file = os.path.join(
            api_dir,
            f"{endpoint}_api.py",
        )
        view_init = os.path.join(
            api_dir,
            "__init__.py",
        )
        urls_file = os.path.join(
            app_dir,
            "urls.py",
        )
        test_file = os.path.join(
            app_dir,
            "tests",
            f"test_api_{endpoint}_{app}.py",
        )

        if os.path.exists(view_file):
            cls.emit_log(
                "[FORGE_ENGINE] [FAIL] Collision detected: API "
                f"Component '{endpoint}' already exists.\n"
            )
            return {
                "status": "error",
                "message": (
                    f"Collision: API Component '{endpoint}' "
                    "already exists."
                ),
            }

        try:
            # 1. Generate Function-Based View with Explicit Module Anchors
            cls.emit_log(
                "[INFO] Writing endpoint logic script file artifact: "
                f"{view_file}\n"
            )

            with open(view_file, "w") as file_handle:
                decorator_import = (
                    "from django.contrib.auth.decorators "
                    "import login_required\n"
                    if is_private
                    else ""
                )
                decorator_line = (
                    "@login_required\n"
                    if is_private
                    else ""
                )
                file_handle.write(
                    f"# {'=' * 70}\n"
                    f"# FILE: {app}/api/{endpoint}_api.py\n"
                    "# START: PACKAGED_IMPORTS_AND_DEPENDENCIES\n"
                    f"# {'=' * 70}\n"
                    "from django.http import JsonResponse\n"
                    f"{decorator_import}"
                    f"# {'=' * 70}\n"
                    "# END: PACKAGED_IMPORTS_AND_DEPENDENCIES\n"
                    f"# {'=' * 70}\n\n"
                    f"# {'=' * 70}\n"
                    "# START: API_ENDPOINT_LOGIC\n"
                    f"# {'=' * 70}\n"
                    f"{decorator_line}"
                    f"def {func_name}(request):\n"
                    '    """Automated JSON payload endpoint forged '
                    'by Aurora Forge Engine."""\n'
                    "    payload = {\n"
                    '        "status": "success",\n'
                    f'        "visibility": "{visibility}",\n'
                    f'        "endpoint": "{endpoint}",\n'
                    f'        "app": "{app}"\n'
                    "    }\n"
                    "    return JsonResponse(payload)\n"
                    f"# {'=' * 70}\n"
                    "# END: API_ENDPOINT_LOGIC\n"
                    f"# {'=' * 70}\n"
                )
# ======================================================================
# END: PATH_RESOLUTION_AND_FUNCTION_VIEW_FORGE (PATCH 2 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/utils/api_skeleton.py (PATCH 3 OF 5)
# START: API_PACKAGE_WHITELIST_INJECTION
# ======================================================================
            # 2. Inject to api/__init__.py whitelist package exporter loop
            # FIXED: Converted tracking log label prefix signature from [INFO] to [FORGE_ENGINE]
            cls.emit_log(f"[FORGE_ENGINE] Appending API hook function to package exports initialization layer: {view_init}\n")
            mode = 'r+' if os.path.exists(view_init) else 'w+'
            with open(view_init, mode) as f:
                content = f.read() if mode == 'r+' else ""
                import_stmt = f"from .{endpoint}_api import {func_name}\n"
                if import_stmt not in content:
                    content = import_stmt + content
                if "__all__ = [" in content:
                    p = content.split("__all__ = [")
                    sp = p[1].split("]", 1)
                    inner = sp[0].strip()
                    if inner and not inner.endswith(","):
                        inner += ","
                    inner += f"\n    '{func_name}',"
                    sp[0] = f"\n    {inner.strip()}\n"
                    p[1] = "]".join(sp)
                    content = "__all__ = [".join(p)
                elif mode == 'w+':
                    content += f"\n__all__ = [\n    '{func_name}'\n]\n"
                f.seek(0)
                f.write(content)
                f.truncate()
# ======================================================================
# END: API_PACKAGE_WHITELIST_INJECTION (PATCH 3 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/utils/api_skeleton.py (PATCH 4 OF 5)
# START: URL_ROUTING_INJECTION_AND_FORGE_COMPLETION
# ======================================================================
            # 3. Inject into target urls.py pattern loop safely
            if os.path.exists(urls_file):
                cls.emit_log(f"[FORGE_ENGINE] Injecting endpoint routing pathway to URL dispatcher configuration: {urls_file}\n")
                with open(urls_file, 'r') as f:
                    urls_content = f.read()
                if f"from {app} import api as api_commands" not in urls_content:
                    urls_content = f"from {app} import api as api_commands\n" + urls_content
                if "urlpatterns = [" in urls_content:
                    p = urls_content.split("urlpatterns = [")
                    sp = p[1].split("]", 1)
                    inner = sp[0].rstrip()
                    route = f"    path('api/{endpoint}/', api_commands.{func_name}, name='{func_name}'),"
                    if route.strip() not in inner:
                        sp[0] = f"{inner}\n{route}\n"
                    p[1] = "]".join(sp)
                    urls_content = "urlpatterns = [".join(p)
                with open(urls_file, 'w') as f:
                    f.write(urls_content)

            cls.emit_log(f"[FORGE_ENGINE] SUCCESS: Functional API module '{func_name}' successfully compiled.\n")
            return {"status": "success", "message": f"Successfully forged API function '{func_name}' inside app '{app}/api/' ({visibility})."}
        except Exception as e:
            error_trace = f"[FAIL] Compilation exception caught inside forge layer:\n{traceback.format_exc()}"
            cls.emit_log(f"{error_trace}\n")
            return {"status": "error", "message": f"Failed to execute API forge sequence: {str(e)}"}
# ======================================================================
# END: URL_ROUTING_INJECTION_AND_FORGE_COMPLETION (PATCH 4 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/utils/api_skeleton.py (PATCH 5 OF 5)
# START: SURGICAL_API_COMPONENT_PURGE_ROUTINE
# ======================================================================
    @classmethod
    def purge_api(cls, target_app: str, endpoint_name: str) -> dict:
        """Surgically removes forged filesystem artifacts."""
        app, endpoint, func_name = cls.clean_inputs(target_app, endpoint_name)
        base_dir = os.getcwd()
        view_file = os.path.join(base_dir, app, 'api', f'{endpoint}_api.py')
        view_init = os.path.join(base_dir, app, 'api', '__init__.py')
        urls_file = os.path.join(base_dir, app, 'urls.py')
        logs = []

        cls.emit_log(
            f"[FORGE_ENGINE] Initializing surgical wipe operation for API endpoint: "
            f"{app}/api/{endpoint}_api.py\n"
        )

        try:
            if os.path.exists(view_file):
                os.remove(view_file)
                logs.append(f"Deleted api: {endpoint}_api.py")
                cls.emit_log(
                    f"[FORGE_ENGINE] [PURGE] Physically erased API core script: "
                    f"{view_file}\n"
                )

            if os.path.exists(view_init):
                with open(view_init, 'r') as f:
                    lines = f.readlines()

                clean_lines = [
                    line
                    for line in lines
                    if f"{endpoint}_api" not in line
                    and f"'{func_name}'" not in line
                ]

                with open(view_init, 'w') as f:
                    f.writelines(clean_lines)

                logs.append("Scrubbed api package exporter.")
                cls.emit_log(
                    f"[FORGE_ENGINE] [PURGE] Cleaned API package whitelist "
                    f"references inside: {view_init}\n"
                )

            if os.path.exists(urls_file):
                with open(urls_file, 'r') as f:
                    lines = f.readlines()

                clean_lines = [
                    line
                    for line in lines
                    if f"api_commands.{func_name}" not in line
                    and f"'api/{endpoint}/'" not in line
                ]

                with open(urls_file, 'w') as f:
                    f.writelines(clean_lines)

                logs.append("Erased url routing node.")
                cls.emit_log(
                    f"[FORGE_ENGINE] [PURGE] Cleaned application URL "
                    f"configuration space: {urls_file}\n"
                )

            cls.emit_log(
                f"[FORGE_ENGINE] SUCCESS: Wipe routine complete for API "
                f"'{endpoint}'. Status: Success.\n"
            )

            return {
                "status": "success",
                "message": " | ".join(logs)
                if logs
                else "No API components found to purge.",
            }

        except Exception as e:
            error_trace = (
                "[FAIL] Wipe failure occurred during API unlinking procedure:\n"
                f"{traceback.format_exc()}"
            )
            cls.emit_log(f"{error_trace}\n")
            return {
                "status": "error",
                "message": f"Surgical wipe failure: {str(e)}",
            }
# ======================================================================
# END: SURGICAL_API_COMPONENT_PURGE_ROUTINE (PATCH 5 OF 5)
# ======================================================================