# aurora/api_skeleton.py
import os
import re

class ApiSkeletonBuilder:
    """Automated multi-app builder and destroyer to forge or purge functional API endpoints with visibility safety."""

    @staticmethod
    def clean_inputs(app_name: str, endpoint_name: str):
        app = re.sub(r'[^a-zA-Z0-9_]', '', app_name.lower().strip())
        endpoint = re.sub(r'[^a-zA-Z0-9_]', '', endpoint_name.lower().strip())
        func_name = f"{endpoint}_endpoint"
        return app, endpoint, func_name

    @classmethod
    def forge_api(cls, target_app: str, endpoint_name: str, visibility: str) -> dict:
        app, endpoint, func_name = cls.clean_inputs(target_app, endpoint_name)
        if not app or not endpoint:
            return {"status": "error", "message": "Invalid architectural parameters."}

        is_private = visibility.lower().strip() != "public"
        base_dir = os.getcwd()
        if not os.path.exists(os.path.join(base_dir, app)):
            return {"status": "error", "message": f"Target app directory '{app}' does not exist."}

        view_file = os.path.join(base_dir, app, 'views', f'{endpoint}_view.py')
        view_init = os.path.join(base_dir, app, 'views', '__init__.py')
        urls_file = os.path.join(base_dir, app, 'urls.py')
        test_file = os.path.join(base_dir, app, 'tests', f'test_{endpoint}_{app}.py')

        if os.path.exists(view_file):
            return {"status": "error", "message": f"Collision: API Component '{endpoint}' already exists in app '{app}'."}

        try:
            # 1. Write Function-Based View Endpoint returning JSON
            os.makedirs(os.path.dirname(view_file), exist_ok=True)
            with open(view_file, 'w') as f:
                decorator_import = "from django.contrib.auth.decorators import login_required\n" if is_private else ""
                decorator_line = "@login_required\n" if is_private else ""
                f.write(
                    f'# {app}/views/{endpoint}_view.py\n'
                    f'from django.http import JsonResponse\n{decorator_import}\n'
                    f'{decorator_line}'
                    f'def {func_name}(request):\n'
                    f'    """Automated test payload endpoint forged by Aurora Forge Engine."""\n'
                    f'    payload = {{\n'
                    f'        "status": "success",\n'
                    f'        "visibility": "{visibility}",\n'
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
            with open(test_file, 'w') as f:
                expected_status = "302" if is_private else "200"
                formatted_cls = func_name.replace("_", " ").title().replace(" ", "")
                f.write(
                    f'# {app}/tests/test_{endpoint}_{app}.py\n'
                    f'from django.test import TestCase\n'
                    f'from django.urls import reverse\n\n'
                    f'class {app.capitalize()}{formatted_cls}IsolationTest(TestCase):\n'
                    f'    def test_visibility_api_rules(self):\n'
                    f'        url = reverse("{app}:{func_name}")\n'
                    f'        response = self.client.get(url)\n'
                    f'        self.assertEqual(response.status_code, {expected_status})\n'
                )

            return {"status": "success", "message": f"Successfully forged API function '{func_name}' inside app '{app}' ({visibility})."}

        except Exception as e:
            return {"status": "error", "message": f"Failed to execute API forge sequence: {str(e)}"}

    @classmethod
    def purge_api(cls, target_app: str, endpoint_name: str) -> dict:
        """Surgically undoes file builds and deletes registrations completely."""
        app, endpoint, func_name = cls.clean_inputs(target_app, endpoint_name)
        base_dir = os.getcwd()
        
        view_file = os.path.join(base_dir, app, 'views', f'{endpoint}_view.py')
        view_init = os.path.join(base_dir, app, 'views', '__init__.py')
        urls_file = os.path.join(base_dir, app, 'urls.py')
        test_file = os.path.join(base_dir, app, 'tests', f'test_{endpoint}_{app}.py')
        logs = []

        try:
            if os.path.exists(view_file):
                os.remove(view_file)
                logs.append(f"Deleted view: {endpoint}_view.py")

            if os.path.exists(test_file):
                os.remove(test_file)
                logs.append(f"Deleted test file: test_{endpoint}_{app}.py")

            if os.path.exists(view_init):
                with open(view_init, 'r') as f:
                    lines = f.readlines()
                clean_lines = [l for l in lines if f"{endpoint}_view" not in l and f"'{func_name}'" not in l]
                with open(view_init, 'w') as f:
                    f.writelines(clean_lines)
                logs.append("Scrubbed package exporter.")

            if os.path.exists(urls_file):
                with open(urls_file, 'r') as f:
                    lines = f.readlines()
                clean_lines = [l for l in lines if f"views.{func_name}" not in l and f"'api/{endpoint}/'" not in l]
                with open(urls_file, 'w') as f:
                    f.writelines(clean_lines)
                logs.append("Erased url routing node.")

            return {"status": "success", "message": " | ".join(logs) if logs else "No API components found to purge."}

        except Exception as e:
            return {"status": "error", "message": f"Surgical wipe failure: {str(e)}"}
