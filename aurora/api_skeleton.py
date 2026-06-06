# ======================================================================
# FILE: aurora/api_skeleton.py (PATCH 1 OF 5)
# START: INITIAL CONFIGURATIONS & CORE IMPORTS
# ======================================================================
import os
import re

class ApiSkeletonBuilder:
    """Automated multi-app builder and destroyer to forge functional API endpoints with visibility safety."""

    @staticmethod
    def clean_inputs(app_name: str, endpoint_name: str):
        app = re.sub(r'[^a-zA-Z0-9_]', '', app_name.lower().strip())
        endpoint = re.sub(r'[^a-zA-Z0-9_]', '', endpoint_name.lower().strip())
        func_name = f"{endpoint}_endpoint"
        return app, endpoint, func_name
# ======================================================================
# END: INITIAL CONFIGURATIONS & CORE IMPORTS
# ======================================================================

# ======================================================================
# FILE: aurora/api_skeleton.py (PATCH 2 OF 5)
# START: FORGE PATH RESOLUTION & FUNCTION-BASED VIEW GENERATION
# ======================================================================
    @classmethod
    def forge_api(cls, target_app: str, endpoint_name: str, visibility: str) -> dict:
        app, endpoint, func_name = cls.clean_inputs(target_app, endpoint_name)
        if not app or not endpoint:
            return {"status": "error", "message": "Invalid architectural parameters."}
        
        is_private = visibility.lower().strip() != "public"
        base_dir = os.getcwd()
        
        if not os.path.exists(os.path.join(base_dir, app)):
            return {"status": "error", "message": f"Target app directory '{app}' does not exist."}

        # STRUCTURAL REDIRECT: Target 'api/' directory with matching naming convention
        view_file = os.path.join(base_dir, app, 'api', f'{endpoint}_api.py')
        view_init = os.path.join(base_dir, app, 'api', '__init__.py')
        urls_file = os.path.join(base_dir, app, 'urls.py')
        
        # FIXED PARADIGM: Isolated filename path to prevent Page collision
        test_file = os.path.join(base_dir, app, 'tests', f'test_api_{endpoint}_{app}.py')

        if os.path.exists(view_file):
            return {"status": "error", "message": f"Collision: API Component '{endpoint}' already exists."}

        try:
            # 1. Generate Function-Based View Returning JSON Payload Data
            os.makedirs(os.path.dirname(view_file), exist_ok=True)
            with open(view_file, 'w') as f:
                dec_import = "from django.contrib.auth.decorators import login_required\n" if is_private else ""
                dec_line = "@login_required\n" if is_private else ""
                f.write(
                    f'# {app}/api/{endpoint}_api.py\n'
                    f'from django.http import JsonResponse\n{dec_import}\n'
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
                )
# ======================================================================
# END: FORGE PATH RESOLUTION & FUNCTION-BASED VIEW GENERATION
# ======================================================================

# ======================================================================
# FILE: aurora/api_skeleton.py (PATCH 3 OF 5)
# START: API PACKAGE INITIALIZATION & EXPORT LOOP CONTROL
# ======================================================================
            # 2. Inject to api/__init__.py whitelist package exporter loop
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
# END: API PACKAGE INITIALIZATION & EXPORT LOOP CONTROL
# ======================================================================

