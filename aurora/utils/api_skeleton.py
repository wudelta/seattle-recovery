# ======================================================================
# FILE: aurora/utils/api_skeleton.py (PATCH 1 of 5)
# START: PACKAGED_IMPORTS_AND_INPUT_SANITIZATION
# ======================================================================
import os
import re
import traceback
from aurora.api.dev_streamer_api import send_to_console

class ApiSkeletonBuilder:
    """Automated multi-app builder and destroyer to forge functional API endpoints with visibility safety."""

    @staticmethod
    def clean_inputs(app_name: str, endpoint_name: str):
        app = re.sub(r'[^a-zA-Z0-9_]', '', app_name.lower().strip())
        page = re.sub(r'[^a-zA-Z0-9_]', '', endpoint_name.lower().strip())
        func_name = f"{page}_endpoint"
        return app, page, func_name
# ======================================================================
# END: PACKAGED_IMPORTS_AND_INPUT_SANITIZATION
# ======================================================================

# ======================================================================
# FILE: aurora/utils/api_skeleton.py (PATCH 2 OF 5)
# START: PATH_RESOLUTION_AND_FUNCTION_VIEW_FORGE
# ======================================================================
    @classmethod
    def forge_api(cls, target_app: str, endpoint_name: str, visibility: str) -> dict:
        app, endpoint, func_name = cls.clean_inputs(target_app, endpoint_name)
        if not app or not endpoint:
            send_to_console("[FORGE_ENGINE] [FAIL] Invalid parameters provided to forge API.")
            return {"status": "error", "message": "Invalid architectural parameters."}

        is_private = visibility.lower().strip() != "public"
        base_dir = os.getcwd()

        if not os.path.exists(os.path.join(base_dir, app)):
            send_to_console(f"[FORGE_ENGINE] [FAIL] Target app directory '{app}' does not exist on host.")
            return {"status": "error", "message": f"Target app directory '{app}' does not exist."}

        view_file = os.path.join(base_dir, app, 'api', f'{endpoint}_api.py')
        view_init = os.path.join(base_dir, app, 'api', '__init__.py')
        urls_file = os.path.join(base_dir, app, 'urls.py')
        test_file = os.path.join(base_dir, app, 'tests', f'test_api_{endpoint}_{app}.py')

        if os.path.exists(view_file):
            send_to_console(f"[FORGE_ENGINE] [FAIL] Collision detected: API Component '{endpoint}' already exists.")
            return {"status": "error", "message": f"Collision: API Component '{endpoint}' already exists."}

        try:
            # 1. Generate Function-Based View with Explicit Module Anchors
            send_to_console(f"[INFO] Writing endpoint logic script file artifact: {view_file}")
            os.makedirs(os.path.dirname(view_file), exist_ok=True)
            with open(view_file, 'w') as f:
                dec_import = "from django.contrib.auth.decorators import login_required\n" if is_private else ""
                dec_line = "@login_required\n" if is_private else ""
                f.write(
                    f'# ======================================================================\n'
                    f'# FILE: {app}/api/{endpoint}_api.py\n'
                    f'# START: PACKAGED_IMPORTS_AND_DEPENDENCIES\n'
                    f'# ======================================================================\n'
                    f'from django.http import JsonResponse\n{dec_import}'
                    f'# ======================================================================\n'
                    f'# END: PACKAGED_IMPORTS_AND_DEPENDENCIES\n'
                    f'# ======================================================================\n\n'
                    f'# ======================================================================\n'
                    f'# START: API_ENDPOINT_LOGIC\n'
                    f'# ======================================================================\n'
                    f'{dec_line}'
                    f'def {func_name}(request):\n'
                    f'    """Automated JSON payload endpoint forged by Aurora Forge Engine."""\n'
                    f'    payload = {{\n'
                    f'        "status": "success",\n'
                    f'        "visibility": "{visibility}",\n'
                    f'        "endpoint": "{endpoint}",\n'
                    f'        "app": "{app}"\n'
                    f'    }}\n'
                    f'    return JsonResponse(payload)\n'
                    f'# ======================================================================\n'
                    f'# END: API_ENDPOINT_LOGIC\n'
                    f'# ======================================================================\n'
                )
