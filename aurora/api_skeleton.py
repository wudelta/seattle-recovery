# aurora/api_skeleton.py
import os
import re

class ApiSkeletonBuilder:
    """Automated multi-app builder and destroyer to forge or purge functional API endpoints with zero tokens."""

    @staticmethod
    def clean_inputs(app_name: str, endpoint_name: str):
        app = re.sub(r'[^a-zA-Z0-9_]', '', app_name.lower().strip())
        endpoint = re.sub(r'[^a-zA-Z0-9_]', '', endpoint_name.lower().strip())
        func_name = f"{endpoint}_endpoint"
        return app, endpoint, func_name

    @classmethod
    def forge_api(cls, target_app: str, endpoint_name: str) -> dict:
        app, endpoint, func_name = cls.clean_inputs(target_app, endpoint_name)
        if not app or not endpoint:
            return {"status": "error", "message": "Invalid architectural parameters."}

        base_dir = os.getcwd()
        if not os.path.exists(os.path.join(base_dir, app)):
            return {"status": "error", "message": f"Target app directory '{app}' does not exist."}

        view_file = os.path.join(base_dir, app, 'views', f'{endpoint}_view.py')
        view_init = os.path.join(base_dir, app, 'views', '__init__.py')
        urls_file = os.path.join(base_dir, app, 'urls.py')
        test_file = os.path.join(base_dir, app, 'tests', f'test_{endpoint}.py')

        if os.path.exists(view_file):
            return {"status": "error", "message": f"Collision: API Component '{endpoint}' already exists in app '{app}'."}

        try:
            # 1. Write Function-Based View Endpoint returning JSON
            os.makedirs(os.path.dirname(view_file), exist_ok=True)
            with open(view_file, 'w') as f:
                f.write(
                    f'# {app}/views/{endpoint}_view.py\n'
                    f'from django.http import JsonResponse\n'
                    f'from django.contrib.auth.decorators import login_required\n\n'
                    f'@login_required\n'
                    f'def {func_name}(request):\n'
                    f'    """Automated test payload endpoint forged by Aurora Forge Engine."""\n'
                    f'    payload = {{\n'
                    f'        "status": "success",\n'
                    f'        "message": "Dynamic API node executed successfully.",\n'
                    f'        "endpoint": "{endpoint}",\n'
                    f'        "app": "{app}"\n'
                    f'    }}\n'
                    f'    return JsonResponse(payload)\n'
                )

            # 2. Inject to views/__init__.py package whitelist
            if os.path.exists(view_init):
                with open(view_init, 'r') as f:
                    content = f.read()
                import_stmt = f"from .{endpoint}_view import {func_name}\n"
                if import_stmt not in content:
                    content = import_stmt + content
                if "__all__ = [" in content:
                    parts = content.split("__all__ = [")
                    sub_parts = parts[1].split("]", 1)
                    inner_all = sub_parts[0].strip()
                    if inner_all and not inner_all.endswith(","):
                        inner_all += ","
                    inner_all += f"\n    '{func_name}',"
                    sub_parts[0] = f"\n    {inner_all.strip()}\n"
                    parts[1] = "]".join(sub_parts)
                    content = "__all__ = [".join(parts)
                with open(view_init, 'w') as f:
                    f.write(content)

            # 3. Inject into target urls.py pattern loop
            if os.path.exists(urls_file):
                with open(urls_file, 'r') as f:
                    urls_content = f.read()
                if "urlpatterns = [" in urls_content:
                    parts = urls_content.split("urlpatterns = [")
                    sub_parts = parts[1].split("]", 1)
                    inner_urls = sub_parts[0].rstrip()
                    url_route = f"    path('api/{endpoint}/', views.{func_name}, name='{func_name}'),"
                    if url_route.strip() not in inner_urls:
                        sub_parts[0] = f"{inner_urls}\n{url_route}\n"
                        parts[1] = "]".join(sub_parts)
                        urls_content = "urlpatterns = [".join(parts)
                with open(urls_file, 'w') as f:
                    f.write(urls_content)

            # 4. Forged API Unit Test Generation
            os.makedirs(os.path.dirname(test_file), exist_ok=True)
            formatted_cls = func_name.replace("_", " ").title().replace(" ", "")
            with open(test_file, 'w') as f:
                f.write(
                    f'# {app}/tests/test_{endpoint}_{app}.py\n'
                    f'from django.test import TestCase\n'
                    f'from django.urls import reverse\n'
                    f'from django.contrib.auth import get_user_model\n\n'
                    f'class {app.capitalize()}{formatted_cls}Test(TestCase):\n'
                    f'    """Automated isolated API endpoint testing suite."""\n\n'
                    f'    def setUp(self):\n'
                    f'        self.user = get_user_model().objects.create_user(username="{app}_api_pilot", password="password123")\n'
                    f'        self.url = reverse("{app}:{func_name}")\n\n'
                    f'    def test_unauthenticated_api_request_redirects(self):\n'
                    f'        response = self.client.get(self.url)\n'
                    f'        self.assertEqual(response.status_code, 302)\n\n'
                    f'    def test_authenticated_api_delivers_json_payload(self):\n'
                    f'        self.client.login(username="{app}_api_pilot", password="password123")\n'
                    f'        response = self.client.get(self.url)\n'
                    f'        self.assertEqual(response.status_code, 200)\n'
                    f'        self.assertEqual(response.json()["status"], "success")\n'
                    f'        self.assertEqual(response.json()["endpoint"], "{endpoint}")\n'
                )

            return {"status": "success", "message": f"Successfully forged API function '{func_name}' with tests."}

        except Exception as e:
            return {"status": "error", "message": f"Failed to execute API forge sequence: {str(e)}"}

    @classmethod
    def purge_api(cls, target_app: str, endpoint_name: str) -> dict:
        """Surgically undoes file builds and removes API registrations completely."""
        app, endpoint, func_name = cls.clean_inputs(target_app, endpoint_name)
        base_dir = os.getcwd()
        
        view_file = os.path.join(base_dir, app, 'views', f'{endpoint}_view.py')
        view_init = os.path.join(base_dir, app, 'views', '__init__.py')
        urls_file = os.path.join(base_dir, app, 'urls.py')
        test_file = os.path.join(base_dir, app, 'tests', f'test_{endpoint}.py')
        logs = []

        try:
            if os.path.exists(view_file): os.remove(view_file); logs.append(f"Deleted view")
            if os.path.exists(test_file): os.remove(test_file); logs.append(f"Deleted dynamic test profile")

            if os.path.exists(view_init):
                with open(view_init, 'r') as f: lines = f.readlines()
                clean_lines = [l for l in lines if f"{endpoint}_view" not in l and f"'{func_name}'" not in l]
                with open(view_init, 'w') as f: f.writelines(clean_lines)
                logs.append("Scrubbed package exporter.")

            if os.path.exists(urls_file):
                with open(urls_file, 'r') as f: lines = f.readlines()
                clean_lines = [l for l in lines if f"views.{func_name}" not in l and f"'api/{endpoint}/'" not in l]
                with open(urls_file, 'w') as f: f.writelines(clean_lines)
                logs.append("Erased url routing node.")

            return {"status": "success", "message": " | ".join(logs) if logs else "No API components found to purge."}
        except Exception as e:
            return {"status": "error", "message": f"Surgical wipe failure: {str(e)}"}
