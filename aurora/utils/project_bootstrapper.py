# ======================================================================
# FILE: aurora/utils/project_bootstrapper.py (PATCH 1 OF 2)
# START: REGISTRY_INITIAL_POPULATOR
# ======================================================================
import os
from django.contrib.auth.models import User
from aurora.models import ComponentRegistry
from aurora.utils.ast_scanner import OGMTopographyScanner

class ProjectBootstrapper:
    """Discovers untracked codebase files and registers them into PostgreSQL."""

    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.abspath(workspace_root)

    def bootstrap_ecosystem(self, developer_username: str) -> dict:
        """Finds local .py files and bulk-registers them to kickstart signals."""
        # Ensure a valid developer user exists to own the newly forged assets
        dev_user, _ = User.objects.get_or_create(
            username=developer_username, 
            defaults={"is_staff": True}
        )

        created_count = 0
        skipped_count = 0
        registered_paths = []

        # Walk the drive to find files that aren't tracked yet
        for root_dir, _, files in os.walk(self.workspace_root):
            for file in files:
                if not file.endswith(".py"):
                    continue

                full_path = os.path.join(root_dir, file)
                rel_file_path = os.path.relpath(full_path, self.workspace_root)

                # Avoid registering files inside virtual environments or hidden dirs
                if any(part.startswith('.') or part in ['venv', 'env'] for part in rel_file_path.split(os.sep)):
                    continue

                # Get or create ensures we never duplicate entries
                obj, created = ComponentRegistry.objects.get_or_create(
                    file_path=rel_file_path,
                    defaults={
                        "name": file,
                        "persona": "COMPILER_MODULE",
                        "status": "ACTIVE",
                        "created_by": dev_user,
                        "description": "Legacy codebase asset ingested during master bootstrap loop."
                    }
                )
                
                if created:
                    created_count += 1
                    registered_paths.append(rel_file_path)
                else:
                    skipped_count += 1
# ======================================================================
# END: REGISTRY_INITIAL_POPULATOR
# ======================================================================

# ======================================================================
# FILE: aurora/utils/project_bootstrapper.py (PATCH 2 OF 2)
# START: TOPOGRAPHY_FINALIZER_LOOP
# ======================================================================
        # Step 2: Initialize and execute full topography relationship generation
        print(f"PostgreSQL Ingestion Complete. Created: {created_count}, Skipped: {skipped_count}.")
        print("Initializing secondary AST topography generation over newly generated nodes...")
        
        scanner = OGMTopographyScanner(self.workspace_root)
        scanner.map_workspace_topography()
        
        return {
            "status": "SUCCESS",
            "ingested_nodes_count": created_count,
            "retained_nodes_count": skipped_count,
            "registered_modules": registered_paths
        }

if __name__ == "__main__":
    import django
    import sys
    
    # Ensure tool runs with context initialized from your root directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(project_root)
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seattle_recovery.settings')
    django.setup()
    
    bootstrapper = ProjectBootstrapper(project_root)
    report = bootstrapper.bootstrap_ecosystem(developer_username="delta")
    print(f"Bootstrap sequence completed smoothly. System metrics: {report}")
# ======================================================================
# END: TOPOGRAPHY_FINALIZER_LOOP
# ======================================================================