# ======================================================================
# END: PATH_RESOLUTION_AND_FUNCTION_VIEW_FORGE
# ======================================================================

# ======================================================================
# FILE: aurora/utils/api_skeleton.py (PATCH 3 OF 5)
# START: API_PACKAGE_WHITELIST_INJECTION
# ======================================================================
            # 2. Inject to api/__init__.py whitelist package exporter loop
            send_to_console(f"[INFO] Appending API hook function to package exports initialization layer: {view_init}")
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
# END: API_PACKAGE_WHITELIST_INJECTION
# ======================================================================

# ======================================================================
# FILE: aurora/utils/api_skeleton.py (PATCH 4 OF 5)
# START: URL_ROUTING_INJECTION_AND_ISOLATED_TEST_GENERATION
# ======================================================================
            # 3. Inject into target urls.py pattern loop safely
            if os.path.exists(urls_file):
                send_to_console(f"[INFO] Injecting endpoint routing pathway to URL dispatcher configuration: {urls_file}")
                with open(urls_file, 'r') as f:
                    urls_content = f.read()
                # Refactored package alias name from api_views to api_commands
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

            # 4. Forged API Unit Test Generation for Component Verification
            send_to_console(f"[INFO] Writing automated validation test suite harness: {test_file}")
            os.makedirs(os.path.dirname(test_file), exist_ok=True)
            with open(test_file, 'w') as f:
                exp_status = "302" if is_private else "200"
                fmt_cls = func_name.replace("_", " ").title().replace(" ", "")
                f.write(
                    f'# ======================================================================\n'
                    f'# FILE: {app}/tests/test_api_{endpoint}_{app}.py\n'
                    f'# START: LIFECYCLE_TEST_SUITE_SETUP\n'
                    f'# ======================================================================\n'
                    f'import os\n'
                    f'from django.test import TestCase\n'
                    f'from django.urls import reverse\n'
                    f'from django.contrib.auth.models import User\n'
                    f'from neomodel import db\n'
                    f'from aurora.models import ComponentRegistry\n'
                    f'from aurora.utils.forge_registry import register_new_component\n\n'
                    f'class {app.capitalize()}{fmt_cls}ProductionTest(TestCase):\n'
                    f'    def setUp(self):\n'
                    f'        self.test_user = User.objects.create_user(username="test_dev", password="password")\n'
                    f'        self.expected_path = "{app}/api/{endpoint}_api.py"\n'
                    f'        # Enforce graph loopback isolation by clearing unique paths before validation\n'
                    f'        try:\n'
                    f'            db.cypher_query("MATCH (n:ComponentNode) WHERE n.file_path = \'" + self.expected_path + "\' DETACH DELETE n")\n'
                    f'        except Exception:\n'
                    f'            pass\n'
                    f'        register_new_component(self.expected_path, "{func_name}", "{visibility}", self.test_user, "ENTRY_POINT", "Verification baseline")\n'
                    f'# ======================================================================\n'
                    f'# END: LIFECYCLE_TEST_SUITE_SETUP\n'
                    f'# ======================================================================\n\n'
                    f'# ======================================================================\n'
                    f'# START: LIFECYCLE_TEST_EXECUTION_FLOW\n'
                    f'# ======================================================================\n'
                    f'    def test_forged_endpoint_integrity(self):\n'
                    f'        disk_path = os.path.join(os.getcwd(), "{app}", "api", "{endpoint}_api.py")\n'
                    f'        self.assertTrue(os.path.exists(disk_path), f"API core module missing from disk path: {{disk_path}}")\n\n'
                    f'        url = reverse("{app}:{func_name}")\n'
                    f'        response = self.client.get(url)\n'
                    f'        self.assertEqual(response.status_code, {exp_status})\n\n'
                    f'        self.assertTrue(ComponentRegistry.objects.filter(file_path=self.expected_path).exists(), "Postgres API endpoint index mapping unresolved.")\n'
                    f'# ======================================================================\n'
                    f'# END: LIFECYCLE_TEST_EXECUTION_FLOW\n'
                    f'# ======================================================================\n'
                )
            send_to_console(f"[SUCCESS] Functional API module '{func_name}' successfully compiled.")
            return {"status": "success", "message": f"Successfully forged API function '{func_name}' inside app '{app}/api/' ({visibility})."}
        except Exception as e:
            error_trace = f"[FAIL] Compilation exception caught inside forge layer:\n{traceback.format_exc()}"
            send_to_console(error_trace)
            return {"status": "error", "message": f"Failed to execute API forge sequence: {str(e)}"}
