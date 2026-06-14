# ======================================================================
# FILE: aurora/utils/ast_scanner.py (PATCH 1 OF 2)
# START: AST_SCANNER_CORE_INITIALIZATION_AND_PARSER
# ======================================================================
import ast
import os
from typing import Set
from aurora.nodes import ComponentNode

class OGMTopographyScanner:
    """Parses modules using AST and hooks into neomodel to link existing graph structures."""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.abspath(workspace_root)

    def parse_dependencies(self, file_path: str) -> Set[str]:
        """Extracts import targets from a single file path without code execution."""
        dependencies = set()
        if not os.path.exists(file_path):
            return dependencies
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                root = ast.parse(f.read(), filename=file_path)
            for node in ast.walk(root):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.add(node.module)
        except (SyntaxError, UnicodeDecodeError):
            pass  # Safely bypass non-source assets or invalid formats
        return dependencies

    def inject_implicit_framework_dependencies(self):
        """Connects framework core entry vectors that bypass explicit python imports."""
        try:
            settings_node = ComponentNode.nodes.get(file_path="core_logic/settings.py")
            entry_paths = [
                "manage.py",
                "core_logic/urls.py",
                "core_logic/wsgi.py",
                "core_logic/asgi.py"
            ]
            for path in entry_paths:
                try:
                    entry_node = ComponentNode.nodes.get(file_path=path)
                    if not entry_node.depends_on.is_connected(settings_node):
                        entry_node.depends_on.connect(settings_node)
                except ComponentNode.DoesNotExist:
                    continue

            urls_node = ComponentNode.nodes.get(file_path="core_logic/urls.py")
            app_urls = ["aurora/urls.py", "hopehub/urls.py"]
            for path in app_urls:
                try:
                    sub_url_node = ComponentNode.nodes.get(file_path=path)
                    if not urls_node.depends_on.is_connected(sub_url_node):
                        urls_node.depends_on.connect(sub_url_node)
                except ComponentNode.DoesNotExist:
                    continue
        except ComponentNode.DoesNotExist:
            pass
# ======================================================================
# END: AST_SCANNER_CORE_INITIALIZATION_AND_PARSER (PATCH 1 OF 2)
# ======================================================================

# ======================================================================
# FILE: aurora/utils/ast_scanner.py (PATCH 2 OF 2)
# START: DEFENSIVE_WORKSPACE_MAPPER_ENGINE
# ======================================================================
    def map_workspace_topography(self):
        """Walks project tree, scans imports, and connects ComponentNodes via OGM."""
        for root_dir, _, files in os.walk(self.workspace_root):
            for file in files:
                if not file.endswith(".py"):
                    continue
                full_path = os.path.join(root_dir, file)
                rel_file_path = os.path.relpath(full_path, self.workspace_root)
                
                try:
                    source_node = ComponentNode.nodes.get(file_path=rel_file_path)
                except ComponentNode.DoesNotExist:
                    continue

                found_imports = self.parse_dependencies(full_path)
                for import_name in found_imports:
                    possible_paths = [
                        f"{import_name.replace('.', '/')}.py",
                        f"{import_name.replace('.', '/')}/__init__.py"
                    ]
                    for target_path in possible_paths:
                        try:
                            target_node = ComponentNode.nodes.get(file_path=target_path)
                            if not source_node.depends_on.is_connected(target_node):
                                source_node.depends_on.connect(target_node)
                            break
                        except ComponentNode.DoesNotExist:
                            # SAFE GUARD FIX: Absorb missing dependencies gracefully during scans
                            continue
                            
        # Inject implicit Django bindings immediately after processing explicit physical file code imports
        self.inject_implicit_framework_dependencies()
# ======================================================================
# END: DEFENSIVE_WORKSPACE_MAPPER_ENGINE (PATCH 2 OF 2)
# ======================================================================
