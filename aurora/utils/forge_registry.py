# ======================================================================
# FILE: aurora/utils/forge_registry.py (PATCH 1 OF 2)
# START: REGISTRY CORE IMPORTS & SYSTEM CONSTRAINT DEFINITIONS
# ======================================================================
import os
from aurora.models import ComponentRegistry
from django.contrib.auth.models import User

# Enforce explicit sandbox guardrails to keep core tooling isolated
BANNED_DIRECTORIES = ["venv", ".venv", "site-packages", ".git"]
# ======================================================================
# END: REGISTRY CORE IMPORTS & SYSTEM CONSTRAINT DEFINITIONS
# ======================================================================

# ======================================================================
# FILE: aurora/utils/forge_registry.py (PATCH 2 OF 2)
# START: SANDBOX GUARDRAILS & POSTGRES RECORD PROVISIONING
# ======================================================================
def register_new_component(file_path: str, name: str, visibility: str, user_instance: User, persona: str = 'COMPILER_MODULE', description: str = '', run_scanner: bool = True):
    """
    Enforces a strict sandbox guardrail. Registers component footprints into PostgreSQL 
    and conditionally recalculates graph network lineages.
    """
    path_parts = file_path.replace("\\", "/").split("/")
    if any(banned in path_parts for banned in BANNED_DIRECTORIES):
        raise PermissionError(f"FORGE GUARDRAIL VIOLATION: Execution blocked for environment path: {file_path}")

    clean_visibility = visibility.strip().upper()
    if clean_visibility not in ['PUBLIC', 'PRIVATE']:
        clean_visibility = 'PRIVATE'

    # 1. Commit structural record profile to Postgres (Triggers the new sync signal)
    postgres_entry = ComponentRegistry.objects.create(
        file_path=file_path,
        name=name,
        persona=persona,
        status='ACTIVE',
        visibility=clean_visibility,
        locked=False,
        created_by=user_instance,
        description=description,
        description_audiences=["developers"]
    )

    # 2. Trigger real-time AST import parsing and map graph network linkages
    if run_scanner:
        try:
            from aurora.utils.ast_scanner import OGMTopographyScanner
            from aurora.utils.page_skeleton import PageSkeletonBuilder
            PageSkeletonBuilder.emit_log("[FORGE_ENGINE] [AST] Initializing topological dependency resolution scanner pass...\n")

            # Walk active workspace tree path bounds to build structural link lineages
            base_project_dir = os.getcwd()
            scanner = OGMTopographyScanner(base_project_dir)
            scanner.map_workspace_topography()
            PageSkeletonBuilder.emit_log("[FORGE_ENGINE] [AST] Graph dependency matrix computation finalized successfully.\n")
        except Exception as graph_err:
            from aurora.utils.page_skeleton import PageSkeletonBuilder
            PageSkeletonBuilder.emit_log(f"[WARNING] AST scanner pass failed to complete graph linkages: {str(graph_err)}\n")

    return postgres_entry
# ======================================================================
# END: SANDBOX GUARDRAILS & POSTGRES RECORD PROVISIONING (PATCH 2 OF 2)
# ======================================================================