# ======================================================================
# END: URL_ROUTING_INJECTION_AND_ISOLATED_TEST_GENERATION
# ======================================================================

# ======================================================================
# FILE: aurora/utils/api_skeleton.py (PATCH 5 OF 5)
# START: SURGICAL_API_COMPONENT_PURGE_ROUTINE
# ======================================================================
    @classmethod
    def purge_api(cls, target_app: str, endpoint_name: str) -> dict:
        """Surgically undoes file builds and deletes registrations completely."""
        app, endpoint, func_name = cls.clean_inputs(target_app, endpoint_name)
        base_dir = os.getcwd()

        view_file = os.path.join(base_dir, app, 'api', f'{endpoint}_api.py')
        view_init = os.path.join(base_dir, app, 'api', '__init__.py')
        urls_file = os.path.join(base_dir, app, 'urls.py')
        test_file = os.path.join(base_dir, app, 'tests', f'test_api_{endpoint}_{app}.py')
        logs = []

        send_to_console(f"[INFO] Initializing surgical wipe operation for API endpoint: {app}/api/{endpoint}_api.py")

        try:
            if os.path.exists(view_file):
                os.remove(view_file)
                logs.append(f"Deleted api: {endpoint}_api.py")
                send_to_console(f"[INFO] [PURGE] Physically erased API core script: {view_file}")

            # PRESERVE TEST SUITE INFRASTRUCTURE DURING ACTIVE RUNS
            if os.path.exists(test_file):
                if "AURORA_TEST_RUNNING" not in os.environ:
                    os.remove(test_file)
                    logs.append(f"Deleted test file: test_api_{endpoint}_{app}.py")
                    send_to_console(f"[INFO] [PURGE] Physically erased test script module: {test_file}")
                else:
                    logs.append("Preserved test file context during active test suite execution.")

            if os.path.exists(view_init):
                with open(view_init, 'r') as f:
                    lines = f.readlines()
                clean_lines = [l for l in lines if f"{endpoint}_api" not in l and f"'{func_name}'" not in l]
                with open(view_init, 'w') as f:
                    f.writelines(clean_lines)
                logs.append("Scrubbed api package exporter.")
                send_to_console(f"[INFO] [PURGE] Cleaned API package whitelist references inside: {view_init}")

            if os.path.exists(urls_file):
                with open(urls_file, 'r') as f:
                    lines = f.readlines()
                # Refactored to hunt and clear api_commands syntax footprints instead of api_views
                clean_lines = [l for l in lines if f"api_commands.{func_name}" not in l and f"'api/{endpoint}/'" not in l]
                with open(urls_file, 'w') as f:
                    f.writelines(clean_lines)
                logs.append("Erased url routing node.")
                send_to_console(f"[INFO] [PURGE] Cleaned application URL configuration space: {urls_file}")

            send_to_console(f"[SUCCESS] Wipe routine complete for API '{endpoint}'. Status: Success.")
            return {"status": "success", "message": " | ".join(logs) if logs else "No API components found to purge."}

        except Exception as e:
            error_trace = f"[FAIL] Wipe failure occurred during API unlinking procedure:\n{traceback.format_exc()}"
            send_to_console(error_trace)
            return {"status": "error", "message": f"Surgical wipe failure: {str(e)}"}
# ======================================================================
# END: SURGICAL_API_COMPONENT_PURGE_ROUTINE
# ======================================================================
