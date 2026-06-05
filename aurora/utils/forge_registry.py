# aurora/utils/forge_registry.py
import os
from aurora.models import ComponentRegistry

BANNED_DIRECTORIES = ["venv", ".venv", "site-packages", ".git"]

def register_new_component(file_path: str, name: str, visibility: str, created_by: str, description: str):
    """
    Enforces strict sandbox parameters. Registers the asset profile into 
    PostgreSQL, which automatically triggers the Neo4j node synchronization signal.
    """
    path_parts = file_path.replace("\\", "/").split("/")
    if any(banned in path_parts for banned in BANNED_DIRECTORIES):
        raise PermissionError(f"FORGE GUARDRAIL VIOLATION: Execution blocked for unmanaged path: {file_path}")

    # Standardize the incoming visibility text to match choices array format
    clean_visibility = visibility.strip().upper()
    if clean_visibility not in ['PUBLIC', 'PRIVATE']:
        clean_visibility = 'PRIVATE' # Default to strict protection mode

    # Relational transactional entry write
    postgres_entry = ComponentRegistry.objects.create(
        file_path=file_path,
        name=name,
        persona='COMPILER_MODULE',
        status='ACTIVE',
        visibility=clean_visibility,
        locked=False, # Remains unlocked during creation/construction phase
        created_by=created_by,
        description=description,
        description_audiences=["developers"]
    )
    
    return postgres_entry
