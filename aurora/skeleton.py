# aurora/skeleton.py
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

        # Dynamic Path Layout Mappings
        view_file = os.path.join(base_dir, app, 'views', f'{page}_view.py')
        view_init = os.path.join(base_dir, app, 'views', '__init__.py')
        template_file = os.path.join(base_dir, app, 'templates', app, f'{page}.html')
        urls_file = os.path.join(base_dir, app, 'urls.py')
        
        if os.path.exists(view_file) or os.path.exists(template_file):
            return {"status": "error", "message": f"Collision: Component '{page}' already exists in app '{app}'."}
            
        base_template_extends = f"{app}/{app}_base.html"
            
        try:
            # 1. Write Template File
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
                    f'    <a href="{{% url \'aurora:console\' %}}" class="btn btn-outline-secondary btn-sm font-monospace mt-3">Return to Console</a>\n'
                    f'</div>\n'
                    f'{{% endblock %}}\n'
                )
                
            # 2. Write Class-Based View
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
                    f'        return context\n'
                )
                
            # 3. Inject to __init__.py package whitelists (Fixed Type-Mismatch Logic)
            if os.path.exists(view_init):
                with open(view_init, 'r') as f:
                    content = f.read()
                
                # Prepend the dynamic module import statement securely as a single text block string
                content = f"from .{page}_view import {class_name}\n" + content
                
                # Append the new view token array element cleanly into your __all__ block
                if "__all__ = [" in content:
                    parts = content.split("__all__ = [")
                    # Split further at the closing array bracket of __all__
                    sub_parts = parts[1].split("]")
                    # Inject class name array variable string token smoothly right at the end
                    sub_parts[0] = sub_parts[0] + f"    '{class_name}',\n"
                    # Stitch array structure back together cleanly
                    parts[1] = "]".join(sub_parts)
                    content = "__all__ = [".join(parts)
                    
                with open(view_init, 'w') as f:
                    f.write(content)
            
            # 4. Inject into target urls.py pattern loop (Fixed Type-Mismatch Logic)
            if os.path.exists(urls_file):
                with open(urls_file, 'r') as f:
                    urls_content = f.read()
                if "urlpatterns = [" in urls_content:
                    parts = urls_content.split("urlpatterns = [")
                    sub_parts = parts[1].split("]")
                    sub_parts[0] = sub_parts[0] + f"    path('{page}/', views.{class_name}.as_view(), name='{page}'),\n"
                    parts[1] = "]".join(sub_parts)
                    urls_content = "urlpatterns = [".join(parts)
                    
                with open(urls_file, 'w') as f:
                    f.write(urls_content)
                    
            return {"status": "success", "message": f"Successfully forged '{class_name}' inside app '{app}'."}
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
        
        logs = []
        try:
            if os.path.exists(view_file):
                os.remove(view_file)
                logs.append(f"Deleted view: {page}_view.py")
            if os.path.exists(template_file):
                os.remove(template_file)
                logs.append(f"Deleted template: {page}.html")
                
            if os.path.exists(view_init):
                with open(view_init, 'r') as f:
                    lines = f.readlines()
                clean_lines = [l for l in lines if f"{page}_view" not in l and f"'{class_name}'" not in l]
                with open(view_init, 'w') as f:
                    f.writelines(clean_lines)
                logs.append("Scrubbed package exporter.")
                
            if os.path.exists(urls_file):
                with open(urls_file, 'r') as f:
                    lines = f.readlines()
                clean_lines = [l for l in lines if f"views.{class_name}.as_view()" not in l and f"'{page}/'" not in l]
                with open(urls_file, 'w') as f:
                    f.writelines(clean_lines)
                logs.append("Erased url routing node.")
                
            return {"status": "success", "message": " | ".join(logs)}
        except Exception as e:
            return {"status": "error", "message": f"Surgical wipe failure: {str(e)}"}