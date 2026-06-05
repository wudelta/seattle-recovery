# aurora/utils/forge_registry.py
import os
from aurora.models import ComponentRegistry
from django.contrib.auth.models import User # Ensure User model accessibility

BANNED_DIRECTORIES = ["venv", ".venv", "site-packages", ".git"]

def register_new_component(file_path: str, name: str, visibility: str, user_instance: User, persona: str = 'COMPILER_MODULE', description: str = ''):
    """
    Enforces a strict sandbox guardrail. Registers component footprints
    into PostgreSQL linked directly to a verified User object instance.
    """
    path_parts = file_path.replace("\\", "/").split("/")
    if any(banned in path_parts for banned in BANNED_DIRECTORIES):
        raise PermissionError(f"FORGE GUARDRAIL VIOLATION: Execution blocked for environment path: {file_path}")

    clean_visibility = visibility.strip().upper()
    if clean_visibility not in ['PUBLIC', 'PRIVATE']:
        clean_visibility = 'PRIVATE'

    # Commit structural record profile to Postgres
    postgres_entry = ComponentRegistry.objects.create(
        file_path=file_path,
        name=name,
        persona=persona,
        status='ACTIVE',
        visibility=clean_visibility,
        locked=False,
        created_by=user_instance,  # <-- Drops the verified User instance key into the database relation
        description=description,
        description_audiences=["developers"]
    )
    
    return postgres_entry