# ======================================================================
# FILE: aurora/api_skeleton.py (PATCH 4 OF 5)
# START: API URL ROUTING & DECOUPLED UNIT TEST GENERATION
# ======================================================================
            # 3. Inject into target urls.py pattern loop
            if os.path.exists(urls_file):
                with open(urls_file, 'r') as f:
                    urls_content = f.read()
                if f"from {app} import api as api_views" not in urls_content:
                    urls_content = f"from {app} import api as api_views\n" + urls_content
                if "urlpatterns = [" in urls_content:
                    p = urls_content.split("urlpatterns = [")
                    sp = p[1].split("]", 1)
                    inner = sp[0].rstrip()
                    route = f"    path('api/{endpoint}/', api_views.{func_name}, name='{func_name}'),"
                    if route.strip() not in inner:
                        sp[0] = f"{inner}\n{route}\n"
                    p[1] = "]".join(sp)
                    urls_content = "urlpatterns = [".join(p)
                with open(urls_file, 'w') as f:
                    f.write(urls_content)

            # 4. Forged API Unit Test Generation with Database Assertions
            os.makedirs(os.path.dirname(test_file), exist_ok=True)
            with open(test_file, 'w') as f:
                exp_status = "302" if is_private else "200"
                fmt_cls = func_name.replace("_", " ").title().replace(" ", "")
                test_header = (
                    f'# {app}/tests/test_api_{endpoint}_{app}.py\n'
                    f'import os\n'
                    f'from django.test import TestCase\n'
                    f'from django.urls import reverse\n'
                    f'from aurora.models import ComponentRegistry\n'
                    f'from aurora.nodes import ComponentNode\n'
                    f'from aurora.api_skeleton import ApiSkeletonBuilder\n\n'
                    f'class {app.capitalize()}{fmt_cls}IsolationTest(TestCase):\n'
                    f'    def test_api_lifecycle_forge_and_destruction_sync(self):\n'
                    f'        expected_path = "{app}/api/{endpoint}_api.py"\n\n'
                )
                test_body_1 = (
                    f'        # PHASE 1: HTTP pipeline gate check\n'
                    f'        url = reverse("{app}:{func_name}")\n'
                    f'        response = self.client.get(url)\n'
                    f'        self.assertEqual(response.status_code, {exp_status})\n\n'
                    f'        # PHASE 2: Verify forge footprint database writing accuracy\n'
                    f'        self.assertTrue(ComponentRegistry.objects.filter(file_path=expected_path).exists())\n'
                    f'        try:\n'
                    f'            node = ComponentNode.nodes.get(file_path=expected_path)\n'
                    f'            self.assertIsNotNone(node.postgres_id)\n'
                    f'        except ComponentNode.DoesNotExist:\n'
                    f'            self.fail("Neo4j Graph Node missing on forge.")\n\n'
                )
                test_body_2 = (
                    f'        # PHASE 3: Trigger console destruction clean wipe simulation\n'
                    f'        ApiSkeletonBuilder.purge_api("{app}", "{endpoint}")\n'
                    f'        ComponentRegistry.objects.filter(file_path=expected_path).delete()\n\n'
                    f'        # PHASE 4: Enforce destruction verification loops\n'
                    f'        self.assertFalse(ComponentRegistry.objects.filter(file_path=expected_path).exists())\n'
                    f'        try:\n'
                    f'            ComponentNode.nodes.get(file_path=expected_path)\n'
                    f'            self.fail("Neo4j node leaked after execution of destroy loop.")\n'
                    f'        except ComponentNode.DoesNotExist:\n'
                    f'            pass\n'
                )
                f.write(test_header + test_body_1 + test_body_2)

            return {"status": "success", "message": f"Successfully forged API function '{func_name}' inside app '{app}/api/' ({visibility})."}
        except Exception as e:
            return {"status": "error", "message": f"Failed to execute API forge sequence: {str(e)}"}
# ======================================================================
# END: API URL ROUTING & DECOUPLED UNIT TEST GENERATION
# ======================================================================

# ======================================================================
# FILE: aurora/api_skeleton.py (PATCH 5 OF 5)
# START: SURGICAL API COMPONENT PURGE ROUTINE
# ======================================================================
    @classmethod
    def purge_api(cls, target_app: str, endpoint_name: str) -> dict:
        """Surgically undoes file builds and deletes registrations completely."""
        app, endpoint, func_name = cls.clean_inputs(target_app, endpoint_name)
        base_dir = os.getcwd()
        
        view_file = os.path.join(base_dir, app, 'api', f'{endpoint}_api.py')
        view_init = os.path.join(base_dir, app, 'api', '__init__.py')
        urls_file = os.path.join(base_dir, app, 'urls.py')
        
        # FIXED PARADIGM: Targeted erasure of the isolated API test filename
        test_file = os.path.join(base_dir, app, 'tests', f'test_api_{endpoint}_{app}.py')
        
        logs = []
        try:
            if os.path.exists(view_file):
                os.remove(view_file)
                logs.append(f"Deleted api: {endpoint}_api.py")
            if os.path.exists(test_file):
                os.remove(test_file)
                logs.append(f"Deleted test file: test_api_{endpoint}_{app}.py")
            if os.path.exists(view_init):
                with open(view_init, 'r') as f:
                    lines = f.readlines()
                clean_lines = [l for l in lines if f"{endpoint}_api" not in l and f"'{func_name}'" not in l]
                with open(view_init, 'w') as f:
                    f.writelines(clean_lines)
                logs.append("Scrubbed api package exporter.")
            if os.path.exists(urls_file):
                with open(urls_file, 'r') as f:
                    lines = f.readlines()
                clean_lines = [l for l in lines if f"api_views.{func_name}" not in l and f"'api/{endpoint}/'" not in l]
                with open(urls_file, 'w') as f:
                    f.writelines(clean_lines)
                logs.append("Erased url routing node.")
                
            return {"status": "success", "message": " | ".join(logs) if logs else "No API components found to purge."}
        except Exception as e:
            return {"status": "error", "message": f"Surgical wipe failure: {str(e)}"}
# ======================================================================
# END: SURGICAL API COMPONENT PURGE ROUTINE
# ======================================================================
