# aurora/page_skeleton.py
import os
import re

class PageSkeletonBuilder:
    """Automated multi-app builder and destroyer to forge or purge pages with zero tokens."""

    @staticmethod
    def clean_inputs(app_name: str, page_name: str):
        app = re.sub(r'[^a-zA-Z0-9_]', '', app_name.lower().strip())
        page = re.sub(r'[^a-zA-Z0-9_]', '', page_name.lower().strip())
        cls = "".join([part.capitalize() for part in page.split("_")]) + "View"
        return app, page, cls

    @classmethod
    def forge_page(cls, target_app: str, page_name: str) -> dict:
        app, page, class_name = cls.clean_inputs(target_app, page_name)
        if not app or not page:
            return {"status": "error", "message": "Invalid architectural parameters."}

        base_dir = os.getcwd()
        if not os.path.exists(os.path.join(base_dir, app)):
            return {"status": "error", "message": f"Target app directory '{app}' does not exist on this machine."}

        view_file = os.path.join(base_dir, app, 'views', f'{page}_view.py')
        view_init = os.path.join(base_dir, app, 'views', '__init__.py')
        template_file = os.path.join(base_dir, app, 'templates', app, f'{page}.html')
        urls_file = os.path.join(base_dir, app, 'urls.py')
        test_file = os.path.join(base_dir, app, 'tests', f'test_{page}.py')

        if os.path.exists(view_file) or os.path.exists(template_file):
            return {"status": "error", "message": f"Collision: Component '{page}' already exists in app '{app}'."}

        base_template_extends = f"{app}/{app}_base.html"

        try:
            # 1. HTML Template Generation
            os.makedirs(os.path.dirname(template_file), exist_ok=True)
            with open(template_file, 'w') as f:
                f.write(
                    f'{{% extends "{base_template_extends}" %}}\n'
                    f'{{% load static %}}\n\n'
                    f'{{% block title %}}{page.replace("_", " ").title()} | Under Construction{{% endblock %}}\n\n'
                    f'{{% block content %}}\n'
                    f'<div class="d-flex flex-column align-items-center justify-content-center text-center p-5 rounded bg-black" style="min-height: 60vh;">\n'
                    f'    <div class="spinner-border text-warning mb-4" role="status" style="width: 3rem; height: 3rem;"></div>\n'
                    f'    <h2 class="display-5 text-warning font-monospace">🚧 Under Construction 🚧</h2>\n'
                    f'    <p class="lead text-muted font-monospace mt-2">The class-based structure for <strong>{class_name}</strong> has been forged in <strong>{app}</strong>.</p>\n'
                    f'    <a href="{{{{ return_path }}}}" class="btn btn-outline-warning btn-sm font-monospace mt-3">Return to Dashboard</a>\n'
                    f'</div>\n'
                    f'{{% endblock %}}\n'
                )

            # 2. Class-Based View Generation
            os.makedirs(os.path.dirname(view_file), exist_ok=True)
            with open(view_file, 'w') as f:
                f.write(
                    f'# {app}/views/{page}_view.py\n'
                    f'from django.views.generic import TemplateView\n'
                    f'from django.contrib.auth.mixins import LoginRequiredMixin\n\n'
                    f'class {class_name}(LoginRequiredMixin, TemplateView):\n'
                    f'    template_name = "{app}/{page}.html"\n\n'
                    f'    def get_context_data(self, **kwargs):\n'
                    f'        context = super().get_context_data(**kwargs)\n'
                    f'        context["page_title"] = "{page.replace("_", " ").title()}"\n'
                    f'        context["return_path"] = "/hopehub/" if "{app}" == "hopehub" else "/aurora/"\n'
                    f'        return context\n'
                )

            # 3. Inject to views/__init__.py package whitelist
            if os.path.exists(view_init):
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

            # 4. Inject into target urls.py pattern loop
            if os.path.exists(urls_file):
                with open(urls_file, 'r') as f:
                    urls_content = f.read()
                if "urlpatterns = [" in urls_content:
                    parts = urls_content.split("urlpatterns = [")
                    sub_parts = parts[1].split("]", 1)
                    inner_urls = sub_parts[0].rstrip()
                    url_route = f"    path('{page}/', views.{class_name}.as_view(), name='{page}'),"
                    if url_route.strip() not in inner_urls:
                        sub_parts[0] = f"{inner_urls}\n{url_route}\n"
                        parts[1] = "]".join(sub_parts)
                        urls_content = "urlpatterns = [".join(parts)
                with open(urls_file, 'w') as f:
                    f.write(urls_content)

            # 5. Forged Unit Test Generation
            os.makedirs(os.path.dirname(test_file), exist_ok=True)
            with open(test_file, 'w') as f:
                f.write(
                    f'# {app}/tests/test_{page}_{app}.py\n'
                    f'from django.test import TestCase\n'
                    f'from django.urls import reverse\n'
                    f'from django.contrib.auth import get_user_model\n\n'
                    f'class {app.capitalize()}{class_name}RouteTest(TestCase):\n'
                    f'    """Automated isolated page testing suite."""\n\n'
                    f'    def setUp(self):\n'
                    f'        self.user = get_user_model().objects.create_user(username="{app}_pilot", password="password123")\n'
                    f'        self.url = reverse("{app}:{page}")\n\n'
                    f'    def test_unauthenticated_user_redirects_to_login(self):\n'
                    f'        response = self.client.get(self.url)\n'
                    f'        self.assertEqual(response.status_code, 302)\n\n'
                    f'    def test_authenticated_user_accesses_forged_view_successfully(self):\n'
                    f'        self.client.login(username="{app}_pilot", password="password123")\n'
                    f'        response = self.client.get(self.url)\n'
                    f'        self.assertEqual(response.status_code, 200)\n'
                    f'        self.assertTemplateUsed(response, "{app}/{page}.html")\n'
                )

            return {"status": "success", "message": f"Successfully forged '{class_name}' with accompanying tests."}

        except Exception as e:
            return {"status": "error", "message": f"Failed to execute forge sequence: {str(e)}"}

    @classmethod
    def purge_page(cls, target_app: str, page_name: str) -> dict:
        """Surgically undoes file builds and deletes registrations completely."""
        app, page, class_name = cls.clean_inputs(target_app, page_name)
        base_dir = os.getcwd()
        
        view_file = os.path.join(base_dir, app, 'views', f'{page}_view.py')
        view_init = os.path.join(base_dir, app, 'views', '__init__.py')
        template_file = os.path.join(base_dir, app, 'templates', app, f'{page}.html')
        urls_file = os.path.join(base_dir, app, 'urls.py')
        test_file = os.path.join(base_dir, app, 'tests', f'test_{page}.py')
        logs = []

        try:
            if os.path.exists(view_file): os.remove(view_file); logs.append(f"Deleted view")
            if os.path.exists(template_file): os.remove(template_file); logs.append(f"Deleted template")
            if os.path.exists(test_file): os.remove(test_file); logs.append(f"Deleted dynamic test profile")

            if os.path.exists(view_init):
                with open(view_init, 'r') as f: lines = f.readlines()
                clean_lines = [l for l in lines if f"{page}_view" not in l and f"'{class_name}'" not in l]
                with open(view_init, 'w') as f: f.writelines(clean_lines)
                logs.append("Scrubbed package exporter.")

            if os.path.exists(urls_file):
                with open(urls_file, 'r') as f: lines = f.readlines()
                clean_lines = [l for l in lines if f"views.{class_name}.as_view()" not in l and f"'{page}/'" not in l]
                with open(urls_file, 'w') as f: f.writelines(clean_lines)
                logs.append("Erased url routing node.")

            return {"status": "success", "message": " | ".join(logs) if logs else "No structural components found to purge."}
        except Exception as e:
            return {"status": "error", "message": f"Surgical wipe failure: {str(e)}"}
