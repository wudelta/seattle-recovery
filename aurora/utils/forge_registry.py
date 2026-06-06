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
def register_new_component(file_path: str, name: str, visibility: str, user_instance: User, persona: str = 'COMPILER_MODULE', description: str = ''):
    """
    Enforces a strict sandbox guardrail. 
    Registers component footprints into PostgreSQL linked directly to a verified User object instance.
    """
    path_parts = file_path.replace("\\", "/").split("/")
    if any(banned in path_parts for banned in BANNED_DIRECTORIES):
        raise PermissionError(f"FORGE GUARDRAIL VIOLATION: Execution blocked for environment path: {file_path}")
        
    clean_visibility = visibility.strip().upper()
    if clean_visibility not in ['PUBLIC', 'PRIVATE']:
        clean_visibility = 'PRIVATE'

    # Commit structural record profile to Postgres with strict developer accountability
    postgres_entry = ComponentRegistry.objects.create(
        file_path=file_path,
        name=name,
        persona=persona,
        status='ACTIVE',
        visibility=clean_visibility,
        locked=False,  # Unlocked by default; modified later via explicit lock commands
        created_by=user_instance,  # Drops the verified User instance key into the relation
        description=description,
        description_audiences=["developers"]
    )
    return postgres_entry
# ======================================================================
# END: SANDBOX GUARDRAILS & POSTGRES RECORD PROVISIONING
# ======================================================================
